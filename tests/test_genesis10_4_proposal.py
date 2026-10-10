"""Unapplied Genesis D/R research proposal; no canonical source approval."""
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
COMPARISON = PREFIX + "comparisons/genesis10_4_ethnonym.2026-10-10.v1.json"
CONTRACT = PREFIX + "comparisons/genesis10_4_review_contract.2026-10-10.v1.json"
COMPOSITION = PREFIX + "applications/genesis10_4_composition.2026-10-10.v1.json"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads((ROOT / path).read_text())


class Genesis104ProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.comparison, cls.contract = load(COMPARISON), load(CONTRACT)
        cls.bundle = load(COMPOSITION)
        entry = cls.bundle["entries"][0]
        cls.candidate = load(entry["candidate"]["path"])
        cls.before = yaml.safe_load((ROOT / entry["baseline"]["path"]).read_text())
        cls.companion = load(cls.comparison["companion_candidate"])
        cls.parallel = yaml.safe_load((ROOT / "translation/ot/1_chronicles/001/007.yaml").read_text())

    def test_frozen_inputs_and_context(self):
        for pin in self.contract["inputs"]:
            self.assertEqual(digest((ROOT / pin["path"]).read_bytes()), pin["sha256"], pin["path"])
        self.assertEqual(len(self.comparison["context_pins"]), 55)
        for path, expected in self.comparison["context_pins"].items():
            self.assertEqual(digest((ROOT / path).read_bytes()), expected, path)

    def test_exact_composition_not_an_editorial_pass(self):
        result = verify(ROOT, self.bundle)
        self.assertTrue(result["composition_verified"])
        self.assertFalse(result["editorial_approval"])
        self.assertFalse(result["canonical_change_applied"])
        self.assertEqual(self.candidate["source"]["text"],
                         normalized(self.before["source"]["text"]).replace("ודדנים", "ורודנים", 1))
        self.assertEqual(self.candidate["source"]["edition"], "POB-critical-draft")
        self.assertEqual(self.companion["source"], self.parallel["source"])
        schema = load("schema/verse.schema.json")
        self.assertNotIn("POB-critical-draft", schema["properties"]["source"]["properties"]["edition"]["enum"])
        proposal_schema = copy.deepcopy(schema)
        proposal_schema["properties"]["source"]["properties"]["edition"]["enum"].append("POB-critical-draft")
        raw = json.dumps(proposal_schema, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(digest(raw), self.contract["proposal_schema_sha256"])
        Draft202012Validator(proposal_schema).validate(self.candidate)
        Draft202012Validator(schema).validate(self.companion)

    def test_exact_noncertifying_archives_and_generation(self):
        for candidate, before, fields in [
            (self.candidate, self.before,
             ["source", "status", "translation", "lexical_decisions", "revision_pass", "cross_check"]),
            (self.companion, self.parallel,
             ["status", "translation", "revision_pass", "cross_check"]),
        ]:
            self.assertEqual(candidate["ai_draft"], before["ai_draft"])
            self.assertEqual(candidate["revisions"][:-1], before.get("revisions", []))
            history = candidate["review_history"]
            self.assertEqual([x["field"] for x in history], fields)
            self.assertEqual({x["field"]: x["value"] for x in history},
                             {f: before[f] for f in fields})
            self.assertTrue(all(x["certifies_this_candidate"] is False for x in history))
            self.assertEqual(candidate["cross_check"], {"status": "needs_review"})
            self.assertEqual(candidate["status"], "draft")
            self.assertNotIn("revision_pass", candidate)
        for flag in ("approved", "canonical_change_applied", "publication_ready"):
            self.assertFalse(self.candidate["restoration_draft"][flag])
        self.assertEqual([i for i, (a, b) in enumerate(zip(
            self.before["lexical_decisions"], self.candidate["lexical_decisions"])) if a != b], [5])
        self.assertEqual(self.companion["lexical_decisions"], self.parallel["lexical_decisions"])

    def test_reader_markers_and_explicit_no_approval(self):
        for candidate, verse in [(self.candidate, 4), (self.companion, 7)]:
            text = candidate["translation"]["text"]
            self.assertNotIn("Elishah[a]", text)
            self.assertIn("Rodanim[a]", text)
            exported = export_mobile_bible._export_record_verse(
                verse, candidate)
            self.assertEqual(exported["footnotes"], candidate["translation"]["footnotes"])
        for flag in ("source_selection_approved", "full_record_editorially_approved",
                     "canonical_change_applied", "publication_ready"):
            self.assertFalse(self.contract[flag])

    def test_independent_hold_is_not_converted_into_source_approval(self):
        path = PREFIX + "comparisons/genesis10_4_exact_review.2026-10-10.v1.json"
        raw = (ROOT / path).read_bytes()
        self.assertEqual(digest(raw), "6fa1ec20d4721696fd6285729da303c4de175b570f8a00de2de3e3f3ab6d8ea3")
        review = json.loads(raw)
        self.assertTrue(review["decisions"]["source_preference"].startswith("HOLD"))
        for flag in ("source_selection_approved", "full_record_editorially_approved",
                     "canonical_change_applied", "publication_ready", "canon_changed"):
            self.assertFalse(review["decisions"][flag])
        candidate_pin = self.bundle["entries"][0]["candidate"]
        self.assertIn(candidate_pin, review["inputs"])
        self.assertIn("unchanged inputs", review["stopping_rule"])


if __name__ == "__main__":
    unittest.main()

