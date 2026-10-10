"""Bounded same-source interpretation checks; not historical priority certification."""
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import unittest
from unittest.mock import patch

import yaml
from jsonschema import Draft202012Validator
from tools import audit_footnotes
from tools import export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]
BASE = "cfbc9d9b5fba46a3d08558ef35b38410b1244b0e"
TARGET = "translation/ot/zephaniah/003/018.yaml"
PREFIX = "sources/textual_restoration/"
CANDIDATE = PREFIX + "candidates/zephaniah3_18_reader.2026-10-10.v1.json"
CONTRACT = PREFIX + "comparisons/zephaniah3_18_reader_contract.2026-10-10.v1.json"
CONTRACT_SHA = "b09c83dde7dd0f45b1fcae01149d518bffeb77584a86ae0adef1593547881bc9"
RECEIPT = PREFIX + "applications/zephaniah3_18_reader.2026-10-10.v1.json"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact_sha(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":")).encode())


def index(book):
    return {(c["chapter"], v["verse"]): v for c in book["chapters"] for v in c["verses"]}


class Zephaniah318ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = subprocess.check_output(["git", "show", f"{BASE}:{TARGET}"], cwd=ROOT)
        cls.before = yaml.safe_load(cls.raw)
        cls.candidate = json.loads((ROOT / CANDIDATE).read_text())
        cls.contract = json.loads((ROOT / CONTRACT).read_text())
        cls.preflight = cls.contract["preflight"]

    def test_schema_pins_source_and_meaning_change(self):
        c = self.candidate
        Draft202012Validator(json.loads((ROOT / "schema/verse.schema.json").read_text())).validate(c)
        self.assertEqual(sha((ROOT / CONTRACT).read_bytes()), CONTRACT_SHA)
        self.assertEqual(sha(self.raw), self.preflight["baseline_yaml_sha256"])
        self.assertEqual(sha((ROOT / CANDIDATE).read_bytes()), self.preflight["candidate_sha256"])
        self.assertEqual(sha(yaml.safe_dump(c, allow_unicode=True, sort_keys=False,
                                          width=1000).encode()), self.preflight["candidate_yaml_sha256"])
        for field in ("source", "ai_draft"):
            self.assertEqual(c[field], self.before[field])
        clean = lambda s: re.sub(r"\[[a-z]\]", "", s)
        self.assertNotEqual(clean(c["translation"]["text"]), clean(self.before["translation"]["text"]))
        self.assertEqual(clean(c["translation"]["text"]),
                         "I have gathered those grieving over the appointed festival—they were from you; reproach was a burden upon her.")
        self.assertTrue(c["source_audit"]["source_interpretation_changed"])
        self.assertFalse(c["source_audit"]["original_priority_settled"])

    def test_exact_archives_prior_history_and_scoped_metadata(self):
        c = self.candidate
        fields = ["status", "translation", "lexical_decisions", "theological_decisions",
                  "revision_pass", "cross_check", "ai_draft"]
        history = c["review_history"]
        self.assertEqual([h["field"] for h in history], fields)
        self.assertEqual({h["field"]: h["value"] for h in history},
                         {k: self.before[k] for k in fields})
        self.assertTrue(all(h["archived_from_baseline_sha256"] == sha(self.raw)
                            and h["certifies_this_candidate"] is False for h in history))
        self.assertEqual(c["revisions"][:2], self.before["revisions"])
        self.assertEqual(len(c["revisions"]), 3)
        self.assertEqual(c["revisions"][-1]["category"], "source_interpretation")
        self.assertEqual([i for i, (a, b) in enumerate(zip(self.before["lexical_decisions"],
                                                        c["lexical_decisions"])) if a != b],
                         [1, 3, 4, 5, 6, 7])
        self.assertEqual(c["status"], "draft")
        self.assertEqual(c["cross_check"], {"status": "needs_review"})
        self.assertNotIn("revision_pass", c)
        self.assertEqual(len(c["theological_decisions"]), 1)
        self.assertIn("without selecting by pastoral desirability",
                      c["theological_decisions"][0]["rationale"])

    def test_anchors_and_alternatives(self):
        tr = self.candidate["translation"]
        self.assertIn("gathered[b]", tr["text"])
        self.assertIn("festival[a]", tr["text"])
        self.assertIn("her[c][d][e]", tr["text"])
        self.assertNotIn("her[c][b]", tr["text"])
        self.assertEqual(re.findall(r"\[([a-z])\]", tr["text"]), ["b", "a", "c", "d", "e"])
        notes = {n["marker"]: n for n in tr["footnotes"]}
        for marker in "abc":
            self.assertEqual(notes[marker], next(n for n in self.before["translation"]["footnotes"]
                                                 if n["marker"] == marker))
        self.assertEqual(notes["d"]["reason"], "alternative_reading")
        for phrase in ("supplied", "context", "do not make the alternative impossible"):
            self.assertIn(phrase, notes["d"]["text"])
        self.assertEqual(notes["e"]["reason"], "textual_variant")
        for phrase in ("partly", "supplied and uncertain", "historical priority"):
            self.assertIn(phrase, notes["e"]["text"])

    def test_evidence_limits_and_one_masked_vote(self):
        for path, expected in self.preflight["pins"].items():
            self.assertEqual(sha((ROOT / path).read_bytes()), expected)
        comp = json.loads((ROOT / (PREFIX + "comparisons/zephaniah3_18_clause.2026-10-10.v1.json")).read_text())
        self.assertFalse(comp["source_changed"])
        self.assertFalse(comp["fresh_image_reading"])
        mur = comp["controls"][1]
        self.assertEqual(mur["supplied"], ["final י of אספתי", "הי of היו"])
        self.assertIn("ו of היו", mur["uncertain"])
        self.assertFalse(mur["whole_verse_preserved"])
        self.assertFalse(mur["pointing_attested"])
        self.assertFalse(comp["controls"][5]["unanimity_inferred"])
        self.assertIn("Indirect Aquila report", comp["controls"][7]["limits"])
        result = json.loads((ROOT / (PREFIX + "comparisons/zephaniah3_18_english_result.2026-10-10.v1.json")).read_text())
        self.assertEqual(result["preference"], "S")
        self.assertEqual(result["independent_votes"], 1)
        self.assertFalse(result["repeat_until_agreement"])
        ec = ROOT / (PREFIX + "comparisons/zephaniah3_18_english_contract.2026-10-10.v1.json")
        self.assertEqual(sha(ec.read_bytes()), result["contract_sha256"])

    def test_historical_full_book_overlay(self):
        archive = subprocess.check_output(["git", "archive", BASE, "translation/ot/zephaniah"], cwd=ROOT)
        records, manifest = {}, {}
        with tarfile.open(fileobj=io.BytesIO(archive)) as snapshot:
            for m in snapshot.getmembers():
                if m.isfile() and m.name.endswith(".yaml"):
                    raw = snapshot.extractfile(m).read()
                    p = Path(m.name)
                    records[(int(p.parent.name), int(p.stem))] = yaml.safe_load(raw)
                    if m.name != TARGET:
                        manifest[m.name] = sha(raw)
        loader = exporter.load_translation_record

        def historical(code, ch, v, overlay=False):
            if code == "ZEP":
                return self.candidate if overlay and (ch, v) == (3, 18) else records.get((ch, v))
            return loader(code, ch, v)

        with patch.object(exporter, "load_translation_record", side_effect=historical):
            before = exporter.export_book("ZEP")
        with patch.object(exporter, "load_translation_record", side_effect=lambda *args:
                          historical(*args, overlay=True)):
            after = exporter.export_book("ZEP")
        a, b = index(before), index(after)
        self.assertEqual(len(before["chapters"]), 3)
        self.assertEqual(len(a), 53)
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[3, 18]])
        self.assertEqual(compact_sha(before), self.preflight["export_before_sha256"])
        self.assertEqual(compact_sha(after), self.preflight["export_candidate_sha256"])
        self.assertEqual(len(manifest), 52)
        self.assertEqual(compact_sha(manifest), self.preflight["other_verse_manifest_sha256"])
        self.assertEqual(b[(3, 18)]["footnotes"], self.candidate["translation"]["footnotes"])

    def test_exact_application_and_current_export(self):
        receipt = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(sha((ROOT / TARGET).read_bytes()), self.preflight["candidate_yaml_sha256"])
        self.assertEqual(yaml.safe_load((ROOT / TARGET).read_text()), self.candidate)
        self.assertEqual(receipt["reader_contract_sha256"], CONTRACT_SHA)
        self.assertEqual(receipt["review"]["status"], "pass")
        self.assertFalse(receipt["review"]["source_priority_approved"])
        self.assertFalse(receipt["review"]["additional_english_preference_vote"])
        self.assertFalse(receipt["application"]["deployed_reader_verified"])
        self.assertEqual(compact_sha(exporter.export_book("ZEP")),
                         self.preflight["export_candidate_sha256"])
        other = {str(p.relative_to(ROOT)): sha(p.read_bytes())
                 for p in (ROOT / "translation/ot/zephaniah").rglob("*.yaml")
                 if str(p.relative_to(ROOT)) != TARGET}
        self.assertEqual(len(other), 52)
        self.assertEqual(compact_sha(other), self.preflight["other_verse_manifest_sha256"])
        self.assertEqual(audit_footnotes.audit_one(ROOT / TARGET)["status"], "ok")


if __name__ == "__main__":
    unittest.main()
