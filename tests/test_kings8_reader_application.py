"""Bounded reader disclosure; not Hebrew priority or whole-verse approval."""
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
CONTRACT = 'sources/textual_restoration/comparisons/kings8_reader_contract.2026-10-17.v1.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode())


def plain(text):
    return re.sub(r'\[[a-z]+\]', '', text)


def baseline_files(contract):
    raw = subprocess.check_output(['git', 'archive', contract['baseline_commit'],
                                   contract['book_baseline']['path']], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        return {m.name: archive.extractfile(m).read() for m in archive.getmembers()
                if m.isfile() and m.name.endswith('.yaml')}


def expected_record(before, item, contract):
    """Explicit allowed delta; all other fields must remain identical."""
    expected = copy.deepcopy(before)
    expected['translation']['text'] = item['text']
    if before['id'] == '1KI.8.13':
        expected['translation']['footnotes'].append(contract['new_note'])
    expected['status'] = 'draft'
    expected['cross_check'] = {'status': 'needs_review'}
    expected.pop('revision_pass')
    expected['review_history'] = copy.deepcopy(before.get('review_history', []))
    for field in contract['archives']:
        value = before
        for part in field.split('.'):
            value = value[part]
        expected['review_history'].append({
            'field': field, 'value': value,
            'archived_from_baseline_commit': contract['baseline_commit'],
            'archived_from_baseline_sha256': item['before_sha256'],
            'historical_review_inputs_verified': False,
            'certifies_this_candidate': False,
        })
    expected['revisions'] = copy.deepcopy(before.get('revisions', [])) + [{
        'date': '2026-10-17', 'agent': 'Codex',
        'scope': 'Reader footnote anchors and factual Greek-poem disclosure only; source and marker-free main English unchanged',
        'from': before['translation']['text'], 'to': item['text'],
        'baseline_sha256': item['before_sha256'],
        'case_document': contract['report'],
        'application_receipt': contract['application_receipt'],
    }]
    return expected


def export_probe(before, candidates):
    def load(records):
        def overlay(code, chapter, verse):
            if code != '1KI':
                raise AssertionError('Unexpected book')
            return records[(chapter, verse)]
        return overlay
    with patch.object(exporter, 'load_translation_record', side_effect=load(before)):
        old = exporter.export_book('1KI')
    combined = {**before, **candidates}
    with patch.object(exporter, 'load_translation_record', side_effect=load(combined)):
        new = exporter.export_book('1KI')
    def index(book):
        return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}
    a, b = index(old), index(new)
    changed = sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))
    assert changed == [(8, 12), (8, 13)], changed
    restored = copy.deepcopy(new)
    for chapter in restored['chapters']:
        for i, verse in enumerate(chapter['verses']):
            key = (chapter['chapter'], verse['verse'])
            if key in candidates:
                chapter['verses'][i] = a[key]
    assert restored == old, 'Export metadata or unrelated unit changed'
    for key, record in candidates.items():
        assert b[key]['text'] == record['translation']['text']
        assert b[key]['footnotes'] == record['translation']['footnotes']
    return {'before_export_sha256': digest(old), 'candidate_export_sha256': digest(new),
            'chapter_count': len(new['chapters']), 'unit_count': len(b),
            'changed_export_ids': changed, 'other_units_unchanged': len(b) - len(changed)}


class Kings8ReaderApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / CONTRACT).read_text())
        cls.raw = baseline_files(cls.contract)
        cls.before = {(int(Path(p).parent.name), int(Path(p).stem)): yaml.safe_load(raw)
                      for p, raw in cls.raw.items()}
        cls.candidates = {(8, int(Path(i['path']).stem)):
                          yaml.safe_load((ROOT / i['candidate']).read_bytes())
                          for i in cls.contract['records']}

    def test_frozen_inputs_and_candidates(self):
        c = self.contract
        self.assertEqual(c['baseline_commit'], '6a2cc87cc5085eab28b341999a11d17004db842e')
        self.assertEqual(len(self.raw), c['book_baseline']['yaml_count'])
        self.assertEqual(digest({p: sha(raw) for p, raw in self.raw.items()}),
                         c['book_baseline']['sha256'])
        for path, expected in c['input_pins'].items():
            raw = subprocess.check_output(['git', 'show', f"{c['baseline_commit']}:{path}"], cwd=ROOT)
            self.assertEqual(sha(raw), expected, path)
        for item in c['records']:
            self.assertEqual(sha(self.raw[item['path']]), item['before_sha256'])
            self.assertEqual(sha((ROOT / item['candidate']).read_bytes()), item['candidate_sha256'])

    def test_exact_delta_schema_archives_and_anchors(self):
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        for item in self.contract['records']:
            key = (8, int(Path(item['path']).stem))
            before, candidate = self.before[key], self.candidates[key]
            validator.validate(candidate)
            self.assertEqual(candidate, expected_record(before, item, self.contract))
            self.assertEqual(plain(candidate['translation']['text']), plain(before['translation']['text']))
            notes = candidate['translation']['footnotes']
            self.assertEqual(re.findall(r'\[([a-z]+)\]', candidate['translation']['text']),
                             [n['marker'] for n in notes])
            self.assertEqual(candidate['translation']['text'].count('[a]'), 1)
        self.assertIn('thick darkness[a]', self.candidates[(8, 12)]['translation']['text'])
        self.assertIn('exalted house[a], a settled place for you to dwell[b] forever[c]',
                      self.candidates[(8, 13)]['translation']['text'])
        self.assertEqual(self.contract['new_note']['reason'], 'textual_variant')

    def test_complete_historical_book_export(self):
        result = export_probe(self.before, self.candidates)
        self.assertEqual(result['chapter_count'], 22)
        self.assertEqual(result['unit_count'], len(self.before))
        self.assertFalse(self.contract['review_contract']['whole_verse_certification'])
        self.assertFalse(self.contract['review_contract']['source_priority_certification'])

    def test_live_targets_are_exact_baseline_or_candidate(self):
        states = []
        for item in self.contract['records']:
            current = sha((ROOT / item['path']).read_bytes())
            self.assertIn(current, (item['before_sha256'], item['candidate_sha256']))
            states.append(current == item['candidate_sha256'])
        self.assertEqual(states[0], states[1], 'Partial application')
        live = exporter.export_book('1KI')
        index = {(c['chapter'], v['verse']): v for c in live['chapters'] for v in c['verses']}
        for key, candidate in self.candidates.items():
            expected = candidate if states[0] else self.before[key]
            self.assertEqual(index[key]['text'], expected['translation']['text'])
            self.assertEqual(index[key]['footnotes'], expected['translation']['footnotes'])


if __name__ == '__main__':
    unittest.main()
