"""Exact scoped disclosure, not earliest-text or whole-verse certification."""
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
BASE = '6017ffa06c1fc8eee2247ce01308df131fcfc557'
CONTRACT = 'sources/textual_restoration/comparisons/habakkuk1_17_reader_contract.2026-10-12.v1.json'
CONTRACT_SHA = 'bb82167b173cda694658212ee458d2d1d6e5bf83c695234b41b22b0e6a63b534'
RECEIPT = 'sources/textual_restoration/applications/habakkuk1_17_reader.2026-10-12.v1.json'
KEY = (1, 17)


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


class Habakkuk117ReaderDisclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract_raw = (ROOT / CONTRACT).read_bytes()
        cls.contract = json.loads(cls.contract_raw)
        cls.target = cls.contract['target']
        cls.candidate_raw = (ROOT / cls.target['candidate']).read_bytes()
        cls.candidate = yaml.safe_load(cls.candidate_raw)
        cls.historical = {}
        for path, pin in cls.contract['book_baseline_pins'].items():
            raw = subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)
            assert sha(raw) == pin, path
            location = Path(path)
            cls.historical[(int(location.parent.name), int(location.stem))] = yaml.safe_load(raw)
        cls.before = cls.historical[KEY]
        cls.schema = json.loads((ROOT / 'schema/verse.schema.json').read_text())

    def test_frozen_inputs_and_exact_candidate(self):
        self.assertEqual(sha(self.contract_raw), CONTRACT_SHA)
        self.assertEqual(self.contract['baseline_commit'], BASE)
        self.assertEqual(sha(self.candidate_raw), self.target['candidate_yaml_sha256'])
        self.assertEqual(self.target['baseline_yaml_sha256'],
                         self.contract['book_baseline_pins'][self.target['canonical_target']])
        for path, pin in self.contract['input_pins'].items():
            historical = subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)
            self.assertEqual(sha(historical), pin, path)
            self.assertEqual(sha((ROOT / path).read_bytes()), pin, path)
        self.assertEqual(digest(self.contract['book_baseline_pins']),
                         self.contract['book_baseline_manifest_sha256'])

    def test_exact_source_main_english_and_generation_provenance(self):
        for field in ('id', 'reference', 'source', 'ai_draft'):
            self.assertEqual(self.candidate[field], self.before[field])
        self.assertEqual(plain(self.candidate['translation']['text']),
                         plain(self.before['translation']['text']))
        self.assertEqual(self.candidate['translation']['philosophy'],
                         self.before['translation']['philosophy'])
        allowed = {'translation', 'lexical_decisions', 'status', 'revision_pass',
                   'cross_check', 'revisions', 'review_history', 'source_audit'}
        self.assertLessEqual({k for k in set(self.before) | set(self.candidate)
                              if self.before.get(k) != self.candidate.get(k)}, allowed)
        self.assertFalse(any(self.contract['scope'].values()))

    def test_exact_disclosure_and_relabelled_existing_notes(self):
        t = self.candidate['translation']
        self.assertEqual(t['text'], 'Will he therefore keep emptying his net[a][b] '
                         'and continually slaughtering nations without mercy?[c]')
        self.assertEqual(t['footnotes'], self.target['footnotes'])
        self.assertEqual(t['footnotes'][0]['reason'], 'textual_variant')
        self.assertEqual(t['footnotes'][1], self.before['translation']['footnotes'][1])
        mercy = copy.deepcopy(self.before['translation']['footnotes'][0])
        mercy['marker'] = 'c'
        self.assertEqual(t['footnotes'][2], mercy)
        self.assertEqual(re.findall(r'\[([a-z])\]', t['text']), ['a', 'b', 'c'])
        self.assertEqual(audit_footnotes.audit_one(ROOT / self.target['candidate'])['status'], 'ok')

    def test_only_connected_net_rationale_changes(self):
        lexical = copy.deepcopy(self.before['lexical_decisions'])
        self.assertEqual(lexical[2]['source_word'], 'חֶרְמוֹ')
        lexical[2]['rationale'] = self.candidate['lexical_decisions'][2]['rationale']
        self.assertEqual(self.candidate['lexical_decisions'], lexical)
        for phrase in ('Retention is provisional', 'different source wording',
                       'not another lexical gloss', 'Source priority remains HOLD',
                       'no fresh HALOT entry consultation'):
            self.assertIn(phrase, lexical[2]['rationale'])

    def test_exact_archives_revisions_and_no_score_transfer(self):
        history = self.candidate['review_history']
        self.assertEqual([h['field'] for h in history], self.target['archive_fields'])
        self.assertEqual(len(history), 5)
        for item in history:
            self.assertEqual(item['value'], self.before[item['field']])
            self.assertEqual(item['archived_from_baseline_sha256'], self.target['baseline_yaml_sha256'])
            self.assertIs(item['historical_review_inputs_verified'], False)
            self.assertIs(item['certifies_this_candidate'], False)
        self.assertEqual(self.candidate['revisions'][:-1], self.before['revisions'])
        revision = self.candidate['revisions'][-1]
        self.assertEqual(revision['from'], self.before['translation']['text'])
        self.assertEqual(revision['to'], self.candidate['translation']['text'])
        self.assertEqual(revision['baseline_sha256'], self.target['baseline_yaml_sha256'])
        self.assertEqual(self.candidate['status'], 'draft')
        self.assertEqual(self.candidate['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', self.candidate)
        audit = self.candidate['source_audit']
        self.assertEqual(audit['historical_priority'], 'HOLD')
        for flag in ('declared_source_retained', 'source_consonants_pointing_segmentation_retained',
                     'marker_free_main_english_retained', 'reader_disclosure_scope_only'):
            self.assertIs(audit[flag], True)
        for flag in ('whole_verse_optimality_certified', 'generated_images_used_as_evidence',
                     'fresh_halot_consultation', 'fresh_manuscript_transcription',
                     'full_source_census_complete'):
            self.assertIs(audit[flag], False)
        for kind in ('report', 'receipt'):
            self.assertEqual(audit[f'comparison_{kind}_sha256'],
                             self.contract['input_pins'][audit[f'comparison_{kind}']])

    def test_full_candidate_schema_and_recorded_baseline_debt(self):
        validator = Draft202012Validator(self.schema)
        validator.validate(self.candidate)
        self.assertEqual(self.target['candidate_schema_errors'], [])
        errors = [{'path': list(e.path), 'validator': e.validator, 'message': e.message}
                  for e in validator.iter_errors(self.before)]
        self.assertEqual(errors, self.target['before_schema_errors'])

    def test_complete_historical_and_proposed_book_exports(self):
        with patch.object(exporter, 'load_translation_record',
                          side_effect=lambda code, ch, v: self.historical[(ch, v)]):
            before = exporter.export_book('HAB')
        with patch.object(exporter, 'load_translation_record', side_effect=lambda code, ch, v:
                          self.candidate if (ch, v) == KEY else self.historical[(ch, v)]):
            after = exporter.export_book('HAB')
        a, b = index(after), index(before)
        self.assertEqual((len(before['chapters']), len(after['chapters']), len(a)), (3, 3, 56))
        self.assertEqual(set(a), set(self.historical))
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[1, 17]])
        preflight = self.contract['preflight']
        self.assertIs(preflight['canonical_written'], False)
        self.assertEqual(preflight['other_units_unchanged'], 55)
        self.assertEqual(digest(before), preflight['before_export_sha256'])
        self.assertEqual(digest(after), preflight['candidate_export_sha256'])
        self.assertEqual(a[KEY]['footnotes'], self.candidate['translation']['footnotes'])
        self.assertEqual(len(a[KEY]['footnotes']), 3)
        self.assertNotIn('review_history', a[KEY])

    def test_applied_current_complete_export_and_receipt(self):
        self.assertEqual((ROOT / self.target['canonical_target']).read_bytes(), self.candidate_raw)
        self.assertEqual(audit_footnotes.audit_one(ROOT / self.target['canonical_target'])['status'], 'ok')
        for path, pin in self.contract['book_baseline_pins'].items():
            if path != self.target['canonical_target']:
                self.assertEqual(sha((ROOT / path).read_bytes()), pin, path)
        after = exporter.export_book('HAB')
        self.assertEqual(len(index(after)), 56)
        self.assertEqual(digest(after), self.contract['preflight']['candidate_export_sha256'])
        self.assertEqual(index(after)[KEY]['footnotes'], self.candidate['translation']['footnotes'])
        receipt = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(receipt['contract'], CONTRACT)
        self.assertEqual(receipt['contract_sha256'], CONTRACT_SHA)
        self.assertEqual(receipt['candidate_yaml_sha256'], sha(self.candidate_raw))
        self.assertEqual(receipt['review']['status'], 'pass')
        self.assertEqual(receipt['review']['reviewed_contract_sha256'], CONTRACT_SHA)
        self.assertEqual(receipt['review']['reviewed_candidate_yaml_sha256'], sha(self.candidate_raw))
        self.assertEqual(receipt['application']['status'], 'applied-local-verified')
        self.assertIs(receipt['application']['canonical_written'], True)
        self.assertEqual(receipt['application']['after_export_sha256'], digest(after))
        self.assertEqual(receipt['application']['changed_export_ids'], [[1, 17]])
        self.assertEqual(receipt['application']['other_units_unchanged'], 55)


if __name__ == '__main__':
    unittest.main()
