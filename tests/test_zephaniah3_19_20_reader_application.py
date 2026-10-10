"""Two-verse same-source honor trial; not a discovery/priority certification."""
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
BASE = "08930ce8b20e54896f153537bfd8d636eef21248"
PREFIX = "sources/textual_restoration/"
CANDIDATE = PREFIX + "candidates/zephaniah3_19_20_reader.2026-10-10.v2.json"
CONTRACT = PREFIX + "comparisons/zephaniah3_19_20_reader_contract.2026-10-10.v2.json"
CONTRACT_SHA = "b0d2429d1216f266fca3b47a5b31211a38b668fc98800fae4c4c9c0340e54aae"
RECEIPT = PREFIX + "applications/zephaniah3_19_20_reader.2026-10-10.v1.json"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact_sha(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(",", ":")).encode())


def index(book):
    return {(c["chapter"], v["verse"]): v for c in book["chapters"] for v in c["verses"]}


class Zephaniah31920ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidates = json.loads((ROOT / CANDIDATE).read_text())["records"]
        cls.contract = json.loads((ROOT / CONTRACT).read_text())
        cls.preflight = cls.contract["preflight"]
        cls.raw = {p: subprocess.check_output(["git", "show", BASE + ":" + p], cwd=ROOT)
                   for p in cls.candidates}
        cls.before = {p: yaml.safe_load(raw) for p, raw in cls.raw.items()}

    def test_schema_pins_and_same_source_english(self):
        self.assertEqual(sha((ROOT / CONTRACT).read_bytes()), CONTRACT_SHA)
        self.assertEqual(sha((ROOT / CANDIDATE).read_bytes()), self.preflight["candidate_sha256"])
        schema = json.loads((ROOT / "schema/verse.schema.json").read_text())
        ec = json.loads((ROOT / (PREFIX + "comparisons/zephaniah3_19_20_english_contract.2026-10-10.v1.json")).read_text())
        for p, c in self.candidates.items():
            with self.subTest(path=p):
                Draft202012Validator(schema).validate(c)
                pins = self.preflight["verse_pins"][p]
                self.assertEqual(sha(self.raw[p]), pins["baseline_yaml_sha256"])
                self.assertEqual(sha(yaml.safe_dump(c, allow_unicode=True, sort_keys=False,
                                                  width=1000).encode()), pins["candidate_yaml_sha256"])
                for field in ("source", "ai_draft"):
                    self.assertEqual(c[field], self.before[p][field])
                clean = lambda text: re.sub(r"\[[a-z]\]", "", text)
                target = next(t for t in ec["targets"] if t["path"] == p)
                preferred = next(t["text"] for t in target["candidates"] if t["id"] == "T")
                self.assertEqual(clean(c["translation"]["text"]), preferred)
                self.assertNotEqual(preferred, clean(self.before[p]["translation"]["text"]))
                for flag in ("source_changed", "source_interpretation_changed", "original_priority_settled"):
                    self.assertIs(c["source_audit"][flag], False)

    def test_exact_archives_history_and_scoped_metadata(self):
        fields = ["status", "translation", "lexical_decisions", "theological_decisions",
                  "revision_pass", "cross_check", "ai_draft"]
        for p, c in self.candidates.items():
            b = self.before[p]
            with self.subTest(path=p):
                history = c["review_history"]
                self.assertEqual([h["field"] for h in history], fields)
                self.assertEqual({h["field"]: h["value"] for h in history},
                                 {k: b[k] for k in fields})
                self.assertTrue(all(h["archived_from_baseline_sha256"] == sha(self.raw[p])
                                    and h["certifies_this_candidate"] is False for h in history))
                self.assertEqual(c["revisions"][:-1], b.get("revisions", []))
                self.assertEqual(c["revisions"][-1]["category"], "same_source_english")
                self.assertEqual(len(c["lexical_decisions"]), len(b["lexical_decisions"]))
                self.assertEqual([i for i, (a, z) in enumerate(zip(b["lexical_decisions"],
                                                                 c["lexical_decisions"])) if a != z],
                                 self.preflight["changed_lexical_indices"][p])
                self.assertEqual(c["theological_decisions"], b["theological_decisions"])
                self.assertEqual(c["status"], "draft")
                self.assertEqual(c["cross_check"], {"status": "needs_review"})
                self.assertNotIn("revision_pass", c)

    def test_corrected_anchors_and_qualified_disclosures(self):
        a, b = [self.candidates[p]["translation"] for p in sorted(self.candidates)]
        for anchor in ("oppressors[a][f]", "outcast[b]", "renowned[e]", "land[c]", "shame[d]"):
            self.assertIn(anchor, a["text"])
        self.assertIn("praised[b]", b["text"])
        self.assertIn("fortunes[a]", b["text"])
        self.assertNotIn("in[a]", b["text"])
        notes = {n["marker"]: n for n in a["footnotes"]}
        self.assertEqual(notes["d"]["reason"], "alternative_reading")
        self.assertIn("contextual expansion", notes["d"]["text"])
        self.assertIn("noun imagery", notes["e"]["text"])
        self.assertEqual(notes["f"]["reason"], "textual_variant")
        for phrase in ("in you, for your sake", "Rahlfs–Hanhart numbers", "Swete prints", "no subject named",
                       "damaged or supplied", "historical priority"):
            self.assertIn(phrase, notes["f"]["text"])
        self.assertEqual(re.findall(r"\[([a-z])\]", a["text"]), ["a", "f", "b", "e", "c", "d"])
        self.assertEqual(re.findall(r"\[([a-z])\]", b["text"]), ["b", "a"])

    def test_evidence_limits_and_single_masked_vote(self):
        for p, expected in self.preflight["pins"].items():
            self.assertEqual(sha((ROOT / p).read_bytes()), expected)
        comp = json.loads((ROOT / (PREFIX + "comparisons/zephaniah3_19_20_source.2026-10-10.v1.json")).read_text())
        for flag in ("source_changed", "fresh_image_reading", "novel_reading_demonstrated",
                     "canon_changed", "publication_approved", "canonical_application_performed"):
            self.assertIs(comp[flag], False)
        self.assertIs(comp["controls"][1]["shame_tail_preserved"], False)
        self.assertIs(comp["controls"][2]["shame_word_published_preserved"], True)
        for ctrl in comp["controls"][1:3]:
            self.assertIs(ctrl["whole_verse_preserved"], False)
            self.assertIs(ctrl["pointing_attested"], False)
        self.assertIn("future-passive", comp["controls"][4]["shame_alignment"])
        self.assertIn("καὶ θήσομαι", comp["controls"][4]["honor_clause_edition_difference"])
        result = json.loads((ROOT / (PREFIX + "comparisons/zephaniah3_19_20_english_result.2026-10-10.v1.json")).read_text())
        self.assertEqual(result["preferences"], {"verse19": "T", "verse20": "T", "coherent_pair": "T"})
        self.assertEqual(result["strength"], "moderate")
        self.assertEqual(result["independent_votes"], 1)
        self.assertIs(result["repeat_until_agreement"], False)
        self.assertEqual(result["contract_sha256"], self.contract["english_contract_sha256"])
        self.assertIs(self.contract["additional_english_preference_vote"], False)
        self.assertIs(self.contract["source_priority_vote"], False)
        old_path = PREFIX + "comparisons/zephaniah3_19_20_reader_contract.2026-10-10.v1.json"
        self.assertEqual(sha((ROOT / old_path).read_bytes()),
                         self.contract["superseded_reader_contract_sha256"])
        old_contract = json.loads((ROOT / old_path).read_text())
        old_candidate_path = old_contract["candidate"]
        self.assertEqual(sha((ROOT / old_candidate_path).read_bytes()),
                         old_contract["preflight"]["candidate_sha256"])
        old_records = json.loads((ROOT / old_candidate_path).read_text())["records"]
        for p, c in self.candidates.items():
            expected = json.loads(json.dumps(old_records[p]))
            if p.endswith("019.yaml"):
                expected["translation"]["footnotes"][-1] = c["translation"]["footnotes"][-1]
                expected["lexical_decisions"][12] = c["lexical_decisions"][12]
            self.assertEqual(c, expected)

    def test_historical_full_book_overlay(self):
        archive = subprocess.check_output(["git", "archive", BASE, "translation/ot/zephaniah"], cwd=ROOT)
        records, manifest = {}, {}
        with tarfile.open(fileobj=io.BytesIO(archive)) as snapshot:
            for m in snapshot.getmembers():
                if m.isfile() and m.name.endswith(".yaml"):
                    raw = snapshot.extractfile(m).read()
                    p = Path(m.name)
                    records[(int(p.parent.name), int(p.stem))] = yaml.safe_load(raw)
                    if m.name not in self.candidates:
                        manifest[m.name] = sha(raw)
        loader = exporter.load_translation_record

        def historical(code, ch, v, overlay=False):
            if code == "ZEP":
                p = f"translation/ot/zephaniah/{ch:03}/{v:03}.yaml"
                return self.candidates.get(p, records.get((ch, v))) if overlay else records.get((ch, v))
            return loader(code, ch, v)

        with patch.object(exporter, "load_translation_record", side_effect=historical):
            before = exporter.export_book("ZEP")
        with patch.object(exporter, "load_translation_record", side_effect=lambda *args:
                          historical(*args, overlay=True)):
            after = exporter.export_book("ZEP")
        a, b = index(before), index(after)
        self.assertEqual(len(before["chapters"]), 3)
        self.assertEqual(len(a), 53)
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[3, 19], [3, 20]])
        self.assertEqual(compact_sha(before), self.preflight["export_before_sha256"])
        self.assertEqual(compact_sha(after), self.preflight["export_candidate_sha256"])
        self.assertEqual(len(manifest), 51)
        self.assertEqual(compact_sha(manifest), self.preflight["other_verse_manifest_sha256"])
        for p, c in self.candidates.items():
            key = (3, int(Path(p).stem))
            self.assertEqual(b[key]["footnotes"], c["translation"]["footnotes"])

    def test_exact_application_and_current_export(self):
        receipt = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(receipt["reader_contract_sha256"], CONTRACT_SHA)
        self.assertEqual(receipt["review"]["status"], "pass")
        self.assertIs(receipt["review"]["source_priority_approved"], False)
        self.assertIs(receipt["review"]["additional_english_preference_vote"], False)
        self.assertIs(receipt["application"]["deployed_reader_verified"], False)
        for p, c in self.candidates.items():
            self.assertEqual(sha((ROOT / p).read_bytes()),
                             self.preflight["verse_pins"][p]["candidate_yaml_sha256"])
            self.assertEqual(yaml.safe_load((ROOT / p).read_text()), c)
            self.assertEqual(audit_footnotes.audit_one(ROOT / p)["status"], "ok")
        after = exporter.export_book("ZEP")
        loader = exporter.load_translation_record
        with patch.object(exporter, "load_translation_record", side_effect=lambda code, ch, v:
                          self.before.get(f"translation/ot/zephaniah/{ch:03}/{v:03}.yaml",
                                          loader(code, ch, v)) if code == "ZEP" else loader(code, ch, v)):
            before = exporter.export_book("ZEP")
        a, b = index(before), index(after)
        self.assertEqual(len(after["chapters"]), 3)
        self.assertEqual(len(a), 53)
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[3, 19], [3, 20]])
        for p, c in self.candidates.items():
            self.assertEqual(b[(3, int(Path(p).stem))]["footnotes"], c["translation"]["footnotes"])


if __name__ == "__main__":
    unittest.main()
