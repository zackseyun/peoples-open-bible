"""Ezekiel 4 numerical disclosure and anchors, not original-number certification."""
import json
from pathlib import Path
import re
import subprocess
import unittest

import yaml
from jsonschema import Draft202012Validator
from tools import audit_footnotes
from tools import export_mobile_bible as exporter
from tests.test_ezekiel35_14_joy_reader_application import (
    digest, export_records, historical_book, index, sha,
)

ROOT = Path(__file__).resolve().parents[1]
BASE = '277aad88b04dd5afb1a3604a9ec06d3a9d1b346f'
STEM = 'ezekiel4_4_9_reader.2026-10-16.v1.json'
CONTRACT = ROOT / 'sources/textual_restoration/comparisons' / STEM
ANCHORS = {
    4: ['iniquity[a]', 'number of the days[b]'],
    5: ['their iniquity[a]', 'three hundred and ninety days[b]'],
    6: ['a day for each year[a]'],
    7: ['against it[a]'],
    8: ['ropes[a]', 'from your side to your other side[b]'],
    9: ['spelt[a]', 'three hundred and ninety days[b]'],
}


class Ezekiel4PreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text())
        cls.candidates = json.loads((ROOT / cls.contract['candidate']).read_text())
        cls.raw = historical_book(BASE)
        cls.records = {p: yaml.safe_load(raw) for p, raw in cls.raw.items()}

    def test_complete_records_and_provenance(self):
        ct = self.contract
        self.assertEqual(set(self.candidates), {f'translation/ot/ezekiel/004/{v:03}.yaml' for v in range(4, 10)})
        self.assertEqual(set(ct['targets']), set(self.candidates))
        self.assertEqual(sha((ROOT / ct['candidate']).read_bytes()), ct['candidate_sha256'])
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        for p, c in self.candidates.items():
            with self.subTest(path=p):
                b, pin = self.records[p], ct['targets'][p]
                validator.validate(c)
                self.assertEqual(sha(self.raw[p]), pin['baseline_yaml_sha256'])
                self.assertEqual(sha(yaml.safe_dump(c, allow_unicode=True, sort_keys=False, width=1000).encode()), pin['candidate_yaml_sha256'])
                for field in ('id', 'reference', 'source', 'lexical_decisions', 'ai_draft', 'theological_decisions'):
                    self.assertEqual(field in c, field in b, field)
                    self.assertEqual(c.get(field), b.get(field), field)
                self.assertEqual(c['translation']['philosophy'], b['translation']['philosophy'])
                plain = lambda s: re.sub(r'\[[a-z]\]', '', s)
                self.assertEqual(plain(c['translation']['text']), plain(b['translation']['text']))
                self.assertEqual(c['revisions'][:-1], b.get('revisions', []))
                self.assertEqual(c['revisions'][-1]['from'], b['translation']['text'])
                self.assertEqual(c['revisions'][-1]['to'], c['translation']['text'])
                self.assertEqual(c['revisions'][-1]['baseline_sha256'], pin['baseline_yaml_sha256'])
                self.assertEqual(c['status'], 'draft')
                self.assertEqual(c['cross_check'], {'status': 'needs_review'})
                self.assertNotIn('revision_pass', c)
                self.assertEqual(c['review_history'][:-5], b.get('review_history', []))
                archives = c['review_history'][-5:]
                self.assertEqual({a['field'] for a in archives}, {'status', 'revision_pass', 'cross_check', 'translation.text', 'translation.footnotes'})
                for a in archives:
                    old = b
                    for part in a['field'].split('.'):
                        old = old[part]
                    self.assertEqual(a['value'], old)
                    self.assertEqual(a['archived_from_baseline_sha256'], pin['baseline_yaml_sha256'])
                    self.assertIs(a['historical_review_inputs_verified'], False)
                    self.assertIs(a['certifies_this_candidate'], False)
                self.assertEqual({k for k in set(c) | set(b) if c.get(k) != b.get(k)}, {'translation', 'status', 'revision_pass', 'cross_check', 'review_history', 'revisions', 'source_audit', 'textual_comparison'})

    def test_exact_disclosures_and_semantic_anchors(self):
        for p, c in self.candidates.items():
            v = int(Path(p).stem)
            text, notes = c['translation']['text'], c['translation']['footnotes']
            old_notes = self.records[p]['translation']['footnotes']
            for anchor in ANCHORS[v]:
                self.assertIn(anchor, text)
            self.assertEqual(re.findall(r'\[([a-z])\]', text), [n['marker'] for n in notes])
            self.assertEqual(notes[:len(old_notes)], old_notes)
            if v in (4, 5, 9):
                note = ("Swete's Greek text (based here on Codex Vaticanus) specifies 'one hundred and fifty' days here, where the Hebrew gives no numeral. See the numerical differences noted at verses 5 and 9; the relationship between these readings remains unresolved." if v == 4 else
                        "Swete's Greek text (based here on Codex Vaticanus) reads 'one hundred and ninety days,' also in verse " + ('9' if v == 5 else '5') + ". The Hebrew has 390 in both verses; which number came first remains uncertain.")
                self.assertEqual(len(notes), len(old_notes) + 1)
                self.assertEqual(notes[-1], {'marker': 'b', 'text': note, 'reason': 'textual_variant'})
            else:
                self.assertEqual(notes, old_notes)
            for field in ('declared_source_retained', 'source_consonants_pointing_segmentation_retained', 'main_english_retained'):
                self.assertIs(c['source_audit'][field], True)
            for field in ('fresh_manuscript_transcription', 'generated_images_used_as_evidence', 'fresh_halot_consultation'):
                self.assertIs(c['source_audit'][field], False)
            self.assertIn('HOLD', c['source_audit']['historical_priority'])
            self.assertIs(c['textual_comparison']['whole_verse_optimality_certified'], False)

    def test_historical_inputs_and_full_book_preflight(self):
        ct = self.contract
        self.assertEqual(ct['baseline_commit'], BASE)
        for p, h in ct['input_pins'].items():
            self.assertEqual(sha(subprocess.check_output(['git', 'show', f'{BASE}:{p}'], cwd=ROOT)), h, p)
        self.assertEqual(subprocess.check_output(['git', 'rev-parse', f'{BASE}:translation/ot/ezekiel'], cwd=ROOT).decode().strip(), ct['book_baseline_tree_oid'])
        self.assertEqual(digest({p: sha(r) for p, r in self.raw.items()}), ct['book_baseline_manifest_sha256'])
        before = export_records(self.records)
        after = export_records({**self.records, **self.candidates})
        a, b = index(after), index(before)
        changed = [list(k) for k in a if a[k] != b[k]]
        self.assertEqual((len(after['chapters']), len(a), len(self.raw)), (48, 1273, 1273))
        self.assertEqual(changed, [[4, v] for v in range(4, 10)])
        self.assertEqual(changed, ct['preflight']['changed_export_ids'])
        self.assertEqual(ct['preflight']['other_units_unchanged'], 1267)
        self.assertEqual(digest(before), ct['preflight']['before_export_sha256'])
        self.assertEqual(digest(after), ct['preflight']['candidate_export_sha256'])
        self.assertIs(ct['preflight']['canonical_written'], False)
        self.assertIs(ct['preflight']['deployed_reader_verified'], False)


class Ezekiel4AppliedTests(unittest.TestCase):
    def test_current_targets_actual_export_and_receipt(self):
        ct = json.loads(CONTRACT.read_text())
        candidates = json.loads((ROOT / ct['candidate']).read_text())
        receipt = json.loads((ROOT / 'sources/textual_restoration/applications' / STEM).read_text())
        self.assertEqual(sha(CONTRACT.read_bytes()), receipt['review']['reviewed_contract_sha256'])
        self.assertEqual(ct['candidate_sha256'], receipt['review']['reviewed_candidate_sha256'])
        self.assertEqual(receipt['review']['status'], 'pass')
        self.assertIs(receipt['review']['repeat_until_agreement'], False)
        current = index(exporter.export_book('EZK'))
        self.assertEqual(len(current), 1273)
        for p, c in candidates.items():
            self.assertEqual(sha((ROOT / p).read_bytes()), ct['targets'][p]['candidate_yaml_sha256'])
            self.assertEqual(yaml.safe_load((ROOT / p).read_text()), c)
            self.assertEqual(audit_footnotes.audit_one(ROOT / p)['status'], 'ok')
            actual = current[(4, int(Path(p).stem))]
            self.assertEqual(actual['text'], c['translation']['text'])
            self.assertEqual(actual['footnotes'], c['translation']['footnotes'])
        self.assertEqual(receipt['application']['after_export_sha256'], ct['preflight']['candidate_export_sha256'])
        self.assertEqual(receipt['application']['other_units_unchanged'], 1267)
        self.assertIs(receipt['application']['deployed_reader_verified'], False)


if __name__ == '__main__':
    unittest.main()
