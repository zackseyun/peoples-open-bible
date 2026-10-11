"""Actual target consultation is not source or translation approval."""
import hashlib
import json
from pathlib import Path
import subprocess
import unittest

from jsonschema import Draft202012Validator, FormatChecker
from tools.textual_restoration.validate_ot_witness_registry import validate

ROOT = Path(__file__).resolve().parents[1]
RECORD = "sources/textual_restoration/comparisons/ecclesiastes8_10_ctat.2026-10-10.v1.json"
REGISTRY = "sources/textual_restoration/ot_witness_registry.v1.json"
BASE = "73978a840df59022c248c423673c8d3c5c12b97d"


class CTATComparisonTests(unittest.TestCase):
    def test_new_evidence_review_does_not_upgrade_the_old_candidate(self):
        review = json.loads((ROOT / "sources/textual_restoration/comparisons/ecclesiastes8_10_ctat_review.2026-10-10.v1.json").read_text())
        for pin in review["inputs"]:
            self.assertEqual(hashlib.sha256((ROOT / pin["path"]).read_bytes()).hexdigest(), pin["sha256"], pin["path"])
        self.assertEqual(review["review_count"], 1)
        self.assertFalse(review["candidate_identity_blinded"])
        self.assertEqual(review["decisions"]["research_accuracy"], "PASS_WITH_SCOPE_LIMITS")
        self.assertEqual(review["decisions"]["earliest_hebrew_source_selection"], "HOLD")
        self.assertEqual(review["decisions"]["full_english_application"], "HOLD")
        self.assertFalse(review["decisions"]["canonical_change_applied"])
        self.assertFalse(review["registry_review_claimed"])

    def test_target_consultation_closes_only_its_own_gate(self):
        r = json.loads((ROOT / RECORD).read_text())
        self.assertTrue(r["source"]["target_entry_read_in_full"])
        self.assertEqual(r["source"]["target_printed_pages"], [841, 842, 843, 844])
        self.assertEqual(r["source"]["target_pdf_pages"], [870, 871, 872, 873])
        self.assertEqual((r["source"]["bytes"], r["source"]["pages"]), (8114592, 1009))
        self.assertTrue(all(v is False for v in r["remaining_access_gates"].values()))
        for pin in r["pinned_existing_inputs"]:
            self.assertEqual(hashlib.sha256((ROOT / pin["path"]).read_bytes()).hexdigest(), pin["sha256"], pin["path"])

    def test_confidence_votes_and_source_arguments_are_not_new_copies(self):
        r = json.loads((ROOT / RECORD).read_text())
        self.assertEqual(r["published_outcome"]["retained_word"], "וישתכחו")
        self.assertEqual(r["published_outcome"]["committee_votes"], {"B": 5, "C": 1})
        self.assertFalse(r["published_outcome"]["votes_are_manuscript_support_counts"])
        self.assertIsNone(r["published_outcome"]["reported_hebrew_copy_counts"]["verified_independent_total"])
        self.assertEqual(r["root_decisions"]["source_selection"], "HOLD")
        self.assertEqual(r["root_decisions"]["full_english_application"], "HOLD")
        self.assertFalse(any(row["approved_by_this_record"] for row in r["comparison_rows"]))
        for key in ("canonical_change_applied", "reader_change_applied", "source_schema_changed", "fresh_manuscript_transcription", "canon_changed"):
            self.assertFalse(r["root_decisions"][key])

    def test_one_apparatus_registration_preserves_existing_forty_records(self):
        old_raw = subprocess.check_output(["git", "show", BASE + ":" + REGISTRY], cwd=ROOT)
        self.assertEqual(hashlib.sha256(old_raw).hexdigest(), "4cc204ff10a0431556934522497a8db538042349890e0263a8ba5cc7809a35a2")
        old = json.loads(old_raw)
        current = json.loads((ROOT / REGISTRY).read_text())
        old_entries = {w["id"]: w for w in old["witnesses"]}
        current_entries = {w["id"]: w for w in current["witnesses"]}
        self.assertEqual((len(old_entries), len(current_entries)), (40, 41))
        self.assertEqual(set(current_entries) - set(old_entries), {"ctat-wisdom-volume5"})
        for wid, entry in old_entries.items():
            self.assertEqual(current_entries[wid], entry, wid)
        added = current_entries["ctat-wisdom-volume5"]
        self.assertEqual(added["witness_class"], "critical-apparatus")
        self.assertEqual(added["coverage_status"], "partial-map")
        self.assertEqual(added["restoration_suitability"], "none")
        self.assertEqual(added["access"][0]["rights_status"], "study-only")
        schema = json.loads((ROOT / "schemas/ot-witness-registry.schema.json").read_text())
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(current)
        self.assertEqual(validate(current), [])


if __name__ == "__main__":
    unittest.main()
