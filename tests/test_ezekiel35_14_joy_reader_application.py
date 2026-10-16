"""Scoped temporal/subject English application; not source-priority certification."""
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
BASE = '4522efbfab0443723d9e8609718a913de54064a8'
APPLIED = '45b8803d2071d28ef01cd824a053816643823b4a'
STEM = 'ezekiel35_14_joy_reader.2026-10-16.v1.json'
CONTRACT = ROOT / 'sources/textual_restoration/comparisons' / STEM
TARGET = 'translation/ot/ezekiel/035/014.yaml'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(obj):
    return sha(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())


def historical_book(commit=BASE):
    raw = subprocess.check_output(['git', 'archive', commit, 'translation/ot/ezekiel'], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        return {m.name: archive.extractfile(m).read() for m in archive.getmembers()
                if m.isfile() and m.name.endswith('.yaml')}


def export_records(records):
    lookup = {(int(Path(p).parent.name), int(Path(p).stem)): record for p, record in records.items()}
    with patch.object(exporter, 'load_translation_record', side_effect=lambda code, ch, v: lookup.get((ch, v))):
        return exporter.export_book('EZK')


def index(book):
    return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}


class EzekielJoyApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text())
        cls.candidate = json.loads((ROOT / cls.contract['candidate']).read_text())
        cls.raw = historical_book()
        cls.records = {p: yaml.safe_load(raw) for p, raw in cls.raw.items()}
        cls.before = cls.records[TARGET]

    def test_exact_candidate_and_preserved_provenance(self):
        c, b, contract = self.candidate, self.before, self.contract
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(c)
        self.assertEqual(contract['baseline_commit'], BASE)
        self.assertEqual(sha(self.raw[TARGET]), contract['baseline_yaml_sha256'])
        self.assertEqual(sha((ROOT / contract['candidate']).read_bytes()), contract['candidate_sha256'])
        self.assertEqual(sha(yaml.safe_dump(c, allow_unicode=True, sort_keys=False, width=1000).encode()), contract['candidate_yaml_sha256'])
        for key in ('id', 'reference', 'source', 'ai_draft', 'theological_decisions'):
            self.assertEqual(c[key], b[key], key)
        self.assertEqual(c['translation']['philosophy'], b['translation']['philosophy'])
        self.assertEqual(c['revisions'][:-1], b['revisions'])
        self.assertEqual(c['revisions'][-1]['from'], b['translation']['text'])
        self.assertEqual(c['revisions'][-1]['to'], c['translation']['text'])
        self.assertEqual(c['revisions'][-1]['baseline_sha256'], contract['baseline_yaml_sha256'])
        self.assertEqual(c['status'], 'draft')
        self.assertEqual(c['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', c)
        archives = c['review_history']
        self.assertEqual(len(archives), 6)
        self.assertEqual({a['field'] for a in archives}, {'status', 'revision_pass', 'cross_check', 'translation.text', 'translation.footnotes', 'lexical_decisions'})
        for a in archives:
            old = b
            for part in a['field'].split('.'):
                old = old[part]
            self.assertEqual(a['value'], old)
            self.assertEqual(a['archived_from_baseline_sha256'], contract['baseline_yaml_sha256'])
            self.assertIs(a['historical_review_inputs_verified'], False)
            self.assertIs(a['certifies_this_candidate'], False)
        changed = {k for k in set(b) | set(c) if b.get(k) != c.get(k)}
        self.assertEqual(changed, {'translation', 'lexical_decisions', 'status', 'revision_pass', 'revisions', 'cross_check', 'review_history', 'source_audit', 'textual_comparison'})

    def test_clause_notes_lexical_scope_and_limits(self):
        c, b = self.candidate, self.before
        self.assertEqual(c['translation']['text'], 'Thus says the Lord GOD: When the whole earth[b] rejoices[a], I will make you desolate.')
        notes = c['translation']['footnotes']
        self.assertEqual(notes[1], b['translation']['footnotes'][1])
        self.assertEqual(notes[0]['reason'], 'alternative_reading')
        for phrase in ('Just as you rejoiced', 'implied subject', 'verse 15', 'occasion of its joy is not stated'):
            self.assertIn(phrase, notes[0]['text'])
        self.assertEqual(re.findall(r'\[([a-z])\]', c['translation']['text']), ['b', 'a'])
        self.assertEqual(audit_footnotes.audit_one(ROOT / self.contract['candidate'])['status'], 'ok')
        self.assertEqual(len(c['lexical_decisions']), len(b['lexical_decisions']))
        for i, entry in enumerate(c['lexical_decisions']):
            changed = {k for k in set(entry) | set(b['lexical_decisions'][i]) if entry.get(k) != b['lexical_decisions'][i].get(k)}
            self.assertEqual(changed, {'chosen', 'alternatives', 'rationale'} if i == 3 else {'rationale'} if i in (4, 5) else set())
        self.assertIs(c['source_audit']['source_consonants_pointing_segmentation_retained'], True)
        self.assertIs(c['source_audit']['generated_images_used_as_evidence'], False)
        self.assertIn('HOLD', c['source_audit']['historical_priority'])
        self.assertIs(c['textual_comparison']['whole_verse_optimality_certified'], False)

    def test_frozen_masked_comparison_and_inputs(self):
        for p, h in self.contract['input_pins'].items():
            raw = (ROOT / p).read_bytes() if p in self.contract['new_input_paths'] else subprocess.check_output(['git', 'show', f'{BASE}:{p}'], cwd=ROOT)
            self.assertEqual(sha(raw), h, p)
        cmp = self.candidate['textual_comparison']
        packet = json.loads((ROOT / cmp['english_contract']).read_text())
        result = json.loads((ROOT / cmp['english_result']).read_text())
        self.assertEqual(sha((ROOT / cmp['english_contract']).read_bytes()), result['contract_sha256'])
        self.assertEqual(packet['source_text'], self.before['source']['text'])
        for ref, text in packet['context_source'].items():
            ch, v = map(int, ref.split(':'))
            self.assertEqual(text, self.records[f'translation/ot/ezekiel/{ch:03}/{v:03}.yaml']['source']['text'])
        self.assertEqual(re.sub(r'\[[ab]\]', '', self.before['translation']['text']).split(': ', 1)[1], packet['candidates']['P'])
        self.assertEqual(re.sub(r'\[[ab]\]', '', self.candidate['translation']['text']).split(': ', 1)[1], packet['candidates']['T'])
        self.assertEqual(result['working_preference'], 'T')
        self.assertIs(result['repeat_until_agreement'], False)
        self.assertIn('An infinitive can refer to past action', result['actual_assessment'])
        self.assertIn('context supports those decisions collectively, but does not compel them', result['actual_assessment'])

    def test_complete_historical_export_preflight(self):
        contract = self.contract
        tree = subprocess.check_output(['git', 'rev-parse', f'{BASE}:translation/ot/ezekiel'], cwd=ROOT).decode().strip()
        self.assertEqual(tree, contract['book_baseline_tree_oid'])
        self.assertEqual(digest({p: sha(r) for p, r in self.raw.items()}), contract['book_baseline_manifest_sha256'])
        before = export_records(self.records)
        after = export_records({**self.records, TARGET: self.candidate})
        a, b = index(after), index(before)
        self.assertEqual((len(after['chapters']), len(a), len(self.raw)), (48, 1273, 1273))
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[35, 14]])
        self.assertEqual(a[(35, 14)]['footnotes'], self.candidate['translation']['footnotes'])
        self.assertEqual(digest(before), contract['preflight']['before_export_sha256'])
        self.assertEqual(digest(after), contract['preflight']['candidate_export_sha256'])
        self.assertIs(contract['preflight']['canonical_written'], False)

    def test_historical_application_complete_export_and_non_targets(self):
        receipt = json.loads((ROOT / 'sources/textual_restoration/applications' / STEM).read_text())
        self.assertEqual(sha(CONTRACT.read_bytes()), receipt['review']['reviewed_contract_sha256'])
        self.assertEqual(receipt['review']['status'], 'pass')
        # Prove the actual transaction at its immutable application commit;
        # later applications may legitimately change other current verses.
        applied = historical_book(APPLIED)
        self.assertEqual(applied.keys(), self.raw.keys())
        self.assertEqual(sha(applied[TARGET]), self.contract['candidate_yaml_sha256'])
        self.assertEqual(yaml.safe_load(applied[TARGET]), self.candidate)
        for p, historical in self.raw.items():
            if p != TARGET:
                self.assertEqual(applied[p], historical, p)
        after = export_records({p: yaml.safe_load(raw) for p, raw in applied.items()})
        self.assertEqual(digest(after), self.contract['preflight']['candidate_export_sha256'])
        self.assertEqual(digest(after), receipt['application']['after_export_sha256'])
        self.assertEqual(len(index(after)), 1273)
        self.assertEqual(receipt['application']['other_units_unchanged'], 1272)

    def test_current_target_and_actual_reader_notes(self):
        raw = (ROOT / TARGET).read_bytes()
        self.assertEqual(sha(raw), self.contract['candidate_yaml_sha256'])
        self.assertEqual(yaml.safe_load(raw), self.candidate)
        current = exporter.export_book('EZK')
        self.assertEqual(len(index(current)), 1273)
        target = index(current)[(35, 14)]
        self.assertEqual(target['text'], self.candidate['translation']['text'])
        self.assertEqual(target['footnotes'], self.candidate['translation']['footnotes'])


if __name__ == '__main__':
    unittest.main()
