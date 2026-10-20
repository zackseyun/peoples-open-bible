import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

try:
    import numpy as np
    from PIL import Image
    from PIL.TiffImagePlugin import ImageFileDirectory_v2
except ImportError:
    np = None

if np is not None:
    SPEC = importlib.util.spec_from_file_location(
        "mercati", Path(__file__).resolve().parents[1] / "tools/textual_restoration/probe_mercati_spectral.py")
    probe = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(probe)


class Response(io.BytesIO):
    status = 206

    def __init__(self, data, start, end, total, etag="same"):
        super().__init__(data)
        self.headers = {"Content-Range": f"bytes {start}-{end}/{total}", "ETag": etag}


@unittest.skipIf(np is None, "Requires NumPy and Pillow")
class MercatiTests(unittest.TestCase):
    def test_constant_stretch_is_finite(self):
        result, limits = probe.stretch(np.ones((3, 4)))
        self.assertEqual(limits, [1, 1])
        np.testing.assert_array_equal(result, 127)

    def test_stretch_keeps_source_and_orders_intensities(self):
        pixels = np.array([[0, 100, 200, 300]], dtype=">u2")
        before = pixels.copy()
        result, _ = probe.stretch(pixels, 0, 100)
        np.testing.assert_array_equal(result, [[0, 85, 170, 255]])
        np.testing.assert_array_equal(pixels, before)

    def test_nonfinite_pixels_rejected(self):
        with self.assertRaises(ValueError):
            probe.stretch([0, np.nan])

    def test_crop_uses_xywh_and_is_a_copy(self):
        source = np.arange(30).reshape(5, 6)
        cut = probe.crop(source, [2, 1, 3, 2])
        np.testing.assert_array_equal(cut, [[8, 9, 10], [14, 15, 16]])
        cut[0, 0] = -1
        self.assertEqual(source[1, 2], 8)

    def test_invalid_crops_rejected(self):
        for box in ([-1, 0, 1, 1], [0, 0, 0, 1], [3, 2, 2, 2], [0.5, 0, 1, 1]):
            with self.subTest(box=box), self.assertRaises(ValueError):
                probe.crop(np.zeros((3, 4)), box)

    def test_missing_compression_tag_means_tiff_default(self):
        # The actual provider TIFF omits the Compression tag; TIFF defines default 1.
        pixels = np.arange(300000, dtype=np.uint16).reshape(500, 600)
        tags = ImageFileDirectory_v2(prefix=b"MM")
        for key, value in {256: 600, 257: 500, 258: (16,), 262: 1,
                           273: (0,), 278: 500, 279: (pixels.size * 2,)}.items():
            tags[key] = value
        header = b"MM\x00*\x00\x00\x00\x08" + tags.tobytes(8)
        payload = header + pixels.astype(">u2").tobytes()

        def open_range(request, timeout):
            start, end = map(int, request.get_header("Range").split("=")[1].split("-"))
            return Response(payload[start:end + 1], start, end, len(payload))

        with patch.object(probe.urllib.request, "urlopen", side_effect=open_range):
            result, receipt = probe.remote_crop("https://example.test/image.tif", [13, 121, 17, 10])
        np.testing.assert_array_equal(result, pixels[121:131, 13:30])
        self.assertFalse(receipt["full_capture_downloaded"])
        self.assertIsNone(receipt["full_capture_sha256"])
        self.assertEqual(len(receipt["range_receipts"]), 2)

    def test_ignored_range_is_rejected(self):
        response = Response(b"x" * 65536, 0, 65535, 100000)
        response.status = 200
        with patch.object(probe.urllib.request, "urlopen", return_value=response):
            with self.assertRaises(ValueError):
                probe.RangeReader("https://example.test").read(16)

    def test_source_change_is_rejected(self):
        responses = [Response(b"x" * 65536, 0, 65535, 100000),
                     Response(b"y" * 10, 70000, 70009, 100000, etag="changed")]
        reader = probe.RangeReader("https://example.test")
        with patch.object(probe.urllib.request, "urlopen", side_effect=responses):
            reader.read(16)
            reader.seek(70000)
            with self.assertRaises(ValueError):
                reader.read(10)

    def test_rgb_separation_is_navigation_only_and_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "control.png"
            pixels = np.array([[[30, 10, 10], [10, 30, 30]]], dtype=np.uint8)
            Image.fromarray(pixels).save(path)
            result, report = probe.inspect(path, [0, 0, 2, 1], "published-red-navigation")
            np.testing.assert_array_equal(result, [[255, 0]])
            self.assertEqual(report["mode_requested"], "published-red-navigation")

    def test_rgb_crop_and_rotation_preserve_sample_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "control.png"
            pixels = np.arange(36, dtype=np.uint8).reshape(3, 4, 3)
            Image.fromarray(pixels).save(path)
            result, report = probe.inspect(path, [1, 0, 2, 3], "rgb", 2)
            np.testing.assert_array_equal(result, np.rot90(pixels[:, 1:3], 2))
            self.assertIsNone(report["display_limits"])

    def test_linear_fit_excludes_test_region_and_preserves_inputs(self):
        nuisance = np.arange(1200).reshape(30, 40).astype(float)
        signal = nuisance * 3 + 2
        signal[10:15, 12:18] -= 100
        before = signal.copy()
        mask = np.zeros(signal.shape, dtype=bool)
        mask[:5], mask[-5:] = True, True
        result, coefficients = probe.linear_residual(signal, nuisance, mask)
        np.testing.assert_allclose(coefficients, [3, 2], atol=1e-10)
        np.testing.assert_allclose(result[10:15, 12:18], -100, atol=1e-10)
        np.testing.assert_allclose(result[mask], 0, atol=1e-10)
        np.testing.assert_array_equal(signal, before)

    def test_uninformative_linear_calibration_rejected(self):
        with self.assertRaises(ValueError):
            probe.linear_residual(np.ones((3, 3)), np.ones((3, 3)), np.ones((3, 3)))

    def test_existing_fetch_output_is_not_overwritten(self):
        import sys
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.bin"
            path.write_bytes(b"original")
            args = ["probe", "--url", "https://example.test", "--box", "0", "0", "1", "1", "--output", str(path)]
            with patch.object(sys, "argv", args), patch.object(probe.urllib.request, "urlopen") as network:
                with self.assertRaises(ValueError):
                    probe.fetch_main()
                network.assert_not_called()
            self.assertEqual(path.read_bytes(), b"original")


if __name__ == "__main__":
    unittest.main()
