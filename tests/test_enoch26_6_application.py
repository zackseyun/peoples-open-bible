import hashlib,json,unittest,yaml
from pathlib import Path
from tools.enoch import verse_parser
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'sources/textual_restoration/applications/enoch_26_6_20261017'
Y=ROOT/'translation/extra_canonical/1_enoch/026/006.yaml'
class Enoch266Application(unittest.TestCase):
 def test_individual_unit_exact_and_chapter_still_held(self):
  record=yaml.safe_load(Y.read_text());app=json.loads((P/'application.json').read_text())
  recovered={r.verse:r.text for r in verse_parser.parse_chapter(26)[0]}
  self.assertEqual(record['source']['text'],recovered[6]);self.assertEqual(record['reference'],'1 Enoch 26:6')
  self.assertIn('marveled greatly',record['translation']['text'])
  for key in ('chapter_complete','graphic_publication_approved','app_published'):self.assertFalse(app[key])
  self.assertEqual(app['canonical_sha256'],hashlib.sha256(Y.read_bytes()).hexdigest())
  self.assertFalse(record['source_correction']['chapter_publication_approval'])
  self.assertFalse(record['source_correction']['human_specialist_certification'])
  self.assertFalse((Y.parent/'005.yaml').exists())
 def test_two_acceptances_and_refined_note(self):
  hashes=[]
  for n in (1,2):
   p=P/f'review-pass{n}';review=json.loads((p/'review.json').read_text());provenance=json.loads((p/'provenance.json').read_text());inp=json.loads((p/'review-input.json').read_text())
   self.assertFalse(review['chapter_complete'])
   self.assertEqual([(r['reference'],r['verdict']) for r in review['reviews']],[('1 Enoch 26:6','accept')])
   self.assertEqual(inp[0]['source']['text'],yaml.safe_load(Y.read_text())['source']['text'])
   digest=hashlib.sha256((p/'review.json').read_bytes()).hexdigest();self.assertEqual(provenance['review_sha256'],digest);hashes.append(digest)
  app=json.loads((P/'application.json').read_text());self.assertEqual(app['review_sha256'],hashes)
  final=json.loads((P/'review-pass2/review-input.json').read_text())[0]['translation']
  self.assertEqual(yaml.safe_load(Y.read_text())['translation'],final)
if __name__=='__main__':unittest.main()
