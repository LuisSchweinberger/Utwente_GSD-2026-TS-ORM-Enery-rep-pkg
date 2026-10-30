"""Mac backend tests use fake IOReport counters and need no Zeus installation."""
from contextlib import ExitStack
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from runner import energy
from runner.artifacts import TaskPaths, assemble, write_json
from runner.config import Config
from runner.manifest import build_manifest


class AppleTests(unittest.TestCase):
    def mocks(self, values=(0, 1000, 2250)):
        stack = ExitStack()
        self.addCleanup(stack.close)
        monitor = MagicMock()
        monitor.get_cumulative_energy.side_effect = [SimpleNamespace(dram_mj=v) for v in values]
        module = SimpleNamespace(AppleEnergyMonitor=MagicMock(return_value=monitor))
        stack.enter_context(patch.dict(sys.modules, zeus_apple_silicon=module))
        stack.enter_context(patch.object(energy.importlib.metadata, "version", return_value="1.1.0"))
        stack.enter_context(patch.object(energy.platform, "system", return_value="Darwin"))
        stack.enter_context(patch.object(energy.platform, "machine", return_value="arm64"))
        return monitor

    def test_counter_units_and_snapshot_brackets(self):
        self.mocks()
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(energy.time, "monotonic_ns", side_effect=[0, 100, 1_000_000_000,
                              1_002_000_000, 2_000_000_000, 2_004_000_000]):
                memory = energy.AppleMemory(Path(temp) / "energy.raw")
                memory.start()
                domain = memory.finish(1.003, 1.999)
                memory.close()
            self.assertEqual(domain["energyJ"], 1.25)
            self.assertEqual(domain["sampleCount"], 2)
            self.assertEqual(domain["name"], "dram")
            self.assertAlmostEqual(domain["counterWindowElapsedMs"], 1001)
            self.assertEqual(domain["counterWindowBoundsMs"], {"lower": 998, "upper": 1004})
            self.assertAlmostEqual(domain["startOffsetMs"], -2)
            self.assertAlmostEqual(domain["endOffsetMs"], 3)
            self.assertNotIn("coverageFraction", domain)
            raw = json.loads((Path(temp) / "energy.raw.memory.json").read_text())
            self.assertEqual([s["energyMj"] for s in raw["snapshots"]], [0, 1000, 2250])
            memory.close()  # Idempotent cleanup.

    def test_zero_delta_is_valid(self):
        self.mocks((0, 10, 10))
        with tempfile.TemporaryDirectory() as temp:
            memory = energy.AppleMemory(Path(temp) / "raw")
            try:
                memory.start()
                domain = memory.finish(0, 1)
                self.assertEqual(domain["energyJ"], 0)
            finally:
                memory.close()

    def test_invalid_capability_preserved_in_sidecar(self):
        for value in (None, True, "123", -1, float("nan"), float("inf")):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as temp:
                self.mocks((value,))
                with self.assertRaisesRegex(ValueError, "dram_mj"):
                    energy.AppleMemory(Path(temp) / "raw")
                raw = json.loads((Path(temp) / "raw.memory.json").read_text())
                self.assertIn("error", raw)
                self.assertIsNone(raw["snapshots"][0]["energyMj"])

    def test_counter_reset_fails(self):
        self.mocks((0, 1000, 10))
        with tempfile.TemporaryDirectory() as temp:
            memory = energy.AppleMemory(Path(temp) / "raw")
            try:
                memory.start()
                with self.assertRaisesRegex(ValueError, "decreased/reset"):
                    memory.finish(0, 1)
            finally:
                memory.close()

    def test_overlapping_snapshot_brackets_fail(self):
        self.mocks()
        with tempfile.TemporaryDirectory() as temp, patch.object(energy.time, "monotonic_ns", return_value=1):
            memory = energy.AppleMemory(Path(temp) / "raw")
            try:
                memory.start()
                with self.assertRaisesRegex(ValueError, "positive counter window"):
                    memory.finish(0, 1)
            finally:
                memory.close()

    def test_combined_output_and_memory_read_before_power_drain(self):
        self.mocks()
        power = MagicMock()
        power.samples = [{"receiptLagMs": 0}]
        power.command = ["powermetrics", "-i", "100"]
        def drain(start, end):
            self.assertEqual(meter.collector.memory.data["snapshots"][-1]["kind"], "end")
            return [{"name": "cpu", "energyJ": 2, "sampleCount": 4,
                     "coverageFraction": 1, "quality": "adequate"}]
        power.finish.side_effect = drain
        with tempfile.TemporaryDirectory() as temp, patch.object(energy, "Powermetrics", return_value=power):
            path = Path(temp) / "measurement.json"
            with energy.Measurement("powermetrics_zeus", 100, path, Path(temp) / "energy.raw") as meter:
                meter.start()
                meter.stop()
            result = json.loads(path.read_text())
            self.assertEqual(result["status"], "valid")
            self.assertEqual(result["backend"], "powermetrics_zeus")
            self.assertEqual(len(result["collectors"]), 2)
            domains = {d["name"]: d for d in result["domains"]}
            self.assertEqual(set(domains), {"cpu", "dram"})
            for name, domain in domains.items():
                for field in ("id", "name", "energyJ", "sampleCount", "quality", "averagePowerW"):
                    self.assertIn(field, domain)
                self.assertEqual(domain["source"], "ioreport" if name == "dram" else "powermetrics")
            dram = domains["dram"]
            self.assertAlmostEqual(dram["averagePowerW"], 1.25 / (dram["counterWindowElapsedMs"] / 1000))
            power.close.assert_called_once()

    def test_memory_failure_invalidates_combined_and_closes_power(self):
        self.mocks((0, 1000, 1))
        power = MagicMock()
        with tempfile.TemporaryDirectory() as temp, patch.object(energy, "Powermetrics", return_value=power):
            path = Path(temp) / "measurement.json"
            with self.assertRaisesRegex(ValueError, "decreased/reset"):
                with energy.Measurement("powermetrics_zeus", 100, path, Path(temp) / "raw") as meter:
                    meter.start()
                    meter.stop()
            self.assertEqual(json.loads(path.read_text())["status"], "failed")
            power.close.assert_called_once()
            power.finish.assert_not_called()
            self.assertTrue((Path(temp) / "raw.memory.json").exists())

    def test_power_setup_failure_preserves_memory_sidecar_and_failed_measurement(self):
        self.mocks((0,))
        with tempfile.TemporaryDirectory() as temp, patch.object(energy, "Powermetrics", side_effect=ValueError("sudo needed")):
            path = Path(temp) / "measurement.json"
            with self.assertRaisesRegex(ValueError, "sudo needed"):
                with energy.Measurement("powermetrics_zeus", 100, path, Path(temp) / "raw"):
                    pass
            self.assertEqual(json.loads(path.read_text())["status"], "failed")
            self.assertEqual(len(json.loads((Path(temp) / "raw.memory.json").read_text())["snapshots"]), 1)

    def test_power_finish_failure_still_closes_memory(self):
        self.mocks()
        power = MagicMock()
        power.finish.side_effect = ValueError("coverage failed")
        with tempfile.TemporaryDirectory() as temp, patch.object(energy, "Powermetrics", return_value=power):
            path = Path(temp) / "measurement.json"
            with self.assertRaisesRegex(ValueError, "coverage failed"):
                with energy.Measurement("powermetrics_zeus", 100, path, Path(temp) / "raw") as meter:
                    meter.start()
                    meter.stop()
            self.assertEqual(json.loads(path.read_text())["status"], "failed")
            self.assertEqual(len(json.loads((Path(temp) / "raw.memory.json").read_text())["snapshots"]), 3)
            power.close.assert_called_once()

    def test_interrupt_keeps_partial_memory_snapshots(self):
        self.mocks((0, 100))
        power = MagicMock()
        with tempfile.TemporaryDirectory() as temp, patch.object(energy, "Powermetrics", return_value=power):
            path = Path(temp) / "measurement.json"
            with self.assertRaises(KeyboardInterrupt):
                with energy.Measurement("powermetrics_zeus", 100, path, Path(temp) / "raw") as meter:
                    meter.start()
                    raise KeyboardInterrupt("interrupted")
            self.assertEqual(json.loads(path.read_text())["status"], "failed")
            self.assertEqual(len(json.loads((Path(temp) / "raw.memory.json").read_text())["snapshots"]), 2)
            power.close.assert_called_once()

    def test_missing_cpu_is_not_replaced_by_zeus_cpu(self):
        self.mocks()
        power = MagicMock()
        power.finish.return_value = [{"name": "gpu", "energyJ": 1}]
        with tempfile.TemporaryDirectory() as temp, patch.object(energy, "Powermetrics", return_value=power):
            path = Path(temp) / "measurement.json"
            with self.assertRaisesRegex(ValueError, "CPU energy domain"):
                with energy.Measurement("powermetrics_zeus", 100, path, Path(temp) / "raw") as meter:
                    meter.start()
                    meter.stop()
            self.assertEqual(json.loads(path.read_text())["status"], "failed")

    def test_zeus_import_failure_has_installation_hint(self):
        with tempfile.TemporaryDirectory() as temp, \
                patch.object(energy.importlib.metadata, "version", return_value="1.1.0"), \
                patch.dict(sys.modules, zeus_apple_silicon=None):
            with self.assertRaisesRegex(ValueError, "Cannot import zeus-apple-silicon"):
                energy.AppleMemory(Path(temp) / "raw")
            self.assertIn("error", json.loads((Path(temp) / "raw.memory.json").read_text()))

    def test_platform_and_dependency_errors(self):
        with patch.object(energy.platform, "system", return_value="Linux"):
            with self.assertRaisesRegex(ValueError, "Apple Silicon"):
                energy.PowermetricsZeus("unused", .1)
        with patch.object(energy.importlib.metadata, "version", side_effect=energy.importlib.metadata.PackageNotFoundError):
            with self.assertRaisesRegex(ValueError, "requirements-mac.txt"):
                energy.collector_metadata("powermetrics_zeus")
            self.assertEqual(energy.collector_metadata("rapl"), [])

    def test_old_live_backend_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "powermetrics_zeus"):
                with energy.Measurement("powermetrics", 100, Path(temp) / "out", Path(temp) / "raw"):
                    pass
        with patch.object(Config, "bridge", return_value={"environment": {}, "combinations": []}):
            with self.assertRaisesRegex(ValueError, "Replace MEASUREMENT_BACKEND"):
                Config.load(".", {"MEASUREMENT_BACKEND": "powermetrics"})

    def test_combined_config_and_manifest(self):
        self.mocks()
        with patch.object(Config, "bridge", return_value={"environment": {}, "combinations": []}):
            config = Config.load(".", {"MEASUREMENT_BACKEND": "powermetrics_zeus", "POWER_SAMPLE_INTERVAL_MS": "100"})
        config.validate_backend(experiment=True)
        self.assertEqual(config.env["MEASUREMENT_BACKEND"], "powermetrics_zeus")
        with tempfile.TemporaryDirectory() as temp:
            config.root = Path(temp)
            (config.root / "package-lock.json").write_text("{}")
            with patch.object(Config, "bridge", return_value={"host": {}, "software": {}}), \
                    patch("runner.manifest.command", return_value=None):
                manifest = build_manifest(config, "pilot", 43, 1, 0, 0, 1)
            self.assertEqual(manifest["configuration"]["backend"], "powermetrics_zeus")
            self.assertEqual(manifest["configuration"]["collectors"], energy.collector_metadata("powermetrics_zeus"))
        with patch.object(energy.platform, "machine", return_value="x86_64"):
            with self.assertRaises(ValueError):
                config.validate_backend()

    def test_artifact_references_shared_baseline_and_cleanup(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = TaskPaths(root, root / "results", root / "logs", "prisma", "test")
            paths.clear()
            write_json(paths.result(".execution.json"), {"scenario": "read-pet", "profile": "populated",
                                                       "status": "pending_verification"})
            data = {"backend": "powermetrics_zeus", "status": "valid", "domains": []}
            write_json(paths.result(".measurement.json"), data)
            baseline = root / "baseline/measurement.json"
            write_json(baseline, data)
            result = assemble(paths, baseline_path=baseline)
            self.assertEqual(result["artifacts"]["rawMemoryEnergy"], "results/prisma/test.energy.raw.memory.json")
            self.assertEqual(result["artifacts"]["idleBaselineMemoryRaw"], "baseline/energy.raw.memory.json")
            sidecar = paths.result(".energy.raw.memory.json")
            sidecar.write_text("{}")
            paths.clear(quiet=True)
            self.assertFalse(sidecar.exists())


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[2] / "analysis/common.py"
        spec = importlib.util.spec_from_file_location("apple_analysis_common", path)
        cls.common = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.common
        spec.loader.exec_module(cls.common)

    def fixture(self, root, name, backend, dram=True):
        directory = root / "mac" / name
        write_json(directory / "manifest.json", {"configuration": {"backend": backend}})
        task = directory / "trials/trial-001/prisma/read-pet-populated"
        domains = [{"name": "cpu", "energyJ": 2}]
        if dram:
            domains.append({"id": "ioreport:dram", "name": "dram", "energyJ": 1.25})
        write_json(Path(str(task) + ".measurement.json"), {"status": "valid", "backend": backend,
                   "domains": domains, "timing": {"workloadElapsedMs": 1000,
                   "workloadStartedMonotonicNs": 0, "workloadFinishedMonotonicNs": 1_000_000_000}})
        write_json(Path(str(task) + ".json"), {"status": "valid", "scenario": "read-pet", "profile": "populated"})
        return directory

    def test_new_and_legacy_experiments_are_selected_separately(self):
        common = self.common
        with tempfile.TemporaryDirectory() as temp, patch.object(common, "RAW_DIR", Path(temp)):
            root = Path(temp)
            self.fixture(root, "experiment-42", "powermetrics", dram=False)
            self.fixture(root, "experiment-43", "powermetrics_zeus")
            with self.assertRaisesRegex(SystemExit, "Select exactly one"):
                common.select_machine("mac")
            old = common.select_machine("mac", "experiment-42")
            new = common.select_machine("mac", "experiment-43")
            self.assertNotIn(common.MEMORY, common.available_metrics(old))
            self.assertIn(common.MEMORY, common.available_metrics(new))
            self.assertEqual(common.load(new)[0][0].values[common.MEMORY], 1.25)
            self.assertNotIn(common.MEMORY, common.load(old)[0][0].values)
            self.assertEqual(new.experiment_path.name, "experiment-43")
            with self.assertRaises(SystemExit):
                common.select_machine("mac", "../experiment-43")

    def test_mixed_backends_and_missing_memory_rejected(self):
        common = self.common
        with tempfile.TemporaryDirectory() as temp, patch.object(common, "RAW_DIR", Path(temp)):
            directory = self.fixture(Path(temp), "experiment-43", "powermetrics_zeus", dram=False)
            selected = common.select_machine("mac")
            with self.assertRaisesRegex(SystemExit, "No valid observations"):
                common.load(selected)
            write_json(directory / "manifest.json", {"configuration": {"backend": "powermetrics"}})
            with self.assertRaisesRegex(SystemExit, "mixed measurement backends"):
                common.load(common.select_machine("mac"))


if __name__ == "__main__":
    unittest.main()
