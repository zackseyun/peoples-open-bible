import json
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.textual_restoration import enoch_29_transaction as transaction
from tools.enoch import verse_parser

class Enoch29Transaction(unittest.TestCase):
    def test_full_two_unit_printed_source_and_review_bindings(self):
        applied=(transaction.P/'application.json').exists()
        rows=transaction.verify_evidence(applied=applied)
        self.assertEqual(set(rows),{1,2})
        self.assertEqual([r.verse for r in verse_parser.parse_chapter(29)[0]],[1,2])
        self.assertEqual([x['reference'] for x in json.loads((transaction.P/'review-final/review.json').read_text())['reviews']],['1 Enoch 29:1','1 Enoch 29:2'])
        if applied:self.assertEqual(transaction.verify_applied()['status'],'applied_verified')
        else:self.assertEqual(transaction.verify_export()['changed_chapters'],[29])

    def test_history_preserves_rejection_before_acceptance(self):
        prior=json.loads((transaction.P/'prior-revise-review.json').read_text())
        current=json.loads((transaction.P/'review-final/review.json').read_text())
        self.assertEqual([r['verdict'] for r in prior['review']['reviews']],['accept','revise'])
        self.assertEqual([r['verdict'] for r in current['reviews']],['accept','accept'])

    def test_changed_review_hash_fails_closed(self):
        actual=transaction.sha
        with patch.object(transaction,'sha',side_effect=lambda path:'bad' if path==transaction.P/'review-final/review.json' else actual(path)):
            with self.assertRaises(ValueError):transaction.verify_evidence(applied=(transaction.P/'application.json').exists())

    def test_source_review_scope_never_claims_human_or_manuscript_certification(self):
        rows=transaction.verify_evidence(applied=(transaction.P/'application.json').exists())
        for row in rows.values():
            self.assertFalse(row['source_correction']['human_specialist_certification'])
            self.assertFalse(row['source_correction']['manuscript_witness_certification'])
            self.assertIn('judgment',row['source_correction']['editorial_decision'])
        manifest=json.loads((transaction.P/'manifest.json').read_text())
        self.assertFalse(manifest['graphic_publication_approved'])

if __name__=='__main__':unittest.main()
