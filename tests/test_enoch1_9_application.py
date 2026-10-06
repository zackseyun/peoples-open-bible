"""Scoped source-to-English correction, not earliest-text certification."""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest
from unittest.mock import patch

import yaml
from tools import audit_footnotes
from tools import export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]
BASE = 'ac3e51bd2580ab433502f65b2d46414b6a8c312b'
TARGET = ROOT / 'translation/extra_canonical/1_enoch/001/009.yaml'
CANDIDATE = ROOT / 'sources/textual_restoration/candidates/enoch1_9.2026-10-05.v1.json'
RECEIPT = ROOT / 'sources/textual_restoration/applications/enoch1_9.2026-10-05.v1.json'


class Enoch19ApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before_raw = subprocess.check_output(
            ['git', 'show', f'{BASE}:{TARGET.relative_to(ROOT)}'], cwd=ROOT)
        cls.before = yaml.safe_load(cls.before_raw)
        cls.current = yaml.safe_load(TARGET.read_text())
        cls.candidate = json.loads(CANDIDATE.read_text())
        cls.receipt = json.loads(RECEIPT.read_text())

    def test_exact_candidate_and_same_source_one_rendering_change(self):
        self.assertEqual(self.current, self.candidate)
        self.assertEqual(self.current['source'], self.before['source'])
        clean = lambda text: re.sub(r'\[[a-c]\]', '', text)
        self.assertEqual(clean(self.current['translation']['text']),
                         clean(self.before['translation']['text']).replace(
                             'done and spoken', 'done and committed'))
        self.assertEqual(self.current['translation']['philosophy'],
                         self.before['translation']['philosophy'])

    def test_note_anchors_and_edition_qualifications(self):
        text = self.current['translation']['text']
        for phrase in ('holy ones[a]', 'all flesh[b]', 'against him[c]'):
            self.assertIn(phrase, text)
        for marker in 'abc':
            self.assertEqual(text.count(f'[{marker}]'), 1)
        self.assertEqual(self.current['translation']['footnotes'][:2],
                         self.before['translation']['footnotes'][:2])
        note = self.current['translation']['footnotes'][2]['text']
        for phrase in ('Greek Enoch edition', 'edited Ge\'ez', 'done and committed',
                       'editorial proposals', 'not additional independent'):
            self.assertIn(phrase, note)
        self.assertEqual(audit_footnotes.audit_one(TARGET)['status'], 'ok')

    def test_historical_reviews_and_provenance_not_transferred(self):
        digest = hashlib.sha256(self.before_raw).hexdigest()
        history = self.current['review_history']
        self.assertEqual({h['field']: h['value'] for h in history},
                         {f: self.before[f] for f in ('status', 'revision_pass', 'cross_check')})
        self.assertTrue(all(h['archived_from_baseline_sha256'] == digest for h in history))
        self.assertTrue(all(not h['certifies_this_candidate'] for h in history))
        for field in ('ai_draft', 'revisions', 'theological_decisions'):
            self.assertEqual(self.current[field], self.before[field])
        self.assertEqual(self.current['status'], 'draft')
        self.assertEqual(self.current['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', self.current)
        self.assertFalse(self.current['textual_comparison']['publication_approved'])

    def test_lexical_change_does_not_import_greek_speech(self):
        word = 'ኵሉ ዘገብሩ ወረሰዩ'
        lexical = next(x for x in self.current['lexical_decisions'] if x['source_word'] == word)
        self.assertEqual(lexical['chosen'], 'everything that ... have done and committed')
        self.assertIn('sense D4 explicitly cites Enoch 1:9', lexical['rationale'])
        self.assertTrue(all('spoken' not in x for x in lexical['alternatives']))
        before_other = [x for x in self.before['lexical_decisions'] if x['source_word'] != word]
        current_other = [x for x in self.current['lexical_decisions'] if x['source_word'] != word]
        self.assertEqual(current_other, before_other)
        decision = self.receipt['decision']
        self.assertFalse(decision['source_changed'])
        self.assertTrue(decision['marker_free_english_changed'])
        for field in ('greek_restoration_promoted', 'novel_reading_demonstrated',
                      'canon_changed', 'fresh_manuscript_reading', 'publication_approved'):
            self.assertFalse(decision[field])

    def test_complete_available_reader_export_changes_only_one_unit(self):
        after = exporter.export_extra_canonical_book('ENO')
        original = Path.read_text
        before_text = self.before_raw.decode()
        def read_before(path, *args, **kwargs):
            return before_text if path.resolve() == TARGET else original(path, *args, **kwargs)
        with patch.object(Path, 'read_text', autospec=True, side_effect=read_before):
            before = exporter.export_extra_canonical_book('ENO')
        index = lambda book: {(ch['chapter'], v['verse']): v
                              for ch in book['chapters'] for v in ch['verses']}
        a, b = index(after), index(before)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([key for key in a if a[key] != b[key]], [(1, 9)])
        self.assertEqual(a[(1, 9)]['footnotes'], self.current['translation']['footnotes'])
        reconstructed = copy.deepcopy(before)
        next(ch for ch in reconstructed['chapters'] if ch['chapter'] == 1)['verses'][-1] = a[(1, 9)]
        self.assertEqual(reconstructed, after)
        # Frozen receipt counts describe its baseline, not all later additions.
        self.assertIn('not complete Enoch', self.receipt['application']['export_scope'])

    def test_receipt_binds_candidate_source_control_and_application(self):
        r = self.receipt
        self.assertEqual(r['baseline_revision'], BASE)
        self.assertEqual(r['baseline_sha256'], hashlib.sha256(self.before_raw).hexdigest())
        self.assertEqual(r['target'], str(TARGET.relative_to(ROOT)))
        self.assertEqual(r['candidate_sha256'], hashlib.sha256(CANDIDATE.read_bytes()).hexdigest())
        self.assertEqual(r['application']['yaml_sha256'], hashlib.sha256(TARGET.read_bytes()).hexdigest())
        control = ROOT / r['greek_control']['repo_path']
        self.assertEqual(r['greek_control']['sha256'], hashlib.sha256(control.read_bytes()).hexdigest())
        self.assertEqual(r['application']['changed_export_units'], [[1, 9]])
        self.assertEqual(r['lexical_evidence']['response_sha256'],
                         '9ae5fdd15e38e6d4620de978f32ea8a76ce22056aa01cd526078331672e7160e')


if __name__ == '__main__':
    unittest.main()
