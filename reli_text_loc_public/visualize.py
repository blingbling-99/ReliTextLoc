"""Visualize evaluated world-XY predictions, with each scene in its own panel."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True, help="public per_query.json")
    parser.add_argument("--metrics", type=Path, required=True, help="matching metrics.json (includes example label)")
    parser.add_argument("--method", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from .figure_style import BASELINE, GRID, OURS, RED, apply_style
    apply_style()
    rows = [row for row in json.loads(args.results.read_text(encoding="utf-8"))
            if row["method"] == args.method]
    if not rows:
        parser.error("selected method has no per-query rows")
    report = json.loads(args.metrics.read_text(encoding="utf-8"))
    scenes = sorted({row["source_scene"] for row in rows})
    columns = min(3, len(scenes))
    count_rows = math.ceil(len(scenes) / columns)
    figure, axes = plt.subplots(count_rows, columns, squeeze=False,
                               figsize=(4.3 * columns, 5.0 * count_rows))
    for axis, scene in zip(axes.flat, scenes):
        scene_rows = [row for row in rows if row["source_scene"] == scene]
        first_finite = True
        first_failed = True
        for index, row in enumerate(scene_rows):
            gx, gy = row["gt_x"], row["gt_y"]
            axis.scatter([gx], [gy], color=BASELINE, s=24,
                         label="Ground truth" if index == 0 else None, zorder=3)
            if row["finite_error"]:
                px, py = row["world_x"], row["world_y"]
                axis.plot([gx, px], [gy, py], color=OURS, linewidth=0.9, alpha=0.75)
                axis.scatter([px], [py], color=OURS, marker="^", s=28,
                             label="Usable prediction" if first_finite else None, zorder=4)
                first_finite = False
            else:
                # Coordinates in a different scene cannot be overlaid as world positions.
                axis.scatter([gx], [gy], marker="x", color=RED, s=55,
                             label="Failed prediction" if first_failed else None, zorder=5)
                first_failed = False
            axis.annotate(row["query_id"], (gx, gy), xytext=(4, 4),
                          textcoords="offset points", fontsize=6)
        axis.set_title(f"{scene}: {args.method}")
        axis.set_xlabel("World X (m)")
        axis.set_ylabel("World Y (m)")
        axis.set_aspect("equal", adjustable="datalim")
        axis.margins(0.18)
        axis.grid(color=GRID, linewidth=0.6)
        axis.legend(loc="upper left", frameon=False, fontsize=6.5)
    for axis in list(axes.flat)[len(scenes):]:
        axis.set_visible(False)
    label = "Synthetic illustration" if report.get("example_kind") == "synthetic" else "User-supplied predictions"
    figure.suptitle(label + ": errors are measured within the matching scene", fontsize=10)
    figure.tight_layout(rect=(0, 0, 1, 0.94))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=180)
    plt.close(figure)
    print(f"Saved {args.output.name}")


if __name__ == "__main__":
    main()
