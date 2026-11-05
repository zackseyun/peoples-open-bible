"""Guard the recovered IX/X boundary, without treating reassignment as new extent."""
import hashlib
import json
from pathlib import Path
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'


class VisionBoundariesTests(unittest.TestCase):
    def test_complete_separate_sections_and_warning_scope(self):
        for n, label, uid in [(17, 'IX', 'V.3.ix'), (18, 'X', 'V.3.x')]:
            docs, _ = review.load_pair(*[ROOT / root / f'extra_canonical/shepherd_of_hermas/{n:03}.yaml'
                                        for root in ['translation', 'translation_simplified']])
            for doc in docs:
                ps = doc['translation']['text'].split('\n\n')
                self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'{label}.{i}' for i in range(1, 11)])
                self.assertEqual(doc['source']['text'], hermas.load_normalized_unit(uid).text)
                self.assertNotIn('…', doc['translation']['text'])
                if n == 17:
                    self.assertNotIn('young men', doc['translation']['text'])
                    self.assertIn('righteous and', ps[0])
                    self.assertIn('holy', ps[0])
                    self.assertIn('do not want', ps[0])
                    self.assertIn('not share', ps[3])
                    self.assertIn('judgment', ps[4])
                    self.assertIn('[which you cannot keep]', ps[5])
                    self.assertIn('deprive you of life', ps[8])
                    self.assertIn('among them', ps[9])
                    self.assertIn('account', ps[9])
                    self.assertIn('so that', ps[9])
                    self.assertNotIn('have not been taught', ps[9])
                else:
                    self.assertNotIn('wickedness', doc['translation']['text'])
                    self.assertIn('six young men', ps[0])
                    self.assertIn('Four others', ps[0])
                    self.assertIn('last year', ps[2])
                    self.assertIn('humility', ps[5])
                    self.assertNotIn('to the end', ps[4])
                    self.assertIn('Surely you cannot', ps[7])
                    self.assertIn('fast', ps[5])
                    self.assertIn('one day', ps[6])
                    self.assertIn('harm your flesh', ps[6])
                    self.assertIn('Lord[c]', ps[5])
                    self.assertIn('Sir,', ps[8])
                    self.assertIn('double-mindedness', ps[8])
                    self.assertIn('heart', ps[8])
                    self.assertIn('sir,', ps[9])
                for note in doc['translation']['footnotes']:
                    self.assertEqual(doc['translation']['text'].count('[' + note['marker'] + ']'), 1)

    def test_original_extent_and_history_are_preserved(self):
        a = json.loads((P / 'vision-nine-ten-boundaries-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertTrue(a['normalized_source_body_changed'])
        old17 = arc['flats']['translation/extra_canonical/shepherd_of_hermas/017.yaml']['record']['translation']['text']
        old18 = arc['flats']['translation/extra_canonical/shepherd_of_hermas/018.yaml']['record']['translation']['text']
        self.assertTrue(old17.endswith('and …'))
        self.assertTrue(old18.startswith('Be made holy'))
        self.assertIn('How can you wish to train', old18)
        self.assertIn('X. When she had ceased', old18)
        self.assertEqual(hermas.load_normalized_unit('V.3.ix').text, arc['normalized_before']['V.3.ix'])
        self.assertEqual(hermas.load_normalized_unit('V.3.x').text,
                         arc['normalized_before']['V.3.x'].replace('πρὸς τὸν πύργου', 'πρὸς τὸν πύργον'))
        self.assertTrue(arc['nested_unchanged'])
        for path, item in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), item['file_sha256'])
        for item in json.loads((P / 'model_reviews/legacy061-20261104-r1/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest(), item['file_sha256'])


if __name__ == '__main__':
    unittest.main()
