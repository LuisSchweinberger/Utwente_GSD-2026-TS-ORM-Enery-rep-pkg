import express from "express";
import type { NextFunction, Request, Response } from "express";
import { databaseUrl } from "./config.js";
import type { Adapter, NewOwner, NewPet } from "./types.js";

export type Orm = "prisma" | "sequelize" | "drizzle";

async function createAdapter(orm: Orm): Promise<Adapter> {
  switch (orm) {
    case "prisma": return (await import("./prisma.js")).prismaAdapter();
    case "sequelize": return (await import("./sequelize.js")).sequelizeAdapter();
    case "drizzle": return (await import("./drizzle.js")).drizzleAdapter();
  }
}

function id(value: string): number {
  const number = Number(value);
  if (!Number.isSafeInteger(number) || number < 1) throw new Error("ID must be a positive integer");
  return number;
}
function text(value: unknown): string {
  if (typeof value !== "string" || !value.trim()) throw new Error("Expected a nonempty string");
  return value;
}
function isoDate(value: unknown): string {
  const result = text(value);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(result) || Number.isNaN(Date.parse(`${result}T00:00:00Z`))) throw new Error("Expected YYYY-MM-DD");
  return result;
}
function pet(value: Record<string, unknown>): NewPet {
  return { name: text(value.name), birthDate: isoDate(value.birthDate), typeId: id(String(value.typeId)), ownerId: id(String(value.ownerId)) };
}
function owner(value: Record<string, unknown>): NewOwner {
  if (!Array.isArray(value.pets) || value.pets.length !== 2) throw new Error("Expected exactly two pets");
  return {
    firstName: text(value.firstName), lastName: text(value.lastName), address: text(value.address),
    city: text(value.city), telephone: text(value.telephone),
    pets: value.pets.map((p: Record<string, unknown>) => ({ name: text(p.name), birthDate: isoDate(p.birthDate), typeId: id(String(p.typeId)) })),
  };
}

export function createApp(adapter: Adapter, orm?: Orm): express.Express {
  const app = express();
  app.use(express.json());
  app.get("/health", (_req, res) => res.json({ status: "ok", ...(orm ? { orm } : {}) }));
  app.get("/pets/:id", async (req, res) => {
    const result = await adapter.readPet(id(req.params.id));
    if (!result) return res.sendStatus(404);
    return res.json(result);
  });
  app.get("/owners/:id/pets", async (req, res) => {
    const result = await adapter.readOwner(id(req.params.id));
    if (!result) return res.sendStatus(404);
    return res.json(result);
  });
  app.post("/pets", async (req, res) => res.status(201).json(await adapter.createPet(pet(req.body))));
  app.post("/owners-with-pets", async (req, res) => res.status(201).json(await adapter.createOwner(owner(req.body))));
  app.patch("/pets/:id", async (req, res) => {
    const updated = await adapter.updatePet(id(req.params.id), text(req.body.name));
    if (!updated) return res.sendStatus(404);
    return res.json({ updated });
  });
  app.patch("/owners/:id/pets", async (req, res) => {
    const result = await adapter.updateOwner(id(req.params.id), text(req.body.address), text(req.body.petName));
    if (!result.owners) return res.sendStatus(404);
    return res.json(result);
  });
  app.delete("/visits/:id", async (req, res) => res.json({ deleted: await adapter.deleteVisit(id(req.params.id)) }));
  app.delete("/owners/:id/visits", async (req, res) => res.json({ deleted: await adapter.deleteOwnerVisits(id(req.params.id)) }));
  app.use((error: unknown, _req: Request, res: Response, _next: NextFunction) => {
    if (error instanceof Error && (error.message.startsWith("Expected") || error.message.startsWith("ID must"))) {
      res.status(400).json({ error: error.message });
      return;
    }
    console.error(error);
    res.status(500).json({ error: "Database operation failed" });
  });
  return app;
}

if (process.argv[1] && import.meta.url === new URL(`file://${process.argv[1]}`).href) {
  const orm = process.argv[2] as Orm;
  if (!["prisma", "sequelize", "drizzle"].includes(orm)) throw new Error("Choose prisma, sequelize, or drizzle");
  databaseUrl();
  const adapter = await createAdapter(orm);
  const port = Number(process.env.PORT ?? 3100);
  const server = createApp(adapter, orm).listen(port, () => console.log(`${orm} API listening on ${port}`));
  const shutdown = () => server.close(() => void adapter.close());
  process.once("SIGINT", shutdown);
  process.once("SIGTERM", shutdown);
}
