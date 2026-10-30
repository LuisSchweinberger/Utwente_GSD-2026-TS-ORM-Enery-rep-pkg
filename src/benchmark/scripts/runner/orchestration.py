"""Task measurements within persistent ORM blocks and managed complete trials."""
from dataclasses import replace
import json
import socket
import sys
import time
from urllib.parse import urlparse
from urllib.request import urlopen
from .artifacts import TaskPaths, assemble, now, write_json
from .database import Database
from .energy import Measurement
from .processes import Processes, Protocol


class Progress:
    def __init__(self, label):
        self.label, self.active = label, False

    def phase(self, message):
        self.finish()
        print(f"{self.label} | {message}", flush=True)

    def requests(self, completed, total):
        self.active = sys.stdout.isatty()
        print(("\r" if self.active else "") + f"{self.label} | requests ({completed}/{total})",
              end="" if self.active else "\n", flush=True)

    def finish(self):
        if self.active:
            print(flush=True)
            self.active = False


def health(base):
    try:
        with urlopen(base.rstrip("/") + "/health", timeout=1) as response:
            return json.load(response)
    except (OSError, ValueError):
        return None


def check_port(config):
    url = urlparse(config.base_url)
    if url.hostname not in ("localhost", "127.0.0.1") or (url.port or 80) != config.port:
        raise ValueError("BENCHMARK_BASE_URL must address the local API at configured PORT")
    with socket.socket() as connection:
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            connection.bind(("127.0.0.1", config.port))
        except OSError as error:
            raise ValueError(f"PORT={config.port} is already in use") from error


def start_api(config, processes, orm, log):
    server = processes.start("src/server.ts", [orm], log)
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if server.poll() is not None:
            raise RuntimeError(f"API exited; see {log}")
        if health(config.base_url) == {"status": "ok", "orm": orm}:
            return server
        time.sleep(.1)
    raise TimeoutError("API did not become ready")


def execute_task(config, task, orm, paths, processes, label, manifest=None, baseline=None, trial_info=None, server_log=None, clear=True):
    """The API is already running. Restore first, prepare next, time only requests."""
    config.snapshot()
    if {"scenario": task.scenario, "profile": task.profile} not in config.combinations:
        raise ValueError(f"Invalid task: {task.scenario}/{task.profile}")
    if clear:
        paths.clear()
    progress, stage, protocol, runner = Progress(label), "snapshot-restore", None, None
    try:
        progress.phase("restoring snapshot")
        processes.run("src/reset.ts", [], paths.log("reset"))
        stage = "task-preparation"
        runner = processes.start("src/bench.ts", ["--scenario", task.scenario, "--profile", task.profile, "--run-id", paths.run_id],
                                 paths.log("bench"), protocol=True,
                                 environment={"BENCH_CONTROL": "stdio", "BENCHMARK_BASE_URL": config.base_url,
                                              "BENCH_RESULT_DIR": str(paths.results / orm)})
        protocol = Protocol(runner)
        if protocol.receive(60) != "READY":
            raise RuntimeError("Expected READY from request sender")
        stage = "measurement-preparation"
        with Measurement(config.backend, config.interval_ms, paths.result(".measurement.json"), paths.result(".energy.raw")) as meter:
            stage = "request-workload"
            meter.start()
            protocol.send("GO")
            completion = protocol.receive(config.timeout, progress.requests)
            meter.stop()
        progress.finish()
        stage = "result-assembly"
        code = processes.finish(runner)
        result = assemble(paths, manifest, baseline, trial_info)
        if completion != "DONE" or code or result["status"] != "pending_verification":
            raise RuntimeError(f"Task failed; see {paths.result()}")
        stage = "verification"
        progress.phase("verifying")
        processes.run("src/verify.ts", ["--result", str(paths.result())], paths.log("verification"))
        progress.phase("complete")
        return paths.result()
    except BaseException as error:
        progress.finish()
        if paths.result(".execution.json").exists() and paths.result(".measurement.json").exists() and not paths.result().exists():
            try:
                assemble(paths, manifest, baseline, trial_info)
            except (OSError, ValueError):
                pass
        write_json(paths.result(".failure.json"), {"runId": paths.run_id, "orm": orm, "task": {"scenario": task.scenario, "profile": task.profile},
                   "stage": stage, "error": str(error) or type(error).__name__,
                   "serverLog": paths.reference(server_log or paths.log("server")), "benchLog": paths.reference(paths.log("bench"))})
        print(f"Failed: {label} ({stage}); see {paths.reference(paths.result('.failure.json'))}", file=sys.stderr)
        raise
    finally:
        if runner and runner in processes.children:
            processes.stop(runner)
            processes.release(runner)
        if protocol:
            protocol.close(paths.log("bench"))


def run_task(config, task, orm, paths):
    """Standalone debugging command; PostgreSQL/snapshot are supplied by the user."""
    config.validate_backend()
    config.snapshot()
    check_port(config)
    if {"scenario": task.scenario, "profile": task.profile} not in config.combinations:
        raise ValueError("Invalid task")
    paths.clear()
    try:
        with Processes(config) as processes:
            start_api(config, processes, orm, paths.log("server"))
            return execute_task(config, task, orm, paths, processes, f"{orm}-{task.scenario}-{task.profile}", server_log=paths.log("server"), clear=False)
    except BaseException as error:
        if not paths.result(".failure.json").exists():
            write_json(paths.result(".failure.json"), {"runId": paths.run_id, "orm": orm, "stage": "api-startup",
                       "error": str(error) or type(error).__name__, "serverLog": paths.reference(paths.log("server"))})
        raise


def run_trial(config, trial, directory, total, cooldown, orm_cooldown, idle, manifest_path, update=None):
    label = f"Trial {trial.index}/{total} | seed {trial.dataset_seed}"
    progress = Progress(label)
    logs = directory / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    environment = {**config.env, "DATASET_SEED": str(trial.dataset_seed), "SNAPSHOT_DIR": str(directory / "snapshot")}
    local = replace(config, env=environment, snapshot_sha256=None)
    report = {"formatVersion": 2, "index": trial.index, "datasetSeed": trial.dataset_seed, "status": "running", "startedAt": now(),
              "ormOrder": list(trial.orms), "taskOrder": [task.__dict__ for task in trial.tasks],
              "taskMeasurementsCompleted": 0, "ormsCompleted": 0, "ormBlocks": [], "activeTask": None}
    report_path = directory / "manifest.json"
    write_json(report_path, report)
    try:
        check_port(local)
        with Processes(local) as setup, Database(local, setup, logs) as database:
            progress.phase(f"trial cooldown ({cooldown:g}s; PostgreSQL stopped)")
            time.sleep(cooldown)
            progress.phase("starting PostgreSQL")
            database.start()
            progress.phase("generating dataset and saving snapshot")
            setup.run("src/init.ts", [], logs / "init.log", timeout=300)
            snapshot = local.snapshot()
            if snapshot.get("dataset", {}).get("seed") != trial.dataset_seed:
                raise ValueError("Generated snapshot seed differs from trial seed")
            local.snapshot_sha256 = snapshot["sha256"]
            report["snapshot"] = snapshot
            report["postgres"] = local.bridge(local.root, "metadata", local.env)["software"]["postgres"]
            baseline_path = None
            if idle:
                baseline_dir = directory / "baseline"
                baseline_dir.mkdir(parents=True, exist_ok=True)
                baseline_path = baseline_dir / "measurement.json"
                progress.phase(f"measured idle baseline ({idle:g}s)")
                with Measurement(local.backend, local.interval_ms, baseline_path, baseline_dir / "energy.raw", "idle-baseline") as meter:
                    meter.start()
                    time.sleep(idle)
                    meter.stop()
                report["baseline"] = str(baseline_path.relative_to(config.root))
            else:
                report["baseline"] = None
            write_json(report_path, report)
            for position, orm in enumerate(trial.orms, 1):
                progress.phase(f"{orm} | ORM cooldown ({orm_cooldown:g}s)")
                time.sleep(orm_cooldown)
                block = {"orm": orm, "position": position, "status": "running", "startedAt": now(), "results": []}
                report["ormBlocks"].append(block)
                write_json(report_path, report)
                with Processes(local) as processes:
                    server_log = logs / f"{orm}.server.log"
                    server = start_api(local, processes, orm, server_log)
                    block["apiPid"] = server.pid
                    for task_index, task in enumerate(trial.tasks, 1):
                        report["activeTask"] = {"orm": orm, **task.__dict__}
                        write_json(report_path, report)
                        if update:
                            update(orm, task, False)
                        paths = TaskPaths(config.root, directory, logs, orm, f"{task.scenario}-{task.profile}", f"{orm}-")
                        task_label = f"Trial {trial.index}/{total} | ORM {position}/3 {orm} | task {task_index}/{len(trial.tasks)} {task.scenario}-{task.profile}"
                        path = execute_task(local, task, orm, paths, processes, task_label, manifest_path, baseline_path,
                                            {"index": trial.index, "datasetSeed": trial.dataset_seed, "ormPosition": position, "taskPosition": task_index,
                                             "manifest": str(report_path.relative_to(config.root))}, server_log)
                        block["results"].append(str(path.relative_to(config.root)))
                        report["taskMeasurementsCompleted"] += 1
                        if update:
                            update(orm, task, True)
                    block.update(status="completed", finishedAt=now())
                    write_json(directory / orm / "report.json", block)
                block["apiStoppedAt"] = now()
                report.update(ormsCompleted=position, activeTask=None)
                write_json(directory / orm / "report.json", block)
                write_json(report_path, report)
                progress.phase(f"{orm} | API stopped")
            progress.phase("stopping PostgreSQL")
        report["status"] = "completed"
        progress.phase("complete")
    except BaseException as error:
        report.update(status="failed", error=str(error) or type(error).__name__)
        raise
    finally:
        report["finishedAt"] = now()
        write_json(report_path, report)
    return report
