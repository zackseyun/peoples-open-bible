"""Scoped Obadiah note application; no source-priority or corpus-quality proof."""
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
BASE = 'abbdeca3a38846bcc7bb1741476d480961fffa48'
CONTRACT = 'sources/textual_restoration/comparisons/obadiah1_7_21_reader_contract.2026-10-10.v1.json'
RECEIPT = 'sources/textual_restoration/applications/obadiah1_7_21_reader.2026-10-10.v1.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def plain(text):
    return re.sub(r'\[[a-z]\]', '', text)


def index(book):
    return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}


def digest(book):
    return sha(json.dumps(book, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


class ObadiahReaderApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / CONTRACT).read_text())
        cls.pins = {int(Path(p['path']).stem): p for p in cls.contract['records']}
        cls.before = {}
        cls.candidates = {}
        for n, pin in cls.pins.items():
            raw = subprocess.check_output(['git', 'show', f"{BASE}:{pin['path']}"], cwd=ROOT)
            assert sha(raw) == pin['before_sha256']
            cls.before[n] = yaml.safe_load(raw)
            cls.candidates[n] = json.loads((ROOT / pin['candidate']).read_text())

    def test_frozen_complete_records_preserve_source_main_and_exact_archives(self):
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        for n, c in self.candidates.items():
            b, pin = self.before[n], self.pins[n]
            validator.validate(c)
            self.assertEqual(sha((ROOT / pin['candidate']).read_bytes()), pin['candidate_sha256'])
            self.assertEqual(sha(yaml.safe_dump(c, allow_unicode=True, sort_keys=False,
                                              width=1000).encode()), pin['candidate_yaml_sha256'])
            for field in ('id', 'reference', 'source', 'ai_draft'):
                self.assertEqual(c[field], b[field])
            self.assertEqual(plain(c['translation']['text']), plain(b['translation']['text']))
            self.assertEqual(c['translation']['philosophy'], b['translation']['philosophy'])
            history = {h['field']: h for h in c['review_history']}
            expected = {'status', 'revision_pass', 'cross_check', 'translation.text',
                        'translation.footnotes', 'lexical_decisions'}
            if 'theological_decisions' in b:
                expected.add('theological_decisions')
            self.assertEqual(set(history), expected)
            for field, h in history.items():
                obj = b
                for key in field.split('.'):
                    obj = obj[key]
                self.assertEqual(h['value'], obj)
                self.assertEqual(h['archived_from_baseline_sha256'], pin['before_sha256'])
                self.assertIs(h['certifies_this_candidate'], False)
                self.assertIs(h['historical_review_inputs_verified'], False)
            self.assertEqual(c['status'], 'draft')
            self.assertEqual(c['cross_check'], {'status': 'needs_review'})
            self.assertNotIn('revision_pass', c)
            self.assertEqual(c['revisions'][:-1], b.get('revisions', []))
            changed = {k for k in set(b) | set(c) if b.get(k) != c.get(k)}
            allowed = {'translation', 'status', 'revision_pass', 'cross_check',
                       'review_history', 'revisions'}
            if n == 21:
                allowed |= {'lexical_decisions', 'theological_decisions'}
            self.assertLessEqual(changed, allowed)

    def test_notes_are_qualified_and_anchored_to_exact_referents(self):
        seven, last = self.candidates[7], self.candidates[21]
        self.assertEqual(seven['translation']['footnotes'], self.before[7]['translation']['footnotes'])
        self.assertEqual(seven['lexical_decisions'], self.before[7]['lexical_decisions'])
        for fragment in ('border[a]', 'trap[b]', 'him[c]'):
            self.assertIn(fragment, seven['translation']['text'])
        for fragment in ('Deliverers[a]', 'Esau[b]', 'Yahweh[c]'):
            self.assertIn(fragment, last['translation']['text'])
        for n, c in self.candidates.items():
            for note in c['translation']['footnotes']:
                self.assertEqual(c['translation']['text'].count('[' + note['marker'] + ']'), 1)
        self.assertEqual(last['translation']['footnotes'][1:], self.before[21]['translation']['footnotes'][1:])
        note = last['translation']['footnotes'][0]
        self.assertEqual(note['reason'], 'textual_variant')
        for phrase in ('provisionally', 'alternative Hebrew vocalization', 'selected Greek',
                       'from Mount Zion', 'unpointed', 'does not settle', 'remains uncertain'):
            self.assertIn(phrase.lower(), note['text'].lower())
        for key, position in [('lexical_decisions', 1), ('theological_decisions', 0)]:
            for i, item in enumerate(last[key]):
                if i != position:
                    self.assertEqual(item, self.before[21][key][i])
                else:
                    changed = {k for k in item if item[k] != self.before[21][key][i].get(k)}
                    self.assertEqual(changed, {'rationale', 'alternatives'} if key == 'lexical_decisions'
                                     else {'rationale', 'alternative_readings'})

    def test_applied_bytes_and_complete_current_reader_export(self):
        after = exporter.export_book('OBA')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v:
                          self.before[v] if c == 'OBA' and ch == 1 and v in self.before
                          else loader(c, ch, v)):
            before = exporter.export_book('OBA')
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 1)
        self.assertEqual(len(a), 21)
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[1, 7], [1, 21]])
        for n, pin in self.pins.items():
            raw = (ROOT / pin['path']).read_bytes()
            self.assertEqual(sha(raw), pin['candidate_yaml_sha256'])
            self.assertEqual(yaml.safe_load(raw), self.candidates[n])
            self.assertEqual(a[(1, n)]['footnotes'], self.candidates[n]['translation']['footnotes'])
            self.assertEqual(audit_footnotes.audit_one(ROOT / pin['path'])['status'], 'ok')

    def test_historical_export_and_receipt_do_not_certify_source_priority(self):
        historical = {}
        for n in range(1, 22):
            p = f'translation/ot/obadiah/001/{n:03}.yaml'
            historical[n] = yaml.safe_load(subprocess.check_output(['git', 'show', f'{BASE}:{p}'], cwd=ROOT))
        loader = exporter.load_translation_record
        def load(code, ch, v, candidate=False):
            if code != 'OBA':
                return loader(code, ch, v)
            return self.candidates[v] if candidate and v in self.candidates else historical[v]
        with patch.object(exporter, 'load_translation_record', side_effect=load):
            before = exporter.export_book('OBA')
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v: load(c, ch, v, True)):
            after = exporter.export_book('OBA')
        self.assertEqual(digest(before), self.contract['preflight']['before_export_sha256'])
        self.assertEqual(digest(after), self.contract['preflight']['candidate_export_sha256'])
        receipt = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(receipt['records'], self.contract['records'])
        self.assertEqual(receipt['review']['status'], 'pass')
        self.assertEqual(receipt['application']['status'], 'applied-local-verified')
        for k in ('source_changed', 'marker_free_main_english_changed', 'source_priority_settled',
                  'canon_changed', 'fresh_manuscript_transcription', 'deployed_reader_verified'):
            self.assertIs(receipt['decisions'][k], False)
        self.assertIs(self.contract['repeat_until_agreement'], False)


if __name__ == '__main__':
    unittest.main()
