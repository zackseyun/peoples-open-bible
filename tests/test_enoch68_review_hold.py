import hashlib,json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'sources/textual_restoration/applications/enoch_68_review_hold_20261017'
class Enoch68ReviewHold(unittest.TestCase):
 def test_five_unit_scope_and_hold(self):
  state=json.loads((P/'status.json').read_text())
  for n in (1,2):
   result=json.loads((P/f'pass{n}/review.json').read_text());self.assertFalse(result['chapter_complete'])
   self.assertEqual([r['reference'] for r in result['reviews']],[f'1 Enoch 68:{i}' for i in range(1,6)])
  self.assertEqual(state['held_references'],['1 Enoch 68:1','1 Enoch 68:3','1 Enoch 68:5'])
  for key in ('chapter_editorially_accepted','canonical_changed','graphic_published','full_108_goal_complete','human_specialist_certification'):self.assertFalse(state[key])
 def test_evidence_integrity(self):
  state=json.loads((P/'status.json').read_text())
  for rel,digest in state['files'].items():self.assertEqual(hashlib.sha256((P/rel).read_bytes()).hexdigest(),digest)
  for n in (1,2):
   p=P/f'pass{n}';v=json.loads((p/'provenance.json').read_text())
   self.assertEqual(v['review_sha256'],hashlib.sha256((p/'review.json').read_bytes()).hexdigest())
if __name__=='__main__':unittest.main()
