import { profileNames, snapshotLayout, type ProfileName } from "./profiles.js";

export type ScenarioName =
  | "read-pet"
  | "read-owner"
  | "create-pet"
  | "create-owner"
  | "update-pet"
  | "update-owner"
  | "delete-visit"
  | "delete-owner-visits";

export type ScenarioRequest = { method: string; path: string; body?: unknown };

export const scenarioNames: ScenarioName[] = [
  "read-pet", "read-owner", "create-pet", "create-owner",
  "update-pet", "update-owner", "delete-visit", "delete-owner-visits",
];

export const scenarioProfiles: Record<ScenarioName, ProfileName[]> = {
  "read-pet": ["populated"],
  "read-owner": [...profileNames],
  "create-pet": ["populated"],
  "create-owner": ["populated"],
  "update-pet": ["populated"],
  "update-owner": [...profileNames],
  "delete-visit": ["populated"],
  "delete-owner-visits": [...profileNames],
};

export function scenarioRequest(name: ScenarioName, profile: ProfileName, zeroBasedIndex: number, size: number): ScenarioRequest {
  const id = zeroBasedIndex + 1;
  const layout = snapshotLayout(size)[profile];
  switch (name) {
    case "read-pet": return { method: "GET", path: `/pets/${layout.pets.start + zeroBasedIndex}` };
    case "read-owner": return { method: "GET", path: `/owners/${layout.owners.start + zeroBasedIndex}/pets` };
    case "create-pet": return {
      method: "POST", path: "/pets",
      body: { name: `BenchPet${id}`, birthDate: "2020-01-01", typeId: 1, ownerId: layout.owners.start + zeroBasedIndex },
    };
    case "create-owner": return {
      method: "POST", path: "/owners-with-pets",
      body: {
        firstName: `Bench${id}`, lastName: "Owner", address: `${id} Main St`, city: "Madison", telephone: "1234567890",
        pets: [
          { name: `First${id}`, birthDate: "2020-01-01", typeId: 1 },
          { name: `Second${id}`, birthDate: "2020-01-02", typeId: 2 },
        ],
      },
    };
    case "update-pet": return { method: "PATCH", path: `/pets/${layout.pets.start + zeroBasedIndex}`, body: { name: `UpdatedPet${id}` } };
    case "update-owner": return { method: "PATCH", path: `/owners/${layout.owners.start + zeroBasedIndex}/pets`, body: { address: `Updated ${id}`, petName: `Renamed${id}` } };
    case "delete-visit": return { method: "DELETE", path: `/visits/${layout.visits.start + zeroBasedIndex}` };
    case "delete-owner-visits": return { method: "DELETE", path: `/owners/${layout.owners.start + zeroBasedIndex}/visits` };
  }
}
