"""Correct the Greek/Hebrew distinction without rewriting the chosen source."""
import copy
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
from tools import export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '08b1aef09b1dae33f9b06aa31b55e64268e65d6b'
TARGET = 'translation/ot/jeremiah/031/032.yaml'
CONTRACT = 'sources/textual_restoration/comparisons/jeremiah31_reader_contract.2026-10-18.v1.json'
REPORT = 'docs/JEREMIAH_31_READER_NOTE_CORRECTION_2026-10-18.md'
RECEIPT = 'sources/textual_restoration/applications/jeremiah31_reader.2026-10-18.v1.json'
BEFORE_SHA = '1121182be0ca9f68f2df93f1d670edbd644542676da3d2b792aeb0d0d34dad20'
NOTE = 'Or, “though I was lord over them.” Greek Jeremiah 38:32 and Hebrews 8:9 instead have “and I disregarded them.” Whether this reflects another sense of the same Hebrew verb or a different Hebrew source remains disputed.'
LEXICAL = 'POB provisionally retains the covenantal husband metaphor; lord or master is another relational interpretation. Greek Jeremiah 38:32 and Hebrews 8:9 instead express disregard. A negative sense under the same Hebrew spelling has been proposed, but neither that interpretation nor a different Hebrew ancestor is established as earliest. The note distinguishes these alternatives rather than equating Greek disregard with dominion.'
THEOLOGICAL = 'Retain the husband interpretation provisionally while disclosing lord as an alternative and the Greek disregard wording separately. The relation between the Greek and Hebrew remains disputed; neither covenant theology nor the selected English settles historical source priority.'
SCOPE = 'Correct Jeremiah 31:32 disclosure and relocate its existing anchor; unchanged Hebrew and marker-free main English; source priority unresolved'
ARCHIVES = ['status', 'revision_pass', 'cross_check', 'translation.text',
            'translation.footnotes', 'lexical_decisions', 'theological_decisions']


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def expected(before):
    d = copy.deepcopy(before)
    old = before['translation']['text']
    assert old.count('[a]') == 1 and 'Egypt[a]' in old
    d['translation']['text'] = old.replace('Egypt[a]', 'Egypt').replace('husband,', 'husband[a],')
    d['translation']['footnotes'][0]['text'] = NOTE
    assert d['lexical_decisions'][8]['source_word'] == 'בָּעַלְתִּי בָם'
    d['lexical_decisions'][8]['rationale'] = LEXICAL
    d['theological_decisions'][0]['rationale'] = THEOLOGICAL
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
    d['revisions'].append({
        'date': '2026-10-18', 'agent': 'Codex', 'scope': SCOPE,
        'from': old, 'to': d['translation']['text'],
        'from_note': before['translation']['footnotes'][0]['text'], 'to_note': NOTE,
        'baseline_sha256': BEFORE_SHA, 'case_document': REPORT,
        'application_receipt': RECEIPT,
    })
    return d


class Jeremiah31ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads((ROOT / CONTRACT).read_text())
        raw = subprocess.check_output(['git', 'archive', BASELINE, 'translation/ot/jeremiah'], cwd=ROOT)
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
                           ('theological_rationale', THEOLOGICAL)]:
            self.assertEqual(self.c[key], value)
        self.assertEqual(self.candidate, expected(self.before))
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(self.candidate)
        for key in ['source', 'ai_draft']:
            self.assertEqual(self.candidate[key], self.before[key])
        plain = lambda s: re.sub(r'\[a\]', '', s)
        self.assertEqual(plain(self.candidate['translation']['text']), plain(self.before['translation']['text']))
        self.assertIn('husband[a],', self.candidate['translation']['text'])
        self.assertNotIn('Egypt[a]', self.candidate['translation']['text'])
        self.assertEqual(self.candidate['translation']['text'].count('[a]'), 1)
        self.assertEqual(self.candidate['lexical_decisions'][:8], self.before['lexical_decisions'][:8])
        self.assertEqual(self.candidate['lexical_decisions'][9:], self.before['lexical_decisions'][9:])
        for key in ['publication_approval', 'source_priority_approval',
                    'whole_verse_certification', 'external_reader_publisher_code_changed']:
            self.assertFalse(self.c[key])

    def test_evidence_and_implementation_pins(self):
        self.assertEqual(len(self.c['input_pins']), 12)
        for path, pin in self.c['input_pins'].items():
            historical = subprocess.check_output(['git', 'show', f'{BASELINE}:{path}'], cwd=ROOT)
            self.assertEqual(sha(historical), pin, path)
            if path != 'docs/TEXTUAL_ADJUDICATION_METHOD.md':
                self.assertEqual(sha((ROOT / path).read_bytes()), pin, path)

    def test_real_whole_jeremiah_export(self):
        self.assertEqual(len(self.book), 1364)
        records = {(int(Path(p).parent.name), int(Path(p).stem)): yaml.safe_load(raw)
                   for p, raw in self.book.items()}
        def load(current):
            def get(code, chapter, verse):
                self.assertEqual(code, 'JER')
                return current[(chapter, verse)]
            return get
        with patch.object(exporter, 'load_translation_record', side_effect=load(records)):
            before = exporter.export_book('JER')
        with patch.object(exporter, 'load_translation_record',
                          side_effect=load({**records, (31, 32): self.candidate})):
            after = exporter.export_book('JER')
        def index(book):
            return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}
        a, b = index(before), index(after)
        self.assertEqual(len(before['chapters']), 52)
        self.assertEqual(len(a), 1364)
        self.assertEqual(set(a), set(b))
        self.assertEqual([k for k in a if a[k] != b[k]], [(31, 32)])
        restored = copy.deepcopy(after)
        for chapter in restored['chapters']:
            for i, verse in enumerate(chapter['verses']):
                if (chapter['chapter'], verse['verse']) == (31, 32):
                    chapter['verses'][i] = a[(31, 32)]
        self.assertEqual(restored, before)
        target = copy.deepcopy(a[(31, 32)])
        target['text'] = self.candidate['translation']['text']
        target['footnotes'][0]['text'] = NOTE
        self.assertEqual(b[(31, 32)], target)

    def test_live_target_is_baseline_or_exact_candidate(self):
        self.assertIn(sha((ROOT / TARGET).read_bytes()),
                      (BEFORE_SHA, self.c['candidate_sha256']))


if __name__ == '__main__':
    unittest.main()
