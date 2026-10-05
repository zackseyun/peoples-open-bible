"""Scoped integrity checks, not adjudication of Hebrew historical priority."""
import hashlib
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

import yaml
from jsonschema import Draft202012Validator

from tools import export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]
TARGET = 'translation/ot/judges/020/048.yaml'
CANDIDATE = 'sources/textual_restoration/candidates/judges20_48.2026-10-05.v1.json'
RECEIPT = 'sources/textual_restoration/applications/judges20_48.2026-10-05.v1.json'
BASE = '015bdfa7dcec66acfc40217a3085b0e75b82c90e'


class JudgesPointingApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before_raw = subprocess.run(
            ['git', 'show', f'{BASE}:{TARGET}'], cwd=ROOT,
            capture_output=True, check=True).stdout
        cls.before = yaml.safe_load(cls.before_raw)
        cls.raw = (ROOT / TARGET).read_bytes()
        cls.current = yaml.safe_load(cls.raw)
        cls.candidate = json.loads((ROOT / CANDIDATE).read_text())
        cls.receipt = json.loads((ROOT / RECEIPT).read_text())

    def test_application_is_exact_reviewed_candidate(self):
        self.assertEqual(self.current, self.candidate)
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(),
                         self.receipt['application']['applied_yaml_sha256'])
        self.assertEqual(hashlib.sha256((ROOT / CANDIDATE).read_bytes()).hexdigest(),
                         self.receipt['candidate_sha256'])
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(self.current)

    def test_diplomatic_source_and_minimal_working_vowel_are_distinct(self):
        self.assertEqual(self.current['source']['text'], self.before['source']['text'])
        self.assertEqual(self.current['source']['edition'], 'WLC')
        interpretation = self.current['source_interpretation']
        self.assertEqual(interpretation['working_source_text'],
                         self.before['source']['text'].replace('מְתֹם֙', 'מְתִם֙'))
        self.assertTrue(interpretation['diplomatic_source_retained'])
        self.assertEqual(interpretation['historical_priority'], 'unresolved')
        self.assertFalse(interpretation['publication_approved'])
        self.assertIn('וַ/יַּכּ֣וּ/ם', interpretation['working_source_text'])

    def test_old_review_values_do_not_certify_new_record(self):
        archive = {h['field']: h['value'] for h in self.current['review_history']}
        self.assertEqual(archive, {f: self.before[f] for f in ('status', 'revision_pass', 'cross_check')})
        self.assertTrue(all(not h['certifies_this_candidate'] for h in self.current['review_history']))
        self.assertEqual(self.current['ai_draft'], self.before['ai_draft'])
        self.assertEqual(self.current['revisions'][:-1], self.before['revisions'])
        self.assertEqual(self.current['status'], 'draft')
        self.assertEqual(self.current['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', self.current)

    def test_notes_are_qualified_and_correctly_anchored(self):
        text = self.current['translation']['text']
        self.assertIn('sons of Benjamin[a]', text)
        self.assertIn('inhabitants of the cities[b] to livestock', text)
        self.assertIn('set on fire[c]', text)
        for marker in ('a', 'b', 'c'):
            self.assertEqual(text.count(f'[{marker}]'), 1)
        notes = self.current['translation']['footnotes']
        self.assertEqual(notes[0], self.before['translation']['footnotes'][0])
        self.assertEqual(notes[2], self.before['translation']['footnotes'][2])
        self.assertEqual(notes[1]['reason'], 'textual_variant')
        for phrase in ('alternative vocalization', 'retained WLC', 'both vowel marks',
                       'earlier wording remain uncertain', 'singular city collectively'):
            self.assertIn(phrase, notes[1]['text'])

    def test_complete_book_export_changes_only_target(self):
        after = exporter.export_book('JDG')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda code, ch, v:
                          self.before if (code, ch, v) == ('JDG', 20, 48) else loader(code, ch, v)):
            before = exporter.export_book('JDG')
        index = lambda book: {(c['chapter'], v['verse']): v
                              for c in book['chapters'] for v in c['verses']}
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 21)
        self.assertEqual(len(a), 618)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([k for k in a if a[k] != b[k]], [(20, 48)])
        self.assertEqual(a[(20, 48)]['footnotes'], self.current['translation']['footnotes'])
        digest = lambda x: hashlib.sha256(json.dumps(x, ensure_ascii=False, sort_keys=True,
                                                   separators=(',', ':')).encode()).hexdigest()
        self.assertEqual(digest(b[(20, 48)]), self.receipt['application']['before_target_export_sha256'])
        self.assertEqual(digest(a[(20, 48)]), self.receipt['application']['actual_target_export_sha256'])

    def test_frozen_protocol_precedes_and_binds_the_comparison(self):
        path = self.receipt['protocol']
        raw = (ROOT / path).read_bytes()
        protocol = json.loads(raw)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.receipt['input_pins'][path])
        self.assertEqual(protocol['baseline']['sha256'], hashlib.sha256(self.before_raw).hexdigest())
        self.assertEqual(protocol['candidates']['T'], self.current['translation']['text']
                         .replace('[a]', '').replace('[b]', '').replace('[c]', ''))
        self.assertFalse(self.receipt['english_comparison']['randomized_order'])


if __name__ == '__main__':
    unittest.main()
