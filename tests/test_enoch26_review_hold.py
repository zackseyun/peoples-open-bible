import hashlib,json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'sources/textual_restoration/applications/enoch_26_review_hold_20261017'
class Enoch26ReviewHold(unittest.TestCase):
 def test_review_scope_and_hold(self):
  state=json.loads((P/'status.json').read_text())
  for n in (1,2):
   review=json.loads((P/f'pass{n}/review.json').read_text())
   self.assertEqual([r['reference'] for r in review['reviews']],[f'1 Enoch 26:{i}' for i in range(1,7)])
   self.assertFalse(review['chapter_complete'])
  self.assertEqual(state['held_references'],['1 Enoch 26:3','1 Enoch 26:4'])
  self.assertEqual(state['disputed_references'],['1 Enoch 26:1','1 Enoch 26:2','1 Enoch 26:3'])
  for key in ('chapter_structure_complete','chapter_editorially_accepted','canonical_changed','graphic_published','full_108_goal_complete','human_specialist_certification'):self.assertFalse(state[key])
 def test_evidence_integrity(self):
  state=json.loads((P/'status.json').read_text())
  for rel,digest in state['files'].items():self.assertEqual(hashlib.sha256((P/rel).read_bytes()).hexdigest(),digest)
  for n in (1,2):
   provenance=json.loads((P/f'pass{n}/provenance.json').read_text())
   self.assertEqual(provenance['review_sha256'],hashlib.sha256((P/f'pass{n}/review.json').read_bytes()).hexdigest())
   self.assertFalse(provenance['canonical_translation_changed'])
if __name__=='__main__':unittest.main()
