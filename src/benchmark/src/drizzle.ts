import { eq, inArray } from "drizzle-orm";
import { drizzle } from "drizzle-orm/node-postgres";
import { date } from "./types.js";
import type { Adapter, NewOwner, NewPet, OwnerWithPets, PetResult } from "./types.js";
import pg from "pg";
import { integer, pgTable, serial, text, date as pgDate, unique } from "drizzle-orm/pg-core";
import { databasePoolMax, databaseUrl } from "./config.js";

export const owners = pgTable("owners", {
  id: serial("id").primaryKey(), firstName: text("first_name"), lastName: text("last_name"),
  address: text("address"), city: text("city"), telephone: text("telephone"),
});
export const types = pgTable("types", { id: serial("id").primaryKey(), name: text("name") });
export const pets = pgTable("pets", {
  id: serial("id").primaryKey(), name: text("name"), birthDate: pgDate("birth_date"),
  typeId: integer("type_id").notNull().references(() => types.id), ownerId: integer("owner_id").references(() => owners.id),
});
export const visits = pgTable("visits", {
  id: serial("id").primaryKey(), petId: integer("pet_id").references(() => pets.id),
  visitDate: pgDate("visit_date"), description: text("description"),
});
export const vets = pgTable("vets", { id: serial("id").primaryKey(), firstName: text("first_name"), lastName: text("last_name") });
export const specialties = pgTable("specialties", { id: serial("id").primaryKey(), name: text("name") });
export const vetSpecialties = pgTable("vet_specialties", {
  vetId: integer("vet_id").notNull().references(() => vets.id),
  specialtyId: integer("specialty_id").notNull().references(() => specialties.id),
}, (t) => [unique().on(t.vetId, t.specialtyId)]);

function pet(row: typeof pets.$inferSelect): PetResult {
  return { id: row.id, name: row.name, birthDate: date(row.birthDate), typeId: row.typeId, ownerId: row.ownerId };
}

export function drizzleAdapter(): Adapter {
  const pool = new pg.Pool({ connectionString: databaseUrl(), max: databasePoolMax });
  const db = drizzle(pool);
  const readOwner = async (id: number): Promise<OwnerWithPets | null> => {
    const [o] = await db.select().from(owners).where(eq(owners.id, id));
    if (!o) return null;
    const rows = await db.select().from(pets).innerJoin(types, eq(pets.typeId, types.id)).where(eq(pets.ownerId, id));
    const petIds = rows.map((r) => r.pets.id);
    const visitRows = petIds.length ? await db.select().from(visits).where(inArray(visits.petId, petIds)) : [];
    return {
      id: o.id, firstName: o.firstName, lastName: o.lastName, address: o.address, city: o.city, telephone: o.telephone,
      pets: rows.map((r) => ({
        ...pet(r.pets), type: { id: r.types.id, name: r.types.name },
        visits: visitRows.filter((v) => v.petId === r.pets.id).map((v) => ({ id: v.id, visitDate: date(v.visitDate), description: v.description })).sort((a, b) => a.id - b.id),
      })).sort((a, b) => a.id - b.id),
    };
  };
  return {
    close: () => pool.end(),
    async readPet(id) { const [row] = await db.select().from(pets).where(eq(pets.id, id)); return row ? pet(row) : null; },
    readOwner,
    async createPet(data: NewPet) {
      const [row] = await db.insert(pets).values(data).returning({ id: pets.id });
      return { id: row.id };
    },
    async createOwner(data: NewOwner) {
      return db.transaction(async (tx) => {
        const [o] = await tx.insert(owners).values({ firstName: data.firstName, lastName: data.lastName, address: data.address, city: data.city, telephone: data.telephone }).returning();
        const createdPets = await tx.insert(pets).values(data.pets.map((p) => ({ ...p, ownerId: o.id }))).returning({ id: pets.id });
        return { ownerId: o.id, petIds: createdPets.map((p) => p.id) };
      });
    },
    async updatePet(id, name) { return (await db.update(pets).set({ name }).where(eq(pets.id, id)).returning({ id: pets.id })).length; },
    async updateOwner(id, address, petName) {
      return db.transaction(async (tx) => {
        const [o] = await tx.update(owners).set({ address }).where(eq(owners.id, id)).returning();
        if (!o) return { owners: 0, pets: 0 };
        const updatedPets = await tx.update(pets).set({ name: petName }).where(eq(pets.ownerId, id)).returning({ id: pets.id });
        return { owners: 1, pets: updatedPets.length };
      });
    },
    async deleteVisit(id) { return (await db.delete(visits).where(eq(visits.id, id)).returning({ id: visits.id })).length; },
    async deleteOwnerVisits(id) {
      const petIds = db.select({ id: pets.id }).from(pets).where(eq(pets.ownerId, id));
      return (await db.delete(visits).where(inArray(visits.petId, petIds)).returning({ id: visits.id })).length;
    },
  };
}
