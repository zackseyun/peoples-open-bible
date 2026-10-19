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


if __name__ == "__main__":
    unittest.main()
