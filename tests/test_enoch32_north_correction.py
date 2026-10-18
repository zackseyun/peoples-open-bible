import hashlib,json,subprocess,unittest,yaml
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'sources/textual_restoration/applications/enoch_32_review_hold_20261017'
Y=ROOT/'translation/extra_canonical/1_enoch/032/001.yaml'
class Enoch32NorthCorrection(unittest.TestCase):
 def test_bounded_correction_not_publication(self):
  x=yaml.safe_load(Y.read_text());a=json.loads((P/'translation-correction.json').read_text())
  self.assertIn('these aromatics, toward the north',x['translation']['text'])
  self.assertNotIn('south',x['translation']['text'].lower())
  self.assertEqual(x['translation_correction']['scope'],'bounded_north_and_aromatics_only')
  self.assertFalse(x['translation_correction']['source_text_changed'])
  self.assertTrue(a['source_text_unchanged'])
  self.assertFalse(a['chapter_editorially_approved']);self.assertFalse(a['graphic_published'])
  self.assertEqual(a['corrected_sha256'],hashlib.sha256(Y.read_bytes()).hexdigest())
  self.assertFalse((Y.parent/'006.yaml').exists())
 def test_review_evidence_and_hold(self):
  state=json.loads((P/'status.json').read_text());self.assertEqual(state['held_references'],['1 Enoch 32:2','1 Enoch 32:3','1 Enoch 32:4','1 Enoch 32:6'])
  self.assertEqual(state['bounded_followup_verdict'],'hold')
  for n in (1,2):
   review=json.loads((P/f'pass{n}/review.json').read_text())
   self.assertEqual([r['reference'] for r in review['reviews']],[f'1 Enoch 32:{i}' for i in range(1,7)])
  for rel,digest in state['files'].items():self.assertEqual(hashlib.sha256((P/rel).read_bytes()).hexdigest(),digest)
if __name__=='__main__':unittest.main()
