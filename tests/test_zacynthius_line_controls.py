import importlib.util
from pathlib import Path
import unittest

try:
    import cv2
    import numpy as np
    from PIL import Image
except ImportError:
    cv2 = None

if cv2 is not None:
    path = Path(__file__).resolve().parents[1] / "tools/textual_restoration/check_zacynthius_line_controls.py"
    spec = importlib.util.spec_from_file_location("controls", path)
    controls = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(controls)


@unittest.skipIf(cv2 is None, "Requires OpenCV, NumPy and Pillow")
class ControlTests(unittest.TestCase):
    def test_color_subtraction_uses_signed_values(self):
        rgb = np.array([[[0, 200, 10], [0, 10, 200]]], dtype=np.uint8)
        np.testing.assert_array_equal(controls.color_difference(rgb), [[-190, 190]])

    def test_source_box_conversion(self):
        matrix = np.array([[1., 0., 0.], [0., 1., 0.]])
        self.assertEqual(controls.component_box((1000, 1200, 7800, 5700), matrix),
                         (-203, -276, 1803, 1054))

    def test_insufficient_supported_patches_fail(self):
        rows = [{"response": .8, "shift_norm_px": 0.} for _ in range(19)]
        self.assertFalse(controls.patch_gate(rows))

    def test_large_residuals_fail(self):
        rows = [{"response": .8, "shift_norm_px": 8.} for _ in range(35)]
        self.assertFalse(controls.patch_gate(rows))

    def test_small_supported_residuals_pass(self):
        rows = [{"response": .8, "shift_norm_px": .5} for _ in range(35)]
        self.assertTrue(controls.patch_gate(rows))

    def test_identical_image_patch_shifts_are_zero(self):
        rng = np.random.default_rng(1729)
        image = rng.uniform(0, 255, (1324, 2000)).astype(np.float32)
        rows = controls.patch_checks(image, image)
        self.assertEqual(len(rows), 35)
        self.assertLess(max(row["shift_norm_px"] for row in rows), 1e-5)
        self.assertTrue(controls.patch_gate(rows))


if __name__ == "__main__":
    unittest.main()
