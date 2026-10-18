import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'sources/textual_restoration/applications'
class Enoch63And73ReviewHolds(unittest.TestCase):
 def test_scope_and_editorial_holds(self):
  expected={63:[5,6,8,10,12],73:[3,5,6,7,8]}
  for ch,nums in expected.items():
   p=ROOT/f'enoch_{ch}_review_hold_20261017';state=json.loads((p/'status.json').read_text())
   self.assertEqual(state['held_references'],[f'1 Enoch {ch}:{n}' for n in nums])
   for n in (1,2):
    result=json.loads((p/f'pass{n}/review.json').read_text())
    self.assertEqual([r['reference'] for r in result['reviews']],[f'1 Enoch {ch}:{i}' for i in range(1,state['expected_printed_units']+1)])
   for key in ('chapter_editorially_accepted','canonical_changed','graphic_published','full_108_goal_complete','human_specialist_certification'):self.assertFalse(state[key])
 def test_evidence_integrity(self):
  for ch in (63,73):
   p=ROOT/f'enoch_{ch}_review_hold_20261017';state=json.loads((p/'status.json').read_text())
   for rel,digest in state['files'].items():self.assertEqual(hashlib.sha256((p/rel).read_bytes()).hexdigest(),digest)
   for n in (1,2):
    q=p/f'pass{n}';v=json.loads((q/'provenance.json').read_text())
    self.assertEqual(v['review_sha256'],hashlib.sha256((q/'review.json').read_bytes()).hexdigest())
if __name__=='__main__':unittest.main()
