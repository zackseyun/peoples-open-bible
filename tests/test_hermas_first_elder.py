"""Preserve questions, moral contrast, and the witness-specific corrections."""
import hashlib
import json
from pathlib import Path
import re
import unittest
from tools import shepherd_of_hermas as hermas
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / r / 'extra_canonical/shepherd_of_hermas/002.yaml' for r in ['translation', 'translation_simplified']]


class FirstElderTests(unittest.TestCase):
    def test_argument_and_local_notes(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps], [f'II.{i}' for i in range(1, 5)])
            for term in ['saved', 'make atonement to God', 'completed sins[a][4]', 'Lord']:
                self.assertIn(term, ps[0])
            for term in ['chair[2]', 'snowy wool[6]', 'elderly woman[5]', 'weeping[b]', 'book']:
                self.assertIn(term, ps[1])
            self.assertIn('contention[7]', ps[2])
            for term in ['By no means', 'servant of God[d]', 'surely', 'spirit[8]', 'proven', 'if it', 'every evil desire', 'all simplicity', 'great innocence[f]']:
                self.assertIn(term, ps[3])
            notes = {x['marker']: x['text'] for x in doc['translation']['footnotes']}
            self.assertEqual(set(re.findall(r'\[([a-z]|[0-9]+)\]', doc['translation']['text'])), set(notes))
            for marker in notes:
                self.assertEqual(doc['translation']['text'].count('[' + marker + ']'), 1)
            self.assertIn('first hand', notes['6'])
            self.assertIn('rejoicing', notes['b'])
            self.assertIn('marked supplied', notes['c'])
            self.assertIn('perhaps', notes['e'])
            self.assertIn('editorial supplement', notes['f'])
            self.assertEqual(next(x['chosen'] for x in doc['lexical_decisions'] if x['source_word'] == 'δοῦλος τοῦ Θεοῦ'), 'servant of God')

    def test_preserved_source_and_archives(self):
        a = json.loads((P / 'first-elder-alignment-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['english_extent_changed'])
        self.assertFalse(a['normalized_source_body_changed'])
        self.assertTrue(a['broader_source_collation_flag_retained'])
        self.assertEqual(hermas.load_normalized_unit('V.1.ii').text, arc['normalized_before'])
        for path, row in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), row['file_sha256'])
        for row in json.loads((P / 'model_reviews/legacy001-20261104-r2/receipt.json').read_text())['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest(), row['file_sha256'])
        u = next(x for x in json.loads((P / 'coverage.v1.json').read_text())['units'] if x['unit_id'] == 'V.1.ii')
        self.assertEqual(u['translation_status'], 'requires_source_collation')


if __name__ == '__main__':
    unittest.main()
