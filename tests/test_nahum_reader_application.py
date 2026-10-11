"""Scoped Nahum reader-note application; not source-priority certification."""
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
BASE = 'f38b774ed4fbec0e9a6b740481b5dd1106cad538'
CONTRACT = 'sources/textual_restoration/comparisons/nahum1_5_2_9_3_18_reader_contract.2026-10-10.v1.json'
RECEIPT = 'sources/textual_restoration/applications/nahum1_5_2_9_3_18_reader.2026-10-10.v1.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def plain(text):
    return re.sub(r'\[[a-z]\]', '', text)


def index(book):
    return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}


def digest(book):
    return sha(json.dumps(book, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


class NahumReaderApplicationTests(unittest.TestCase):
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
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        for key, c in self.candidates.items():
            b, pin = self.before[key], self.pins[key]
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
            allowed = {'translation', 'status', 'revision_pass', 'cross_check',
                       'review_history', 'revisions'}
            if key == (2, 9):
                allowed.add('lexical_decisions')
            self.assertLessEqual({k for k in set(b) | set(c) if b.get(k) != c.get(k)}, allowed)

    def test_notes_have_semantic_anchors_and_qualified_alternative(self):
        anchors = {(1, 5): ['rises up[a]', 'face[b]'],
                   (2, 9): ['earliest days[b]', 'Stop! Stop!”[a]'],
                   (3, 18): ['shepherds[b]', 'slumber[a]', 'lie down[c]', 'scattered[d]']}
        for key, c in self.candidates.items():
            b = self.before[key]
            for fragment in anchors[key]:
                self.assertIn(fragment, c['translation']['text'])
            for note in c['translation']['footnotes']:
                self.assertEqual(c['translation']['text'].count('[' + note['marker'] + ']'), 1)
            if key != (2, 9):
                self.assertEqual(c['translation']['footnotes'], b['translation']['footnotes'])
                self.assertEqual(c['lexical_decisions'], b['lexical_decisions'])
                self.assertEqual(c.get('theological_decisions'), b.get('theological_decisions'))
            else:
                self.assertEqual(c['translation']['footnotes'][0], b['translation']['footnotes'][0])
                note = c['translation']['footnotes'][1]
                self.assertEqual(note['reason'], 'textual_variant')
                for phrase in ('provisionally', 'selected Greek', 'her waters', 'unpointed',
                               'context is supplied', 'read temporally', 'remains uncertain'):
                    self.assertIn(phrase.lower(), note['text'].lower())
                for i, entry in enumerate(c['lexical_decisions']):
                    changed = {k for k in set(entry) | set(b['lexical_decisions'][i])
                               if entry.get(k) != b['lexical_decisions'][i].get(k)}
                    self.assertEqual(changed, {'rationale', 'alternatives'} if i == 2
                                     else {'rationale'} if i == 3 else set())

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
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[1, 5], [2, 9], [3, 18]])
        for key, pin in self.pins.items():
            raw = (ROOT / pin['path']).read_bytes()
            self.assertEqual(sha(raw), pin['candidate_yaml_sha256'])
            self.assertEqual(yaml.safe_load(raw), self.candidates[key])
            self.assertEqual(a[key]['footnotes'], self.candidates[key]['translation']['footnotes'])
            self.assertEqual(audit_footnotes.audit_one(ROOT / pin['path'])['status'], 'ok')
        self.assertEqual(sum(len(a[k]['footnotes']) for k in self.pins), 8)

    def test_historical_export_and_scoped_receipt(self):
        historical = {}
        for path in sorted((ROOT / 'translation/ot/nahum').glob('*/*.yaml')):
            relative = path.relative_to(ROOT).as_posix()
            historical[(int(path.parent.name), int(path.stem))] = yaml.safe_load(
                subprocess.check_output(['git', 'show', f'{BASE}:{relative}'], cwd=ROOT))
        loader = exporter.load_translation_record
        def load(code, ch, v, candidate=False):
            if code != 'NAM':
                return loader(code, ch, v)
            return self.candidates[(ch, v)] if candidate and (ch, v) in self.candidates else historical[(ch, v)]
        with patch.object(exporter, 'load_translation_record', side_effect=load):
            before = exporter.export_book('NAM')
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v: load(c, ch, v, True)):
            after = exporter.export_book('NAM')
        self.assertEqual(digest(before), self.contract['preflight']['before_export_sha256'])
        self.assertEqual(digest(after), self.contract['preflight']['candidate_export_sha256'])
        receipt = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(sha((ROOT / CONTRACT).read_bytes()), receipt['contract_sha256'])
        self.assertEqual(receipt['records'], self.contract['records'])
        self.assertEqual(receipt['review']['status'], 'pass')
        self.assertEqual(receipt['application']['status'], 'applied-local-verified')
        for field in ('source_changed', 'marker_free_main_english_changed', 'source_priority_settled',
                      'canon_changed', 'fresh_manuscript_transcription', 'deployed_reader_verified'):
            self.assertIs(receipt['decisions'][field], False)
        self.assertIs(self.contract['repeat_until_agreement'], False)


if __name__ == '__main__':
    unittest.main()
