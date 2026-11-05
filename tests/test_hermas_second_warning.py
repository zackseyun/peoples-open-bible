"""Guard conditional forgiveness, difficult negatives, and the printed-verb repair."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / r / 'extra_canonical/shepherd_of_hermas/006.yaml' for r in ['translation', 'translation_simplified']]


class SecondWarningTests(unittest.TestCase):
    def test_conditions_and_temporal_groups_remain_explicit(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'II.{i}' for i in range(1, 9)])
            for phrase in ['all the holy ones[d]', 'up to this day', 'if they repent[c] with all their heart', 'and remove from their heart']:
                self.assertIn(phrase, ps[3])
            for phrase in ['appointed day[e]', 'they have no salvation', 'end for the righteous', 'fulfilled for all the holy ones', 'until the last day']:
                self.assertIn(phrase, ps[4])
            self.assertIn('will not deny their life[12]', ps[6])
            for phrase in ['their Lord[f]', 'are rejected from their life[a][14]', 'now about to deny', 'who denied before']:
                self.assertIn(phrase, ps[7])
            notes = {n['marker']: n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]', doc['translation']['text'])), set(notes))
            self.assertEqual(len(notes), 20)
            for marker in notes:
                self.assertEqual(doc['translation']['text'].count('[' + marker + ']'), 1)
            self.assertIn('first hand', notes['f'])
            self.assertIn('changed by ca', notes['f'])
            self.assertIn('positively', notes['12'])
            self.assertIn('editorial emendation', notes['g'])

    def test_exact_printed_correction_and_preserved_history(self):
        a = json.loads((P / 'second-warning-alignment-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertTrue(a['broader_source_collation_flag_retained'])
        self.assertEqual(hermas.load_normalized_unit('V.2.ii').text, arc['normalized_before'].replace('ἀπεγνωσθαι', 'ἀπεγνωρίσθαι'))
        raw = (ROOT / 'sources/shepherd_of_hermas/transcribed/raw/hermas_lightfoot1891_p0317.txt').read_text()
        self.assertEqual(raw, arc['raw317_before'].replace('ἀπεγνωσθαι', 'ἀπεγνωρίσθαι'))
        self.assertEqual(len(arc['nested_unchanged']), 16)
        for path, row in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), row['file_sha256'])
        for row in json.loads((P / 'model_reviews/legacy005-20261104-r2/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest(), row['file_sha256'])


if __name__ == '__main__':
    unittest.main()
