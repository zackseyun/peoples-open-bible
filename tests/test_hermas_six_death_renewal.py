"""Guard the restored warning rather than counting headings as completeness."""
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
PATHS = [ROOT / root / 'extra_canonical/shepherd_of_hermas/055.yaml'
         for root in ['translation', 'translation_simplified']]


class DeathRenewalTests(unittest.TestCase):
    def test_restored_missing_warning_preserves_both_outcomes(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'II.{i}' for i in range(1, 7)])
            self.assertIn('angel of luxury and deception', ps[0])
            self.assertIn('living God', ps[1])
            self.assertIn('some to death and some to corruption', ps[1])
            self.assertIn('no repentance of life', ps[2])
            self.assertIn('blasphemed because of them', ps[2])
            self.assertIn('life of such people is death', ps[2])
            self.assertIn('hope for repentance[l]', ps[3])
            self.assertIn('death has eternal destruction', ps[3])
            self.assertIn('very bitter', ps[4])
            self.assertIn('[were entangled', ps[5])
            self.assertIn('not at ease at all', ps[5])
            self.assertEqual(doc['source']['sequence'], 62)
            for note in doc['translation']['footnotes']:
                self.assertEqual(doc['translation']['text'].count('[' + note['marker'] + ']'), 1)
        notes = {n['marker']: n['text'] for n in docs[0]['translation']['footnotes']}
        self.assertIn('absent from its codex', notes['c'])
        self.assertIn('active', notes['e'])
        self.assertIn('shorter nominal', notes['f'])

    def test_archive_and_source_unchanged(self):
        audit = json.loads((P / 'six-death-renewal-restoration-20261104.v1.json').read_text())
        archive = json.loads((P / audit['history_archive']).read_text())
        self.assertTrue(audit['english_extent_changed'])
        self.assertFalse(audit['normalized_source_body_changed'])
        self.assertEqual(hermas.load_normalized_unit('S.6.ii').text, archive['normalized_before']['text'])
        old = archive['standard_flat']['record']['translation']['text']
        self.assertNotIn('no repentance of life', old)
        self.assertNotIn('angel of luxury and deception', old)
        self.assertIn('hope for repentance', old)
        self.assertTrue(archive['nested_unchanged'])
        for path, item in archive['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), item['file_sha256'])
        for path, digest in archive['neighbors_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)

    def test_exact_policy_followup_rejects_changed_warning_or_note(self):
        doc = yaml.safe_load(PATHS[0].read_text())
        self.assertEqual(policy.approved_errors(PATHS[0], doc), [])
        historical = policy.historical_view(PATHS[0], doc)
        self.assertEqual(historical['translation']['text'], policy.plan_by_path()[str(PATHS[0].relative_to(ROOT))]['after_text'])
        for field in ['text', 'footnotes']:
            bad = copy.deepcopy(doc)
            if field == 'text':
                bad['translation']['text'] = bad['translation']['text'].replace('no repentance of life', 'hope of life')
            else:
                bad['translation']['footnotes'][0]['text'] = 'changed'
            self.assertTrue(policy.approved_errors(PATHS[0], bad))


if __name__ == '__main__':
    unittest.main()
