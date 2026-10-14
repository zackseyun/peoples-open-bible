"""Scoped reader disclosures; no earliest-source or whole-verse certification."""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest
from unittest.mock import patch

import yaml
from jsonschema import Draft202012Validator
from tools import audit_footnotes
from tools import export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]
BASE = '324d1a56295e84cc5976be0501702adcbd16a13c'
APPLIED_COMMIT = '7f4381b74becaae410273b245abab71aba009e9d'
CONTRACT = 'sources/textual_restoration/comparisons/habakkuk2_reader_contract.2026-10-12.v1.json'
CONTRACT_SHA = '1fe49fe05f72f2fc8cc54e07b271ad515e53f1239c23a875e411a3bffb6669c3'
RECEIPT = 'sources/textual_restoration/applications/habakkuk2_reader.2026-10-12.v1.json'
TARGETS = {(2, 5), (2, 16)}
METHOD_PATH = 'docs/TEXTUAL_ADJUDICATION_METHOD.md'
HISTORICAL_POLICY_PATHS = {METHOD_PATH, 'DOCTRINE.md'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode('utf-8'))


def plain(text):
    return re.sub(r'\[[a-z]\]', '', text)


def index(book):
    return {(c['chapter'], v['verse']): v
            for c in book['chapters'] for v in c['verses']}


def schema_errors(validator, record):
    errors = [{'path': list(e.path), 'validator': e.validator, 'message': e.message}
              for e in validator.iter_errors(record)]
    return sorted(errors, key=lambda e: (len(e['path']), str(e['path']), e['validator'], e['message']))


class Habakkuk2ReaderDisclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract_raw = (ROOT / CONTRACT).read_bytes()
        cls.contract = json.loads(cls.contract_raw)
        cls.candidate_raw = {}
        cls.candidates = {}
        for number, target in cls.contract['targets'].items():
            key = (2, int(number))
            raw = (ROOT / target['candidate']).read_bytes()
            cls.candidate_raw[key] = raw
            cls.candidates[key] = yaml.safe_load(raw)
        cls.historical = {}
        for path, pin in cls.contract['book_baseline_pins'].items():
            raw = subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)
            assert sha(raw) == pin, path
            location = Path(path)
            cls.historical[(int(location.parent.name), int(location.stem))] = yaml.safe_load(raw)
        cls.schema = json.loads((ROOT / 'schema/verse.schema.json').read_text())
        # The whole-book receipt belongs to its actual application transaction.
        # Later scoped changes must not rewrite its frozen evidence or digest.
        cls.applied = {}
        for path in cls.contract['book_baseline_pins']:
            raw = subprocess.check_output(['git', 'show', f'{APPLIED_COMMIT}:{path}'], cwd=ROOT)
            location = Path(path)
            key = (int(location.parent.name), int(location.stem))
            if key in TARGETS:
                assert raw == cls.candidate_raw[key], path
            else:
                assert sha(raw) == cls.contract['book_baseline_pins'][path], path
            cls.applied[key] = yaml.safe_load(raw)

    def assert_frozen_input_pins(self):
        for path, pin in self.contract['input_pins'].items():
            raw = subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)
            self.assertEqual(sha(raw), pin, path)
            # Review-method and doctrine documents belong to this historical
            # transaction. A later terminology decision does not rewrite them.
            # Live schemas, source evidence and all other pins remain binding.
            if path not in HISTORICAL_POLICY_PATHS:
                self.assertEqual(sha((ROOT / path).read_bytes()), pin, path)

    def test_corrupt_historical_method_still_fails(self):
        original = subprocess.check_output

        def corrupt_method(args, **kwargs):
            raw = original(args, **kwargs)
            return raw + b'corrupt' if args[-1] == f'{BASE}:{METHOD_PATH}' else raw

        with patch.object(subprocess, 'check_output', side_effect=corrupt_method):
            with self.assertRaisesRegex(AssertionError, METHOD_PATH):
                self.assert_frozen_input_pins()

    def test_corrupt_historical_doctrine_still_fails(self):
        original = subprocess.check_output

        def corrupt_doctrine(args, **kwargs):
            raw = original(args, **kwargs)
            return raw + b'corrupt' if args[-1] == f'{BASE}:DOCTRINE.md' else raw

        with patch.object(subprocess, 'check_output', side_effect=corrupt_doctrine):
            with self.assertRaisesRegex(AssertionError, 'DOCTRINE.md'):
                self.assert_frozen_input_pins()

    def test_live_schema_and_source_pins_still_fail_on_drift(self):
        source_path = next(p for p in self.contract['input_pins'] if p.startswith('sources/'))
        original = Path.read_bytes
        for target in ('schema/verse.schema.json', source_path):
            def corrupt_live(path):
                raw = original(path)
                return raw + b'corrupt' if path == ROOT / target else raw

            with self.subTest(path=target), patch.object(Path, 'read_bytes', new=corrupt_live):
                with self.assertRaisesRegex(AssertionError, re.escape(target)):
                    self.assert_frozen_input_pins()

    def test_frozen_inputs_and_exact_candidate_digests(self):
        self.assertEqual(sha(self.contract_raw), CONTRACT_SHA)
        self.assertEqual(self.contract['baseline_commit'], BASE)
        self.assertEqual(set(self.candidates), TARGETS)
        self.assert_frozen_input_pins()
        self.assertEqual(digest(self.contract['book_baseline_pins']),
                         self.contract['book_baseline_manifest_sha256'])
        for number, target in self.contract['targets'].items():
            self.assertEqual(sha(self.candidate_raw[(2, int(number))]),
                             target['candidate_yaml_sha256'])
            self.assertEqual(target['baseline_yaml_sha256'],
                             self.contract['book_baseline_pins'][target['canonical_target']])
        self.assertEqual(self.contract['history_boundary']['habakkuk1_5_applied_commit'],
                         'c62b1903963cfafce58b9a87770994e4d0a1df4b')
        self.assertIs(self.contract['history_boundary']['old_inputs_and_hashes_changed'], False)

    def test_exact_source_main_english_and_missing_provenance_retained(self):
        allowed = {'translation', 'lexical_decisions', 'status', 'revision_pass',
                   'cross_check', 'revisions', 'review_history', 'source_audit'}
        for key, candidate in self.candidates.items():
            before = self.historical[key]
            for field in ('id', 'reference', 'source', 'ai_draft'):
                self.assertEqual(field in candidate, field in before, (key, field))
                self.assertEqual(candidate.get(field), before.get(field), (key, field))
            self.assertEqual('philosophy' in candidate['translation'],
                             'philosophy' in before['translation'])
            self.assertEqual(candidate['translation'].get('philosophy'),
                             before['translation'].get('philosophy'))
            self.assertEqual(plain(candidate['translation']['text']),
                             plain(before['translation']['text']))
            self.assertLessEqual({k for k in set(before) | set(candidate)
                                  if before.get(k) != candidate.get(k)}, allowed)
        self.assertNotIn('ai_draft', self.candidates[(2, 16)])
        self.assertNotIn('philosophy', self.candidates[(2, 16)]['translation'])

    def test_exact_disclosures_anchors_and_relabelled_prior_notes(self):
        five = self.candidates[(2, 5)]['translation']
        self.assertEqual(five['text'],
                         'Moreover, wine[a] betrays[b]; an arrogant man does not remain at rest[c]. '
                         'He enlarges his appetite like Sheol[d], and he is like death and is never satisfied. '
                         'He gathers to himself all the nations and collects to himself all the peoples.')
        sixteen = self.candidates[(2, 16)]['translation']
        self.assertEqual(sixteen['text'],
                         'You have had your fill of shame instead of glory. Drink, you also, and show '
                         'your uncircumcision[a]! The cup from the LORD’s right hand will come around '
                         'to you, and utter disgrace will be upon your glory.')
        for number, target in self.contract['targets'].items():
            translation = self.candidates[(2, int(number))]['translation']
            self.assertEqual(translation['footnotes'], target['footnotes'])
            markers = [n['marker'] for n in translation['footnotes']]
            self.assertEqual(re.findall(r'\[([a-z])\]', translation['text']), markers)
            self.assertEqual(audit_footnotes.audit_one(ROOT / target['candidate'])['status'], 'ok')
        original = copy.deepcopy(self.historical[(2, 5)]['translation']['footnotes'])
        for note, marker in zip(original, ('b', 'c', 'd')):
            note['marker'] = marker
        self.assertEqual(five['footnotes'][1:], original)

    def test_only_connected_wine_rationale_changes(self):
        candidate, before = self.candidates[(2, 5)], self.historical[(2, 5)]
        lexical = copy.deepcopy(before['lexical_decisions'])
        self.assertEqual(lexical[1]['source_word'], 'הַיַּיִן')
        lexical[1]['rationale'] = candidate['lexical_decisions'][1]['rationale']
        self.assertEqual(candidate['lexical_decisions'], lexical)
        self.assertEqual(candidate['theological_decisions'], before['theological_decisions'])
        rationale = lexical[1]['rationale']
        for phrase in ('retention is provisional', 'Source priority remains HOLD',
                       'not another lexical gloss', 'editorial conjecture',
                       'no fresh HALOT entry consultation'):
            self.assertIn(phrase, rationale)
        self.assertNotIn('lexical_decisions', self.candidates[(2, 16)])
        self.assertNotIn('theological_decisions', self.candidates[(2, 16)])

    def test_exact_archives_append_only_revisions_and_no_score_transfer(self):
        for number, target in self.contract['targets'].items():
            key = (2, int(number))
            candidate, before = self.candidates[key], self.historical[key]
            history = candidate['review_history']
            self.assertEqual([h['field'] for h in history], target['archive_fields'])
            self.assertEqual(len(history), 5 if number == '5' else 2)
            for item in history:
                self.assertEqual(item['value'], before[item['field']])
                self.assertEqual(item['archived_from_baseline_sha256'], target['baseline_yaml_sha256'])
                self.assertIs(item['historical_review_inputs_verified'], False)
                self.assertIs(item['certifies_this_candidate'], False)
            self.assertEqual(candidate['revisions'][:-1], before.get('revisions', []))
            latest = candidate['revisions'][-1]
            self.assertEqual(latest['from'], before['translation']['text'])
            self.assertEqual(latest['to'], candidate['translation']['text'])
            self.assertEqual(latest['baseline_sha256'], target['baseline_yaml_sha256'])
            self.assertEqual(candidate['status'], 'draft')
            self.assertEqual(candidate['cross_check'], {'status': 'needs_review'})
            self.assertNotIn('revision_pass', candidate)
            audit = candidate['source_audit']
            self.assertEqual(audit['historical_priority'], 'HOLD')
            for flag in ('source_consonants_pointing_segmentation_retained',
                         'marker_free_main_english_retained', 'reader_disclosure_scope_only'):
                self.assertIs(audit[flag], True)
            for flag in ('whole_verse_optimality_certified', 'generated_images_used_as_evidence',
                         'fresh_halot_consultation', 'full_source_census_complete'):
                self.assertIs(audit[flag], False)
            for kind in ('report', 'receipt'):
                self.assertEqual(audit[f'comparison_{kind}_sha256'],
                                 self.contract['input_pins'][audit[f'comparison_{kind}']])
        self.assertEqual(self.candidates[(2, 16)]['source_audit']['legacy_missing_fields_preserved'],
                         ['ai_draft', 'translation.philosophy'])

    def test_schema_preserves_only_known_legacy_errors_and_validates_notes(self):
        validator = Draft202012Validator(self.schema)
        notes_validator = Draft202012Validator(
            self.schema['properties']['translation']['properties']['footnotes'])
        for number, target in self.contract['targets'].items():
            key = (2, int(number))
            self.assertEqual(schema_errors(validator, self.historical[key]),
                             target['before_schema_errors'])
            self.assertEqual(schema_errors(validator, self.candidates[key]),
                             target['candidate_schema_errors'])
            notes_validator.validate(self.candidates[key]['translation']['footnotes'])
        validator.validate(self.candidates[(2, 5)])
        # A scoped note update must not invent metadata to conceal existing debt.
        self.assertEqual(self.contract['targets']['16']['candidate_schema_errors'], [
            {'path': [], 'validator': 'required', 'message': "'ai_draft' is a required property"},
            {'path': ['translation'], 'validator': 'required', 'message': "'philosophy' is a required property"}])

    def test_complete_historical_and_proposed_book_exports(self):
        with patch.object(exporter, 'load_translation_record',
                          side_effect=lambda code, ch, v: self.historical[(ch, v)]):
            before = exporter.export_book('HAB')
        with patch.object(exporter, 'load_translation_record', side_effect=lambda code, ch, v:
                          self.candidates.get((ch, v), self.historical[(ch, v)])):
            after = exporter.export_book('HAB')
        a, b = index(after), index(before)
        self.assertEqual(len(self.historical), 56)
        self.assertEqual(set(a), set(self.historical))
        self.assertEqual((len(before['chapters']), len(after['chapters']), len(a)), (3, 3, 56))
        changed = [list(k) for k in a if a[k] != b[k]]
        self.assertEqual(changed, [[2, 5], [2, 16]])
        preflight = self.contract['preflight']
        self.assertIs(preflight['canonical_written'], False)
        self.assertEqual(preflight['changed_export_ids'], changed)
        self.assertEqual(preflight['other_units_unchanged'], 54)
        self.assertEqual(digest(before), preflight['before_export_sha256'])
        self.assertEqual(digest(after), preflight['candidate_export_sha256'])
        for key in TARGETS:
            self.assertEqual(a[key]['footnotes'], self.candidates[key]['translation']['footnotes'])
            self.assertEqual(len(a[key]['footnotes']), preflight['footnote_counts'][f'{key[0]}.{key[1]}'])
            self.assertNotIn('review_history', a[key])

    def test_exact_current_targets_historical_complete_export_and_application_receipt(self):
        expected_hashes = {number: target['candidate_yaml_sha256']
                           for number, target in self.contract['targets'].items()}
        paths = {target['canonical_target'] for target in self.contract['targets'].values()}
        for number, target in self.contract['targets'].items():
            self.assertEqual((ROOT / target['canonical_target']).read_bytes(),
                             self.candidate_raw[(2, int(number))])
            self.assertEqual(audit_footnotes.audit_one(ROOT / target['canonical_target'])['status'], 'ok')
        for path, pin in self.contract['book_baseline_pins'].items():
            if path not in paths:
                applied_raw = subprocess.check_output(['git', 'show', f'{APPLIED_COMMIT}:{path}'], cwd=ROOT)
                self.assertEqual(sha(applied_raw), pin, path)
        with patch.object(exporter, 'load_translation_record',
                          side_effect=lambda code, ch, v: self.applied[(ch, v)]):
            after = exporter.export_book('HAB')
        self.assertEqual(digest(after), self.contract['preflight']['candidate_export_sha256'])
        self.assertEqual(len(index(after)), 56)
        for key in TARGETS:
            self.assertEqual(index(after)[key]['footnotes'], self.candidates[key]['translation']['footnotes'])
        current = index(exporter.export_book('HAB'))
        for key in TARGETS:
            self.assertEqual(current[key], index(after)[key])
        receipt = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(receipt['contract'], CONTRACT)
        self.assertEqual(receipt['contract_sha256'], CONTRACT_SHA)
        self.assertEqual(receipt['candidate_yaml_sha256'], expected_hashes)
        self.assertEqual(receipt['review']['status'], 'pass')
        self.assertEqual(receipt['review']['reviewed_candidate_yaml_sha256'], expected_hashes)
        self.assertEqual(receipt['review']['reviewed_contract_sha256'], CONTRACT_SHA)
        self.assertEqual(receipt['application']['status'], 'applied-local-verified')
        self.assertEqual(receipt['application']['after_export_sha256'], digest(after))
        self.assertEqual(receipt['application']['changed_export_ids'], [[2, 5], [2, 16]])
        self.assertEqual(receipt['application']['other_units_unchanged'], 54)
        self.assertEqual(receipt['decisions'], self.contract['scope'])
        self.assertTrue(all(value is False for value in receipt['decisions'].values()))


if __name__ == '__main__':
    unittest.main()
