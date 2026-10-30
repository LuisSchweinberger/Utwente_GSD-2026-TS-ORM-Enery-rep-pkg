"""Owned process groups and a bounded line protocol over ordinary stdin/stdout."""
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time


class Processes:
    def __init__(self, config):
        self.config, self.children, self.files = config, [], []
        self.logs = {}

    def __enter__(self):
        return self

    def start(self, source, arguments, log_path, protocol=False, environment=None):
        return self.start_command([str(self.config.root / "node_modules/.bin/tsx"), source, *arguments],
                                  log_path, protocol, environment)

    def start_command(self, command, log_path, protocol=False, environment=None):
        log_path = Path(log_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log = log_path.open("ab")
        self.files.append(log)
        child = subprocess.Popen(command,
                                 cwd=self.config.root, env={**self.config.env, **(environment or {})},
                                 stdin=subprocess.PIPE if protocol else subprocess.DEVNULL,
                                 stdout=subprocess.PIPE if protocol else log, stderr=log,
                                 start_new_session=True)
        self.children.append(child)
        self.logs[child] = log
        return child

    def run(self, source, arguments, log_path, timeout=120):
        child = self.start(source, arguments, log_path)
        code = self.finish(child, timeout)
        if code:
            raise RuntimeError(f"{source} failed (exit {code}); see {log_path}")

    def command(self, command, log_path, timeout=120, capture=False):
        child = self.start_command(command, log_path, protocol=capture)
        output = b""
        if capture:
            output, _ = child.communicate(timeout=timeout)
        code = self.finish(child, timeout)
        if code:
            raise RuntimeError(f"{' '.join(command[:3])} failed (exit {code}); see {log_path}")
        return output.decode() if capture else ""

    def finish(self, child, timeout=15):
        code = child.wait(timeout=timeout)
        self.release(child)
        return code

    def release(self, child):
        for stream in (child.stdin, child.stdout):
            if stream:
                stream.close()
        log = self.logs.pop(child, None)
        if log:
            log.close()
            self.files.remove(log)
        if child in self.children:
            self.children.remove(child)

    @staticmethod
    def stop(child):
        if child.poll() is None:
            try:
                os.killpg(child.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait(timeout=5)
        for stream in (child.stdin, child.stdout):
            if stream:
                stream.close()

    def __exit__(self, exc_type, error, traceback):
        for child in reversed(self.children):
            self.stop(child)
        for stream in self.files:
            stream.close()


class Protocol:
    def __init__(self, child):
        self.child, self.buffer, self.records = child, b"", []
        self.selector = selectors.DefaultSelector()
        self.selector.register(child.stdout, selectors.EVENT_READ)

    def send(self, command):
        self.child.stdin.write((command + "\n").encode())
        self.child.stdin.flush()

    def receive(self, timeout, progress=None):
        deadline = time.monotonic() + timeout
        while True:
            if b"\n" in self.buffer:
                line, self.buffer = self.buffer.split(b"\n", 1)
                message = line.decode().strip()
                self.records.append(message)
                if message.startswith("PROGRESS "):
                    if progress:
                        _, completed, total = message.split()
                        progress(int(completed), int(total))
                    continue
                return message
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not self.selector.select(remaining):
                raise TimeoutError("Timed out waiting for workload runner")
            chunk = os.read(self.child.stdout.fileno(), 65536)
            if not chunk:
                raise RuntimeError("Workload runner exited before signaling completion; inspect bench log")
            self.buffer += chunk

    def close(self, log_path):
        self.selector.close()
        with Path(log_path).open("ab") as output:
            output.write(("\n".join(self.records) + "\n").encode())
            output.write(self.buffer)
