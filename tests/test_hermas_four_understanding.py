"""Keep repentance's ethical sequence, source uncertainty and final condition."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from tools import repentance_reassessment as policy, shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / r / 'extra_canonical/shepherd_of_hermas/030.yaml' for r in ['translation', 'translation_simplified']]


class FourUnderstandingTests(unittest.TestCase):
    def test_complete_argument_and_disclosed_conjecture(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'II.{n}' for n in range(1, 5)])
            self.assertIn('hardened', ps[0])
            self.assertIn('all who repent', ps[1])
            self.assertIn('[the man] who has sinned[3]', ps[1])
            self.assertIn('no longer', ps[1])
            self.assertIn('lavishly[4]', ps[1])
            self.assertIn('humbles his own soul', ps[1])
            self.assertIn('because he sinned', ps[1])
            self.assertIn('I do not know', ps[2])
            self.assertIn('if you keep my commandments and walk in them', ps[3])
            self.assertIn('will live to God[6]', ps[3])
            notes = {n['marker']: n['text'] for n in doc['translation']['footnotes']}
            self.assertIn('Harmer', notes['5'])
            self.assertIn('severely damaged', notes['c'])
            self.assertIn('dotted', notes['b'])
            for n in doc['translation']['footnotes']:
                self.assertEqual(doc['translation']['text'].count('[' + n['marker'] + ']'), 1)

    def test_full_history_and_no_false_collation_completion(self):
        a = json.loads((P / 'four-understanding-alignment-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertFalse(a['normalized_source_body_changed'])
        self.assertTrue(a['broader_source_collation_flag_retained'])
        self.assertEqual(hermas.load_normalized_unit('M.4.ii').text, arc['normalized_before'])
        for path, row in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), row['file_sha256'])
        docs, _ = review.load_pair(*PATHS)
        self.assertEqual(policy.historical_view(PATHS[0], docs[0]), arc['prior_followup']['before_record'])
        broken = copy.deepcopy(docs[0])
        broken['translation']['text'] = broken['translation']['text'].replace('if you keep', 'whether you keep')
        with self.assertRaises(ValueError):
            policy.historical_view(PATHS[0], broken)
        for row in json.loads((P / 'model_reviews/legacy029-20261104-r2/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest(), row['file_sha256'])


if __name__ == '__main__':
    unittest.main()
