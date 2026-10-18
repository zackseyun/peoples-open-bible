import hashlib,json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'sources/textual_restoration/applications/enoch_21_9_followup_hold_20261017'
class Enoch219FollowupHold(unittest.TestCase):
 def test_disagreement_is_not_application(self):
  state=json.loads((P/'status.json').read_text());self.assertEqual(state['reference'],'1 Enoch 21:9')
  self.assertEqual(state['review_verdicts'],['revise','accept','revise'])
  for n,verdict in enumerate(state['review_verdicts'],1):
   result=json.loads((P/f'pass{n}/review.json').read_text());self.assertFalse(result['chapter_complete'])
   self.assertEqual([(r['reference'],r['verdict']) for r in result['reviews']],[('1 Enoch 21:9',verdict)])
  for key in ('canonical_changed','chapter_complete','graphic_published','human_specialist_certification','manuscript_witness_certification'):self.assertFalse(state[key])
 def test_evidence_integrity(self):
  state=json.loads((P/'status.json').read_text())
  for rel,digest in state['files'].items():self.assertEqual(hashlib.sha256((P/rel).read_bytes()).hexdigest(),digest)
  for n in (1,2,3):
   p=P/f'pass{n}';v=json.loads((p/'provenance.json').read_text())
   self.assertEqual(v['review_sha256'],hashlib.sha256((p/'review.json').read_bytes()).hexdigest())
if __name__=='__main__':unittest.main()
