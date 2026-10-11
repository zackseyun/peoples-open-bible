"""Published reviser reports do not silently approve a Bible text change."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "sources/textual_restoration/comparisons/ecclesiastes8_10_reviser_followup.2026-10-10.v1.json"


class ReviserFollowupTests(unittest.TestCase):
    def test_new_evidence_review_remains_exact_and_held(self):
        review = json.loads((ROOT / "sources/textual_restoration/comparisons/ecclesiastes8_10_reviser_followup_review.2026-10-10.v1.json").read_text())
        for pin in review["inputs"]:
            self.assertEqual(hashlib.sha256((ROOT / pin["path"]).read_bytes()).hexdigest(), pin["sha256"], pin["path"])
        self.assertEqual(review["review_count"], 1)
        self.assertFalse(review["candidate_identity_blinded"])
        self.assertEqual(review["decisions"]["research_accuracy"], "PASS_WITH_SCOPE_LIMITS")
        self.assertEqual(review["decisions"]["earliest_hebrew_source_selection"], "HOLD")
        self.assertEqual(review["decisions"]["full_record_application"], "HOLD")
        self.assertIn("laudentes", review["nonblocking_clarification"])
        self.assertFalse(review["decisions"]["canonical_change_applied"])

    def test_original_candidate_and_hold_are_unchanged(self):
        record = json.loads(RECORD.read_text())
        for key in ("candidate", "historical_review"):
            pin = record[key]
            self.assertEqual(hashlib.sha256((ROOT / pin["path"]).read_bytes()).hexdigest(), pin["sha256"])
        self.assertTrue(record["candidate"]["unchanged"])
        self.assertFalse(record["historical_review"]["receipt_rewritten"])
        self.assertEqual(record["historical_review"]["source_priority"], "HOLD")
        self.assertEqual(record["historical_review"]["full_english_application"], "HOLD")

    def test_reports_and_inference_are_not_new_ink_or_approval(self):
        record = json.loads(RECORD.read_text())
        field, gentry = record["sources"]
        self.assertFalse(field["aquila_theodotion"]["direct_target_greek_glyphs_read"])
        self.assertTrue(field["combined_sigla_identical_wording_not_guaranteed"])
        self.assertFalse(field["fresh_hebrew_attestation"])
        self.assertFalse(gentry["exact_ancient_hebrew_glyphs_established"])
        self.assertFalse(gentry["direct_BHQ_target_consulted"])
        self.assertFalse(gentry["final_2019_target_apparatus_consulted"])
        self.assertTrue(all(not gate["target_read"] for gate in record["access_gates"]))
        for flag in ("source_selection_approved", "full_record_editorially_approved", "canonical_change_applied", "publication_ready", "canon_changed", "fresh_manuscript_transcription"):
            self.assertFalse(record["root_assessment"][flag])


if __name__ == "__main__":
    unittest.main()
