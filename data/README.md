# Research artifacts

- `raw/intel/experiment-42/`: completed Intel RAPL experiment.
- `raw/mac/experiment-42/`: completed Apple powermetrics + Zeus experiment.
- `results/reference/{intel,mac}/`: copied statistical CSVs, reports and plots.
- `results/reproduced/`: newly generated outputs, ignored by Git.
- `processed/`: reserved; analysis currently reads per-task JSON directly.
- `inventory.json`: file sizes and SHA-256 checksums for raw and reference files.

Original manifests, SQL snapshots, raw traces, baseline measurements, schedules,
verification reports and per-experiment logs are retained without rewriting.
Exploratory `results/`, top-level runtime logs, `.env`, caches and dependencies
were not imported. Each selected experiment was marked completed with 12 trials
and 504 task measurements in its manifest.

Never regenerate the inventory merely to hide an unexplained data change.
