export const profileNames = ["populated", "no-visits", "no-pets"] as const;
export type ProfileName = typeof profileNames[number];

export type ProfileLayout = {
  owners: { start: number; count: number };
  pets: { start: number; count: number };
  visits: { start: number; count: number };
};
export type SnapshotLayout = Record<ProfileName, ProfileLayout>;

export function snapshotLayout(size: number): SnapshotLayout {
  return {
    populated: {
      owners: { start: 1, count: size },
      pets: { start: 1, count: 2 * size },
      visits: { start: 1, count: 4 * size },
    },
    "no-visits": {
      owners: { start: size + 1, count: size },
      pets: { start: 2 * size + 1, count: 2 * size },
      visits: { start: 4 * size + 1, count: 0 },
    },
    "no-pets": {
      owners: { start: 2 * size + 1, count: size },
      pets: { start: 4 * size + 1, count: 0 },
      visits: { start: 4 * size + 1, count: 0 },
    },
  };
}
