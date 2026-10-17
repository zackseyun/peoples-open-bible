"""Bounded ketiv/qere disclosure and rationale repair; source priority stays held."""
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
METHOD_PATH = 'docs/TEXTUAL_ADJUDICATION_METHOD.md'
BASELINE = '12fa8aad57a9bb573177c4a5864c0e9ee62b369d'
CONTRACT = 'sources/textual_restoration/comparisons/kings2_8_10_reader_contract.2026-10-17.v1.json'
TARGET = 'translation/ot/2_kings/008/010.yaml'
CANDIDATE = 'sources/textual_restoration/candidates/kings2_8_10_reader.2026-10-17.v1.yaml'
KEY = (8, 10)
TEXT = 'And Elisha said to him, “Go, say to him, ‘You will certainly recover’[a]; but Yahweh has shown me that he will certainly die.”'
BEFORE_TEXT = 'And Elisha said to him[a], “Go, say to him, ‘You will certainly recover’; but Yahweh has shown me that he will certainly die.”'
REPORT = 'docs/KINGS_2_8_10_SOURCE_AND_READER_REVIEW_2026-10-17.md'
RECEIPT = 'sources/textual_restoration/applications/kings2_8_10_reader.2026-10-17.v1.json'
EVIDENCE = 'sources/textual_restoration/comparisons/kings2_8_10_sources.2026-10-17.v1.json'
NOTE = {
    'marker': 'a',
    'text': "POB follows the Hebrew reading tradition (qere), which has לו, ‘to him,’ followed by the positive recovery message. The written form (ketiv) has לא, ‘not,’ making that message negative. These readings affect how Hazael's report in verse 14 relates to Elisha's instruction; their historical priority remains uncertain.",
    'reason': 'textual_variant',
}
LEXICAL_RATIONALE = "The vendored WLC/OSHB explicitly marks ketiv לא (‘not’) and qere לו (‘to him’). POB's positive recovery message follows the qere, not merely a conjectural correction of an uninterpretable line. The ketiv makes the recovery statement negative and agrees with the following death announcement; verse 14's positive report then raises a different question about Hazael's faithfulness. Neither narrative smoothness nor a preference about prophetic truthfulness settles historical priority. The illness context supports recovery or survival language, and the infinitive absolute plus imperfect provides emphasis. No fresh HALOT consultation is claimed."
THEOLOGY_CHOSEN = "Provisionally retain POB's positive recovery message as a use of the attested Hebrew qere, while disclosing the negative ketiv without treating it as grammatically or contextually impossible."
THEOLOGY_ALTERNATIVES = [
    'The formal qere has לו (‘to him’) and leaves the recovery statement positive.',
    'The ketiv has לא (‘not’) and makes the recovery statement negative.',
]
THEOLOGY_RATIONALE = "Both Hebrew forms are explicit in the vendored edition. The negative ketiv is grammatically coherent and agrees with the following death announcement; it makes Hazael's positive report in verse 14 a changed message. The qere preserves a positive instruction alongside the death revelation. Recovery from illness versus death through a subsequent act is one possible explanation; a deceptive instruction or selective report is another. These are interpretive alternatives, not additional surviving Hebrew words or grounds to adjust a prophet's morality. POB's existing positive wording is retained provisionally without settling historical priority."
ARCHIVES = ('status', 'revision_pass', 'cross_check', 'translation.text',
            'translation.footnotes', 'lexical_decisions', 'theological_decisions')
REVISION_SCOPE = ('Ketiv/qere reader disclosure, semantic footnote anchor and bounded lexical/theological rationale repair only; '
                  'source and marker-free main English unchanged; historical source priority held')


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
    """Independent hardcoded oracle; candidate and contract prose are not inputs."""
    expected = copy.deepcopy(before)
    expected['translation']['text'] = TEXT
    expected['translation']['footnotes'] = [copy.deepcopy(NOTE)]
    expected['lexical_decisions'][2].pop('lexicon')
    expected['lexical_decisions'][2]['rationale'] = LEXICAL_RATIONALE
    expected['theological_decisions'][0]['chosen_reading'] = THEOLOGY_CHOSEN
    expected['theological_decisions'][0]['alternative_readings'] = copy.deepcopy(THEOLOGY_ALTERNATIVES)
    expected['theological_decisions'][0]['rationale'] = THEOLOGY_RATIONALE
    expected['status'] = 'draft'
    expected['cross_check'] = {'status': 'needs_review'}
    expected.pop('revision_pass')
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
            if code != '2KI':
                raise AssertionError('Unexpected book')
            return records[(chapter, verse)]
        return overlay
    with patch.object(exporter, 'load_translation_record', side_effect=load(before)):
        old = exporter.export_book('2KI')
    with patch.object(exporter, 'load_translation_record',
                      side_effect=load({**before, KEY: candidate})):
        new = exporter.export_book('2KI')
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
    assert b[KEY]['footnotes'] == [NOTE]
    assert plain(b[KEY]['text']) == plain(a[KEY]['text'])
    return {'before_export_sha256': digest(old), 'candidate_export_sha256': digest(new),
            'chapter_count': len(new['chapters']), 'unit_count': len(b),
            'changed_export_ids': [list(k) for k in changed],
            'other_units_unchanged': len(b) - len(changed)}


class Kings2EightTenReaderApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / CONTRACT).read_text())
        cls.raw = baseline_files(cls.contract)
        cls.before = {(int(Path(p).parent.name), int(Path(p).stem)): yaml.safe_load(raw)
                      for p, raw in cls.raw.items()}
        cls.item, = cls.contract['records']
        cls.candidate_raw = (ROOT / cls.item['candidate']).read_bytes()
        cls.candidate = yaml.safe_load(cls.candidate_raw)

    def assert_frozen_input_pins(self):
        for path, expected in self.contract['input_pins'].items():
            raw = subprocess.check_output(['git', 'show', f'{BASELINE}:{path}'], cwd=ROOT)
            self.assertEqual(sha(raw), expected, path)
            # Preserve the policy actually reviewed without freezing later
            # method revisions. Every other live pin remains binding.
            if path != METHOD_PATH:
                self.assertEqual(sha((ROOT / path).read_bytes()), expected, path)

    def test_corrupt_historical_method_still_fails(self):
        original = subprocess.check_output

        def corrupt_method(args, **kwargs):
            raw = original(args, **kwargs)
            return raw + b'corrupt' if args[-1] == f'{BASELINE}:{METHOD_PATH}' else raw

        with patch.object(subprocess, 'check_output', side_effect=corrupt_method):
            with self.assertRaisesRegex(AssertionError, METHOD_PATH):
                self.assert_frozen_input_pins()

    def test_live_nonpolicy_pins_still_fail_on_drift(self):
        original = Path.read_bytes
        for target in self.contract['input_pins']:
            if target == METHOD_PATH:
                continue

            def corrupt_live(path):
                raw = original(path)
                return raw + b'corrupt' if path == ROOT / target else raw

            with self.subTest(path=target), patch.object(Path, 'read_bytes', new=corrupt_live):
                with self.assertRaisesRegex(AssertionError, re.escape(target)):
                    self.assert_frozen_input_pins()

    def test_frozen_inputs_and_candidate(self):
        c = self.contract
        self.assertEqual(c['baseline_commit'], BASELINE)
        self.assertFalse(c['canonical_written_at_freeze'])
        self.assertEqual(c['book_baseline']['path'], 'translation/ot/2_kings')
        self.assertEqual(len(self.raw), 719)
        self.assertEqual(c['book_baseline']['yaml_count'], 719)
        self.assertEqual(digest({p: sha(raw) for p, raw in self.raw.items()}),
                         c['book_baseline']['sha256'])
        self.assertEqual(set(c['input_pins']), {
            'docs/TEXTUAL_ADJUDICATION_METHOD.md', 'REFERENCE_SOURCES.md',
            'schema/verse.schema.json', 'tools/export_mobile_bible.py',
            'sources/ot/wlc/2Kgs.xml'})
        self.assert_frozen_input_pins()
        self.assertEqual(set(c['evidence_pins']), {EVIDENCE})
        for path, expected in c['evidence_pins'].items():
            self.assertEqual(sha((ROOT / path).read_bytes()), expected, path)
        self.assertEqual(self.item['path'], TARGET)
        self.assertEqual(self.item['candidate'], CANDIDATE)
        self.assertEqual(self.item['before_sha256'], sha(self.raw[TARGET]))
        self.assertEqual(self.item['candidate_sha256'], sha(self.candidate_raw))
        self.assertEqual(self.item['text'], TEXT)
        self.assertEqual(c['new_note'], NOTE)
        self.assertEqual(c['archives'], list(ARCHIVES))
        self.assertEqual(c['report'], REPORT)
        self.assertEqual(c['application_receipt'], RECEIPT)

    def test_exact_delta_schema_archives_and_anchor(self):
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        validator.validate(self.candidate)
        before = self.before[KEY]
        self.assertNotIn('source_audit', before)
        self.assertEqual(before['translation']['text'], BEFORE_TEXT)
        self.assertEqual(self.candidate, expected_record(before, sha(self.raw[TARGET])))
        self.assertEqual(self.candidate['source'], before['source'])
        self.assertEqual(plain(TEXT), plain(BEFORE_TEXT))
        self.assertIn('‘You will certainly recover’[a];', TEXT)
        self.assertEqual(re.findall(r'\[([a-z]+)\]', TEXT), ['a'])
        self.assertEqual([n['marker'] for n in self.candidate['translation']['footnotes']], ['a'])
        self.assertEqual(before['lexical_decisions'][2]['source_word'], 'לא חָיֹה תִחְיֶה')
        self.assertEqual(before['lexical_decisions'][2]['lexicon'], 'HALOT')
        self.assertNotIn('lexicon', self.candidate['lexical_decisions'][2])
        for i, entry in enumerate(before['lexical_decisions']):
            if i != 2:
                self.assertEqual(self.candidate['lexical_decisions'][i], entry)
        self.assertNotIn('revision_pass', self.candidate)
        self.assertNotIn('source_audit', self.candidate)
        self.assertFalse(self.contract['historical_review_transfer'])
        self.assertEqual(self.contract['source_priority_status'], 'HOLD')

    def test_complete_historical_and_candidate_book_exports(self):
        result = export_probe(self.before, self.candidate)
        self.assertEqual(result['chapter_count'], 25)
        self.assertEqual(result['unit_count'], 719)
        self.assertEqual(result['other_units_unchanged'], 718)
        for field in ('whole_verse_certification', 'source_priority_certification',
                      'deployment_review', 'blind_stylistic_vote_claimed'):
            self.assertFalse(self.contract['review_contract'][field])

    def test_live_book_is_exact_baseline_or_candidate(self):
        live_raw = {str(p.relative_to(ROOT)): p.read_bytes()
                    for p in (ROOT / 'translation/ot/2_kings').rglob('*.yaml')}
        self.assertEqual(set(live_raw), set(self.raw), '2 Kings record path set changed')
        current = sha(live_raw[TARGET])
        self.assertIn(current, (self.item['before_sha256'], self.item['candidate_sha256']))
        expected_raw = {p: sha(raw) for p, raw in self.raw.items()}
        expected_raw[TARGET] = current
        self.assertEqual({p: sha(raw) for p, raw in live_raw.items()}, expected_raw,
                         'Unrelated 2 Kings bytes changed')
        selected = self.candidate if current == self.item['candidate_sha256'] else self.before[KEY]
        live = exporter.export_book('2KI')
        def overlay(code, chapter, verse):
            self.assertEqual(code, '2KI')
            return selected if (chapter, verse) == KEY else self.before[(chapter, verse)]
        with patch.object(exporter, 'load_translation_record', side_effect=overlay):
            expected = exporter.export_book('2KI')
        self.assertEqual(live, expected, 'Live full-book units or metadata differ')


if __name__ == '__main__':
    unittest.main()
