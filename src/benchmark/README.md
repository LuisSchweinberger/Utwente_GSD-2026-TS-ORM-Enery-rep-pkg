# PetClinic ORM benchmark

Compare Prisma, Sequelize, and Drizzle using sequential HTTP requests. Python controls the experiment and measures time/energy; TypeScript implements the API, workload and database checks.

**Task** = scenario + profile. **Trial** = all 14 tasks for all three ORMs. **Experiment** = repeated complete trials.

## 1. Setup

Requires Node.js 20+, Python 3.10+, and a running Docker engine with Docker Compose
(`up --wait` support). Run the following commands from `src/benchmark/`.

```sh
cp .env.example .env
npm ci
npm run prisma:generate
```

Set workload/measurement settings in `.env`. Complete trials start/stop PostgreSQL and generate their own data; no manual database initialization or API startup is needed. They use the **dedicated Compose benchmark database** and replace its benchmark tables.

## 2. Run

| Command | Scope | Default complete trials |
| --- | --- | ---: |
| `task` | One ORM + one task; existing database/snapshot | — |
| `trial` | All tasks for all ORMs | 1 |
| `pilot` | Short experiment using the same lifecycle | 3 |
| `experiment` | Full experiment | 10 |

```sh
npm run --silent trial -- --seed 42
npm run --silent pilot -- --seed 42
npm run --silent experiment -- --seed 42 --trials 12
```

There are **42 task measurements per trial**. Multiples of three trials balance ORM positions exactly; other counts are supported.

**Choose energy measurement before launch:**

- **Apple Silicon macOS:** `MEASUREMENT_BACKEND=powermetrics_zeus`; both powermetrics (CPU/GPU/ANE) and Zeus/IOReport (unified memory) are mandatory. Set up the runner's Python and authenticate sudo:

  ```sh
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements-mac.txt
  sudo -v
  MEASUREMENT_BACKEND=powermetrics_zeus .venv/bin/python scripts/benchmark.py pilot --seed 43
  ```

  Alternatively, activate that environment before using npm commands and set
  `MEASUREMENT_BACKEND=powermetrics_zeus` in `.env`. Zeus needs no sudo;
  powermetrics does.
- **Intel Linux:** `MEASUREMENT_BACKEND=rapl`; RAPL powercap counters must be readable.
- **Timing only:** `MEASUREMENT_BACKEND=none`, supported for tasks, trials and pilots.

The full experiment requires an energy backend at 10 Hz. Progress shows trial, ORM, task and request counts. Failures preserve partial reports and stop the run. Reusing a complete-trial/pilot/experiment ID or seed warns and **replaces the entire run folder**, so old trial directories cannot remain.

For a small timing-only pilot:

```sh
SIZE=10 QUERY_COUNT=5 MEASUREMENT_BACKEND=none npm run --silent pilot -- --seed 43 --trials 1
```

## 3. Flow and configuration

```text
Trial cooldown → start PostgreSQL → generate seeded data/snapshot → measure idle
For each ORM: cooldown → start API → execute all tasks → save reports → stop API
Stop PostgreSQL
```

Every task restores the trial snapshot before request preparation and measurement. The API stays alive across its ORM block. Tasks are shuffled once per trial, identically for every ORM; ORM order rotates. Dataset seeds are `SEED`, `SEED + 1`, and so on.

| Variable | Default | Meaning |
| --- | --- | --- |
| `SIZE` | `1000` | Owners per data profile |
| `QUERY_COUNT` | `SIZE` | Requests per task, at most `SIZE` |
| `SEED` | `42` | Initial dataset/schedule seed |
| `TRIALS` | mode default | Complete trials; CLI `--trials` overrides |
| `TRIAL_COOLDOWN_SECONDS` | `30` | Wait before PostgreSQL startup |
| `ORM_COOLDOWN_SECONDS` | `10` | Wait before each API startup |
| `IDLE_SECONDS` | `30` | One measured idle baseline per trial |
| `MEASUREMENT_BACKEND` | `none` | `none`, `powermetrics_zeus`, or `rapl` |
| `POWER_SAMPLE_INTERVAL_MS` | `100` | Full experiment requires 100ms |
| `WORKLOAD_TIMEOUT_SECONDS` | `3600` | Request-batch timeout |
| `PORT` / `POSTGRES_PORT` | `3100` / `55432` | API / database ports |

Environment overrides `.env`; CLI overrides both:

```sh
npm run --silent pilot -- --trials 3 --trial-cooldown-seconds 5 --orm-cooldown-seconds 2 --idle-seconds 10
```

## 4. Results

```text
results/experiment-42/
├── manifest.json / schedule.tsv
├── summary.json / summary.csv   # Means, medians, valid counts per ORM + task
└── trials/trial-001/
    ├── manifest.json           # Seed, ordering and progress
    ├── snapshot/               # Trial-local SQL and metadata
    ├── baseline/               # Shared idle measurement and raw energy
    ├── prisma/                 # Task results, raw energy and ORM report
    ├── sequelize/
    ├── drizzle/
    └── logs/
```

Timing covers requests through the final complete response body, plus small pipe/progress overhead. Setup, restore, cooldown, baseline and verification are excluded. Baseline energy stays separate; summaries use verified workload measurements and available hardware domains.

New measurements stay in `src/benchmark/results/`; the archived data in
`data/raw/` is not overwritten. The analysis scripts read the archived data,
not new benchmark runs, by default.

## 5. Checks

```sh
npm run typecheck
npm run test:dataset
npm run test:runner
npm run db:up
SIZE=10 QUERY_COUNT=5 DATASET_SEED=42 npm test
npm run db:down
```

Database tests modify the database; run them separately from experiments.
