"""Qualify one existing note without choosing the earliest Greek reading."""
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import yaml
from jsonschema import Draft202012Validator
from tools import export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '22ce1fa4b1f4ed7a7c5c8768bf7a2eafb8e48aec'
TARGET = 'translation/ot/psalms/040/006.yaml'
CONTRACT = 'sources/textual_restoration/comparisons/psalm40_reader_note_contract.2026-10-18.v1.json'
NOTE = 'Hebrew: “ears you have dug for me,” likely an idiom for enabling hearing or obedience. Greek texts differ: Swete’s edition prints “a body you prepared for me,” as in Hebrews 10:5; Rahlfs–Hanhart’s edition prints “ears you prepared for me.” Which Greek reading is earlier remains disputed.'
ARCHIVES = ['status', 'revision_pass', 'cross_check', 'source_audit', 'translation.footnotes']
REPORT = 'docs/PSALM_40_READER_NOTE_2026-10-18.md'
RECEIPT = 'sources/textual_restoration/applications/psalm40_reader_note.2026-10-18.v1.json'
SCOPE = 'Existing Psalm40:6 note b qualification only; source, main English and anchors unchanged; no Greek-priority or whole-verse certification'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def expected(before):
    d = copy.deepcopy(before)
    d['translation']['footnotes'][1]['text'] = NOTE
    d['status'] = 'draft'
    d['cross_check'] = {'status': 'needs_review'}
    d.pop('revision_pass')
    d.pop('source_audit')
    for field in ARCHIVES:
        value = before
        for part in field.split('.'):
            value = value[part]
        d.setdefault('review_history', []).append({
            'field': field, 'value': copy.deepcopy(value),
            'archived_from_baseline_commit': BASELINE,
            'archived_from_baseline_sha256': 'e44accd06103a1ed19df77fb723cab15e0dd29c37623d3008d025ececda37ba7',
            'historical_review_inputs_verified': False,
            'certifies_this_candidate': False,
        })
    d['revisions'].append({
        'date': '2026-10-18', 'agent': 'Codex', 'scope': SCOPE,
        'from_note': before['translation']['footnotes'][1]['text'], 'to_note': NOTE,
        'baseline_sha256': 'e44accd06103a1ed19df77fb723cab15e0dd29c37623d3008d025ececda37ba7',
        'case_document': REPORT, 'application_receipt': RECEIPT,
    })
    return d


class Psalm40NoteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads((ROOT / CONTRACT).read_text())
        raw = subprocess.check_output(['git', 'archive', BASELINE, 'translation/ot/psalms'], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
            cls.book = {m.name: archive.extractfile(m).read() for m in archive.getmembers()
                        if m.isfile() and m.name.endswith('.yaml')}
        cls.before = yaml.safe_load(cls.book[TARGET])
        cls.candidate_raw = (ROOT / cls.c['candidate']).read_bytes()
        cls.candidate = yaml.safe_load(cls.candidate_raw)

    def test_exact_record_schema_and_review_archives(self):
        self.assertEqual(self.c['baseline_commit'], BASELINE)
        self.assertEqual(self.c['target'], TARGET)
        self.assertEqual(sha(self.book[TARGET]), self.c['baseline_sha256'])
        self.assertEqual(sha(self.candidate_raw), self.c['candidate_sha256'])
        self.assertEqual(self.c['note'], NOTE)
        self.assertEqual(self.c['archives'], ARCHIVES)
        self.assertEqual(self.candidate, expected(self.before))
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(self.candidate)
        for key in ['source', 'ai_draft', 'lexical_decisions', 'theological_decisions']:
            self.assertEqual(self.candidate[key], self.before[key])
        self.assertEqual(self.candidate['translation']['text'], self.before['translation']['text'])
        self.assertEqual(self.candidate['translation']['footnotes'][0], self.before['translation']['footnotes'][0])
        for key in ['publication_approval', 'greek_priority_approval', 'whole_verse_certification', 'external_reader_publisher_code_changed']:
            self.assertFalse(self.c[key])

    def test_evidence_and_implementation_pins(self):
        self.assertEqual(len(self.c['input_pins']), 9)
        for path, pin in self.c['input_pins'].items():
            historical = subprocess.check_output(['git', 'show', f'{BASELINE}:{path}'], cwd=ROOT)
            self.assertEqual(sha(historical), pin, path)
            if path != 'docs/TEXTUAL_ADJUDICATION_METHOD.md':
                self.assertEqual(sha((ROOT / path).read_bytes()), pin, path)

    def test_real_whole_psalter_export(self):
        self.assertEqual(len(self.book), 2578)
        with tempfile.TemporaryDirectory(prefix='pob-psalm40-export-') as tmp:
            folder = Path(tmp)
            for path, raw in self.book.items():
                dest = folder / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)
            with patch.object(exporter, 'TRANSLATION_ROOT', folder / 'translation'):
                before = exporter.export_book('PSA')
                (folder / TARGET).write_bytes(self.candidate_raw)
                after = exporter.export_book('PSA')
        def index(book):
            return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}
        a, b = index(before), index(after)
        self.assertEqual(len(before['chapters']), 150)
        self.assertEqual(len(a), 2578)
        self.assertEqual(set(a), set(b))
        self.assertEqual([k for k in a if a[k] != b[k]], [(40, 6)])
        restored = copy.deepcopy(after)
        for chapter in restored['chapters']:
            for i, verse in enumerate(chapter['verses']):
                if (chapter['chapter'], verse['verse']) == (40, 6):
                    chapter['verses'][i] = a[(40, 6)]
        self.assertEqual(restored, before)
        target = copy.deepcopy(a[(40, 6)])
        target['footnotes'][1]['text'] = NOTE
        self.assertEqual(b[(40, 6)], target)

    def test_live_target_is_reviewed_baseline_or_candidate(self):
        self.assertIn(sha((ROOT / TARGET).read_bytes()),
                      (self.c['baseline_sha256'], self.c['candidate_sha256']))


if __name__ == '__main__':
    unittest.main()
