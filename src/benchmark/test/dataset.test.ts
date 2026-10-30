import assert from "node:assert/strict";
import { test } from "node:test";
import { ownerRow, petRow, visitRow } from "../src/dataset.js";

test("legacy baseline values remain compatible with existing snapshots", () => {
  assert.deepEqual(ownerRow(10, 11, null), { id: 11, first_name: "NoVisits1", last_name: "Owner", address: "1 Sample Street", city: "Madison", telephone: "6085550000" });
  assert.deepEqual(petRow(10, 21, null), { id: 21, name: "NoVisitsPet1-1", birth_date: "2020-01-03", type_id: 1, owner_id: 11 });
  assert.deepEqual(visitRow(1, null), { id: 1, pet_id: 1, visit_date: "2023-01-02", description: "Visit 1-1" });
});

test("seeded values reproduce and incremented seeds change data without changing layout", () => {
  const rows = (seed: number) => [ownerRow(10, 1, seed), petRow(10, 1, seed), visitRow(1, seed)];
  assert.deepEqual(rows(42), rows(42));
  assert.notDeepEqual(rows(42), rows(43));
  for (const seed of [1, 42, 43, 0xffffffff]) {
    assert.equal(petRow(10, 21, seed).owner_id, 11);
    assert.equal(petRow(10, 21, seed).type_id, 1);
    assert.equal(visitRow(40, seed).pet_id, 20);
    assert.equal(String(ownerRow(10, 1, seed).telephone).length, 10);
    assert.equal(String(ownerRow(10, 1, seed).first_name).length, String(ownerRow(10, 1, 42).first_name).length);
  }
});
