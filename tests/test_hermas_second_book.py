"""Protect time/place links, the borrowing reply, and copying uncertainty."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / r / 'extra_canonical/shepherd_of_hermas/005.yaml' for r in ['translation', 'translation_simplified']]


class SecondBookTests(unittest.TestCase):
    def test_full_narrative_and_local_explanations(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'I.{i}' for i in range(1, 5)])
            for text in ['Cumae[a]', 'spirit[b]', 'same place', 'year before']:
                self.assertIn(text, ps[0])
            for text in ['knelt', '[c]', 'because', 'worthy', 'former sins']:
                self.assertIn(text, ps[1])
            for text in ['last year[h]', 'little book[d]', 'elect of God[f]', 'so many things', 'Take it', 'give it back to me[g]']:
                self.assertIn(text, ps[2])
            for text in ['field', 'letter for letter', 'syllables[e]', 'snatched from my hand']:
                self.assertIn(text, ps[3])
            self.assertTrue('by whom I did not see' in ps[3] or 'did not see who took it' in ps[3])
            notes = {n['marker']: n['text'] for n in doc['translation']['footnotes']}
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]', doc['translation']['text'])), set(notes))
            for marker in notes:
                self.assertEqual(doc['translation']['text'].count('[' + marker + ']'), 1)
            self.assertIn('ca replaces', notes['g'])
            self.assertIn('no separate', notes['g'])
            self.assertIn('does not by itself prove personal illiteracy', notes['e'])
            self.assertIn('editorial emendation', notes['e'])
            self.assertIn('not direct Geʿez', notes['h'])

    def test_preserved_source_history_and_neighbor(self):
        a = json.loads((P / 'second-book-alignment-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertFalse(a['normalized_source_body_changed'])
        self.assertTrue(a['broader_source_collation_flag_retained'])
        self.assertEqual(hermas.load_normalized_unit('V.2.i').text, arc['normalized_before'])
        for path, row in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), row['file_sha256'])
        for row in json.loads((P / 'model_reviews/legacy004-20261104-r1/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest(), row['file_sha256'])
        self.assertEqual(next(x for x in json.loads((P / 'coverage.v1.json').read_text())['units'] if x['unit_id'] == 'V.2.i')['translation_status'], 'requires_source_collation')


if __name__ == '__main__':
    unittest.main()
