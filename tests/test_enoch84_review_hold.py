import hashlib,json,unittest
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/'sources/textual_restoration/applications/enoch_84_20261017'
class Enoch84ReviewHold(unittest.TestCase):
 def test_whole_chapter_structure_does_not_approve_held_glyphs(self):
  state=json.loads((BASE/'status.json').read_text());first=json.loads((BASE/'pass1/review.json').read_text());second=json.loads((BASE/'pass2/review.json').read_text())
  self.assertTrue(first['chapter_complete'] and second['chapter_complete'])
  self.assertEqual([r['reference'] for r in second['reviews']],[f'1 Enoch 84:{v}' for v in range(1,7)])
  self.assertEqual([r['verdict'] for r in second['reviews']],['accept','hold','hold','accept','accept','accept'])
  self.assertEqual(state['second_pass_held_references'],['1 Enoch 84:2','1 Enoch 84:3'])
  for field in ('canonical_changed','translation_approved','graphic_art_published','full_108_goal_complete'):self.assertFalse(state[field])
 def test_all_review_artifacts_are_hash_bound(self):
  state=json.loads((BASE/'status.json').read_text())
  for rel,expected in state['files'].items():self.assertEqual(hashlib.sha256((BASE/rel).read_bytes()).hexdigest(),expected)
  self.assertEqual(state['second_pass_sha256'],hashlib.sha256((BASE/'pass2/review.json').read_bytes()).hexdigest())
  provenance=json.loads((BASE/'pass2/provenance.json').read_text());manifest=json.loads((BASE/'pass2/review-manifest.json').read_text())
  self.assertEqual(provenance['scan_image_sha256'],manifest['scan_sha256'])
  self.assertFalse(provenance['canonical_translation_changed'])
  self.assertFalse(provenance['human_specialist_certification'])
if __name__=='__main__':unittest.main()
