"""Disclose the shorter Judges unit without choosing or removing main text."""
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
BASELINE = '7c6b9bb703e55380b02ee50aaa15c0fb6b1a9e54'
TARGET = 'translation/ot/judges/006/007.yaml'
CONTRACT = 'sources/textual_restoration/comparisons/judges6_reader_note_contract.2026-10-18.v1.json'
NOTE = "Or 'on account of Midian.' The Qumran manuscript 4QJudgesᵃ (4Q49) supports a shorter form without verses 7–10; the exact junction is partly reconstructed from adjacent surviving lines. Whether this reflects an earlier literary stage or a copying omission remains disputed."
ARCHIVES = ['status', 'revision_pass', 'cross_check', 'translation.footnotes']
REPORT = 'docs/JUDGES_6_READER_NOTE_2026-10-18.md'
RECEIPT = 'sources/textual_restoration/applications/judges6_reader_note.2026-10-18.v1.json'
SCOPE = 'Existing Judges6:7 note b source-variant disclosure only; source, full marked main English, anchors and note a unchanged; no historical-priority or whole-verse certification'
BEFORE_SHA = '19630958414b82e4b3697c8644e266c3b7c877261b762cf89cc3567748b5cc12'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def expected(before):
    d = copy.deepcopy(before)
    d['translation']['footnotes'][1]['text'] = NOTE
    d['translation']['footnotes'][1]['reason'] = 'alternative_reading'
    d['status'] = 'draft'
    d['cross_check'] = {'status': 'needs_review'}
    d.pop('revision_pass')
    for field in ARCHIVES:
        value = before
        for part in field.split('.'):
            value = value[part]
        d.setdefault('review_history', []).append({
            'field': field, 'value': copy.deepcopy(value),
            'archived_from_baseline_commit': BASELINE,
            'archived_from_baseline_sha256': BEFORE_SHA,
            'historical_review_inputs_verified': False,
            'certifies_this_candidate': False,
        })
    d.setdefault('revisions', []).append({
        'date': '2026-10-18', 'agent': 'Codex', 'scope': SCOPE,
        'from_note': before['translation']['footnotes'][1]['text'], 'to_note': NOTE,
        'baseline_sha256': BEFORE_SHA,
        'case_document': REPORT, 'application_receipt': RECEIPT,
    })
    return d


class Judges6NoteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads((ROOT / CONTRACT).read_text())
        raw = subprocess.check_output(['git', 'archive', BASELINE, 'translation/ot/judges'], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
            cls.book = {m.name: archive.extractfile(m).read() for m in archive.getmembers()
                        if m.isfile() and m.name.endswith('.yaml')}
        cls.before = yaml.safe_load(cls.book[TARGET])
        cls.candidate_raw = (ROOT / cls.c['candidate']).read_bytes()
        cls.candidate = yaml.safe_load(cls.candidate_raw)

    def test_exact_record_schema_and_review_archives(self):
        self.assertEqual(self.c['baseline_commit'], BASELINE)
        self.assertEqual(self.c['target'], TARGET)
        self.assertEqual(sha(self.book[TARGET]), BEFORE_SHA)
        self.assertEqual(BEFORE_SHA, self.c['baseline_sha256'])
        self.assertEqual(sha(self.candidate_raw), self.c['candidate_sha256'])
        self.assertEqual(self.c['note'], NOTE)
        self.assertEqual(self.c['archives'], ARCHIVES)
        self.assertEqual(self.candidate, expected(self.before))
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(self.candidate)
        for key in ['source', 'ai_draft', 'lexical_decisions', 'theological_decisions']:
            self.assertEqual(self.candidate[key], self.before[key])
        self.assertEqual(self.candidate['translation']['text'], self.before['translation']['text'])
        self.assertEqual(self.candidate['translation']['footnotes'][0], self.before['translation']['footnotes'][0])
        self.assertEqual([n['marker'] for n in self.candidate['translation']['footnotes']], ['a', 'b'])
        self.assertEqual(len(self.candidate['translation']['footnotes']), 2)
        for key in ['publication_approval', 'historical_priority_approval', 'whole_verse_certification', 'external_reader_publisher_code_changed']:
            self.assertFalse(self.c[key])

    def test_evidence_and_implementation_pins(self):
        self.assertEqual(len(self.c['input_pins']), 6)
        for path, pin in self.c['input_pins'].items():
            historical = subprocess.check_output(['git', 'show', f'{BASELINE}:{path}'], cwd=ROOT)
            self.assertEqual(sha(historical), pin, path)
            if path != 'docs/TEXTUAL_ADJUDICATION_METHOD.md':
                self.assertEqual(sha((ROOT / path).read_bytes()), pin, path)

    def test_real_whole_judges_export(self):
        self.assertEqual(len(self.book), 618)
        with tempfile.TemporaryDirectory(prefix='pob-judges6-export-') as tmp:
            folder = Path(tmp)
            for path, raw in self.book.items():
                dest = folder / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)
            # Non-Psalm canonical books load through draft's path resolver.
            # Patch both roots so this exercises the temporary historical book,
            # never the unchanged live tree.
            with patch.object(exporter, 'TRANSLATION_ROOT', folder / 'translation'), \
                    patch.object(exporter.draft, 'TRANSLATION_ROOT', folder / 'translation'):
                before = exporter.export_book('JDG')
                (folder / TARGET).write_bytes(self.candidate_raw)
                after = exporter.export_book('JDG')
        def index(book):
            return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}
        a, b = index(before), index(after)
        self.assertEqual(len(before['chapters']), 21)
        self.assertEqual(len(a), 618)
        self.assertEqual(set(a), set(b))
        self.assertEqual([k for k in a if a[k] != b[k]], [(6, 7)])
        restored = copy.deepcopy(after)
        for chapter in restored['chapters']:
            for i, verse in enumerate(chapter['verses']):
                if (chapter['chapter'], verse['verse']) == (6, 7):
                    chapter['verses'][i] = a[(6, 7)]
        self.assertEqual(restored, before)
        target = copy.deepcopy(a[(6, 7)])
        target['footnotes'][1]['text'] = NOTE
        target['footnotes'][1]['reason'] = 'alternative_reading'
        self.assertEqual(b[(6, 7)], target)

    def test_live_target_is_reviewed_baseline_or_candidate(self):
        self.assertIn(sha((ROOT / TARGET).read_bytes()),
                      (self.c['baseline_sha256'], self.c['candidate_sha256']))


if __name__ == '__main__':
    unittest.main()
