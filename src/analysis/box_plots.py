"""Box plots per operation type: the three ORMs on the x-axis, one metric on the y-axis.

Usage:  python box_plots.py --machine intel|mac|all

Writes data/results/reproduced/<machine>/boxplots/<metric>/<operation>.png, one figure
per operation type and available metric. Values are plotted in their original
units (ms for execution time, J for energy); nothing is converted.

Boxes: median line, Q1-Q3 box, whiskers at 1.5 x IQR (matplotlib default);
every individual trial is overlaid as a jittered dot, so outliers are shown as data
rather than as separate flier markers.
"""

from __future__ import annotations

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import common
from common import METRIC_LABELS, METRIC_UNITS, ORMS

# Categorical slots 1-3 of the validated default palette (blue, orange, aqua), fixed per ORM.
ORM_COLORS = dict(zip(ORMS, ("#2a78d6", "#eb6834", "#1baf7a")))
SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e4e3df"


def plot(machine: common.Machine, observations, operation: str, metric: str, path) -> None:
    groups = [common.series(observations, operation, orm, metric) for orm in ORMS]
    fig, ax = plt.subplots(figsize=(5.2, 4.2), dpi=200)
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)

    box = ax.boxplot(groups, widths=0.5, patch_artist=True, showfliers=False,
                     medianprops={"color": TEXT_PRIMARY, "linewidth": 2},
                     whiskerprops={"color": TEXT_SECONDARY, "linewidth": 1.2},
                     capprops={"color": TEXT_SECONDARY, "linewidth": 1.2},
                     boxprops={"linewidth": 1.2})
    rng = np.random.default_rng(0)
    for i, (orm, values, patch) in enumerate(zip(ORMS, groups, box["boxes"]), start=1):
        patch.set_facecolor(ORM_COLORS[orm] + "40")  # translucent fill
        patch.set_edgecolor(ORM_COLORS[orm])
        x = i + rng.uniform(-0.12, 0.12, len(values))
        ax.scatter(x, values, s=18, color=ORM_COLORS[orm], edgecolor=SURFACE, linewidth=0.8, zorder=3)

    ax.set_xticks(range(1, len(ORMS) + 1), [f"{orm}\n(n={len(v)})" for orm, v in zip(ORMS, groups)])
    ax.set_xlabel("ORM", color=TEXT_SECONDARY)
    ax.set_ylabel(f"{METRIC_LABELS[metric]} ({METRIC_UNITS[metric]})", color=TEXT_SECONDARY)
    ax.set_title(f"{operation}\n{machine.title}", fontsize=10, color=TEXT_PRIMARY)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=TEXT_SECONDARY)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--machine", choices=[*common.MACHINES, "all"], default="all")
    parser.add_argument("--experiment", help="Select one experiment directory name; requires --machine intel or mac")
    args = parser.parse_args()
    if args.experiment and args.machine == "all":
        parser.error("--experiment requires a single --machine")
    for key in common.MACHINES if args.machine == "all" else [args.machine]:
        machine = common.select_machine(key, args.experiment)
        observations, _ = common.load(machine)
        count = 0
        for metric in common.available_metrics(machine):
            folder = common.output_dir(machine) / "boxplots" / metric
            folder.mkdir(parents=True, exist_ok=True)
            for operation in common.operations(observations):
                plot(machine, observations, operation, metric, folder / f"{operation}.png")
                count += 1
        print(f"[{key}] wrote {count} box plots -> {common.output_dir(machine) / 'boxplots'}")


if __name__ == "__main__":
    main()
