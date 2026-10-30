# Controller architecture

## Modules

From `src/benchmark/`, all run commands invoke `scripts/benchmark.py`. The
controller uses Python's standard library; the Apple energy backend additionally
requires `requirements-mac.txt` (Zeus).

| Module | Responsibility |
| --- | --- |
| `cli.py` | Commands, defaults and experiment progress |
| `config.py` | Resolve/freeze settings; validate snapshot checksums |
| `schedule.py` | Incremented seeds, shuffled tasks, rotating ORM blocks |
| `orchestration.py` | Complete trials, persistent API blocks and task measurements |
| `database.py` | Own the dedicated Compose PostgreSQL lifecycle |
| `processes.py` | Owned process groups, bounded pipes, eager resource cleanup |
| `energy.py` | Monotonic windows, combined powermetrics + Zeus, and RAPL |
| `artifacts.py` | Paths, run-folder replacement and result assembly |
| `manifest.py` | Runtime and configuration metadata |
| `summary.py` | Means/medians and valid counts per ORM/task/domain |

TypeScript remains the object of study. The API/adapters implement ORM behavior; `bench.ts` sends requests; `init.ts`/`reset.ts`/`verify.ts` manage/check data. `dataset.ts` shares seeded expected values between initialization and verification. `control.ts` bridges the existing dotenv loader, task definitions, PostgreSQL driver and runtime metadata.

## Lifecycle and ownership

A trial ensures the dedicated PostgreSQL service is stopped, waits its cooldown, starts it and waits for readiness. It creates a snapshot using `seed + zero-based trial index`, records database metadata, then measures idle power once with API/client stopped.

Each ORM gets its cooldown and one API process. Its 14 tasks use the same shuffled order as the other ORMs. Each task restores the snapshot **while the API remains alive**, prepares a task-specific request sender/collector, waits for `READY`, sends `GO`, measures until `DONE`/`FAILED`, then verifies effects. The API stops after its block; PostgreSQL stops after all three blocks.

Task preparation, output writing and verification are outside timing. Progress is emitted about ten times per batch. Node/Compose subprocesses and file descriptors are released eagerly. Failure/interruption stops owned API process groups and PostgreSQL, retaining raw measurements and failure metadata. Partial summaries are marked incomplete.

## Configuration and output

CLI flags override environment/.env values before validation. `--trials` overrides `TRIALS`; `trial` always runs one complete trial. `--repetitions` remains an alias for `--trials`, and `--cooldown-seconds` for `--trial-cooldown-seconds`. Legacy `COOLDOWN_SECONDS` is used if the new trial-cooldown variable is absent.

Complete trials require `DATABASE_URL` to match the dedicated Compose service. Snapshots are trial-local and do not replace the persistent `db/snapshot` used by standalone tasks. Seed overflow is rejected instead of wrapping. Checksums are pinned within each trial, not across the experiment.

Reusing a complete-trial/pilot/experiment name warns and deletes its entire run folder before recreating it, including extra files and old trial directories. Cleanup does not depend on the previous schedule. Standalone `task` reruns replace only that task's generated files. New schedules contain trial, dataset seed, ORM position/name, task position, scenario and profile columns.

Task results reference their shared baseline. ORM reports list task results and API PID; trial reports contain three blocks. Root JSON/CSV summaries contain mean, median and observation count for time, throughput and available per-domain energy. Invalid/missing values are not replaced with zeros. RAPL zone IDs keep equally named domains on different sockets separate. Baselines are not subtracted; inferential tests are not performed.

## Commands

```sh
# Schedule only:
npm run --silent schedule -- --kind experiment --seed 42 --trials 12

# Named complete trial:
npm run --silent trial -- --seed 42 --run-id check-001

# Standalone task debugging (database/snapshot already available):
npm run db:up
DATASET_SEED=42 npm run db:init
npm run --silent task -- --orm prisma --scenario read-owner --profile populated --run-id check-001

# Direct Python invocation:
python3 scripts/benchmark.py pilot --seed 42 --trials 3
```

`task` starts/stops only its API and saves to `results/<orm>/` plus `logs/`. The former single-ORM/task `trial` command is now `task`.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Compose startup fails | Inspect trial `logs/postgres-start.log`; Docker must support `up --wait` |
| DATABASE_URL mismatch | Match the Compose service's database/user/port |
| API port occupied | Stop the existing API or choose another `PORT` |
| Snapshot mismatch | Keep the trial archive unchanged; inspect its checksum/metadata |
| Powermetrics exits without samples | Read `.raw.stderr`; run `sudo -v` in the launching terminal |
| Powermetrics cannot be stopped | Allow `/bin/kill` for the owned collector PID if needed |
| RAPL unavailable | Check driver/domain availability and read permissions |
| Task fails | Read `.failure.json` and referenced phase logs |
| Run stops early | Root/trial manifests and incomplete summaries retain valid observations |

Old task result versions remain readable. The new complete-trial hierarchy replaces the earlier per-task trial design.
