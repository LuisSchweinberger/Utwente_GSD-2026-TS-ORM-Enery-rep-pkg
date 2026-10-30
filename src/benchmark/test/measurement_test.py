import datetime as dt
import json
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from runner import energy as measurement
from runner.artifacts import TaskPaths, assemble, write_json


class EnergyTests(unittest.TestCase):
    def test_rapl_wrap_and_invalid_range(self):
        self.assertEqual(measurement.rapl_delta(90, 15, 100), 25)
        self.assertEqual(measurement.rapl_delta(15, 35, 100), 20)
        with self.assertRaises(ValueError):
            measurement.rapl_delta(0, 101, 100)

    def test_rapl_discovery_deduplication_and_domain_separation(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(measurement.platform, "system", return_value="Linux"):
            root = Path(temp)
            package = root / "intel-rapl:0"
            core = package / "intel-rapl:0:0"
            core.mkdir(parents=True)
            for folder, name, energy in ((package, "package-0", 90), (core, "core", 40)):
                (folder / "name").write_text(name)
                (folder / "max_energy_range_uj").write_text("100")
                (folder / "energy_uj").write_text(str(energy))
            (root / "intel-rapl:0:0").symlink_to(core, target_is_directory=True)
            collector = measurement.Rapl(root / "raw.jsonl", .02, root=root)
            try:
                collector.start()
                started = time.monotonic()
                (package / "energy_uj").write_text("15")
                (core / "energy_uj").write_text("50")
                ended = time.monotonic()
                domains = collector.finish(started, ended)
                self.assertEqual(len(domains), 2)
                values = {domain["name"]: domain["energyJ"] for domain in domains}
                self.assertAlmostEqual(values["package-0"], 25 / 1e6)
                self.assertAlmostEqual(values["core"], 10 / 1e6)
                self.assertGreaterEqual(domains[0]["endOffsetMs"], 0)
            finally:
                collector.close()

    def test_powermetrics_units_and_schema(self):
        fixture = {"timestamp": dt.datetime(2026, 1, 1), "elapsed_ns": 500_000_000,
                   "processor": {"cpu_energy": 157, "gpu_power": 6, "ane_energy": 0, "package_joules": .2}}
        # Exercise the real NUL-delimited plist payload format, not just a Python dict.
        parsed = measurement.power_sample(plistlib.loads(plistlib.dumps(fixture)))
        self.assertAlmostEqual(parsed["energyJ"]["cpu"], .157)
        self.assertAlmostEqual(parsed["energyJ"]["gpu"], .003)
        self.assertAlmostEqual(parsed["energyJ"]["package"], .2)
        with self.assertRaises(ValueError):
            measurement.power_sample({**fixture, "processor": {"unknown": 42}})
        with self.assertRaises(ValueError):
            measurement.power_sample({**fixture, "processor": {"cpu_energy": -1}})

    def test_powermetrics_partial_boundary_integration(self):
        samples = [{"start": i, "end": i + 1, "energyJ": {"cpu": 2, "gpu": .5}} for i in range(4)]
        domains = measurement.integrate_power(samples, .5, 3.5)
        values = {item["name"]: item for item in domains}
        self.assertEqual(values["cpu"]["energyJ"], 6)
        self.assertEqual(values["gpu"]["energyJ"], 1.5)
        self.assertEqual(values["cpu"]["coverageFraction"], 1)
        self.assertEqual(values["cpu"]["quality"], "adequate")
        short = measurement.integrate_power(samples, .5, .6)
        self.assertEqual(short[0]["quality"], "limited")

    def test_powermetrics_rejects_missing_or_overlapping_coverage(self):
        with self.assertRaises(ValueError):
            measurement.integrate_power([{"start": 0, "end": 1, "energyJ": {"cpu": 1}}], 0, 2)
        with self.assertRaises(ValueError):
            measurement.integrate_power([{"start": 0, "end": 2, "energyJ": {"cpu": 1}},
                                         {"start": 1, "end": 3, "energyJ": {"cpu": 1}}], 0, 3)

    def test_live_plist_stream_and_collector_cleanup(self):
        real_popen = subprocess.Popen
        fixture_program = """
import datetime, plistlib, sys, time
while True:
    time.sleep(.03)
    data = {'timestamp': datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
            'elapsed_ns': 30_000_000, 'processor': {'cpu_power': 2000}}
    sys.stdout.buffer.write(plistlib.dumps(data) + b'\\x00')
    sys.stdout.buffer.flush()
"""
        def launch(_command, **kwargs):
            return real_popen([sys.executable, "-c", fixture_program], **kwargs)
        with tempfile.TemporaryDirectory() as temp, \
                patch.object(measurement.platform, "system", return_value="Darwin"), \
                patch.object(measurement.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, stdout="cpu_power gpu_power")), \
                patch.object(measurement.subprocess, "Popen", side_effect=launch):
            collector = measurement.Powermetrics(Path(temp) / "raw.plist", .03)
            try:
                collector.start()
                start = time.monotonic()
                time.sleep(.12)
                end = time.monotonic()
                domains = collector.finish(start, end)
                self.assertAlmostEqual(domains[0]["energyJ"], 2 * (end - start), places=4)
                self.assertIsNotNone(collector.process.poll())
                self.assertTrue((Path(temp) / "raw.plist.samples.jsonl").exists())
            finally:
                collector.close()


class ControllerTests(unittest.TestCase):
    def test_only_start_stop_window_is_timed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            with measurement.Measurement("none", 100, root / "measurement.json", root / "raw") as meter:
                time.sleep(.15)
                meter.start()
                time.sleep(.05)
                meter.stop()
                time.sleep(.15)
            result = json.loads((root / "measurement.json").read_text())
            self.assertEqual(result["status"], "valid")
            self.assertGreaterEqual(result["timing"]["workloadElapsedMs"], 40)
            self.assertLess(result["timing"]["workloadElapsedMs"], 150)

    def test_interrupt_preserves_failed_measurement(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(KeyboardInterrupt):
                with measurement.Measurement("none", 100, Path(temp) / "measurement.json", Path(temp) / "raw") as meter:
                    meter.start()
                    raise KeyboardInterrupt("Measurement interrupted")
            result = json.loads((Path(temp) / "measurement.json").read_text())
            self.assertEqual(result["status"], "failed")
            self.assertIn("interrupted", result["error"])

    def test_baseline_is_attached_without_altering_workload_energy(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = TaskPaths(root, root / "results", root / "logs", "prisma", "test")
            paths.clear()
            execution = {"orm": "prisma", "scenario": "read-pet", "profile": "populated", "status": "pending_verification", "requestCountCompleted": 5}
            workload = {"backend": "rapl", "status": "valid", "domains": [{"name": "package", "energyJ": 10}],
                        "timing": {"workloadElapsedMs": 1000}}
            baseline = {"kind": "idle-baseline", "backend": "rapl", "status": "valid",
                        "domains": [{"name": "package", "energyJ": 3, "averagePowerW": .1}]}
            for suffix, data in ((".execution.json", execution), (".measurement.json", workload), (".baseline.json", baseline)):
                write_json(paths.result(suffix), data)
            result = assemble(paths, root / "manifest.json")
            self.assertEqual(result["measurement"]["domains"][0]["energyJ"], 10)
            self.assertEqual(result["idleBaseline"], baseline)
            self.assertEqual(result["throughputOpsPerSecond"], 5)
            self.assertEqual(result["artifacts"]["idleBaselineRaw"], "results/prisma/test.baseline.raw")


if __name__ == "__main__":
    unittest.main()
