"""Plot full-denominator recall from the public evaluator's metrics.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # Matplotlib is isolated from the NumPy-only evaluator.
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from .figure_style import BASELINE, EXTERNAL, GREEN, GRID, OURS, apply_style
    apply_style()
    report = json.loads(args.metrics.read_text(encoding="utf-8"))
    rows = [row for row in report["metrics"]
            if row["scope"] == "ALL" and row["aggregation"] == "query_micro"]
    if not rows:
        parser.error("no overall query-micro recall rows")
    figure, axis = plt.subplots(figsize=(6.4, 3.5))
    thresholds = [5, 10, 15]
    width = 0.75 / len(rows)
    colors = [OURS, BASELINE, EXTERNAL, GREEN]
    for index, row in enumerate(rows):
        positions = [i - 0.375 + width * (index + 0.5) for i in range(3)]
        bars = axis.bar(positions, [100 * row[f"R@{t}m"] for t in thresholds],
                        width=width, label=f"{row['method']} (N={row['N']})",
                        color=colors[index % len(colors)])
        axis.bar_label(bars, fmt="%.1f%%", fontsize=7, padding=3)
    axis.set_xticks(range(3), [f"R@{t}m" for t in thresholds])
    axis.set_ylabel("Recall over all GT queries (%)")
    axis.set_ylim(0, 110)
    axis.set_yticks(range(0, 101, 20))
    axis.grid(axis="y", color=GRID, linewidth=0.6)
    axis.set_axisbelow(True)
    label = "Synthetic illustration" if report.get("example_kind") == "synthetic" else "User-supplied predictions"
    axis.set_title(label + ": inclusive world-XY thresholds")
    axis.legend(loc="upper left", frameon=False)
    figure.tight_layout()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=180)
    plt.close(figure)
    print(f"Saved {args.output.name}")


if __name__ == "__main__":
    main()
