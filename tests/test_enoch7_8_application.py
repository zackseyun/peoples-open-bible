import hashlib,json,subprocess,unittest
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator
from tools import audit_footnotes
from tools.enoch import verse_parser
ROOT=Path(__file__).resolve().parents[1];RECEIPT=ROOT/'sources/textual_restoration/applications/enoch7_8.2026-10-06.v1.json'
class Enoch78(unittest.TestCase):
 def setUp(self):self.r=json.loads(RECEIPT.read_text());self.rows=self.r['applications']
 def test_complete_selected_counts_and_exact_source(self):
  norm=lambda s:''.join(s.split())
  for c,n in [(7,6),(8,4)]:
   paths=list((ROOT/f'translation/extra_canonical/1_enoch/{c:03}').glob('*.yaml'));self.assertEqual(len(paths),n)
   parsed,_=verse_parser.parse_chapter(c);texts={r.verse:r.text for r in parsed};self.assertEqual(sorted(texts),list(range(1,n+1)))
   for f in paths:self.assertEqual(norm(yaml.safe_load(f.read_text())['source']['text']),norm(texts[int(f.stem)]))
 def test_application_bytes_and_only_two_existing_replacements(self):
  self.assertEqual(len(self.rows),10);self.assertEqual(sum(r['before_sha256'] is not None for r in self.rows),2)
  for r in self.rows:
   p=ROOT/r['target'];self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),r['after_sha256'])
   if r['before_sha256']:
    before=subprocess.check_output(['git','show',f"{self.r['baseline_commit']}:{r['target']}"],cwd=ROOT);self.assertEqual(hashlib.sha256(before).hexdigest(),r['before_sha256']);self.assertEqual(yaml.safe_load(before)['id'],yaml.safe_load(p.read_text())['id'])
 def test_schema_notes_and_truthful_provenance(self):
  validator=Draft202012Validator(json.loads((ROOT/'schema/verse.schema.json').read_text()))
  for r in self.rows:
   p=ROOT/r['target'];d=yaml.safe_load(p.read_text());validator.validate(d);self.assertEqual(audit_footnotes.audit_one(p)['status'],'ok');self.assertEqual(d['status'],'draft');self.assertNotIn('cross_check',d);self.assertFalse(d['textual_comparison']['human_specialist_review']);self.assertTrue(all(not x['certifies_this_candidate'] for x in d['previous_reviews']))
   self.assertTrue(all('lexicon' not in x for x in d.get('lexical_decisions',[])))
 def test_critical_and_uncertain_readings_not_harmonized(self):
  get=lambda c,v:yaml.safe_load((ROOT/f'translation/extra_canonical/1_enoch/{c:03}/{v:03}.yaml').read_text())
  self.assertIn('†',get(7,3)['source']['text']);self.assertIn('three thousand cubits',get(7,2)['translation']['text']);self.assertIn('behind',get(8,1)['translation']['text']);self.assertIn('singular',get(8,3)['translation']['footnotes'][2]['text'])
if __name__=='__main__':unittest.main()
