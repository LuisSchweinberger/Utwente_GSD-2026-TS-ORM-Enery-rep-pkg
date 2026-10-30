# Statistical analysis

Statistical tests and box plots for the ORM benchmark results in `../../data/raw/intel/` and
`../../data/raw/mac/`. Those directories are only read; generated files go to
`../../data/results/reproduced/`, separate from archived `reference/` outputs.
The two machines are analysed separately, because Intel RAPL and Apple powermetrics
values can't be compared directly (see `../../documentation/methodology.md`).

## Running

```bash
pip install -r requirements.txt
python statistical_tests.py --machine all
python box_plots.py --machine all
```

Run the commands above from `src/analysis/` using a virtual environment. From the
package root, use the commands in [the reproduction guide](../../documentation/reproduction.md).

`--machine` accepts `intel`, `mac` or `all` (the default). Results are always written to `../../data/results/reproduced/intel/` and `mac/`,
overwriting the previous outputs.

Each `data/raw/<machine>/` directory must contain exactly one `experiment-*` folder. If it contains several,
choose one with `--experiment` (this requires a single `--machine`):

```bash
python statistical_tests.py --machine mac --experiment experiment-42
python box_plots.py --machine mac --experiment experiment-42
```

The memory domain is chosen from the experiment's backend: `powermetrics_zeus` Mac runs use
`ioreport:dram`. An experiment whose measurements are labelled with more than one backend is rejected.

| File | Purpose |
|---|---|
| `common.py` | Loads the per-trial measurement files and maps each machine's energy domains to the metrics |
| `statistical_tests.py` | Descriptive statistics, assumption checks, Kruskal–Wallis, Dunn's post-hoc test and Spearman correlation, with Holm-adjusted p-values |
| `box_plots.py` | Box plots for each operation type and metric |

## Outputs (per machine under `data/results/reproduced/`: `intel/`, `mac/`)

| File | Content |
|---|---|
| `descriptive_statistics.csv` | For each operation, metric and ORM: n, mean, SD, median, Q1, Q3, min, max |
| `assumptions.csv` | Parametric assumption checks for each operation and metric: Shapiro–Wilk on the residuals and Brown–Forsythe across the ORMs, each with raw p, Holm-adjusted p and whether the assumption is rejected |
| `kruskal_wallis.csv` | Kruskal–Wallis test (3 groups = ORMs) for each operation and metric: df, H, epsilon², raw p, Holm-adjusted p, significant |
| `dunn.csv` | Dunn's test for each ORM pair, run only where the adjusted Kruskal–Wallis p is < 0.05: mean ranks, medians, raw p, Holm-adjusted p, significant |
| `spearman.csv` | Spearman rho, raw p and Holm-adjusted p for execution time vs CPU energy and execution time vs memory energy, for each operation |
| `report.md` | All of the above as readable tables, one section per operation |
| `boxplots/<metric>/<operation>.png` | ORMs on the x-axis and the metric on the y-axis, with every trial overlaid as a dot |

## Data and definitions

- **Source files:** `trials/trial-*/<orm>/<task>.measurement.json` (time and energy) and `<task>.json`
  (correctness verification). Each machine has 12 trials × 14 operations × 3 ORMs, which gives 504 observations.
- **Operation type** = `scenario-profile`, e.g. `read-owner-no-pets`. There are 14 of them.
- **Valid observation:** the measurement `status` and the task verification `status` are both `"valid"`,
  and the metric is a finite number. All 504 observations are valid on both machines, so n = 12 for every ORM.
- The descriptive statistics and the counts were checked against the benchmark's own `summary.csv`
  (count, mean and median). All rows matched.

### Metrics and units

All values keep the **original units stored in the result files**. These scripts don't convert any units.

| Metric | Unit | Intel (RAPL, Linux) | Mac (powermetrics + Zeus, Apple Silicon) |
|---|---|---|---|
| Execution time | ms | `timing.workloadElapsedMs` | `timing.workloadElapsedMs` |
| CPU energy consumption | J | domain `intel-rapl:0` (package-0), `energyJ` | domain `cpu` (`powermetrics:cpu`), `energyJ` |
| Memory energy consumption | J | domain `intel-rapl:0:2` (dram), `energyJ` | domain `ioreport:dram` (unified memory, via zeus-apple-silicon), `energyJ` |

### Unit conversions

**These scripts:** none. Every value is analysed and plotted in the unit it is stored in.

**Upstream, done by the benchmark controller (`../benchmark/scripts/`) before the values were written to
`*.measurement.json`.** These are listed here for transparency.

| Quantity | Raw unit | Stored unit | Conversion |
|---|---|---|---|
| Execution time | ns (monotonic clock stamps) | ms | ÷ 10^6. `common.py` re-derives this from `workloadFinishedMonotonicNs - workloadStartedMonotonicNs` for every observation and stops if a value doesn't match. |
| Intel RAPL energy | µJ (`energy_uj` counters in `*.energy.raw`) | J | ÷ 10^6, as a wrap-aware counter delta |
| Mac powermetrics energy | mJ for each sample interval (plist in `*.energy.raw`) | J | ÷ 10^3, with partial intervals allocated by overlap (an estimate) |
| Mac IOReport memory energy | mJ (cumulative `dram_mj` counter, `*.energy.raw.memory.json`) | J | ÷ 10^3 of the end − start counter delta. Checked against `snapshotBrackets` for all 504 observations: exact match. |

### Domain choices and caveats

- **Intel CPU energy** uses the RAPL *package* domain (`intel-rapl:0`). This covers the core and uncore
  sub-domains, which are not added on top. The `intel-rapl-mmio:*` zones report the same counters as
  `intel-rapl:0` / `intel-rapl:0:2` and are ignored to avoid double counting.
- **Mac memory energy** is a host-wide IOReport energy-model estimate for unified memory, not a direct physical
  measurement. It is read as a counter at the start and end of each workload, and the boundaries are estimated at the midpoints of the counter reads.
- Energy is whole-host, domain-level consumption over the workload window. It includes the client,
  the API, PostgreSQL, and background activity. No baseline is subtracted.

## Statistical methods

- **Significance level:** alpha = 0.05. Significance is always decided on the **Holm-adjusted** p-value.
- **Descriptive statistics:** the SD is the sample standard deviation (`ddof=1`). The quartiles use
  `numpy.percentile` with its default linear interpolation.
- **Assumption checks and choice of tests:** a parametric one-way comparison assumes normally distributed residuals and equal variances.
  For every operation and metric, the residuals (each value minus its ORM's mean) are tested with `scipy.stats.shapiro` (Shapiro–Wilk), and the
  variances with `scipy.stats.levene(center="median")` (Brown–Forsythe). After Holm adjustment:

  | | Normality rejected | Equal variances rejected |
  |---|---|---|
  | Intel | 20 / 42 (time 5, CPU 10, memory 5) | 0 / 42 |
  | Mac | 1 / 42 (time 1) | 0 / 42 |

  Normality does not hold for much of the Intel data, where a few extreme values produce strongly skewed residuals. Rank-based tests, which do not assume
  normality and are robust to such values, are therefore used. They are used for both machines so that both are analysed with the same method.
- **Kruskal–Wallis H test:** `scipy.stats.kruskal` with three groups (drizzle, prisma, sequelize), each with 12 observations
  (df = 2, tie-corrected). The effect size is epsilon² = H / (n − 1), from 0 (no separation) to 1 (complete separation).
  The test checks whether one ORM's values tend to be larger than another's. It is a strict test of medians only if the
  groups' distributions have the same shape.
- **Dunn's post-hoc test:** `scikit_posthocs.posthoc_dunn` (tie-corrected), run only when the adjusted Kruskal–Wallis
  p-value is < 0.05. It compares all 3 ORM pairs using the same ranks as the Kruskal–Wallis test. The direction of a difference
  comes from the mean ranks; medians are reported alongside.
- **Spearman rank-order correlation:** `scipy.stats.spearmanr` between execution time and each energy
  metric, for each operation. It is computed in two ways:
  - `scope = all ORMs`: all 36 observations pooled. Part of this correlation can come from ORM differences.
  - `scope = <orm>`: within one ORM, 12 observations.
- **Multiple testing (Holm, which controls the family-wise error rate):**

  | Family | Size per machine | Adjusted with |
  |---|---|---|
  | Shapiro–Wilk tests | 42 | `statsmodels.stats.multitest.multipletests(method="holm")` |
  | Brown–Forsythe tests | 42 | `multipletests(method="holm")` |
  | Kruskal–Wallis tests | 42 (14 operations × 3 metrics) | `multipletests(method="holm")` |
  | Dunn pairs of one Kruskal–Wallis test | 3 | `posthoc_dunn(p_adjust="holm")` |
  | Spearman correlations | 112 (14 operations × 2 energy metrics × 4 scopes) | `multipletests(method="holm")` |

  A Dunn result is only reported when its Kruskal–Wallis test was significant after the across-operation adjustment.
  The CSV files also keep the raw p-values for transparency, but every significance decision uses the adjusted value.
