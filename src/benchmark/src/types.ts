export type NewPet = { name: string; birthDate: string; typeId: number; ownerId: number };
export type NewOwner = {
  firstName: string; lastName: string; address: string; city: string; telephone: string;
  pets: Array<{ name: string; birthDate: string; typeId: number }>;
};
export type PetResult = { id: number; name: string | null; birthDate: string | null; typeId: number; ownerId: number | null };
export type OwnerResult = {
  id: number; firstName: string | null; lastName: string | null; address: string | null;
  city: string | null; telephone: string | null;
};
export type OwnerWithPets = OwnerResult & {
  pets: Array<PetResult & { type: { id: number; name: string | null }; visits: Array<{ id: number; visitDate: string | null; description: string | null }> }>;
};
export type CreatedOwner = { ownerId: number; petIds: number[] };
export type OwnerUpdateResult = { owners: number; pets: number };

export interface Adapter {
  close(): Promise<void>;
  readPet(id: number): Promise<PetResult | null>;
  readOwner(id: number): Promise<OwnerWithPets | null>;
  createPet(data: NewPet): Promise<{ id: number }>;
  createOwner(data: NewOwner): Promise<CreatedOwner>;
  updatePet(id: number, name: string): Promise<number>;
  updateOwner(id: number, address: string, petName: string): Promise<OwnerUpdateResult>;
  deleteVisit(id: number): Promise<number>;
  deleteOwnerVisits(id: number): Promise<number>;
}

export function date(value: Date | string | null): string | null {
  return value === null ? null : value instanceof Date ? value.toISOString().slice(0, 10) : value.slice(0, 10);
}
