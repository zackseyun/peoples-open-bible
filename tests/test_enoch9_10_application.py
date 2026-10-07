import hashlib,json,re,subprocess,unittest
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator
from tools import audit_footnotes
from tools.enoch import verse_parser
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'sources/textual_restoration/applications/enoch9_10.2026-10-07.v1.json'
class Enoch910(unittest.TestCase):
 def setUp(self):self.r=json.loads(R.read_text());self.rows=self.r['applications']
 def get(self,c,v):return yaml.safe_load((ROOT/f'translation/extra_canonical/1_enoch/{c:03}/{v:03}.yaml').read_text())
 def test_complete_selected_counts_and_exact_source_except_header_note(self):
  norm=lambda s:''.join(s.split())
  for c,n in [(9,11),(10,22)]:
   paths=list((ROOT/f'translation/extra_canonical/1_enoch/{c:03}').glob('*.yaml'));self.assertEqual(len(paths),n);ps,_=verse_parser.parse_chapter(c);self.assertEqual([p.verse for p in ps],list(range(1,n+1)))
   for p in ps:
    expected=p.text.removesuffix(' 18') if (c,p.verse)==(9,11) else p.text
    self.assertEqual(norm(self.get(c,p.verse)['source']['text']),norm(expected))
  self.assertNotRegex(self.get(9,11)['source']['text'],r'[0-9]')
 def test_receipt_after_and_25before_hashes(self):
  self.assertEqual(len(self.rows),33);self.assertEqual(sum(r['before_sha256'] is not None for r in self.rows),25)
  for r in self.rows:
   f=ROOT/r['target'];self.assertEqual(hashlib.sha256(f.read_bytes()).hexdigest(),r['after_sha256'])
   if r['before_sha256']:
    b=subprocess.check_output(['/usr/bin/git','show',self.r['baseline_commit']+':'+r['target']],cwd=ROOT);self.assertEqual(hashlib.sha256(b).hexdigest(),r['before_sha256']);self.assertEqual(yaml.safe_load(b)['id'],yaml.safe_load(f.read_text())['id'])
 def test_schema_notes_and_provenance_are_truthful(self):
  validator=Draft202012Validator(json.loads((ROOT/'schema/verse.schema.json').read_text()))
  for r in self.rows:
   f=ROOT/r['target'];d=yaml.safe_load(f.read_text());validator.validate(d);self.assertIn(audit_footnotes.audit_one(f)['status'],['ok','no_footnotes']);self.assertEqual(d['status'],'draft');self.assertNotIn('cross_check',d);self.assertEqual(d['ai_draft']['model_id'],'codex-assistant');self.assertFalse(d['textual_comparison']['human_specialist_review']);self.assertTrue(all(not x['certifies_this_candidate'] for x in d['previous_reviews']));self.assertTrue(all('lexicon' not in x for x in d.get('lexical_decisions',[])))
 def test_model_mistranslations_are_not_silently_retained(self):
  self.assertNotIn('the King:',self.get(9,4)['translation']['text']);self.assertIn('make known',self.get(10,11)['translation']['text']);self.assertNotIn('bind',self.get(10,11)['translation']['text']);self.assertIn('[disclosed]',self.get(10,7)['translation']['text']);self.assertIn('ten thousand',self.get(10,19)['translation']['text']);self.assertIn(' and the offspring',self.get(10,15)['translation']['text']);self.assertNotIn('is condemned',self.get(10,14)['translation']['text'])
if __name__=='__main__':unittest.main()
