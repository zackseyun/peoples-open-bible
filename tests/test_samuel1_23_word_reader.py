"""Reader disclosure and provenance checks, not original-text certification."""
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
BASE = '34a9faf23d9cac3b2ddd4d6102acc50a2a84344f'
CONTRACT = 'sources/textual_restoration/comparisons/samuel1_23_word_reader_contract.2026-10-16.v1.json'
RECEIPT = 'sources/textual_restoration/applications/samuel1_23_word_reader.2026-10-16.v1.json'
TARGET = (1, 23)
REVIEWED_CONTRACT_SHA256 = 'fa7368543aab69fd0cf43d3d47d6023e41ffa4df2432024d8880a106ae7aaafb'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(obj):
    return sha(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


def plain(text):
    return re.sub(r'\[[a-z]\]', '', text)


def index(book):
    return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}


class SamuelWordReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / CONTRACT).read_text())
        cls.candidate = json.loads((ROOT / cls.contract['candidate']).read_text())
        paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE,
            '--', 'translation/ot/1_samuel'], cwd=ROOT, text=True).splitlines()
        cls.paths = [p for p in paths if p.endswith('.yaml')]
        raw = subprocess.check_output(['git', 'cat-file', '--batch'], cwd=ROOT,
            input=('\n'.join(f'{BASE}:{p}' for p in cls.paths) + '\n').encode())
        cls.historical, cls.raws, pos = {}, {}, 0
        for name in cls.paths:
            end = raw.index(b'\n', pos)
            header = raw[pos:end].split()
            assert header[1] == b'blob'
            size = int(header[2])
            data = raw[end + 1:end + 1 + size]
            pos = end + size + 2
            p = Path(name)
            key = (int(p.parent.name), int(p.stem))
            cls.historical[key] = yaml.safe_load(data)
            cls.raws[key] = data
        assert pos == len(raw)
        cls.before = cls.historical[TARGET]

    def test_frozen_candidate_and_archival_boundaries(self):
        c, b, ct = self.candidate, self.before, self.contract
        self.assertEqual(ct['baseline_commit'], BASE)
        self.assertEqual(sha((ROOT / CONTRACT).read_bytes()), REVIEWED_CONTRACT_SHA256)
        self.assertEqual(sha(self.raws[TARGET]), ct['before_sha256'])
        self.assertEqual(sha((ROOT / ct['candidate']).read_bytes()), ct['candidate_sha256'])
        self.assertEqual(sha(yaml.safe_dump(c, allow_unicode=True, sort_keys=False,
            width=1000).encode()), ct['candidate_yaml_sha256'])
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(c)
        for field in ('id', 'reference', 'source', 'ai_draft'):
            self.assertEqual(c[field], b[field])
        self.assertEqual(c['translation']['philosophy'], b['translation']['philosophy'])
        self.assertEqual(plain(c['translation']['text']), plain(b['translation']['text']))
        old = b.get('review_history', [])
        self.assertEqual(c['review_history'][:len(old)], old)
        added = c['review_history'][len(old):]
        self.assertEqual({x['field'] for x in added}, {'status', 'revision_pass', 'cross_check',
            'translation.text', 'translation.footnotes', 'lexical_decisions', 'theological_decisions'})
        self.assertEqual(len(added), 7)
        for entry in added:
            value = b
            for part in entry['field'].split('.'):
                value = value[part]
            self.assertEqual(entry['value'], value)
            self.assertEqual(entry['archived_from_baseline_sha256'], ct['before_sha256'])
            self.assertIs(entry['certifies_this_candidate'], False)
            self.assertIs(entry['historical_review_inputs_verified'], False)
        self.assertEqual(c['status'], 'draft')
        self.assertEqual(c['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', c)
        self.assertEqual(c['revisions'][:-1], b.get('revisions', []))
        self.assertEqual(c['revisions'][-1]['from'], b['translation']['text'])
        self.assertEqual(c['revisions'][-1]['to'], c['translation']['text'])
        allowed = {'translation', 'lexical_decisions', 'theological_decisions', 'status',
            'cross_check', 'revision_pass', 'review_history', 'revisions', 'source_audit', 'textual_comparison'}
        self.assertLessEqual({k for k in set(b) | set(c) if b.get(k) != c.get(k)}, allowed)
        self.assertEqual(len(c['lexical_decisions']), len(b['lexical_decisions']))
        for i, item in enumerate(c['lexical_decisions']):
            prior = b['lexical_decisions'][i]
            self.assertEqual({k for k in set(item) | set(prior) if item.get(k) != prior.get(k)},
                {'rationale'} if i == 7 else set())

    def test_note_anchor_and_evidence_limits(self):
        c = self.candidate
        self.assertIn('his word[a].', c['translation']['text'])
        self.assertNotIn('her[a]', c['translation']['text'])
        self.assertEqual(re.findall(r'\[([a-z])\]', c['translation']['text']), ['a'])
        self.assertEqual(len(c['translation']['footnotes']), 1)
        note = c['translation']['footnotes'][0]
        self.assertEqual((note['marker'], note['reason']), ('a', 'textual_variant'))
        for phrase in ('4QSam-a (4Q51)', 'what comes out of your mouth',
                       'not simply another translation', 'earlier remains unresolved'):
            self.assertIn(phrase, note['text'])
        self.assertEqual(audit_footnotes.audit_one(ROOT / self.contract['candidate'])['status'], 'ok')
        self.assertIs(c['source_audit']['source_consonants_pointing_segmentation_retained'], True)
        self.assertIs(c['source_audit']['generated_images_used_as_evidence'], False)
        self.assertIs(c['textual_comparison']['whole_verse_optimality_certified'], False)
        raw = subprocess.check_output(['git', 'show', f"{BASE}:{self.contract['source_review']}"], cwd=ROOT)
        self.assertEqual(sha(raw), self.contract['source_review_at_baseline_sha256'])

    def test_complete_frozen_export(self):
        self.assertEqual(len(self.historical), 811)
        loader = exporter.load_translation_record
        def load(code, ch, v, candidate=False):
            if code != '1SA':
                return loader(code, ch, v)
            return self.candidate if candidate and (ch, v) == TARGET else self.historical[ch, v]
        with patch.object(exporter, 'load_translation_record', side_effect=load):
            before = exporter.export_book('1SA')
        with patch.object(exporter, 'load_translation_record', side_effect=lambda *a: load(*a, candidate=True)):
            after = exporter.export_book('1SA')
        a, b = index(after), index(before)
        self.assertEqual((len(after['chapters']), len(a)), (31, 811))
        self.assertEqual({k for k in a if a[k] != b[k]}, {TARGET})
        self.assertEqual(a[TARGET]['footnotes'], self.candidate['translation']['footnotes'])
        self.assertEqual(digest(before), self.contract['preflight']['before_export_sha256'])
        self.assertEqual(digest(after), self.contract['preflight']['candidate_export_sha256'])
        self.assertIs(self.contract['preflight']['canonical_written'], False)

    def test_live_record_and_export(self):
        raw = (ROOT / self.contract['record']).read_bytes()
        self.assertEqual(sha(raw), self.contract['candidate_yaml_sha256'])
        self.assertEqual(yaml.safe_load(raw), self.candidate)
        self.assertEqual(audit_footnotes.audit_one(ROOT / self.contract['record'])['status'], 'ok')
        after = exporter.export_book('1SA')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda code,ch,v:
            self.before if (code,ch,v) == ('1SA',1,23) else loader(code,ch,v)):
            before = exporter.export_book('1SA')
        a, b = index(after), index(before)
        self.assertEqual({k for k in a if a[k] != b[k]}, {TARGET})
        self.assertEqual(a[TARGET]['footnotes'], self.candidate['translation']['footnotes'])
        r = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(r['contract_sha256'], sha((ROOT / CONTRACT).read_bytes()))
        self.assertEqual(r['candidate_sha256'], self.contract['candidate_sha256'])
        self.assertEqual(r['review']['status'], 'pass')
        self.assertEqual(r['review']['reviewed_contract_sha256'], REVIEWED_CONTRACT_SHA256)
        self.assertEqual(r['review']['reviewed_candidate_sha256'], self.contract['candidate_sha256'])
        self.assertEqual(r['preflight'], self.contract['preflight'])
        self.assertEqual(r['application']['status'], 'applied-local-verified')
        self.assertIs(r['application']['canonical_written'], True)
        self.assertIs(r['review']['repeat_until_agreement'], False)
        self.assertEqual(r['application']['after_export_sha256'], self.contract['preflight']['candidate_export_sha256'])
        self.assertEqual(r['application']['other_units_unchanged'], 810)


if __name__ == '__main__':
    unittest.main()
