"""Runtime metadata before startup; per-trial metadata records PostgreSQL/datasets."""
import hashlib
from pathlib import Path
import platform
import socket
import subprocess
from urllib.parse import urlparse
from .artifacts import ORMS, now
from .energy import collector_metadata


def command(root, program, arguments):
    try:
        return subprocess.check_output([program, *arguments], cwd=root, stderr=subprocess.DEVNULL, text=True, timeout=10).strip()
    except (OSError, subprocess.SubprocessError):
        return None


def optional_file(path):
    try:
        return Path(path).read_text().strip()
    except OSError:
        return None


def build_manifest(config, kind, seed, count, cooldown, orm_cooldown, idle):
    metadata = config.bridge(config.root, "runtime", config.env)
    url = urlparse(config.env.get("DATABASE_URL", ""))
    system = platform.system()
    return {
        "formatVersion": 2, "kind": kind, "seed": seed, "status": "prepared", "createdAt": now(),
        "trialsPlanned": count, "trialsCompleted": 0, "taskMeasurementsPlanned": count * len(ORMS) * len(config.combinations),
        "taskMeasurementsCompleted": 0, "activeTrial": None,
        "configuration": {"size": config.size, "queryCount": config.query_count, "backend": config.backend,
                          "collectors": collector_metadata(config.backend),
                          "sampleIntervalMs": config.interval_ms, "trialCooldownSeconds": cooldown,
                          "ormCooldownSeconds": orm_cooldown, "idleSeconds": idle, "workloadTimeoutSeconds": config.timeout,
                          "baselineFrequency": "once per complete trial", "datasetSeed": "experiment seed + zero-based trial index",
                          "taskOrder": "shuffled once per trial, identical for all ORMs", "ormOrder": "rotate by one position per trial",
                          "apiLifecycle": "one process per ORM block", "postgresLifecycle": "start/stop per complete trial",
                          "warmupRequests": 0, "ormPoolMaximum": 5},
        "tasks": config.combinations, "orms": list(ORMS),
        "host": {**metadata["host"], "machineId": config.env.get("EXPERIMENT_MACHINE_ID") or socket.gethostname(),
                 "system": system, "release": platform.release(), "architecture": platform.machine(),
                 "macOSVersion": command(config.root, "sw_vers", ["-productVersion"]) if system == "Darwin" else None,
                 "linuxDistribution": optional_file("/etc/os-release") if system == "Linux" else None,
                 "cpuGovernor": optional_file("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor") if system == "Linux" else None,
                 "powerState": command(config.root, "pmset", ["-g", "batt"]) if system == "Darwin" else None},
        "software": {**metadata["software"], "python": platform.python_version(),
                     "gitCommit": command(config.root, "git", ["rev-parse", "HEAD"]),
                     "gitDirty": bool(command(config.root, "git", ["status", "--porcelain"])),
                     "packageLockSha256": hashlib.sha256((config.root / "package-lock.json").read_bytes()).hexdigest()},
        "databaseEndpoint": {"host": url.hostname, "port": url.port or 5432, "database": url.path.lstrip("/")},
    }
