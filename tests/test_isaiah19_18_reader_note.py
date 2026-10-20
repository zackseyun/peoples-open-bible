"""One Isaiah note; historical book data, current exporter behavior.

The BASE schema is used without rewriting it. This legacy verse already lacks
ai_draft and translation.philosophy; exact unchanged failures are disclosed,
not waived into a full-schema PASS or repaired with invented provenance.
"""
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
BASE = '627ad02109a5970c6e10f3fe872004a30838df31'
TARGET = 'translation/ot/isaiah/019/018.yaml'
CANDIDATE = 'sources/textual_restoration/applications/isaiah19_18_reader_candidate.2026-10-20.v1.json'
CONTRACT = 'sources/textual_restoration/applications/isaiah19_18_reader_contract.2026-10-20.v1.json'
REPORT = 'docs/ISAIAH_19_EGYPT_AND_CITY_COMPARISON_2026-10-20.md'
RECEIPT = 'sources/textual_restoration/applications/isaiah19_18_reader.2026-10-20.v1.json'
NOTE = '1QIsaᵃ and 4QIsaᵇ, two Dead Sea Scroll manuscripts, read “City of the Sun” instead of “City of Destruction.” The Hebrew text followed here reads “City of Destruction.”'
SCOPE = 'Isaiah19:18 existing-verse reader note only; source and marker-free main English unchanged; no historical source-priority selection or whole-verse certification'
BEFORE_SHA = '429f75b1c69920ffa17f3d4bc6a66d966946fe3e2e7833abd0c06eb9645f2339'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode())


def expected(before):
    d = copy.deepcopy(before)
    assert d['translation']['text'].endswith('City of Destruction.')
    d['translation']['text'] = d['translation']['text'][:-1] + '[a].'
    d['translation']['footnotes'] = [
        {'marker': 'a', 'text': NOTE, 'reason': 'textual_variant'}]
    d['status'] = 'draft'
    d['cross_check'] = {'status': 'needs_review'}
    d['review_history'] = [{
        'field': 'revision_pass', 'value': d.pop('revision_pass'),
        'archived_from_baseline_commit': BASE,
        'archived_from_baseline_sha256': BEFORE_SHA,
        'historical_review_inputs_verified': False,
        'certifies_this_candidate': False,
    }]
    d['revisions'].append({
        'date': '2026-10-20', 'agent': 'Codex', 'scope': SCOPE,
        'from_note': None, 'to_note': NOTE, 'baseline_sha256': BEFORE_SHA,
        'case_document': REPORT, 'application_receipt': RECEIPT,
    })
    return d


def index(book):
    return {(c['chapter'], v['verse']): v
            for c in book['chapters'] for v in c['verses']}


def schema_errors(schema, record):
    return sorted((list(e.absolute_path), e.validator, e.message)
                  for e in Draft202012Validator(schema).iter_errors(record))


class Isaiah19ReaderNoteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / CONTRACT).read_text())
        archive_raw = subprocess.check_output(
            ['git', 'archive', BASE, 'translation/ot/isaiah'], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(archive_raw)) as archive:
            cls.book_raw = {m.name: archive.extractfile(m).read()
                            for m in archive.getmembers()
                            if m.isfile() and m.name.endswith('.yaml')}
        cls.book = {path: yaml.safe_load(raw)
                    for path, raw in cls.book_raw.items()}
        cls.before = cls.book[TARGET]
        cls.candidate_raw = (ROOT / CANDIDATE).read_bytes()
        cls.candidate = json.loads(cls.candidate_raw)
        cls.schema = json.loads(subprocess.check_output(
            ['git', 'show', f'{BASE}:schema/verse.schema.json'], cwd=ROOT))

        def historical_export(target_record):
            # Real current export_book and source schedule, with only its
            # record loader redirected to the complete archived Isaiah book.
            def loader(code, chapter, verse):
                if code != 'ISA':
                    raise AssertionError(code)
                path = f'translation/ot/isaiah/{chapter:03d}/{verse:03d}.yaml'
                return target_record if path == TARGET else cls.book.get(path)
            with patch.object(exporter, 'load_translation_record', loader):
                return exporter.export_book('ISA')

        cls.before_export = historical_export(cls.before)
        cls.after_export = historical_export(cls.candidate)

    def test_exact_candidate_mutation_and_contract(self):
        c = self.contract
        self.assertEqual(c['baseline_commit'], BASE)
        self.assertEqual(c['target'], TARGET)
        self.assertEqual(c['candidate'], CANDIDATE)
        self.assertEqual(sha(self.book_raw[TARGET]), BEFORE_SHA)
        self.assertEqual(c['baseline_sha256'], BEFORE_SHA)
        self.assertEqual(c['candidate_sha256'], sha(self.candidate_raw))
        self.assertEqual(c['note'], NOTE)
        self.assertEqual(c['archives'], ['revision_pass'])
        self.assertEqual(c['case_document'], REPORT)
        self.assertEqual(c['application_receipt'], RECEIPT)
        self.assertEqual(self.candidate, expected(self.before))
        for flag in ('historical_priority_approval', 'whole_verse_certification',
                     'external_reader_publisher_code_changed',
                     'publication_approval', 'canonical_source_changed',
                     'marker_free_main_english_changed', 'full_schema_valid'):
            self.assertIs(c[flag], False)

    def test_legacy_schema_failures_are_exact_and_not_invented(self):
        errors = [([], 'required', "'ai_draft' is a required property"),
                  (['translation'], 'required',
                   "'philosophy' is a required property")]
        self.assertEqual(schema_errors(self.schema, self.before), errors)
        self.assertEqual(schema_errors(self.schema, self.candidate), errors)
        self.assertEqual(self.contract['preexisting_schema_errors'], [
            {'path': p, 'validator': v, 'message': m} for p, v, m in errors])
        # Validate present source, text and new note against the unmodified
        # historical property definitions, separately from missing provenance.
        props = self.schema['properties']
        Draft202012Validator(props['source']).validate(self.candidate['source'])
        Draft202012Validator(props['translation']['properties']['text']).validate(
            self.candidate['translation']['text'])
        Draft202012Validator(props['translation']['properties']['footnotes']).validate(
            self.candidate['translation']['footnotes'])
        self.assertNotIn('ai_draft', self.candidate)
        self.assertNotIn('philosophy', self.candidate['translation'])

    def test_archives_source_main_text_and_anchor(self):
        self.assertEqual(self.candidate['source'], self.before['source'])
        marked = self.candidate['translation']['text']
        self.assertEqual(marked.replace('[a]', ''),
                         self.before['translation']['text'])
        self.assertEqual(marked.count('[a]'), 1)
        self.assertTrue(marked.endswith('City of Destruction[a].'))
        self.assertNotIn('revision_pass', self.candidate)
        self.assertEqual(self.candidate['review_history'][0]['value'],
                         self.before['revision_pass'])
        self.assertEqual(self.candidate['revisions'][:-1], self.before['revisions'])
        self.assertEqual(self.candidate['status'], 'draft')
        self.assertEqual(self.candidate['cross_check'], {'status': 'needs_review'})

    def test_actual_whole_archived_isaiah_export(self):
        a, b = index(self.before_export), index(self.after_export)
        c = self.contract['preflight_export']
        self.assertEqual(len(self.book_raw), c['historical_yaml_records'])
        self.assertEqual(len(a), c['before_units'])
        self.assertEqual(len(b), c['after_units'])
        self.assertEqual(len(self.before_export['chapters']), c['chapters'])
        self.assertEqual(digest(self.before_export), c['before_sha256'])
        self.assertEqual(digest(self.after_export), c['after_sha256'])
        self.assertEqual(set(a), set(b))
        self.assertEqual([k for k in a if a[k] != b[k]], [(19, 18)])
        proposed = copy.deepcopy(a[(19, 18)])
        proposed['text'] = self.candidate['translation']['text']
        proposed['footnotes'] = self.candidate['translation']['footnotes']
        self.assertEqual(b[(19, 18)], proposed)
        restored = copy.deepcopy(self.after_export)
        for chapter in restored['chapters']:
            for n, verse in enumerate(chapter['verses']):
                if (chapter['chapter'], verse['verse']) == (19, 18):
                    chapter['verses'][n] = a[(19, 18)]
        self.assertEqual(restored, self.before_export)

    def test_live_target_and_full_export_are_baseline_or_candidate(self):
        current = yaml.safe_load((ROOT / TARGET).read_text())
        self.assertIn(current, (self.before, self.candidate))
        live = exporter.export_book('ISA')
        self.assertIn(live, (self.before_export, self.after_export))
        expected_target = index(self.after_export if current == self.candidate
                                else self.before_export)[(19, 18)]
        self.assertEqual(index(live)[(19, 18)], expected_target)


if __name__ == '__main__':
    unittest.main()
