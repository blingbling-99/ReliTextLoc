# Synthetic CPU example

Every coordinate and scene identifier here is invented. These 12 ground-truth
queries and 11 manually constructed predictions demonstrate the evaluation
interface only. They are neither third-party data nor model-generated results,
and are not evidence of ReliTextLoc performance.

Cases cover exact inclusive 5/10/15-meter thresholds, values immediately below
and above boundaries, a diagonal 3-4-5 displacement, wrong-scene coordinates,
an invalid flag, missing/malformed coordinates, and one omitted prediction.
All 12 GT queries stay in the denominator. Expected overall counts are 3, 5,
and 6 successes, giving R@5m = 25%, R@10m = 41.6667%, and R@15m = 50%.
Only 7 errors are finite; finite-only recalls are diagnostic values.

Run from the repository root:

```bash
python -m reli_text_loc_public.evaluate --config configs/synthetic.json
python -m reli_text_loc_public.plot --metrics outputs/synthetic/metrics.json --output outputs/synthetic/recall.png
python -m reli_text_loc_public.visualize --results outputs/synthetic/per_query.json --metrics outputs/synthetic/metrics.json --method synthetic_demo --output outputs/synthetic/xy.png
```

Generated results and images belong in `outputs/` and are not shipped as research
predictions. `expected_metrics.json` is a hand-checked synthetic test oracle.
