"""Scientific metric-contract checks, using invented coordinates only."""

import json
import math
import unittest
from pathlib import Path

from reli_text_loc_public.data import read_ground_truth, read_predictions
from reli_text_loc_public.metrics import THRESHOLDS, aggregate, classify, evaluate

ROOT = Path(__file__).resolve().parents[1]


class MetricContractTests(unittest.TestCase):
    def setUp(self):
        self.gt = {"query_id": "q", "source_scene": "a", "gt_xy": [0.0, 0.0]}

    def pred(self, xy, **overrides):
        return {"query_id": "q", "method": "m", "valid": True,
                "candidate_scene": "a", "world_xy": xy, **overrides}

    def test_inclusive_thresholds_and_nearby_values(self):
        for boundary in THRESHOLDS:
            for offset in (-1e-9, 0, 1e-9):
                with self.subTest(boundary=boundary, offset=offset):
                    result = classify(self.pred([boundary + offset, 0]), self.gt)
                    for threshold in THRESHOLDS:
                        self.assertEqual(result[f"success_{threshold}m"], boundary + offset <= threshold)

    def test_euclidean_world_xy_with_shifted_origin(self):
        gt = {**self.gt, "gt_xy": [100, -20]}
        result = classify(self.pred([103, -16]), gt)
        self.assertEqual(result["error_m"], 5)
        self.assertTrue(result["success_5m"])

    def test_preserve_author_float64_norm_at_nonaxis_boundaries(self):
        # These vectors expose different rounding between np.linalg.norm and
        # math.hypot. The authoritative evaluator uses the NumPy float64 norm.
        inside = classify(self.pred([-4.075821514125616, 2.8961489921947687]), self.gt)
        outside = classify(self.pred([-4.900241136291229, 0.9937991780029034]), self.gt)
        self.assertEqual(inside["error_m"], 5.0)
        self.assertTrue(inside["success_5m"])
        self.assertEqual(outside["error_m"], 5.000000000000001)
        self.assertFalse(outside["success_5m"])

    def test_wrong_scene_fails_even_at_identical_xy(self):
        result = classify(self.pred([0, 0], candidate_scene="b"), self.gt)
        self.assertTrue(result["wrong_scene"])
        self.assertTrue(result["valid"])
        self.assertTrue(math.isinf(result["error_m"]))
        self.assertFalse(any(result[f"success_{threshold}m"] for threshold in THRESHOLDS))

    def test_invalid_declared_flag_fails_even_at_identical_xy(self):
        result = classify(self.pred([0, 0], valid=False), self.gt)
        self.assertFalse(result["valid"])
        self.assertTrue(math.isinf(result["error_m"]))

    def test_unusable_xy_fails_without_dropping_query(self):
        for xy in (None, [], [0], [0, 0, 0], [math.nan, 0], [math.inf, 0],
                   ["0", 0], [True, 0], "0,0", [10 ** 400, 0]):
            with self.subTest(xy=xy):
                result = classify(self.pred(xy), self.gt)
                self.assertFalse(result["finite_xy"])
                self.assertTrue(math.isinf(result["error_m"]))
                self.assertEqual(aggregate([result])["N"], 1)
                self.assertEqual(aggregate([result])["R@15m"], 0)

    def test_nonboolean_flags_rejected(self):
        with self.assertRaisesRegex(ValueError, "valid must be a boolean"):
            classify(self.pred([0, 0], valid="false"), self.gt)

    def test_missing_prediction_retains_full_denominator(self):
        gt = [self.gt, {**self.gt, "query_id": "missing"}]
        summary, rows = evaluate(gt, [self.pred([0, 0])], ["m"])
        overall = next(row for row in summary if row["scope"] == "ALL")
        self.assertEqual(overall["N"], 2)
        self.assertEqual(overall["missing_predictions"], 1)
        self.assertEqual(overall["finite_error_denominator"], 1)
        self.assertEqual(overall["R@5m"], 0.5)
        self.assertEqual(overall["finite_only_R@5m"], 1.0)
        self.assertEqual(len(rows), 2)

    def test_wholly_absent_method_is_all_failures(self):
        summary, rows = evaluate([self.gt], [], ["absent_method"])
        overall = next(row for row in summary if row["scope"] == "ALL")
        self.assertEqual(overall["N"], 1)
        self.assertEqual(overall["missing_predictions"], 1)
        self.assertEqual(overall["R@15m"], 0)
        self.assertIsNone(overall["finite_only_R@15m"])

    def test_duplicate_queries_predictions_and_methods_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate ground-truth"):
            evaluate([self.gt, self.gt], [], ["m"])
        with self.assertRaisesRegex(ValueError, "duplicate query/method"):
            evaluate([self.gt], [self.pred([0, 0]), self.pred([0, 0])], ["m"])
        with self.assertRaisesRegex(ValueError, "unique"):
            evaluate([self.gt], [], ["m", "m"])

    def test_unknown_prediction_query_or_method_rejected(self):
        with self.assertRaisesRegex(ValueError, "query_id absent"):
            evaluate([self.gt], [self.pred([0, 0], query_id="unknown")], ["m"])
        with self.assertRaisesRegex(ValueError, "method absent"):
            evaluate([self.gt], [self.pred([0, 0], method="unknown")], ["m"])

    def test_empty_gt_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least one"):
            evaluate([], [], ["m"])

    def test_synthetic_oracle(self):
        example = ROOT / "examples" / "synthetic"
        expected = json.loads((example / "expected_metrics.json").read_text())
        summary, rows = evaluate(read_ground_truth(example / "ground_truth.jsonl"),
                                 read_predictions(example / "predictions.jsonl"), ["synthetic_demo"])
        overall = next(row for row in summary if row["scope"] == "ALL")
        for key, value in expected.items():
            if key != "example_kind":
                self.assertEqual(overall[key], value)
        self.assertEqual(len(rows), expected["N"])


if __name__ == "__main__":
    unittest.main()
