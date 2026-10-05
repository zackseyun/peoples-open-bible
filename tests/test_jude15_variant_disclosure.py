"""Scoped source/reader integrity, not proof of Greek historical priority."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest
from unittest.mock import patch

import yaml
from jsonschema import Draft202012Validator
from tools import audit_footnotes
from tools import export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]
BASE = '812b40b4583513af6d7832f24f85ec93a7f7666a'
TARGET = 'translation/nt/jude/001/015.yaml'
CANDIDATE = 'sources/textual_restoration/candidates/jude1_15.2026-10-05.v1.json'


class JudeVariantDisclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before_raw = subprocess.check_output(['git', 'show', f'{BASE}:{TARGET}'], cwd=ROOT)
        cls.before = yaml.safe_load(cls.before_raw)
        cls.current = yaml.safe_load((ROOT / TARGET).read_text())
        cls.candidate = json.loads((ROOT / CANDIDATE).read_text())

    def test_exact_candidate_schema_and_source_retention(self):
        self.assertEqual(self.current, self.candidate)
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(self.current)
        self.assertEqual(self.current['source'], self.before['source'])
        clean = lambda s: re.sub(r'\[[a-d]\]', '', s)
        self.assertEqual(clean(self.current['translation']['text']), clean(self.before['translation']['text']))

    def test_notes_preserved_and_anchored_to_their_own_phrases(self):
        self.assertEqual(self.current['translation']['footnotes'][:3], self.before['translation']['footnotes'])
        text = self.current['translation']['text']
        for phrase in ('convict[a]', 'ungodly[d] concerning', 'harsh things[c]', 'him[b].'):
            self.assertIn(phrase, text)
        for marker in 'abcd':
            self.assertEqual(text.count(f'[{marker}]'), 1)
        self.assertEqual(audit_footnotes.audit_one(ROOT / TARGET)['status'], 'ok')
        note = self.current['translation']['footnotes'][3]
        self.assertEqual(note['reason'], 'textual_variant')
        for phrase in ('Sinaiticus', 'P72', 'every soul', 'every person', 'provisionally', 'disputed'):
            self.assertIn(phrase, note['text'])

    def test_old_reviews_are_archived_not_transferred(self):
        history = self.current['review_history']
        self.assertEqual({h['field']: h['value'] for h in history},
                         {f: self.before[f] for f in ('status', 'revision_pass', 'cross_check')})
        self.assertTrue(all(not h['certifies_this_candidate'] for h in history))
        self.assertEqual(self.current['ai_draft'], self.before['ai_draft'])
        self.assertEqual(self.current['theological_decisions'], self.before['theological_decisions'])
        self.assertEqual(self.current['cross_check'], {'status': 'needs_review'})
        self.assertEqual(self.current['status'], 'draft')
        self.assertNotIn('revision_pass', self.current)
        self.assertEqual(self.current['textual_comparison']['historical_priority'], 'unresolved')
        self.assertFalse(self.current['textual_comparison']['publication_approved'])

    def test_full_book_export_changes_only_target_notes_and_anchors(self):
        after = exporter.export_book('JUD')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda code, ch, v:
                          self.before if (code, ch, v) == ('JUD', 1, 15) else loader(code, ch, v)):
            before = exporter.export_book('JUD')
        index = lambda b: {(c['chapter'], v['verse']): v for c in b['chapters'] for v in c['verses']}
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 1)
        self.assertEqual(len(a), 25)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([k for k in a if a[k] != b[k]], [(1, 15)])
        self.assertEqual(a[(1, 15)]['footnotes'], self.current['translation']['footnotes'])
        for p in sorted((ROOT / 'translation/nt/jude').rglob('*.yaml')):
            if p != ROOT / TARGET:
                raw = subprocess.check_output(['git', 'show', f'{BASE}:{p.relative_to(ROOT)}'], cwd=ROOT)
                self.assertEqual(hashlib.sha256(raw).digest(), hashlib.sha256(p.read_bytes()).digest())

    def test_existing_lexical_entries_are_not_claimed_as_new_consultation(self):
        a, b = self.current['lexical_decisions'], self.before['lexical_decisions']
        self.assertEqual(len(a), len(b))
        for new, old in zip(a, b):
            if old['source_word'] == 'πάντας τοὺς ἀσεβεῖς':
                self.assertEqual({k: v for k, v in new.items() if k != 'rationale'},
                                 {k: v for k, v in old.items() if k != 'rationale'})
                self.assertIn('textual variant', new['rationale'])
                self.assertIn('No new BDAG consultation', new['rationale'])
            else:
                self.assertEqual(new, old)

    def test_receipt_binds_actual_application_and_review_correction(self):
        receipt = json.loads((ROOT / 'sources/textual_restoration/applications/jude1_15.2026-10-05.v1.json').read_text())
        self.assertEqual(receipt['candidate_sha256'], hashlib.sha256((ROOT / CANDIDATE).read_bytes()).hexdigest())
        self.assertEqual(receipt['application']['applied_yaml_sha256'], hashlib.sha256((ROOT / TARGET).read_bytes()).hexdigest())
        self.assertEqual(receipt['baseline_yaml_sha256'], hashlib.sha256(self.before_raw).hexdigest())
        self.assertEqual(receipt['application']['changed_export_units'], [[1, 15]])
        self.assertEqual(receipt['review']['corrected_candidate_sha256'], receipt['candidate_sha256'])
        self.assertTrue(receipt['review']['correction_applied'])
        self.assertFalse(receipt['decision']['fresh_decipherment'])
        self.assertFalse(receipt['decision']['canon_change'])


if __name__ == '__main__':
    unittest.main()
