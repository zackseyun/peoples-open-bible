"""Bounded disclosure/application checks, not proof of historical priority."""
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
BASE = 'c14ef7e301576128acd863042cdd667b27051dce'
TARGET = 'translation/ot/numbers/013/033.yaml'
CANDIDATE = 'sources/textual_restoration/candidates/numbers13_33.2026-10-05.v1.json'
RECEIPT = 'sources/textual_restoration/applications/numbers13_33.2026-10-05.v1.json'
ALIGNMENT = 'sources/textual_restoration/discovery/numbers13_33_alignment.2026-10-05.v1.json'
BEFORE_BOOK_SHA = '47469f0dc6dd390cb38525d0cfe0baaef347cde8981f01934f4d2c47e9dfce5a'
AFTER_BOOK_SHA = '294ff1fa618f8700450ccab7bf4c704c1d85f36572be0e35f1bb1a40875c3ee2'


class Numbers1333DisclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before_raw = subprocess.check_output(['git', 'show', f'{BASE}:{TARGET}'], cwd=ROOT)
        cls.before = yaml.safe_load(cls.before_raw)
        cls.current = yaml.safe_load((ROOT / TARGET).read_text())
        cls.candidate = json.loads((ROOT / CANDIDATE).read_text())

    def test_candidate_schema_and_unchanged_source_marker_free_english(self):
        self.assertEqual(self.current, self.candidate)
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(self.current)
        self.assertEqual(self.current['source'], self.before['source'])
        clean = lambda text: re.sub(r'\[[a-c]\]', '', text)
        self.assertEqual(clean(self.current['translation']['text']), clean(self.before['translation']['text']))
        self.assertEqual(self.current['translation']['philosophy'], self.before['translation']['philosophy'])

    def test_existing_note_retained_and_variant_notes_anchored(self):
        self.assertEqual(self.current['translation']['footnotes'][0], self.before['translation']['footnotes'][0])
        text = self.current['translation']['text']
        self.assertIn('the Nephilim[a]—the sons of Anak, from the Nephilim[b]—', text)
        self.assertIn('in their eyes[c].', text)
        for marker in 'abc':
            self.assertEqual(text.count(f'[{marker}]'), 1)
        self.assertNotIn('Anak[a]', text)
        self.assertEqual(audit_footnotes.audit_one(ROOT / TARGET)['status'], 'ok')
        greek, samaritan = self.current['translation']['footnotes'][1:]
        self.assertEqual(greek['marker'], 'b')
        self.assertEqual(samaritan['marker'], 'c')
        self.assertEqual(greek['reason'], 'textual_variant')
        self.assertEqual(samaritan['reason'], 'textual_variant')
        for phrase in ('Vaticanus-based', 'other Greek readings', 'retains the Hebrew clause'):
            self.assertIn(phrase, greek['text'])
        for phrase in ('transcription compared here', 'adapted', 'Deuteronomy 1:27–33',
                       'God hates them', 'Moses urges courage', 'unresolved', 'provisionally'):
            self.assertIn(phrase, samaritan['text'])
        self.assertNotIn('verbatim', samaritan['text'])

    def test_old_reviews_archived_without_new_certification(self):
        history = self.current['review_history']
        self.assertEqual([h['field'] for h in history], ['status', 'revision_pass', 'cross_check'])
        self.assertEqual({h['field']: h['value'] for h in history},
                         {f: self.before[f] for f in ('status', 'revision_pass', 'cross_check')})
        digest = hashlib.sha256(self.before_raw).hexdigest()
        self.assertTrue(all(h['archived_from_baseline_sha256'] == digest for h in history))
        self.assertTrue(all(not h['certifies_this_candidate'] for h in history))
        for field in ('ai_draft', 'lexical_decisions', 'theological_decisions'):
            self.assertEqual(self.current[field], self.before[field])
        self.assertEqual(self.current.get('revisions'), self.before.get('revisions'))
        self.assertEqual(self.current['status'], 'draft')
        self.assertEqual(self.current['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', self.current)
        comparison = self.current['textual_comparison']
        self.assertEqual(comparison['historical_priority'], 'unresolved')
        self.assertEqual(comparison['main_english_outcome'], 'unchanged')
        self.assertFalse(comparison['fresh_image_reading'])
        self.assertFalse(comparison['publication_approved'])

    def test_current_complete_book_changes_only_target_disclosure(self):
        after = exporter.export_book('NUM')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda code, ch, v:
                          self.before if (code, ch, v) == ('NUM', 13, 33) else loader(code, ch, v)):
            before = exporter.export_book('NUM')
        index = lambda book: {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 36)
        self.assertEqual(len(a), 1289)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([key for key in a if a[key] != b[key]], [(13, 33)])
        self.assertEqual(a[(13, 33)]['footnotes'], self.current['translation']['footnotes'])
        clean = lambda text: re.sub(r'\[[a-c]\]', '', text)
        self.assertEqual(clean(a[(13, 33)]['text']), clean(b[(13, 33)]['text']))

    def test_historical_baseline_plus_candidate_book_digests(self):
        # Receipts remain about their original snapshot, not every later edit.
        archive = subprocess.check_output(['git', 'archive', BASE, 'translation/ot/numbers'], cwd=ROOT)
        historical = {}
        with tarfile.open(fileobj=io.BytesIO(archive)) as snapshot:
            for member in snapshot.getmembers():
                if member.isfile() and member.name.endswith('.yaml'):
                    path = Path(member.name)
                    historical[(int(path.parent.name), int(path.stem))] = yaml.safe_load(
                        snapshot.extractfile(member).read())
        self.assertEqual(len(historical), 1289)
        loader = exporter.load_translation_record
        def snapshot_record(code, chapter, verse, candidate=False):
            if code != 'NUM':
                return loader(code, chapter, verse)
            if candidate and (chapter, verse) == (13, 33):
                return self.candidate
            return historical.get((chapter, verse))
        with patch.object(exporter, 'load_translation_record', side_effect=snapshot_record):
            before = exporter.export_book('NUM')
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v:
                          snapshot_record(c, ch, v, candidate=True)):
            after = exporter.export_book('NUM')
        application = json.loads((ROOT / RECEIPT).read_text())['application']
        for key, book, expected in (
                ('export_before_sha256', before, BEFORE_BOOK_SHA),
                ('export_after_sha256', after, AFTER_BOOK_SHA)):
            self.assertEqual(hashlib.sha256(json.dumps(book, ensure_ascii=False, sort_keys=True).encode()).hexdigest(), expected)
            self.assertEqual(application[key], expected)

    def test_receipt_binds_inputs_application_and_uncertainty(self):
        receipt = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(receipt['baseline_revision'], BASE)
        self.assertEqual(receipt['target'], TARGET)
        self.assertEqual(receipt['candidate'], CANDIDATE)
        self.assertEqual(receipt['candidate_sha256'], hashlib.sha256((ROOT / CANDIDATE).read_bytes()).hexdigest())
        self.assertEqual(receipt['baseline_sha256'], hashlib.sha256(self.before_raw).hexdigest())
        self.assertEqual(receipt['alignment']['repo_path'], ALIGNMENT)
        self.assertEqual(receipt['alignment']['sha256'], hashlib.sha256((ROOT / ALIGNMENT).read_bytes()).hexdigest())
        application = receipt['application']
        self.assertEqual(application['yaml_sha256'], hashlib.sha256((ROOT / TARGET).read_bytes()).hexdigest())
        self.assertEqual(application['changed_export_units'], [[13, 33]])
        self.assertEqual(application['chapters'], 36)
        self.assertEqual(application['verses'], 1289)
        for flag in ('source_changed', 'marker_free_english_changed', 'novel_reading_demonstrated',
                     'canon_changed', 'fresh_image_reading', 'publication_approved'):
            self.assertFalse(receipt['decision'][flag])


if __name__ == '__main__':
    unittest.main()
