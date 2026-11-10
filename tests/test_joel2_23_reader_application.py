"""Scoped Joel timing interpretation and notes; not earliest-source certification."""
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
from tools import export_mobile_bible as ex

ROOT = Path(__file__).resolve().parents[1]
BASE = 'e8791d444be8f298857dbb6145164d52b0a47b9b'
CONTRACT = 'sources/textual_restoration/comparisons/joel2_23_reader_contract.2026-10-12.v1.json'
RECEIPT = 'sources/textual_restoration/applications/joel2_23_reader.2026-10-12.v1.json'
TARGET = (2, 23)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def plain(text):
    return re.sub(r'\[[a-z]+\]', '', text)

def digest(obj):
    return sha(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())

def index(book):
    return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}

class JoelReaderApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / CONTRACT).read_text())
        cls.candidate = json.loads((ROOT / cls.contract['candidate']).read_text())
        cls.before = {}
        for pin in cls.contract['book_baseline_pins']:
            raw = subprocess.check_output(['git', 'show', f"{BASE}:{pin['path']}"], cwd=ROOT)
            assert sha(raw) == pin['sha256']
            p = Path(pin['path'])
            cls.before[(int(p.parent.name), int(p.stem))] = yaml.safe_load(raw)

    def test_candidate_pins_and_preserved_source(self):
        c, k, b = self.candidate, self.contract, self.before[TARGET]
        self.assertEqual(k['baseline_commit'], BASE)
        self.assertEqual(sha((ROOT / k['candidate']).read_bytes()), k['candidate_sha256'])
        self.assertEqual(sha(yaml.safe_dump(c, allow_unicode=True, sort_keys=False, width=1000).encode()),
                         k['candidate_yaml_sha256'])
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(c)
        for field in ('id', 'reference', 'source', 'ai_draft'):
            self.assertEqual(c[field], b[field])
        self.assertEqual(c['translation']['philosophy'], b['translation']['philosophy'])
        self.assertEqual(plain(c['translation']['text']),
                         plain(b['translation']['text']).replace('as before.', 'in the first month.'))
        self.assertEqual(c['status'], 'draft')
        self.assertEqual(c['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', c)
        changed = {key for key in set(b) | set(c) if b.get(key) != c.get(key)}
        self.assertEqual(changed, {'translation', 'lexical_decisions', 'theological_decisions',
                                 'revision_pass', 'revisions', 'status', 'cross_check',
                                 'review_history', 'source_audit', 'textual_comparison'})

    def test_exact_archives_and_revision_history(self):
        c, b, k = self.candidate, self.before[TARGET], self.contract
        old = b.get('review_history', [])
        self.assertEqual(c['review_history'][:len(old)], old)
        archives = c['review_history'][len(old):]
        self.assertEqual(len(archives), 7)
        self.assertEqual({h['field'] for h in archives}, {
            'status', 'revision_pass', 'cross_check', 'translation.text',
            'translation.footnotes', 'lexical_decisions', 'theological_decisions'})
        for h in archives:
            value = b
            for key in h['field'].split('.'):
                value = value[key]
            self.assertEqual(h['value'], value)
            self.assertEqual(h['archived_from_baseline_sha256'], k['baseline_yaml_sha256'])
            self.assertIs(h['historical_review_inputs_verified'], False)
            self.assertIs(h['certifies_this_candidate'], False)
        self.assertEqual(c['revisions'][:-1], b['revisions'])
        self.assertEqual(c['revisions'][-1]['from'], b['translation']['text'])
        self.assertEqual(c['revisions'][-1]['to'], c['translation']['text'])

    def test_notes_anchors_and_disclosure(self):
        c = self.candidate
        text = c['translation']['text']
        self.assertEqual(re.findall(r'\[([a-z]+)\]', text), ['a', 'b', 'c'])
        self.assertIn('early rain[a] for righteousness[b]', text)
        self.assertTrue(text.endswith('in the first month[c].'))
        notes = c['translation']['footnotes']
        self.assertEqual([n['marker'] for n in notes], ['a', 'b', 'c'])
        self.assertIn('Latin reads teacher', notes[0]['text'])
        self.assertIn('Greek and Syriac use food', notes[0]['text'])
        self.assertIn('do not prove a different Hebrew noun', notes[0]['text'])
        self.assertIn('for your vindication', notes[1]['text'])
        self.assertIn('for your prosperity', notes[1]['text'])
        self.assertIn('not a general promise of wealth', notes[1]['text'])
        for phrase in ('at first', 'as formerly', 'no explicit date formula',
                       'both seasonal rains', 'not adopted'):
            self.assertIn(phrase, notes[2]['text'])
        self.assertEqual(audit_footnotes.audit_one(ROOT / self.contract['candidate'])['status'], 'ok')

    def test_only_dependent_metadata_changes(self):
        c, b = self.candidate, self.before[TARGET]
        self.assertEqual(len(c['lexical_decisions']), len(b['lexical_decisions']))
        for i, entry in enumerate(c['lexical_decisions']):
            self.assertEqual(entry['source_word'], b['lexical_decisions'][i]['source_word'])
            self.assertEqual(entry['lexicon'], b['lexical_decisions'][i]['lexicon'])
            if i not in (2, 4, 8):
                self.assertEqual(entry, b['lexical_decisions'][i])
            else:
                changed = {key for key in set(entry) | set(b['lexical_decisions'][i])
                           if entry.get(key) != b['lexical_decisions'][i].get(key)}
                self.assertEqual(changed, {'alternatives', 'rationale'} if i == 4 else
                                 {'chosen', 'alternatives', 'rationale'})
        self.assertEqual(c['lexical_decisions'][2]['chosen'], 'in Yahweh your God')
        self.assertEqual(c['lexical_decisions'][8]['chosen'], 'in the first month')
        self.assertNotIn('A minority reading takes', c['lexical_decisions'][8]['rationale'])
        self.assertIn('unsupported and removed', c['lexical_decisions'][8]['rationale'])
        for i, expected in ((0, {'rationale'}), (1, {'chosen_reading', 'alternative_readings', 'rationale'})):
            changed = {key for key in set(c['theological_decisions'][i]) | set(b['theological_decisions'][i])
                       if c['theological_decisions'][i].get(key) != b['theological_decisions'][i].get(key)}
            self.assertEqual(changed, expected)
        self.assertIn('teacher need not automatically', c['theological_decisions'][0]['rationale'].lower())
        self.assertIn('not a veto', c['theological_decisions'][1]['rationale'])
        self.assertEqual(c['source_audit']['historical_priority'], 'HOLD')
        self.assertIs(c['source_audit']['canonical_calendar_identified'], False)
        self.assertIs(c['source_audit']['generated_images_used_as_evidence'], False)
        self.assertIs(c['textual_comparison']['whole_verse_optimality_certified'], False)

    def test_english_assessment_and_historical_input_pins(self):
        k, c = self.contract, self.candidate
        new = set(k['new_input_paths'])
        for path, expected in k['input_pins'].items():
            raw = ((ROOT / path).read_bytes() if path in new else
                   subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))
            self.assertEqual(sha(raw), expected, path)
        packet = json.loads((ROOT / c['textual_comparison']['english_contract']).read_text())
        result = json.loads((ROOT / c['textual_comparison']['english_result']).read_text())
        self.assertEqual(sha((ROOT / result['contract']).read_bytes()), result['contract_sha256'])
        self.assertEqual(packet['source_text'], c['source']['text'])
        self.assertEqual(plain(c['translation']['text']), packet['candidates']['M'])
        self.assertEqual(result['working_preference'], 'M')
        self.assertIs(result['repeat_until_agreement'], False)
        self.assertIn('cannot be independently checked', result['actual_assessment'])
        target = [r for r in packet['source_context'] if r['reference'] == 'Joel 2:23'][0]
        self.assertNotIn('english', target)
        self.assertIs(packet['blinding']['full_main_english_blind_vote_claimed'], False)

    def test_frozen_complete_book_export(self):
        self.assertEqual(len(self.before), 73)
        loader = ex.load_translation_record
        def load(code, ch, v, proposed=False):
            if code != 'JOL':
                return loader(code, ch, v)
            return self.candidate if proposed and (ch, v) == TARGET else self.before[(ch, v)]
        with patch.object(ex, 'load_translation_record', side_effect=lambda c, ch, v: load(c, ch, v)):
            before = ex.export_book('JOL')
        with patch.object(ex, 'load_translation_record', side_effect=lambda c, ch, v: load(c, ch, v, True)):
            after = ex.export_book('JOL')
        self.assertEqual(digest(before), self.contract['export']['before_sha256'])
        self.assertEqual(digest(after), self.contract['export']['proposed_sha256'])
        bi, ai = index(before), index(after)
        self.assertEqual([k for k in bi if bi[k] != ai[k]], [TARGET])
        self.assertEqual(ai[TARGET]['footnotes'], self.candidate['translation']['footnotes'])

    def test_current_application_state_and_other_files(self):
        receipt = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(sha((ROOT / CONTRACT).read_bytes()), receipt['contract_sha256'])
        for pin in self.contract['book_baseline_pins']:
            p = ROOT / pin['path']
            if str(p.relative_to(ROOT)) != self.contract['canonical_target']:
                self.assertEqual(sha(p.read_bytes()), pin['sha256'])
        raw = (ROOT / self.contract['canonical_target']).read_bytes()
        if receipt['canonical_change_applied']:
            self.assertEqual(sha(raw), self.contract['candidate_yaml_sha256'])
            self.assertEqual(yaml.safe_load(raw), self.candidate)
            book = ex.export_book('JOL')
            self.assertEqual(digest(book), self.contract['export']['proposed_sha256'])
            self.assertEqual(len(book['chapters']), 4)
            self.assertEqual(len(index(book)), 73)
            actual = index(book)[TARGET]
            self.assertEqual(actual['text'], self.candidate['translation']['text'])
            self.assertEqual(actual['footnotes'], self.candidate['translation']['footnotes'])
        else:
            self.assertEqual(sha(raw), self.contract['baseline_yaml_sha256'])

if __name__ == '__main__':
    unittest.main()
