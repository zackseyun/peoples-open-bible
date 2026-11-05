"""Guard conditions and distinguish bracketed, corrected and conjectural evidence."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / r / 'extra_canonical/shepherd_of_hermas/007.yaml' for r in ['translation', 'translation_simplified']]


class MaximusWarningTests(unittest.TestCase):
    def test_complete_exhortation_and_precise_evidence_limits(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'III.{i}' for i in range(1, 5)])
            for phrase in ['your sister[a]', 'cleansed from their former sins', 'righteous discipline[b]', 'if you do not bear a grudge', 'Resentment produces death[f]', 'private tribulations[g]']:
                self.assertIn(phrase, ps[0])
            for phrase in ['did not depart from the living God', 'simplicity and great self-control', 'have saved you, if you continue in them[i]', 'guilelessness and simplicity', 'eternal life[j]']:
                self.assertIn(phrase, ps[1])
            self.assertIn('never be destroyed[k]', ps[2])
            for phrase in ['Maximus', 'if it seems good to you to deny again[d]', 'those who return[e]', 'Eldad and Modat[c]', 'people in the wilderness']:
                self.assertIn(phrase, ps[3])
            notes = {n['marker']: n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]', doc['translation']['text'])), set(notes))
            for marker in notes:
                self.assertEqual(doc['translation']['text'].count('[' + marker + ']'), 1)
            self.assertIn('Harmer’s conjecture', notes['d'])
            self.assertIn('square brackets', notes['k'])
            self.assertIn('one unreadable-character gap', notes['j'])
            self.assertIn('not direct Geʿez', notes['j'])
            self.assertIn('ca changes it to sins', notes['h'])

    def test_unchanged_source_nested_history_and_accepted_neighbor(self):
        a = json.loads((P / 'maximus-warning-alignment-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertFalse(a['normalized_source_body_changed'])
        self.assertTrue(a['broader_source_collation_flag_retained'])
        self.assertEqual(hermas.load_normalized_unit('V.2.iii').text, arc['normalized_before'])
        self.assertEqual(len(arc['nested_unchanged']), 8)
        for path, row in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), row['file_sha256'])
        for row in json.loads((P / 'model_reviews/legacy006-20261104-r2/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest(), row['file_sha256'])


if __name__ == '__main__':
    unittest.main()
