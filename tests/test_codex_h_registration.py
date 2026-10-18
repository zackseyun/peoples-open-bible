"""Exercise the successful-fit branch without manuscript or expected text."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

try:
    import cv2
    import numpy as np
    from PIL import Image
except ImportError:
    cv2 = None

SCRIPT = Path(__file__).resolve().parents[1] / "tools/textual_restoration/register_codex_h_pair.py"


@unittest.skipIf(cv2 is None, "image dependencies are optional")
class CodexHRegistrationTests(unittest.TestCase):
    def run_pair(self, array):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, value in [("2v", array[:, ::-1]), ("3r", 255-array)]:
                folder = root / f"codex-h-{name}-overview"
                folder.mkdir()
                Image.fromarray(value).convert("RGB").save(folder / "assembled.png")
            run = subprocess.run([sys.executable, str(SCRIPT), "--work-dir", str(root)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            return json.loads((root / "codex-h-pair-registration/report.json").read_text())

    def test_alternating_match_slices_fit_successfully(self):
        array = np.random.default_rng(73).integers(0, 256, size=(400, 400), dtype=np.uint8)
        report = self.run_pair(array)
        self.assertGreaterEqual(report["matches"], 40)
        self.assertTrue(report["passes_navigation_gate"])
        self.assertLess(report["heldout_p95"], .01)

    def test_blank_images_are_not_registered(self):
        report = self.run_pair(np.zeros((400, 400), dtype=np.uint8))
        self.assertEqual(report["matches"], 0)
        self.assertFalse(report["accepted_transform"])
        self.assertEqual(report["new_letters"], 0)


if __name__ == "__main__":
    unittest.main()
