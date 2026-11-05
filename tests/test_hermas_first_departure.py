"""Keep the two departures, the later/earlier contrast and corrected readings."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / r / 'extra_canonical/shepherd_of_hermas/004.yaml' for r in ['translation', 'translation_simplified']]


class FirstDepartureTests(unittest.TestCase):
    def test_departures_and_contrasting_reading_parts(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'IV.{i}' for i in range(1, 4)])
            self.assertIn('four young men', ps[0])
            self.assertIn('lifted the chair[e]', ps[0])
            for text in ['my chest', 'my reading', 'last things[a]', 'earlier things are hard and harsh[d]', 'for the righteous', 'nations[b]', 'apostates']:
                self.assertIn(text, ps[1])
            for text in ['two men', 'by the elbows[f]', 'where the chair also was', 'cheerful', 'Take courage[c], Hermas']:
                self.assertIn(text, ps[2])
            self.assertIn('east', ps[0])
            self.assertIn('east', ps[2])
            notes = {n['marker']: n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]', doc['translation']['text'])), set(notes))
            for marker in notes:
                self.assertEqual(doc['translation']['text'].count('[' + marker + ']'), 1)
            self.assertIn('S1 adds', notes['d'])
            self.assertIn('ca adds both', notes['e'])
            self.assertIn('their shoulders', notes['f'])
            self.assertIn('with their hands', notes['f'])
            self.assertIn('not direct Geʿez collation', notes['c'])
            self.assertIn('one must go', notes['c'])

    def test_preserved_source_history_and_neighbor(self):
        a = json.loads((P / 'first-departure-alignment-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertFalse(a['normalized_source_body_changed'])
        self.assertTrue(a['broader_source_collation_flag_retained'])
        self.assertEqual(hermas.load_normalized_unit('V.1.iv').text, arc['normalized_before'])
        for path, row in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), row['file_sha256'])
        for row in json.loads((P / 'model_reviews/legacy003-20261104-r2/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest(), row['file_sha256'])
        self.assertEqual(next(x for x in json.loads((P / 'coverage.v1.json').read_text())['units'] if x['unit_id'] == 'V.1.iv')['translation_status'], 'requires_source_collation')


if __name__ == '__main__':
    unittest.main()
