"""One factual ending note; no source priority or whole-verse certification."""
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
BASELINE = '332a7f9b050acedcf99a5e99412c63980c901115'
CONTRACT = 'sources/textual_restoration/comparisons/job42_reader_contract.2026-10-17.v1.json'
TARGET = 'translation/ot/job/042/017.yaml'
KEY = (42, 17)
TEXT = 'And Job died, old and full of days.[a][b]'
REPORT = 'docs/JOB_42_READER_DISCLOSURE_2026-10-17.md'
RECEIPT = 'sources/textual_restoration/applications/job42_reader.2026-10-17.v1.json'
NOTE = {
    'marker': 'b',
    'text': "Swete's Greek text continues after Job's death with a statement that he will rise again with those the Lord raises, then identifies him as Jobab and gives a genealogy and Edomite royal list. POB provisionally retains the Hebrew ending. The Greek continuation's earliest form and any Hebrew precursor remain uncertain.",
    'reason': 'textual_variant',
}
ARCHIVES = ('status', 'revision_pass', 'cross_check', 'source_audit',
            'translation.text', 'translation.footnotes')
REVISION_SCOPE = ('One factual Greek-ending reader footnote only; Hebrew source, '
                  'marker-free main English and existing lifespan note unchanged; '
                  'not whole-verse or source-priority certification')


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


def expected_record(before, before_sha256):
    """Derive the only permitted delta independently of candidate/contract text."""
    expected = copy.deepcopy(before)
    expected['translation']['text'] = TEXT
    expected['translation']['footnotes'].append(copy.deepcopy(NOTE))
    expected['status'] = 'draft'
    expected['cross_check'] = {'status': 'needs_review'}
    expected.pop('revision_pass')
    expected.pop('source_audit')
    expected['review_history'] = copy.deepcopy(before.get('review_history', []))
    for field in ARCHIVES:
        value = before
        for part in field.split('.'):
            value = value[part]
        expected['review_history'].append({
            'field': field, 'value': copy.deepcopy(value),
            'archived_from_baseline_commit': BASELINE,
            'archived_from_baseline_sha256': before_sha256,
            'historical_review_inputs_verified': False,
            'certifies_this_candidate': False,
        })
    expected['revisions'] = copy.deepcopy(before.get('revisions', [])) + [{
        'date': '2026-10-17', 'agent': 'Codex', 'scope': REVISION_SCOPE,
        'from': before['translation']['text'], 'to': TEXT,
        'baseline_sha256': before_sha256, 'case_document': REPORT,
        'application_receipt': RECEIPT,
    }]
    return expected


def export_probe(before, candidate):
    def load(records):
        def overlay(code, chapter, verse):
            if code != 'JOB':
                raise AssertionError('Unexpected book')
            return records[(chapter, verse)]
        return overlay
    with patch.object(exporter, 'load_translation_record', side_effect=load(before)):
        old = exporter.export_book('JOB')
    with patch.object(exporter, 'load_translation_record',
                      side_effect=load({**before, KEY: candidate})):
        new = exporter.export_book('JOB')
    def index(book):
        return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}
    a, b = index(old), index(new)
    changed = sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))
    assert changed == [KEY], changed
    restored = copy.deepcopy(new)
    for chapter in restored['chapters']:
        for i, verse in enumerate(chapter['verses']):
            if (chapter['chapter'], verse['verse']) == KEY:
                chapter['verses'][i] = a[KEY]
    assert restored == old, 'Export metadata or another unit changed'
    assert b[KEY]['text'] == TEXT
    assert b[KEY]['footnotes'] == before[KEY]['translation']['footnotes'] + [NOTE]
    return {'before_export_sha256': digest(old), 'candidate_export_sha256': digest(new),
            'chapter_count': len(new['chapters']), 'unit_count': len(b),
            'changed_export_ids': [list(k) for k in changed],
            'other_units_unchanged': len(b) - len(changed)}


class Job42ReaderApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / CONTRACT).read_text())
        cls.raw = baseline_files(cls.contract)
        cls.before = {(int(Path(p).parent.name), int(Path(p).stem)): yaml.safe_load(raw)
                      for p, raw in cls.raw.items()}
        cls.item, = cls.contract['records']
        cls.candidate_raw = (ROOT / cls.item['candidate']).read_bytes()
        cls.candidate = yaml.safe_load(cls.candidate_raw)

    def test_frozen_inputs_and_candidate(self):
        c = self.contract
        self.assertEqual(c['baseline_commit'], BASELINE)
        self.assertEqual(c['book_baseline']['path'], 'translation/ot/job')
        self.assertEqual(len(self.raw), 1070)
        self.assertEqual(c['book_baseline']['yaml_count'], 1070)
        self.assertEqual(digest({p: sha(raw) for p, raw in self.raw.items()}),
                         c['book_baseline']['sha256'])
        for path, expected in c['input_pins'].items():
            raw = subprocess.check_output(['git', 'show', f'{BASELINE}:{path}'], cwd=ROOT)
            self.assertEqual(sha(raw), expected, path)
            self.assertEqual(sha((ROOT / path).read_bytes()), expected, path)
        self.assertEqual(self.item['path'], TARGET)
        self.assertEqual(self.item['before_sha256'], sha(self.raw[TARGET]))
        self.assertEqual(self.item['candidate_sha256'], sha(self.candidate_raw))
        self.assertEqual(self.item['text'], TEXT)
        self.assertEqual(c['new_note'], NOTE)
        self.assertEqual(c['archives'], list(ARCHIVES))
        self.assertEqual(c['report'], REPORT)
        self.assertEqual(c['application_receipt'], RECEIPT)

    def test_exact_delta_schema_archives_and_anchors(self):
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        validator.validate(self.candidate)
        before = self.before[KEY]
        self.assertEqual(self.candidate, expected_record(before, sha(self.raw[TARGET])))
        self.assertEqual(plain(TEXT), plain(before['translation']['text']))
        self.assertEqual(before['translation']['text'], 'And Job died, old and full of days.[a]')
        self.assertEqual(self.candidate['translation']['footnotes'][:-1],
                         before['translation']['footnotes'])
        self.assertEqual(re.findall(r'\[([a-z]+)\]', TEXT), ['a', 'b'])
        self.assertEqual([n['marker'] for n in self.candidate['translation']['footnotes']], ['a', 'b'])
        self.assertNotIn('revision_pass', self.candidate)
        self.assertNotIn('source_audit', self.candidate)
        self.assertFalse(self.contract['historical_review_transfer'])

    def test_complete_historical_book_export(self):
        result = export_probe(self.before, self.candidate)
        self.assertEqual(result['chapter_count'], 42)
        self.assertEqual(result['unit_count'], 1070)
        self.assertEqual(result['other_units_unchanged'], 1069)
        for field in ('whole_verse_certification', 'source_priority_certification',
                      'deployment_review', 'blind_stylistic_vote_claimed'):
            self.assertFalse(self.contract['review_contract'][field])

    def test_live_book_is_exact_baseline_or_candidate(self):
        live_raw = {str(p.relative_to(ROOT)): p.read_bytes()
                    for p in (ROOT / 'translation/ot/job').rglob('*.yaml')}
        self.assertEqual(set(live_raw), set(self.raw), 'Job record path set changed')
        current = sha(live_raw[TARGET])
        self.assertIn(current, (self.item['before_sha256'], self.item['candidate_sha256']))
        expected_raw = {p: sha(raw) for p, raw in self.raw.items()}
        expected_raw[TARGET] = current
        self.assertEqual({p: sha(raw) for p, raw in live_raw.items()}, expected_raw,
                         'Unrelated Job bytes changed')
        selected = self.candidate if current == self.item['candidate_sha256'] else self.before[KEY]
        live = exporter.export_book('JOB')
        def overlay(code, chapter, verse):
            self.assertEqual(code, 'JOB')
            return selected if (chapter, verse) == KEY else self.before[(chapter, verse)]
        with patch.object(exporter, 'load_translation_record', side_effect=overlay):
            expected = exporter.export_book('JOB')
        self.assertEqual(live, expected, 'Live full-book units or metadata differ')


if __name__ == '__main__':
    unittest.main()
