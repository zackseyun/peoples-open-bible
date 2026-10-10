"""Exact source-stable translation application; not proof of original spelling."""
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
BASE = '71b6568dd6862883aa71c0dab87c3ff037a451e0'
TARGET = 'translation/ot/genesis/006/003.yaml'
PREFIX = 'sources/textual_restoration/'
CANDIDATE = PREFIX + 'candidates/genesis6_3_spirit.2026-10-10.v1.json'
RECEIPT = PREFIX + 'applications/genesis6_3_spirit.2026-10-10.v1.json'


class Genesis63ApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before_raw = subprocess.check_output(['git', 'show', f'{BASE}:{TARGET}'], cwd=ROOT)
        cls.before = yaml.safe_load(cls.before_raw)
        cls.current = yaml.safe_load((ROOT / TARGET).read_text())
        cls.candidate = json.loads((ROOT / CANDIDATE).read_text())
        cls.receipt = json.loads((ROOT / RECEIPT).read_text())

    def test_full_candidate_schema_source_generation_and_main_english(self):
        self.assertEqual(self.current, self.candidate)
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(self.current)
        self.assertEqual(self.current['source'], self.before['source'])
        self.assertEqual(self.current['ai_draft'], self.before['ai_draft'])
        self.assertEqual(self.current['translation']['philosophy'], self.before['translation']['philosophy'])
        clean = re.sub(r'\[[a-e]\]', '', self.current['translation']['text'])
        self.assertEqual(clean, 'Then Yahweh said, “My Spirit will not remain in man forever, for he is flesh; his days will be one hundred and twenty years.”')
        self.assertNotIn('therefore', clean)
        self.assertNotIn('more years', clean)
        self.assertIn('יָד֨וֹן', self.current['source']['text'])
        self.assertNotIn('ידור', self.current['source']['text'])

    def test_reader_notes_are_anchored_and_uncertainty_preserved(self):
        text = self.current['translation']['text']
        for phrase in ('Spirit[a]', 'remain[b]', 'man[c]', 'flesh[d]', 'years[e]'):
            self.assertIn(phrase, text)
        self.assertEqual([n['marker'] for n in self.current['translation']['footnotes']], list('abcde'))
        self.assertEqual(audit_footnotes.audit_one(ROOT / TARGET)['status'], 'ok')
        notes = {n['marker']: n['text'] for n in self.current['translation']['footnotes']}
        self.assertIn('life-giving breath', notes['a'])
        self.assertIn('English interpretive choice', notes['a'])
        for phrase in ('contend with man', 'uncertain', 'reworked', 'does not establish the original'):
            self.assertIn(phrase, notes['b'])
        self.assertIn('humankind', notes['c'])
        self.assertIn('also', notes['d'])
        for phrase in ('lifespan', 'time until the flood', 'does not say'):
            self.assertIn(phrase, notes['e'])

    def test_history_is_exact_without_transferred_certification(self):
        fields = ['status', 'translation', 'lexical_decisions', 'theological_decisions', 'revision_pass', 'cross_check', 'ai_draft']
        history = self.current['review_history']
        self.assertEqual([h['field'] for h in history], fields)
        self.assertEqual({h['field']: h['value'] for h in history}, {f: self.before[f] for f in fields})
        for h in history:
            self.assertEqual(h['archived_from_baseline_sha256'], hashlib.sha256(self.before_raw).hexdigest())
            self.assertFalse(h['certifies_this_candidate'])
        self.assertEqual(self.current['revisions'][:-1], self.before['revisions'])
        self.assertEqual(self.current['revisions'][-1]['from'], self.before['translation']['text'])
        self.assertEqual(self.current['revisions'][-1]['to'], self.current['translation']['text'])
        self.assertEqual(self.current['status'], 'draft')
        self.assertEqual(self.current['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', self.current)

    def test_connected_rationales_and_outcome_limits(self):
        lex = {d['source_word']: d for d in self.current['lexical_decisions']}
        self.assertEqual(lex['יָדוֹן']['chosen'], 'will not remain')
        self.assertEqual(lex['בָאָדָם']['chosen'], 'in man')
        self.assertEqual(lex['הוּא בָשָׂר']['chosen'], 'he is flesh')
        self.assertEqual(lex['וְהָיוּ יָמָיו']['chosen'], 'his days will be')
        for d in self.before['lexical_decisions']:
            if d['source_word'] not in ('יָדוֹן', 'רוּחִי', 'בָאָדָם', 'בְּשַׁגַּם', 'הוּא בָשָׂר', 'וְהָיוּ יָמָיו'):
                self.assertEqual(lex[d['source_word']], d)
        audit = self.current['source_audit']
        for flag in ('source_changed', 'original_spelling_settled', 'publication_approved'):
            self.assertFalse(audit[flag])
        self.assertTrue(audit['no_fresh_halot_consultation'])
        comparison = self.current['textual_comparison']
        self.assertEqual(comparison['historical_priority'], 'unresolved')
        for flag in ('fresh_image_reading', 'novel_reading_demonstrated', 'canon_changed', 'publication_approved'):
            self.assertFalse(comparison[flag])

    def test_actual_current_book_export_changes_only_target(self):
        after = exporter.export_book('GEN')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda code, ch, v:
                          self.before if (code, ch, v) == ('GEN', 6, 3) else loader(code, ch, v)):
            before = exporter.export_book('GEN')
        index = lambda book: {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 50)
        self.assertEqual(len(a), 1533)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([k for k in a if a[k] != b[k]], [(6, 3)])
        self.assertEqual(a[(6, 3)]['text'], self.current['translation']['text'])
        self.assertEqual(a[(6, 3)]['footnotes'], self.current['translation']['footnotes'])

    def test_receipt_exact_bytes_and_narrow_review_scope(self):
        r = self.receipt
        self.assertEqual(r['baseline_revision'], BASE)
        self.assertEqual(r['baseline_sha256'], hashlib.sha256(self.before_raw).hexdigest())
        for field, path in (('candidate_sha256', CANDIDATE), ('assessment_sha256', r['assessment'])):
            self.assertEqual(r[field], hashlib.sha256((ROOT / path).read_bytes()).hexdigest())
        self.assertEqual(r['candidate_yaml_sha256'], hashlib.sha256((ROOT / TARGET).read_bytes()).hexdigest())
        self.assertEqual(r['review']['status'], 'pass')
        self.assertEqual(r['review']['candidate_sha256'], r['candidate_sha256'])
        self.assertEqual(r['application']['status'], 'applied-verified')
        self.assertEqual(r['application']['changed_units'], [[6, 3]])
        self.assertFalse(r['application']['deployed_reader_verified'])
        self.assertTrue(r['decision']['marker_free_main_english_changed'])
        for flag in ('source_changed', 'original_spelling_settled', 'spirit_breath_semantics_settled',
                     'days_scope_settled', 'novel_reading_demonstrated', 'canon_changed', 'publication_approved'):
            self.assertFalse(r['decision'][flag])


if __name__ == '__main__':
    unittest.main()
