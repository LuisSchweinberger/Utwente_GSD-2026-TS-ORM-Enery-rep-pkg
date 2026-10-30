import { DataTypes, Op, Sequelize } from "sequelize";
import { databasePoolMax, databaseUrl } from "./config.js";
import { date } from "./types.js";
import type { Adapter, NewOwner, NewPet, OwnerWithPets, PetResult } from "./types.js";

type OwnerRow = { id: number; firstName: string | null; lastName: string | null; address: string | null; city: string | null; telephone: string | null };
type PetRow = { id: number; name: string | null; birthDate: string | null; typeId: number; ownerId: number | null };
type TypeRow = { id: number; name: string | null };
type VisitRow = { id: number; petId: number | null; visitDate: string | null; description: string | null };

function pet(row: PetRow): PetResult {
  return { id: row.id, name: row.name, birthDate: date(row.birthDate), typeId: row.typeId, ownerId: row.ownerId };
}

export function sequelizeAdapter(): Adapter {
  const db = new Sequelize(databaseUrl(), { logging: false, pool: { max: databasePoolMax, min: 0 } });
  const options = { timestamps: false, freezeTableName: true } as const;
  const Owner = db.define("owners", {
    id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
    firstName: { type: DataTypes.TEXT, field: "first_name" }, lastName: { type: DataTypes.TEXT, field: "last_name" },
    address: DataTypes.TEXT, city: DataTypes.TEXT, telephone: DataTypes.TEXT,
  }, options);
  const Type = db.define("types", { id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true }, name: DataTypes.TEXT }, options);
  const Pet = db.define("pets", {
    id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true }, name: DataTypes.TEXT,
    birthDate: { type: DataTypes.DATEONLY, field: "birth_date" }, typeId: { type: DataTypes.INTEGER, field: "type_id" },
    ownerId: { type: DataTypes.INTEGER, field: "owner_id" },
  }, options);
  const Visit = db.define("visits", {
    id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
    petId: { type: DataTypes.INTEGER, field: "pet_id" }, visitDate: { type: DataTypes.DATEONLY, field: "visit_date" },
    description: DataTypes.TEXT,
  }, options);
  // Declared for schema parity; database creation always comes from db/schema.sql.
  db.define("vets", { id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true }, firstName: { type: DataTypes.TEXT, field: "first_name" }, lastName: { type: DataTypes.TEXT, field: "last_name" } }, options);
  db.define("specialties", { id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true }, name: DataTypes.TEXT }, options);
  db.define("vet_specialties", {
    vetId: { type: DataTypes.INTEGER, field: "vet_id", allowNull: false },
    specialtyId: { type: DataTypes.INTEGER, field: "specialty_id", allowNull: false },
  }, {
    ...options,
    indexes: [{ unique: true, fields: ["vet_id", "specialty_id"] }],
  });

  const readOwner = async (id: number): Promise<OwnerWithPets | null> => {
    const owner = await Owner.findByPk(id);
    if (!owner) return null;
    const o = owner.get({ plain: true }) as OwnerRow;
    const petRows = (await Pet.findAll({ where: { ownerId: id }, raw: true })) as unknown as PetRow[];
    const typeIds = [...new Set(petRows.map((p) => p.typeId))];
    const types = typeIds.length ? (await Type.findAll({ where: { id: { [Op.in]: typeIds } }, raw: true })) as unknown as TypeRow[] : [];
    const visits = petRows.length ? (await Visit.findAll({ where: { petId: { [Op.in]: petRows.map((p) => p.id) } }, raw: true })) as unknown as VisitRow[] : [];
    return {
      id: o.id, firstName: o.firstName, lastName: o.lastName, address: o.address, city: o.city, telephone: o.telephone,
      pets: petRows.map((p) => ({
        ...pet(p), type: { id: p.typeId, name: types.find((t) => t.id === p.typeId)!.name },
        visits: visits.filter((v) => v.petId === p.id).map((v) => ({ id: v.id, visitDate: date(v.visitDate), description: v.description })).sort((a, b) => a.id - b.id),
      })).sort((a, b) => a.id - b.id),
    };
  };
  return {
    close: () => db.close(),
    async readPet(id) { const row = await Pet.findByPk(id); return row ? pet(row.get({ plain: true }) as PetRow) : null; },
    readOwner,
    async createPet(data: NewPet) { return { id: (await Pet.create(data)).get("id") as number }; },
    async createOwner(data: NewOwner) {
      return db.transaction(async (transaction) => {
        const row = await Owner.create({ firstName: data.firstName, lastName: data.lastName, address: data.address, city: data.city, telephone: data.telephone }, { transaction });
        const id = row.get("id") as number;
        const pets = await Pet.bulkCreate(data.pets.map((p) => ({ ...p, ownerId: id })), { transaction, returning: true });
        return { ownerId: id, petIds: pets.map((p) => p.get("id") as number) };
      });
    },
    async updatePet(id, name) { return (await Pet.update({ name }, { where: { id } }))[0]; },
    async updateOwner(id, address, petName) {
      return db.transaction(async (transaction) => {
        const [ownerCount] = await Owner.update({ address }, { where: { id }, transaction });
        if (!ownerCount) return { owners: 0, pets: 0 };
        const [petCount] = await Pet.update({ name: petName }, { where: { ownerId: id }, transaction });
        return { owners: ownerCount, pets: petCount };
      });
    },
    deleteVisit(id) { return Visit.destroy({ where: { id } }); },
    async deleteOwnerVisits(id) {
      const rows = await Pet.findAll({ attributes: ["id"], where: { ownerId: id }, raw: true });
      return rows.length ? Visit.destroy({ where: { petId: { [Op.in]: rows.map((p) => (p as unknown as { id: number }).id) } } }) : 0;
    },
  };
}
