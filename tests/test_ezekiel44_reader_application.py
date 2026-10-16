"""Named-witness disclosure, not a Hebrew-priority or whole-verse approval."""
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
BASE = 'fbbe0d9d1d09145909089852b60436b86add0e98'
STEM = 'ezekiel44_7_reader.2026-10-16.v1.json'
CONTRACT = ROOT / 'sources/textual_restoration/comparisons' / STEM
TARGET = 'translation/ot/ezekiel/044/007.yaml'


class Ezekiel44ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text())
        cls.candidate = json.loads((ROOT / cls.contract['candidate']).read_text())
        cls.raw = historical_book(BASE)
        cls.records = {p: yaml.safe_load(raw) for p, raw in cls.raw.items()}
        cls.before = cls.records[TARGET]

    def test_complete_record_scope_and_archives(self):
        c, b, ct = self.candidate, self.before, self.contract
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(c)
        self.assertEqual(sha(self.raw[TARGET]), ct['baseline_yaml_sha256'])
        self.assertEqual(sha((ROOT / ct['candidate']).read_bytes()), ct['candidate_sha256'])
        self.assertEqual(sha(yaml.safe_dump(c, allow_unicode=True, sort_keys=False, width=1000).encode()), ct['candidate_yaml_sha256'])
        for field in ('id', 'reference', 'source', 'lexical_decisions', 'ai_draft', 'theological_decisions'):
            self.assertEqual(c[field], b[field], field)
        self.assertEqual(c['translation']['philosophy'], b['translation']['philosophy'])
        plain = lambda s: re.sub(r'\[[a-z]\]', '', s)
        self.assertEqual(plain(c['translation']['text']), plain(b['translation']['text']))
        self.assertEqual(c['revisions'][:-1], b['revisions'])
        self.assertEqual(c['revisions'][-1]['baseline_sha256'], ct['baseline_yaml_sha256'])
        self.assertEqual(c['revisions'][-1]['from'], b['translation']['text'])
        self.assertEqual(c['revisions'][-1]['to'], c['translation']['text'])
        self.assertEqual(c['status'], 'draft')
        self.assertEqual(c['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', c)
        self.assertEqual(len(c['review_history']), 5)
        self.assertEqual({a['field'] for a in c['review_history']}, {'status', 'revision_pass', 'cross_check', 'translation.text', 'translation.footnotes'})
        for archive in c['review_history']:
            old = b
            for part in archive['field'].split('.'):
                old = old[part]
            self.assertEqual(archive['value'], old)
            self.assertEqual(archive['archived_from_baseline_sha256'], ct['baseline_yaml_sha256'])
            self.assertIs(archive['historical_review_inputs_verified'], False)
            self.assertIs(archive['certifies_this_candidate'], False)
        self.assertEqual({k for k in set(c) | set(b) if c.get(k) != b.get(k)}, {'translation', 'status', 'revision_pass', 'cross_check', 'review_history', 'revisions', 'source_audit', 'textual_comparison'})

    def test_disclosure_and_semantic_anchors(self):
        c, b = self.candidate, self.before
        text, notes = c['translation']['text'], c['translation']['footnotes']
        self.assertEqual(re.findall(r'\[([a-z])\]', text), ['a', 'b', 'c', 'd'])
        for phrase in ('foreigners[a]', 'uncircumcised in flesh[b]', 'my food[c]', 'my covenant[d]'):
            self.assertIn(phrase, text)
        self.assertEqual(notes[0], b['translation']['footnotes'][0])
        self.assertEqual(notes[2], {**b['translation']['footnotes'][1], 'marker': 'c'})
        self.assertEqual(notes[3], {**b['translation']['footnotes'][2], 'marker': 'd'})
        self.assertEqual(notes[1], {'marker': 'b', 'text': "Papyrus 967, an ancient Greek manuscript, omits 'and uncircumcised in flesh' here, but includes the corresponding qualification in verse 9. The Hebrew wording is retained; the omission's origin remains uncertain.", 'reason': 'textual_variant'})
        self.assertEqual(audit_footnotes.audit_one(ROOT / self.contract['candidate'])['status'], 'ok')
        self.assertIs(c['source_audit']['main_english_retained'], True)
        self.assertIn('HOLD', c['source_audit']['historical_priority'])
        self.assertIs(c['source_audit']['generated_images_used_as_evidence'], False)
        self.assertIs(c['textual_comparison']['whole_verse_optimality_certified'], False)

    def test_historical_inputs_and_complete_preflight(self):
        ct = self.contract
        self.assertEqual(ct['baseline_commit'], BASE)
        for p, h in ct['input_pins'].items():
            self.assertEqual(sha(subprocess.check_output(['git', 'show', f'{BASE}:{p}'], cwd=ROOT)), h, p)
        self.assertEqual(subprocess.check_output(['git', 'rev-parse', f'{BASE}:translation/ot/ezekiel'], cwd=ROOT).decode().strip(), ct['book_baseline_tree_oid'])
        self.assertEqual(digest({p: sha(r) for p, r in self.raw.items()}), ct['book_baseline_manifest_sha256'])
        before = export_records(self.records)
        after = export_records({**self.records, TARGET: self.candidate})
        a, b = index(after), index(before)
        self.assertEqual((len(after['chapters']), len(a), len(self.raw)), (48, 1273, 1273))
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[44, 7]])
        self.assertEqual(a[(44, 7)]['footnotes'], self.candidate['translation']['footnotes'])
        self.assertEqual(digest(before), ct['preflight']['before_export_sha256'])
        self.assertEqual(digest(after), ct['preflight']['candidate_export_sha256'])
        self.assertIs(ct['preflight']['canonical_written'], False)

    def test_current_application_and_receipt(self):
        receipt = json.loads((ROOT / 'sources/textual_restoration/applications' / STEM).read_text())
        self.assertEqual(sha(CONTRACT.read_bytes()), receipt['review']['reviewed_contract_sha256'])
        self.assertEqual(self.contract['candidate_sha256'], receipt['review']['reviewed_candidate_sha256'])
        self.assertEqual(receipt['review']['status'], 'pass')
        self.assertEqual(sha((ROOT / TARGET).read_bytes()), self.contract['candidate_yaml_sha256'])
        self.assertEqual(yaml.safe_load((ROOT / TARGET).read_text()), self.candidate)
        current = exporter.export_book('EZK')
        self.assertEqual(len(index(current)), 1273)
        target = index(current)[(44, 7)]
        self.assertEqual(target['text'], self.candidate['translation']['text'])
        self.assertEqual(target['footnotes'], self.candidate['translation']['footnotes'])
        self.assertEqual(receipt['application']['after_export_sha256'], self.contract['preflight']['candidate_export_sha256'])
        self.assertEqual(receipt['application']['other_units_unchanged'], 1272)


if __name__ == '__main__':
    unittest.main()
