"""Guard the cleansing qualifier, distinct builders, and complete stone groups."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / r / 'extra_canonical/shepherd_of_hermas/010.yaml' for r in ['translation', 'translation_simplified']]


class TowerStonesTests(unittest.TestCase):
    def test_complete_scene_and_unharmonized_variants(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'II.{i}' for i in range(1, 10)])
            for phrase in ['crucifixions[1]', 'wild beasts[13]', 'the Name[2]', 'sanctuary[3]']:
                self.assertIn(phrase, ps[0])
            self.assertIn('same', ps[0])
            for phrase in ['will be cleansed', 'not double-minded[4]', 'all their sins', 'up to this day[5]']:
                self.assertIn(phrase, ps[1])
            self.assertIn('bench[6]', ps[3])
            self.assertNotIn('plaited', doc['translation']['text'])
            for phrase in ['[You,][7]', 'bright rod[b]', 'square-cut, shining stones']:
                self.assertIn(phrase, ps[3])
            for phrase in ['foursquare[8]', 'six young men[c]', 'Myriads' if doc is docs[1] else 'myriads']:
                self.assertIn(phrase, ps[4])
            self.assertIn('single stone', ps[5])
            for phrase in ['scabby[10]', 'cracks', 'truncated[11]', 'white and round']:
                self.assertIn(phrase, ps[7])
            for phrase in ['trackless places[12]', 'burned[f]', 'water[g]', 'wanted']:
                self.assertIn(phrase, ps[8])
            notes = {n['marker']: n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]', doc['translation']['text'])), set(notes))
            for marker in notes:
                self.assertEqual(doc['translation']['text'].count('[' + marker + ']'), 1)
            self.assertIn('all who are doubtful', notes['4'])
            self.assertIn('not counted as a preserved Ethiopic negative', notes['4'])
            self.assertIn('sixty', notes['c'])
            self.assertIn('both places', notes['c'])
            self.assertIn('unreadable-character gap', notes['a'])
            self.assertIn('first lacks', notes['f'])

    def test_one_print_change_and_accepted_neighbor_history(self):
        a = json.loads((P / 'tower-stones-alignment-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertTrue(a['broader_source_collation_flag_retained'])
        self.assertEqual(hermas.load_normalized_unit('V.3.ii').text, arc['normalized_before'].replace('συμπλέσιον', 'συμψέλιον'))
        raw = ROOT / 'sources/shepherd_of_hermas/transcribed/raw/hermas_lightfoot1891_p0320.txt'
        self.assertEqual(arc['raw_before']['320'].count('συμπλέσιον'), 1)
        self.assertEqual(raw.read_text(), arc['raw_before']['320'].replace('συμπλέσιον', 'συμψέλιον'))
        self.assertEqual(len(arc['nested_unchanged']), 18)
        for path, row in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), row['file_sha256'])
        for row in json.loads((P / 'model_reviews/legacy009-20261104-r2/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest(), row['file_sha256'])


if __name__ == '__main__':
    unittest.main()
