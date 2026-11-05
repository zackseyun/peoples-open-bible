"""Guard the tower disclosure's conditions and the exact historical policy projection."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from tools import shepherd_of_hermas as hermas, repentance_reassessment as policy
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / r / 'extra_canonical/shepherd_of_hermas/011.yaml' for r in ['translation', 'translation_simplified']]


class VisionThreeTests(unittest.TestCase):
    def test_complete_conditions_and_corrected_source(self):
        docs, _ = review.load_pair(*PATHS)
        source = hermas.load_normalized_unit('V.3.iii').text
        self.assertIn('θελήσῃς ἐπερώτα', source)
        self.assertIn('ἄξιόν με ἡγήσω', source)
        self.assertNotIn('AP. FATH.', source)
        for doc in docs:
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'III.{n}' for n in range(1, 6)])
            self.assertIn('[that they may become more cheerful, and]' if doc is docs[0] else '[so that they may become more cheerful, and]', ps[0])
            self.assertIn('having heard [these things]', ps[0])
            self.assertIn('if', ps[1])
            self.assertIn('hear and repent[b]', ps[1])
            self.assertIn('they too will rejoice', ps[1])
            self.assertIn('you will not stop asking', ps[1])
            self.assertIn('shameless', ps[1])
            self.assertIn('ask about the tower', ps[2])
            self.assertIn('so that you may rejoice', ps[2])
            self.assertIn('Whatever can be revealed', ps[3])
            self.assertIn('do not be double-minded', ps[3])
            self.assertIn('was saved through water and will be saved', ps[4])
            self.assertIn('unseen power of the Master', ps[4])
            for note in doc['translation']['footnotes']:
                self.assertEqual(doc['translation']['text'].count('[' + note['marker'] + ']'), 1)

    def test_archive_extent_and_finite_policy_projection(self):
        a = json.loads((P / 'vision-three-tower-alignment-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        old = arc['standard_flat']['record']
        self.assertFalse(a['english_extent_changed'])
        self.assertEqual(len(old['translation']['text'].split('\n\n')), 5)
        self.assertIn('AP. FATH. 20', old['source']['text'])
        self.assertEqual(hermas.load_normalized_unit('V.3.iii').text,
                         arc['normalized_before'].replace('θελήσῃς ἐπερωτᾷν', 'θελήσῃς ἐπερώτα').replace('ἠξίών με ἠγήσω', 'ἄξιόν με ἡγήσω'))
        for path, row in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), row['file_sha256'])
        docs, _ = review.load_pair(*PATHS)
        self.assertEqual(policy.historical_view(PATHS[0], docs[0]), old)
        drifted = copy.deepcopy(docs[0])
        drifted['translation']['text'] = drifted['translation']['text'].replace('hear and repent[b]', 'hear[b]')
        with self.assertRaises(ValueError):
            policy.historical_view(PATHS[0], drifted)
        for n in [17, 18]:
            r = json.loads((P / f'model_reviews/legacy{n:03}-20261104-r2/receipt.json').read_text())
            for row in r['input_manifest']:
                self.assertEqual(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest(), row['file_sha256'])


if __name__ == '__main__':
    unittest.main()
