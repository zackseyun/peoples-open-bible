"""Protect the printed pronoun, both conditions, and manuscript distinctions."""
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
PATHS = [ROOT / r / 'extra_canonical/shepherd_of_hermas/003.yaml' for r in ['translation', 'translation_simplified']]


class FirstHouseholdTests(unittest.TestCase):
    def test_conditions_and_complete_recital(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'III.{i}' for i in range(1, 5)])
            self.assertIn('against you[h], their parents', ps[0])
            self.assertIn('all the past evils', ps[0])
            self.assertIn('lawless deeds', ps[0])
            self.assertIn('worldly affairs', ps[0])
            for text in ['blacksmith', 'day by day[e]', 'every wickedness', 'if they repent[i][f]', 'with their whole heart', 'books of life[b]', 'with the holy ones[g]']:
                self.assertIn(text, ps[1])
            self.assertIn('terrifying', ps[2])
            self.assertIn('beneficial and gentle for us[j]', ps[2])
            for text in ['invisible and mighty power[k]', 'understanding', 'beauty', 'earth upon the waters[d]', 'wisdom and providence', 'holy church', 'blessed', 'mountains', 'hills', 'seas', 'level', 'elect', 'glory and joy', 'if they keep the statutes of God', 'great faith[l]']:
                self.assertIn(text, ps[3])
            notes = {n['marker']: n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]', doc['translation']['text'])), set(notes))
            for marker in notes:
                self.assertEqual(doc['translation']['text'].count('[' + marker + ']'), 1)
            self.assertIn('corrector ca', notes['h'])
            self.assertIn('editorial emendation', notes['h'])
            self.assertIn('omitting the if', notes['f'])
            self.assertIn('conjectures', notes['k'])
            self.assertIn('whom I love', notes['k'])

    def test_exact_source_history_policy_and_neighbors(self):
        a = json.loads((P / 'first-household-alignment-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertTrue(a['normalized_source_body_changed'])
        self.assertTrue(a['broader_source_collation_flag_retained'])
        self.assertEqual(hermas.load_normalized_unit('V.1.iii').text, arc['normalized_before'].replace('εἰς τὸν Κύριον καὶ εἰς ἡμᾶς', 'εἰς τὸν Κύριον καὶ εἰς ὑμᾶς'))
        self.assertEqual(hermas.raw_page_path(315).read_text(), arc['raw315_before'].replace('εἰς τὸν Κύριον καὶ εἰς ἡμᾶς', 'εἰς τὸν Κύριον καὶ εἰς ὑμᾶς'))
        for path, row in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), row['file_sha256'])
        docs, _ = review.load_pair(*PATHS)
        self.assertEqual(policy.historical_view(PATHS[0], docs[0]), arc['standard_flat']['record'])
        bad = copy.deepcopy(docs[0])
        bad['translation']['text'] = bad['translation']['text'].replace('if they repent', 'they will repent')
        with self.assertRaises(ValueError):
            policy.historical_view(PATHS[0], bad)
        for row in json.loads((P / 'model_reviews/legacy002-20261104-r1/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest(), row['file_sha256'])
        self.assertEqual(next(x for x in json.loads((P / 'coverage.v1.json').read_text())['units'] if x['unit_id'] == 'V.1.iii')['translation_status'], 'requires_source_collation')


if __name__ == '__main__':
    unittest.main()
