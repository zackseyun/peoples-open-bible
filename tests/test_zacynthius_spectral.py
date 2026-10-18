import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest

try:
    import cv2
    import numpy as np
    from PIL import Image
except ImportError:
    cv2 = None

if cv2 is not None:
    path = Path(__file__).resolve().parents[1] / "tools/textual_restoration/probe_zacynthius_spectral.py"
    spec = importlib.util.spec_from_file_location("pilot", path)
    pilot = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pilot)


@unittest.skipIf(cv2 is None, "Spectral pilot requires OpenCV, NumPy and Pillow")
class AlignmentTests(unittest.TestCase):
    def exposure_rows(self, prefix):
        suffixes = ["MB530GN_005.jpg"] + [f"W_test_{i}.jpg" for i in range(41)]
        suffixes += [f"TX_test_{i}.jpg" for i in range(9)]
        return [{"archive_member": f"{prefix}/{prefix}+{suffix}",
                 "local_file": f"{prefix}+{suffix}"} for suffix in suffixes]

    def test_selects_reference_for_each_supported_folio(self):
        for folio, prefix in pilot.FOLIOS.items():
            selected, reference, name = pilot.select_exposures(self.exposure_rows(prefix), folio)
            self.assertEqual(len(selected), 42)
            self.assertEqual(name, prefix + "+MB530GN_005.jpg")
            self.assertEqual(reference["local_file"], name)

    def test_wrong_folio_is_rejected_before_image_processing(self):
        with self.assertRaisesRegex(ValueError, "modern folio 164v"):
            pilot.select_exposures(self.exposure_rows("00057-R"), "164v")

    def test_duplicate_exposure_is_rejected(self):
        rows = self.exposure_rows("00164-V")
        rows[-1] = rows[0]
        with self.assertRaisesRegex(ValueError, "51 distinct"):
            pilot.select_exposures(rows, "164v")

    def test_wrong_band_family_count_is_rejected(self):
        rows = self.exposure_rows("00164-V")
        rows[-1] = {key: value.replace("+TX_test", "+W_extra") for key, value in rows[-1].items()}
        with self.assertRaisesRegex(ValueError, "42 prespecified"):
            pilot.select_exposures(rows, "164v")

    def fixture(self):
        rng = np.random.default_rng(1729)
        points = np.float32([(x, y) for x in np.linspace(300, 1200, 10)
                            for y in np.linspace(250, 1700, 10)])
        descriptors = rng.normal(size=(len(points), 128)).astype(np.float32)
        return points, descriptors

    def test_recovers_known_small_translation(self):
        points, descriptors = self.fixture()
        matrix, report = pilot.fit(points - np.float32([3, -2]), descriptors, points, descriptors)
        self.assertTrue(report["passed"])
        np.testing.assert_allclose(matrix[:, 2], [3, -2], atol=1e-3)

    def test_large_scale_is_rejected(self):
        points, descriptors = self.fixture()
        matrix, report = pilot.fit(points / 1.05, descriptors, points, descriptors)
        self.assertIsNone(matrix)
        self.assertFalse(report["passed"])

    def test_held_out_bad_matches_are_not_hidden_by_fit(self):
        points, descriptors = self.fixture()
        moved = points.copy()
        moved[1::2] += np.float32([35, 0])
        matrix, report = pilot.fit(moved, descriptors, points, descriptors)
        self.assertIsNone(matrix)
        self.assertGreater(report["p95_error_px"], 30)

    def test_missing_descriptors_are_rejected(self):
        matrix, report = pilot.fit([], None, [], None)
        self.assertIsNone(matrix)
        self.assertFalse(report["passed"])

    def test_flat_image_does_not_fabricate_features(self):
        points, descriptors = pilot.features(np.zeros((2044, 1533), np.uint8), None)
        self.assertEqual(len(points), 0)
        self.assertIsNone(descriptors)

    def test_wrong_input_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            (source / "image.jpg").write_bytes(b"not an image")
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                pilot.read_verified(source, {"local_file": "image.jpg", "sha256": "0" * 64})

    def test_wrong_image_geometry_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            path = source / "image.jpg"
            Image.new("L", (10, 10)).save(path)
            with self.assertRaisesRegex(ValueError, "grayscale derivatives"):
                pilot.read_verified(source, {"local_file": path.name,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})

    def test_source_path_escape_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "basename"):
            pilot.read_verified(Path("."), {"local_file": "../outside.jpg"})


if __name__ == "__main__":
    unittest.main()
