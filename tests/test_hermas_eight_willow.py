"""Keep the complete willow vision and its thirteen distinct rod groups."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
import yaml
from tools import repentance_reassessment as policy
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / root / 'extra_canonical/shepherd_of_hermas/060.yaml'
         for root in ['translation', 'translation_simplified']]


class WillowTests(unittest.TestCase):
    def test_opening_and_each_rod_group(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'I.{i}' for i in range(1, 19)])
            self.assertIn('plains and mountains', ps[0])
            self.assertIn('[large]', ps[0])
            self.assertIn('by the name of the Lord', ps[0])
            self.assertIn('within myself', ps[3])
            self.assertIn('same order', ps[4])
            self.assertEqual(len(ps[5:]), 13)
            for i in range(5, 17):
                self.assertIn('stand apart' if i in [5, 6] else 'stood apart', ps[i])
            self.assertIn('not been eaten by a moth', ps[6])
            self.assertIn('half-dry', ps[7])
            self.assertNotIn('splits', ps[7])
            self.assertIn('splits', ps[8])
            self.assertIn('green and with splits', ps[9])
            self.assertIn('half dry and half green', ps[10])
            self.assertIn('third part dry', ps[11])
            self.assertIn('third part green', ps[12])
            self.assertIn('very tip', ps[13])
            self.assertIn('splits', ps[13])
            self.assertIn('only a very little was green', ps[14])
            self.assertIn('greater part of the crowd', ps[15])
            self.assertIn('with shoots', ps[16])
            self.assertNotIn('fruit', ps[16])
            self.assertIn('something like fruit', ps[17])
            self.assertIn('shepherd', ps[17])
            self.assertNotIn('repent', doc['translation']['text'])
            self.assertEqual(doc['source']['sequence'], 67)
            for note in doc['translation']['footnotes']:
                self.assertEqual(doc['translation']['text'].count('[' + note['marker'] + ']'), 1)
        notes = {n['marker']: n['text'] for n in docs[0]['translation']['footnotes']}
        self.assertIn('not independent Vulgata', notes['e'])
        self.assertIn('S1correction', notes['i'])
        self.assertIn('mostly', notes['f'])

    def test_history_boundary_and_preserved_source(self):
        a = json.loads((P / 'eight-willow-restoration-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['normalized_source_body_changed'])
        self.assertEqual(hermas.load_normalized_unit('S.8.i').text, arc['normalized_before']['text'])
        old = arc['standard_flat']['record']['translation']['text']
        self.assertIn('the sins of those who are repenting', old)
        self.assertNotIn('something like fruit', old)
        self.assertNotIn('plains and mountains', old)
        self.assertTrue(arc['nested_unchanged'])
        for path, item in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), item['file_sha256'])
        for path, digest in arc['neighbor61_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)
        # The transferred teaching remains in the complete preceding chapter.
        prior = yaml.safe_load((ROOT / 'translation/extra_canonical/shepherd_of_hermas/059.yaml').read_text())
        self.assertIn('forgiven immediately', prior['translation']['text'])
        for item in json.loads((P / 'model_reviews/legacy059-20261104-r2/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest(), item['file_sha256'])

    def test_exact_policy_rejects_collapsed_group_or_changed_note(self):
        doc = yaml.safe_load(PATHS[0].read_text())
        self.assertEqual(policy.approved_errors(PATHS[0], doc), [])
        self.assertIn('repenting', policy.historical_view(PATHS[0], doc)['translation']['text'])
        bad = copy.deepcopy(doc)
        bad['translation']['text'] = bad['translation']['text'].replace('two parts dry and the third part green', 'two parts green and the third part dry')
        self.assertNotEqual(bad['translation']['text'], doc['translation']['text'])
        self.assertTrue(policy.approved_errors(PATHS[0], bad))
        bad = copy.deepcopy(doc)
        bad['translation']['footnotes'][0]['text'] = 'changed'
        self.assertTrue(policy.approved_errors(PATHS[0], bad))


if __name__ == '__main__':
    unittest.main()
