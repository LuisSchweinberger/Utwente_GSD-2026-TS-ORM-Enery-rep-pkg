# Conclusions from the statistical analysis

**Sources.** Intel results are in `../data/results/reference/intel/` (data: `../data/raw/intel/experiment-42`, RAPL). Mac results are in `../data/results/reference/mac/` (data: `../data/raw/mac/experiment-42`, powermetrics + Zeus). Each machine has 12 trials × 14 operation types × 3 ORMs, which gives n = 12 per ORM and operation.
All 504 observations per machine are valid. Units are measured in: time in ms, energy in J.

**Tests.** Non-parametric Kruskal–Wallis, followed by Dunn's post-hoc test for differences between ORMs, and the Spearman rank-order correlation coefficient for comparing time with energy. Every test uses alpha = 0.05, and every p-value is Holm-adjusted before deciding significance:
- Assumption checks (Shapiro–Wilk and Brown–Forsythe): across the 42 tests per machine, each check separately.
- Kruskal–Wallis: across the 42 tests per machine.
- Dunn: across the 3 ORM pairs of one test, and only run where the Kruskal–Wallis test is significant.
- Spearman: across the 112 correlations per machine.

The [analysis README](../src/analysis/README.md) describes the methods.

**Why rank-based tests.** A parametric comparison assumes normal residuals and equal variances. After Holm adjustment:
- Shapiro–Wilk rejects normal residuals in 20 of 42 Intel tests (time 5, CPU 10, memory 5) and in 1 of 42 Mac tests (time 1).
- Brown–Forsythe rejects equal variances in none of the tests on either machine.

Because normality fails for much of the Intel data, rank-based tests are used, for both machines, so that both are analysed with the same method.

**How to read this file.**
- **Sections 1–2 (conclusions)** contain only statements backed by a significant, Holm-adjusted test result. "A < B" means that Dunn's test finds A's values significantly lower than B's.
  A difference that is not significant is not treated as a difference.
- **Section 3 (anomalies)** describes things seen in the data that were not part of the planned tests.
- **Section 4 (speculations)** offers possible explanations. None of them was tested.

The machines are analysed separately. Absolute values must not be compared between them, because the energy backends, the hardware and the Node.js versions differ.
"On both machines" means that the same significant result appears in each machine's own tests.

---

## 1. Conclusions: differences between ORMs (Kruskal–Wallis + Dunn)

### 1.1 The ORM affects all three metrics

Number of operations in which the Kruskal–Wallis test finds a significant difference between ORMs (Holm-adjusted):

| | Execution time | CPU energy | Memory energy | Total |
|---|---|---|---|---|
| Intel | 13 / 14 | 14 / 14 | 14 / 14 | 41 / 42 |
| Mac | 12 / 14 | 12 / 14 | 9 / 14 | 33 / 42 |

Where the test is significant, the effect is large: epsilon² is 0.21–0.89 on Intel and 0.34–0.89 on the Mac, with medians of 0.53–0.70 per metric.
Every operation has a significant ORM effect in at least one metric, with one exception: Mac `delete-visit-populated`, where none of the three metrics is significant.

### 1.2 Significant pairs

Number of operations in which Dunn's test (Holm-adjusted) finds a significant difference, with the lower ORM listed first:

| Pair | Intel time | Intel CPU | Intel memory | Mac time | Mac CPU | Mac memory |
|---|---|---|---|---|---|---|
| Drizzle < Prisma | 12 | 13 | 13 | 10 | 9 | 7 |
| Sequelize < Prisma | 10 | 11 | 9 | 8 | 7 | 3 |
| Drizzle < Sequelize | 6 | 6 | 7 | 6 | 5 | 5 |
| Sequelize < Drizzle | 1 | 1 | 1 | 1 | 1 | 0 |
| Prisma < Sequelize | 1 | 0 | 1 | 2 | 2 | 2 |
| Prisma < Drizzle | 0 | 0 | 0 | 0 | 1 | 0 |

How large these significant differences are (the higher ORM's median relative to the lower one's; median over operations, with the range in brackets):

| Pair | Intel time | Intel CPU | Intel memory | Mac time | Mac CPU | Mac memory |
|---|---|---|---|---|---|---|
| Drizzle < Prisma | +8.9% (3.5–28.4) | +10.6% (4.0–28.4) | +12.0% (4.6–30.3) | +13.0% (3.1–59.8) | +15.6% (7.4–96.7) | +21.0% (12.5–45.0) |
| Sequelize < Prisma | +10.1% (2.7–20.8) | +8.4% (3.6–19.1) | +11.4% (4.3–21.3) | +11.2% (5.3–52.3) | +11.1% (4.5–78.5) | +17.4% (11.3–40.4) |
| Drizzle < Sequelize | +8.9% (4.2–19.9) | +9.1% (2.9–16.5) | +9.1% (4.8–19.2) | +16.1% (3.4–24.4) | +17.3% (10.4–25.3) | +18.1% (16.3–23.1) |

**Conclusions:**

1. **Prisma is the most expensive ORM.** Prisma is in 168 pairwise comparisons (2 pairs × 3 metrics × 14 operations × 2 machines).
   It is significantly more expensive in 112 of them and significantly cheaper in only 9:
   - `create-pet-populated` on Intel: time and memory, vs Sequelize.
   - The two owner-visit deletes on the Mac: every metric, vs Sequelize.
   - Mac CPU energy in `read-owner-no-pets`: vs Drizzle.
2. **Drizzle is the cheapest ORM.** Drizzle < Prisma is the most frequent significant result in every metric on both machines. Drizzle is significantly more expensive than Prisma
   in only one comparison (Mac CPU energy, `read-owner-no-pets`).
3. **Drizzle and Sequelize often don't differ significantly.** Drizzle < Sequelize is significant in 5–7 operations per metric. When the pair differs,
   Drizzle is the cheaper one in 35 of 40 significant comparisons over both machines.
4. **The differences are moderate on Intel and larger on the Mac.** The typical significant difference is about 8–12% on Intel and 11–21% on the Mac. The largest
   is +97% (Mac CPU energy, Drizzle vs Prisma, `update-pet-populated`).

### 1.3 Results that hold on both machines

| Operation | Significant on both machines, in every metric |
|---|---|
| `create-owner-populated` | Drizzle < Prisma, Sequelize < Prisma |
| `read-pet-populated` | Drizzle < Prisma, Sequelize < Prisma |
| `create-pet-populated` | Drizzle < Prisma, Drizzle < Sequelize (Drizzle is the cheapest) |
| `read-owner-no-visits`, `read-owner-populated` | Drizzle < Prisma, Drizzle < Sequelize; for time and CPU energy also Sequelize < Prisma (Drizzle < Sequelize < Prisma) |
| `delete-owner-visits-no-visits` | Drizzle < Sequelize |
| `update-owner-no-pets`, `update-pet-populated` | Drizzle < Prisma |

Further results on both machines, for some metrics:

- **`delete-owner-visits-no-pets`:** Sequelize < Prisma for time.
- **`delete-owner-visits-no-visits`:** Drizzle < Prisma for time.
- **`delete-owner-visits-populated`:** Drizzle < Sequelize for CPU and memory energy.
- **`read-owner-no-pets`:** Drizzle < Prisma and Sequelize < Prisma for time.
- **`update-owner-no-pets`:** Sequelize < Prisma for time and CPU energy.
- **`update-owner-no-visits`:** Drizzle < Prisma and Sequelize < Prisma for CPU energy.
- **`update-owner-populated`:** Drizzle < Prisma for time and CPU energy.
- **`update-pet-populated`:** Sequelize < Prisma for CPU and memory energy.

**One conflict between the machines:** for `read-owner-no-pets` CPU energy, Intel finds Drizzle < Prisma, but the Mac finds Prisma < Drizzle. No other
significant pair has opposite directions on the two machines.

### 1.4 Results that are not significant (after Holm adjustment)

| Machine | Metric | Operation (Holm-adjusted p) |
|---|---|---|
| Intel | Execution time | delete-owner-visits-populated (0.079) |
| Mac | Execution time | delete-visit-populated (0.198), update-owner-no-visits (0.058) |
| Mac | CPU energy | delete-owner-visits-no-pets (0.392), delete-visit-populated (0.198) |
| Mac | Memory energy | delete-owner-visits-no-pets (0.058), delete-visit-populated (0.190), read-owner-no-pets (0.177), update-owner-no-visits (0.238), update-owner-populated (0.054) |

For these, the data shows no difference between ORMs. Section 3.2 describes an anomaly that affects several Mac memory results.

---

## 2. Conclusions: execution time vs energy (Spearman, Holm-adjusted)

| Pair | Intel, pooled over ORMs (n = 36) | Intel, within one ORM (n = 12) | Mac, pooled (n = 36) | Mac, within one ORM (n = 12) |
|---|---|---|---|---|
| Time vs CPU energy | 13 / 14 significant (rho 0.53–0.98) | 14 / 42 | 9 / 14 significant (rho 0.66–0.96) | 6 / 42 |
| Time vs memory energy | 14 / 14 significant (rho 0.79–0.99) | 39 / 42 | 11 / 14 significant (rho 0.58–0.82) | 1 / 42 |

(The rho ranges cover the significant correlations.)

1. **Longer runs use more energy.** Every significant correlation is positive on both machines; none is significantly negative.
2. **On Intel, memory energy is almost a monotonic function of execution time,** both pooled and within each ORM (39 / 42).
3. **On Intel, the within-ORM link between time and CPU energy exists only in short operations.** All 14 significant within-ORM time vs CPU correlations are in reads or in deletes that have nothing to delete. None is in a create, update or `delete-*-populated` operation.
4. **On the Mac, the link is weaker.** Pooled over ORMs, time correlates significantly with CPU energy in 9 / 14 operations and with memory energy in 11 / 14.
   The within-ORM correlations are rarely significant after adjustment (6 / 42 and 1 / 42).
   The non-significant pooled time vs CPU correlations are in the four shortest operations (`read-pet-populated`, `delete-visit-populated`,
   `delete-owner-visits-no-pets`, `create-pet-populated`) and in `read-owner-no-pets`.
5. Pooled correlations partly reflect the ORM differences from Section 1, because the slower ORM also uses more energy. The within-ORM values exclude this effect.

---

## 3. Anomalies

### 3.1 Intel: Prisma's trial 5

Prisma's trial-5 block contains 20 of Intel's 31 extreme values (more than 3 × IQR beyond the quartiles): 7 for time, 8 for CPU energy and 5 for memory energy.
In several write operations, that block ran much faster yet used much more CPU energy. For example, `update-owner-no-pets` took 14.9 s against a median of 22.1 s and used 124.2 J against a median of 49.5 J.

These values account for most of the non-normal Intel residuals. Of the 20 Intel tests where Shapiro–Wilk rejects normality, 18 contain an extreme value from Prisma's trial 5, and all 20 contain at least one extreme value.

Effect on the tests: rank-based tests are robust to such values. Rerunning the full pipeline, Holm adjustment included, without Prisma's trial 5 changes, no Kruskal–Wallis verdict, and only two Dunn pairs:
- Intel memory `create-pet-populated`: Prisma < Sequelize becomes non-significant.
- Intel time `update-pet-populated`: Sequelize < Prisma becomes significant.

### 3.2 Mac: host state changed from trial 7 onward

From trial 7 onward, the idle baseline measured before each trial changed abruptly and stayed changed: GPU power rose from about 0.005 W to about 0.158 W and DRAM power from about
0.035 W to about 0.1 W. In every operation, workload memory energy in trials 7–12 is 5.8–12.8% higher than in trials 1–6. Execution time is unchanged (median −0.9%) and
CPU energy slightly lower (median −5%). The trials ran back to back with no gap. The Intel run shows no comparable shift.

Effect on the tests: all three ORMs ran in every trial, so the shift affects them equally, but it adds variance. When CPU and memory energy are rescaled so that both
halves have the same level, and the full pipeline is rerun:
- Three Mac memory-energy Kruskal–Wallis tests become significant: `delete-owner-visits-no-pets`, `read-owner-no-pets` and `update-owner-populated`.
  Because the Holm family is shared, one time test (`update-owner-no-visits`) also becomes significant.
- The significant within-ORM time vs memory correlations rise from 1 / 42 to 7 / 42, and the pooled ones from 11 / 14 to 14 / 14.

The weaker Mac memory results in Sections 1.4 and 2 are therefore at least partly caused by this anomaly. The reported results do not include the adjustment.

---

## 4. Speculations

- **Intel long writes are I/O-bound (Section 3.3).** The CPU may mostly wait on PostgreSQL commits and disk writes, which cost the same for every ORM. ORM overhead would then be a smaller share of the total, and extra wall-clock time would add little CPU energy. This would explain the non-significant time test and the missing within-ORM time vs CPU correlations in these operations.
- **Intel trial 5 (Section 3.1).** Shorter time with much higher power suggests the host was in a different power state during that Prisma block, for example a CPU that did not drop into idle states. That would point to the host, not to Prisma.
- **Mac trial 7 (Section 3.2).** The GPU and memory power step suggests that something on the host started using the GPU, for example a display wake or a GPU-using application.

---

## 5. Limitations

- **Choice of tests.** Kruskal–Wallis and Dunn test whether one ORM's values tend to be larger than another's. These differences reflect the medians only if the distributions have similar shapes. The direction of pairwise differences is inferred from the mean ranks, while medians are reported for size.
Spearman's rank test assesses the correlation strength of a monotonic relationship between two variables, but may not detect non-monotonic associations, even when a strong relationship exists. Moreover, correlation does not imply causation, and the coefficient does not describe the magnitude of change in the original measurement units.
- **Choice of correction.** Holm controls the family-wise error rate, which is conservative. Results near the threshold, mostly Mac memory energy (Section 1.4), could become significant under a less strict correction or with more trials.
- **Scope of the energy values.** Energy is whole-host consumption by hardware domain over the workload window. It includes the client, the API, PostgreSQL, and background activity, and no idle baseline is subtracted. Differences between ORMs are differences in system energy while each ORM runs the workload.
- **What the domains measure.** Both Intel and Mac machines get data from models. Intel CPU energy is the RAPL package domain (core + uncore), and Intel memory energy is RAPL DRAM. Mac CPU energy is a powermetrics estimate, and Mac memory energy is an IOReport energy-model estimate for unified memory. Neither Intel or Mac value is a direct physical measurement.
- **A single session per machine.** The 12 trials of each machine ran in one session, so the tests describe variation within that session only.
- **Provenance.** The Node.js version differs between the machines (v26.10.0 on Intel, v24.9.0 on Mac).
- **Sample size.** n = 12 per group. Small differences of a few percent are at the limit of what this design can detect, especially after Holm adjustment.

## 6. Summary

After Holm adjustment, Kruskal–Wallis finds a significant ORM effect in 41 of 42 (Intel) and 33 of 42 (Mac) operation–metric combinations. Prisma is significantly more expensive than Drizzle in 7–13 of 14 operations per metric. Over both machines, it is significantly more expensive in 112 of its 168 comparisons and cheaper in 9.
Drizzle is the cheapest ORM: it is significantly more expensive than Prisma in only one comparison. Sequelize often doesn't differ significantly from Drizzle, and when it does, it is usually more expensive.

The clearest results that hold on both machines in every metric:
- Prisma > Drizzle and Prisma > Sequelize for `create-owner-populated` and `read-pet-populated`.
- Drizzle as the cheapest ORM for `create-pet-populated`.
- Drizzle < Sequelize < Prisma for the time and CPU energy of reads with relations.

Execution time is significantly and positively correlated with energy on both machines. The correlation is strongest for Intel memory energy and weakest on the Mac. The Mac memory results are the least conclusive, and a host-state change partway through the Mac run (Section 3.2) may explains this.
