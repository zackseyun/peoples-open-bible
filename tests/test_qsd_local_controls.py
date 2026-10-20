import importlib.util
from pathlib import Path
import sys
import unittest

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None

if cv2 is not None:
    folder = Path(__file__).resolve().parents[1] / "tools/textual_restoration"
    sys.path.insert(0, str(folder))
    spec = importlib.util.spec_from_file_location("qsd_local", folder / "probe_qsd_local_controls.py")
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)


@unittest.skipIf(cv2 is None, "Requires image dependencies")
class QsdLocalTests(unittest.TestCase):
    @staticmethod
    def control_rows(false_blank=False, missing_all_ink=False):
        rows = []
        for name, counts, positives in [
            ("124_008", {"tp": 0 if missing_all_ink else 2, "fp": 0,
                         "fn": 3 if missing_all_ink else 1, "tn": 7}, 3),
            ("690_015", {"tp": 0, "fp": int(false_blank), "fn": 0,
                         "tn": 10-int(false_blank)}, 0),
            ("690_016", {"tp": 0, "fp": 0, "fn": 0, "tn": 10}, 0),
        ]:
            rows.append({"fragment": name, "reference_positive_pixels": positives,
                         **counts, **probe.scores(counts)})
        return rows

    def test_constant_local_field_is_finite_zero(self):
        image = np.full((40, 40), 12345, dtype=np.uint16)
        result = probe.local_z(image)
        self.assertTrue(np.isfinite(result).all())
        self.assertLess(float(np.max(np.abs(result))), 0.001)
        self.assertTrue(np.all(image == 12345))

    def test_dark_center_has_negative_measured_local_contrast(self):
        image = np.full((41, 41), 40000, dtype=np.uint16)
        image[20, 20] = 1000
        result = probe.local_z(image)
        self.assertLess(result[20, 20], 0)
        self.assertLessEqual(float(np.max(np.abs(result))), 8)

    def test_raw_features_match_prior_signed_difference(self):
        first = np.array([30000, 1000], dtype=np.float32)
        last = np.array([1000, 30000], dtype=np.float32)
        result = probe.batch_features(first, last, slice(None), "raw")
        np.testing.assert_array_equal(result, probe.raw_features(first, last, True))
        self.assertLess(result[0, 2], 0)

    def test_local_features_append_without_replacing_measurements(self):
        first = np.array([1, 2], dtype=np.float32)
        result = probe.batch_features(first, first, slice(None), "local", (first, -first))
        self.assertEqual(result.shape, (2, 5))
        np.testing.assert_array_equal(result[:, :3], probe.raw_features(first, first, True))

    def test_class_sampling_is_fixed_and_disjoint(self):
        labels = np.repeat(np.arange(3), 40)
        one = probe.selected_pixels(labels, 1776, maximum=10)
        np.testing.assert_array_equal(one, probe.selected_pixels(labels, 1776, maximum=10))
        self.assertEqual(len(np.unique(one)), 30)
        self.assertEqual(np.bincount(labels[one]).tolist(), [10, 10, 10])

    def test_empty_reference_is_not_silently_counted_as_perfect(self):
        row = {"fragment": "blank", "reference_positive_pixels": 0,
               "tp": 0, "fp": 1, "fn": 0, "tn": 9,
               "precision": 0, "recall": None, "iou": 0, "f1": 0}
        result = probe.summarize([row])
        self.assertEqual(result["nonempty_reference_fragments"], 0)
        self.assertIsNone(result["nonempty_reference_macro_f1"])
        self.assertEqual(result["empty_reference_false_positives"], {"blank": 1})

    def test_development_pass_never_authorizes_transcription(self):
        rows = self.control_rows()
        result = probe.development_screen(rows, rows)
        self.assertTrue(result["passed"])
        self.assertFalse(result["transcription_deployment_authorized"])

    def test_any_false_pixel_on_empty_control_fails_screen(self):
        result = probe.development_screen(self.control_rows(false_blank=True), self.control_rows())
        self.assertFalse(result["checks"]["empty_controls"])
        self.assertFalse(result["passed"])

    def test_fixed_nonempty_average_has_same_denominator(self):
        result = probe.summarize(self.control_rows(false_blank=True))
        self.assertEqual(result["nonempty_reference_macro_f1"], 0.8)
        self.assertEqual(result["macro_all_defined"]["f1"], 0.4)
        self.assertEqual(result["nonempty_reference_fragments"], 1)

    def test_zero_predictions_cannot_pass_on_undefined_precision(self):
        result = probe.development_screen(self.control_rows(missing_all_ink=True), self.control_rows())
        self.assertFalse(result["checks"]["pooled_precision"])
        self.assertFalse(result["passed"])


if __name__ == "__main__":
    unittest.main()
