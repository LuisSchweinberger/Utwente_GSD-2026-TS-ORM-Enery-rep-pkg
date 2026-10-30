"""Descriptive statistics, Kruskal-Wallis, Dunn post-hoc and Spearman correlation per operation.

Usage:  python statistical_tests.py --machine intel|mac|all

For every operation type (scenario + data profile) and every available metric:
  * descriptive statistics per ORM (n, mean, SD, median, Q1, Q3, min, max)
  * parametric assumption checks: Shapiro-Wilk on the residuals (value minus ORM mean)
    and Brown-Forsythe (Levene, median-centred) across the three ORMs
  * Kruskal-Wallis H test with three groups (drizzle, prisma, sequelize)
  * Dunn's post-hoc test on all ORM pairs (scikit-posthocs), only when the
    Holm-adjusted Kruskal-Wallis p-value is below alpha
  * Spearman rank-order correlation of execution time vs CPU energy and
    execution time vs memory energy (pooled over ORMs, and within each ORM)

Multiple testing, alpha = 0.05, Holm adjustment:
  * Shapiro-Wilk and Brown-Forsythe: one family each per machine (all operations x metrics), statsmodels multipletests
  * Kruskal-Wallis: one family per machine (all operations x metrics), statsmodels multipletests
  * Dunn: one family per Kruskal-Wallis test (the three ORM pairs), scikit-posthocs p_adjust
  * Spearman: one family per machine (all operations x pairs x scopes), statsmodels multipletests

Outputs go to data/results/reproduced/<machine>/ (CSV files + report.md).
All values keep their original units (ms, J); nothing is converted.
"""

from __future__ import annotations

import argparse
import csv
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
import scikit_posthocs as sp
from scipy import stats
from statsmodels.stats.multitest import multipletests

import common
from common import CPU, MEMORY, METRIC_LABELS, METRIC_UNITS, ORMS, TIME

ALPHA = 0.05
P_ADJUST = "holm"


def describe(values: list[float]) -> dict[str, float]:
    a = np.asarray(values, dtype=float)
    q1, median, q3 = np.percentile(a, [25, 50, 75])  # numpy default: linear interpolation
    return {
        "n": a.size,
        "mean": a.mean(),
        "sd": a.std(ddof=1) if a.size > 1 else float("nan"),  # sample standard deviation
        "median": median,
        "q1": q1,
        "q3": q3,
        "min": a.min(),
        "max": a.max(),
    }


def holm(p_values: list[float]) -> list[float]:
    return list(multipletests(p_values, alpha=ALPHA, method=P_ADJUST)[1])


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def fmt(value, digits: int = 4) -> str:
    if isinstance(value, str):
        return value
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "n/a"
    if isinstance(value, (int, np.integer)):
        return str(value)
    if value != 0 and abs(value) < 1e-3:
        return f"{value:.3e}"
    return f"{value:.{digits}f}"


def md_table(headers: list[str], rows: list[list]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines += ["| " + " | ".join(fmt(c) for c in row) + " |" for row in rows]
    return "\n".join(lines)


def dunn(groups: dict[str, list[float]]) -> list[dict]:
    """Dunn's test (scikit-posthocs), raw and Holm-adjusted over the three pairs.

    Mean ranks over the pooled observations of the operation give the direction of each difference.
    """
    frame = pd.DataFrame([(orm, v) for orm, values in groups.items() for v in values], columns=["orm", "value"])
    p_raw = sp.posthoc_dunn(frame, val_col="value", group_col="orm")
    p_holm = sp.posthoc_dunn(frame, val_col="value", group_col="orm", p_adjust=P_ADJUST)
    mean_rank = frame.assign(rank=stats.rankdata(frame["value"])).groupby("orm")["rank"].mean()
    return [{
        "orm_a": a, "orm_b": b,
        "mean_rank_a": mean_rank[a], "mean_rank_b": mean_rank[b],
        "median_a": float(np.median(groups[a])), "median_b": float(np.median(groups[b])),
        "p_value": float(p_raw.loc[a, b]), "p_holm": float(p_holm.loc[a, b]),
        "significant": bool(p_holm.loc[a, b] < ALPHA),
    } for a, b in itertools.combinations(ORMS, 2)]


def analyse(machine: common.Machine) -> None:
    observations, excluded = common.load(machine)
    ops = common.operations(observations)
    metrics = common.available_metrics(machine)
    out = common.output_dir(machine)

    descriptive_rows, assumption_rows, kw_rows, dunn_rows, spearman_rows = [], [], [], [], []
    groups_by_test = {}

    for op in ops:
        for metric in metrics:
            unit = METRIC_UNITS[metric]
            groups = {orm: common.series(observations, op, orm, metric) for orm in ORMS}
            groups_by_test[(op, metric)] = groups
            for orm, values in groups.items():
                descriptive_rows.append({"operation": op, "metric": metric, "unit": unit, "orm": orm, **describe(values)})

            # Assumptions of a parametric one-way comparison: normal residuals, equal variances.
            residuals = np.concatenate([np.asarray(v) - np.mean(v) for v in groups.values()])
            assumption_rows.append({
                "operation": op, "metric": metric,
                "shapiro_W": stats.shapiro(residuals).statistic, "shapiro_p": stats.shapiro(residuals).pvalue,
                "brown_forsythe_W": stats.levene(*groups.values(), center="median").statistic,
                "brown_forsythe_p": stats.levene(*groups.values(), center="median").pvalue,
            })

            kw = stats.kruskal(*groups.values())
            n_total = sum(len(v) for v in groups.values())
            kw_rows.append({
                "operation": op, "metric": metric, "unit": unit,
                "df": len(groups) - 1, "H": kw.statistic,
                "epsilon_squared": kw.statistic / (n_total - 1),  # rank-based effect size, 0..1
                "p_value": kw.pvalue,
            })

        # Spearman: execution time vs each available energy metric.
        for energy in (m for m in (CPU, MEMORY) if m in metrics):
            for scope in ("all ORMs", *ORMS):
                x, y = common.paired(observations, op, TIME, energy, None if scope == "all ORMs" else scope)
                rho = stats.spearmanr(x, y)
                spearman_rows.append({
                    "operation": op, "pair": f"{TIME} vs {energy}", "scope": scope, "n": len(x),
                    "rho": rho.statistic, "p_value": rho.pvalue,
                })

    # Holm across each assumption-check family of this machine.
    for test in ("shapiro", "brown_forsythe"):
        for row, p_adj in zip(assumption_rows, holm([r[f"{test}_p"] for r in assumption_rows])):
            row.update({f"{test}_p_holm": p_adj, f"{test}_rejected": bool(p_adj < ALPHA)})

    # Holm across all Kruskal-Wallis tests of this machine; Dunn only where the adjusted p is significant.
    for row, p_adj in zip(kw_rows, holm([r["p_value"] for r in kw_rows])):
        row.update({"p_holm": p_adj, "alpha": ALPHA, "significant": bool(p_adj < ALPHA)})
        if row["significant"]:
            for d in dunn(groups_by_test[(row["operation"], row["metric"])]):
                dunn_rows.append({"operation": row["operation"], "metric": row["metric"], "unit": row["unit"], **d})

    # Holm across all Spearman tests of this machine.
    for row, p_adj in zip(spearman_rows, holm([r["p_value"] for r in spearman_rows])):
        row.update({"p_holm": p_adj, "significant": bool(p_adj < ALPHA)})

    write_csv(out / "descriptive_statistics.csv", descriptive_rows)
    write_csv(out / "assumptions.csv", assumption_rows)
    write_csv(out / "kruskal_wallis.csv", kw_rows)
    if dunn_rows:
        write_csv(out / "dunn.csv", dunn_rows)
    else:
        (out / "dunn.csv").write_text("no Kruskal-Wallis test was significant; Dunn's test not run\n", encoding="utf-8")
    write_csv(out / "spearman.csv", spearman_rows)

    write_report(machine, out, observations, excluded, ops, metrics,
                 descriptive_rows, assumption_rows, kw_rows, dunn_rows, spearman_rows)
    print(f"[{machine.key}] {len(observations)} valid observations, {len(excluded)} excluded -> {out}")


def write_report(machine, out, observations, excluded, ops, metrics,
                 descriptive_rows, assumption_rows, kw_rows, dunn_rows, spearman_rows) -> None:
    trials = sorted({o.trial for o in observations})
    lines = [
        f"# Statistical analysis: {machine.title}",
        "",
        f"Source: `{machine.results_dir}/` (read-only). {len(trials)} trials, {len(ops)} operation types, "
        f"{len(observations)} valid ORM x operation x trial observations; {len(excluded)} excluded.",
        "",
        f"Significance level alpha = {ALPHA}. All p-values are Holm-adjusted and significance is decided on the "
        f"adjusted value: each assumption check and Kruskal-Wallis across the {len(kw_rows)} tests of this machine, "
        f"Dunn across the three ORM pairs of one test, Spearman across the {len(spearman_rows)} correlations of this machine.",
        "",
        "## Metrics and units (original units, no conversion)",
        "",
        md_table(["Metric", "Unit", "Source"], [
            [METRIC_LABELS[TIME], "ms", "`timing.workloadElapsedMs` (controller monotonic clock, GO to DONE)"],
            [METRIC_LABELS[CPU], "J", machine.domain_notes[CPU] + " Field `energyJ`."],
            [METRIC_LABELS[MEMORY], "J" if MEMORY in metrics else "-", machine.domain_notes[MEMORY]
             + (" Field `energyJ`." if MEMORY in metrics else "")],
        ]),
        "",
    ]
    if excluded:
        lines += ["## Excluded observations", ""] + [f"- {e}" for e in excluded] + [""]

    lines += ["## Parametric assumption checks", "",
              "Shapiro-Wilk on the residuals (normality) and Brown-Forsythe across the ORMs (equal variances); "
              "Holm-adjusted p-values, `*` marks a rejected assumption (adjusted p < 0.05).", ""]
    rows = []
    for m in metrics:
        a = [r for r in assumption_rows if r["metric"] == m]
        rows.append([METRIC_LABELS[m], f"{sum(r['shapiro_rejected'] for r in a)} / {len(a)}",
                     f"{sum(r['brown_forsythe_rejected'] for r in a)} / {len(a)}"])
    lines += [md_table(["Metric", "Normality rejected", "Equal variances rejected"], rows), ""]
    lines += [md_table(["Operation"] + [f"{METRIC_LABELS[m]} Shapiro p_holm / B-F p_holm" for m in metrics],
                       [[op] + [(lambda r: f"{fmt(r['shapiro_p_holm'])}{' *' if r['shapiro_rejected'] else ''} / "
                                           f"{fmt(r['brown_forsythe_p_holm'])}{' *' if r['brown_forsythe_rejected'] else ''}")(
                                next(r for r in assumption_rows if r["operation"] == op and r["metric"] == m))
                                for m in metrics] for op in ops]), ""]

    lines += ["## Kruskal-Wallis overview", "",
              "H statistic and Holm-adjusted p-value per operation; `*` marks adjusted p < 0.05.", ""]
    headers = ["Operation"] + [f"{METRIC_LABELS[m]} H (p_holm)" for m in metrics]
    rows = []
    for op in ops:
        row = [op]
        for m in metrics:
            k = next(r for r in kw_rows if r["operation"] == op and r["metric"] == m)
            row.append(f"{fmt(k['H'], 2)} ({fmt(k['p_holm'])}){' *' if k['significant'] else ''}")
        rows.append(row)
    lines += [md_table(headers, rows), ""]

    for op in ops:
        lines += [f"## {op}", ""]
        for m in metrics:
            unit = METRIC_UNITS[m]
            lines += [f"### {METRIC_LABELS[m]} ({unit})", ""]
            desc = [r for r in descriptive_rows if r["operation"] == op and r["metric"] == m]
            lines += [md_table(["ORM", "n", "Mean", "SD", "Median", "Q1", "Q3", "Min", "Max"],
                               [[r["orm"], r["n"], r["mean"], r["sd"], r["median"], r["q1"], r["q3"], r["min"], r["max"]]
                                for r in desc]), ""]
            k = next(r for r in kw_rows if r["operation"] == op and r["metric"] == m)
            verdict = "significant difference between ORMs" if k["significant"] else "no significant difference"
            lines += [f"Kruskal-Wallis: H({k['df']}) = {fmt(k['H'], 3)}, epsilon² = {fmt(k['epsilon_squared'], 3)}, "
                      f"p = {fmt(k['p_value'])}, Holm-adjusted p = {fmt(k['p_holm'])} -> {verdict}.", ""]
            dn = [r for r in dunn_rows if r["operation"] == op and r["metric"] == m]
            if dn:
                lines += ["Dunn's test (Holm-adjusted over the three pairs):", "",
                          md_table(["Pair (A - B)", "Mean rank A", "Mean rank B", f"Median A ({unit})",
                                    f"Median B ({unit})", "p", "p_holm", "Significant"],
                                   [[f"{r['orm_a']} - {r['orm_b']}", r["mean_rank_a"], r["mean_rank_b"], r["median_a"],
                                     r["median_b"], r["p_value"], r["p_holm"], "yes" if r["significant"] else "no"]
                                    for r in dn]),
                          ""]
            else:
                lines += ["Dunn's test not run (Kruskal-Wallis not significant after adjustment).", ""]

        sp_rows = [r for r in spearman_rows if r["operation"] == op]
        lines += ["### Spearman rank-order correlation", "",
                  md_table(["Pair", "Scope", "n", "rho", "p", "p_holm", "Significant"],
                           [[r["pair"], r["scope"], r["n"], r["rho"], r["p_value"], r["p_holm"],
                             "yes" if r["significant"] else "no"] for r in sp_rows]), ""]
        if MEMORY not in metrics:
            lines += ["Execution time vs memory energy: not computed, memory energy is not measured on this machine.", ""]

    (out / "report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--machine", choices=[*common.MACHINES, "all"], default="all")
    parser.add_argument("--experiment", help="Select one experiment directory name; requires --machine intel or mac")
    args = parser.parse_args()
    if args.experiment and args.machine == "all":
        parser.error("--experiment requires a single --machine")
    for key in common.MACHINES if args.machine == "all" else [args.machine]:
        analyse(common.select_machine(key, args.experiment))


if __name__ == "__main__":
    main()
