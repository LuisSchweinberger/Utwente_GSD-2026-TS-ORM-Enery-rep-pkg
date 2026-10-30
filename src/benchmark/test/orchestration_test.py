"""Trial hierarchy, reproducibility, aggregation, failure cleanup and process control."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from runner.artifacts import TaskPaths, write_json
from runner.cli import run_series
from runner.config import Config
from runner.database import Database
from runner.orchestration import run_trial
from runner.processes import Processes, Protocol
from runner.schedule import build_schedule
from runner.summary import summarize


class OrchestrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.combinations = Config.bridge(ROOT, "config", dict(os.environ))["combinations"]

    def config(self, root):
        return Config(Path(root), {"DATABASE_URL": "postgresql://benchmark:benchmark@localhost:55432/orm_benchmark"},
                      self.combinations, 10, 5, 3197, "none", 100, 1, 30)

    def test_schedule_shares_shuffled_tasks_rotates_orms_and_increments_seed(self):
        trials = build_schedule(self.combinations, 42, 3)
        self.assertEqual([trial.dataset_seed for trial in trials], [42, 43, 44])
        self.assertEqual([trial.orms for trial in trials], [("prisma", "sequelize", "drizzle"),
                         ("sequelize", "drizzle", "prisma"), ("drizzle", "prisma", "sequelize")])
        self.assertEqual(trials, build_schedule(self.combinations, 42, 3))
        self.assertNotEqual(trials[0].tasks, trials[1].tasks)
        for trial in trials:
            self.assertEqual(len(trial.tasks), 14)
            sequences = [[row[5:] for row in trial.rows() if row[3] == orm] for orm in trial.orms]
            self.assertEqual(sequences[0], sequences[1])
            self.assertEqual(sequences[1], sequences[2])
        full = build_schedule(self.combinations, 42, 10)
        self.assertEqual(sum(len(list(trial.rows())) for trial in full), 420)
        with self.assertRaises(ValueError):
            build_schedule(self.combinations, 0xffffffff, 2)

    def test_configuration_freezes_values_and_cli_overrides_invalid_file_values(self):
        bridge = {"environment": {"SIZE": "20", "QUERY_COUNT": "7", "PORT": "3197", "ORM_COOLDOWN_SECONDS": "10"}, "combinations": self.combinations}
        with patch.object(Config, "bridge", return_value=bridge) as loader:
            config = Config.load(ROOT)
        loader.assert_called_once()
        bridge["environment"]["QUERY_COUNT"] = "19"
        self.assertEqual(config.query_count, 7)
        self.assertEqual(config.env["QUERY_COUNT"], "7")
        self.assertEqual(config.orm_cooldown, 10)
        bridge["environment"]["TRIAL_COOLDOWN_SECONDS"] = "invalid"
        with patch.object(Config, "bridge", return_value=bridge):
            overridden = Config.load(ROOT, {"TRIAL_COOLDOWN_SECONDS": "1", "IDLE_SECONDS": "0.2", "TRIALS": "3"})
        self.assertEqual((overridden.cooldown, overridden.idle_seconds, overridden.trial_count), (1, .2, 3))

    def test_snapshot_checksum_and_pinned_trial_dataset(self):
        with tempfile.TemporaryDirectory() as temp:
            config = self.config(temp)
            directory = Path(temp) / "db/snapshot"
            directory.mkdir(parents=True)
            content = b"-- fixture snapshot\n"
            (directory / "baseline.sql").write_bytes(content)
            metadata = {"layoutVersion": 2, "size": 10, "profiles": {"populated": {}}, "sha256": hashlib.sha256(content).hexdigest()}
            write_json(directory / "baseline.json", metadata)
            config.snapshot_sha256 = config.snapshot()["sha256"]
            (directory / "baseline.sql").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "checksum"):
                config.snapshot()
            metadata["sha256"] = hashlib.sha256(b"changed").hexdigest()
            write_json(directory / "baseline.json", metadata)
            with self.assertRaisesRegex(ValueError, "changed during"):
                config.snapshot()

    def test_task_overwrite_preserves_unrelated_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = TaskPaths(root, root / "results", root / "logs", "prisma", "same")
            paths.clear()
            for path in paths.generated():
                path.write_text("old")
            unrelated = paths.result().parent / "notes.txt"
            unrelated.write_text("keep")
            with contextlib.redirect_stderr(io.StringIO()) as output:
                paths.clear()
            self.assertIn("overwriting previous task", output.getvalue())
            self.assertFalse(any(path.exists() for path in paths.generated()))
            self.assertTrue(unrelated.exists())

    def test_series_nested_outputs_summary_and_stale_rerun_cleanup(self):
        with tempfile.TemporaryDirectory() as temp:
            root, calls = Path(temp), []
            config = self.config(root)
            def metadata(cfg, kind, seed, count, *args):
                return {"tasks": cfg.combinations, "software": {"postgres": None}, "configuration": {},
                        "trialsPlanned": count, "trialsCompleted": 0, "taskMeasurementsPlanned": count * 42,
                        "taskMeasurementsCompleted": 0}
            def trial_runner(cfg, trial, directory, total, cooldown, orm_cooldown, idle, manifest, update):
                calls.append((trial, cooldown, orm_cooldown, idle))
                write_json(directory / "baseline/measurement.json", {"kind": "idle-baseline", "status": "valid"})
                write_json(directory / "snapshot/baseline.json", {"seed": trial.dataset_seed})
                (directory / "snapshot/baseline.sql").write_text("fixture")
                for orm in trial.orms:
                    for task in trial.tasks:
                        paths = TaskPaths(root, directory, directory / "logs", orm, f"{task.scenario}-{task.profile}", f"{orm}-")
                        paths.clear()
                        update(orm, task, False)
                        write_json(paths.result(), {"status": "valid", "orm": orm, **task.__dict__,
                                   "workloadElapsedMs": trial.index * 10, "throughputOpsPerSecond": 5,
                                   "measurement": {"domains": []}})
                        update(orm, task, True)
                return {"postgres": {"version": "fixture"}}
            output = io.StringIO()
            with patch.object(config, "validate_backend"), patch("runner.cli.check_port"), \
                    patch("runner.cli.build_manifest", side_effect=metadata), patch("runner.cli.run_trial", side_effect=trial_runner), \
                    contextlib.redirect_stdout(output):
                run_series(config, "experiment", 42, 3, 30, 10, 30)
            directory = root / "results/experiment-42"
            manifest = json.loads((directory / "manifest.json").read_text())
            self.assertEqual((manifest["trialsCompleted"], manifest["taskMeasurementsCompleted"]), (3, 126))
            self.assertEqual(len(calls), 3)
            self.assertTrue(all(values[1:] == (30, 10, 30) for values in calls))
            summary = json.loads((directory / "summary.json").read_text())
            self.assertTrue(summary["complete"])
            self.assertEqual(len(summary["groups"]), 42)
            self.assertEqual(summary["groups"][0]["metrics"]["workloadElapsedMs"], {"count": 3, "mean": 20, "median": 20})
            unrelated = directory / "trials/trial-001/prisma/notes.txt"
            unrelated.write_text("keep")
            with patch.object(config, "validate_backend"), patch("runner.cli.check_port"), \
                    patch("runner.cli.build_manifest", side_effect=metadata), patch("runner.cli.run_trial", side_effect=RuntimeError("fixture failure")), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaisesRegex(RuntimeError, "fixture failure"):
                    run_series(config, "experiment", 42, 1, .25, 10, 30)
            self.assertEqual(list(directory.glob("trials/trial-*/*/*.json")), [])
            self.assertFalse(unrelated.exists())
            self.assertFalse((directory / "trials").exists())
            manifest = json.loads((directory / "manifest.json").read_text())
            self.assertEqual(manifest["status"], "failed")
            self.assertEqual(manifest["activeTrial"], 1)
            self.assertFalse(json.loads((directory / "summary.json").read_text())["complete"])
            with patch.object(config, "validate_backend"), patch("runner.cli.check_port"), \
                    patch("runner.cli.build_manifest", side_effect=metadata), patch("runner.cli.run_trial", side_effect=trial_runner), \
                    contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                run_series(config, "experiment", 42, 1, 0, 0, 0)
            self.assertEqual([path.name for path in (directory / "trials").iterdir()], ["trial-001"])
            self.assertEqual(json.loads((directory / "manifest.json").read_text())["trialsPlanned"], 1)
            self.assertEqual(json.loads((directory / "summary.json").read_text())["groups"][0]["validTaskCount"], 1)

    def test_trial_one_baseline_three_api_blocks_and_database_cleanup_on_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            root, events = Path(temp), []
            config = self.config(root)
            trial = build_schedule(self.combinations, 42, 1)[0]
            class FakeProcesses:
                def __init__(self, cfg): self.role = None
                def __enter__(self): return self
                def __exit__(self, *args):
                    if self.role: events.append(("api-stop", self.role))
                def run(self, source, *args, **kwargs): events.append(("command", source))
            class FakeDatabase:
                def __init__(self, *args): pass
                def __enter__(self): return self
                def start(self): events.append(("postgres-start",))
                def __exit__(self, *args): events.append(("postgres-stop",))
            class FakeMeasurement:
                def __init__(self, backend, interval, output, raw, kind): self.output = output
                def __enter__(self): return self
                def start(self): events.append(("baseline-start",))
                def stop(self): events.append(("baseline-stop",))
                def __exit__(self, *args): write_json(self.output, {"status": "valid"})
            def api(cfg, processes, orm, log):
                events.append(("api-start", orm))
                processes.role = orm
                return SimpleNamespace(pid=123)
            def task(cfg, task, orm, paths, *args):
                events.append(("task", orm, task.scenario, task.profile))
                return paths.result()
            with patch("runner.orchestration.Processes", FakeProcesses), patch("runner.orchestration.Database", FakeDatabase), \
                    patch("runner.orchestration.Measurement", FakeMeasurement), patch("runner.orchestration.start_api", side_effect=api), \
                    patch("runner.orchestration.execute_task", side_effect=task), patch("runner.orchestration.check_port"), \
                    patch("runner.orchestration.time.sleep"), patch.object(Config, "snapshot", return_value={"sha256": "fixture", "dataset": {"seed": 42}}), \
                    patch.object(Config, "bridge", return_value={"software": {"postgres": {}}}), contextlib.redirect_stdout(io.StringIO()):
                report = run_trial(config, trial, root / "trials/trial-001", 1, 30, 10, 30, root / "manifest.json")
            self.assertEqual(report["taskMeasurementsCompleted"], 42)
            self.assertEqual(events.count(("baseline-start",)), 1)
            self.assertEqual(events.count(("postgres-start",)), 1)
            self.assertEqual(events.count(("postgres-stop",)), 1)
            self.assertEqual(len([event for event in events if event[0] == "api-start"]), 3)
            self.assertLess(events.index(("baseline-stop",)), events.index(("api-start", "prisma")))
            self.assertEqual(events[-1], ("postgres-stop",))
            events.clear()
            with patch("runner.orchestration.Processes", FakeProcesses), patch("runner.orchestration.Database", FakeDatabase), \
                    patch("runner.orchestration.Measurement", FakeMeasurement), patch("runner.orchestration.start_api", side_effect=api), \
                    patch("runner.orchestration.execute_task", side_effect=RuntimeError("task failed")), patch("runner.orchestration.check_port"), \
                    patch("runner.orchestration.time.sleep"), patch.object(Config, "snapshot", return_value={"sha256": "fixture", "dataset": {"seed": 42}}), \
                    patch.object(Config, "bridge", return_value={"software": {"postgres": {}}}), contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(RuntimeError, "task failed"):
                    run_trial(config, trial, root / "trials/trial-002", 1, 30, 10, 30, root / "manifest.json")
            self.assertEqual(events[-2:], [("api-stop", "prisma"), ("postgres-stop",)])

    def test_summary_excludes_invalid_results_and_keeps_hardware_domains_separate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = {"tasks": [{"scenario": "read-pet", "profile": "populated"}], "trialsPlanned": 3, "trialsCompleted": 2, "status": "failed"}
            for index, duration in ((1, 10), (2, 30), (3, 999)):
                write_json(root / f"trials/trial-{index:03d}/prisma/read-pet-populated.json", {"orm": "prisma", "scenario": "read-pet", "profile": "populated",
                           "status": "invalid" if index == 3 else "valid", "workloadElapsedMs": duration, "throughputOpsPerSecond": 1,
                           "measurement": {"domains": [{"id": "package0-core", "name": "core", "energyJ": 2}, {"id": "package1-core", "name": "core", "energyJ": 4}]}})
            summary = summarize(root, manifest)
            self.assertFalse(summary["complete"])
            row = summary["groups"][0]
            self.assertEqual(row["metrics"]["workloadElapsedMs"], {"count": 2, "mean": 20, "median": 20})
            self.assertEqual(len(row["energyDomains"]), 2)
            self.assertIsNone(row["energyDomains"]["package0-core:core"]["averagePowerW"]["mean"])

    def test_postgres_cleanup_after_partial_startup_and_interruption(self):
        with tempfile.TemporaryDirectory() as temp:
            config = self.config(temp)
            calls = []
            class Commands:
                fail_start = False
                def command(self, command, *args, **kwargs):
                    calls.append(command)
                    if command[2] == "config":
                        return json.dumps({"services": {"postgres": {"environment": {
                            "POSTGRES_USER": "benchmark", "POSTGRES_PASSWORD": "benchmark", "POSTGRES_DB": "orm_benchmark"},
                            "ports": [{"target": 5432, "published": "55432"}]}}})
                    if command[2] == "up" and self.fail_start:
                        raise RuntimeError("partial startup failure")
                    return ""
            commands = Commands()
            commands.fail_start = True
            with self.assertRaisesRegex(RuntimeError, "partial startup"):
                with Database(config, commands, Path(temp)) as database:
                    database.start()
            self.assertEqual(sum(command[2] == "stop" for command in calls), 1)
            calls.clear()
            commands.fail_start = False
            with self.assertRaises(KeyboardInterrupt):
                with Database(config, commands, Path(temp)) as database:
                    database.start()
                    raise KeyboardInterrupt("interrupted")
            self.assertEqual(sum(command[2] == "stop" for command in calls), 1)

    def test_protocol_timeout_is_not_extended_by_progress(self):
        program = "import time; exec(\"for i in range(100):\\n print('PROGRESS 1 100', flush=True)\\n time.sleep(.02)\")"
        child = subprocess.Popen([sys.executable, "-c", program], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, start_new_session=True)
        protocol = Protocol(child)
        try:
            started = time.monotonic()
            with self.assertRaises(TimeoutError): protocol.receive(.1, lambda *_: None)
            self.assertLess(time.monotonic() - started, .4)
        finally:
            protocol.selector.close()
            Processes.stop(child)

    def test_cleanup_stops_descendant_processes(self):
        with tempfile.TemporaryDirectory() as temp:
            marker = Path(temp) / "child-stopped"
            descendant = ("import pathlib,signal,time; "
                          f"signal.signal(signal.SIGTERM, lambda *_: (pathlib.Path({str(marker)!r}).write_text('stopped'), exit(0))); "
                          "print('READY', flush=True); time.sleep(60)")
            parent = ("import subprocess,sys,time; "
                      f"child=subprocess.Popen([sys.executable,'-c',{descendant!r}],stdout=subprocess.PIPE); "
                      "child.stdout.readline(); print('READY',flush=True); time.sleep(60)")
            process = subprocess.Popen([sys.executable, "-c", parent], stdout=subprocess.PIPE, start_new_session=True)
            try:
                self.assertEqual(process.stdout.readline().strip(), b"READY")
                Processes.stop(process)
                deadline = time.monotonic() + 2
                while not marker.exists() and time.monotonic() < deadline: time.sleep(.01)
                self.assertEqual(marker.read_text(), "stopped")
            finally: Processes.stop(process)


if __name__ == "__main__":
    unittest.main()
