"""CLI for evaluating JSONL predictions; run with python -m."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

from .data import read_ground_truth, read_predictions
from .metrics import evaluate


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
                    encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, help="JSON config; paths relative to the config file")
    parser.add_argument("--gt", type=Path, help="GT JSONL; paths relative to current directory")
    parser.add_argument("--predictions", type=Path, help="prediction JSONL")
    parser.add_argument("--methods", nargs="+", help="expected methods (including wholly missing ones)")
    parser.add_argument("--output", type=Path, help="output directory")
    args = parser.parse_args()
    config = {}
    base = Path.cwd()
    if args.config:
        config = json.loads(args.config.read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            parser.error("config must be a JSON object")
        unknown = set(config) - {"ground_truth", "predictions", "methods", "output_dir", "example_kind"}
        if unknown:
            parser.error(f"unsupported config keys: {sorted(unknown)}")
        base = args.config.resolve().parent

    def path_setting(override: Path | None, key: str, option: str) -> Path:
        if override is not None:
            return override
        value = config.get(key)
        if not isinstance(value, str) or not value:
            parser.error(f"provide {option} or config key {key}")
        return base / value

    gt_path = path_setting(args.gt, "ground_truth", "--gt")
    prediction_path = path_setting(args.predictions, "predictions", "--predictions")
    output = path_setting(args.output, "output_dir", "--output")
    methods = args.methods if args.methods is not None else config.get("methods")
    if not isinstance(methods, list):
        parser.error("provide --methods or a methods array in config")
    summary, per_query = evaluate(read_ground_truth(gt_path), read_predictions(prediction_path), methods)
    report = {
        "release_scope": "partial public utilities; no reranking or model inference",
        "example_kind": config.get("example_kind", "user_supplied"),
        "contract": {
            "coordinate_system": "world XY in meters", "distance": "Euclidean",
            "threshold_comparison": "<=", "thresholds_m": [5, 10, 15],
            "recall_denominator": "all ground-truth queries, separately for each method",
            "failure_error": "+inf", "finite_only_metrics": "diagnostics; not headline recall",
        },
        "metrics": summary,
    }
    write_json(output / "metrics.json", report)
    # Standard JSON cannot encode infinity. The documented sentinel preserves it.
    serial_rows = [{**row, "error_m": row["error_m"] if math.isfinite(row["error_m"]) else "+inf"}
                   for row in per_query]
    write_json(output / "per_query.json", serial_rows)
    with (output / "metrics.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    for row in summary:
        if row["scope"] == "ALL":
            print(json.dumps({key: row[key] for key in
                              ("method", "N", "finite_error_denominator", "missing_predictions",
                               "R@5m", "R@10m", "R@15m")}, allow_nan=False))


if __name__ == "__main__":
    main()
