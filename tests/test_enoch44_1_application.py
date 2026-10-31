import hashlib,json,re,subprocess,unittest
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator
from tools import audit_footnotes
from tools.enoch import verse_parser, legacy44_evidence as legacy44
from tools.enoch import bounded_application as t
ROOT=Path(__file__).resolve().parents[1];TARGET=ROOT/'translation/extra_canonical/1_enoch/044/001.yaml';RECEIPT=ROOT/'sources/textual_restoration/applications/enoch44_1.2026-10-06.v1.json'
BASE='21faf461feba9970d651bb70fa8d88aabeab43fe'
class Enoch441Application(unittest.TestCase):
 def setUp(self):
  self.applied_bytes=legacy44.historical_bytes();self.d=yaml.safe_load(self.applied_bytes);self.r=json.loads(RECEIPT.read_text());self.before_bytes=subprocess.check_output(['git','show',f'{BASE}:{TARGET.relative_to(ROOT)}'],cwd=ROOT);self.before=yaml.safe_load(self.before_bytes)
 def test_exact_bounded_closure_and_witness_match(self):
  self.assertEqual(self.d['source']['text'],self.before['source']['text']+' ምስሌሆሙ፡');self.assertEqual(self.d['source']['pages'],[122,123]);rows,w=verse_parser.parse_ocr_chapter(44);norm=lambda s:''.join(s.split());self.assertEqual(norm(rows[0].text),norm(self.d['source']['text']))
  self.assertEqual(self.d['enoch_witnesses']['available_witnesses'][0]['text'],self.d['source']['text'])
 def test_plural_relation_and_uncertainty_not_silently_flattened(self):
  self.assertIn('along with them[a]',self.d['translation']['text']);self.assertNotIn('leave it',self.d['translation']['text']);note=self.d['translation']['footnotes'][0]['text'];self.assertIn('uncertain',note);self.assertIn('not a scientific account',note);self.assertEqual(audit_footnotes.audit_one(TARGET)['status'],'ok')
 def test_schema_and_old_reviews_are_not_current_certificates(self):
  Draft202012Validator(json.loads((ROOT/'schema/verse.schema.json').read_text())).validate(self.d);self.assertEqual(self.d['status'],'draft');self.assertNotIn('cross_check',self.d);self.assertTrue(all(not h['certifies_this_candidate'] for h in self.d['previous_reviews']));self.assertFalse(self.d['textual_comparison']['human_specialist_review'])
 def test_application_hashes_and_reference_unchanged(self):
  self.assertEqual(self.r['before_sha256'],hashlib.sha256(self.before_bytes).hexdigest());self.assertEqual(self.r['after_sha256'],hashlib.sha256(self.applied_bytes).hexdigest());self.assertEqual(self.d['id'],self.before['id']);self.assertEqual(self.d['reference'],self.before['reference']);self.assertFalse(self.r['canonical_reference_changed']);self.assertTrue(self.r['graphic_publication_authorized'])
 def test_current_target_is_original_or_exact_fresh_paired_successor(self):
  legacy44.verify_historical()
  if TARGET.read_bytes()==self.applied_bytes:return
  matches=[]
  for package in t.APPLICATIONS.glob('enoch_full_repair_batch*'):
   if not(package/'application.json').is_file():continue
   manifest=json.loads((package/'manifest.json').read_text())
   if manifest.get('supersedes_legacy44')==legacy44.declaration():matches.append(package)
  self.assertEqual(len(matches),1,'Changed44 needs one explicit installed legacy44 successor')
  package=matches[0];manifest=t.load_manifest(package)
  self.assertEqual(manifest['references'],[legacy44.REF])
  self.assertEqual(manifest['retirements'],[])
  self.assertEqual(t.verify(package,applied=True,check_corpus=True)['references'],[legacy44.REF])
  receipt=json.loads((package/'application.json').read_text())
  self.assertEqual(receipt['status'],'applied_verified')
  self.assertEqual(receipt['manifest_sha256'],t.sha((package/'manifest.json').read_bytes()))
  expected=dict(manifest['canonical_baseline_sha256']);expected['044/001.yaml']=manifest['files']['044-001.candidate.yaml']
  self.assertEqual(len(expected),966);self.assertEqual(receipt['canonical_after_sha256'],expected)
  rows,_=verse_parser.parse_chapter(44);current=yaml.safe_load(TARGET.read_text())
  self.assertEqual(rows[0].text,current['source']['text'])
  self.assertEqual(current['enoch_witnesses']['available_witnesses'][0]['text'],current['source']['text'])
if __name__=='__main__':unittest.main()
