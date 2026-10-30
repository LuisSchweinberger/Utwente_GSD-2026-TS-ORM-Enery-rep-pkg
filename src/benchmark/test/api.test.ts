import assert from "node:assert/strict";
import { after, test } from "node:test";
import type { Server } from "node:http";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import pg from "pg";
import { benchmarkSize, databaseUrl, queryCount } from "../src/config.js";
import { initDatabase } from "../src/init.js";
import { loadSnapshot, restoreSnapshot } from "../src/snapshot.js";
import { createApp } from "../src/server.js";
import { prismaAdapter } from "../src/prisma.js";
import { sequelizeAdapter } from "../src/sequelize.js";
import { drizzleAdapter } from "../src/drizzle.js";
import { profileNames, type ProfileName } from "../src/profiles.js";
import { scenarioNames, scenarioProfiles, scenarioRequest, type ScenarioName } from "../src/scenarios.js";
import type { Adapter } from "../src/types.js";
import { verifyTask } from "../src/verify.js";

const size = benchmarkSize();
const count = queryCount(size);
const snapshotDirectory = await mkdtemp(join(tmpdir(), "orm-snapshot-test-"));
process.env.SNAPSHOT_DIR = snapshotDirectory;
const client = new pg.Client({ connectionString: databaseUrl() });
await client.connect();
after(async () => {
  await client.end();
  await rm(snapshotDirectory, { recursive: true, force: true });
});

test("seeded snapshots reproduce row contents and verification detects unchanged-count corruption", async () => {
  await initDatabase(size, 101);
  const first = await loadSnapshot(size);
  const firstRow = (await client.query("SELECT * FROM owners WHERE id=1")).rows[0];
  await initDatabase(size, 101);
  const repeated = await loadSnapshot(size);
  assert.equal(first.dataset?.contentSha256, repeated.dataset?.contentSha256);
  assert.deepEqual((await client.query("SELECT * FROM owners WHERE id=1")).rows[0], firstRow);
  await initDatabase(size, 102);
  const changed = await loadSnapshot(size);
  assert.notEqual(first.dataset?.contentSha256, changed.dataset?.contentSha256);
  assert.notDeepEqual((await client.query("SELECT * FROM owners WHERE id=1")).rows[0], firstRow);
  await client.query("UPDATE owners SET first_name='corrupt' WHERE id=1");
  await assert.rejects(verifyTask({ formatVersion: 2, orm: "prisma", scenario: "read-pet", profile: "populated",
    runId: "corruption-check", size, queryCount: 1, status: "pending_verification", requests: [{ queryId: 1, status: 200 }] }), /owners ID 1/);
  await restoreSnapshot(size);
});

async function send(base: string, request: ReturnType<typeof scenarioRequest>) {
  const response = await fetch(`${base}${request.path}`, {
    method: request.method,
    headers: request.body ? { "content-type": "application/json" } : undefined,
    body: request.body ? JSON.stringify(request.body) : undefined,
  });
  const data: unknown = response.headers.get("content-type")?.includes("application/json")
    ? await response.json()
    : await response.text();
  return { status: response.status, data };
}

async function assertBaseline(size: number) {
  const result = await client.query(`SELECT
    (SELECT count(*)::int FROM owners) AS owners,
    (SELECT count(*)::int FROM pets) AS pets,
    (SELECT count(*)::int FROM visits) AS visits,
    (SELECT count(*)::int FROM types) AS types,
    (SELECT count(*)::int FROM vets) AS vets,
    (SELECT count(*)::int FROM specialties) AS specialties,
    (SELECT count(*)::int FROM vet_specialties) AS vet_specialties`);
  assert.deepEqual(result.rows[0], {
    owners: 3 * size, pets: 4 * size, visits: 4 * size,
    types: 6, vets: 6, specialties: 3, vet_specialties: 5,
  });
}

async function listen(app: ReturnType<typeof createApp>): Promise<Server> {
  return new Promise((resolve, reject) => {
    const server = app.listen(0);
    server.once("listening", () => resolve(server));
    server.once("error", reject);
  });
}

test(`all APIs match for ${count} IDs per valid scenario/profile (SIZE=${size})`, async () => {
  const adapters: Record<string, () => Adapter> = {
    prisma: prismaAdapter,
    sequelize: sequelizeAdapter,
    drizzle: drizzleAdapter,
  };
  const reference = new Map<string, unknown[]>();
  await initDatabase(size);

  // The new snapshot must contain exactly the three specified fixture profiles.
  const profileCounts = await client.query(`SELECT
    count(*) FILTER (WHERE id BETWEEN 1 AND $1)::int AS populated_owners,
    count(*) FILTER (WHERE id BETWEEN $1 + 1 AND 2 * $1)::int AS no_visits_owners,
    count(*) FILTER (WHERE id BETWEEN 2 * $1 + 1 AND 3 * $1)::int AS no_pets_owners
    FROM owners`, [size]);
  assert.deepEqual(profileCounts.rows[0], { populated_owners: size, no_visits_owners: size, no_pets_owners: size });

  for (const [name, factory] of Object.entries(adapters)) {
    const adapter = factory();
    const server = await listen(createApp(adapter, name as "prisma" | "sequelize" | "drizzle"));
    try {
      const port = (server.address() as { port: number }).port;
      const base = `http://127.0.0.1:${port}`;
      const health = await fetch(`${base}/health`);
      assert.deepEqual(await health.json(), { status: "ok", orm: name });

      for (const scenario of scenarioNames) {
        for (const profile of profileNames.filter((candidate) => scenarioProfiles[scenario].includes(candidate))) {
          await restoreSnapshot(size);
          await assertBaseline(size);
          const key = `${scenario}:${profile}`;
          const actual: unknown[] = [];
          for (let i = 0; i < count; i += 1) {
            const result = await send(base, scenarioRequest(scenario, profile as ProfileName, i, size));
            const expectedStatus = scenario.startsWith("create-") ? 201 : 200;
            assert.equal(result.status, expectedStatus, `${name} ${key}, ID ${i + 1}`);

            if (scenario === "read-owner") {
              const data = result.data as { pets: Array<{ visits: unknown[] }> };
              if (profile === "populated") {
                assert.equal(data.pets.length, 2);
                assert.ok(data.pets.every((p) => p.visits.length === 2));
              } else if (profile === "no-visits") {
                assert.equal(data.pets.length, 2);
                assert.ok(data.pets.every((p) => p.visits.length === 0));
              } else assert.deepEqual(data.pets, []);
            }
            if (scenario === "create-pet") assert.deepEqual(Object.keys(result.data as object).sort(), ["id"]);
            if (scenario === "create-owner") assert.deepEqual(Object.keys(result.data as object).sort(), ["ownerId", "petIds"]);
            if (scenario === "update-pet") assert.deepEqual(result.data, { updated: 1 });
            if (scenario === "update-owner") {
              assert.deepEqual(result.data, { owners: 1, pets: profile === "no-pets" ? 0 : 2 });
            }
            actual.push(result);
          }
          await verifyTask({
            formatVersion: 2,
            orm: name,
            scenario,
            profile,
            runId: `test-${name}-${scenario}-${profile}`,
            size,
            queryCount: count,
            status: "pending_verification",
            requests: actual.map((result, index) => ({
              queryId: index + 1,
              status: (result as { status: number }).status,
            })),
          });
          const expected = reference.get(key);
          if (expected === undefined) reference.set(key, actual);
          else assert.deepEqual(actual, expected, `${name} differs for ${key}`);
        }
      }
      const missingPetId = 4 * size + 1;
      assert.equal((await fetch(`${base}/pets/${missingPetId}`)).status, 404);
      assert.equal((await fetch(`${base}/pets/0`)).status, 400);
    } finally {
      await new Promise<void>((resolve, reject) => server.close((error) => error ? reject(error) : resolve()));
      await adapter.close();
    }
  }
});
