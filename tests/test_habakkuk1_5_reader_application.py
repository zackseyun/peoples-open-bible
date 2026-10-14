"""Retained-source disclosure and book export, not earliest-text certification."""
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
BASE = 'c769c858a85a6140c6b7a551855c4db1b734d0a7'
APPLIED = 'c62b1903963cfafce58b9a87770994e4d0a1df4b'
CONTRACT = 'sources/textual_restoration/comparisons/habakkuk1_5_reader_contract.2026-10-12.v1.json'
RECEIPT = 'sources/textual_restoration/applications/habakkuk1_5_reader.2026-10-12.v1.json'
TARGET = (1, 5)


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


class HabakkukReaderApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / CONTRACT).read_text())
        cls.candidate_raw = (ROOT / cls.contract['candidate']).read_bytes()
        cls.candidate = yaml.safe_load(cls.candidate_raw)
        cls.historical = {}
        for pin in cls.contract['book_baseline_pins']:
            raw = subprocess.check_output(['git', 'show', f"{BASE}:{pin['path']}"], cwd=ROOT)
            assert sha(raw) == pin['sha256'], pin['path']
            path = Path(pin['path'])
            cls.historical[(int(path.parent.name), int(path.stem))] = yaml.safe_load(raw)
        cls.before = cls.historical[TARGET]

    def test_frozen_inputs_schema_and_scope(self):
        c, b, contract = self.candidate, self.before, self.contract
        self.assertEqual(contract['baseline_commit'], BASE)
        self.assertEqual(sha(self.candidate_raw), contract['candidate_yaml_sha256'])
        for path, pin in contract['input_pins'].items():
            raw = subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)
            self.assertEqual(sha(raw), pin, path)
        self.assertEqual(contract['baseline_yaml_sha256'],
                         next(p['sha256'] for p in contract['book_baseline_pins']
                              if p['path'] == contract['canonical_target']))
        allowed = {'translation', 'lexical_decisions', 'theological_decisions',
                   'status', 'revision_pass', 'cross_check', 'revisions',
                   'review_history', 'source_audit'}
        self.assertLessEqual({k for k in set(b) | set(c) if b.get(k) != c.get(k)}, allowed)
        for key in ('id', 'reference', 'source', 'ai_draft'):
            self.assertEqual(c[key], b[key], key)
        self.assertEqual(c['translation']['philosophy'], b['translation']['philosophy'])
        self.assertEqual(plain(c['translation']['text']), plain(b['translation']['text']))
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(c)

    def test_exact_note_anchors_and_preservation_qualifiers(self):
        c = self.candidate
        self.assertEqual(c['translation']['text'],
                         'Look among the nations[a] and see; be astonished, be astounded[b]. '
                         'For I am doing a work[c] in your days that you would not believe if it were told.')
        notes = c['translation']['footnotes']
        self.assertEqual([n['marker'] for n in notes], ['a', 'b', 'c'])
        self.assertEqual(re.findall(r'\[([a-z])\]', c['translation']['text']), ['a', 'b', 'c'])
        for phrase in ('Greek version', 'despisers', 'Acts 13:41', 'Mur88 preserves',
                       'quoted verse of 1QpHab is supplied', 'commentary concerns traitors',
                       'earliest address remains unresolved'):
            self.assertIn(phrase, notes[0]['text'])
        self.assertEqual(notes[0]['reason'], 'textual_variant')
        self.assertIn('two astonishment commands', notes[1]['text'])
        for phrase in ('a deed is being done', 'no explicit first-person pronoun',
                       'inferred from the speaker context', 'especially verse 6',
                       'Greek explicitly expresses'):
            self.assertIn(phrase, notes[2]['text'])
        self.assertEqual(audit_footnotes.audit_one(ROOT / self.contract['candidate'])['status'], 'ok')

    def test_only_connected_lexical_and_theological_fields_change(self):
        c, b = self.candidate, self.before
        expected_lexical = copy.deepcopy(b['lexical_decisions'])
        expected_lexical[3]['chosen'] = 'be astonished, be astounded'
        expected_lexical[5]['rationale'] = c['lexical_decisions'][5]['rationale']
        self.assertEqual(c['lexical_decisions'], expected_lexical)
        self.assertIn('not an explicit pronoun', c['lexical_decisions'][5]['rationale'])
        self.assertIn('impersonal rendering remains possible', c['lexical_decisions'][5]['rationale'])
        self.assertIn('no fresh entry consultation', c['lexical_decisions'][5]['rationale'])
        expected_theological = copy.deepcopy(b['theological_decisions'])
        expected_theological[0]['rationale'] = c['theological_decisions'][0]['rationale']
        expected_theological[1]['chosen_reading'] = 'be astonished, be astounded'
        expected_theological[1]['doctrine_reference'] = 'Translation philosophy §§1, 5'
        self.assertEqual(c['theological_decisions'], expected_theological)
        self.assertIn('not a restoration of Hebrew pronoun letters',
                      c['theological_decisions'][0]['rationale'])

    def test_six_exact_archives_revisions_and_current_review_status(self):
        c, b = self.candidate, self.before
        expected = {'status', 'revision_pass', 'cross_check', 'translation',
                    'lexical_decisions', 'theological_decisions'}
        self.assertEqual(len(c['review_history']), 6)
        self.assertEqual({h['field'] for h in c['review_history']}, expected)
        for h in c['review_history']:
            self.assertEqual(h['value'], b[h['field']], h['field'])
            self.assertEqual(h['archived_from_baseline_sha256'], self.contract['baseline_yaml_sha256'])
            self.assertIs(h['historical_review_inputs_verified'], False)
            self.assertIs(h['certifies_this_candidate'], False)
        self.assertEqual(c['status'], 'draft')
        self.assertEqual(c['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', c)
        self.assertEqual(c['revisions'][:-1], b['revisions'])
        self.assertEqual(c['revisions'][-1]['from'], b['translation']['text'])
        self.assertEqual(c['revisions'][-1]['to'], c['translation']['text'])
        self.assertEqual(c['revisions'][-1]['baseline_sha256'], self.contract['baseline_yaml_sha256'])
        audit = c['source_audit']
        self.assertEqual(audit['historical_priority'], 'HOLD')
        self.assertIs(audit['source_consonants_pointing_segmentation_retained'], True)
        for flag in ('greek_address_is_unique_hebrew_restoration',
                     'whole_verse_optimality_certified', 'generated_images_used_as_evidence',
                     'fresh_halot_consultation'):
            self.assertIs(audit[flag], False)
        self.assertEqual(audit['comparison_report_sha256'],
                         self.contract['input_pins'][audit['comparison_report']])

    def test_complete_historical_and_proposed_book_exports(self):
        historical = lambda code, ch, v: self.historical[(ch, v)]
        proposed = lambda code, ch, v: self.candidate if (ch, v) == TARGET else self.historical[(ch, v)]
        with patch.object(exporter, 'load_translation_record', side_effect=historical):
            before = exporter.export_book('HAB')
        with patch.object(exporter, 'load_translation_record', side_effect=proposed):
            after = exporter.export_book('HAB')
        a, b = index(after), index(before)
        self.assertEqual(len(self.historical), 56)
        self.assertEqual(set(a), set(self.historical))
        self.assertEqual((len(before['chapters']), len(after['chapters']), len(a)), (3, 3, 56))
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[1, 5]])
        self.assertEqual(a[TARGET]['footnotes'], self.candidate['translation']['footnotes'])
        self.assertEqual(len(a[TARGET]['footnotes']), 3)
        preflight = self.contract['preflight']
        self.assertIs(preflight['canonical_written'], False)
        self.assertEqual(preflight['other_units_unchanged'], 55)
        self.assertEqual(preflight['changed_export_ids'], [[1, 5]])
        self.assertEqual(digest(before), preflight['before_export_sha256'])
        self.assertEqual(digest(after), preflight['candidate_export_sha256'])
        self.assertNotIn('review_history', a[TARGET])

    def test_exact_current_target_historical_applied_export_and_receipt(self):
        # Later reviewed applications may change other verses. This receipt
        # certifies the book as published by this transaction, not all future books.
        raw = (ROOT / self.contract['canonical_target']).read_bytes()
        self.assertEqual(raw, self.candidate_raw)
        applied = {}
        for pin in self.contract['book_baseline_pins']:
            historical_raw = subprocess.check_output(
                ['git', 'show', f"{APPLIED}:{pin['path']}"], cwd=ROOT)
            if pin['path'] == self.contract['canonical_target']:
                self.assertEqual(historical_raw, self.candidate_raw)
            else:
                self.assertEqual(sha(historical_raw), pin['sha256'], pin['path'])
            path = Path(pin['path'])
            applied[(int(path.parent.name), int(path.stem))] = yaml.safe_load(historical_raw)
        with patch.object(exporter, 'load_translation_record',
                          side_effect=lambda code, ch, v: applied[(ch, v)]):
            after = exporter.export_book('HAB')
        self.assertEqual(digest(after), self.contract['preflight']['candidate_export_sha256'])
        self.assertEqual(index(after)[TARGET]['footnotes'], self.candidate['translation']['footnotes'])
        self.assertEqual(audit_footnotes.audit_one(ROOT / self.contract['canonical_target'])['status'], 'ok')
        receipt = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(receipt['contract'], CONTRACT)
        self.assertEqual(receipt['contract_sha256'], sha((ROOT / CONTRACT).read_bytes()))
        self.assertEqual(receipt['candidate_yaml_sha256'], sha(self.candidate_raw))
        self.assertEqual(receipt['review']['status'], 'pass')
        self.assertEqual(receipt['review']['reviewed_candidate_yaml_sha256'], sha(self.candidate_raw))
        self.assertEqual(receipt['review']['reviewed_contract_sha256'], receipt['contract_sha256'])
        self.assertEqual(receipt['application']['status'], 'applied-local-verified')
        self.assertEqual(receipt['application']['after_export_sha256'], digest(after))
        self.assertEqual(receipt['application']['changed_export_ids'], [[1, 5]])
        self.assertEqual(receipt['application']['other_units_unchanged'], 55)
        self.assertEqual(receipt['decisions'], self.contract['scope'])
        self.assertTrue(all(value is False for value in receipt['decisions'].values()))


if __name__ == '__main__':
    unittest.main()
