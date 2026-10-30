"""Shared data loading for the statistical analysis of the ORM benchmark.

Reads the per-task files produced by the benchmark controller
(results-<machine>/experiment-*/trials/trial-*/<orm>/<task>.measurement.json
plus the matching <task>.json verification file). The result directories are
only read, never written.

Units are kept exactly as stored by the benchmark (no conversion happens here):
  * execution time  -> milliseconds (timing.workloadElapsedMs)
  * energy          -> joules       (domains[].energyJ)
See README.md for the upstream conversions the benchmark controller applied.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field, replace
from pathlib import Path

ANALYSIS_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = ANALYSIS_DIR.parents[1]
RAW_DIR = PACKAGE_DIR / "data" / "raw"
RESULTS_DIR = PACKAGE_DIR / "data" / "results" / "reproduced"

ORMS = ("drizzle", "prisma", "sequelize")

TIME = "execution_time"
CPU = "cpu_energy"
MEMORY = "memory_energy"
METRICS = (TIME, CPU, MEMORY)

METRIC_LABELS = {
    TIME: "Execution time",
    CPU: "CPU energy consumption",
    MEMORY: "Memory energy consumption",
}
METRIC_UNITS = {TIME: "ms", CPU: "J", MEMORY: "J"}


@dataclass(frozen=True)
class Machine:
    key: str
    title: str
    results_dir: str
    # (field, value) used to pick the energy domain from measurement.json.
    # None means the backend does not measure that domain on this machine.
    cpu_domain: tuple[str, str]
    memory_domain: tuple[str, str] | None
    domain_notes: dict[str, str] = field(default_factory=dict)
    experiment_path: Path | None = None
    backend: str | None = None


MACHINES = {
    "intel": Machine(
        key="intel",
        title="Intel (Linux, RAPL)",
        results_dir="intel",
        cpu_domain=("id", "intel-rapl:0"),
        memory_domain=("id", "intel-rapl:0:2"),
        domain_notes={
            CPU: "RAPL `intel-rapl:0` (package-0): whole CPU package, includes the core and uncore sub-domains.",
            MEMORY: "RAPL `intel-rapl:0:2` (dram).",
        },
    ),
    "mac": Machine(
        key="mac",
        title="Apple Silicon Mac (macOS, powermetrics)",
        results_dir="mac",
        cpu_domain=("name", "cpu"),
        memory_domain=None,
        domain_notes={
            CPU: "powermetrics `cpu` domain (cpu_power sampler).",
            MEMORY: "Not measured: powermetrics only reported cpu/gpu/ane domains on this machine. "
            "Per documentation/methodology.md, missing DRAM stays unavailable and CPU energy is not substituted.",
        },
    ),
}


@dataclass(frozen=True)
class Observation:
    trial: str
    orm: str
    operation: str
    values: dict[str, float]  # metric -> value in its original unit


def select_machine(key: str, experiment: str | None = None) -> Machine:
    """Select one archived experiment; write only to data/results/reproduced/."""
    machine = MACHINES[key]
    root = RAW_DIR / machine.results_dir
    if experiment is not None:
        if Path(experiment).name != experiment or not experiment.startswith("experiment-"):
            raise SystemExit("--experiment must be a directory name such as experiment-42")
        experiments = [root / experiment]
    else:
        experiments = sorted(root.glob("experiment-*"))
    if len(experiments) != 1 or not experiments[0].is_dir():
        raise SystemExit(f"Select exactly one experiment in {root} with --experiment")
    selected = experiments[0]
    manifest = json.loads((selected / "manifest.json").read_text(encoding="utf-8"))
    backend = manifest["configuration"]["backend"]
    combined = key == "mac" and backend == "powermetrics_zeus"
    notes = dict(machine.domain_notes)
    if combined:
        notes[MEMORY] = "IOReport unified-memory Energy Model estimate via zeus-apple-silicon `dram_mj`; stored as J."
    return replace(machine, experiment_path=selected, backend=backend,
                   title="Apple Silicon Mac (macOS, powermetrics + Zeus)" if combined else machine.title,
                   memory_domain=("id", "ioreport:dram") if combined else machine.memory_domain,
                   domain_notes=notes)


def available_metrics(machine: Machine) -> list[str]:
    return [m for m in METRICS if m != MEMORY or machine.memory_domain is not None]


def _domain_energy(domains: list[dict], selector: tuple[str, str]) -> float | None:
    key, wanted = selector
    for domain in domains:
        if domain.get(key) == wanted:
            return domain.get("energyJ")
    return None


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value)


def load(machine: Machine) -> tuple[list[Observation], list[str]]:
    """Return valid observations and a list of human-readable exclusion notes.

    An observation is valid when both the energy measurement and the task's
    correctness verification have status "valid" and the metric is a finite number.
    """
    experiments = ([machine.experiment_path] if machine.experiment_path is not None else
                    sorted((RAW_DIR / machine.results_dir).glob("experiment-*")))
    if len(experiments) != 1:
        raise SystemExit(f"Expected exactly one experiment in {machine.results_dir}, found {len(experiments)}")

    observations: list[Observation] = []
    excluded: list[str] = []
    for path in sorted(experiments[0].glob("trials/trial-*/*/*.measurement.json")):
        orm = path.parent.name
        if orm not in ORMS:
            continue
        trial = path.parent.parent.name
        measurement = json.loads(path.read_text(encoding="utf-8"))
        task = json.loads(path.with_name(path.name.replace(".measurement.json", ".json")).read_text(encoding="utf-8"))
        operation = f"{task['scenario']}-{task['profile']}"
        label = f"{trial}/{orm}/{operation}"

        if machine.backend is not None and measurement.get("backend") != machine.backend:
            raise SystemExit(f"{label}: mixed measurement backends in selected experiment")

        if measurement.get("status") != "valid" or task.get("status") != "valid":
            excluded.append(f"{label}: status measurement={measurement.get('status')} task={task.get('status')}")
            continue

        timing = measurement["timing"]
        elapsed_ms = timing["workloadElapsedMs"]
        # Sanity check of the stored ms value against the raw monotonic ns stamps.
        raw_ms = (timing["workloadFinishedMonotonicNs"] - timing["workloadStartedMonotonicNs"]) / 1e6
        if not math.isclose(elapsed_ms, raw_ms, rel_tol=1e-9, abs_tol=1e-6):
            raise SystemExit(f"{label}: workloadElapsedMs {elapsed_ms} != monotonic delta {raw_ms} ms")

        values = {
            TIME: elapsed_ms,
            CPU: _domain_energy(measurement["domains"], machine.cpu_domain),
        }
        if machine.memory_domain is not None:
            values[MEMORY] = _domain_energy(measurement["domains"], machine.memory_domain)

        bad = [m for m, v in values.items() if not _is_number(v)]
        if bad:
            excluded.append(f"{label}: missing/non-numeric {', '.join(bad)}")
            continue
        observations.append(Observation(trial, orm, operation, values))

    if not observations:
        raise SystemExit(f"No valid observations found in {machine.results_dir}")
    return observations, excluded


def operations(observations: list[Observation]) -> list[str]:
    return sorted({o.operation for o in observations})


def series(observations: list[Observation], operation: str, orm: str, metric: str) -> list[float]:
    return [o.values[metric] for o in observations if o.operation == operation and o.orm == orm]


def paired(observations: list[Observation], operation: str, metric_a: str, metric_b: str, orm: str | None = None):
    rows = [o for o in observations if o.operation == operation and (orm is None or o.orm == orm)]
    return [o.values[metric_a] for o in rows], [o.values[metric_b] for o in rows]


def output_dir(machine: Machine) -> Path:
    path = RESULTS_DIR / machine.key
    path.mkdir(parents=True, exist_ok=True)
    return path
