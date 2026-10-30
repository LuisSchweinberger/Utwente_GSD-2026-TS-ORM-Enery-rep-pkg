import { PrismaClient } from "@prisma/client";
import type { Adapter, NewOwner, NewPet, OwnerUpdateResult, OwnerWithPets, PetResult } from "./types.js";
import { date } from "./types.js";
import { prismaDatabaseUrl } from "./config.js";

const includes = { pets: { include: { type: true, visits: true } } } as const;
type PetRow = { id: number; name: string | null; birthDate: Date | null; typeId: number; ownerId: number | null };
function pet(row: PetRow): PetResult {
  return { id: row.id, name: row.name, birthDate: date(row.birthDate), typeId: row.typeId, ownerId: row.ownerId };
}
type OwnerRow = NonNullable<Awaited<ReturnType<PrismaClient["owner"]["findFirst"]>>>;
type DetailedOwner = OwnerRow & { pets: Array<PetRow & { type: { id: number; name: string | null }; visits: Array<{ id: number; visitDate: Date | null; description: string | null }> }> };
function owner(row: DetailedOwner): OwnerWithPets {
  return {
    id: row.id, firstName: row.firstName, lastName: row.lastName, address: row.address,
    city: row.city, telephone: row.telephone,
    pets: row.pets.map((p) => ({
      ...pet(p), type: { id: p.type.id, name: p.type.name },
      visits: p.visits.map((v) => ({ id: v.id, visitDate: date(v.visitDate), description: v.description })).sort((a, b) => a.id - b.id),
    })).sort((a, b) => a.id - b.id),
  };
}

export function prismaAdapter(): Adapter {
  const db = new PrismaClient({ datasources: { db: { url: prismaDatabaseUrl() } } });
  const readOwner = async (id: number) => {
    const row = await db.owner.findUnique({ where: { id }, include: includes });
    return row ? owner(row) : null;
  };
  return {
    close: () => db.$disconnect(),
    async readPet(id) { const row = await db.pet.findUnique({ where: { id } }); return row ? pet(row) : null; },
    readOwner,
    async createPet(data: NewPet) {
      const row = await db.pet.create({
        data: { ...data, birthDate: new Date(`${data.birthDate}T00:00:00Z`) },
        select: { id: true },
      });
      return { id: row.id };
    },
    async createOwner(data: NewOwner) {
      const row = await db.owner.create({ data: {
        firstName: data.firstName, lastName: data.lastName, address: data.address, city: data.city, telephone: data.telephone,
        pets: { create: data.pets.map((p) => ({ ...p, birthDate: new Date(`${p.birthDate}T00:00:00Z`) })) },
      }, select: { id: true, pets: { select: { id: true } } } });
      return { ownerId: row.id, petIds: row.pets.map((p) => p.id) };
    },
    async updatePet(id, name) {
      return (await db.pet.updateMany({ where: { id }, data: { name } })).count;
    },
    async updateOwner(id, address, petName): Promise<OwnerUpdateResult> {
      return db.$transaction(async (tx) => {
        const ownerResult = await tx.owner.updateMany({ where: { id }, data: { address } });
        if (!ownerResult.count) return { owners: 0, pets: 0 };
        const petResult = await tx.pet.updateMany({ where: { ownerId: id }, data: { name: petName } });
        return { owners: ownerResult.count, pets: petResult.count };
      });
    },
    async deleteVisit(id) { return (await db.visit.deleteMany({ where: { id } })).count; },
    async deleteOwnerVisits(id) {
      return (await db.visit.deleteMany({ where: { pet: { ownerId: id } } })).count;
    },
  };
}
