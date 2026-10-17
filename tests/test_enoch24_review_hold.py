import hashlib,json,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'sources/textual_restoration/applications/enoch_24_review_hold_20261017'
class Enoch24ReviewHold(unittest.TestCase):
 def test_entire_printed_chapter_is_not_editorially_accepted(self):
  state=json.loads((P/'status.json').read_text());result=json.loads((P/'pass2/review.json').read_text())
  self.assertTrue(result['chapter_complete']);self.assertEqual([r['reference'] for r in result['reviews']],[f'1 Enoch 24:{n}' for n in range(1,7)])
  self.assertEqual([r['verdict'] for r in result['reviews']],['accept','hold','hold','accept','accept','accept'])
  self.assertEqual(state['accepted_references'],['1 Enoch 24:1','1 Enoch 24:4','1 Enoch 24:5','1 Enoch 24:6'])
  self.assertEqual(state['held_references'],['1 Enoch 24:2','1 Enoch 24:3'])
  for key in ('chapter_editorially_accepted','canonical_changed','graphic_published','full_108_goal_complete','human_specialist_certification'):self.assertFalse(state[key])
 def test_preserved_review_inputs_results_and_image_hashes(self):
  state=json.loads((P/'status.json').read_text());
  for rel,digest in state['files'].items():self.assertEqual(hashlib.sha256((P/rel).read_bytes()).hexdigest(),digest)
  for n in (1,2):
   root=P/f'pass{n}';provenance=json.loads((root/'provenance.json').read_text());self.assertEqual(provenance['review_sha256'],hashlib.sha256((root/'review.json').read_bytes()).hexdigest());self.assertFalse(provenance['canonical_translation_changed'])
if __name__=='__main__':unittest.main()
