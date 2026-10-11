"""Scoped Nahum 3 pesher disclosures; not source-priority certification."""
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
BASE = '8f63b40ff486daa2641160acf5ddb7daa775466f'
CONTRACT = 'sources/textual_restoration/comparisons/nahum3_6_11_reader_contract.2026-10-10.v1.json'
RECEIPT = 'sources/textual_restoration/applications/nahum3_6_11_reader.2026-10-10.v1.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def plain(text):
    return re.sub(r'\[[a-z]\]', '', text)


def index(book):
    return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}


def digest(book):
    return sha(json.dumps(book, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


class Nahum3PesherReaderApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / CONTRACT).read_text())
        cls.pins = {(int(Path(p['path']).parent.name), int(Path(p['path']).stem)): p
                    for p in cls.contract['records']}
        cls.before, cls.candidates = {}, {}
        for key, pin in cls.pins.items():
            raw = subprocess.check_output(['git', 'show', f"{BASE}:{pin['path']}"], cwd=ROOT)
            assert sha(raw) == pin['before_sha256']
            cls.before[key] = yaml.safe_load(raw)
            cls.candidates[key] = json.loads((ROOT / pin['candidate']).read_text())

    def test_frozen_complete_records_preserve_fields_and_exact_archives(self):
        self.assertEqual(self.contract['baseline_commit'], BASE)
        self.assertEqual(set(self.pins), {(3, 6), (3, 11)})
        self.assertEqual(sha((ROOT / self.contract['source_comparison']).read_bytes()),
                         self.contract['source_comparison_sha256'])
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        for key, c in self.candidates.items():
            with self.subTest(verse=key):
                b, pin = self.before[key], self.pins[key]
                validator.validate(c)
                self.assertEqual(sha((ROOT / pin['candidate']).read_bytes()), pin['candidate_sha256'])
                self.assertEqual(sha(yaml.safe_dump(c, allow_unicode=True, sort_keys=False,
                                                  width=1000).encode()), pin['candidate_yaml_sha256'])
                for field in ('id', 'reference', 'source', 'ai_draft'):
                    self.assertEqual(c[field], b[field])
                self.assertEqual(plain(c['translation']['text']), plain(b['translation']['text']))
                self.assertEqual(c['translation']['philosophy'], b['translation']['philosophy'])
                self.assertEqual(c.get('theological_decisions'), b.get('theological_decisions'))
                self.assertEqual({f for f in set(b['translation']) | set(c['translation'])
                                  if b['translation'].get(f) != c['translation'].get(f)},
                                 {'text', 'footnotes'})
                history = {h['field']: h for h in c['review_history']}
                expected = {'status', 'revision_pass', 'cross_check', 'translation.text',
                            'translation.footnotes', 'lexical_decisions'}
                if 'theological_decisions' in b:
                    expected.add('theological_decisions')
                self.assertEqual(set(history), expected)
                self.assertEqual(len(c['review_history']), len(expected))
                for field, h in history.items():
                    obj = b
                    for part in field.split('.'):
                        obj = obj[part]
                    self.assertEqual(h['value'], obj)
                    self.assertEqual(h['archived_from_baseline_sha256'], pin['before_sha256'])
                    self.assertIs(h['historical_review_inputs_verified'], False)
                    self.assertIs(h['certifies_this_candidate'], False)
                self.assertEqual(c['status'], 'draft')
                self.assertEqual(c['cross_check'], {'status': 'needs_review'})
                self.assertNotIn('revision_pass', c)
                self.assertEqual(c['revisions'][:-1], b.get('revisions', []))
                revision = c['revisions'][-1]
                self.assertEqual(revision['from'], b['translation']['text'])
                self.assertEqual(revision['to'], c['translation']['text'])
                self.assertEqual(revision['baseline_sha256'], pin['before_sha256'])
                allowed = {'translation', 'lexical_decisions', 'status', 'revision_pass',
                           'cross_check', 'review_history', 'revisions'}
                self.assertLessEqual({f for f in set(b) | set(c) if b.get(f) != c.get(f)}, allowed)

    def test_exact_semantic_anchors_and_qualified_published_readings(self):
        expected_text = {
            (3, 6): 'And I will throw filth upon you[a], and treat you with contempt, '
                    'and make you a spectacle[b].',
            (3, 11): 'You too will become drunk[b]; you will be hidden. '
                     'You too will seek a refuge[a] from the enemy[c].',
        }
        for key, c in self.candidates.items():
            self.assertEqual(c['translation']['text'], expected_text[key])
            notes = c['translation']['footnotes']
            self.assertEqual([n['marker'] for n in notes], ['a', 'b'] if key == (3, 6)
                             else ['a', 'b', 'c'])
            self.assertEqual(re.findall(r'\[([a-z])\]', c['translation']['text']),
                             ['a', 'b'] if key == (3, 6) else ['b', 'a', 'c'])
            for note in notes:
                self.assertEqual(c['translation']['text'].count('[' + note['marker'] + ']'), 1)
            b = self.before[key]
            self.assertEqual(notes[0], b['translation']['footnotes'][0])
            if key == (3, 11):
                self.assertEqual(notes[1], b['translation']['footnotes'][1])
            note = notes[-1]
            self.assertEqual(note['reason'], 'textual_variant')
            phrases = ('retained provisionally', 'quotation', 'Nahum commentary', '4Q169',
                       'Murabba\'at scroll', 'supplied')
            phrases += (('iii 2', 'כאורה', 'repulsive', 'earlier wording', 'adapts',
                         'remains uncertain', 'decisive ending') if key == (3, 6) else
                        ('iv 7', 'בעיר', 'in a city', 'opening verb is supplied',
                         'in the city', 'Inherited wording', 'adaptation',
                         "words for 'refuge from the enemy'", 'does not attest omission'))
            for phrase in phrases:
                self.assertIn(phrase.lower(), note['text'].lower())

    def test_only_dependent_lexical_fields_change(self):
        for key, c in self.candidates.items():
            entries, old = c['lexical_decisions'], self.before[key]['lexical_decisions']
            self.assertEqual(len(entries), len(old))
            for i, entry in enumerate(entries):
                changed = {f for f in set(entry) | set(old[i]) if entry.get(f) != old[i].get(f)}
                expected = ({'rationale', 'alternatives'} if key == (3, 6) and i == 5 else
                            {'rationale'} if key == (3, 11) and i == 3 else set())
                self.assertEqual(changed, expected, (key, i))
            rationale = entries[5 if key == (3, 6) else 3]['rationale']
            for phrase in ('4Q169', 'source', 'Source priority',
                           'whole-verse English optimality remain unresolved'):
                self.assertIn(phrase, rationale)
        self.assertEqual(self.candidates[(3, 6)]['lexical_decisions'][5]['alternatives'],
                         self.before[(3, 6)]['lexical_decisions'][5]['alternatives'] +
                         ['repulsive (alternative source reading)'])

    def test_complete_pinned_historical_proposed_export(self):
        # All historical inputs come from BASE, never from mutable current records.
        pins = self.contract['book_baseline_pins']
        self.assertEqual(len(pins), 47)
        self.assertEqual(len({p['path'] for p in pins}), 47)
        historical = {}
        for pin in pins:
            raw = subprocess.check_output(['git', 'show', f"{BASE}:{pin['path']}"], cwd=ROOT)
            self.assertEqual(sha(raw), pin['sha256'])
            key = (int(Path(pin['path']).parent.name), int(Path(pin['path']).stem))
            historical[key] = yaml.safe_load(raw)
        self.assertEqual(set(historical), {(ch, v) for ch, count in ((1, 14), (2, 14), (3, 19))
                                          for v in range(1, count + 1)})
        for key, pin in self.pins.items():
            self.assertEqual(historical[key], self.before[key])
            self.assertEqual(next(p['sha256'] for p in pins if p['path'] == pin['path']),
                             pin['before_sha256'])
        loader = exporter.load_translation_record
        def load(code, ch, v, candidate=False):
            if code != 'NAM':
                return loader(code, ch, v)
            return self.candidates[(ch, v)] if candidate and (ch, v) in self.candidates else historical[(ch, v)]
        with patch.object(exporter, 'load_translation_record', side_effect=load):
            before = exporter.export_book('NAM')
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v: load(c, ch, v, True)):
            after = exporter.export_book('NAM')
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 3)
        self.assertEqual(len(a), 47)
        changed = [list(k) for k in a if a[k] != b[k]]
        self.assertEqual(changed, [[3, 6], [3, 11]])
        self.assertEqual(sum(a[k] == b[k] for k in a), 45)
        self.assertEqual(sum(len(a[k]['footnotes']) for k in self.pins), 5)
        preflight = self.contract['preflight']
        self.assertEqual(digest(before), preflight['before_export_sha256'])
        self.assertEqual(digest(after), preflight['candidate_export_sha256'])
        self.assertEqual(preflight['changed_export_ids'], changed)
        self.assertEqual((preflight['chapters'], preflight['units'],
                          preflight['other_units_unchanged'], preflight['target_note_count']),
                         (3, 47, 45, 5))
        self.assertIs(preflight['canonical_written'], False)

    def test_exact_applied_bytes_and_complete_current_export(self):
        after = exporter.export_book('NAM')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda code, ch, v:
                          self.before[(ch, v)] if code == 'NAM' and (ch, v) in self.before
                          else loader(code, ch, v)):
            before = exporter.export_book('NAM')
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 3)
        self.assertEqual(len(a), 47)
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[3, 6], [3, 11]])
        self.assertEqual(sum(a[k] == b[k] for k in a), 45)
        for key, pin in self.pins.items():
            raw = (ROOT / pin['path']).read_bytes()
            self.assertEqual(sha(raw), pin['candidate_yaml_sha256'])
            self.assertEqual(yaml.safe_load(raw), self.candidates[key])
            self.assertEqual(a[key]['footnotes'], self.candidates[key]['translation']['footnotes'])
            self.assertEqual(audit_footnotes.audit_one(ROOT / pin['path'])['status'], 'ok')
        self.assertEqual(sum(len(a[k]['footnotes']) for k in self.pins), 5)

    def test_scoped_application_receipt_does_not_claim_source_certification(self):
        receipt = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(sha((ROOT / CONTRACT).read_bytes()), receipt['contract_sha256'])
        self.assertEqual(receipt['records'], self.contract['records'])
        self.assertEqual(receipt['review']['status'], 'pass')
        self.assertEqual(receipt['application']['status'], 'applied-local-verified')
        for field in ('source_changed', 'marker_free_main_english_changed', 'source_priority_settled',
                      'canon_changed', 'fresh_manuscript_transcription', 'deployed_reader_verified'):
            self.assertIs(receipt['decisions'][field], False)
        for field in ('blind_main_english_vote_claimed', 'source_priority_vote',
                      'repeat_until_agreement', 'canon_changed', 'imagegen_evidence'):
            self.assertIs(self.contract[field], False)


if __name__ == '__main__':
    unittest.main()
