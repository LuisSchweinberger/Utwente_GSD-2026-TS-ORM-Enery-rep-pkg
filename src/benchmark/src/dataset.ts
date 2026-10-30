/** Reproducible row values shared by initialization and correctness verification. */
export const generatorVersion = "petclinic-v1";
export type Dataset = { generatorVersion: typeof generatorVersion; seed: number | null; contentSha256?: string };
export type Row = Record<string, string | number>;

export function datasetSeed(): number | null {
  const raw = process.env.DATASET_SEED;
  if (raw === undefined || raw === "") return null;
  const seed = Number(raw);
  if (!Number.isInteger(seed) || seed < 1 || seed > 0xffffffff) throw new Error("DATASET_SEED must be between 1 and 4294967295");
  return seed;
}

function value(seed: number, id: number, channel: number): number {
  let x = (seed ^ Math.imul(id, 0x9e3779b1) ^ Math.imul(channel, 0x85ebca6b)) >>> 0;
  x ^= x << 13; x ^= x >>> 17; x ^= x << 5;
  return x >>> 0;
}
function token(seed: number, id: number, channel: number): string {
  return value(seed, id, channel).toString(16).padStart(8, "0");
}
function day(base: string, offset: number): string {
  const date = new Date(`${base}T00:00:00Z`);
  date.setUTCDate(date.getUTCDate() + offset);
  return date.toISOString().slice(0, 10);
}

export function ownerRow(size: number, id: number, seed: number | null): Row {
  const profile = id <= size ? "Populated" : id <= 2 * size ? "NoVisits" : "NoPets";
  const local = (id - 1) % size + 1;
  return {
    id, first_name: seed === null ? `${profile}${local}` : `${profile}${token(seed, id, 1)}`,
    last_name: seed === null ? "Owner" : `Owner${token(seed, id, 2)}`,
    address: seed === null ? `${local} Sample Street` : `${token(seed, id, 3)} Sample Street`,
    city: seed === null ? "Madison" : `City${token(seed, id, 4)}`,
    telephone: seed === null ? "6085550000" : String(value(seed, id, 5) % 1000000000).padStart(10, "0"),
  };
}

export function petRow(size: number, id: number, seed: number | null): Row {
  const populated = id <= 2 * size;
  const local = populated ? id : id - 2 * size;
  const owner = Math.floor((local - 1) / 2) + 1;
  const position = (local - 1) % 2 + 1;
  return { id, name: seed === null ? `${populated ? "Populated" : "NoVisits"}Pet${owner}-${position}` : `Pet${token(seed, id, 6)}`,
    birth_date: day("2020-01-01", seed === null ? (owner + position) % 365 : value(seed, id, 7) % 365),
    type_id: position, owner_id: owner + (populated ? 0 : size) };
}

export function visitRow(id: number, seed: number | null): Row {
  const pet = Math.floor((id - 1) / 2) + 1;
  const position = (id - 1) % 2 + 1;
  return { id, pet_id: pet, visit_date: day("2023-01-01", seed === null ? position : value(seed, id, 8) % 365),
    description: seed === null ? `Visit ${pet}-${position}` : `Visit${token(seed, id, 9)}` };
}
