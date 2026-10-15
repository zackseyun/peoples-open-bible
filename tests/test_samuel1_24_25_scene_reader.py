"""Scoped Samuel reader application; no historical source-priority certification."""
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
BASE = 'e0bb485013cfbd6af50633b7b565877b03b3c897'
CONTRACT = 'sources/textual_restoration/comparisons/samuel1_24_25_scene_reader_contract.2026-10-15.v1.json'
REVIEWED_CONTRACT_SHA256 = '6f20385f76a4d95ea7c9e3a4d0d6e2357b4cefa2b58450ac2236dc7511e8cdee'
RECEIPT = 'sources/textual_restoration/applications/samuel1_24_25_scene_reader.2026-10-15.v1.json'
TARGETS = {(1, 24), (1, 25)}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def plain(text):
    return re.sub(r'\[[a-z]\]', '', text)


def digest(obj):
    return sha(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


def index(book):
    return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}


class SamuelSceneReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / CONTRACT).read_text())
        cls.receipt = json.loads((ROOT / RECEIPT).read_text())
        cls.candidates = {}
        for row in cls.contract['records']:
            key = (int(Path(row['path']).parent.name), int(Path(row['path']).stem))
            cls.candidates[key] = json.loads((ROOT / row['candidate']).read_text())
        pins = cls.contract['book_baseline_pins']
        raw = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=ROOT,
            input=('\n'.join(f"{BASE}:{p['path']}" for p in pins) + '\n').encode())
        cls.historical = {}
        pos = 0
        for pin in pins:
            end = raw.index(b'\n', pos)
            header = raw[pos:end].split()
            assert header[1] == b'blob'
            size = int(header[2])
            data = raw[end + 1:end + 1 + size]
            pos = end + size + 2
            assert sha(data) == pin['sha256'], pin['path']
            p = Path(pin['path'])
            cls.historical[int(p.parent.name), int(p.stem)] = yaml.safe_load(data)
        assert pos == len(raw)

    def test_candidate_pins_schema_and_exact_archives(self):
        self.assertEqual(self.contract['baseline_commit'], BASE)
        schema = json.loads((ROOT / 'schema/verse.schema.json').read_text())
        for row in self.contract['records']:
            key = (1, int(Path(row['path']).stem))
            c, b = self.candidates[key], self.historical[key]
            Draft202012Validator(schema).validate(c)
            self.assertEqual(sha((ROOT / row['candidate']).read_bytes()), row['candidate_sha256'])
            self.assertEqual(sha(yaml.safe_dump(c, allow_unicode=True, sort_keys=False,
                width=1000).encode()), row['candidate_yaml_sha256'])
            for field in ('id', 'reference', 'source', 'ai_draft', 'theological_decisions'):
                self.assertEqual(c[field], b[field], field)
            self.assertEqual(c['translation']['philosophy'], b['translation']['philosophy'])
            self.assertEqual(plain(c['translation']['text']), plain(b['translation']['text']))
            old_history = b.get('review_history', [])
            self.assertEqual(c['review_history'][:len(old_history)], old_history)
            added = c['review_history'][len(old_history):]
            expected = {'status', 'revision_pass', 'cross_check', 'translation.text',
                        'translation.footnotes', 'lexical_decisions'}
            self.assertEqual(len(added), 6)
            self.assertEqual({h['field'] for h in added}, expected)
            for entry in added:
                old = b
                for part in entry['field'].split('.'):
                    old = old[part]
                self.assertEqual(entry['value'], old)
                self.assertEqual(entry['archived_from_baseline_sha256'], row['before_sha256'])
                self.assertIs(entry['historical_review_inputs_verified'], False)
                self.assertIs(entry['certifies_this_candidate'], False)
            self.assertEqual(c['status'], 'draft')
            self.assertEqual(c['cross_check'], {'status': 'needs_review'})
            self.assertNotIn('revision_pass', c)
            self.assertEqual(c['revisions'][:-1], b.get('revisions', []))
            revision = c['revisions'][-1]
            self.assertEqual(revision['from'], b['translation']['text'])
            self.assertEqual(revision['to'], c['translation']['text'])
            self.assertEqual(revision['baseline_sha256'], row['before_sha256'])
            allowed = {'translation', 'lexical_decisions', 'status', 'cross_check',
                       'revision_pass', 'revisions', 'review_history', 'source_audit', 'textual_comparison'}
            self.assertLessEqual({k for k in set(b) | set(c) if b.get(k) != c.get(k)}, allowed)

    def test_only_three_rationales_change_and_old_notes_survive(self):
        for key, indices in [((1, 24), {10}), ((1, 25), {0, 2})]:
            c, b = self.candidates[key], self.historical[key]
            self.assertEqual(len(c['lexical_decisions']), len(b['lexical_decisions']))
            for i, entry in enumerate(c['lexical_decisions']):
                old = b['lexical_decisions'][i]
                changed = {k for k in set(old) | set(entry) if old.get(k) != entry.get(k)}
                self.assertEqual(changed, {'rationale'} if i in indices else set())
            self.assertEqual(c['translation']['footnotes'][:-1], b['translation']['footnotes'])
            for i in indices:
                self.assertIn('HALOT', c['lexical_decisions'][i]['rationale'])
        self.assertIn('not established', self.candidates[1, 24]['lexical_decisions'][10]['rationale'])
        self.assertIn('participants are not named', self.candidates[1, 25]['lexical_decisions'][0]['rationale'])
        self.assertIn('no named subject', self.candidates[1, 25]['lexical_decisions'][2]['rationale'])

    def test_reader_anchors_disclosure_and_claim_limits(self):
        c24, c25 = self.candidates[1, 24], self.candidates[1, 25]
        self.assertTrue(c24['translation']['text'].endswith('Now the boy was young[b].'))
        self.assertEqual(c25['translation']['text'],
            'Then they slaughtered[a] the bull and brought the boy[b] to Eli[c].')
        note24 = c24['translation']['footnotes'][-1]
        note25 = c25['translation']['footnotes'][-1]
        for note in (note24, note25):
            self.assertEqual(note['reason'], 'textual_variant')
            self.assertIn('selected Septuagint', note['text'])
        for phrase in ('boy was a boy', 'boy was with them', 'much of its wording must be supplied', 'remains unresolved'):
            self.assertIn(phrase, note24['text'])
        for phrase in ('without naming the participants', "father's recurring sacrifice", 'names Hannah', 'not just alternative translations'):
            self.assertIn(phrase, note25['text'])
        for row in self.contract['records']:
            c = self.candidates[1, int(Path(row['path']).stem)]
            self.assertEqual(audit_footnotes.audit_one(ROOT / row['candidate'])['status'], 'ok')
            self.assertEqual(re.findall(r'\[([a-z])\]', c['translation']['text']),
                             [n['marker'] for n in c['translation']['footnotes']])
            self.assertIs(c['source_audit']['source_consonants_pointing_segmentation_retained'], True)
            for flag in ('fresh_manuscript_transcription', 'generated_images_used_as_evidence', 'fresh_halot_consultation'):
                self.assertIs(c['source_audit'][flag], False)
            self.assertIs(c['textual_comparison']['whole_verse_optimality_certified'], False)

    def test_context_and_historical_inputs(self):
        for row in self.contract['context']:
            v = int(row['id'].split('.')[-1])
            self.assertEqual(row['source'], self.historical[1, v]['source'])
            self.assertEqual(row['marker_free_english'], plain(self.historical[1, v]['translation']['text']))
        self.assertEqual([row['id'] for row in self.contract['context']], [f'1SA.1.{v}' for v in range(22, 29)])
        for path, expected in self.contract['historical_input_pins'].items():
            self.assertEqual(sha(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)), expected)
        if self.contract.get('case_document_sha256'):
            self.assertEqual(sha((ROOT / self.contract['case_document']).read_bytes()), self.contract['case_document_sha256'])
        else:
            self.assertEqual(self.contract['case_document_pin_status'], 'pending-final-document-before-review')

    def test_complete_historical_proposed_export(self):
        self.assertEqual(len(self.contract['book_baseline_pins']), 811)
        self.assertEqual(len(self.historical), 811)
        loader = exporter.load_translation_record
        def load(code, ch, v, candidate=False):
            if code != '1SA':
                return loader(code, ch, v)
            return self.candidates.get((ch, v), self.historical[ch, v]) if candidate else self.historical[ch, v]
        with patch.object(exporter, 'load_translation_record', side_effect=load):
            before = exporter.export_book('1SA')
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v: load(c, ch, v, True)):
            after = exporter.export_book('1SA')
        a, b = index(after), index(before)
        self.assertEqual((len(after['chapters']), len(a)), (31, 811))
        self.assertEqual({k for k in a if a[k] != b[k]}, TARGETS)
        self.assertEqual(sum(a[k] == b[k] for k in a), 809)
        for key in TARGETS:
            self.assertEqual(a[key]['footnotes'], self.candidates[key]['translation']['footnotes'])
        self.assertEqual(sum(len(a[k]['footnotes']) for k in TARGETS), 5)
        pre = self.contract['preflight']
        self.assertEqual(digest(before), pre['before_export_sha256'])
        self.assertEqual(digest(after), pre['candidate_export_sha256'])
        self.assertIs(pre['canonical_written'], False)

    def test_review_and_application_receipt_preserve_preflight_and_limits(self):
        r = self.receipt
        self.assertEqual(r['contract'], CONTRACT)
        self.assertEqual(sha((ROOT / CONTRACT).read_bytes()), REVIEWED_CONTRACT_SHA256)
        self.assertEqual(r['contract_sha256'], sha((ROOT / CONTRACT).read_bytes()))
        self.assertEqual(r['records'], self.contract['records'])
        self.assertEqual(r['preflight'], self.contract['preflight'])
        self.assertIs(r['review']['repeat_until_agreement'], False)
        self.assertEqual(r['review']['status'], 'pass')
        self.assertEqual(r['review']['reviewed_contract_sha256'], REVIEWED_CONTRACT_SHA256)
        self.assertEqual(r['review']['reviewed_candidate_sha256'],
                         [row['candidate_sha256'] for row in self.contract['records']])
        self.assertTrue(r['review']['actual_assessment'])
        self.assertEqual(r['application']['status'], 'applied-local-verified')
        self.assertIs(r['application']['canonical_written'], True)
        self.assertEqual(r['application']['after_export_sha256'],
                         r['preflight']['candidate_export_sha256'])
        self.assertEqual(r['application']['changed_export_ids'], [[1, 24], [1, 25]])
        self.assertEqual(r['application']['other_units_unchanged'], 809)
        self.assertEqual(r['application']['target_notes'], 5)
        self.assertIs(r['preflight']['canonical_written'], False)
        for flag, value in r['decisions'].items():
            self.assertIs(value, flag == 'reader_notes_changed', flag)

    def test_live_application_and_complete_reader_export(self):
        for row in self.contract['records']:
            key = (1, int(Path(row['path']).stem))
            raw = (ROOT / row['path']).read_bytes()
            self.assertEqual(sha(raw), row['candidate_yaml_sha256'])
            self.assertEqual(yaml.safe_load(raw), self.candidates[key])
            self.assertEqual(audit_footnotes.audit_one(ROOT / row['path'])['status'], 'ok')
        after = exporter.export_book('1SA')
        loader = exporter.load_translation_record
        def before_load(code, ch, v):
            if code == '1SA' and (ch, v) in TARGETS:
                return self.historical[ch, v]
            return loader(code, ch, v)
        with patch.object(exporter, 'load_translation_record', side_effect=before_load):
            before = exporter.export_book('1SA')
        a, b = index(after), index(before)
        self.assertEqual((len(after['chapters']), len(a)), (31, 811))
        self.assertEqual({k for k in a if a[k] != b[k]}, TARGETS)
        self.assertEqual(sum(a[k] == b[k] for k in a), 809)
        for key in TARGETS:
            self.assertEqual(a[key]['footnotes'], self.candidates[key]['translation']['footnotes'])
            self.assertEqual(plain(a[key]['text']),
                             plain(self.historical[key]['translation']['text']))
        self.assertEqual(sum(len(a[k]['footnotes']) for k in TARGETS), 5)
        # Other current records may evolve legitimately. The preceding historical
        # test, not a permanent whole-book freeze, owns the original export pin.


if __name__ == '__main__':
    unittest.main()
