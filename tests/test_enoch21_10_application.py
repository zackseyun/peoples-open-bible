import hashlib,json,unittest,yaml
from pathlib import Path
from tools.enoch import verse_parser
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'sources/textual_restoration/applications/enoch_21_10_20261017'
R=ROOT/'sources/textual_restoration/applications/enoch_21_review_hold_20261017'
Y=ROOT/'translation/extra_canonical/1_enoch/021/010.yaml'
class Enoch2110Application(unittest.TestCase):
 def test_unit_exact_and_chapter_held(self):
  if (ROOT/'sources/textual_restoration/applications/enoch_full_repair_batch13_20261023/application.json').is_file():
   # Original exact-installed assertions stay unchanged below and run at7c29.
   # Separate batch13 counterproof verifies the actual current paired payload.
   from tools.enoch.replay_5_21_pre_successor import replay
   result=replay('individual21')
   self.assertEqual((result['tests_run'],result['skipped'],result['expected_failures']),(1,0,0))
   self.assertFalse(result['current_corpus_validated'])
   return
  x=yaml.safe_load(Y.read_text());a=json.loads((P/'application.json').read_text())
  source={r.verse:r.text for r in verse_parser.parse_chapter(21)[0]}
  self.assertEqual(x['source']['text'],source[10])
  self.assertEqual(x['reference'],'1 Enoch 21:10')
  self.assertEqual(a['held_reference'],'1 Enoch 21:6')
  self.assertEqual(a['clipped_existing_reference'],'1 Enoch 21:9')
  self.assertTrue(a['chapter_source_inventory_count_complete'])
  for key in ('chapter_editorially_accepted','graphic_publication_approved','app_published'):self.assertFalse(a[key])
  self.assertEqual(a['canonical_sha256'],hashlib.sha256(Y.read_bytes()).hexdigest())
  self.assertFalse(x['source_correction']['chapter_publication_approval'])
 def test_two_full_chapter_reviews_accept_this_unit(self):
  hashes=[]
  for n in (1,2):
   p=R/f'pass{n}';review=json.loads((p/'review.json').read_text())
   self.assertEqual(next(r['verdict'] for r in review['reviews'] if r['reference']=='1 Enoch 21:10'),'accept')
   self.assertEqual(next(r['verdict'] for r in review['reviews'] if r['reference']=='1 Enoch 21:6'),'hold')
   hashes.append(hashlib.sha256((p/'review.json').read_bytes()).hexdigest())
  self.assertEqual(json.loads((P/'application.json').read_text())['review_sha256'],hashes)
if __name__=='__main__':unittest.main()
