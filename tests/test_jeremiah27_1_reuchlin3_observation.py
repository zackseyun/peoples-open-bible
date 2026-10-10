"""Raw-image provenance and claim boundaries, not palaeographic certification."""
import hashlib
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
OBSERVATION = "sources/textual_restoration/controls/2026-10-10-reuchlin3-jer27/observation.v1.json"
OBSERVATION_SHA = "3cf630bb21af2076074f4a52de05c4ed5288fee261fb2256d6f0a0abebd53144"


class Reuchlin3ObservationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / OBSERVATION).read_bytes()
        cls.record = json.loads(cls.raw)

    def test_raw_capture_and_exact_parent_provenance(self):
        r = self.record
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), OBSERVATION_SHA)
        image = (ROOT / r["surface"]["raw_path"]).read_bytes()
        self.assertEqual(len(image), r["surface"]["bytes"])
        self.assertEqual(hashlib.sha256(image).hexdigest(), r["surface"]["sha256"])
        self.assertTrue(image.startswith(b"\xff\xd8"))
        self.assertTrue(image.endswith(b"\xff\xd9"))
        self.assertEqual(r["surface"]["dimensions"], [4049, 4559])
        self.assertEqual(r["surface"]["folio"], "264r")
        self.assertEqual(r["surface"]["holding_image_id"], "3396662")
        parent = subprocess.check_output(["git", "show",
            r["baseline_revision"] + ":" + r["parent_comparison"]], cwd=ROOT)
        self.assertEqual(hashlib.sha256(parent).hexdigest(), r["parent_sha256"])

    def test_exploratory_observations_do_not_recover_an_earlier_state(self):
        limits = self.record["limits"]
        for field in ["unblinded", "context_informed", "same_family_machine_observers"]:
            self.assertTrue(limits[field])
        for field in ["two_family_blinded_workflow_completed", "calibration_certified",
                      "accepted_transcription", "imagegen_used", "generative_restoration_used",
                      "published_initial_reading_independently_verified",
                      "earlier_zedekiah_report_refuted", "chronological_preference_used",
                      "canonical_source_changed", "canonical_english_changed",
                      "priority_reopened_by_this_image", "canon_changed", "novel_reading_demonstrated"]:
            self.assertFalse(limits[field], field)
        observations = self.record["observations"]
        self.assertIsNone(observations["earlier_king_reading"])
        self.assertFalse(observations["earlier_state_recovered"])
        self.assertFalse(observations["correction_hand_identified"])
        self.assertFalse(observations["correction_hand_dated"])

    def test_disagreement_language_and_corrected_extent_are_preserved(self):
        r = self.record
        o = r["observations"]
        self.assertEqual(o["tentative_reader_spelling"], "יהויקם")
        self.assertEqual(o["tentative_root_spelling"], "יהויקים")
        self.assertIn("unresolved", o["exact_spelling_disagreement"])
        self.assertTrue(o["middle_heading_phrase_visible"])
        self.assertFalse(o["middle_phrase_omission_claimed"])
        self.assertIn("Aramaic", o["targum_language"])
        self.assertFalse(r["navigation"]["reference_text_used_as_ink"])
        self.assertIsNone(r["catalog"]["manifest_license_field"])
        self.assertIn("Public Domain Mark", r["catalog"]["rights_catalog"])
        self.assertEqual(len(r["observation_history"]), 2)
        self.assertIn("Withdrawn", r["observation_history"][0]["disposition"])
        width, height = r["surface"]["dimensions"]
        for crop in r["derivatives"]:
            x, y, w, h = crop["region"]
            self.assertTrue(0 <= x < x + w <= width)
            self.assertTrue(0 <= y < y + h <= height)
            self.assertIn("3396662", crop["url"])


if __name__ == "__main__":
    unittest.main()
