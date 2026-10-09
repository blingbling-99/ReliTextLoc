"""Localization metrics adapted from the authors' existing evaluator.

The metric contract is Euclidean world XY in meters, inclusive thresholds,
invalid/unusable/wrong-scene predictions assigned +inf, and a full GT-query
denominator. No reranking, candidate selection, or model inference is included.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from .data import finite_xy

THRESHOLDS = (5, 10, 15)


def classify(pred: dict[str, Any] | None, gt: dict[str, Any]) -> dict[str, Any]:
    """Classify one already-selected prediction against one GT query.

    Missing predictions also fail. Ground-truth coordinates must be finite.
    The public reader validates boolean flags before calling this function.
    """
    gt_xy = finite_xy(gt.get("gt_xy"))
    if gt_xy is None:
        raise ValueError("gt_xy must contain two finite numbers")
    missing = pred is None
    pred = {} if missing else pred
    valid = pred.get("valid", False)
    if not isinstance(valid, bool):
        raise ValueError("valid must be a boolean")
    xy = finite_xy(pred.get("world_xy"))
    wrong = pred.get("candidate_scene") != gt["source_scene"]
    # Preserve the author's float64 subtraction/norm, including numerical
    # rounding at inclusive boundaries; do not substitute another norm routine.
    error = (float(np.linalg.norm(np.asarray(xy, dtype=np.float64)
                                  - np.asarray(gt_xy, dtype=np.float64)))
             if valid and xy is not None and not wrong else math.inf)
    return {
        "valid": valid,
        "finite_xy": xy is not None,
        "wrong_scene": wrong,
        "missing_prediction": missing,
        "finite_error": math.isfinite(error),
        "error_m": error,
        **{f"success_{t}m": bool(error <= t) for t in THRESHOLDS},
    }


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Recall uses every GT query; finite-only recalls are diagnostics."""
    n = len(rows)
    finite = [row for row in rows if row["finite_error"]]
    result: dict[str, Any] = {
        "N": n,
        "valid": sum(row["valid"] for row in rows),
        "wrong_scene": sum(row["wrong_scene"] for row in rows),
        "missing_predictions": sum(row["missing_prediction"] for row in rows),
        "finite_error_denominator": len(finite),
    }
    for threshold in THRESHOLDS:
        successes = sum(row[f"success_{threshold}m"] for row in rows)
        result[f"success_{threshold}m"] = successes
        result[f"R@{threshold}m"] = successes / n if n else None
        result[f"finite_only_R@{threshold}m"] = successes / len(finite) if finite else None
    return result


def evaluate(ground_truth: list[dict[str, Any]], predictions: list[dict[str, Any]],
             methods: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Evaluate each requested method over all supplied GT queries."""
    if not ground_truth:
        raise ValueError("ground truth must contain at least one query")
    if (not methods or any(not isinstance(m, str) or not m.strip() for m in methods)
            or len(set(methods)) != len(methods)):
        raise ValueError("methods must be a nonempty list of unique nonempty strings")
    query_ids = [gt["query_id"] for gt in ground_truth]
    if len(set(query_ids)) != len(query_ids):
        raise ValueError("duplicate ground-truth query_id")
    known_queries = set(query_ids)
    indexed = {}
    for pred in predictions:
        key = (pred["query_id"], pred["method"])
        if key in indexed:
            raise ValueError(f"duplicate query/method prediction: {key}")
        if pred["query_id"] not in known_queries:
            raise ValueError(f"prediction query_id absent from ground truth: {pred['query_id']}")
        if pred["method"] not in methods:
            raise ValueError(f"prediction method absent from requested methods: {pred['method']}")
        indexed[key] = pred

    per_query = []
    summary = []
    for method in methods:
        classified = []
        for gt in ground_truth:
            pred = indexed.get((gt["query_id"], method))
            result = classify(pred, gt)
            classified.append({"source_scene": gt["source_scene"], **result})
            xy = finite_xy(pred.get("world_xy")) if pred is not None else None
            per_query.append({
                "query_id": gt["query_id"], "method": method,
                "source_scene": gt["source_scene"],
                "gt_x": gt["gt_xy"][0], "gt_y": gt["gt_xy"][1],
                "candidate_scene": pred.get("candidate_scene") if pred is not None else None,
                "world_x": xy[0] if xy is not None else None,
                "world_y": xy[1] if xy is not None else None,
                **result,
            })
        for scene in sorted({gt["source_scene"] for gt in ground_truth}):
            scene_rows = [row for row in classified if row["source_scene"] == scene]
            summary.append({"scope": scene, "aggregation": "query_micro",
                            "method": method, **aggregate(scene_rows)})
        summary.append({"scope": "ALL", "aggregation": "query_micro",
                        "method": method, **aggregate(classified)})
    return summary, per_query
