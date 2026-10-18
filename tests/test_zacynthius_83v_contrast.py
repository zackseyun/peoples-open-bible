import copy
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
    path = Path(__file__).resolve().parents[1] / "tools/textual_restoration/probe_zacynthius_83v_contrast.py"
    spec = importlib.util.spec_from_file_location("contrast", path)
    contrast = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(contrast)


@unittest.skipIf(cv2 is None, "Spectral contrast requires OpenCV, NumPy and Pillow")
class ContrastTests(unittest.TestCase):
    def fixture(self):
        x = np.random.default_rng(1729).normal(size=(100, 4))
        return x, x @ np.array([1., -2., 3., .5]) + 17

    def test_recovers_synthetic_linear_contrast(self):
        x, y = self.fixture()
        model = contrast.fit_contrast(x, y, alpha=1e-8)
        np.testing.assert_allclose(contrast.predict(x, model), y, atol=1e-6)

    def test_collinear_bands_remain_finite(self):
        x, y = self.fixture()
        x[:, 1] = x[:, 0]
        model = contrast.fit_contrast(x, y)
        self.assertTrue(np.isfinite(contrast.predict(x, model)).all())

    def test_prediction_does_not_refit_from_target_pixels(self):
        x, y = self.fixture()
        model = contrast.fit_contrast(x, y)
        before = copy.deepcopy(model)
        contrast.predict(x * 10, model)
        self.assertEqual(model, before)

    def test_flat_band_is_rejected(self):
        x, y = self.fixture()
        x[:, 0] = 1
        with self.assertRaisesRegex(ValueError, "Uninformative"):
            contrast.fit_contrast(x, y)

    def test_nan_or_invalid_alpha_is_rejected(self):
        x, y = self.fixture()
        for alpha in (0, -1, float("nan")):
            with self.assertRaisesRegex(ValueError, "Invalid"):
                contrast.fit_contrast(x, y, alpha=alpha)
        x[0, 0] = np.nan
        with self.assertRaisesRegex(ValueError, "Invalid"):
            contrast.fit_contrast(x, y)

    def test_recorded_boxes_include_orientation_reversal(self):
        self.assertEqual(contrast.component_box(contrast.SOURCE_BOXES["selection_line1"]), (200, 199, 457, 251))
        self.assertEqual(contrast.component_box(contrast.SOURCE_BOXES["uncertain_line2_band"]), (175, 121, 1257, 198))


if __name__ == "__main__":
    unittest.main()
