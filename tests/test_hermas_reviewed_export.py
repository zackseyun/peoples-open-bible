"""Exercise the actual reviewed-input and reader-note publication boundary."""
import unittest
from pathlib import Path
from tools.hermas import export_reviewed_reader as export
from tools.hermas.review_repair_draft import sha
ROOT=Path(__file__).resolve().parents[1]
class ReviewedHermasExportTests(unittest.TestCase):
    def test_actual_accepted_pair_and_note_localization(self):
        p=ROOT/'sources/shepherd_of_hermas/repair/model_reviews/legacy027-20261105-r2/receipt.json'
        docs=export.verified_pair({'receipt':str(p.relative_to(ROOT)),'receipt_sha256':sha(p.read_bytes())})
        for doc in docs:
            paragraphs=export.paragraphs(doc)
            self.assertEqual(len(paragraphs),7)
            self.assertEqual('\n\n'.join(p['text'] for p in paragraphs),doc['translation']['text'])
            self.assertEqual({n['marker'] for p in paragraphs for n in p.get('footnotes',[])},{n['marker'] for n in doc['translation']['footnotes']})
    def test_changed_receipt_and_orphaned_notes_are_rejected(self):
        with self.assertRaisesRegex(ValueError,'Changed review receipt'):
            export.verified_pair({'receipt':'sources/shepherd_of_hermas/repair/model_reviews/legacy027-20261105-r2/receipt.json','receipt_sha256':'0'*64})
        for doc in [{'translation':{'text':'A claim[a].','footnotes':[]}}, {'translation':{'text':'A claim.','footnotes':[{'marker':'a','text':'Lost note'}]}}]:
            with self.assertRaisesRegex(ValueError,'Orphaned/unanchored'):export.paragraphs(doc)
if __name__=='__main__':unittest.main()
