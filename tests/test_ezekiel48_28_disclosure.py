"""Scoped application checks, not source priority or philological approval."""
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
RECEIPT = ROOT / 'sources/textual_restoration/applications/ezekiel48_28.2026-10-06.v1.json'
SHA = lambda raw: hashlib.sha256(raw).hexdigest()


class EzekielDisclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(RECEIPT.read_text())
        cls.target = ROOT / cls.receipt['target']
        cls.raw = subprocess.check_output(['git', 'show',
            f"{cls.receipt['baseline_revision']}:{cls.receipt['target']}"], cwd=ROOT)
        cls.before = yaml.safe_load(cls.raw)
        cls.after = yaml.safe_load(cls.target.read_text())

    def test_complete_candidate_and_preserved_source_main_words(self):
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(self.after)
        candidate = ROOT / self.receipt['candidate']
        self.assertEqual(self.after, json.loads(candidate.read_text()))
        self.assertEqual(SHA(self.raw), self.receipt['baseline_sha256'])
        self.assertEqual(SHA(candidate.read_bytes()), self.receipt['candidate_sha256'])
        self.assertEqual(SHA(self.target.read_bytes()), self.receipt['application']['yaml_sha256'])
        self.assertEqual(self.before['source'], self.after['source'])
        clean = lambda t: re.sub(r'\[[a-z]+\]', '', t)
        self.assertEqual(clean(self.before['translation']['text']), clean(self.after['translation']['text']))

    def test_correct_referent_and_source_qualified_note(self):
        tr = self.after['translation']
        self.assertNotIn('Gad[a]', tr['text'])
        self.assertIn('Meribath-kadesh[a]', tr['text'])
        self.assertIn('Wadi of Egypt[b]', tr['text'])
        self.assertEqual(tr['footnotes'][0], self.before['translation']['footnotes'][0])
        self.assertEqual(tr['footnotes'][1]['text'], self.receipt['note_b'])
        for phrase in ('without ‘of Egypt’', 'identification', 'contextual', 'often seasonal'):
            self.assertIn(phrase, tr['footnotes'][1]['text'])
        self.assertEqual(audit_footnotes.audit_one(self.target)['status'], 'ok')
        for marker in ('a', 'b'):
            self.assertEqual(tr['text'].count(f'[{marker}]'), 1)

    def test_old_approvals_are_preserved_not_transferred(self):
        self.assertEqual({r['field']: r['value'] for r in self.after['review_history']},
            {f: self.before[f] for f in ('status', 'revision_pass', 'cross_check')})
        self.assertTrue(all(not r['certifies_this_candidate'] and
            r['archived_from_baseline_sha256'] == SHA(self.raw) for r in self.after['review_history']))
        for field in ('ai_draft', 'revisions', 'theological_decisions'):
            self.assertEqual(self.after.get(field), self.before.get(field))
        self.assertEqual(self.after['status'], 'draft')
        self.assertEqual(self.after['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', self.after)
        for old, new in zip(self.before['lexical_decisions'], self.after['lexical_decisions']):
            if old['source_word'] == 'נַחֲלָה':
                self.assertEqual({k:v for k,v in old.items() if k != 'rationale'},
                    {k:v for k,v in new.items() if k != 'rationale'})
                self.assertIn('does not claim a new HALOT consultation', new['rationale'])
            else:
                self.assertEqual(old, new)

    def test_live_complete_export_only_target_differs(self):
        # Other future EZK changes do not have to match this historical receipt.
        # Within the current complete export, substitute only the frozen target.
        after = exporter.export_book('EZK')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c,ch,v:
            self.before if (c,ch,v) == ('EZK',48,28) else loader(c,ch,v)):
            before = exporter.export_book('EZK')
        index = lambda b: {(c['chapter'],v['verse']):v for c in b['chapters'] for v in c['verses']}
        a,b = index(before),index(after)
        self.assertEqual(len(after['chapters']), 48)
        self.assertEqual(len(b), 1273)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([k for k in a if a[k] != b[k]], [(48,28)])
        self.assertEqual(b[(48,28)]['footnotes'], self.after['translation']['footnotes'])
        self.assertEqual(b[(48,28)]['text'], self.after['translation']['text'])

    def test_historical_sample_is_not_upgraded_by_application(self):
        assessment = ROOT / self.receipt['assessment']
        selection = ROOT / self.receipt['selection']
        self.assertEqual(SHA(assessment.read_bytes()), self.receipt['assessment_sha256'])
        self.assertEqual(SHA(selection.read_bytes()), self.receipt['selection_sha256'])
        record = json.loads(assessment.read_text())
        self.assertEqual(record['summary']['established_main_english_semantic_improvements'], 0)
        self.assertFalse(record['limits']['application_approved'])
        self.assertFalse(self.receipt['decision']['source_changed'])
        self.assertFalse(self.receipt['decision']['marker_free_english_changed'])
        self.assertFalse(self.receipt['decision']['novel_reading_demonstrated'])
        self.assertFalse(self.receipt['decision']['publication_approved'])


if __name__ == '__main__':
    unittest.main()
