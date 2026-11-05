"""Preserve the distinct seals, conditional warning and final hope."""
import hashlib
import json
from pathlib import Path
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / root / 'extra_canonical/shepherd_of_hermas/061.yaml'
         for root in ['translation', 'translation_simplified']]


class CrownsPlantingTests(unittest.TestCase):
    def test_complete_claims_and_conditions(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'II.{i}' for i in range(1, 10)])
            self.assertIn('some fruit', ps[0])
            self.assertTrue('no fruit' in ps[1] or 'not have fruit' in ps[1])
            self.assertIn('a seal[b]', ps[1])
            self.assertNotIn('seals', ps[1])
            self.assertIn('white as snow', ps[2])
            self.assertIn('[white] clothing and seals[c]', ps[3])
            self.assertEqual(ps[4].count('carefully'), 2)
            self.assertIn('if anyone does slip past you', ps[4])
            self.assertIn('upon the altar', ps[4])
            self.assertIn('After the angel had gone away', ps[5])
            self.assertIn('many of them will live', ps[6])
            self.assertIn('if it does not live', ps[6])
            self.assertIn('not be found negligent', ps[6])
            self.assertIn('Rank by rank' if doc is docs[0] else 'rank by rank', ps[7])
            self.assertIn('could not be seen', ps[7])
            self.assertIn('desires all who have taken branches', ps[8])
            self.assertIn('I too hope', ps[8])
            self.assertIn('greater part of them will live', ps[8])
            self.assertEqual(doc['source']['sequence'], 68)
            for note in doc['translation']['footnotes']:
                self.assertEqual(doc['translation']['text'].count('[' + note['marker'] + ']'), 1)
        notes = {n['marker']: n['text'] for n in docs[0]['translation']['footnotes']}
        self.assertIn('singular', notes['b'])
        self.assertIn('without supply/correction', notes['c'])
        self.assertIn('stops earlier', notes['e'])
        self.assertIn('Lord of this tree', notes['i'])

    def test_no_invented_extent_and_prior_records_retained(self):
        a = json.loads((P / 'eight-crowns-planting-alignment-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertFalse(a['normalized_source_body_changed'])
        self.assertEqual(hermas.load_normalized_unit('S.8.ii').text, arc['normalized_before']['text'])
        old = arc['standard_flat']['record']['translation']['text']
        for n in range(2, 10):
            self.assertIn(f'{n}. ', old)
        self.assertIn('hope', old)
        self.assertTrue(arc['nested_unchanged'])
        for path, item in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), item['file_sha256'])
        for item in json.loads((P / 'model_reviews/legacy060-20261104-r1/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest(), item['file_sha256'])


if __name__ == '__main__':
    unittest.main()
