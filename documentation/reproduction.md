# Reproduction guide

All commands below start at the repository root unless a `cd` is shown.

## 1. Reanalyse existing measurements (no Docker or energy hardware)

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r src/analysis/requirements.txt
.venv/bin/python src/analysis/statistical_tests.py --machine all
.venv/bin/python src/analysis/box_plots.py --machine all
```

Outputs: `data/results/reproduced/{intel,mac}/`. Reference outputs remain in
`data/results/reference/{intel,mac}/`. Scripts replace only their own reproduced
outputs on reruns. `--machine intel` or `--machine mac` selects one platform;
`--experiment experiment-42` may be used with a single machine.

The analysis requirements retain their original minimum-version constraints.
The original analysis environment was not recorded; exact dependency versions
used for this package's validation are recorded in
`src/analysis/requirements-validation.txt` (Python 3.14.5, macOS arm64). Install
that file instead of `requirements.txt` to request that exact validation set.
PNG
bytes may differ with library/font/platform versions. Compare numerical CSVs
with a tolerance rather than requiring byte-identical figures.

See [validation results](validation.md) for checks actually performed.

## 2. Install and check the benchmark

```sh
cd src/benchmark
cp .env.example .env
npm ci
npm run prisma:generate
npm run typecheck
npm run test:dataset
npm run test:runner
```

Node.js 20+ and Python 3.10+ are minimum requirements, not claims about the
versions originally used. See `environment.md` for the recorded environments.

## 3. Run new measurements

**Warning:** only use the dedicated Compose benchmark database. Complete trials
start/stop PostgreSQL and replace its benchmark tables. Database integration
tests modify it too; never run them alongside experiments.

From `src/benchmark/`, a small timing-only pilot is:

```sh
SIZE=10 QUERY_COUNT=5 MEASUREMENT_BACKEND=none npm run --silent pilot -- --seed 43 --trials 1
```

For Intel Linux, verify readable RAPL powercap counters, then:

```sh
MEASUREMENT_BACKEND=rapl npm run --silent experiment -- --seed 42 --trials 12
```

For Apple Silicon macOS:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-mac.txt
sudo -v
MEASUREMENT_BACKEND=powermetrics_zeus .venv/bin/python scripts/benchmark.py experiment --seed 42 --trials 12
```

Authenticate sudo in the launching terminal; both Apple collectors are mandatory.
The full experiment requires `POWER_SAMPLE_INTERVAL_MS=100` (the default).
Check a pilot and collector quality before committing to the full experiment.

New runs stay in `src/benchmark/results/`, never in the archived `data/raw/`.
**Reusing a run ID/seed replaces that generated run folder.** Select a new seed
or `--run-id` when retaining previous runs. The analysis currently targets the
archived experiments; reviewing/importing a new run is a separate explicit step.

## 4. Database integration checks (optional)

From `src/benchmark/`, after installation:

```sh
npm run db:up
SIZE=10 QUERY_COUNT=5 DATASET_SEED=42 npm test
npm run db:down
```

## Scope of changes during packaging

Benchmark implementation and measurement logic were copied without changes.
Analysis tests were updated for the relocated module/data paths, and a stale
`output_name` assertion now checks the selected `experiment_path.name` instead.
Analysis paths now read `data/raw/` and write `data/results/reproduced/`.
Documentation links were updated and a reference to a missing Apple smoke-test
script was removed. `source-provenance.json` records hashes of imported source
files **before** these packaging edits, for traceability; it is not a checksum
manifest of the final package source.
