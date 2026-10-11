"""Bounded note disclosure and complete Jonah export, not source adjudication."""
import copy
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
BASE = '65af2445c13e3ec1b22e7d455e40fe5a4857b0fb'
TARGET = 'translation/ot/jonah/004/006.yaml'
BEFORE_SHA = '78d065f148b9da3219ad7a9dc37a190b8f091602f307f58fdd5e1bbfd88fa056'


class JonahDisclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = subprocess.check_output(['git', 'show', f'{BASE}:{TARGET}'], cwd=ROOT)
        assert hashlib.sha256(raw).hexdigest() == BEFORE_SHA
        cls.before = yaml.safe_load(raw)
        cls.after = yaml.safe_load((ROOT / TARGET).read_text())

    def test_exact_content_scope_and_schema(self):
        a, b = self.after, self.before
        allowed = {'translation', 'lexical_decisions', 'status', 'cross_check',
                   'revision_pass', 'review_history', 'revisions'}
        self.assertLessEqual({k for k in set(a) | set(b) if a.get(k) != b.get(k)}, allowed)
        self.assertEqual(a['source'], b['source'])
        self.assertEqual(a['ai_draft'], b['ai_draft'])
        self.assertEqual(re.sub(r'\[[a-z]\]', '', a['translation']['text']),
                         re.sub(r'\[[a-z]\]', '', b['translation']['text']))
        self.assertEqual(a['translation']['philosophy'], b['translation']['philosophy'])
        self.assertEqual(a['translation']['footnotes'][0], b['translation']['footnotes'][0])
        expected = copy.deepcopy(b['lexical_decisions'])
        expected[1] = a['lexical_decisions'][1]
        self.assertEqual(expected, a['lexical_decisions'])
        self.assertEqual(a['lexical_decisions'][1]['chosen'], 'Yahweh God')
        self.assertEqual(a['lexical_decisions'][1]['source_word'], b['lexical_decisions'][1]['source_word'])
        self.assertEqual(a['lexical_decisions'][1]['alternatives'], b['lexical_decisions'][1]['alternatives'])
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(a)

    def test_note_anchor_qualifications_and_archives(self):
        a, b = self.after, self.before
        self.assertIn('Yahweh God[b]', a['translation']['text'])
        for marker in ['a', 'b']:
            self.assertEqual(a['translation']['text'].count(f'[{marker}]'), 1)
        note = a['translation']['footnotes'][1]
        self.assertEqual(note['reason'], 'textual_variant')
        for phrase in ['4Q82', 'conventionally', 'letters uncertain', 'Mur.88 supplies',
                       'earliest wording remains uncertain']:
            self.assertIn(phrase, note['text'])
        self.assertEqual(a['status'], 'draft')
        self.assertEqual(a['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', a)
        entries = {e['field']: e for e in a['review_history']}
        self.assertEqual(set(entries), {'status', 'revision_pass', 'cross_check', 'lexical_decisions.1'})
        for field, entry in entries.items():
            value = b
            for part in field.split('.'):
                value = value[int(part)] if isinstance(value, list) else value[part]
            self.assertEqual(entry['value'], value)
            self.assertEqual(entry['archived_from_baseline_sha256'], BEFORE_SHA)
            self.assertEqual(entry['historical_review_input_binding'], 'not-verified')
            self.assertFalse(entry['certifies_this_candidate'])

    def test_complete_actual_book_export_and_single_record_delta(self):
        after = exporter.export_book('JON')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda code, ch, v:
                          self.before if (code, ch, v) == ('JON', 4, 6) else loader(code, ch, v)):
            before = exporter.export_book('JON')
        index = lambda book: {(c['chapter'], v['verse']): v
                              for c in book['chapters'] for v in c['verses']}
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 4)
        self.assertEqual(len(a), 48)
        self.assertEqual([key for key in a if a[key] != b[key]], [(4, 6)])
        self.assertEqual(a[(4, 6)]['footnotes'], self.after['translation']['footnotes'])
        self.assertEqual(audit_footnotes.audit_one(ROOT / TARGET)['status'], 'ok')
        self.assertNotIn('review_history', a[(4, 6)])


if __name__ == '__main__':
    unittest.main()
