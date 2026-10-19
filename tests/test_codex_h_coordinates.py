import importlib.util
from pathlib import Path
import sys
import unittest

try:
    import cv2
    import numpy as np
    from PIL import Image
except ImportError:
    cv2 = None

if cv2 is not None:
    folder = Path(__file__).resolve().parents[1] / "tools/textual_restoration"
    sys.path.insert(0, str(folder))
    spec = importlib.util.spec_from_file_location("codex_coordinates", folder / "check_codex_h_coordinates.py")
    controls = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(controls)


@unittest.skipIf(cv2 is None, "Requires image dependencies")
class CoordinateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = np.random.default_rng(1043).integers(0, 256, (1775, 1320, 3), dtype=np.uint8)

    def test_identity_passes_both_fields(self):
        for region in ("upper", "lower"):
            result = controls.measure_region(self.image, self.image, region)
            self.assertEqual(len(result["rows"]), 35)
            self.assertEqual(result["strong_count"], 35)
            self.assertTrue(result["gate_passed"])
            self.assertLess(result["strong_p95"], 1e-5)

    def test_three_pixel_shift_fails_unchanged_gate(self):
        shifted = np.roll(self.image, 3, axis=1)
        result = controls.measure_region(self.image, shifted, "upper")
        self.assertGreaterEqual(result["strong_count"], 20)
        self.assertGreater(result["strong_median"], 2.5)
        self.assertFalse(result["gate_passed"])

    def test_kyiv_identity_uses_native_overview_dimensions(self):
        image = np.random.default_rng(1044).integers(0, 256, (1759, 1396, 3), dtype=np.uint8)
        for region in ("upper", "lower"):
            result = controls.measure_region(image, image, region, (1759, 1396, 3))
            self.assertEqual(result["strong_count"], 35)
            self.assertTrue(result["gate_passed"])

    def test_wrong_dimensions_are_rejected(self):
        with self.assertRaises(ValueError):
            controls.measure_region(self.image, self.image, "upper", (1759, 1396, 3))

    def test_incomplete_patch_grid_is_rejected(self):
        image = self.image[:900]
        with self.assertRaisesRegex(ValueError, "complete fixed patch grid"):
            controls.measure_region(image, image, "lower", image.shape)


if __name__ == "__main__":
    unittest.main()
