"""Disclose the attested Chronicles age alternatives without changing the base."""
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
BASE = 'a0ae3c29b4525087faa1ceab1ed2822301aa2f37'
BOOK = 'translation/ot/2_chronicles'
TARGET = BOOK + '/022/002.yaml'
CANDIDATE = 'sources/textual_restoration/candidates/chronicles22_2_reader.2026-10-19.v1.yaml'
PACKET = 'sources/textual_restoration/comparisons/chronicles22_2_apparatus.2026-10-19.v1.json'
NOTE = "Hebrew: 'forty-two.' Some Greek manuscripts and the Syriac text read 'twenty-two,' as in 2 Kings 8:26; other Greek witnesses read 'twenty.' The original age in Chronicles is uncertain."
THEOLOGY = {
    'issue': 'Chronological tension in Ahaziah’s accession age',
    'chosen_reading': "Retain the recorded WLC wording 'forty-two years old' provisionally in this working verse.",
    'alternative_readings': [
        'Twenty-two, attested in Greek manuscript reports and the consulted Syriac text, also matching 2 Kings 8:26.',
        'Twenty, the selected Greek text and another reported Greek word order.',
        'A dynastic-age interpretation has been proposed but is not established by the consulted age formula.'],
    'rationale': 'The recorded Hebrew numeral is forty-two; its ordinary age interpretation conflicts with the connected father/son chronology. Twenty-two is an attested correction candidate, not merely a modern attempt to reconcile the accounts. Harmonization remains a possible transmission explanation, not an observed fact, and twenty remains another Greek reading. Retaining this WLC working record does not certify forty-two as earliest. Selecting another Hebrew numeral requires a separate explicitly reconstructed critical-source record.',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class ChroniclesAgeReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packet = json.loads((ROOT / PACKET).read_text())
        cls.candidate = yaml.safe_load((ROOT / CANDIDATE).read_bytes())
        data = subprocess.check_output(['git', 'archive', BASE, BOOK], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            cls.book = {m.name: archive.extractfile(m).read() for m in archive.getmembers()
                        if m.isfile() and m.name.endswith('.yaml')}
        cls.before = yaml.safe_load(cls.book[TARGET])

    def test_exact_delta_and_archives(self):
        old, new = self.before, self.candidate
        expected = copy.deepcopy(old)
        expected['translation']['footnotes'][0]['text'] = NOTE
        expected['theological_decisions'][0] = copy.deepcopy(THEOLOGY)
        expected['status'] = 'draft'
        expected['cross_check'] = {'status': 'needs_review'}
        expected.pop('revision_pass')
        expected['review_history'] = copy.deepcopy(old.get('review_history', [])) + [{
            'baseline_commit': BASE, 'baseline_sha256': sha(self.book[TARGET]),
            'date': '2026-10-19', 'certifies_this_candidate': False,
            'historical_review_inputs_verified': False,
            'fields': {k: copy.deepcopy(old[k]) for k in
                       ('status', 'revision_pass', 'cross_check', 'theological_decisions', 'translation')}}]
        expected['revisions'] = copy.deepcopy(old.get('revisions', [])) + [{
            'date': '2026-10-19', 'agent': 'Codex',
            'scope': 'Note a and age rationale only; source and main English unchanged.',
            'case_document': 'docs/CHRONICLES_22_2_GREEK_APPARATUS_2026-10-19.md',
            'from_note': old['translation']['footnotes'][0]['text'], 'to_note': NOTE}]
        self.assertEqual(new, expected)
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(new)
        self.assertEqual(new['translation']['text'], old['translation']['text'])
        self.assertIn('became king[a]', new['translation']['text'])
        self.assertEqual(new['translation']['footnotes'][1], old['translation']['footnotes'][1])

    def test_frozen_inputs_and_apparatus_identities(self):
        self.assertEqual(self.packet['baseline_commit'], BASE)
        for path, pin in self.packet['historical_input_pins'].items():
            raw = subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)
            self.assertEqual(sha(raw), pin, path)
        for path, pin in self.packet['reviewed_file_pins'].items():
            self.assertEqual(sha((ROOT / path).read_bytes()), pin, path)
        self.assertEqual(self.packet['greek_age_units']['twenty_two_reported_numbers'],
                         [19, 55, 71, 93, 106, 107, 108, 119, 120, 121, 134])
        self.assertEqual(self.packet['greek_age_units']['range_n_to_y'], ['n', 'p', 'q', 't', 'y'])
        workflow = (ROOT / '.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn(f'git fetch --no-tags --depth=1 origin {BASE}', workflow)

    def test_complete_book_export_changes_only_target_note(self):
        records = {}
        for path, raw in self.book.items():
            record = yaml.safe_load(raw)
            records[tuple(map(int, record['id'].split('.')[1:]))] = record
        def reader(code, chapter, verse):
            self.assertEqual(code, '2CH')
            return records[(chapter, verse)]
        with patch.object(exporter, 'load_translation_record', side_effect=reader):
            old = exporter.export_book('2CH')
            records[(22, 2)] = self.candidate
            new = exporter.export_book('2CH')
        def index(book):
            return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}
        a, b = index(old), index(new)
        self.assertEqual(len(old['chapters']), 36)
        self.assertEqual(len(a), 822)
        self.assertEqual(set(a), set(b))
        self.assertEqual([k for k in a if a[k] != b[k]], [(22, 2)])
        target = copy.deepcopy(a[(22, 2)])
        target['footnotes'][0]['text'] = NOTE
        self.assertEqual(b[(22, 2)], target)
        restored = copy.deepcopy(new)
        for chapter in restored['chapters']:
            if chapter['chapter'] == 22:
                chapter['verses'][1] = copy.deepcopy(a[(22, 2)])
        self.assertEqual(restored, old)

    def test_all_live_files_exact_baseline_or_candidate(self):
        actual = {str(p.relative_to(ROOT)): p.read_bytes()
                  for p in (ROOT / BOOK).rglob('*.yaml')}
        self.assertEqual(len(actual), 822)
        self.assertEqual(set(actual), set(self.book))
        for path, raw in actual.items():
            if path == TARGET:
                self.assertIn(yaml.safe_load(raw), [self.before, self.candidate])
            else:
                self.assertEqual(raw, self.book[path], path)


if __name__ == '__main__':
    unittest.main()
