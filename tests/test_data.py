"""Reject ambiguous identities/GT while counting unusable predictions as failures."""

import json
import tempfile
import unittest
from pathlib import Path

from reli_text_loc_public.data import read_ground_truth, read_jsonl, read_predictions


class DataValidationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "example.jsonl"
        self.gt = {"query_id": "q", "source_scene": "a", "gt_xy": [0, 0]}
        self.pred = {"query_id": "q", "method": "m", "valid": True,
                     "candidate_scene": "a", "world_xy": [0, 0]}

    def write_rows(self, rows):
        self.path.write_text("\n".join(json.dumps(row, allow_nan=False) for row in rows) + "\n")

    def test_reject_nonstandard_nan_and_duplicate_json_keys(self):
        for text in ('{"query_id":"q","world_xy":[NaN,0]}',
                     '{"query_id":"q","query_id":"r"}'):
            with self.subTest(text=text):
                self.path.write_text(text)
                with self.assertRaises(ValueError):
                    read_jsonl(self.path)

    def test_reject_duplicate_ground_truth_id(self):
        self.write_rows([self.gt, self.gt])
        with self.assertRaisesRegex(ValueError, "duplicate ground-truth"):
            read_ground_truth(self.path)

    def test_reject_duplicate_prediction_identity(self):
        self.write_rows([self.pred, self.pred])
        with self.assertRaisesRegex(ValueError, "duplicate prediction"):
            read_predictions(self.path)

    def test_reject_invalid_gt_coordinates(self):
        for xy in (None, [0], [True, 0], ["0", 0]):
            with self.subTest(xy=xy):
                self.write_rows([{**self.gt, "gt_xy": xy}])
                with self.assertRaisesRegex(ValueError, "two finite"):
                    read_ground_truth(self.path)

    def test_unusable_prediction_coordinates_reach_evaluation(self):
        self.write_rows([{**self.pred, "world_xy": None}])
        self.assertIsNone(read_predictions(self.path)[0]["world_xy"])

    def test_reject_ambiguous_prediction_flag(self):
        self.write_rows([{**self.pred, "valid": "false"}])
        with self.assertRaisesRegex(ValueError, "JSON boolean"):
            read_predictions(self.path)

    def test_extra_metadata_is_not_exported(self):
        self.write_rows([{**self.gt, "unused_metadata": "ignored"}])
        self.assertEqual(set(read_ground_truth(self.path)[0]), {"query_id", "source_scene", "gt_xy"})
        self.write_rows([{**self.pred, "unused_metadata": "ignored"}])
        self.assertNotIn("unused_metadata", read_predictions(self.path)[0])

    def test_empty_gt_rejected(self):
        self.path.write_text("\n")
        with self.assertRaisesRegex(ValueError, "at least one"):
            read_ground_truth(self.path)


if __name__ == "__main__":
    unittest.main()
