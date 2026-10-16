"""Person disclosure and provenance checks, not earliest-Hebrew certification."""
import json
from pathlib import Path
import re
import subprocess
import unittest

import yaml
from jsonschema import Draft202012Validator
from tools import audit_footnotes
from tools import export_mobile_bible as exporter
from tests.test_ezekiel35_14_joy_reader_application import (
    digest, export_records, historical_book, index, sha,
)

ROOT = Path(__file__).resolve().parents[1]
BASE = '7739693711e70a2d941c30f657eefadfe1a2d42f'
APPLIED = 'c519d9d96d1e535f5b820b94f8520c1be21c27f6'
TARGET = 'translation/ot/ezekiel/005/015.yaml'
STEM = 'ezekiel5_15_person_reader.2026-10-16.v1.json'
CONTRACT = ROOT / 'sources/textual_restoration/comparisons' / STEM
RECEIPT = ROOT / 'sources/textual_restoration/applications' / STEM


class Ezekiel5PersonPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ct = json.loads(CONTRACT.read_text())
        cls.c = json.loads((ROOT / cls.ct['candidate']).read_text())
        cls.raw = historical_book(BASE)
        cls.records = {p: yaml.safe_load(raw) for p, raw in cls.raw.items()}
        cls.b = cls.records[TARGET]

    def test_complete_record_and_archived_history(self):
        c, b, ct = self.c, self.b, self.ct
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(c)
        self.assertEqual(ct['baseline_commit'], BASE)
        self.assertEqual(sha(self.raw[TARGET]), ct['baseline_yaml_sha256'])
        self.assertEqual(sha((ROOT / ct['candidate']).read_bytes()), ct['candidate_sha256'])
        self.assertEqual(sha(yaml.safe_dump(c, allow_unicode=True, sort_keys=False, width=1000).encode()), ct['candidate_yaml_sha256'])
        for field in ('id', 'reference', 'source', 'ai_draft', 'theological_decisions'):
            self.assertEqual(c[field], b[field], field)
        self.assertEqual(c['translation']['philosophy'], b['translation']['philosophy'])
        plain = lambda s: re.sub(r'\[[a-z]\]', '', s)
        self.assertEqual(plain(c['translation']['text']), plain(b['translation']['text']))
        self.assertEqual(c['status'], 'draft')
        self.assertEqual(c['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', c)
        self.assertEqual(c['revisions'][:-1], b.get('revisions', []))
        self.assertEqual(c['revisions'][-1]['from'], b['translation']['text'])
        self.assertEqual(c['revisions'][-1]['to'], c['translation']['text'])
        self.assertEqual(c['revisions'][-1]['baseline_sha256'], ct['baseline_yaml_sha256'])
        self.assertEqual(c['review_history'][:-6], b.get('review_history', []))
        archives = c['review_history'][-6:]
        self.assertEqual({a['field'] for a in archives}, {'status', 'revision_pass', 'cross_check', 'translation.text', 'translation.footnotes', 'lexical_decisions'})
        for a in archives:
            old = b
            for part in a['field'].split('.'):
                old = old[part]
            self.assertEqual(a['value'], old)
            self.assertEqual(a['archived_from_baseline_sha256'], ct['baseline_yaml_sha256'])
            self.assertIs(a['historical_review_inputs_verified'], False)
            self.assertIs(a['certifies_this_candidate'], False)
        self.assertEqual({k for k in set(b) | set(c) if b.get(k) != c.get(k)}, {'translation', 'lexical_decisions', 'status', 'revision_pass', 'cross_check', 'revisions', 'review_history', 'source_audit', 'textual_comparison'})

    def test_disclosure_anchors_and_lexical_scope(self):
        c, b = self.c, self.b
        self.assertEqual(c['translation']['footnotes'][:3], b['translation']['footnotes'])
        for anchor in ('you shall become[d]', 'warning[a]', 'horror[b]', 'wrathful rebukes[c]'):
            self.assertIn(anchor, c['translation']['text'])
        self.assertEqual(re.findall(r'\[([a-z])\]', c['translation']['text']), ['d', 'a', 'b', 'c'])
        self.assertEqual(c['translation']['footnotes'][3], {
            'marker': 'd',
            'text': "Hebrew 'she/it shall become'; the translation continues the address to Jerusalem. Greek has 'you shall be.' The Qumran fragment 11Q4 reads והית, whose grammatical interpretation is disputed. The Hebrew source is retained; English 'you' does not establish a second-person Hebrew original.",
            'reason': 'textual_variant',
        })
        changed = [a['source_word'] for a, z in zip(c['lexical_decisions'], b['lexical_decisions']) if a != z]
        self.assertEqual(changed, ['וְהָיְתָה', 'אֲנִי יְהוָה'])
        self.assertEqual(len(c['lexical_decisions']), len(b['lexical_decisions']))
        self.assertIn('third feminine singular', c['lexical_decisions'][0]['rationale'])
        self.assertIn('smooths grammatical person', c['lexical_decisions'][0]['rationale'])
        self.assertEqual(c['lexical_decisions'][10]['chosen'], 'I am Yahweh')
        for flag in ('declared_source_retained', 'source_consonants_pointing_segmentation_retained', 'main_english_retained'):
            self.assertIs(c['source_audit'][flag], True)
        for flag in ('fresh_manuscript_transcription', 'generated_images_used_as_evidence', 'fresh_halot_consultation'):
            self.assertIs(c['source_audit'][flag], False)
        self.assertIn('HOLD', c['source_audit']['historical_priority'])
        self.assertIs(c['textual_comparison']['whole_verse_optimality_certified'], False)

    def test_frozen_inputs_and_full_book_export(self):
        ct = self.ct
        for p, pin in ct['input_pins'].items():
            self.assertEqual(sha(subprocess.check_output(['git', 'show', f'{BASE}:{p}'], cwd=ROOT)), pin)
        self.assertEqual(subprocess.check_output(['git', 'rev-parse', f'{BASE}:translation/ot/ezekiel'], cwd=ROOT).decode().strip(), ct['book_baseline_tree_oid'])
        self.assertEqual(digest({p: sha(raw) for p, raw in self.raw.items()}), ct['book_baseline_manifest_sha256'])
        before = export_records(self.records)
        after = export_records({**self.records, TARGET: self.c})
        a, b = index(after), index(before)
        self.assertEqual((len(after['chapters']), len(a), len(self.raw)), (48, 1273, 1273))
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[5, 15]])
        self.assertEqual(ct['preflight']['changed_export_ids'], [[5, 15]])
        self.assertEqual(ct['preflight']['other_units_unchanged'], 1272)
        self.assertEqual(digest(before), ct['preflight']['before_export_sha256'])
        self.assertEqual(digest(after), ct['preflight']['candidate_export_sha256'])
        self.assertIs(ct['preflight']['canonical_written'], False)
        self.assertIs(ct['preflight']['deployed_reader_verified'], False)


class Ezekiel5PersonAppliedTests(unittest.TestCase):
    def test_immutable_application_and_non_targets(self):
        ct = json.loads(CONTRACT.read_text())
        receipt = json.loads(RECEIPT.read_text())
        applied = receipt['application']['commit']
        self.assertEqual(applied, APPLIED)
        self.assertEqual(sha(subprocess.check_output(['git', 'show', f'{APPLIED}:docs/EZEKIEL_5_15_PERSON_COMPARISON_2026-10-16.md'], cwd=ROOT)), ct['report_sha256_at_freeze'])
        before, after = historical_book(BASE), historical_book(applied)
        self.assertEqual(before.keys(), after.keys())
        for p, raw in after.items():
            if p == TARGET:
                self.assertEqual(sha(raw), ct['candidate_yaml_sha256'])
            else:
                self.assertEqual(raw, before[p], p)
        book = export_records({p: yaml.safe_load(raw) for p, raw in after.items()})
        self.assertEqual(digest(book), ct['preflight']['candidate_export_sha256'])

    def test_current_target_export_and_review(self):
        ct = json.loads(CONTRACT.read_text())
        c = json.loads((ROOT / ct['candidate']).read_text())
        r = json.loads(RECEIPT.read_text())
        self.assertEqual(sha(CONTRACT.read_bytes()), r['review']['reviewed_contract_sha256'])
        self.assertEqual(ct['candidate_sha256'], r['review']['reviewed_candidate_sha256'])
        self.assertEqual(r['review']['status'], 'pass')
        self.assertIs(r['review']['repeat_until_agreement'], False)
        self.assertEqual(sha((ROOT / TARGET).read_bytes()), ct['candidate_yaml_sha256'])
        self.assertEqual(yaml.safe_load((ROOT / TARGET).read_text()), c)
        self.assertEqual(audit_footnotes.audit_one(ROOT / TARGET)['status'], 'ok')
        current = index(exporter.export_book('EZK'))
        self.assertEqual(len(current), 1273)
        self.assertEqual(current[(5, 15)]['text'], c['translation']['text'])
        self.assertEqual(current[(5, 15)]['footnotes'], c['translation']['footnotes'])
        self.assertEqual(r['application']['after_export_sha256'], ct['preflight']['candidate_export_sha256'])
        self.assertIs(r['application']['deployed_reader_verified'], False)


if __name__ == '__main__':
    unittest.main()
