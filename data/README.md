# Data

- `raw/intel/experiment-42/`: Intel RAPL measurements.
- `raw/mac/experiment-42/`: Apple powermetrics + Zeus measurements.
- `results/reference/{intel,mac}/`: saved statistical CSVs, reports, and plots.
- `results/reproduced/`: new analysis outputs, ignored by Git.
- `processed/`: reserved; analysis currently reads raw JSON directly.
- `inventory.json`: file sizes and SHA-256 checksums for raw and reference files.

Each experiment contains 12 trials and 504 task measurements, including manifests,
schedules, database snapshots, raw energy traces, correctness reports, and logs.

Run the scripts described in the [analysis instructions](../src/analysis/README.md)
to generate new outputs without modifying the archived files.
