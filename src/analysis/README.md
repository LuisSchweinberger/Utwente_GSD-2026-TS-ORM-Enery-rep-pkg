# Analysis

## Run

From the repository root, with Python 3.10+:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r src/analysis/requirements.txt
.venv/bin/python src/analysis/statistical_tests.py --machine all
.venv/bin/python src/analysis/box_plots.py --machine all
```

`--machine` accepts `intel`, `mac`, or `all` (default). If a machine's input
directory contains multiple experiments, select one explicitly:

```sh
.venv/bin/python src/analysis/statistical_tests.py --machine mac --experiment experiment-42
.venv/bin/python src/analysis/box_plots.py --machine mac --experiment experiment-42
```

`requirements.txt` lists minimum dependency versions. The optional
`requirements-validation.txt` pins the versions tested on Python 3.14.5,
macOS arm64; install that file instead to use that environment's versions.

## Inputs and outputs

- Input: `data/raw/{intel,mac}/experiment-*/`.
- Saved outputs: `data/results/reference/{intel,mac}/`.
- New outputs: `data/results/reproduced/{intel,mac}/`.

The scripts read per-task `*.measurement.json` files and matching correctness
reports. Only valid observations with finite metric values are included.
Intel and Mac experiments are processed separately. Time is stored in
milliseconds and energy in joules.

| Script | Output |
|---|---|
| `statistical_tests.py` | Descriptive statistics, assumption checks, Kruskal–Wallis, Dunn and Spearman CSVs, plus `report.md` |
| `box_plots.py` | PNG figures in `boxplots/<metric>/<operation>.png` |
| `common.py` | Shared data loading and platform-specific energy-domain selection |

Rerunning the scripts overwrites generated outputs in `reproduced/`, not the
raw data or saved reference outputs.
