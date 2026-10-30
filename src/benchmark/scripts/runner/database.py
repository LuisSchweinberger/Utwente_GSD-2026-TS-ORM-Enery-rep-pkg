"""Own the dedicated Compose PostgreSQL service for one complete trial."""
import json
from urllib.parse import urlparse, unquote


class Database:
    def __init__(self, config, processes, logs):
        self.config, self.processes, self.logs = config, processes, logs
        self.started = False

    def validate(self):
        text = self.processes.command(["docker", "compose", "config", "--format", "json"], self.logs / "postgres-config.log", capture=True)
        service = json.loads(text)["services"]["postgres"]
        environment = service["environment"]
        ports = {int(port["published"]) for port in service.get("ports", []) if int(port["target"]) == 5432}
        url = urlparse(self.config.env.get("DATABASE_URL", ""))
        if (url.hostname not in ("localhost", "127.0.0.1") or (url.port or 5432) not in ports or
            unquote(url.username or "") != environment["POSTGRES_USER"] or unquote(url.password or "") != environment["POSTGRES_PASSWORD"] or
            unquote(url.path.lstrip("/")) != environment["POSTGRES_DB"]):
            raise ValueError("DATABASE_URL must address the dedicated Docker Compose PostgreSQL service")

    def __enter__(self):
        self.validate()
        running = self.processes.command(["docker", "compose", "ps", "--status", "running", "--services"],
                                         self.logs / "postgres-state.log", capture=True)
        if "postgres" in running.splitlines():
            self.stop()
        return self

    def start(self):
        self.started = True  # A partially failed startup must also be cleaned up.
        self.processes.command(["docker", "compose", "up", "-d", "--wait", "--wait-timeout", "60", "postgres"],
                               self.logs / "postgres-start.log", timeout=90)

    def stop(self):
        self.processes.command(["docker", "compose", "stop", "-t", "5", "postgres"],
                               self.logs / "postgres-stop.log", timeout=30)
        self.started = False

    def __exit__(self, exc_type, error, traceback):
        if self.started:
            self.stop()
