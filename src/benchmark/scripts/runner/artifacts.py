"""Task paths, run-folder replacement, and result assembly."""
from dataclasses import dataclass
import datetime as dt
import json
from pathlib import Path
import re
import shutil
import sys

ORMS = ("prisma", "sequelize", "drizzle")
RUN_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,119}\Z")


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


@dataclass(frozen=True)
class TaskPaths:
    root: Path
    results: Path
    logs: Path
    orm: str
    run_id: str
    log_prefix: str = ""

    def __post_init__(self):
        if self.orm not in ORMS or not RUN_ID.fullmatch(self.run_id):
            raise ValueError("Invalid ORM or run ID")

    def result(self, suffix=".json"):
        return self.results / self.orm / (self.run_id + suffix)

    def log(self, phase):
        return self.logs / f"{self.log_prefix}{self.run_id}.{phase}.log"

    def reference(self, path):
        try:
            return str(Path(path).relative_to(self.root))
        except ValueError:
            return str(path)

    def generated(self):
        suffixes = (".json", ".failure.json", ".execution.json", ".measurement.json", ".energy.raw",
                    ".energy.raw.memory.json", ".baseline.raw.memory.json",
                    ".energy.raw.stderr", ".energy.raw.samples.jsonl", ".baseline.json", ".baseline.raw",
                    ".baseline.raw.stderr", ".baseline.raw.samples.jsonl")
        return [self.result(suffix) for suffix in suffixes] + [
            self.log(phase) for phase in ("server", "bench", "reset", "measurement", "verification", "baseline")]

    def clear(self, quiet=False):
        existing = [path for path in self.generated() if path.exists() or path.is_symlink()]
        if existing and not quiet:
            print(f"Warning: overwriting previous task {self.run_id} in {self.reference(self.results / self.orm)}", file=sys.stderr)
        for path in existing:
            path.unlink()
        (self.results / self.orm).mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)


def clear_series(root, directory):
    root, directory = Path(root).resolve(), Path(directory)
    if directory.parent.resolve() != (root / "results").resolve():
        raise ValueError("Run cleanup must target a direct child of the results directory")
    if not directory.exists() and not directory.is_symlink():
        return
    print(f"Warning: overwriting previous run in results/{directory.name}", file=sys.stderr)
    if directory.is_symlink():
        directory.unlink()
    else:
        shutil.rmtree(directory)


def assemble(paths, manifest=None, baseline_path=None, trial_info=None):
    result = json.loads(paths.result(".execution.json").read_text())
    measurement = json.loads(paths.result(".measurement.json").read_text())
    result["measurement"] = measurement
    refs = {"execution": paths.reference(paths.result(".execution.json")),
            "measurement": paths.reference(paths.result(".measurement.json"))}
    if measurement["backend"] != "none":
        refs["rawEnergy"] = paths.reference(paths.result(".energy.raw"))
    if measurement["backend"] in ("powermetrics", "powermetrics_zeus"):
        refs["normalizedSamples"] = paths.reference(paths.result(".energy.raw.samples.jsonl"))
    if measurement["backend"] == "powermetrics_zeus":
        refs["rawMemoryEnergy"] = paths.reference(paths.result(".energy.raw.memory.json"))
    if manifest:
        refs["experimentManifest"] = paths.reference(manifest)
    shared_baseline = baseline_path is not None
    baseline_path = baseline_path or paths.result(".baseline.json")
    if baseline_path.exists():
        baseline = json.loads(baseline_path.read_text())
        if shared_baseline:
            result["idleBaselineRef"] = paths.reference(baseline_path)
        else:
            result["idleBaseline"] = baseline
        refs["idleBaseline"] = paths.reference(baseline_path)
        if baseline["backend"] != "none" and not shared_baseline:
            refs["idleBaselineRaw"] = paths.reference(paths.result(".baseline.raw"))
        if baseline["backend"] in ("powermetrics", "powermetrics_zeus") and not shared_baseline:
            refs["idleBaselineSamples"] = paths.reference(paths.result(".baseline.raw.samples.jsonl"))
        if baseline["backend"] == "powermetrics_zeus":
            raw = baseline_path.parent / "energy.raw" if shared_baseline else paths.result(".baseline.raw")
            refs["idleBaselineMemoryRaw"] = paths.reference(Path(str(raw) + ".memory.json"))
        if baseline["status"] != "valid" or baseline["backend"] != measurement["backend"]:
            result["status"] = "baseline_failed"
    if "timing" in measurement:
        result.update(measurement["timing"])
        result["throughputOpsPerSecond"] = result["requestCountCompleted"] / (result["workloadElapsedMs"] / 1000)
    if measurement["status"] != "valid" and result["status"] == "pending_verification":
        result["status"] = "measurement_failed"
    result["artifacts"] = refs
    result["task"] = {"scenario": result["scenario"], "profile": result["profile"]}
    if trial_info:
        result["trial"] = trial_info
    write_json(paths.result(), result)
    return result
