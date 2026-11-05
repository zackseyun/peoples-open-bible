"""The opening must retain both the accusation and the difficult promise."""
import copy
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import repentance_reassessment as policy, shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / r / 'extra_canonical/shepherd_of_hermas/001.yaml' for r in ['translation', 'translation_simplified']]


class OpeningAlignmentTests(unittest.TestCase):
    def test_complete_dialogue_and_no_orphan_notes(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'I.{i}' for i in range(1, 10)])
            self.assertIn('nothing', ps[1])
            self.assertIn('confess my sins', ps[2])
            self.assertIn('broken up by the waters', ps[2])
            self.assertNotIn('cut off by the waters', ps[2])
            self.assertIn('against me', ps[5])
            self.assertIn('falsely accusing', ps[6])
            self.assertIn('goddess[1]', ps[6])
            self.assertIn('righteous', ps[7])
            self.assertIn('captivity', ps[7])
            self.assertIn('wealth', ps[7])
            self.assertIn('Their souls will repent[a][6]', ps[8])
            self.assertIn('no hope', ps[8])
            self.assertIn('despaired', ps[8])
            self.assertIn('heal your sins[7]', ps[8])
            self.assertIn('whole household', ps[8])
            self.assertIn('all the holy ones[8]', ps[8])
            notes = {n['marker']: n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]', doc['translation']['text'])), set(notes))
            for marker in notes:
                self.assertEqual(doc['translation']['text'].count('[' + marker + ']'), 1)
            self.assertIn('different verb', notes['6'])
            self.assertIn('editorial emendation', notes['6'])
            self.assertIn('daughter', notes['1'])
            self.assertIn('first hand', notes['d'])

    def test_history_and_policy_are_exactly_bounded(self):
        a = json.loads((P / 'opening-alignment-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertFalse(a['normalized_source_body_changed'])
        self.assertEqual(hermas.load_normalized_unit('V.1.i').text, arc['normalized_before'])
        for path, row in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), row['file_sha256'])
        docs, _ = review.load_pair(*PATHS)
        followup = json.loads((ROOT / policy.HERMAS_FOLLOWUP).read_text())
        historical = policy.historical_view(PATHS[0], docs[0])
        self.assertEqual(historical, followup['before_record'])
        self.assertEqual(historical['source'], arc['prior_followup']['before_source'])
        self.assertEqual(historical['translation']['text'], arc['prior_followup']['before_text'])
        broken = copy.deepcopy(docs[0])
        broken['translation']['footnotes'][0]['text'] += ' An unreviewed change.'
        with self.assertRaises(ValueError):
            policy.historical_view(PATHS[0], broken)
        for row in json.loads((P / 'model_reviews/legacy030-20261104-r3/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest(), row['file_sha256'])


if __name__ == '__main__':
    unittest.main()
