"""Scoped application integrity; not proof of narrative historical priority."""
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
BASE = '812b40b4583513af6d7832f24f85ec93a7f7666a'
TARGET = 'translation/ot/numbers/020/013.yaml'
CANDIDATE = 'sources/textual_restoration/candidates/numbers20_13.2026-10-05.v1.json'
RECEIPT = 'sources/textual_restoration/applications/numbers20_13.2026-10-05.v1.json'


class NumbersDisclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before_raw = subprocess.check_output(['git', 'show', f'{BASE}:{TARGET}'], cwd=ROOT)
        cls.before = yaml.safe_load(cls.before_raw)
        cls.current = yaml.safe_load((ROOT / TARGET).read_text())
        cls.candidate = json.loads((ROOT / CANDIDATE).read_text())

    def test_exact_candidate_schema_and_unchanged_source_main_english(self):
        self.assertEqual(self.current, self.candidate)
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(self.current)
        self.assertEqual(self.current['source'], self.before['source'])
        clean = lambda text: re.sub(r'\[[a-c]\]', '', text)
        self.assertEqual(clean(self.current['translation']['text']), clean(self.before['translation']['text']))

    def test_existing_notes_retained_and_anchor_repaired(self):
        self.assertEqual(self.current['translation']['footnotes'][:2], self.before['translation']['footnotes'])
        text = self.current['translation']['text']
        self.assertIn('Meribah[a]', text)
        self.assertIn('Yahweh,', text)
        self.assertIn('holy among them[b][c].', text)
        for marker in 'abc':
            self.assertEqual(text.count(f'[{marker}]'), 1)
        self.assertEqual(audit_footnotes.audit_one(ROOT / TARGET)['status'], 'ok')
        note = self.current['translation']['footnotes'][2]
        self.assertEqual(note['reason'], 'textual_variant')
        for phrase in ('transcription compared here', 'Joshua', 'Edom', 'paralleling', 'provisionally'):
            self.assertIn(phrase, note['text'])
        self.assertNotIn('verbatim', note['text'])

    def test_historical_reviews_not_transferred(self):
        history = self.current['review_history']
        self.assertEqual({h['field']: h['value'] for h in history},
                         {f: self.before[f] for f in ('status', 'revision_pass', 'cross_check')})
        self.assertTrue(all(not h['certifies_this_candidate'] for h in history))
        for field in ('ai_draft', 'lexical_decisions', 'theological_decisions', 'revisions'):
            self.assertEqual(self.current[field], self.before[field])
        self.assertEqual(self.current['status'], 'draft')
        self.assertEqual(self.current['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', self.current)
        self.assertEqual(self.current['textual_comparison']['historical_priority'], 'unresolved')
        self.assertFalse(self.current['textual_comparison']['publication_approved'])

    def test_full_numbers_export_changes_only_target_notes_and_markers(self):
        after = exporter.export_book('NUM')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda code, ch, v:
                          self.before if (code, ch, v) == ('NUM', 20, 13) else loader(code, ch, v)):
            before = exporter.export_book('NUM')
        index = lambda book: {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}
        a, b = index(after), index(before)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([key for key in a if a[key] != b[key]], [(20, 13)])
        self.assertEqual(a[(20, 13)]['footnotes'], self.current['translation']['footnotes'])

    def test_historical_book_digests_remain_bound_to_original_snapshot(self):
        # Later Numbers applications are not changes to this historical receipt.
        # Current-book isolation is checked separately in the preceding test.
        archive = subprocess.check_output(['git', 'archive', BASE, 'translation/ot/numbers'], cwd=ROOT)
        historical = {}
        with tarfile.open(fileobj=io.BytesIO(archive)) as snapshot:
            for member in snapshot.getmembers():
                if member.isfile() and member.name.endswith('.yaml'):
                    path = Path(member.name)
                    historical[(int(path.parent.name), int(path.stem))] = yaml.safe_load(
                        snapshot.extractfile(member).read())
        loader = exporter.load_translation_record
        def snapshot_record(code, chapter, verse, candidate=False):
            if code != 'NUM':
                return loader(code, chapter, verse)
            if candidate and (chapter, verse) == (20, 13):
                return self.candidate
            return historical.get((chapter, verse))
        with patch.object(exporter, 'load_translation_record', side_effect=snapshot_record):
            before = exporter.export_book('NUM')
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v:
                          snapshot_record(c, ch, v, candidate=True)):
            after = exporter.export_book('NUM')
        application = json.loads((ROOT / RECEIPT).read_text())['application']
        expected = {
            'export_before_sha256': '49aee56142c6c10083e64bea17c32f6c051e07b5a35f1681f0f51ecb31845e9c',
            'export_after_sha256': '47469f0dc6dd390cb38525d0cfe0baaef347cde8981f01934f4d2c47e9dfce5a',
        }
        for key, book in (('export_before_sha256', before), ('export_after_sha256', after)):
            digest = hashlib.sha256(json.dumps(book, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            self.assertEqual(digest, expected[key])
            self.assertEqual(application[key], expected[key])

    def test_receipt_binds_application_and_uncertainty(self):
        receipt = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(receipt['candidate_sha256'], hashlib.sha256((ROOT / CANDIDATE).read_bytes()).hexdigest())
        self.assertEqual(receipt['application']['yaml_sha256'], hashlib.sha256((ROOT / TARGET).read_bytes()).hexdigest())
        self.assertEqual(receipt['baseline_sha256'], hashlib.sha256(self.before_raw).hexdigest())
        discovery = receipt['discovery']
        self.assertEqual(discovery['sha256'], hashlib.sha256((ROOT / discovery['repo_path']).read_bytes()).hexdigest())
        self.assertEqual(receipt['application']['changed_export_units'], [[20, 13]])
        self.assertFalse(receipt['decision']['source_changed'])
        self.assertFalse(receipt['decision']['novel_reading_demonstrated'])
        self.assertFalse(receipt['decision']['canon_changed'])
        self.assertFalse(receipt['decision']['fresh_image_reading'])


if __name__ == '__main__':
    unittest.main()
