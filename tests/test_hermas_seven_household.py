"""Restore the chapter ending and guard its household/forgiveness conditions."""
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
PATHS = [ROOT / root / 'extra_canonical/shepherd_of_hermas/059.yaml'
         for root in ['translation', 'translation_simplified']]


class SevenHouseholdTests(unittest.TestCase):
    def test_full_ending_conditions_and_household_subject(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [str(i) for i in range(1, 8)])
            self.assertIn('while you are at ease', ps[2])
            self.assertNotIn('being steadfast', ps[2])
            self.assertIn('forgiven immediately', ps[3])
            self.assertIn('Not at all', ps[3])
            self.assertIn('afflict his own soul', ps[3])
            self.assertIn('If he endures', ps[3])
            self.assertIn('[God]', ps[4])
            self.assertIn('every evil deed', ps[4])
            self.assertIn('so that, knowing', ps[4])
            self.assertIn('[easily]', ps[5])
            self.assertIn('your children', ps[5].lower())
            self.assertIn('strong and clean', ps[5])
            self.assertIn('if you keep', ps[6].lower())
            self.assertIn('all who walk', ps[6])
            self.assertEqual(doc['source']['sequence'], 66)
            for note in doc['translation']['footnotes']:
                self.assertEqual(doc['translation']['text'].count('[' + note['marker'] + ']'), 1)
        notes = {n['marker']: n['text'] for n in docs[0]['translation']['footnotes']}
        self.assertIn('six-line gap', notes['b'])
        self.assertIn('perhaps', notes['g'])
        self.assertIn('physical gap', notes['g'])
        self.assertIn('place', notes['j'])
        self.assertIn('Palatina173 omits', notes['k'])

    def test_boundary_archive_without_false_new_extent(self):
        audit = json.loads((P / 'seven-household-restoration-20261104.v1.json').read_text())
        archive = json.loads((P / audit['history_archive']).read_text())
        self.assertFalse(audit['normalized_source_body_changed'])
        self.assertEqual(hermas.load_normalized_unit('S.7').text, archive['normalized_before']['text'])
        donor = archive['read_only_donor60']['translation/extra_canonical/shepherd_of_hermas/060.yaml']['record']
        self.assertIn('sins of those who are repenting', donor['translation']['text'])
        self.assertNotIn('be restored again', donor['translation']['text'])
        for path, item in archive['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), item['file_sha256'])
        later = json.loads((P / 'legacy60-before-willow-restoration-20261104.v1.json').read_text())
        for path, item in archive['read_only_donor60'].items():
            self.assertEqual(path, later['standard_flat']['path'])
            self.assertEqual(item['file_sha256'], later['standard_flat']['file_sha256'])
            current = yaml.safe_load((ROOT / path).read_text())
            self.assertEqual(current['source_grounding']['evidence_record'],
                             'sources/shepherd_of_hermas/repair/eight-willow-restoration-20261104.v1.json')
            self.assertEqual(current['source']['unit_id'], 'S.8.i')

    def test_exact_policy_followup_rejects_unconditional_promise(self):
        doc = yaml.safe_load(PATHS[0].read_text())
        self.assertEqual(policy.approved_errors(PATHS[0], doc), [])
        historical = policy.historical_view(PATHS[0], doc)
        self.assertEqual(historical['translation']['text'], policy.plan_by_path()[str(PATHS[0].relative_to(ROOT))]['after_text'])
        bad = copy.deepcopy(doc)
        bad['translation']['text'] = bad['translation']['text'].replace('if you keep these with your household', 'whatever your household does')
        self.assertNotEqual(bad['translation']['text'], doc['translation']['text'])
        self.assertTrue(policy.approved_errors(PATHS[0], bad))
        bad = copy.deepcopy(doc)
        bad['translation']['footnotes'][0]['text'] = 'changed'
        self.assertTrue(policy.approved_errors(PATHS[0], bad))


if __name__ == '__main__':
    unittest.main()
