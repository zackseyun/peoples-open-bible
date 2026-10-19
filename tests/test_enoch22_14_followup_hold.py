import hashlib,json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'sources/textual_restoration/applications/enoch_22_14_followup_hold_20261018'
class Enoch2214FollowupHold(unittest.TestCase):
 def test_new_hold_overrides_old_acceptance(self):
  x=json.loads((P/'status.json').read_text());r=json.loads((P/'highres-followup/review.json').read_text())
  self.assertEqual(x['reference'],'1 Enoch 22:14');self.assertEqual(r['reviews'][0]['verdict'],'hold')
  for key in ('canonical_changed','chapter_complete','graphic_published','human_specialist_certification','manuscript_witness_certification'):self.assertFalse(x[key])
 def test_evidence_integrity(self):
  x=json.loads((P/'status.json').read_text())
  for rel,digest in x['files'].items():self.assertEqual(hashlib.sha256((P/rel).read_bytes()).hexdigest(),digest)
  q=P/'highres-followup';v=json.loads((q/'provenance.json').read_text())
  self.assertEqual(v['review_sha256'],hashlib.sha256((q/'review.json').read_bytes()).hexdigest())
if __name__=='__main__':unittest.main()
