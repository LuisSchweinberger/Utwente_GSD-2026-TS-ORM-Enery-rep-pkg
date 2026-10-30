"""Task → ORM block → complete trial → experiment, using one controller."""
import argparse
from pathlib import Path
import signal
import sys
from .artifacts import ORMS, RUN_ID, TaskPaths, clear_series, now, write_json
from .config import Config, number
from .manifest import build_manifest
from .orchestration import check_port, run_task, run_trial
from .schedule import Task, build_schedule, write_schedule
from .summary import summarize

ROOT = Path(__file__).resolve().parents[2]


def parser():
    cli = argparse.ArgumentParser(description="PetClinic experiment: each trial covers all ORMs and tasks")
    commands = cli.add_subparsers(dest="command", required=True)
    task = commands.add_parser("task", help="one ORM + scenario/profile (PostgreSQL/snapshot already available)")
    task.add_argument("--orm", choices=ORMS, required=True)
    task.add_argument("--scenario", required=True)
    task.add_argument("--profile", required=True)
    task.add_argument("--run-id", required=True)
    for kind in ("trial", "pilot", "experiment", "schedule"):
        sub = commands.add_parser(kind)
        sub.add_argument("--seed", type=int)
        if kind != "trial":
            sub.add_argument("--trials", "--repetitions", dest="trials", type=int, help="complete trials; multiples of 3 balance ORM positions")
        else:
            sub.add_argument("--run-id", help="optional name for this complete-trial output")
        if kind == "schedule":
            sub.add_argument("--kind", choices=("pilot", "experiment"), default="pilot")
            sub.add_argument("--output", type=Path)
        else:
            sub.add_argument("--trial-cooldown-seconds", "--cooldown-seconds", dest="trial_cooldown", type=float)
            sub.add_argument("--orm-cooldown-seconds", dest="orm_cooldown", type=float)
            sub.add_argument("--idle-seconds", type=float)
    return cli


def run_series(config, kind, seed, count, cooldown, orm_cooldown, idle, name=None):
    config.validate_backend(experiment=kind == "experiment")
    check_port(config)
    trials = build_schedule(config.combinations, seed, count)
    manifest = build_manifest(config, kind, seed, count, cooldown, orm_cooldown, idle)
    directory = config.root / "results" / (f"trial-{name}" if name else f"{kind}-{seed}")
    clear_series(config.root, directory)
    write_schedule(directory / "schedule.tsv", trials)
    manifest_path = directory / "manifest.json"
    manifest.update(status="running", startedAt=now())
    write_json(manifest_path, manifest)
    print(f"{kind.title()} {seed}: {count} complete trials, {manifest['taskMeasurementsPlanned']} task measurements → {directory.relative_to(config.root)}", flush=True)
    if count > 1 and count % 3:
        print("Note: a trial count divisible by 3 balances ORM positions exactly.", flush=True)
    try:
        for trial in trials:
            manifest["activeTrial"] = trial.index
            write_json(manifest_path, manifest)
            def update(orm, task, complete):
                manifest.update(activeOrm=orm, activeTask=task.__dict__)
                if complete:
                    manifest["taskMeasurementsCompleted"] += 1
                write_json(manifest_path, manifest)
            report = run_trial(config, trial, directory / "trials" / f"trial-{trial.index:03d}", count,
                               cooldown, orm_cooldown, idle, manifest_path, update)
            manifest.update(trialsCompleted=trial.index, activeTrial=None, activeOrm=None, activeTask=None)
            if manifest["software"].get("postgres") is None:
                manifest["software"]["postgres"] = report["postgres"]
            write_json(manifest_path, manifest)
    except BaseException as error:
        manifest.update(status="failed", error=str(error) or type(error).__name__)
        raise
    else:
        manifest["status"] = "completed"
        print(f"{kind.title()} complete: {count}/{count} trials", flush=True)
    finally:
        manifest["finishedAt"] = now()
        write_json(manifest_path, manifest)
        summarize(directory, manifest)


def main(argv=None):
    args = parser().parse_args(argv)
    def interrupted(_signal, _frame):
        raise KeyboardInterrupt("Interrupted")
    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    try:
        overrides = {}
        for attribute, variable in (("trial_cooldown", "TRIAL_COOLDOWN_SECONDS"), ("orm_cooldown", "ORM_COOLDOWN_SECONDS"),
                                    ("idle_seconds", "IDLE_SECONDS"), ("trials", "TRIALS"), ("seed", "SEED")):
            value = getattr(args, attribute, None)
            if value is not None:
                overrides[variable] = str(value)
        config = Config.load(ROOT, overrides)
        if args.command == "task":
            paths = TaskPaths(config.root, config.root / "results", config.root / "logs", args.orm, args.run_id)
            run_task(config, Task(args.scenario, args.profile), args.orm, paths)
            return 0
        kind = args.kind if args.command == "schedule" else args.command
        seed = config.seed
        count = 1 if kind == "trial" else (config.trial_count or (10 if kind == "experiment" else 3))
        trials = build_schedule(config.combinations, seed, count)
        if args.command == "schedule":
            output = args.output or config.root / f"results/{kind}-{seed}/schedule.tsv"
            if output.exists():
                print(f"Warning: overwriting existing schedule {output}", file=sys.stderr)
            write_schedule(output, trials)
            print(f"Scheduled {count} complete trials / {count * len(ORMS) * len(config.combinations)} task measurements → {output}")
            return 0
        name = getattr(args, "run_id", None)
        if name and not RUN_ID.fullmatch(name):
            raise ValueError("Invalid run ID")
        run_series(config, kind, seed, count, config.cooldown, config.orm_cooldown, config.idle_seconds, name)
        return 0
    except KeyboardInterrupt:
        print("Interrupted; owned resources cleaned up; partial results preserved.", file=sys.stderr)
        return 130
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
