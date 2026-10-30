# Energy Usage of TypeScript ORMs

Replication package for a study comparing **Prisma, Sequelize, and Drizzle** on a
PetClinic-inspired PostgreSQL workload. It includes the benchmark, original Intel
and Apple Silicon measurements, statistical analysis, and archived tables/figures.

**Status:** initial package assembled from the course-project working tree.
Publication title, complete author list, venue, citation, and project licensing
still need confirmation; no publication or DOI is claimed.

## Getting started

```sh
git clone https://github.com/LuisSchweinberger/Energy-Usage-of-TS-ORMS.git
cd Energy-Usage-of-TS-ORMS
```

The archive contains two completed experiments, each with 12 trials × 14 tasks ×
3 ORMs = **504 task measurements**. Raw data and reference outputs occupy about
536 MB (decimal). Individual files are below GitHub's 100 MiB limit.

## Reproduce the statistical analysis

From the repository root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r src/analysis/requirements.txt
.venv/bin/python src/analysis/statistical_tests.py --machine all
.venv/bin/python src/analysis/box_plots.py --machine all
```

New tables and figures go to `data/results/reproduced/`; archived references in
[`data/results/reference/`](data/results/reference/) are not overwritten.
See [reproduction instructions](documentation/reproduction.md) and the
[analysis guide](src/analysis/README.md).

[Local validation](documentation/validation.md) reproduced all 10 statistical
CSVs within floating-point tolerance and generated all 84 box plots. Type
checking and all 39 dataset/runner tests passed; live database/energy runs were
not performed.

## Rerun the benchmark

Requires Node.js 20+, Python 3.10+, Docker Compose (`up --wait` support), and
supported hardware/permissions for energy measurement. See the
[benchmark setup](src/benchmark/README.md) before running anything: experiments
replace tables in the dedicated benchmark database. Timing-only pilots are
available; full experiments require an energy backend.

## Repository structure

```text
src/benchmark/              Runnable benchmark, configuration, tests, schema
src/analysis/               Statistical tests and figure generation
data/raw/{intel,mac}/       Original experiment-42 archives, unchanged
data/processed/             Reserved for derived analysis inputs (currently none)
data/results/reference/    Archived analysis outputs
data/results/reproduced/   New analysis outputs (ignored by Git)
data/inventory.json        SHA-256 and byte size of every archived data/output file
documentation/             Methods, environment, provenance, interpretation
```

The layout follows the [S2-group replication-package template](https://github.com/S2-group/template-replication-package)
at revision `06cb8739afbe6c809f8512577cfdb837e3057844`.

## Interpretation and release checklist

Intel RAPL and Apple powermetrics/IOReport have different hardware scopes and are
analysed **separately**. Apple unified-memory energy is a model estimate, not a
calibrated power-rail measurement. No idle-baseline subtraction is performed.
See [methodology](documentation/methodology.md) and
[environment and limitations](documentation/environment.md).

Before publishing, confirm the citation, authors, licensing, and review archived
hostnames/local paths in manifests/logs. See [release checklist](documentation/release-checklist.md).
Third-party notices are in [LICENSE](LICENSE).
