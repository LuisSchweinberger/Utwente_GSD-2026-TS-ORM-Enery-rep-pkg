# Energy Usage and Performance of Typescript ORM Libraries

This repository contains the replication package for our project "Energy Usage
and Performance of Typescript ORM Libraries" as part of the Green Software
Development Course Q1 2026.

The project compares Prisma, Sequelize, and Drizzle using a PetClinic-inspired
PostgreSQL workload. This package contains the benchmark, measurements from Intel
and Apple Silicon machines, and scripts for statistical analysis and plots.

## Getting started

```sh
git clone https://github.com/LuisSchweinberger/Energy-Usage-of-TS-ORMS.git
cd Energy-Usage-of-TS-ORMS
```

### Run the analysis

Requires Python 3.10+. No database or energy-measurement hardware is needed.
From the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r src/analysis/requirements.txt
.venv/bin/python src/analysis/statistical_tests.py --machine all
.venv/bin/python src/analysis/box_plots.py --machine all
```

Outputs go to `data/results/reproduced/`, without changing the original data or
reference outputs. See [analysis instructions](src/analysis/README.md).

### Run the benchmark

Requires Node.js 20+, Python 3.10+, Docker Compose, and supported hardware for
energy measurements. Follow the [benchmark instructions](src/benchmark/README.md)
for installation, configuration, execution, and tests.

## Repository structure

```text
src/benchmark/             Benchmark code, configuration, database schema, tests
src/analysis/              Statistical analysis and plot scripts
data/raw/{intel,mac}/      Original measurements
data/results/reference/   Saved analysis outputs
data/results/reproduced/  Newly generated outputs (ignored by Git)
data/processed/            Reserved; analysis currently reads raw JSON directly
data/inventory.json        File sizes and SHA-256 checksums of archived artifacts
documentation/            Recorded experiment environment
```

Each machine's archive contains 12 trials × 14 tasks × 3 ORMs = 504 task
measurements. Hardware, versions, and run settings are listed in
[the environment documentation](documentation/environment.md).

## License

Project-authored material is licensed under the [MIT License](LICENSE).
The adapted PetClinic schema retains its Apache-2.0 license; see
[third-party notices](THIRD_PARTY_NOTICES.md).
