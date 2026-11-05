"""Keep all adultery/repentance conditions and the precise prior policy history."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from tools import repentance_reassessment as policy, shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / r / 'extra_canonical/shepherd_of_hermas/029.yaml' for r in ['translation', 'translation_simplified']]


class FourReceptionTests(unittest.TestCase):
    def test_all_eleven_paragraphs_conditions_and_variant_disclosure(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            self.assertEqual(doc['lexical_decisions'][10]['chosen'], 'servant')
            self.assertIn('servant of God', doc['theological_decisions'][2]['chosen_reading'])
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'I.{n}' for n in range(1, 12)])
            self.assertIn('your own wife', ps[0])
            self.assertIn('servant of God', ps[1])
            self.assertIn('death upon himself', ps[1])
            self.assertIn('[and]', ps[3])
            self.assertIn('does not repent[b]', ps[4])
            self.assertIn('if', ps[4].lower())
            self.assertIn('adultery', ps[4])
            self.assertIn('he', ps[5])
            self.assertIn('also commits adultery' if doc is docs[0] else 'too commits adultery', ps[5])
            self.assertIn('[the wife] repents', ps[6])
            self.assertIn('must be received', ps[7])
            self.assertIn('not repeatedly[5]', ps[7])
            self.assertIn('repentance is one[6]', ps[7])
            self.assertIn('both woman and man', ps[7])
            self.assertIn('does not repent', ps[8])
            self.assertIn('there can be repentance', ps[9])
            self.assertIn('able to give healing[9]', ps[10])
            self.assertIn('authority over all', ps[10])
            for n in doc['translation']['footnotes']:
                self.assertEqual(doc['translation']['text'].count('[' + n['marker'] + ']'), 1)
            notes = {n['marker']: n['text'] for n in doc['translation']['footnotes']}
            self.assertIn('Vulgata39instead', notes['c'])
            self.assertIn('alternative', notes['8'])
            self.assertIn('first-hand', notes['9'])
            self.assertIn('ca and d', notes['9'])

    def test_no_invented_extent_and_finite_history(self):
        a = json.loads((P / 'four-reception-alignment-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertFalse(a['normalized_source_body_changed'])
        self.assertEqual(hermas.load_normalized_unit('M.4.i').text, arc['normalized_before'])
        self.assertEqual(arc['standard_flat']['record']['source']['text'], arc['normalized_before'])
        for path, row in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), row['file_sha256'])
        docs, _ = review.load_pair(*PATHS)
        self.assertEqual(policy.historical_view(PATHS[0], docs[0]), arc['prior_followup']['before_record'])
        broken = copy.deepcopy(docs[0])
        broken['translation']['text'] = broken['translation']['text'].replace('must be received', 'may be received')
        with self.assertRaises(ValueError):
            policy.historical_view(PATHS[0], broken)
        r = json.loads((P / 'model_reviews/legacy011-20261104-r1/receipt.json').read_text())
        for row in r['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest(), row['file_sha256'])


if __name__ == '__main__':
    unittest.main()
