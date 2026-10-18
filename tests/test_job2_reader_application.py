"""Qualify an interpretation note without changing the selected Hebrew or English."""
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import unittest
from unittest.mock import patch

import yaml
from jsonschema import Draft202012Validator
from tools import export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '254512e48dce73421dc3eca449d2413625a3ee2c'
TARGET = 'translation/ot/job/002/009.yaml'
CONTRACT = 'sources/textual_restoration/comparisons/job2_reader_contract.2026-10-18.v1.json'
REPORT = 'docs/JOB_2_READER_QUALIFICATION_2026-10-18.md'
RECEIPT = 'sources/textual_restoration/applications/job2_reader.2026-10-18.v1.json'
BEFORE_SHA = '6df4ffe64917aa477c6ff35aa06d3955b7cb16c6ed8679b5da9ac5e24680e007'
NOTE = 'Hebrew literally “Bless God and die.” POB interprets “bless” here as an indirect way of saying “curse,” in light of 1:11; 2:5 and Job’s reply in 2:10. A literal blessing before death remains another interpretation.'
LEXICAL = 'The written verb normally means “bless.” POB provisionally renders its contextual force as “curse,” comparing 1:11; 2:5 and the reply in 2:10. Literal blessing before death remains an interpretive alternative; neither interpretation requires different Hebrew letters.'
THEOLOGICAL = 'Retain the contextual “Curse God and die” in the main text, with the literal Hebrew “Bless God and die” and the competing blessing interpretation disclosed in the note.'
RATIONALE = 'The source spelling is unchanged. The prologue and Job’s reply support the contextual rendering, but a literal blessing interpretation remains viable. The current main text and note must be described consistently, without treating this provisional interpretation as a settled source-text result.'
SCOPE = 'Qualify the existing Job 2:9 interpretation note and align active lexical/theological rationale; unchanged Hebrew, full marked main English and anchor; no whole-verse or source-priority certification'
ARCHIVES = ['status', 'revision_pass', 'cross_check', 'source_audit',
            'translation.footnotes', 'lexical_decisions', 'theological_decisions']


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def expected(before):
    d = copy.deepcopy(before)
    d['translation']['footnotes'][0]['text'] = NOTE
    assert d['lexical_decisions'][5]['source_word'] == 'בָּרֵךְ'
    d['lexical_decisions'][5]['alternatives'] = ['Bless']
    d['lexical_decisions'][5]['rationale'] = LEXICAL
    d['theological_decisions'][0]['chosen_reading'] = THEOLOGICAL
    d['theological_decisions'][0]['alternative_readings'] = ['Bless God and die']
    d['theological_decisions'][0]['rationale'] = RATIONALE
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
            'archived_from_baseline_sha256': BEFORE_SHA,
            'historical_review_inputs_verified': False,
            'certifies_this_candidate': False,
        })
    d['revisions'].append({
        'date': '2026-10-18', 'agent': 'Codex', 'scope': SCOPE,
        'from_note': before['translation']['footnotes'][0]['text'], 'to_note': NOTE,
        'baseline_sha256': BEFORE_SHA, 'case_document': REPORT,
        'application_receipt': RECEIPT,
    })
    return d


class Job2ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads((ROOT / CONTRACT).read_text())
        raw = subprocess.check_output(['git', 'archive', BASELINE, 'translation/ot/job'], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
            cls.book = {m.name: archive.extractfile(m).read() for m in archive.getmembers()
                        if m.isfile() and m.name.endswith('.yaml')}
        cls.before = yaml.safe_load(cls.book[TARGET])
        cls.candidate_raw = (ROOT / cls.c['candidate']).read_bytes()
        cls.candidate = yaml.safe_load(cls.candidate_raw)

    def test_exact_record_schema_and_archives(self):
        self.assertEqual(self.c['baseline_commit'], BASELINE)
        self.assertEqual(self.c['target'], TARGET)
        self.assertEqual(sha(self.book[TARGET]), BEFORE_SHA)
        self.assertEqual(self.c['baseline_sha256'], BEFORE_SHA)
        self.assertEqual(sha(self.candidate_raw), self.c['candidate_sha256'])
        self.assertEqual(self.c['archives'], ARCHIVES)
        for key, value in [('note', NOTE), ('lexical_rationale', LEXICAL),
                           ('theological_chosen_reading', THEOLOGICAL),
                           ('theological_rationale', RATIONALE)]:
            self.assertEqual(self.c[key], value)
        self.assertEqual(self.candidate, expected(self.before))
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(self.candidate)
        for key in ['source', 'ai_draft']:
            self.assertEqual(self.candidate[key], self.before[key])
        self.assertEqual(self.candidate['translation']['text'], self.before['translation']['text'])
        self.assertEqual(self.candidate['lexical_decisions'][:5], self.before['lexical_decisions'][:5])
        self.assertEqual(self.candidate['lexical_decisions'][6:], self.before['lexical_decisions'][6:])
        for key in ['publication_approval', 'source_priority_approval',
                    'whole_verse_certification', 'external_reader_publisher_code_changed']:
            self.assertFalse(self.c[key])

    def test_evidence_and_implementation_pins(self):
        self.assertEqual(len(self.c['input_pins']), 10)
        for path, pin in self.c['input_pins'].items():
            historical = subprocess.check_output(['git', 'show', f'{BASELINE}:{path}'], cwd=ROOT)
            self.assertEqual(sha(historical), pin, path)
            if path != 'docs/TEXTUAL_ADJUDICATION_METHOD.md':
                self.assertEqual(sha((ROOT / path).read_bytes()), pin, path)

    def test_real_whole_job_export(self):
        self.assertEqual(len(self.book), 1070)
        records = {(int(Path(p).parent.name), int(Path(p).stem)): yaml.safe_load(raw)
                   for p, raw in self.book.items()}
        def load(current):
            def get(code, chapter, verse):
                self.assertEqual(code, 'JOB')
                return current[(chapter, verse)]
            return get
        with patch.object(exporter, 'load_translation_record', side_effect=load(records)):
            before = exporter.export_book('JOB')
        with patch.object(exporter, 'load_translation_record',
                          side_effect=load({**records, (2, 9): self.candidate})):
            after = exporter.export_book('JOB')
        def index(book):
            return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}
        a, b = index(before), index(after)
        self.assertEqual(len(before['chapters']), 42)
        self.assertEqual(len(a), 1070)
        self.assertEqual(set(a), set(b))
        self.assertEqual([k for k in a if a[k] != b[k]], [(2, 9)])
        restored = copy.deepcopy(after)
        for chapter in restored['chapters']:
            for i, verse in enumerate(chapter['verses']):
                if (chapter['chapter'], verse['verse']) == (2, 9):
                    chapter['verses'][i] = a[(2, 9)]
        self.assertEqual(restored, before)
        target = copy.deepcopy(a[(2, 9)])
        target['footnotes'][0]['text'] = NOTE
        self.assertEqual(b[(2, 9)], target)

    def test_live_target_is_baseline_or_exact_candidate(self):
        self.assertIn(sha((ROOT / TARGET).read_bytes()),
                      (BEFORE_SHA, self.c['candidate_sha256']))


if __name__ == '__main__':
    unittest.main()
