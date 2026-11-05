"""Protect full parable identities, disclosed negation and unaltered source history."""
import hashlib
import json
from pathlib import Path
import unittest
from tools import shepherd_of_hermas as h, draft_shepherd_of_hermas as d
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / root / 'extra_canonical/shepherd_of_hermas/052.yaml'
         for root in ['translation', 'translation_simplified']]


class ServantExplanationTests(unittest.TestCase):
    def test_source_and_history_preserved(self):
        a = json.loads((P / 'five-servant-explanation-restoration-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['normalized_source_body_changed'])
        self.assertEqual(len(arc['nested_unchanged']), 8)
        for uid, item in arc['normalized_before'].items():
            self.assertEqual(h.load_normalized_unit(uid).text, item['text'])
            self.assertEqual(d.sha256_hex(item['text']), item['sha256'])
        for path, item in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), item['file_sha256'])
        neighbor = ROOT / 'translation/extra_canonical/shepherd_of_hermas/053.yaml'
        self.assertEqual(hashlib.sha256(neighbor.read_bytes()).hexdigest(), arc['neighbor053_unchanged_sha256'])
        for key in ['legacy049-20261104-r2', 'legacy050-20261104-r1', 'legacy051-20261104-r2']:
            for item in json.loads((P / 'model_reviews' / key / 'receipt.json').read_text())['input_manifest']:
                self.assertEqual(hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest(), item['file_sha256'])

    def test_complete_sections_and_disclosed_differences(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            self.assertEqual(doc['id'], 'HERM.S.5.v')
            self.assertEqual([s['unit_id'] for s in doc['source']['source_unit_spans']], ['S.5.v', 'S.5.vi'])
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps],
                             [f'V.{i}' for i in range(1, 6)] + [f'VI.{i}' for i in range(1, 9)])
            self.assertIn('servant is the Son of God', ps[1])
            self.assertIn('not placed', ps[5])
            self.assertIn('created all creation', ps[9])
            self.assertIn('undefiled and spotless', ps[11])
            notes = {n['marker']: n['text'] for n in doc['translation']['footnotes']}
            self.assertIn('Michigan cannot vote', notes['f'])
            self.assertIn('lacks it', notes['f'])
            self.assertIn('Palatina', notes['a'])
            for n in doc['translation']['footnotes']:
                self.assertEqual(doc['translation']['text'].count('[' + n['marker'] + ']'), 1)
        std, simple = docs
        payload = dict(english_text=std['translation']['text'], translation_philosophy=std['translation']['philosophy'],
                       lexical_decisions=std['lexical_decisions'], footnotes=std['translation']['footnotes'],
                       theological_decisions=std['theological_decisions'])
        self.assertEqual(std['ai_draft']['output_hash'], d.sha256_hex(d.canonical_json(payload)))
        self.assertEqual(simple['ai_draft']['output_hash'], d.sha256_hex(simple['translation']['text']))


if __name__ == '__main__':
    unittest.main()
