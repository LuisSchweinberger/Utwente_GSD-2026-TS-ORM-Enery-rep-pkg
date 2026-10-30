import "dotenv/config";
import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import pg from "pg";
import { databaseUrl } from "./config.js";
import { scenarioProfiles, scenarioRequest, type ScenarioName } from "./scenarios.js";
import { profileNames, snapshotLayout, type ProfileName } from "./profiles.js";
import { ownerRow, petRow, visitRow, type Row } from "./dataset.js";
import { loadSnapshot } from "./snapshot.js";

export type TaskForVerification = {
  formatVersion: number; orm: string; scenario: ScenarioName; profile: ProfileName;
  runId: string; size: number; queryCount: number; status: string;
  snapshot?: { sha256: string };
  requests: Array<{ queryId: number; status: number }>;
};

const columns = {
  owners: "id,first_name,last_name,address,city,telephone",
  pets: "id,name,birth_date::text AS birth_date,type_id,owner_id",
  visits: "id,pet_id,visit_date::text AS visit_date,description",
} as const;

async function checkRows(client: pg.Client, table: keyof typeof columns, first: number, last: number,
                         expected: (id: number) => Row | null): Promise<void> {
  for (let start = first; start <= last; start += 1000) {
    const end = Math.min(last, start + 999);
    const rows = await client.query(`SELECT ${columns[table]} FROM ${table} WHERE id BETWEEN $1 AND $2 ORDER BY id`, [start, end]);
    const actual = new Map<number, Record<string, unknown>>(rows.rows.map((row) => [row.id as number, row]));
    for (let id = start; id <= end; id++) {
      const wanted = expected(id), found = actual.get(id);
      if (wanted === null ? found !== undefined : !found || Object.entries(wanted).some(([key, value]) => found[key] !== value)) {
        throw new Error(`${table} ID ${id} does not match expected task state`);
      }
    }
  }
}

export async function verifyTask(task: TaskForVerification): Promise<string[]> {
  if (![2, 3].includes(task.formatVersion) || task.status !== "pending_verification") throw new Error(`Task status is ${task.status}; only successful unverified tasks can be verified`);
  if (!scenarioProfiles[task.scenario]?.includes(task.profile) || !profileNames.includes(task.profile)) throw new Error("Invalid scenario/profile pair");
  if (task.requests.length !== task.queryCount || task.requests.some((request, i) => request.queryId !== i + 1 || request.status !== (task.scenario.startsWith("create-") ? 201 : 200))) {
    throw new Error("Task request list is incomplete or contains an unexpected status");
  }
  const { size, queryCount: count, scenario, profile } = task;
  const snapshot = await loadSnapshot(size);
  if (task.snapshot && task.snapshot.sha256 !== snapshot.sha256) throw new Error("Task snapshot differs from verification snapshot");
  const seed = snapshot.dataset?.seed ?? null;
  const layout = snapshotLayout(size)[profile];
  const ownerStart = layout.owners.start;
  const targetedOwner = (id: number) => id >= ownerStart && id < ownerStart + count;
  const client = new pg.Client({ connectionString: databaseUrl() });
  await client.connect();
  try {
    const expectedCounts = {
      owners: 3 * size + (scenario === "create-owner" ? count : 0),
      pets: 4 * size + (scenario === "create-owner" ? 2 * count : scenario === "create-pet" ? count : 0),
      visits: 4 * size - (scenario === "delete-visit" ? count : scenario === "delete-owner-visits" && profile === "populated" ? 4 * count : 0),
      types: 6, vets: 6, specialties: 3, vet_specialties: 5,
    };
    for (const [table, expected] of Object.entries(expectedCounts)) {
      const actual = Number((await client.query(`SELECT count(*) AS count FROM ${table}`)).rows[0].count);
      if (actual !== expected) throw new Error(`${table}: expected ${expected} rows, found ${actual}`);
    }
    await checkRows(client, "owners", 1, 3 * size, (id) => {
      const row = ownerRow(size, id, seed);
      if (scenario === "update-owner" && targetedOwner(id)) row.address = `Updated ${id - ownerStart + 1}`;
      return row;
    });
    await checkRows(client, "pets", 1, 4 * size, (id) => {
      const row = petRow(size, id, seed);
      if (scenario === "update-pet" && id >= layout.pets.start && id < layout.pets.start + count) row.name = `UpdatedPet${id - layout.pets.start + 1}`;
      if (scenario === "update-owner" && targetedOwner(Number(row.owner_id))) row.name = `Renamed${Number(row.owner_id) - ownerStart + 1}`;
      return row;
    });
    await checkRows(client, "visits", 1, 4 * size, (id) => {
      const row = visitRow(id, seed);
      if (scenario === "delete-visit" && id >= layout.visits.start && id < layout.visits.start + count) return null;
      const owner = Math.floor((Number(row.pet_id) - 1) / 2) + 1;
      if (scenario === "delete-owner-visits" && profile === "populated" && targetedOwner(owner)) return null;
      return row;
    });
    if (scenario === "create-pet") {
      await checkRows(client, "pets", 4 * size + 1, 4 * size + count, (id) => {
        const index = id - 4 * size - 1;
        const body = scenarioRequest(scenario, profile, index, size).body as { name: string; birthDate: string; typeId: number; ownerId: number };
        return { id, name: body.name, birth_date: body.birthDate, type_id: body.typeId, owner_id: body.ownerId };
      });
    } else if (scenario === "create-owner") {
      type OwnerInput = { firstName: string; lastName: string; address: string; city: string; telephone: string; pets: Array<{ name: string; birthDate: string; typeId: number }> };
      const input = (index: number) => scenarioRequest(scenario, profile, index, size).body as OwnerInput;
      await checkRows(client, "owners", 3 * size + 1, 3 * size + count, (id) => {
        const body = input(id - 3 * size - 1);
        return { id, first_name: body.firstName, last_name: body.lastName, address: body.address, city: body.city, telephone: body.telephone };
      });
      await checkRows(client, "pets", 4 * size + 1, 4 * size + 2 * count, (id) => {
        const offset = id - 4 * size - 1;
        const index = Math.floor(offset / 2), body = input(index).pets[offset % 2];
        return { id, name: body.name, birth_date: body.birthDate, type_id: body.typeId, owner_id: 3 * size + index + 1 };
      });
    }
    return ["table counts and complete expected row contents verified", `effects verified for ${scenario}/${profile}/${count} requests`, `dataset seed: ${seed ?? "legacy"}`];
  } finally { await client.end(); }
}

export async function verifyResultFile(resultPath: string): Promise<void> {
  const task = JSON.parse(await readFile(resultPath, "utf8")) as TaskForVerification & Record<string, unknown>;
  try {
    const checks = await verifyTask(task);
    if (task.formatVersion === 3) {
      const measurement = task.measurement as { status: string; domains: Array<{ energyJ: number; energyPerOperationJ?: number }> } | undefined;
      if (!measurement || measurement.status !== "valid") throw new Error("Task has no valid controller measurement");
      for (const domain of measurement.domains) domain.energyPerOperationJ = domain.energyJ / task.queryCount;
    }
    task.status = "valid";
    task.verification = { valid: true, completedAt: new Date().toISOString(), checks };
  } catch (error) {
    task.status = "invalid";
    task.verification = { valid: false, completedAt: new Date().toISOString(), error: error instanceof Error ? error.message : String(error) };
    await writeFile(resultPath, `${JSON.stringify(task, null, 2)}\n`);
    throw error;
  }
  await writeFile(resultPath, `${JSON.stringify(task, null, 2)}\n`);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  if (process.argv.length !== 4 || process.argv[2] !== "--result") throw new Error("Usage: npm run verify -- --result <task-json>");
  const path = resolve(process.argv[3]);
  await verifyResultFile(path);
  console.log(`Verified ${path}`);
}
