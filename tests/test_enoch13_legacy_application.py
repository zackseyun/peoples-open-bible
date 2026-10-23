import hashlib,json,re,subprocess,unittest
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator
from tools import audit_footnotes
ROOT=Path(__file__).resolve().parents[1];PKG=ROOT/'sources/textual_restoration/applications/enoch13_legacy.2026-10-09.v1'
class Enoch13LegacyReview(unittest.TestCase):
 def setUp(self):self.r=json.loads((PKG/'application.json').read_text());self.rows=self.r['applications']
 def test_exact_three_records_and_unchanged_selected_source(self):
  if (ROOT/'sources/textual_restoration/applications/enoch_full_repair_batch17_20261023/application.json').is_file():
   # Replay the unchanged dated assertion, not its superseded installed payload.
   # Fresh paired current source/English/notes and old0-source-pass scope are separate.
   from tools.enoch.replay_13_first3_pre_successor import replay
   result=replay('bytes')
   self.assertEqual((result['tests_run'],result['skipped'],result['expected_failures']),(1,0,0))
   self.assertFalse(result['current_corpus_validated'])
   return
  self.assertEqual([r['reference'] for r in self.rows],['1 Enoch13:1','1 Enoch13:2','1 Enoch13:3'])
  for row in self.rows:
   p=ROOT/row['target'];old=subprocess.check_output(['/usr/bin/git','show',self.r['baseline_commit']+':'+row['target']],cwd=ROOT);d=yaml.safe_load(p.read_text())
   self.assertEqual(hashlib.sha256(old).hexdigest(),row['before_sha256'])
   self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),row['after_sha256'])
   self.assertEqual(d['source']['text'],yaml.safe_load(old)['source']['text'])
   self.assertEqual((PKG/f'013-{int(p.stem):03}.baseline.yaml').read_bytes(),old)
 def test_schema_marker_routing_and_current_review_truth(self):
  if (ROOT/'sources/textual_restoration/applications/enoch_full_repair_batch17_20261023/application.json').is_file():
   # Replay the unchanged dated assertion, not its superseded installed payload.
   # Fresh paired current source/English/notes and old0-source-pass scope are separate.
   from tools.enoch.replay_13_first3_pre_successor import replay
   result=replay('metadata')
   self.assertEqual((result['tests_run'],result['skipped'],result['expected_failures']),(1,0,0))
   self.assertFalse(result['current_corpus_validated'])
   return
  validator=Draft202012Validator(json.loads((ROOT/'schema/verse.schema.json').read_text()))
  for row in self.rows:
   p=ROOT/row['target'];d=yaml.safe_load(p.read_text());validator.validate(d)
   self.assertEqual(audit_footnotes.audit_one(p)['status'],'ok')
   self.assertEqual(d['status'],'draft');self.assertEqual(d['ai_draft']['model_id'],'codex-assistant')
   self.assertFalse(d['textual_comparison']['human_specialist_review'])
   self.assertNotIn('cross_check',d);self.assertNotIn('revision_pass',d)
   self.assertTrue(all('lexicon' not in v for v in d['lexical_decisions']))
 def test_respite_is_not_merged_with_petition_or_mercy(self):
  if (ROOT/'sources/textual_restoration/applications/enoch_full_repair_batch17_20261023/application.json').is_file():
   # Replay the unchanged dated assertion, not its superseded installed payload.
   # Fresh paired current source/English/notes and old0-source-pass scope are separate.
   from tools.enoch.replay_13_first3_pre_successor import replay
   result=replay('respite')
   self.assertEqual((result['tests_run'],result['skipped'],result['expected_failures']),(1,0,0))
   self.assertFalse(result['current_corpus_validated'])
   return
  d=yaml.safe_load((ROOT/'translation/extra_canonical/1_enoch/013/002.yaml').read_text())
  self.assertIn('no respite[a] or petition[b]',d['translation']['text'])
  self.assertNotIn('mercy',d['translation']['text'])
  self.assertEqual(d['lexical_decisions'][0]['chosen'],'respite')
  self.assertEqual(d['lexical_decisions'][1]['chosen'],'petition')
  for x in d['lexical_decisions'][:2]:
   self.assertIn('Dmain',x['consulted_lexicon_entry']['sense']);self.assertIn('4b1cf257',x['consulted_lexicon_entry']['url'])
 def test_first_and_third_main_words_retained(self):
  if (ROOT/'sources/textual_restoration/applications/enoch_full_repair_batch17_20261023/application.json').is_file():
   # Replay the unchanged dated assertion, not its superseded installed payload.
   # Fresh paired current source/English/notes and old0-source-pass scope are separate.
   from tools.enoch.replay_13_first3_pre_successor import replay
   result=replay('words')
   self.assertEqual((result['tests_run'],result['skipped'],result['expected_failures']),(1,0,0))
   self.assertFalse(result['current_corpus_validated'])
   return
  clean=lambda s:re.sub(r'\[[a-z]\]','',s)
  for v in [1,3]:
   old=yaml.safe_load((PKG/f'013-{v:03}.baseline.yaml').read_text())
   current=yaml.safe_load((ROOT/f'translation/extra_canonical/1_enoch/013/{v:03}.yaml').read_text())
   self.assertEqual(clean(old['translation']['text']),clean(current['translation']['text']))
if __name__=='__main__':unittest.main()
