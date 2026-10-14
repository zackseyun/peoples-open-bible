"""Full83accepted source closure, provenance and strict bounded writes."""
import copy,hashlib,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools.textual_restoration import enoch_83_transaction as tx
from tools.enoch import verse_parser, audit_pob_source_coverage
class EnochEightyThree(unittest.TestCase):
 def test_all_eleven_content_bound(self):
  if (tx.PACKAGE/'application.json').exists():self.assertEqual(tx.verify_applied()['refs'],[f'83:{v}' for v in range(1,12)])
  else:self.assertEqual(len(tx.verify_structure()),11)
  tx.verify_review_provenance()
 def test_full_boundary_inventory_is_explicit(self):
  self.assertEqual(audit_pob_source_coverage.EXPECTED_VERSES[83],11)
  rows,warnings=verse_parser.parse_chapter(83);self.assertEqual([r.verse for r in rows],list(range(1,12)))
  self.assertTrue(rows[-1].text.endswith('ፍኖተ፡ እንተ፡ ተርእየት፡ ሎቱ።'))
  self.assertNotIn('LXXXIV',rows[-1].text)
 def test_glyph_repairs_preserve_critical_marks(self):
  self.assertIn('ወመላልያል፡',verse_parser.load_verse(83,6)[0].text)
  self.assertIn('እምሑውየ፡',verse_parser.load_verse(83,6)[0].text)
  self.assertTrue(verse_parser.load_verse(83,6)[0].text.endswith('ትአውይ።'))
  self.assertIn('ውስተ፡ ቀላይ፡',verse_parser.load_verse(83,7)[0].text)
  self.assertIn('አርእየከ፡',verse_parser.load_verse(83,10)[0].text)
  self.assertIn('እመስኮ፡',verse_parser.load_verse(83,11)[0].text)
  self.assertIn('†ዘአመረ፡',verse_parser.load_verse(83,11)[0].text)
 def test_raw_ocr_unmodified(self):
  raw=(verse_parser.CHARLES_ROOT/'ch83.txt').read_text();self.assertIn('ወመላእያል፡',raw);self.assertIn('አርአየከ፡',raw)
  self.assertIn('እመኅከወ፡',(verse_parser.CHARLES_ROOT/'ch84.txt').read_text())
 def test_no_relabeling_or_changed_input(self):
  for file in ('review.json','review-input.json'):
   with tempfile.TemporaryDirectory() as directory:
    pkg=Path(directory)/'package';shutil.copytree(tx.PACKAGE,pkg);p=pkg/'review-pass-4'/file;p.write_bytes(p.read_bytes()+b' ')
    with patch.object(tx,'PACKAGE',pkg):
     with self.assertRaisesRegex(ValueError,'drift'):tx.verify_review_provenance()
 def test_candidate_drift_fails_before_write(self):
  with tempfile.TemporaryDirectory() as directory:
   pkg=Path(directory)/'package';shutil.copytree(tx.PACKAGE,pkg);p=pkg/'083-011.candidate.yaml';p.write_bytes(p.read_bytes()+b' ')
   with patch.object(tx,'PACKAGE',pkg):
    with self.assertRaisesRegex(ValueError,'Package file changed'):tx.verify_structure()
 def test_raw_cleanup_drift_fails_closed(self):
  with tempfile.TemporaryDirectory() as directory:
   p=Path(directory);shutil.copytree(verse_parser.CHARLES_ROOT,p/'raw');q=p/'raw/ch83.txt';q.write_text(q.read_text().replace('ወመላእያል፡','DIFFERENT',1))
   with patch.object(verse_parser,'CHARLES_ROOT',p/'raw'), patch.object(verse_parser,'REPO_ROOT',p):
    with self.assertRaisesRegex(ValueError,'baseline drift'):verse_parser.parse_chapter(83)
if __name__=='__main__':unittest.main()
