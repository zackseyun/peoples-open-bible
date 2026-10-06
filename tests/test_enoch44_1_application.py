import hashlib,json,re,subprocess,unittest
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator
from tools import audit_footnotes
from tools.enoch import verse_parser
ROOT=Path(__file__).resolve().parents[1];TARGET=ROOT/'translation/extra_canonical/1_enoch/044/001.yaml';RECEIPT=ROOT/'sources/textual_restoration/applications/enoch44_1.2026-10-06.v1.json'
BASE='21faf461feba9970d651bb70fa8d88aabeab43fe'
class Enoch441Application(unittest.TestCase):
 def setUp(self):
  self.d=yaml.safe_load(TARGET.read_text());self.r=json.loads(RECEIPT.read_text());self.before_bytes=subprocess.check_output(['git','show',f'{BASE}:{TARGET.relative_to(ROOT)}'],cwd=ROOT);self.before=yaml.safe_load(self.before_bytes)
 def test_exact_bounded_closure_and_witness_match(self):
  self.assertEqual(self.d['source']['text'],self.before['source']['text']+' ምስሌሆሙ፡');self.assertEqual(self.d['source']['pages'],[122,123]);rows,w=verse_parser.parse_chapter(44);norm=lambda s:''.join(s.split());self.assertEqual(norm(rows[0].text),norm(self.d['source']['text']))
  self.assertEqual(self.d['enoch_witnesses']['available_witnesses'][0]['text'],self.d['source']['text'])
 def test_plural_relation_and_uncertainty_not_silently_flattened(self):
  self.assertIn('along with them[a]',self.d['translation']['text']);self.assertNotIn('leave it',self.d['translation']['text']);note=self.d['translation']['footnotes'][0]['text'];self.assertIn('uncertain',note);self.assertIn('not a scientific account',note);self.assertEqual(audit_footnotes.audit_one(TARGET)['status'],'ok')
 def test_schema_and_old_reviews_are_not_current_certificates(self):
  Draft202012Validator(json.loads((ROOT/'schema/verse.schema.json').read_text())).validate(self.d);self.assertEqual(self.d['status'],'draft');self.assertNotIn('cross_check',self.d);self.assertTrue(all(not h['certifies_this_candidate'] for h in self.d['previous_reviews']));self.assertFalse(self.d['textual_comparison']['human_specialist_review'])
 def test_application_hashes_and_reference_unchanged(self):
  self.assertEqual(self.r['before_sha256'],hashlib.sha256(self.before_bytes).hexdigest());self.assertEqual(self.r['after_sha256'],hashlib.sha256(TARGET.read_bytes()).hexdigest());self.assertEqual(self.d['id'],self.before['id']);self.assertEqual(self.d['reference'],self.before['reference']);self.assertFalse(self.r['canonical_reference_changed']);self.assertTrue(self.r['graphic_publication_authorized'])
if __name__=='__main__':unittest.main()
