import { readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import pg from "pg";
import { benchmarkSize, databaseUrl } from "./config.js";
import { saveSnapshot } from "./snapshot.js";
import { snapshotLayout } from "./profiles.js";
import { datasetSeed, generatorVersion, ownerRow, petRow, visitRow, type Row } from "./dataset.js";

export async function initDatabase(size = benchmarkSize(), seed = datasetSeed()): Promise<void> {
  if (!Number.isInteger(size) || size < 1 || size > 100000) {
    throw new Error("SIZE must be an integer between 1 and 100000");
  }
  if (seed !== null && (!Number.isInteger(seed) || seed < 1 || seed > 0xffffffff)) throw new Error("Invalid dataset seed");
  const client = new pg.Client({ connectionString: databaseUrl() });
  const digest = createHash("sha256");
  await client.connect();
  try {
    await client.query("BEGIN");
    const schema = await readFile(new URL("../db/schema.sql", import.meta.url), "utf8");
    await client.query(schema);
    await client.query("INSERT INTO types (name) VALUES ('cat'), ('dog'), ('lizard'), ('snake'), ('bird'), ('hamster')");
    await client.query("INSERT INTO specialties (name) VALUES ('radiology'), ('surgery'), ('dentistry')");
    await client.query("INSERT INTO vets (first_name, last_name) VALUES ('James', 'Carter'), ('Helen', 'Leary'), ('Linda', 'Douglas'), ('Rafael', 'Ortega'), ('Henry', 'Stevens'), ('Sharon', 'Jenkins')");
    await client.query("INSERT INTO vet_specialties (vet_id, specialty_id) VALUES (2,1), (3,2), (3,3), (4,2), (5,1)");
    async function insert(table: string, count: number, columns: string, declaration: string, row: (id: number) => Row) {
      digest.update(`${table}\n`);
      for (let start = 1; start <= count; start += 1000) {
        const rows = Array.from({ length: Math.min(1000, count - start + 1) }, (_, i) => row(start + i));
        for (const value of rows) digest.update(`${JSON.stringify(value)}\n`);
        await client.query(`INSERT INTO ${table} (${columns}) SELECT ${columns} FROM jsonb_to_recordset($1::jsonb) AS r(${declaration}) ORDER BY id`, [JSON.stringify(rows)]);
      }
      await client.query(`SELECT setval(pg_get_serial_sequence('${table}', 'id'), $1, true)`, [count]);
    }
    await insert("owners", 3 * size, "id,first_name,last_name,address,city,telephone",
      "id int,first_name text,last_name text,address text,city text,telephone text", (id) => ownerRow(size, id, seed));
    await insert("pets", 4 * size, "id,name,birth_date,type_id,owner_id",
      "id int,name text,birth_date date,type_id int,owner_id int", (id) => petRow(size, id, seed));
    await insert("visits", 4 * size, "id,pet_id,visit_date,description",
      "id int,pet_id int,visit_date date,description text", (id) => visitRow(id, seed));
    await client.query("COMMIT");
  } catch (error) {
    await client.query("ROLLBACK");
    throw error;
  } finally {
    await client.end();
  }
  await saveSnapshot(size, snapshotLayout(size), { generatorVersion, seed, contentSha256: digest.digest("hex") });
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const size = benchmarkSize();
  await initDatabase(size);
  console.log(`Database initialized with ${size} owners per profile; SQL snapshot saved`);
}
