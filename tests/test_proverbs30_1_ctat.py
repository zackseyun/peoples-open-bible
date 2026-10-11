"""Protect the distinction between published arguments and an applied reading."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECORD = "sources/textual_restoration/comparisons/proverbs30_1_ctat.2026-10-10.v1.json"
REVIEW = "sources/textual_restoration/comparisons/proverbs30_1_ctat_review.2026-10-10.v1.json"


class ProverbsCTATTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads((ROOT / RECORD).read_text())

    def test_live_source_and_existing_records_are_unchanged(self):
        self.assertEqual(len(self.record["pinned_existing_inputs"]), 10)
        for pin in self.record["pinned_existing_inputs"]:
            self.assertEqual(hashlib.sha256((ROOT / pin["path"]).read_bytes()).hexdigest(),
                             pin["sha256"], pin["path"])

    def test_the_complete_entry_is_distinct_from_its_repetition_grade(self):
        source = self.record["source"]
        self.assertEqual(source["target_printed_pages"], [773, 774, 775])
        self.assertEqual(source["target_pdf_pages"], [802, 803, 804])
        self.assertTrue(source["target_entry_read_in_full"])
        judgment = self.record["published_judgment"]
        self.assertEqual(judgment["committee_grades"], {"D": 1, "C": 5})
        self.assertFalse(judgment["votes_are_manuscript_counts"])
        self.assertTrue(judgment["corruption_marker_present"])

    def test_ability_exhaustion_and_names_are_not_collapsed(self):
        rows = {r["id"]: r for r in self.record["interpretations"]}
        self.assertEqual(rows["pob_note"]["final_analysis"], "exhaustion")
        self.assertEqual(rows["ctat_primitive"]["final_analysis"], "ability_success")
        self.assertFalse(rows["ctat_primitive"]["purpose_syntax_established"])
        self.assertTrue(rows["ctat_accepted"]["Ithiel_retained"])
        self.assertFalse(any(row["approved_here"] for row in rows.values()))
        greek = self.record["greek_attributions"]
        self.assertEqual(greek[0]["reported_intermediaries"], ["HP252", "Morin"])
        self.assertEqual(greek[1]["reported_intermediaries"], ["Morin"])
        self.assertFalse(any(row["direct_manuscript_inspected"] for row in greek))
        self.assertFalse(self.record["source_reasoning"]["negative_authorized_by_controls"])

    def test_one_review_does_not_apply_source_or_english(self):
        review = json.loads((ROOT / REVIEW).read_text())
        for pin in review["inputs"]:
            self.assertEqual(hashlib.sha256((ROOT / pin["path"]).read_bytes()).hexdigest(),
                             pin["sha256"], pin["path"])
        self.assertEqual(review["review_count"], 1)
        self.assertFalse(review["candidate_identity_blinded"])
        self.assertEqual(review["decisions"]["research_accuracy"], "PASS_WITH_SCOPE_LIMITS")
        self.assertEqual(review["decisions"]["source_priority"], "HOLD")
        self.assertEqual(review["decisions"]["full_english_application"], "HOLD")
        for decision in (self.record["decisions"], review["decisions"]):
            for key in ("canonical_change_applied", "reader_change_applied", "canon_changed"):
                self.assertFalse(decision[key])


if __name__ == "__main__":
    unittest.main()
