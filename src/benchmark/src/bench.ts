import "dotenv/config";
import { mkdir, writeFile } from "node:fs/promises";
import { readSync } from "node:fs";
import { benchmarkSize, queryCount } from "./config.js";
import { loadSnapshot } from "./snapshot.js";
import { scenarioNames, scenarioProfiles, scenarioRequest, type ScenarioName } from "./scenarios.js";
import { profileNames, type ProfileName } from "./profiles.js";

function argumentsMap(argv: string[]): Map<string, string> {
  const parsed = new Map<string, string>();
  for (let i = 0; i < argv.length; i += 1) {
    const key = argv[i];
    if (!key.startsWith("--") || i + 1 >= argv.length || argv[i + 1].startsWith("--")) {
      throw new Error("Workload arguments: --scenario <name> --profile <profile> --run-id <id>; launch through npm run task");
    }
    if (parsed.has(key)) throw new Error(`Duplicate argument: ${key}`);
    parsed.set(key, argv[++i]);
  }
  return parsed;
}

const args = argumentsMap(process.argv.slice(2));
for (const key of args.keys()) if (!["--scenario", "--profile", "--run-id"].includes(key)) throw new Error(`Unknown argument: ${key}`);
const scenario = args.get("--scenario") as ScenarioName | undefined;
const profile = args.get("--profile") as ProfileName | undefined;
const runId = args.get("--run-id");
if (!scenario || !scenarioNames.includes(scenario)) throw new Error(`--scenario must be one of: ${scenarioNames.join(", ")}`);
if (!profile || !profileNames.includes(profile)) throw new Error(`--profile must be one of: ${profileNames.join(", ")}`);
if (!runId || !/^[A-Za-z0-9][A-Za-z0-9._-]{0,119}$/.test(runId)) throw new Error("--run-id must be 1-120 safe filename characters");
if (!scenarioProfiles[scenario].includes(profile)) {
  throw new Error(`Scenario ${scenario} is not defined for profile ${profile}`);
}

const size = benchmarkSize();
const count = queryCount(size);
const snapshot = await loadSnapshot(size);
const base = process.env.BENCHMARK_BASE_URL ?? "http://127.0.0.1:3100";
const healthResponse = await fetch(`${base}/health`);
if (!healthResponse.ok) throw new Error(`Server health check failed: HTTP ${healthResponse.status}`);
const health = await healthResponse.json() as { status?: string; orm?: string };
const orm = health.orm;
if (health.status !== "ok" || !orm || !["prisma", "sequelize", "drizzle"].includes(orm)) {
  throw new Error("Server /health response must identify the active ORM; restart it with npm run start:<orm>.");
}

if (process.env.BENCH_CONTROL !== "stdio") throw new Error("Run this workload through npm run task; controller pipes are required.");
const prepared = Array.from({ length: count }, (_, i) => {
  const request = scenarioRequest(scenario, profile, i, size);
  return {
    url: `${base}${request.path}`,
    targetId: Number(request.path.match(/\/(\d+)(?:\/|$)/)?.[1] ?? i + 1),
    options: {
      method: request.method,
      headers: request.body ? { "content-type": "application/json" } : undefined,
      body: request.body ? JSON.stringify(request.body) : undefined,
    },
  };
});
const signals = process.stdout;
await new Promise<void>((resolve, reject) => signals.write("READY\n", (error) => error ? reject(error) : resolve()));
// Read only GO synchronously so no pending stdin read keeps Node alive after DONE.
const commandFd = 0;
const byte = Buffer.alloc(1);
let command = "";
while (readSync(commandFd, byte, 0, 1, null) === 1 && byte[0] !== 10) {
  command += byte.toString();
  if (command.length > 16) throw new Error("Invalid trial controller command");
}
if (command !== "GO") throw new Error("Expected GO from trial controller");
const requests: Array<{ queryId: number; targetId: number; status: number }> = [];
// Limit progress messages to about ten per batch to keep measurement overhead small.
const progressEvery = Math.max(1, Math.ceil(count / 10));
let failure: string | undefined;
for (let i = 0; i < count; i += 1) {
  const request = prepared[i];
  try {
    const response = await fetch(request.url, request.options);
    await response.arrayBuffer();
    requests.push({ queryId: i + 1, targetId: request.targetId, status: response.status });
    const expectedStatus = scenario.startsWith("create-") ? 201 : 200;
    if (response.status !== expectedStatus) {
      failure = `${scenario} query ${i + 1} returned HTTP ${response.status}; expected ${expectedStatus}`;
      break;
    }
    if ((i + 1) % progressEvery === 0 || i + 1 === count) {
      signals.write(`PROGRESS ${i + 1} ${count}\n`);
    }
  } catch (error) {
    failure = `${scenario} query ${i + 1} failed: ${error instanceof Error ? error.message : String(error)}`;
    break;
  }
}
await new Promise<void>((resolve, reject) => signals.write(`${failure ? "FAILED" : "DONE"}\n`, (error) => error ? reject(error) : resolve()));

const outputDirectory = process.env.BENCH_RESULT_DIR ?? `results/${orm}`;
await mkdir(outputDirectory, { recursive: true });
const outputPath = `${outputDirectory}/${runId}.execution.json`;
const result = {
  formatVersion: 3,
  orm,
  scenario,
  profile,
  runId,
  base,
  size,
  queryCount: count,
  snapshot: { layoutVersion: snapshot.layoutVersion, sha256: snapshot.sha256, createdAt: snapshot.createdAt, dataset: snapshot.dataset },
  requestCountCompleted: requests.length,
  status: failure ? "request_failed" : "pending_verification",
  failure,
  requests,
};
await writeFile(outputPath, `${JSON.stringify(result, null, 2)}\n`, { flag: "wx" });
console.log(`Saved ${requests.length}/${count} request outcomes to ${outputPath}`);
if (failure) throw new Error(failure);
