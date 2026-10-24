import hashlib,json,unittest,yaml
from pathlib import Path
from tools.enoch import verse_parser
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'sources/textual_restoration/applications/enoch_26_5_20261017'
Y=ROOT/'translation/extra_canonical/1_enoch/026/005.yaml'
class Enoch265Application(unittest.TestCase):
 def test_individual_unit_scan_correction_and_chapter_hold(self):
  record=yaml.safe_load(Y.read_text());app=json.loads((P/'application.json').read_text())
  recovered={r.verse:r.text for r in verse_parser.parse_chapter(26)[0]}
  self.assertEqual(record['source']['text'],recovered[5].replace('ኢ*ይትከል','ኢይትከል'))
  self.assertEqual(record['reference'],'1 Enoch 26:5')
  self.assertIn('no tree',record['translation']['text'])
  for key in ('chapter_complete','graphic_publication_approved','app_published'):self.assertFalse(app[key])
  # The old complete-byte assertion stays on its actual original Git blob;
  # current metadata-only differences require a separately verified exact delta.
  from tools.enoch import metadata26_evidence as followup
  proof=followup.verify_current(P);self.assertTrue(proof['canonical_targets_checked'])
  case=followup.read_index()['cases'][record['reference']]
  import subprocess
  original=subprocess.check_output(['git','show',case['applied_commit']+':'+app['canonical_file']],cwd=ROOT)
  self.assertEqual(app['canonical_sha256'],hashlib.sha256(original).hexdigest())
  self.assertIn('no[b] tree',yaml.safe_load(original)['translation']['text'])
  self.assertEqual(proof['reviewed_supersessions'][0]['superseded_by'],'enoch_full_repair_batch22_20261024')
  self.assertFalse(record['source_correction']['chapter_publication_approval'])
  self.assertFalse(record['source_correction']['human_specialist_certification'])
  self.assertNotEqual(yaml.safe_load(Y.parent.joinpath('004.yaml').read_text())['source']['text'],recovered[4])
 def test_two_bounded_acceptances_same_candidate(self):
  hashes=[]
  for n in (1,2):
   p=P/f'review-pass{n}';review=json.loads((p/'review.json').read_text());provenance=json.loads((p/'provenance.json').read_text());inp=json.loads((p/'review-input.json').read_text())
   self.assertFalse(review['chapter_complete'])
   self.assertEqual([(r['reference'],r['verdict']) for r in review['reviews']],[('1 Enoch 26:5','accept')])
   from tools.enoch import metadata26_evidence as history
   originals,_=history._originals(history.read_index())
   self.assertEqual(inp[0]['source']['text'],originals['1 Enoch 26:5']['source']['text'])
   digest=hashlib.sha256((p/'review.json').read_bytes()).hexdigest();self.assertEqual(provenance['review_sha256'],digest);hashes.append(digest)
  app=json.loads((P/'application.json').read_text());self.assertEqual(app['review_sha256'],hashes)
if __name__=='__main__':unittest.main()
