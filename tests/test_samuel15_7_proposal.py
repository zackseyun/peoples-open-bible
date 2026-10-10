"""Unapplied numeral alternative; accounting is not historical approval."""
import copy
import hashlib
import json
from pathlib import Path
import unittest

import yaml
from jsonschema import Draft202012Validator

from tools import export_mobile_bible
from tools.textual_restoration.verify_source_composition import normalized, verify

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "sources/textual_restoration/"
COMPARISON = PREFIX + "comparisons/samuel15_7_numeral.2026-10-10.v1.json"
CONTRACT = PREFIX + "comparisons/samuel15_7_review_contract.2026-10-10.v1.json"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads((ROOT / path).read_text())


class Samuel157ProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.comparison, cls.contract = load(COMPARISON), load(CONTRACT)
        cls.bundle = load(PREFIX + "applications/samuel15_7_composition.2026-10-10.v1.json")
        entry = cls.bundle["entries"][0]
        cls.candidate = load(entry["candidate"]["path"])
        cls.before = yaml.safe_load((ROOT / entry["baseline"]["path"]).read_text())

    def test_exact_frozen_inputs_and_context(self):
        for pin in self.contract["inputs"]:
            self.assertEqual(digest((ROOT / pin["path"]).read_bytes()), pin["sha256"], pin["path"])
        self.assertEqual(len(self.comparison["context_pins"]), 76)
        for path, expected in self.comparison["context_pins"].items():
            self.assertEqual(digest((ROOT / path).read_bytes()), expected, path)
        self.assertEqual(self.contract["preflight"]["export"]["changed_units"], [[15, 7]])
        self.assertEqual(self.contract["preflight"]["export"]["non_target_count"], 694)

    def test_composition_and_proposal_only_schema(self):
        result = verify(ROOT, self.bundle)
        self.assertTrue(result["composition_verified"])
        self.assertFalse(result["editorial_approval"])
        self.assertFalse(result["canonical_change_applied"])
        self.assertEqual(self.candidate["source"]["text"],
                         normalized(self.before["source"]["text"]).replace("ארבעים שנה", "ארבע שנים", 1))
        self.assertEqual(self.bundle["entries"][0]["patches"],
                         [{"start": 9, "before": "ארבעים שנה", "after": "ארבע שנים", "evidence": [0, 1]}])
        schema = load("schema/verse.schema.json")
        canonical = json.dumps(schema, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(digest(canonical), self.contract["canonical_schema_sha256"])
        self.assertNotIn("POB-critical-draft", schema["properties"]["source"]["properties"]["edition"]["enum"])
        proposal = copy.deepcopy(schema)
        proposal["properties"]["source"]["properties"]["edition"]["enum"].append("POB-critical-draft")
        raw = json.dumps(proposal, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(digest(raw), self.contract["proposal_schema_sha256"])
        Draft202012Validator(proposal).validate(self.candidate)
        errors = list(Draft202012Validator(schema).iter_errors(self.before))
        self.assertTrue(any(e.validator == "required" and "ai_draft" in e.message for e in errors))
        malformed = copy.deepcopy(self.bundle)
        malformed["entries"][0]["patches"][0]["after"] = "ארבע"
        with self.assertRaisesRegex(ValueError, "Unexplained source change"):
            verify(ROOT, malformed)

    def test_no_fabricated_original_provenance(self):
        self.assertNotIn("ai_draft", self.before)
        self.assertEqual(self.candidate["revisions"][:-1], self.before["revisions"])
        self.assertNotIn("revision_pass", self.candidate)
        self.assertEqual(self.candidate["cross_check"], {"status": "needs_review"})
        self.assertEqual(self.candidate["status"], "draft")
        self.assertEqual({x["field"]: x["value"] for x in self.candidate["review_history"]},
                         {f: self.before[f] for f in ["source", "translation", "revision_pass"]})
        self.assertTrue(all(x["certifies_this_candidate"] is False for x in self.candidate["review_history"]))
        self.assertIn("ai_draft", self.candidate["baseline_absent_fields"])
        metadata = self.candidate["ai_draft"]
        self.assertEqual(metadata["model_version"], "unavailable-in-runtime")
        self.assertFalse(metadata["full_conversational_input_hash_available"])
        self.assertEqual(digest((ROOT / metadata["instruction_ref"]).read_bytes()), metadata["prompt_sha256"])
        payload = {f: self.candidate[f] for f in ["source", "translation"]}
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(digest(raw), metadata["output_hash"])

    def test_actual_preservation_and_unapplied_reader_note(self):
        for target in self.comparison["qdr"]["targets"]:
            self.assertFalse(target["numeral_preserved"])
            self.assertFalse(target["year_preserved"])
            self.assertTrue(target["full_line"].startswith("["))
            self.assertIn("ארבע שנים", target["full_line"])
        self.assertFalse(self.comparison["qdr"]["fresh_manuscript_pixels_read"])
        self.assertFalse(self.comparison["qdr"]["numeral_geometry_verified"])
        text = self.candidate["translation"]["text"]
        self.assertEqual(text.replace("four years[a]", "forty years"), self.before["translation"]["text"])
        self.assertNotIn("since reconciliation", text)
        out = export_mobile_bible._export_record_verse(7, self.candidate)
        self.assertEqual(out["footnotes"], self.candidate["translation"]["footnotes"])
        self.assertIn("not surviving letters", out["footnotes"][0]["text"])
        for flag in ["source_selection_approved", "full_record_editorially_approved",
                     "canonical_change_applied", "publication_ready", "canon_changed"]:
            self.assertFalse(self.contract[flag])
            self.assertFalse(self.comparison["decisions"][flag])
        self.assertFalse(self.candidate["restoration_draft"]["approved"])

    def test_exact_hold_cannot_be_relabelled_approval(self):
        path = PREFIX + "comparisons/samuel15_7_exact_review.2026-10-10.v1.json"
        raw = (ROOT / path).read_bytes()
        self.assertEqual(digest(raw), "a56dd56c7426a47bf176c5e179f80052edbec3f09ee3ed52b57240ec9b797f40")
        review = json.loads(raw)
        self.assertEqual(digest((ROOT / CONTRACT).read_bytes()), review["contract"]["sha256"])
        self.assertEqual(review["inputs"], self.contract["inputs"])
        self.assertTrue(review["decisions"]["source_preference"].startswith("HOLD"))
        for flag in ["source_selection_approved", "full_record_editorially_approved",
                     "canonical_change_applied", "publication_ready", "canon_changed"]:
            self.assertFalse(review["decisions"][flag])
        self.assertIn("unchanged inputs", review["stopping_rule"])


if __name__ == "__main__":
    unittest.main()
