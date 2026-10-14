"""Guard false-ink accounting and empty reference semantics in the QSD probe."""

import unittest

import numpy as np

from tools.textual_restoration.evaluate_qsd_release import compare, scores


class QsdMetricsTests(unittest.TestCase):
    def test_confusion_counts_and_scores(self):
        truth = np.array([True, True, False, False])
        prediction = np.array([True, False, True, False])
        counts = compare(truth, prediction)
        self.assertEqual(counts, {"tp": 1, "fp": 1, "fn": 1, "tn": 1})
        self.assertEqual(scores(counts), {"precision": 0.5, "recall": 0.5,
                                         "iou": 1 / 3, "f1": 0.5})

    def test_empty_pair_is_undefined_not_perfect_accuracy(self):
        blank = np.zeros((2, 3), dtype=bool)
        counts = compare(blank, blank)
        self.assertEqual(counts["tn"], 6)
        self.assertTrue(all(value is None for value in scores(counts).values()))
        self.assertTrue(all(value == 0 for value in scores(counts, undefined=0).values()))

    def test_false_ink_on_empty_reference_is_counted(self):
        counts = compare(np.array([False, False]), np.array([True, False]))
        self.assertEqual(counts["fp"], 1)
        self.assertEqual(scores(counts), {"precision": 0.0, "recall": None,
                                         "iou": 0.0, "f1": 0.0})

    def test_shape_mismatch_cannot_broadcast(self):
        with self.assertRaises(ValueError):
            compare(np.zeros((2, 1), dtype=bool), np.zeros((2,), dtype=bool))


if __name__ == "__main__":
    unittest.main()
