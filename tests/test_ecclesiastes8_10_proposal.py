"""Ecclesiastes proposal is research, not canonical source selection."""
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
COMPARISON = PREFIX + "comparisons/ecclesiastes8_10_forgotten_praise.2026-10-10.v1.json"
CONTRACT = PREFIX + "comparisons/ecclesiastes8_10_review_contract.2026-10-10.v1.json"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def load(path):
    return json.loads((ROOT / path).read_text())


class Ecclesiastes810ProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.comparison, cls.contract = load(COMPARISON), load(CONTRACT)
        cls.bundle = load(PREFIX + "applications/ecclesiastes8_10_composition.2026-10-10.v1.json")
        cls.entry = cls.bundle["entries"][0]
        cls.candidate = load(cls.entry["candidate"]["path"])
        cls.before = yaml.safe_load((ROOT / cls.entry["baseline"]["path"]).read_text())

    def test_exact_inputs_context_and_bounded_export(self):
        for pin in self.contract["inputs"]:
            self.assertEqual(digest((ROOT / pin["path"]).read_bytes()), pin["sha256"], pin["path"])
        self.assertEqual(len(self.comparison["context_pins"]), 22)
        for path, sha in self.comparison["context_pins"].items():
            self.assertEqual(digest((ROOT / path).read_bytes()), sha, path)
        out = self.contract["preflight"]["export"]
        self.assertEqual((out["chapters"], out["units"], out["non_target_count"]), (12, 222, 221))
        self.assertEqual(out["changed_units"], [[8, 10]])
        self.assertTrue(self.contract["preflight"]["immutable_baseline_archive_verified"])

    def test_exact_composition_and_proposal_only_schema(self):
        result = verify(ROOT, self.bundle)
        self.assertTrue(result["composition_verified"])
        self.assertFalse(result["editorial_approval"])
        self.assertFalse(result["canonical_change_applied"])
        base = normalized(self.before["source"]["text"])
        self.assertEqual(self.candidate["source"]["text"], base.replace("וישתכחו", "וישתבחו", 1))
        self.assertEqual(self.entry["patches"], [{
            "start": base.index("וישתכחו"), "before": "וישתכחו", "after": "וישתבחו", "evidence": [0, 1]}])
        bad = copy.deepcopy(self.bundle)
        bad["entries"][0]["patches"][0]["after"] = "ישתבחו"
        with self.assertRaisesRegex(ValueError, "Unexplained source change"):
            verify(ROOT, bad)
        schema = load("schema/verse.schema.json")
        self.assertEqual(digest(encoded(schema)), self.contract["canonical_schema_sha256"])
        self.assertNotIn("POB-critical-draft", schema["properties"]["source"]["properties"]["edition"]["enum"])
        proposal = copy.deepcopy(schema)
        proposal["properties"]["source"]["properties"]["edition"]["enum"].append("POB-critical-draft")
        self.assertEqual(digest(encoded(proposal)), self.contract["proposal_schema_sha256"])
        Draft202012Validator(proposal).validate(self.candidate)
        errors = list(Draft202012Validator(schema).iter_errors(self.before))
        self.assertEqual([(e.validator, list(e.absolute_path)) for e in errors], [("enum", ["status"])])
        self.assertFalse(self.contract["preflight"]["baseline_schema_valid"])
        self.assertEqual(self.before["status"], "revised")

    def test_archived_original_metadata_and_truthful_new_generation(self):
        candidate = self.candidate
        self.assertEqual(candidate["revisions"][:-1], self.before["revisions"])
        self.assertNotIn("revision_pass", candidate)
        self.assertNotIn("source_audit", candidate)
        self.assertEqual(candidate["cross_check"], {"status": "needs_review"})
        self.assertEqual(candidate["status"], "draft")
        archive = candidate["review_history"][0]
        self.assertFalse(archive["certifies_this_candidate"])
        self.assertEqual(archive["baseline"]["path"], self.entry["baseline"]["path"])
        self.assertEqual(archive["baseline"]["sha256"], digest((ROOT / archive["baseline"]["path"]).read_bytes()))
        self.assertEqual(archive["baseline"]["git_commit"], "d6ffb4c4919da9d6f67e6737927442b8775113b0")
        self.assertEqual(set(archive["fields_archived_by_reference"]), {
            "source", "translation", "ai_draft", "cross_check", "revision_pass", "source_audit",
            "status", "theological_decisions"})
        metadata = candidate["ai_draft"]
        self.assertEqual(metadata["model_version"], "unavailable-in-runtime")
        self.assertFalse(metadata["full_conversational_input_hash_available"])
        self.assertEqual(digest((ROOT / metadata["instruction_ref"]).read_bytes()), metadata["prompt_sha256"])
        self.assertEqual(digest(encoded({f: candidate[f] for f in ["source", "translation"]})), metadata["output_hash"])
        self.assertTrue(candidate["inherited_lexical_decisions_not_newly_verified"])

    def test_attestation_is_not_new_ink_and_english_is_not_passive_praise(self):
        apparatus = self.comparison["hebrew_apparatus"]
        self.assertEqual(apparatus["reported_reading"], "וישתבחו")
        self.assertEqual(apparatus["counter_controls"][:2], [
            {"collection": "Kennicott", "id": 553, "text": "וישתבחו", "marginal_qere": "וישתכחו"},
            {"collection": "De Rossi", "id": 331, "text": "וישתבחו", "marginal_qere": "וישתכחו"}])
        self.assertFalse(apparatus["modern_shelfmark_mapping_verified"])
        self.assertEqual(self.comparison["qdr"]["hits"], [])
        self.assertFalse(self.comparison["qdr"]["target_ink_recovered"])
        self.assertFalse(self.comparison["decisions"]["fresh_manuscript_transcription"])
        text = self.candidate["translation"]["text"]
        self.assertIn("and had boasted[b]", text)
        self.assertNotIn("righteous works", text)
        self.assertNotIn("Gehinnom", text)
        out = export_mobile_bible._export_record_verse(10, self.candidate)
        self.assertEqual(out, self.contract["preflight"]["export"]["target"])
        self.assertEqual(out["footnotes"], self.candidate["translation"]["footnotes"])
        self.assertEqual(out["footnotes"][0], self.before["translation"]["footnotes"][0])
        self.assertEqual(out["footnotes"][2], self.before["translation"]["footnotes"][2])
        for flag in ["source_selection_approved", "full_record_editorially_approved",
                     "canonical_change_applied", "publication_ready", "canon_changed"]:
            self.assertFalse(self.contract[flag])
            self.assertFalse(self.comparison["decisions"][flag])
        self.assertFalse(self.candidate["restoration_draft"]["approved"])

    def test_exact_hold_is_not_source_or_english_approval(self):
        path = PREFIX + "comparisons/ecclesiastes8_10_exact_review.2026-10-10.v1.json"
        raw = (ROOT / path).read_bytes()
        self.assertEqual(digest(raw), "8bcffa4e6d24780282ca6e43cac3b46ea32322321e17771c3aaea3d4fdc3bdc2")
        review = json.loads(raw)
        self.assertEqual(digest((ROOT / CONTRACT).read_bytes()), review["contract"]["sha256"])
        self.assertEqual(review["inputs"], self.contract["inputs"])
        self.assertEqual(review["review_conditions"]["review_count"], 1)
        self.assertFalse(review["review_conditions"]["candidate_identity_blinded"])
        self.assertEqual(review["decisions"]["research_packet"], "PASS_WITH_SCOPE_LIMITS")
        self.assertEqual(review["decisions"]["earliest_attainable_source_selection"], "HOLD")
        self.assertEqual(review["decisions"]["full_record_editorial_application"], "HOLD")
        for flag in ["source_selection_approved", "full_record_editorially_approved",
                     "canonical_change_applied", "publication_ready", "canon_changed"]:
            self.assertFalse(review["decisions"][flag])
        self.assertIn("exact input", review["stopping_rule"])


if __name__ == "__main__":
    unittest.main()
