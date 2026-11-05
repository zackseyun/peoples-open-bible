"""Guard the restored reply, continuous parable and unchanged legacy reader identity."""
import hashlib
import json
from pathlib import Path
import unittest
import yaml
from tools import shepherd_of_hermas as h, draft_shepherd_of_hermas as d
from tools.hermas import review_repair_draft as review

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'sources/shepherd_of_hermas/repair'
PATHS = [ROOT / root / 'extra_canonical/shepherd_of_hermas/050.yaml'
         for root in ['translation', 'translation_simplified']]


class FastingTests(unittest.TestCase):
    def test_bounded_source_restoration_and_archived_history(self):
        a = json.loads((P / 'five-fasting-restoration-20261104.v1.json').read_text())
        arc = json.loads((P / a['history_archive']).read_text())
        sel = a['bounded_manuscript_selection']
        self.assertEqual(sel['before'], arc['normalized_s05_i_before'])
        self.assertEqual(sel['after'], sel['before'].replace(
            'ἄκουε, φησίν. 4.', sel['added_phrase'] + 'ἄκουε, φησίν. 4.'))
        self.assertEqual(h.load_normalized_unit('S.5.i').text, sel['after'])
        self.assertEqual(h.load_normalized_unit('S.5.ii').text, arc['normalized_s05_ii_before'])
        self.assertIn('τῷ [Θεῷ]', sel['added_phrase'])
        self.assertNotIn('μακάριόν με ποιήσεις', (ROOT / 'sources/shepherd_of_hermas/transcribed/raw/hermas_lightfoot1891_g31_p0363.txt').read_text())
        self.assertEqual(len(arc['nested_unchanged']), 12)
        for path, item in arc['nested_unchanged'].items():
            self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), item['file_sha256'])
        self.assertEqual(len(a['old_reader_paragraph_crosswalk']), 6)

    def test_complete_compound_scope_hashes_and_prior_accepted_files(self):
        docs, _ = review.load_pair(*PATHS)
        for doc in docs:
            self.assertEqual(doc['id'], 'HERM.S.5.ii')
            self.assertEqual(doc['source']['identity_anchor_unit_id'], 'S.5.ii')
            self.assertEqual([s['unit_id'] for s in doc['source']['source_unit_spans']], ['S.5.i', 'S.5.ii'])
            ps = doc['translation']['text'].split('\n\n')
            self.assertEqual([p.split('. ', 1)[0] for p in ps],
                             [f'I.{i}' for i in range(1, 6)] + [f'II.{i}' for i in range(1, 12)])
            self.assertIn('happy if I learn', ps[2])
            self.assertIn('every evil deed', ps[4])
            self.assertIn('freedom', ps[11])
            self.assertIn('pray', ps[14])
            self.assertIn('greater favor', ps[14])
            self.assertIn('co-heir', ps[15])
            for note in doc['translation']['footnotes']:
                self.assertEqual(doc['translation']['text'].count('[' + note['marker'] + ']'), 1)
        std, simple = docs
        payload = dict(english_text=std['translation']['text'], translation_philosophy=std['translation']['philosophy'],
                       lexical_decisions=std['lexical_decisions'], footnotes=std['translation']['footnotes'],
                       theological_decisions=std['theological_decisions'])
        self.assertEqual(std['ai_draft']['output_hash'], d.sha256_hex(d.canonical_json(payload)))
        self.assertEqual(simple['ai_draft']['output_hash'], d.sha256_hex(simple['translation']['text']))
        receipt = json.loads((P / 'model_reviews/legacy049-20261104-r2/receipt.json').read_text())
        for item in receipt['input_manifest']:
            self.assertEqual(hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest(), item['file_sha256'])


if __name__ == '__main__':
    unittest.main()
