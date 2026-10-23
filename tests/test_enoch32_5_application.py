import hashlib,json,unittest,yaml
from pathlib import Path
from tools.enoch import verse_parser
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'sources/textual_restoration/applications/enoch_32_5_20261017'
Y=ROOT/'translation/extra_canonical/1_enoch/032/005.yaml'
class Enoch325Application(unittest.TestCase):
 def test_complete_individual_unit_and_chapter_hold(self):
  if (ROOT/'sources/textual_restoration/applications/enoch_full_repair_batch12_20261022/application.json').is_file():
   from tools.enoch.replay_32_pre_successor import replay
   self.assertTrue(replay('crosspage5')['passed']);return
  x=yaml.safe_load(Y.read_text());old=yaml.safe_load((P/'before.yaml').read_text());a=json.loads((P/'application.json').read_text())
  recovered={r.verse:r.text for r in verse_parser.parse_chapter(32)[0]}
  self.assertEqual(x['source']['text'],recovered[5]);self.assertNotEqual(old['source']['text'],x['source']['text'])
  self.assertIn('[beautiful and]',x['translation']['text'])
  self.assertEqual(x['source']['pages'],[110,112])
  self.assertEqual(x['enoch_witnesses']['available_witnesses'][0]['text'],x['source']['text'])
  self.assertEqual(a['before_sha256'],hashlib.sha256((P/'before.yaml').read_bytes()).hexdigest())
  self.assertEqual(a['canonical_sha256'],hashlib.sha256(Y.read_bytes()).hexdigest())
  for key in ('chapter_complete','graphic_publication_approved','app_published'):self.assertFalse(a[key])
  self.assertFalse((Y.parent/'006.yaml').exists())
 def test_two_bounded_reviews_accept_same_candidate(self):
  hashes=[]
  for n in (1,2):
   q=P/f'review-pass{n}';v=json.loads((q/'review.json').read_text());inp=json.loads((q/'review-input.json').read_text());provenance=json.loads((q/'provenance.json').read_text())
   self.assertFalse(v['chapter_complete'])
   self.assertEqual([(r['reference'],r['verdict']) for r in v['reviews']],[('1 Enoch 32:5','accept')])
   self.assertEqual(inp[0]['source']['text'],yaml.safe_load(Y.read_text())['source']['text'])
   d=hashlib.sha256((q/'review.json').read_bytes()).hexdigest();self.assertEqual(provenance['review_sha256'],d);hashes.append(d)
  self.assertEqual(json.loads((P/'application.json').read_text())['review_sha256'],hashes)
if __name__=='__main__':unittest.main()
