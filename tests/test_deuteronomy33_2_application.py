"""Hash-bound rendering/disclosure application; not original-meaning proof."""
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
BASE = 'ebeca4504e0887e8985be4fb5fda70b8fc98414e'
TARGET = 'translation/ot/deuteronomy/033/002.yaml'
PREFIX = 'sources/textual_restoration/'
CANDIDATE = PREFIX + 'candidates/deuteronomy33_2_sinai.2026-10-10.v1.json'
RECEIPT = PREFIX + 'applications/deuteronomy33_2_sinai.2026-10-10.v1.json'


class Deuteronomy332ApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before_raw = subprocess.check_output(['git', 'show', f'{BASE}:{TARGET}'], cwd=ROOT)
        cls.before = yaml.safe_load(cls.before_raw)
        cls.current = yaml.safe_load((ROOT / TARGET).read_text())
        cls.candidate = json.loads((ROOT / CANDIDATE).read_text())
        cls.receipt = json.loads((ROOT / RECEIPT).read_text())

    def test_exact_candidate_source_generation_and_rendering_scope(self):
        self.assertEqual(self.current, self.candidate)
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(self.current)
        for field in ('source', 'ai_draft'):
            self.assertEqual(self.current[field], self.before[field])
        clean = re.sub(r'\[[a-b]\]', '', self.current['translation']['text'])
        old = re.sub(r'\[[a-b]\]', '', self.before['translation']['text'])
        self.assertEqual(clean, old.replace('myriads of holiness', 'holy myriads'))
        self.assertIn('אשדת', self.current['source']['text'])
        self.assertNotIn('אשדות', self.current['source']['text'])
        self.assertIn('came a fiery law', clean)
        self.assertNotIn('angels', clean)
        self.assertNotIn('fire flew', clean)

    def test_notes_anchor_their_actual_subjects_and_disclose_alternatives(self):
        text = self.current['translation']['text']
        self.assertIn('holy myriads[a]', text)
        self.assertIn('fiery law[b]', text)
        self.assertNotIn('them[a]', text)
        self.assertEqual([n['marker'] for n in self.current['translation']['footnotes']], ['a', 'b'])
        self.assertEqual(audit_footnotes.audit_one(ROOT / TARGET)['status'], 'ok')
        a, b = [n['text'] for n in self.current['translation']['footnotes']]
        for phrase in ('myriads of holiness', 'myriads of holy ones', 'heavenly or human'):
            self.assertIn(phrase, a)
        for phrase in ('Masoretic reading', 'alternative verbal analysis', 'fire flew',
                       'selected Greek text', 'angels with him', 'unresolved'):
            self.assertIn(phrase, b)

    def test_exact_archives_and_revisions_without_transferred_approval(self):
        fields = ['status', 'translation', 'lexical_decisions', 'theological_decisions',
                  'revision_pass', 'cross_check', 'ai_draft']
        history = self.current['review_history']
        self.assertEqual([h['field'] for h in history], fields)
        self.assertEqual({h['field']: h['value'] for h in history}, {f: self.before[f] for f in fields})
        for h in history:
            self.assertEqual(h['archived_from_baseline_sha256'], hashlib.sha256(self.before_raw).hexdigest())
            self.assertFalse(h['certifies_this_candidate'])
        self.assertEqual(self.current['revisions'][:-1], self.before['revisions'])
        self.assertEqual(len(self.before['revisions']), 2)
        self.assertEqual(self.current['revisions'][-1]['from'], self.before['translation']['text'])
        self.assertEqual(self.current['revisions'][-1]['to'], self.current['translation']['text'])
        self.assertEqual(self.current['status'], 'draft')
        self.assertEqual(self.current['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', self.current)

    def test_connected_rationale_and_comparison_boundaries(self):
        lex = {d['source_word']: d for d in self.current['lexical_decisions']}
        self.assertEqual(lex['מֵרִבְבֹת קֹדֶשׁ']['chosen'], 'from holy myriads')
        self.assertEqual(lex['אשדת']['chosen'], 'a fiery law')
        for d in self.before['lexical_decisions']:
            if d['source_word'] not in ('מֵרִבְבֹת קֹדֶשׁ', 'אשדת'):
                self.assertEqual(lex[d['source_word']], d)
        for key in ('source_changed', 'original_meaning_settled', 'publication_approved'):
            self.assertFalse(self.current['source_audit'][key])
        self.assertTrue(self.current['source_audit']['no_fresh_halot_consultation'])
        comparison = self.current['textual_comparison']
        self.assertEqual(comparison['final_colon_historical_priority'], 'held-unresolved')
        for key in ('fresh_image_reading', 'novel_reading_demonstrated', 'canon_changed', 'publication_approved'):
            self.assertFalse(comparison[key])
        a = json.loads((ROOT / comparison['assessment']).read_text())
        self.assertEqual(a['sources'][1]['preserved'], 'מרבבו')
        self.assertIn('entire right-hand/ashdat clause', a['sources'][1]['supplied'])
        self.assertIn('no discriminating support', a['root_assessment']['attestation_vs_priority'])
        self.assertEqual(a['independent_comparison']['status'], 'completed')
        self.assertFalse(a['independent_comparison']['application_approved'])

    def test_actual_book_export_changes_only_target_and_keeps_both_notes(self):
        after = exporter.export_book('DEU')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda code, ch, v:
                          self.before if (code, ch, v) == ('DEU', 33, 2) else loader(code, ch, v)):
            before = exporter.export_book('DEU')
        index = lambda book: {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 34)
        self.assertEqual(len(a), 959)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([k for k in a if a[k] != b[k]], [(33, 2)])
        self.assertEqual(a[(33, 2)]['text'], self.current['translation']['text'])
        self.assertEqual(a[(33, 2)]['footnotes'], self.current['translation']['footnotes'])

    def test_hash_bound_receipt_and_narrow_approval(self):
        r = self.receipt
        self.assertEqual(r['baseline_revision'], BASE)
        self.assertEqual(r['baseline_sha256'], hashlib.sha256(self.before_raw).hexdigest())
        for field, path in (('candidate_sha256', CANDIDATE), ('assessment_sha256', r['assessment'])):
            self.assertEqual(r[field], hashlib.sha256((ROOT / path).read_bytes()).hexdigest())
        self.assertEqual(r['candidate_yaml_sha256'], hashlib.sha256((ROOT / TARGET).read_bytes()).hexdigest())
        self.assertEqual(r['review']['status'], 'pass')
        self.assertEqual(r['review']['candidate_sha256'], r['candidate_sha256'])
        self.assertEqual(r['application']['status'], 'applied-verified')
        self.assertEqual(r['application']['changed_units'], [[33, 2]])
        self.assertFalse(r['application']['deployed_reader_verified'])
        for key in ('source_changed', 'final_colon_priority_settled', 'original_meaning_settled',
                    'novel_reading_demonstrated', 'canon_changed', 'publication_approved'):
            self.assertFalse(r['decision'][key])


if __name__ == '__main__':
    unittest.main()
