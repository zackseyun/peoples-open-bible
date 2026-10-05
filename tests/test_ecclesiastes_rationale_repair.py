import unittest
from pathlib import Path

import yaml

from tools import export_mobile_bible as exporter


ROOT = Path(__file__).resolve().parents[1]


class EcclesiastesRationaleRepairTests(unittest.TestCase):
    def test_qal_rationale_does_not_claim_a_causative_stem(self):
        record = yaml.safe_load((ROOT / 'translation/ot/ecclesiastes/007/019.yaml').read_text())
        verb, construction = record['lexical_decisions'][1], record['lexical_decisions'][6]
        self.assertIn('Qal imperfect third-person feminine singular', verb['rationale'])
        self.assertIn('does not preserve a causative Hebrew stem', verb['rationale'])
        self.assertIn('Qal, not Hifil', construction['rationale'])
        self.assertIn('BDB', verb['lexicon'])
        self.assertEqual(record['status'], 'draft')
        self.assertEqual(record['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('source_audit', record)
        history = {x['field']: x for x in record['review_history']}
        self.assertEqual(set(history), {'status', 'revision_pass', 'cross_check', 'source_audit'})
        for item in history.values():
            self.assertEqual(item['archived_from_baseline_sha256'],
                             '013fb552fce4435ec604263539c540a00bbb9e17d1e54a07c9dc25fb74429056')
        self.assertEqual(history['cross_check']['value']['agreement_score'], 0.85)
        self.assertIn('causative force', history['revision_pass']['value']['changes_summary'])
        self.assertIn('causative force', record['revisions'][1]['rationale'])

    def test_reader_wording_and_notes_remain_unchanged(self):
        book = exporter.export_book('ECC')
        self.assertEqual(len(book['chapters']), 12)
        self.assertEqual(sum(len(c['verses']) for c in book['chapters']), 222)
        verse = next(v for c in book['chapters'] if c['chapter'] == 7
                     for v in c['verses'] if v['verse'] == 19)
        self.assertEqual(verse['text'],
                         'Wisdom gives a wise man more strength than ten rulers in the city.')
        self.assertEqual(verse.get('footnotes', []), [])


if __name__ == '__main__':
    unittest.main()
