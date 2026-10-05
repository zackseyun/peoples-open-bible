"""Scoped reader application checks, not proof of historical priority."""
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
TARGET = 'translation/ot/exodus/020/021.yaml'
CANDIDATE = 'sources/textual_restoration/candidates/exodus20_21.2026-10-05.v1.json'
RECEIPT = 'sources/textual_restoration/applications/exodus20_21.2026-10-05.v1.json'


class ExodusDisclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before_raw = subprocess.check_output(['git', 'show', f'{BASE}:{TARGET}'], cwd=ROOT)
        cls.before = yaml.safe_load(cls.before_raw)
        cls.current = yaml.safe_load((ROOT / TARGET).read_text())
        cls.candidate = json.loads((ROOT / CANDIDATE).read_text())

    def test_candidate_schema_source_and_marker_free_english(self):
        self.assertEqual(self.current, self.candidate)
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(self.current)
        self.assertEqual(self.current['source'], self.before['source'])
        clean = lambda text: re.sub(r'\[[a-b]\]', '', text)
        self.assertEqual(clean(self.current['translation']['text']), clean(self.before['translation']['text']))

    def test_notes_and_anchors(self):
        self.assertEqual(self.current['translation']['footnotes'][0], self.before['translation']['footnotes'][0])
        text = self.current['translation']['text']
        self.assertIn('at a distance,', text)
        self.assertIn('thick darkness[a]', text)
        self.assertIn('where God was[b].', text)
        for marker in 'ab':
            self.assertEqual(text.count(f'[{marker}]'), 1)
        self.assertEqual(audit_footnotes.audit_one(ROOT / TARGET)['status'], 'ok')
        note = self.current['translation']['footnotes'][1]
        self.assertEqual(note['reason'], 'textual_variant')
        for phrase in ('transcription compared here', 'prophet like Moses', 'false prophets',
                       '5:28–31', '18:18–22', 'fragmentarily in 4Q158', 'not every word', 'provisionally'):
            self.assertIn(phrase, note['text'])

    def test_old_reviews_archived_not_transferred(self):
        history = self.current['review_history']
        self.assertEqual({h['field']: h['value'] for h in history},
                         {f: self.before[f] for f in ('status', 'revision_pass', 'cross_check')})
        self.assertTrue(all(not h['certifies_this_candidate'] for h in history))
        self.assertTrue(all(h['archived_from_baseline_sha256'] == hashlib.sha256(self.before_raw).hexdigest()
                            for h in history))
        for field in ('ai_draft', 'lexical_decisions', 'theological_decisions'):
            self.assertEqual(self.current[field], self.before[field])
        self.assertEqual(self.current.get('revisions'), self.before.get('revisions'))
        self.assertEqual(self.current['status'], 'draft')
        self.assertEqual(self.current['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', self.current)
        self.assertEqual(self.current['textual_comparison']['historical_priority'], 'unresolved')
        self.assertFalse(self.current['textual_comparison']['publication_approved'])

    def test_complete_export_only_target_differs(self):
        after = exporter.export_book('EXO')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda code, ch, v:
                          self.before if (code, ch, v) == ('EXO', 20, 21) else loader(code, ch, v)):
            before = exporter.export_book('EXO')
        index = lambda book: {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 40)
        self.assertEqual(len(a), 1213)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([key for key in a if a[key] != b[key]], [(20, 21)])
        self.assertEqual(a[(20, 21)]['footnotes'], self.current['translation']['footnotes'])
        receipt = json.loads((ROOT / RECEIPT).read_text())['application']
        for key, book in (('export_after_sha256', after), ('export_before_sha256', before)):
            self.assertEqual(receipt[key], hashlib.sha256(
                json.dumps(book, ensure_ascii=False, sort_keys=True).encode()).hexdigest())

    def test_receipt_pins_application_and_limits(self):
        receipt = json.loads((ROOT / RECEIPT).read_text())
        for key, file in (('candidate_sha256', CANDIDATE), ('baseline_sha256', None)):
            raw = (ROOT / file).read_bytes() if file else self.before_raw
            self.assertEqual(receipt[key], hashlib.sha256(raw).hexdigest())
        self.assertEqual(receipt['application']['yaml_sha256'], hashlib.sha256((ROOT / TARGET).read_bytes()).hexdigest())
        alignment = receipt['alignment']
        self.assertEqual(alignment['sha256'], hashlib.sha256((ROOT / alignment['repo_path']).read_bytes()).hexdigest())
        self.assertEqual(receipt['application']['changed_export_units'], [[20, 21]])
        for flag in ('source_changed', 'marker_free_english_changed', 'novel_reading_demonstrated',
                     'canon_changed', 'fresh_locus_image_reading', 'publication_approved'):
            self.assertFalse(receipt['decision'][flag])
        self.assertTrue(receipt['image_check']['custodial_pixels_viewed'])
        self.assertFalse(receipt['image_check']['literary_locus_identified'])


if __name__ == '__main__':
    unittest.main()
