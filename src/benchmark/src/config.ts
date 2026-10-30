import "dotenv/config";

export function databaseUrl(): string {
  if (!process.env.DATABASE_URL) throw new Error("DATABASE_URL is required; copy .env.example to .env");
  return process.env.DATABASE_URL;
}

export const databasePoolMax = 5;

export function prismaDatabaseUrl(): string {
  const url = new URL(databaseUrl());
  if (!url.searchParams.has("connection_limit")) url.searchParams.set("connection_limit", String(databasePoolMax));
  return url.toString();
}

function integerEnv(name: string, fallback: number, minimum: number, maximum: number): number {
  const raw = process.env[name];
  const value = raw === undefined || raw === "" ? fallback : Number(raw);
  if (!Number.isInteger(value) || value < minimum || value > maximum) {
    throw new Error(`${name} must be an integer from ${minimum} to ${maximum}`);
  }
  return value;
}

export function benchmarkSize(): number {
  return integerEnv("SIZE", 1000, 1, 100000);
}

export function queryCount(size = benchmarkSize()): number {
  return integerEnv("QUERY_COUNT", size, 1, size);
}
