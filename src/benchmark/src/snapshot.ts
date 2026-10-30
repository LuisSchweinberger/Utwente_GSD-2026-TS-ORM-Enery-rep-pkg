import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { createReadStream, createWriteStream } from "node:fs";
import { mkdir, readFile, rename, rm, writeFile } from "node:fs/promises";
import { pipeline } from "node:stream/promises";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { databaseUrl } from "./config.js";
import type { SnapshotLayout } from "./profiles.js";
import { generatorVersion, type Dataset } from "./dataset.js";

function files() {
  const directory = process.env.SNAPSHOT_DIR
    ? pathToFileURL(`${resolve(process.env.SNAPSHOT_DIR)}/`)
    : new URL("../db/snapshot/", import.meta.url);
  return { directory, sqlFile: new URL("baseline.sql", directory), metadataFile: new URL("baseline.json", directory) };
}
const tables = ["vets", "specialties", "vet_specialties", "types", "owners", "pets", "visits"];

export type Snapshot = { layoutVersion: 2; size: number; sha256: string; createdAt: string; profiles: SnapshotLayout; dataset?: Dataset };

function tool(name: "pg_dump" | "psql", args: string[]) {
  const url = new URL(databaseUrl());
  const local = process.env.PG_TOOLS === "local";
  const connection = ["-h", local ? url.hostname : "127.0.0.1", "-p", local ? url.port || "5432" : "5432",
    "-U", decodeURIComponent(url.username), "-d", decodeURIComponent(url.pathname.slice(1))];
  const password = decodeURIComponent(url.password);
  const child = local
    ? spawn(name, [...connection, ...args], { env: { ...process.env, PGPASSWORD: password } })
    : spawn("docker", ["compose", "exec", "-T", "-e", `PGPASSWORD=${password}`, "postgres", name, ...connection, ...args]);
  let stderr = "";
  child.stderr.on("data", (data: Buffer) => { stderr += data.toString(); });
  const completed = new Promise<void>((resolve, reject) => {
    child.once("error", reject);
    child.once("close", (code) => code === 0 ? resolve() : reject(new Error(`${name} failed: ${stderr}`)));
  });
  return { child, completed };
}

async function hash(file: URL): Promise<string> {
  const digest = createHash("sha256");
  for await (const chunk of createReadStream(file)) digest.update(chunk);
  return digest.digest("hex");
}

export async function saveSnapshot(size: number, profiles: SnapshotLayout, dataset?: Dataset): Promise<Snapshot> {
  const { directory, sqlFile, metadataFile } = files();
  await mkdir(directory, { recursive: true });
  const temporary = new URL("baseline.sql.tmp", directory);
  const { child, completed } = tool("pg_dump", [
    "--format=plain", "--clean", "--if-exists", "--no-owner", "--no-privileges",
    ...tables.flatMap((table) => ["--table", `public.${table}`]),
  ]);
  try {
    await Promise.all([pipeline(child.stdout, createWriteStream(temporary)), completed]);
    const snapshot: Snapshot = { layoutVersion: 2, size, profiles, dataset, sha256: await hash(temporary), createdAt: new Date().toISOString() };
    await rename(temporary, sqlFile);
    await writeFile(metadataFile, `${JSON.stringify(snapshot, null, 2)}\n`);
    return snapshot;
  } finally {
    await rm(temporary, { force: true });
  }
}

export async function loadSnapshot(expectedSize: number): Promise<Snapshot> {
  const { sqlFile, metadataFile } = files();
  let snapshot: Snapshot;
  try {
    snapshot = JSON.parse(await readFile(metadataFile, "utf8")) as Snapshot;
  } catch {
    throw new Error("No valid snapshot found. Run npm run db:init first.");
  }
  if (snapshot.layoutVersion !== 2 || !snapshot.profiles) {
    throw new Error("Snapshot layout is outdated. Run npm run db:init to create the three-profile baseline.");
  }
  if (snapshot.size !== expectedSize) {
    throw new Error(`Snapshot SIZE=${snapshot.size} differs from SIZE=${expectedSize}. Use the snapshot size or run db:init to replace it.`);
  }
  if (snapshot.dataset && (snapshot.dataset.generatorVersion !== generatorVersion ||
      (snapshot.dataset.seed !== null && (!Number.isInteger(snapshot.dataset.seed) || snapshot.dataset.seed < 1 || snapshot.dataset.seed > 0xffffffff)))) {
    throw new Error("Unsupported snapshot dataset generator or seed");
  }
  if (await hash(sqlFile) !== snapshot.sha256) throw new Error("Snapshot checksum mismatch; restore aborted.");
  return snapshot;
}

export async function restoreSnapshot(expectedSize: number): Promise<Snapshot> {
  const snapshot = await loadSnapshot(expectedSize);
  const { sqlFile } = files();
  const { child, completed } = tool("psql", ["-X", "--quiet", "--single-transaction", "--set", "ON_ERROR_STOP=1"]);
  await Promise.all([pipeline(createReadStream(sqlFile), child.stdin), completed]);
  return snapshot;
}
