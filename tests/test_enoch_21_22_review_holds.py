import hashlib,json,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/'sources/textual_restoration/applications'
class EnochHeldSourceReviews(unittest.TestCase):
 def test_both_chapters_are_complete_scope_but_not_editorially_approved(self):
  for chapter,count,passes in ((21,10,2),(22,14,3)):
   root=BASE/f'enoch_{chapter}_review_hold_20261017';state=json.loads((root/'status.json').read_text());final=json.loads((root/f'pass{passes}/review.json').read_text())
   self.assertEqual(state['expected_printed_units'],count);self.assertTrue(final['chapter_complete']);self.assertEqual(len(final['reviews']),count)
   self.assertEqual([r['reference'] for r in final['reviews'] if r['verdict']=='hold'],state['held_references'])
   self.assertEqual([r['reference'] for r in final['reviews'] if r['verdict']=='revise'],state['revise_references'])
   self.assertEqual([r['reference'] for r in final['reviews'] if r['verdict']=='accept'],state['accepted_references'])
   for key in ('chapter_editorially_accepted','canonical_changed','graphic_published','full_108_goal_complete','human_specialist_certification'):self.assertFalse(state[key])
 def test_every_preserved_review_input_result_and_provenance_is_hash_bound(self):
  for chapter,passes in ((21,2),(22,3)):
   root=BASE/f'enoch_{chapter}_review_hold_20261017';state=json.loads((root/'status.json').read_text())
   for path,digest in state['files'].items():self.assertEqual(hashlib.sha256((root/path).read_bytes()).hexdigest(),digest)
   for n in range(1,passes+1):
    p=root/f'pass{n}';provenance=json.loads((p/'provenance.json').read_text());review=json.loads((p/'review.json').read_text())
    self.assertTrue(review['chapter_complete']);self.assertEqual(hashlib.sha256((p/'review.json').read_bytes()).hexdigest(),provenance['review_sha256'])
    self.assertFalse(provenance['canonical_translation_changed']);self.assertFalse(provenance['human_specialist_certification'])
if __name__=='__main__':unittest.main()
