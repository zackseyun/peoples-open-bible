"""Allfour source units, exactacceptance and preserved rawOCR."""
import json,unittest
from tools.textual_restoration import enoch_16_transaction as release
from tools.enoch import verse_parser
class EnochSixteenTransaction(unittest.TestCase):
 def test_all_four_units_are_content_bound(self):
  if (release.PACKAGE/'application.json').exists():self.assertEqual(release.verify_applied()['refs'],[f'16:{v}' for v in range(1,5)])
  else:self.assertEqual(len(release.verify_structure()),4)
  r=json.loads((release.PACKAGE/'final-source-review.json').read_text());self.assertEqual(len(r['reviewed_content_sha256']),4);self.assertTrue(all(x['verdict']=='accept' for x in r['reviews'].values()))
 def test_clipped_tail_and_watchers_recovered(self):
  r,_=verse_parser.load_verse(16,1);self.assertIn('[እምትጉሃን፡',r.text);self.assertIn('ወረሰዓነ፡]',r.text);self.assertTrue(r.text.endswith('*ኵሉ፡ ይትፈጸም።'));self.assertIn('ዘይኩን፡',r.text)
 def test_raw_ocr_is_not_overwritten(self):
  raw=(verse_parser.CHARLES_ROOT/'ch16.txt').read_text();self.assertIn('[እምኀኄን፡',raw);self.assertIn('ሲይኩን፡',raw)
if __name__=='__main__':unittest.main()
