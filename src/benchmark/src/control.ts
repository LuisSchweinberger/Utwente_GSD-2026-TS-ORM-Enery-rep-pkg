/** Bridge for the Python controller: reuse dotenv, scenario definitions and pg. */
import "dotenv/config";
import { readFile } from "node:fs/promises";
import os from "node:os";
import pg from "pg";
import { databaseUrl } from "./config.js";
import { scenarioNames, scenarioProfiles } from "./scenarios.js";

const action = process.argv[2];
if (action === "config") {
  const keys = ["DATABASE_URL", "POSTGRES_PORT", "PORT", "SIZE", "QUERY_COUNT", "SNAPSHOT_DIR", "PG_TOOLS",
    "BENCHMARK_BASE_URL", "MEASUREMENT_BACKEND", "POWER_SAMPLE_INTERVAL_MS", "WORKLOAD_TIMEOUT_SECONDS",
    "COOLDOWN_SECONDS", "TRIAL_COOLDOWN_SECONDS", "ORM_COOLDOWN_SECONDS", "IDLE_SECONDS", "TRIALS",
    "SEED", "DATASET_SEED", "EXPERIMENT_MACHINE_ID", "NODE_OPTIONS"];
  console.log(JSON.stringify({
    environment: Object.fromEntries(keys.filter((key) => process.env[key] !== undefined).map((key) => [key, process.env[key]])),
    combinations: scenarioNames.flatMap((scenario) => scenarioProfiles[scenario].map((profile) => ({ scenario, profile }))),
  }));
} else if (action === "metadata" || action === "runtime") {
  let postgres: Record<string, unknown> | null = null;
  if (action === "metadata") {
    const client = new pg.Client({ connectionString: databaseUrl() });
    await client.connect();
    try {
      postgres = (await client.query("SELECT version() AS version, current_setting('server_version_num') AS version_number, current_setting('max_connections') AS max_connections")).rows[0];
    } finally { await client.end(); }
  }
  const lock = JSON.parse(await readFile(new URL("../package-lock.json", import.meta.url), "utf8")) as { packages: Record<string, { version?: string }> };
  const dependencies = Object.fromEntries(["@prisma/client", "sequelize", "drizzle-orm", "pg", "express", "tsx"].map((name) => [name, lock.packages[`node_modules/${name}`]?.version ?? null]));
  const cpus = os.cpus();
  console.log(JSON.stringify({
    host: { cpuModel: cpus[0]?.model ?? null, logicalCpuCount: cpus.length,
      cpuSpeedMHzAtSetup: cpus.map((cpu) => cpu.speed), totalMemoryBytes: os.totalmem() },
    software: { node: process.version, nodeOptions: process.env.NODE_OPTIONS ?? "", postgres, dependencies },
  }));
} else {
  throw new Error("Usage: tsx src/control.ts config|metadata|runtime");
}
