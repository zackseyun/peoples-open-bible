"""Maintainer-selected grief wording, without flattening other uses of nacham."""
import re
import unittest
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1] / 'translation'
class DivineGriefTests(unittest.TestCase):
    def record(self, path):
        return yaml.safe_load((ROOT / (path + '.yaml')).read_text())
    def test_genesis_exact_reader_text(self):
        text = self.record('ot/genesis/006/006')['translation']['text']
        self.assertEqual(re.sub(r'\[[a-z]\]', '', text), 'And Yahweh was grieved that he had made man on the earth, and he was pained in his heart.')
    def test_four_renderings_and_notes(self):
        for path in ('ot/genesis/006/006','ot/genesis/006/007','ot/1_samuel/015/011','ot/1_samuel/015/035'):
            with self.subTest(path=path):
                record = self.record(path)
                text = record['translation']['text']
                self.assertIn('grieved', text)
                self.assertNotIn('regret', text)
                notes = record['translation']['footnotes']
                self.assertEqual(set(re.findall(r'\[([a-z])\]', text)), {n['marker'] for n in notes})
                self.assertTrue(any('regret' in n['text'] for n in notes))
                self.assertEqual(record['revisions'][0]['to'], text)
    def test_contextual_relenting_and_human_regret_preserved(self):
        for path in ('ot/exodus/032/014','ot/jonah/003/010','ot/1_samuel/015/029'):
            self.assertIn('relent', self.record(path)['translation']['text'])
        self.assertIn('regretted', self.record('nt/matthew/027/003')['translation']['text'])
if __name__ == '__main__':
    unittest.main()
