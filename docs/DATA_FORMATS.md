# Public data interfaces and formats

The public tools evaluate **already selected world-XY predictions**. They do
not load the model, select candidates, rerank candidates, or infer coordinates.
The files in `examples/synthetic/` contain invented data and manually constructed
predictions, solely to demonstrate these interfaces.

## Ground-truth JSONL

Each nonblank UTF-8 line is one JSON object:

```json
{"query_id":"query_001","source_scene":"scene_a","gt_xy":[100.0,200.0]}
```

| Field | Required format | Meaning |
| --- | --- | --- |
| `query_id` | Unique, nonempty string | Query identity; one row per evaluated text query |
| `source_scene` | Nonempty string | Ground-truth scene identity |
| `gt_xy` | Array of two finite numbers | Ground-truth world X/Y coordinates in meters |

Use the complete ground-truth query manifest for the intended evaluation split.
The denominator is the number of supplied GT queries, separately for each
configured method; the public reader cannot verify that a user-supplied manifest
contains every query in an external benchmark. Queries sharing a position still
count separately. Empty GT, duplicate query IDs, booleans used as coordinates,
and nonfinite/malformed GT coordinates are rejected.

## Prediction JSONL

Each row describes one already selected prediction for a query and method:

```json
{"query_id":"query_001","method":"your_method","valid":true,"candidate_scene":"scene_a","world_xy":[103.0,204.0]}
```

| Field | Format | Meaning |
| --- | --- | --- |
| `query_id` | Required nonempty string | Must occur in the GT manifest |
| `method` | Required nonempty string | Must occur in the configured methods list |
| `valid` | JSON boolean; omitted defaults to `false` | Declared prediction-validity flag |
| `candidate_scene` | Nonempty string or `null`; omitted means `null` | Selected prediction's scene identity |
| `world_xy` | Array of two finite numbers for a usable prediction | Selected world X/Y coordinates in meters |

Missing, `null`, malformed, or nonfinite prediction coordinates are retained as
failures. A string such as `"false"` is not a boolean and is rejected. Standard
JSON does not permit literal `NaN` or `Infinity`; use `null` to represent unusable
coordinates. Duplicate JSON keys, duplicate query/method pairs, unknown query
IDs, and prediction methods absent from the configured list are rejected. Empty
prediction files are accepted: every GT query then fails for every configured
method. A missing prediction row is also a failure and is never removed from the
denominator.

The readers project rows onto these public fields. Other metadata is ignored
and does not enter evaluator outputs.

## Coordinates and metric contract

Both coordinate arrays must use the **same world coordinate convention, in
meters**. Coordinates are XY, not XYZ or normalized local-cell coordinates.
If a caller holds normalized cell-local predictions, the caller must perform its
own dataset-specific conversion before writing `world_xy`; the public tools do
not load dataset geometry or guess this conversion.

The evaluator uses the author's NumPy float64 calculation:

```python
error_m = float(np.linalg.norm(np.asarray(world_xy, dtype=np.float64)
                               - np.asarray(gt_xy, dtype=np.float64)))
```

A valid prediction must have `valid == true`, two finite XY coordinates, and
`candidate_scene == source_scene`. Otherwise its error is positive infinity and
it fails every threshold. Coordinates from a different scene fail even when their
numeric values equal GT. Success uses `error_m <= t` for `t` equal to 5, 10, and
15 meters. The original float64 norm and inclusive comparison are preserved,
including floating-point rounding at exact non-axis boundaries.

Headline `R@5m`, `R@10m`, and `R@15m` equal the respective success counts divided
by **all supplied GT queries**, including invalid, missing, wrong-scene, and
unusable predictions. Output recalls are fractions in `[0, 1]`, not percentages.
Metrics are reported for each scene and for all queries (`scope: "ALL"`) using
`query_micro` aggregation. No scene-macro average is calculated by this release.

Diagnostic counters overlap. `valid` counts declared flags, even if coordinates
are unusable or the scene is wrong. `wrong_scene` counts scene inequality,
including a missing candidate-scene identity and omitted prediction row.
`missing_predictions` counts omitted rows. `finite_error_denominator` counts only
predictions having finite evaluated errors. `finite_only_R@5m`,
`finite_only_R@10m`, and `finite_only_R@15m` use that smaller denominator; they
are **diagnostics and must not replace headline recall**. If this denominator is
zero, finite-only recall is JSON `null` (blank in CSV).

## Configuration and paths

`configs/evaluation.template.json` provides the schema:

```json
{
  "ground_truth": "../data/ground_truth.jsonl",
  "predictions": "../data/predictions.jsonl",
  "methods": ["your_method"],
  "output_dir": "../outputs/evaluation",
  "example_kind": "user_supplied"
}
```

Specify every intended method explicitly, including a method with no predictions.
Method names must be unique nonempty strings. Paths from a config resolve
relative to that config file. Explicit command-line paths resolve relative to
the current directory and override corresponding config paths. `example_kind`
labels result provenance; the shipped demonstration sets it to `synthetic`.
There are no workstation paths in the public configuration templates.

```bash
python -m reli_text_loc_public.evaluate --config configs/synthetic.json
python -m reli_text_loc_public.evaluate --gt data/ground_truth.jsonl --predictions data/predictions.jsonl --methods your_method --output outputs/evaluation
```

## Outputs and visualization

Evaluation writes three files under `output_dir`:

| File | Contents |
| --- | --- |
| `metrics.json` | Provenance label, metric contract, and per-scene/overall metric rows |
| `metrics.csv` | The same metric rows in tabular form |
| `per_query.json` | GT/prediction XY, scene identities, flags, errors, and success outcomes for every GT-query/method pair |

`per_query.json` encodes positive infinity as the string `"+inf"`, because
standard JSON has no numeric infinity. Unusable or missing prediction coordinates
become `null` in `world_x`/`world_y`. Finite `error_m` values remain numbers.

```bash
python -m reli_text_loc_public.plot --metrics outputs/synthetic/metrics.json --output outputs/synthetic/recall.png
python -m reli_text_loc_public.visualize --results outputs/synthetic/per_query.json --metrics outputs/synthetic/metrics.json --method synthetic_demo --output outputs/synthetic/xy.png
```

The recall chart plots headline full-denominator recalls. The XY visualization
places each GT scene in a separate panel; failed predictions are marked at their
GT positions, and predictions from a different scene are not drawn as if they
shared that scene's world coordinates. Both figures use the result provenance
label to mark the supplied synthetic example clearly.
