"""Small, documented JSONL interface; no model or private-data imports."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


def finite_xy(value: Any) -> tuple[float, float] | None:
    """Return two finite numeric XY values, or None for unusable coordinates."""
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        return None
    if any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in value):
        return None
    try:
        xy = (float(value[0]), float(value[1]))
    except (OverflowError, ValueError):
        return None
    return xy if all(math.isfinite(v) for v in xy) else None


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant {value}; use null for unusable coordinates")


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Read UTF-8 JSON objects, rejecting ambiguous or non-standard JSON."""
    rows = []
    with Path(path).open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line, object_pairs_hook=_no_duplicate_keys,
                                 parse_constant=_reject_constant)
                if not isinstance(row, dict):
                    raise ValueError("each JSONL record must be an object")
            except (ValueError, json.JSONDecodeError) as exc:
                raise ValueError(f"{Path(path).name}:{line_number}: {exc}") from exc
            rows.append(row)
    return rows


def _required_string(row: dict[str, Any], field: str, context: str) -> str:
    value = row.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{context}: {field} must be a nonempty string")
    return value


def read_ground_truth(path: str | Path) -> list[dict[str, Any]]:
    """Require unique query IDs, scene identities, and finite world-XY GT."""
    result = []
    seen = set()
    for index, row in enumerate(read_jsonl(path), start=1):
        context = f"ground-truth record {index}"
        query_id = _required_string(row, "query_id", context)
        if query_id in seen:
            raise ValueError(f"duplicate ground-truth query_id: {query_id}")
        seen.add(query_id)
        scene = _required_string(row, "source_scene", context)
        xy = finite_xy(row.get("gt_xy"))
        if xy is None:
            raise ValueError(f"{context}: gt_xy must contain two finite numbers")
        # Project to the public schema: private metadata never enters outputs.
        result.append({"query_id": query_id, "source_scene": scene, "gt_xy": list(xy)})
    if not result:
        raise ValueError("ground truth must contain at least one query")
    return result


def read_predictions(path: str | Path) -> list[dict[str, Any]]:
    """Validate identities; unusable XY remains an evaluation failure."""
    result = []
    seen = set()
    for index, row in enumerate(read_jsonl(path), start=1):
        context = f"prediction record {index}"
        query_id = _required_string(row, "query_id", context)
        method = _required_string(row, "method", context)
        key = (query_id, method)
        if key in seen:
            raise ValueError(f"duplicate prediction for query/method: {key}")
        seen.add(key)
        valid = row.get("valid", False)
        if not isinstance(valid, bool):
            raise ValueError(f"{context}: valid must be a JSON boolean")
        scene = row.get("candidate_scene")
        if scene is not None and (not isinstance(scene, str) or not scene.strip()):
            raise ValueError(f"{context}: candidate_scene must be a nonempty string or null")
        result.append({"query_id": query_id, "method": method, "valid": valid,
                       "candidate_scene": scene, "world_xy": row.get("world_xy")})
    return result
