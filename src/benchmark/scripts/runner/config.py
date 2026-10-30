"""Resolve .env once through the existing Node dotenv package, then freeze it."""
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import subprocess


def number(raw, name, default, minimum, maximum, integer=False):
    value = default if raw is None or raw == "" else float(raw)
    if not math.isfinite(value) or not minimum <= value <= maximum or (integer and int(value) != value):
        raise ValueError(f"{name} must be {'an integer ' if integer else ''}between {minimum} and {maximum}")
    return int(value) if integer else value


@dataclass
class Config:
    root: Path
    env: dict
    combinations: list
    size: int
    query_count: int
    port: int
    backend: str
    interval_ms: int
    timeout: float
    cooldown: float
    snapshot_sha256: str | None = None
    orm_cooldown: float = 10
    idle_seconds: float = 30
    trial_count: int | None = None
    seed: int = 42

    @classmethod
    def load(cls, root, overrides=None):
        root = Path(root).resolve()
        data = cls.bridge(root, "config", dict(os.environ))
        env = {**os.environ, **data["environment"], **(overrides or {})}
        size = number(env.get("SIZE"), "SIZE", 1000, 1, 100000, True)
        count = number(env.get("QUERY_COUNT"), "QUERY_COUNT", size, 1, size, True)
        port = number(env.get("PORT"), "PORT", 3100, 1, 65535, True)
        backend = env.get("MEASUREMENT_BACKEND") or "none"
        if backend == "powermetrics":
            raise ValueError("Replace MEASUREMENT_BACKEND=powermetrics with powermetrics_zeus; both Mac collectors are required")
        if backend not in ("none", "powermetrics_zeus", "rapl"):
            raise ValueError("MEASUREMENT_BACKEND must be none, powermetrics_zeus or rapl")
        interval = number(env.get("POWER_SAMPLE_INTERVAL_MS"), "POWER_SAMPLE_INTERVAL_MS", 100, 10, 5000, True)
        timeout = number(env.get("WORKLOAD_TIMEOUT_SECONDS"), "WORKLOAD_TIMEOUT_SECONDS", 3600, 1, 86400)
        cooldown = number(env.get("TRIAL_COOLDOWN_SECONDS", env.get("COOLDOWN_SECONDS")), "TRIAL_COOLDOWN_SECONDS", 30, 0, 86400)
        orm_cooldown = number(env.get("ORM_COOLDOWN_SECONDS"), "ORM_COOLDOWN_SECONDS", 10, 0, 86400)
        idle = number(env.get("IDLE_SECONDS"), "IDLE_SECONDS", 30, 0, 86400)
        trials = number(env.get("TRIALS"), "TRIALS", 10, 1, 1000, True) if env.get("TRIALS") else None
        seed = number(env.get("SEED"), "SEED", 42, 1, 0xffffffff, True)
        # Explicit values keep every TypeScript process on the same resolved configuration.
        env.update(SIZE=str(size), QUERY_COUNT=str(count), PORT=str(port), MEASUREMENT_BACKEND=backend,
                   POWER_SAMPLE_INTERVAL_MS=str(interval), WORKLOAD_TIMEOUT_SECONDS=str(timeout),
                   TRIAL_COOLDOWN_SECONDS=str(cooldown), ORM_COOLDOWN_SECONDS=str(orm_cooldown), IDLE_SECONDS=str(idle),
                   SNAPSHOT_DIR=env.get("SNAPSHOT_DIR") or str(root / "db/snapshot"),
                   PG_TOOLS=env.get("PG_TOOLS") or "")
        return cls(root, env, data["combinations"], size, count, port, backend, interval, timeout, cooldown,
                   orm_cooldown=orm_cooldown, idle_seconds=idle, trial_count=trials, seed=seed)

    @staticmethod
    def bridge(root, action, env):
        executable = root / "node_modules/.bin/tsx"
        if not executable.exists():
            raise ValueError("Dependencies are missing; run npm ci first")
        completed = subprocess.run([str(executable), "src/control.ts", action], cwd=root, env=env,
                                   capture_output=True, text=True, timeout=30)
        if completed.returncode:
            raise ValueError(f"Configuration/metadata query failed: {completed.stderr.strip()}")
        return json.loads(completed.stdout)

    @property
    def base_url(self):
        return self.env.get("BENCHMARK_BASE_URL") or f"http://127.0.0.1:{self.port}"

    def validate_backend(self, experiment=False):
        system = platform.system()
        if (self.backend == "rapl" and system != "Linux") or (self.backend == "powermetrics_zeus" and
                (system != "Darwin" or platform.machine() != "arm64")):
            raise ValueError(f"Backend {self.backend} is not supported on {system}")
        if experiment and (self.backend == "none" or self.interval_ms != 100):
            raise ValueError("The full experiment requires powermetrics_zeus or rapl at 10 Hz (POWER_SAMPLE_INTERVAL_MS=100)")

    def snapshot(self):
        if not self.env.get("DATABASE_URL"):
            raise ValueError("DATABASE_URL is required; copy .env.example to .env")
        directory = Path(self.env.get("SNAPSHOT_DIR") or self.root / "db/snapshot")
        if not directory.is_absolute():
            directory = self.root / directory
        try:
            metadata = json.loads((directory / "baseline.json").read_text())
            sql = directory / "baseline.sql"
            digest = hashlib.sha256()
            with sql.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
        except (OSError, ValueError) as error:
            raise ValueError("No valid snapshot found; run npm run db:init first") from error
        if metadata.get("layoutVersion") != 2 or not metadata.get("profiles"):
            raise ValueError("Snapshot layout is outdated; run npm run db:init")
        if metadata.get("size") != self.size:
            raise ValueError(f"Snapshot SIZE={metadata.get('size')} differs from SIZE={self.size}")
        if digest.hexdigest() != metadata.get("sha256"):
            raise ValueError("Snapshot checksum mismatch")
        if self.snapshot_sha256 and metadata["sha256"] != self.snapshot_sha256:
            raise ValueError("Snapshot changed during the series; use the original baseline")
        return metadata
