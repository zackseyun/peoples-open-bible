"""Preserve the complete flesh/healing passage and expose actual witness differences."""
import hashlib
import json
from pathlib import Path
import unittest
from tools import shepherd_of_hermas as h, draft_shepherd_of_hermas as d
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / root / 'extra_canonical/shepherd_of_hermas/053.yaml'
         for root in ['translation', 'translation_simplified']]


class FleshHealingTests(unittest.TestCase):
    def test_no_invented_extent_and_preserved_history(self):
        a = json.loads((P / 'five-flesh-healing-alignment-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertFalse(a['normalized_source_body_changed'])
        self.assertEqual(h.load_normalized_unit('S.5.vii').text, arc['normalized_before']['text'])
        self.assertIn('†τὴν σάρκα†', arc['normalized_before']['text'])
        self.assertEqual(len(arc['nested_unchanged']), 8)
        for path, item in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), item['file_sha256'])
        for item in json.loads((P / 'model_reviews/legacy052-20261104-r2/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest(), item['file_sha256'])
        coverage = json.loads((P / 'coverage.v1.json').read_text())
        row = next(x for x in coverage['units'] if x['unit_id'] == 'S.5.vii')
        self.assertEqual(row['translation_status'], 'requires_source_collation')

    def test_complete_conditional_warning_and_healing(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            self.assertEqual(doc['id'], 'HERM.S.5.vii')
            self.assertEqual(doc['source']['sequence'], 60)
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'VII.{i}' for i in range(1, 5)])
            self.assertIn('defile the flesh', ps[1])
            self.assertIn('you will not live', ps[1])
            self.assertIn('if from now on', ps[3])
            self.assertIn('clean', ps[0])
            self.assertIn('clean', ps[3])
            notes = {n['marker']: n['text'] for n in doc['translation']['footnotes']}
            self.assertIn('perhaps', notes['g'])
            self.assertIn('Almighty', notes['g'])
            self.assertNotIn('previous_rendering', [n['reason'] for n in doc['translation']['footnotes']])
            for n in doc['translation']['footnotes']:
                self.assertEqual(doc['translation']['text'].count('[' + n['marker'] + ']'), 1)
        std, simple = docs
        payload = dict(english_text=std['translation']['text'], translation_philosophy=std['translation']['philosophy'],
                       lexical_decisions=std['lexical_decisions'], footnotes=std['translation']['footnotes'],
                       theological_decisions=std['theological_decisions'])
        self.assertEqual(std['ai_draft']['output_hash'], d.sha256_hex(d.canonical_json(payload)))
        self.assertEqual(simple['ai_draft']['output_hash'], d.sha256_hex(simple['translation']['text']))


if __name__ == '__main__':
    unittest.main()
