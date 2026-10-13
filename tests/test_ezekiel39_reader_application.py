"""Qualified versional disclosure, not Hebrew source-priority adjudication."""
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
from tools import audit_footnotes
from tools import export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = 'sources/textual_restoration/comparisons/ezekiel39_29_reader_contract.2026-10-13.v1.json'
RECEIPT = 'sources/textual_restoration/applications/ezekiel39_29_reader.2026-10-13.v1.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(obj):
    return sha(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode())


def index(book):
    return {(c['chapter'], v['verse']): v
            for c in book['chapters'] for v in c['verses']}


class Ezekiel39ReaderApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / CONTRACT).read_text())
        cls.candidate = json.loads((ROOT / cls.contract['candidate']).read_text())
        cls.before_raw = subprocess.check_output([
            'git', 'show', cls.contract['baseline_commit'] + ':' + cls.contract['canonical_target']
        ], cwd=ROOT)
        cls.before = yaml.safe_load(cls.before_raw)

    def test_exact_candidate_schema_and_immutable_inputs(self):
        c, k = self.candidate, self.contract
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(c)
        self.assertEqual(sha(self.before_raw), k['baseline_yaml_sha256'])
        self.assertEqual(sha((ROOT / k['candidate']).read_bytes()), k['candidate_sha256'])
        self.assertEqual(sha(yaml.safe_dump(c, allow_unicode=True, sort_keys=False,
                                          width=1000).encode()), k['candidate_yaml_sha256'])
        for path, expected in k['input_pins'].items():
            raw = subprocess.check_output(['git', 'show', k['baseline_commit'] + ':' + path], cwd=ROOT)
            self.assertEqual(sha(raw), expected, path)
        self.assertEqual(sha(subprocess.check_output(k['book_manifest_command'], cwd=ROOT)),
                         k['book_git_manifest_sha256'])

    def test_genuine_generation_recovery_without_old_approval(self):
        c, b, recovery = self.candidate, self.before, self.contract['historical_metadata']
        raw = subprocess.check_output(['git', 'show', recovery['commit'] + ':' + recovery['path']], cwd=ROOT)
        self.assertEqual(sha(raw), recovery['record_sha256'])
        original = yaml.safe_load(raw)
        self.assertEqual(c['ai_draft'], original['ai_draft'])
        self.assertEqual(c['translation']['philosophy'], original['translation']['philosophy'])
        self.assertEqual(original['source'], b['source'])
        self.assertEqual(original['translation']['text'], b['translation']['text'])
        self.assertNotIn('lexical_decisions', c)
        self.assertNotIn('theological_decisions', c)
        self.assertNotIn('revision_pass', c)
        self.assertEqual(c['status'], 'draft')
        self.assertEqual(c['cross_check'], {'status': 'needs_review'})
        self.assertEqual(c['revisions'][:-1], b['revisions'])
        self.assertEqual(len(c['review_history']), 2)
        for archive in c['review_history']:
            value = b
            for part in archive['field'].split('.'):
                value = value[part]
            self.assertEqual(archive['value'], value)
            self.assertEqual(archive['archived_from_baseline_sha256'], sha(self.before_raw))
            self.assertIs(archive['historical_review_inputs_verified'], False)
            self.assertIs(archive['certifies_this_candidate'], False)

    def test_only_qualified_notes_change_reader_meaning(self):
        c, b = self.candidate, self.before
        self.assertEqual(c['source'], b['source'])
        self.assertEqual(re.sub(r'\[[ab]\]', '', c['translation']['text']), b['translation']['text'])
        self.assertIn('when[a]', c['translation']['text'])
        self.assertIn('my Spirit[b]', c['translation']['text'])
        self.assertEqual([n['marker'] for n in c['translation']['footnotes']], ['a', 'b'])
        self.assertEqual(audit_footnotes.audit_one(ROOT / self.contract['candidate'])['status'], 'ok')
        self.assertIs(c['source_audit']['p967_target_word_verified'], False)
        self.assertIs(c['source_audit']['generated_images_used_as_evidence'], False)
        self.assertEqual(c['source_audit']['historical_priority'], 'HOLD')
        self.assertIs(c['textual_comparison']['whole_verse_optimality_certified'], False)

    def test_complete_historical_book_export(self):
        # Read the immutable book in one Git operation; do not freeze future
        # legitimate edits to unrelated current Ezekiel records.
        raw = subprocess.check_output(['git', 'archive', self.contract['baseline_commit'],
                                       'translation/ot/ezekiel'], cwd=ROOT)
        records = {}
        with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
            for member in archive.getmembers():
                if member.isfile() and member.name.endswith('.yaml'):
                    p = Path(member.name)
                    records[(int(p.parent.name), int(p.stem))] = yaml.safe_load(archive.extractfile(member))
        loader = exporter.load_translation_record

        def load(code, ch, verse, proposed=False):
            if code != 'EZK':
                return loader(code, ch, verse)
            return self.candidate if proposed and (ch, verse) == (39, 29) else records[(ch, verse)]

        with patch.object(exporter, 'load_translation_record', side_effect=load):
            before = exporter.export_book('EZK')
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, h, v: load(c, h, v, True)):
            after = exporter.export_book('EZK')
        a, b = index(after), index(before)
        self.assertEqual((len(records), len(a), len(after['chapters'])), (1273, 1273, 48))
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[39, 29]])
        self.assertEqual(a[(39, 29)]['footnotes'], self.candidate['translation']['footnotes'])
        self.assertNotIn('source', a[(39, 29)])
        self.assertEqual(digest(before), self.contract['preflight']['before_export_sha256'])
        self.assertEqual(digest(after), self.contract['preflight']['candidate_export_sha256'])

    def test_applied_target_and_actual_reader_notes(self):
        raw = (ROOT / self.contract['canonical_target']).read_bytes()
        self.assertEqual(sha(raw), self.contract['candidate_yaml_sha256'])
        self.assertEqual(yaml.safe_load(raw), self.candidate)
        current = index(exporter.export_book('EZK'))[(39, 29)]
        self.assertEqual(current['text'], self.candidate['translation']['text'])
        self.assertEqual(current['footnotes'], self.candidate['translation']['footnotes'])
        self.assertEqual(audit_footnotes.audit_one(ROOT / self.contract['canonical_target'])['status'], 'ok')

    def test_application_receipt_does_not_broaden_approval(self):
        receipt = json.loads((ROOT / RECEIPT).read_text())
        self.assertEqual(receipt['contract_sha256'], sha((ROOT / CONTRACT).read_bytes()))
        self.assertEqual(receipt['review']['candidate_sha256'], self.contract['candidate_sha256'])
        self.assertEqual(receipt['review']['candidate_yaml_sha256'], self.contract['candidate_yaml_sha256'])
        self.assertEqual(receipt['review']['status'], 'pass')
        self.assertEqual(receipt['application']['status'], 'applied-local-verified')
        self.assertEqual(receipt['application']['after_export_sha256'], self.contract['preflight']['candidate_export_sha256'])
        for flag in ('source_changed', 'marker_free_main_english_changed', 'source_priority_settled',
                     'whole_verse_optimality_certified', 'deployed_reader_checked'):
            self.assertIs(receipt['decisions'][flag], False)


if __name__ == '__main__':
    unittest.main()
