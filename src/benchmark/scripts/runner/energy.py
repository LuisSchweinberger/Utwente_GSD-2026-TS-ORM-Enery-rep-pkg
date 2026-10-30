"""Monotonic measurement windows; Zeus is required only for the Mac backend."""
import datetime as dt
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import plistlib
import signal
import subprocess
import threading
import time
from .artifacts import write_json


def rapl_delta(previous, current, maximum):
    if not (0 <= previous <= maximum and 0 <= current <= maximum and maximum > 0):
        raise ValueError("Invalid RAPL counter/range")
    return current - previous if current >= previous else maximum - previous + current


def power_sample(sample, end=None):
    """Known powermetrics fields: *_energy in mJ, *_power in mW, package_joules."""
    stamp, elapsed = sample.get("timestamp"), sample.get("elapsed_ns")
    if not isinstance(stamp, dt.datetime) or not isinstance(elapsed, (int, float)) or not math.isfinite(elapsed) or elapsed <= 0:
        raise ValueError("Unsupported powermetrics timestamp/elapsed_ns schema")
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=dt.timezone.utc)
    processor, energies = sample.get("processor", {}), {}
    for domain in ("cpu", "gpu", "ane"):
        key = f"{domain}_energy"
        value = processor.get(key, sample.get(key))
        if value is None and processor.get(f"{domain}_power") is not None:
            value = processor[f"{domain}_power"] * elapsed / 1e9
        if value is not None:
            if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError(f"Invalid powermetrics {key}")
            energies[domain] = value / 1000
    package = processor.get("package_joules")
    if package is not None:
        if not isinstance(package, (int, float)) or not math.isfinite(package) or package < 0:
            raise ValueError("Invalid powermetrics package_joules")
        energies["package"] = package
    if not energies:
        raise ValueError("No supported powermetrics energy fields; inspect raw plist for this hardware/macOS")
    end = stamp.timestamp() if end is None else end
    return {"start": end - elapsed / 1e9, "end": end, "energyJ": energies}


def integrate_power(samples, start, end):
    totals, coverage, counts = {}, {}, {}
    for sample in sorted(samples, key=lambda item: item["start"]):
        overlap = max(0, min(end, sample["end"]) - max(start, sample["start"]))
        if not overlap:
            continue
        for name, energy in sample["energyJ"].items():
            totals[name] = totals.get(name, 0) + energy * overlap / (sample["end"] - sample["start"])
            coverage.setdefault(name, []).append((max(start, sample["start"]), min(end, sample["end"])))
            counts[name] = counts.get(name, 0) + 1
    domains = []
    for name, energy in totals.items():
        covered, last = 0, start
        for a, b in coverage[name]:
            if a < last - .000001:
                raise ValueError(f"Overlapping powermetrics samples for {name}")
            covered += max(0, b - max(a, last))
            last = max(last, b)
        fraction = min(1, covered / (end - start))
        domains.append({"name": name, "energyJ": energy, "coverageFraction": fraction,
                        "sampleCount": counts[name], "quality": "adequate" if fraction >= .99 and counts[name] >= 3 else "limited"})
    if not domains:
        raise ValueError("No power samples overlap the workload")
    if any(item["coverageFraction"] < .99 for item in domains):
        raise ValueError("Incomplete powermetrics workload coverage (below 99%)")
    return domains


class Rapl:
    def __init__(self, raw, interval, root=None):
        if platform.system() != "Linux":
            raise ValueError("RAPL requires Linux powercap")
        self.domains, seen = [], set()
        root = Path("/sys/class/powercap") if root is None else Path(root)
        for entry in sorted(root.glob("intel-rapl*")):
            for counter in [entry / "energy_uj", *entry.rglob("energy_uj")]:
                actual = counter.resolve()
                if not counter.exists() or actual in seen:
                    continue
                seen.add(actual)
                directory = counter.parent
                self.domains.append({"id": directory.name, "name": (directory / "name").read_text().strip(),
                                     "path": str(counter), "maxEnergyRangeUj": int((directory / "max_energy_range_uj").read_text())})
        if not self.domains:
            raise ValueError("No readable Intel RAPL domains found under /sys/class/powercap")
        self.raw = open(raw, "x")
        self.raw.write(json.dumps({"type": "domains", "domains": self.domains}) + "\n")
        self.interval, self.stop_event = interval, threading.Event()
        self.error, self.thread, self.readings = None, None, []
        try:
            self.read()
        except BaseException:
            self.raw.close()
            raise

    def read(self):
        values = [int(Path(domain["path"]).read_text()) for domain in self.domains]
        row = {"monotonicNs": time.monotonic_ns(), "energyUj": values}
        self.readings.append(row)
        self.raw.write(json.dumps(row) + "\n")
        self.raw.flush()

    def start(self):
        self.readings.clear()
        self.read()
        def collect():
            try:
                while not self.stop_event.wait(self.interval):
                    self.read()
            except Exception as error:
                self.error = str(error)
        self.thread = threading.Thread(target=collect, daemon=True)
        self.thread.start()

    def finish(self, start, end):
        self.close_thread()
        self.read()
        if self.error:
            raise ValueError(self.error)
        max_gap = max((b["monotonicNs"] - a["monotonicNs"]) / 1e9 for a, b in zip(self.readings, self.readings[1:]))
        if max_gap > max(self.interval * 3, .1):
            raise ValueError("RAPL sampling stalled; counter wraparound cannot be reliably assessed")
        result = []
        for i, domain in enumerate(self.domains):
            energy = sum(rapl_delta(a["energyUj"][i], b["energyUj"][i], domain["maxEnergyRangeUj"])
                         for a, b in zip(self.readings, self.readings[1:])) / 1e6
            result.append({**domain, "energyJ": energy, "sampleCount": len(self.readings),
                           "counterWindowElapsedMs": (self.readings[-1]["monotonicNs"] - self.readings[0]["monotonicNs"]) / 1e6,
                           "startOffsetMs": (self.readings[0]["monotonicNs"] / 1e9 - start) * 1000,
                           "endOffsetMs": (self.readings[-1]["monotonicNs"] / 1e9 - end) * 1000,
                           "maxReadGapMs": max_gap * 1000, "quality": "counter_delta"})
        return result

    def close_thread(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=5)

    def close(self):
        self.close_thread()
        self.raw.close()


class Powermetrics:
    def __init__(self, raw, interval):
        if platform.system() != "Darwin":
            raise ValueError("powermetrics requires macOS")
        help_text = subprocess.run(["powermetrics", "--help"], capture_output=True, text=True).stdout
        samplers = [name for name in ("cpu_power", "gpu_power", "ane_power") if name in help_text]
        if not samplers:
            raise ValueError("No supported powermetrics power samplers")
        self.command = ["powermetrics", "-f", "plist", "-i", str(round(interval * 1000)), "-s", ",".join(samplers), "-b", "0"]
        if os.geteuid() != 0:
            self.command = ["sudo", "-n", *self.command]
        self.raw, self.normalized = open(raw, "xb"), open(str(raw) + ".samples.jsonl", "x")
        self.stderr = open(str(raw) + ".stderr", "xb")
        self.samples, self.error, self.ready = [], None, threading.Event()
        try:
            self.process = subprocess.Popen(self.command, stdout=subprocess.PIPE, stderr=self.stderr)
        except BaseException:
            self.raw.close()
            self.normalized.close()
            self.stderr.close()
            raise
        self.thread = threading.Thread(target=self.collect, daemon=True)
        self.thread.start()
        try:
            if not self.ready.wait(max(10, interval * 5)) or self.error:
                raise ValueError(self.error or f"powermetrics produced no sample; check {raw}.stderr and sudo credentials")
        except BaseException:
            self.close()
            raise

    def collect(self):
        buffer = b""
        try:
            while True:
                chunk = os.read(self.process.stdout.fileno(), 65536)
                if not chunk:
                    break
                self.raw.write(chunk)
                self.raw.flush()
                buffer += chunk
                while b"</plist>" in buffer:
                    block, buffer = buffer.split(b"</plist>", 1)
                    data = plistlib.loads(block.lstrip(b"\x00\r\n ") + b"</plist>")
                    received = time.monotonic()
                    # Some plist dates have only second resolution. Advance the first
                    # receipt-anchored sample by the collector's actual interval lengths.
                    end = self.samples[-1]["end"] + data["elapsed_ns"] / 1e9 if self.samples else received
                    sample = power_sample(data, end=end)
                    sample.update(receivedMonotonicSeconds=received, receiptLagMs=(received - end) * 1000)
                    self.samples.append(sample)
                    self.normalized.write(json.dumps(sample) + "\n")
                    self.normalized.flush()
                    self.ready.set()
            if not self.samples:
                self.stderr.flush()
                details = Path(self.stderr.name).read_text(errors="replace").strip()
                raise ValueError(f"powermetrics exited without samples; stderr: {self.stderr.name}; {details[-2000:] or 'stderr was empty'}")
        except Exception as error:
            self.error = str(error)
            self.ready.set()

    def start(self):
        if self.error or self.process.poll() is not None:
            raise ValueError(self.error or "powermetrics exited before workload")

    def finish(self, start, end):
        deadline = time.monotonic() + 10
        while not self.error and (not self.samples or self.samples[-1]["end"] < end):
            if self.process.poll() is not None or time.monotonic() > deadline:
                raise ValueError("powermetrics did not capture the end of the workload")
            time.sleep(.01)
        self.close()
        if self.error:
            raise ValueError(self.error)
        return integrate_power(self.samples, start, end)

    def close(self):
        if self.process.poll() is None:
            self.send_signal("TERM")
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.send_signal("KILL")
                self.process.wait(timeout=5)
        self.thread.join(timeout=5)
        self.process.stdout.close()
        if not self.raw.closed:
            self.raw.close()
            self.normalized.close()
            self.stderr.close()

    def send_signal(self, name):
        try:
            self.process.send_signal(getattr(signal, f"SIG{name}"))
        except PermissionError:
            subprocess.run(["sudo", "-n", "/bin/kill", f"-{name}", str(self.process.pid)], check=True, timeout=5)


def collector_metadata(backend):
    if backend != "powermetrics_zeus":
        return []
    try:
        version = importlib.metadata.version("zeus-apple-silicon")
    except importlib.metadata.PackageNotFoundError as error:
        raise ValueError("powermetrics_zeus requires zeus-apple-silicon; install requirements-mac.txt with the runner's Python") from error
    return [{"name": "powermetrics", "version": platform.release(),
             "versionSource": "macOS kernel release (bundled tool)", "domains": ["cpu", "gpu", "ane"],
             "method": "interval integration"},
            {"name": "zeus-apple-silicon", "version": version, "source": "ioreport",
             "domains": ["dram"], "field": "dram_mj", "method": "boundary counter delta"}]


class AppleMemory:
    """Two auditable IOReport snapshots; never substitutes another energy domain."""
    def __init__(self, raw):
        self.path = Path(str(raw) + ".memory.json")
        self.file = self.path.open("x")
        self.monitor = None
        self.data = {"source": "ioreport", "field": "dram_mj", "unit": "mJ",
                     "scope": "host-wide unified-memory energy-model estimate", "snapshots": []}
        try:
            self.data["collector"] = collector_metadata("powermetrics_zeus")[1]
            try:
                from zeus_apple_silicon import AppleEnergyMonitor
            except ImportError as error:
                raise ValueError("Cannot import zeus-apple-silicon; use the Python environment with requirements-mac.txt installed") from error
            self.monitor = AppleEnergyMonitor()
            self.snapshot("capability")
        except BaseException as error:
            self.data["error"] = str(error)
            self.close()
            raise

    def snapshot(self, kind):
        before = time.monotonic_ns()
        value = self.monitor.get_cumulative_energy().dram_mj
        after = time.monotonic_ns()
        row = {"kind": kind, "beforeMonotonicNs": before, "afterMonotonicNs": after,
               "energyMj": None}
        self.data["snapshots"].append(row)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            row["invalidValue"] = repr(value)
            raise ValueError("Invalid or unavailable IOReport dram_mj counter")
        row["energyMj"] = value
        return row

    def start(self):
        self.initial = self.snapshot("start")

    def finish(self, start, end):
        final = self.snapshot("end")
        initial = self.initial
        delta = final["energyMj"] - initial["energyMj"]
        if delta < 0:
            raise ValueError("IOReport DRAM counter decreased/reset during measurement")
        lower = (final["beforeMonotonicNs"] - initial["afterMonotonicNs"]) / 1e6
        upper = (final["afterMonotonicNs"] - initial["beforeMonotonicNs"]) / 1e6
        if lower <= 0:
            raise ValueError("IOReport snapshot brackets do not define a positive counter window")
        first = (initial["beforeMonotonicNs"] + initial["afterMonotonicNs"]) / 2
        last = (final["beforeMonotonicNs"] + final["afterMonotonicNs"]) / 2
        return {"id": "ioreport:dram", "name": "dram", "source": "ioreport",
                "energyJ": delta / 1000, "sampleCount": 2, "quality": "model_counter_delta",
                "counterWindowElapsedMs": (last - first) / 1e6,
                "counterWindowBoundsMs": {"lower": lower, "upper": upper},
                "startOffsetMs": (first / 1e9 - start) * 1000,
                "endOffsetMs": (last / 1e9 - end) * 1000,
                "snapshotBrackets": {"start": initial, "end": final},
                "boundaryMethod": "snapshot-call midpoints estimated; exact hardware snapshot instants unavailable",
                "rawField": "dram_mj", "collectorVersion": self.data["collector"]["version"]}

    def close(self):
        try:
            if not self.file.closed:
                try:
                    json.dump(self.data, self.file, indent=2, allow_nan=False)
                    self.file.write("\n")
                finally:
                    self.file.close()
        finally:
            self.monitor = None


class PowermetricsZeus:
    """One backend: both powermetrics and IOReport memory must succeed."""
    def __init__(self, raw, interval):
        if platform.system() != "Darwin" or platform.machine() != "arm64":
            raise ValueError("powermetrics_zeus requires macOS on Apple Silicon (arm64)")
        self.metadata = collector_metadata("powermetrics_zeus")
        self.memory = AppleMemory(raw)
        try:
            self.power = Powermetrics(raw, interval)
        except BaseException:
            self.memory.close()
            raise

    def start(self):
        self.power.start()
        self.memory.start()

    def finish(self, start, end):
        # Capture DRAM before waiting for powermetrics coverage or process shutdown.
        memory = self.memory.finish(start, end)
        domains = self.power.finish(start, end)
        for domain in domains:
            domain.update(id="powermetrics:" + domain["name"], source="powermetrics")
        if not any(domain["name"] == "cpu" for domain in domains):
            raise ValueError("powermetrics_zeus requires a CPU energy domain")
        return [*domains, memory]

    def close(self):
        try:
            self.power.close()
        finally:
            self.memory.close()


class Measurement:
    """Collector lifetime and timing are controlled directly by the Python runner."""
    def __init__(self, backend, interval_ms, output, raw, kind="workload"):
        self.backend, self.interval = backend, interval_ms
        self.output, self.raw, self.kind = Path(output), Path(raw), kind
        self.collector, self.started = None, None
        self.outcome = {"kind": kind, "backend": backend, "sampleIntervalMs": interval_ms,
                        "host": {"system": platform.system(), "release": platform.release(), "architecture": platform.machine()},
                        "scope": "host hardware domains; client, API, database and background activity",
                        "status": "failed", "domains": []}

    def __enter__(self):
        try:
            if self.backend == "rapl":
                self.collector = Rapl(self.raw, self.interval / 1000)
            elif self.backend == "powermetrics_zeus":
                self.collector = PowermetricsZeus(self.raw, self.interval / 1000)
                self.outcome["collectors"] = self.collector.metadata
            elif self.backend == "powermetrics":
                raise ValueError("Use MEASUREMENT_BACKEND=powermetrics_zeus; CPU-only powermetrics is no longer supported")
            elif self.backend != "none":
                raise ValueError(f"Unknown energy backend: {self.backend}")
        except BaseException as error:
            self.outcome["error"] = str(error)
            write_json(self.output, self.outcome)
            raise
        return self

    def start(self):
        if self.collector:
            self.collector.start()
        self.started = (time.monotonic_ns(), time.time())

    def stop(self):
        end_ns, end_wall = time.monotonic_ns(), time.time()
        start_ns, start_wall = self.started
        duration = (end_ns - start_ns) / 1e9
        self.outcome["timing"] = {
            "boundary": "controller-observed idle window" if self.kind == "idle-baseline" else "controller-observed GO to DONE (includes pipe/progress overhead)",
            "clock": "monotonic_ns", "workloadElapsedMs": duration * 1000,
            "workloadStartedMonotonicNs": start_ns, "workloadFinishedMonotonicNs": end_ns,
            "workloadStartedAt": dt.datetime.fromtimestamp(start_wall, dt.timezone.utc).isoformat(),
            "workloadFinishedAt": dt.datetime.fromtimestamp(end_wall, dt.timezone.utc).isoformat(),
        }
        self.outcome["domains"] = self.collector.finish(start_ns / 1e9, end_ns / 1e9) if self.collector else []
        for domain in self.outcome["domains"]:
            domain["averagePowerW"] = domain["energyJ"] / (domain.get("counterWindowElapsedMs", duration * 1000) / 1000)
        if self.backend == "powermetrics_zeus":
            power = self.collector.power
            self.outcome["maxAbsReceiptLagMs"] = max(abs(sample["receiptLagMs"]) for sample in power.samples)
            self.outcome["collectorCommand"] = power.command
        self.outcome["boundaryMethod"] = (
            "powermetrics: receipt anchored then elapsed_ns, uniform interval allocation; DRAM: bracketed counter reads, midpoint-estimated boundaries"
            if self.backend == "powermetrics_zeus" else "counter reads bracket the controller window; read overhead included"
            if self.collector else "timing only")
        self.outcome["status"] = "valid"

    def __exit__(self, exc_type, error, traceback):
        if error is not None:
            self.outcome.update(status="failed", error=str(error) or exc_type.__name__)
        cleanup_error = None
        if self.collector:
            try:
                self.collector.close()
            except Exception as failure:
                cleanup_error = failure
                self.outcome.update(status="failed", error=f"Collector cleanup failed: {failure}")
        write_json(self.output, self.outcome)
        if cleanup_error and error is None:
            raise cleanup_error
