# Workloads and measurement methodology

## Dataset and tasks

`db/schema.sql` adapts Spring PetClinic's PostgreSQL schema (Apache-2.0), retaining seven tables and omitting secondary indexes. Reference tables have fixed small datasets. `SIZE` counts owners **per profile**:

| Profile | Owners | Pets | Visits |
| --- | ---: | ---: | ---: |
| `populated` | SIZE | 2 × SIZE | 4 × SIZE |
| `no-visits` | SIZE | 2 × SIZE | 0 |
| `no-pets` | SIZE | 0 | 0 |

Each populated owner has two pets and each pet two visits. Profile ID ranges do not overlap. The full snapshot has `3 × SIZE` owners, `4 × SIZE` pets and `4 × SIZE` visits.

Seeded generation varies owner/pet/visit values while preserving counts, IDs, relationships and reference tables. Seed-derived strings have fixed lengths within their field/profile, avoiding changing payload size with trial seed. `petclinic-v1` identifies the deterministic generator; seed + SIZE + generator version reproduce contents across machines. Snapshot metadata records both SQL-file checksum and a canonical generated-row content checksum (dump bytes can differ despite identical rows). Legacy unseeded snapshots retain their original values.

`QUERY_COUNT` counts HTTP requests, **not SQL statements**, using distinct sequential IDs. A task is a scenario/profile combination:

| Scenario | Operation | Profiles |
| --- | --- | --- |
| `read-pet` | Read one pet | populated |
| `read-owner` | Read owner, pets, types and visits | all three |
| `create-pet` | Create a pet for an existing owner | populated |
| `create-owner` | Atomically create an owner and two pets | populated |
| `update-pet` | Rename one pet | populated |
| `update-owner` | Atomically update address and related pet names | all three |
| `delete-visit` | Delete one visit | populated |
| `delete-owner-visits` | Delete visits for an owner's pets | all three |

There are 14 tasks. Responses normalize dates/relation ordering and return IDs/counts for writes. Pool maximum is five; only the selected adapter is imported.

**SQL comparison limitation:** advanced reads use Prisma nested relations, Sequelize separate selects, and Drizzle a pets/types join plus owner/visit selects. Equal application results do not imply equal SQL plans or query counts; timings compare the concrete implementations.

## Experimental flow

One trial contains all tasks for all three ORMs. It uses a new dataset with seed `experiment seed + zero-based trial index` and one idle baseline shared by the three blocks. PostgreSQL is started/stopped per trial; API startup/shutdown is per ORM block.

```text
Trial cooldown (PostgreSQL stopped)
→ start PostgreSQL and wait for readiness
→ generate seeded data and archive snapshot
→ measure idle baseline (PostgreSQL running, API/client stopped)
→ for each rotated ORM:
    ORM cooldown → start API → /health
    for each task in the trial's shared shuffled order:
        restore snapshot → prepare sender/collector → measure requests → verify
    save ORM report → stop API
→ stop PostgreSQL
```

All ORMs share identical data and task order within a trial. ORM order rotates one position per trial. Three-trial cycles give each ORM every position once. Other trial counts are allowed and may leave one extra observation in some positions.

The API stays alive between tasks, retaining runtime/pool state. No explicit warm-up requests are sent. First-task connection costs remain measured; subsequent tasks can use established connections. Restore includes sequences and is transactional. These operations do not guarantee cold OS caches.

The controller uses a monotonic clock from immediately before `GO` until it receives `DONE`, after the final full response body. Small pipe/progress overhead is included. This is end-to-end HTTP time, not isolated SQL time. Restore, preparation, startup, cooling, idle measurement, writing and verification are outside the workload window.

## Reporting and correctness

Every task measurement is retained. Means, medians and counts are computed **separately for every ORM + task**, across complete-trial indices. Available energy domains stay separate. Invalid/missing results are excluded and partial summaries explicitly marked incomplete. Baselines are kept separately; no baseline subtraction or inferential tests are performed automatically.

Verification derives expected initial values from snapshot seed/version, applies the task's expected changes, and checks complete owner/pet/visit contents, deleted/created IDs and all table counts. Tests compare responses across all ORMs, test empty relationships, seeded reproducibility and corruption detection. A wrong value is rejected even if counts are unchanged.

The protocol follows the user's V2 flow and clarified ordering/lifecycle, with Assignment 2 and *Estimating the energy footprint of software systems* as background references. Machines/backends are analyzed separately.

## Energy backends

Energy is **host hardware-domain consumption**, including client/API/PostgreSQL, background activity and collector overhead. Overlapping domains are never summed. Missing DRAM remains unavailable; CPU/package energy is not a substitute. Apple estimates and Intel RAPL are not interchangeable across machines.

### Powermetrics + Zeus (Apple Silicon macOS)

`MEASUREMENT_BACKEND=powermetrics_zeus` always runs both collectors; failure of
either invalidates the measurement. The former CPU-only `powermetrics` backend
is not selectable for new runs. Legacy stored results remain unchanged.

Available CPU/GPU/ANE samplers emit NUL-separated plist output using noninteractive sudo. Supported fields are interval energy in mJ, power in mW, and Intel Mac `package_joules`. Raw output, stderr and normalized samples are retained.

Some plist dates have second-only precision. The first sample is anchored to monotonic receipt, then advanced using `elapsed_ns`. Receipt lag is recorded. Partial intervals are allocated by overlap, assuming uniform power within an interval; energy is estimated, particularly for short windows. Collection begins before and extends through each measured window. Coverage below 99% fails; fewer than three overlapping samples gives `quality: limited`.

Zeus (`zeus-apple-silicon==1.1.0`) reads IOReport's cumulative `dram_mj` field
for host-wide unified-memory energy. Two boundary snapshots give a delta in mJ,
converted to J without baseline subtraction. This private Apple Energy Model
interface provides estimates, not calibrated power-rail measurements. It does
not attribute memory energy to individual processes. CPU/GPU/ANE still come only
from powermetrics; Zeus's overlapping CPU/cache readings are not added.

The first memory snapshot precedes controller GO; the final snapshot follows
controller DONE and precedes powermetrics drain/shutdown. Both snapshot calls are
bracketed with monotonic timestamps. `counterWindowElapsedMs`, offsets and average
power use estimated call midpoints; `counterWindowBoundsMs` and snapshot brackets
retain timing uncertainty. Read overhead (~3.6 ms per call in a local probe) and
extra-window activity are not silently subtracted. Short-task bias must be
assessed during pilot calibration. DRAM uses `sampleCount: 2` and
`quality: model_counter_delta`, not interval-sampler coverage rules.

Like Intel, the result envelope contains `domains[]`, with `id`, `name`,
`energyJ`, `averagePowerW`, `sampleCount`, timing and quality fields. Mac memory
is `name: dram`, `id: ioreport:dram`; its source/version and raw snapshots are
retained in a separate `.energy.raw.memory.json` sidecar. Identical output units
do not imply identical hardware scope between machines.

### Intel RAPL (Linux)

Powercap domains require readable `name`, `energy_uj` and `max_energy_range_uj`; symlinks are deduplicated. Periodic and boundary readings provide wrap-aware deltas, assuming at most one wrap between reads. Stalled sampling fails. Raw readings retain zone identity and counter-window offsets/duration.

RAPL average watts use counter duration; powermetrics average watts use controller duration. Verified tasks receive joules per operation. Sampling defaults to 10 Hz, balancing overhead and temporal resolution as discussed in the reference.
