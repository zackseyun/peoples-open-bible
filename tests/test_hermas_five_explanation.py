"""Prevent the old fasting/understanding joins from replacing complete sections."""
import hashlib
import json
from pathlib import Path
import unittest
from tools import shepherd_of_hermas as h, draft_shepherd_of_hermas as d
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / root / 'extra_canonical/shepherd_of_hermas/051.yaml'
         for root in ['translation', 'translation_simplified']]


class FastExplanationTests(unittest.TestCase):
    def test_unchanged_source_and_preserved_old_records(self):
        a = json.loads((P / 'five-fast-explanation-restoration-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        self.assertFalse(a['normalized_source_body_changed'])
        self.assertEqual(len(a['old_reader_paragraph_crosswalk']), 5)
        self.assertEqual(len(arc['nested_unchanged']), 10)
        for uid, item in arc['normalized_before'].items():
            self.assertEqual(h.load_normalized_unit(uid).text, item['text'])
            self.assertEqual(d.sha256_hex(item['text']), item['sha256'])
        for path, item in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), item['file_sha256'])
        prior = json.loads((P / 'model_reviews/legacy050-20261104-r1/receipt.json').read_text())
        for item in prior['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest(), item['file_sha256'])

    def test_complete_sections_keep_distinct_promises_and_fasting_gift(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            self.assertEqual(doc['id'], 'HERM.S.5.iii')
            self.assertEqual([s['unit_id'] for s in doc['source']['source_unit_spans']], ['S.5.iii', 'S.5.iv'])
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps],
                             [f'III.{i}' for i in range(1, 10)] + [f'IV.{i}' for i in range(1, 6)])
            self.assertIn('bread and water', ps[6])
            for term in ['widow', 'orphan', 'in need', 'humility', 'pray']:
                self.assertIn(term, ps[6])
            self.assertNotIn('prudence', doc['translation']['text'])
            self.assertIn('Whatever' if doc is docs[1] else 'whatever', ps[8])
            self.assertNotIn('understanding', ps[8])
            self.assertIn('understanding', ps[12])
            self.assertIn('anything at all', ps[10])
            for note in doc['translation']['footnotes']:
                self.assertEqual(doc['translation']['text'].count('[' + note['marker'] + ']'), 1)
        std, simple = docs
        payload = dict(english_text=std['translation']['text'], translation_philosophy=std['translation']['philosophy'],
                       lexical_decisions=std['lexical_decisions'], footnotes=std['translation']['footnotes'],
                       theological_decisions=std['theological_decisions'])
        self.assertEqual(std['ai_draft']['output_hash'], d.sha256_hex(d.canonical_json(payload)))
        self.assertEqual(simple['ai_draft']['output_hash'], d.sha256_hex(simple['translation']['text']))


if __name__ == '__main__':
    unittest.main()
