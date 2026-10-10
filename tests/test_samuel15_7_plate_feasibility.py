"""Receipt consistency, not manuscript decipherment or editorial approval."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "sources/textual_restoration/comparisons/samuel15_7_plate_feasibility.2026-10-10.v1.json"


class PlateFeasibilityTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(PACKET.read_text())

    def test_unchanged_frozen_candidate_review_and_canonical(self):
        decision = self.data["decision"]
        for key, path in (
            ("prior_exact_review_sha256", "sources/textual_restoration/comparisons/samuel15_7_exact_review.2026-10-10.v1.json"),
            ("prior_candidate_sha256", "sources/textual_restoration/applications/samuel15_7_candidate.2026-10-10.v1.json"),
            ("canonical_baseline_sha256", "translation/ot/2_samuel/015/007.yaml"),
        ):
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), decision[key])
        self.assertEqual(decision["historical_priority"], "HOLD unchanged")
        for key in ("new_numeral_ink_recovered", "imagegen_executed", "canonical_application", "canon_change"):
            self.assertIs(decision[key], False)

    def test_no_measurement_or_recovery_is_claimed(self):
        for key, value in self.data["geometry"].items():
            if key != "limits":
                self.assertIs(value, False, key)
        limits = self.data["image_limits"]
        self.assertEqual(limits["principal_embedded_raster_pixels"], [608, 800])
        self.assertFalse(limits["rendering_adds_manuscript_resolution"])
        self.assertFalse(limits["montage_white_space_is_measured_physical_gap"])
        for phrase in self.data["candidate_phrases"]:
            self.assertEqual(len(phrase["hebrew"].replace(" ", "")), phrase["letters_excluding_space"])

    def test_actual_plate_and_transcription_locators(self):
        self.assertEqual([(row.get("plate"), row.get("pdf_page")) for row in self.data["inspected"][:2]],
                         [("XIX", 321), ("XXVI", 331)])
        for row in self.data["inspected"]:
            for key, value in row.items():
                if "pdf_page" in key:
                    self.assertLessEqual(value, self.data["source"]["pdf_pages"])


if __name__ == "__main__":
    unittest.main()
