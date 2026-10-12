"""Complete chapter15, source/readback, note anchors and unchanged rawOCR."""
import hashlib,json,unittest
from tools.textual_restoration import enoch_15_transaction as release
from tools.enoch import verse_parser
class EnochFifteenTransaction(unittest.TestCase):
 def test_scoped_source_and_review_bindings(self):
  if (release.PACKAGE/'application.json').exists():self.assertEqual(release.verify_applied()['refs'],[f'15:{v}' for v in range(1,13)])
  else:self.assertEqual(len(release.verify_structure()),12)
  review=json.loads((release.PACKAGE/'final-source-review.json').read_text());self.assertEqual(len(review['reviewed_content_sha256']),12);self.assertTrue(all(r['verdict']=='accept' for r in review['reviews'].values()))
 def test_source_boundaries_and_women_not_animals(self):
  nine,_=verse_parser.load_verse(15,9);ten,_=verse_parser.load_verse(15,10);twelve,_=verse_parser.load_verse(15,12)
  self.assertFalse(nine.text.endswith('['));self.assertTrue(ten.text.startswith('['));self.assertTrue(ten.text.endswith(']'));self.assertIn('አንስት፡',twelve.text);self.assertNotIn('እንስሳ፡',twelve.text)
 def test_raw_ocr_unchanged(self):
  raw=verse_parser.CHARLES_ROOT/'ch16.txt';self.assertIn('እንስሳ፡',raw.read_text());self.assertIn('[10.',raw.read_text())
if __name__=='__main__':unittest.main()
