"""Exact fresh13:6 source/English/explanations supersede only its metadata preimage."""
import json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t,selected_edition_sources as sources,historical_evidence as historical
from tools.enoch.current_evidence import verify_current
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader
P=t.APPLICATIONS/'enoch_full_repair_batch33_20261027';M=t.APPLICATIONS/'enoch_witness_metadata13_14_20261026';SHA='113b61f03934b82eca38023d0d4eb62bb3a78b0c454013d3f12bb4210d6296cc';INPUT='0614fc4a79b0dd44a9214942cd684545bcfbad7f8533204c49f86659d840524c';REF='1 Enoch 13:6';BASE='f125fb680b4107aea28a4cc49eb7182c1ced596c'
def record():return yaml.load((t.TRANSLATION/'013/006.yaml').read_bytes(),Loader=t.LOADER)
def assert_current_batch33(case):
 case.assertEqual(t.sha((P/'manifest.json').read_bytes()),SHA);m=t.load_manifest(P);case.assertEqual(m['references'],[REF]);prior=json.loads((M/'application.json').read_text());case.assertEqual(m['canonical_baseline_sha256'],prior['canonical_after_sha256']);expected=dict(m['canonical_baseline_sha256']);expected['013/006.yaml']=m['files']['013-006.candidate.yaml'];r=json.loads((P/'application.json').read_text());case.assertEqual(r['canonical_after_sha256'],expected);case.assertEqual(t.corpus_hashes(),expected);case.assertEqual(t.verify(P,applied=True,check_corpus=True)['references'],[REF]);case.assertEqual(len(expected),966);case.assertEqual(m['source_baseline_git_commit'],BASE);return m,expected
class Batch33Test(unittest.TestCase):
 def test_exact966_chain_and_only_one_existing_change(self):
  m,after=assert_current_batch33(self);self.assertEqual({k for k in after if after[k]!=m['canonical_baseline_sha256'][k]},{'013/006.yaml'});self.assertEqual(m['retirements'],[])
 def test_actual_intermediate_git_preimage_not_claimed_published_source(self):
  import subprocess
  m=t.load_manifest(P);raw=subprocess.check_output(['git','show',BASE+':translation/extra_canonical/1_enoch/013/006.yaml'],cwd=t.ROOT);self.assertEqual(t.sha(raw),'273c8e5eb3ee14cb1987b43fd4ae2bd64e9e54a58c4ac19b2a2fe9ba07a97a0e');self.assertEqual(m['canonical_baseline_sha256']['013/006.yaml'],t.sha(raw))
 def test_new_full_pair_exact_input_not_metadata_votes(self):
  m=t.load_manifest(P);bindings=m['review_bindings'][REF];self.assertEqual(len({b['reviewer_id']for b in bindings}),2);self.assertEqual({m['files'][b['input']]for b in bindings},{INPUT});rows=t.reviewed_rows(P,bindings,REF,m['files']);self.assertEqual(rows[0],rows[1]);self.assertEqual(rows[0]['translation'],record()['translation']);self.assertEqual(record()['source']['text'],rows[0]['source']['text'])
 def test_actual_memorial_tawe_and_nun_haut_not_old_alf_sat_guess(self):
  d=record();old=yaml.load((M/'013-006.candidate.yaml').read_bytes(),Loader=t.LOADER);self.assertIn('ትዝካረ',old['source']['text']);self.assertIn('ወአስተ',old['source']['text']);self.assertIn('ተዝካረ',d['source']['text']);self.assertTrue(d['source']['text'].endswith('ወኑሐተ።'));self.assertNotIn('ኑኀተ',d['source']['text']);self.assertEqual(d['source']['text'].count('*'),1);self.assertEqual(d['source']['confidence'],'low');self.assertTrue(d['source']['transcription_uncertainties'])
 def test_forbearance_request_not_unspecified_extension_or_unprinted_grantpassive(self):
  d=record();text=d['translation']['text'];self.assertIn('concerning their spirit and their deeds individually',text);self.assertIn('request that forgiveness and forbearance might be theirs',text);self.assertNotIn('be granted',text);self.assertNotIn('extension',text);self.assertEqual(len(d['translation']['footnotes']),2);self.assertIn('delay of punishment',d['translation']['footnotes'][1]['text'])
 def test_exact_metadata_owner_and_unchanged_other_five_projections(self):
  from tools.enoch import witness_projection_metadata as projection
  m=t.load_manifest(P);old=projection.read_manifest();self.assertEqual(m['supersedes'],{REF:{'package':M.name,'manifest_sha256':projection.MANIFEST_SHA,'candidate_sha256':old['cases'][REF]['candidate_sha256']}});proof=verify_current(M);self.assertIn({'reference':REF,'superseded_by':P.name},proof['reviewed_supersessions']);self.assertNotIn((13,6),historical.load_all_current())
  for ref,case in old['cases'].items():
   if ref!=REF:self.assertEqual(t.sha((t.TRANSLATION/('%03d/%03d.yaml'%t.parse_ref(ref))).read_bytes()),case['candidate_sha256'])
 def test_clean_current_record_drops_stale_lexical_objects_without_rewriting_history(self):
  self.assertNotIn('lexical_decisions',record());old=yaml.load((M/'013-006.candidate.yaml').read_bytes(),Loader=t.LOADER);self.assertEqual(old['lexical_decisions'][5]['source_word'],'እሱተ');self.assertEqual(record()['review_history'][0]['sha256'],t.sha((M/'013-006.candidate.yaml').read_bytes()))
 def test_only_individual_source_ingress_and_exact_quiet_details(self):
  d=record();reg=sources.registry_data();self.assertEqual(reg['units']['13:6'],P.name);self.assertNotIn('13',reg['chapters']);self.assertFalse(d['source_correction']['selected_edition_chapter_reviewed']);out=reader._export_record_verse(6,d);self.assertEqual(out['footnote_review'],reader.PROTOCOL);self.assertEqual(out['footnotes'],d['translation']['footnotes']);self.assertEqual(out['source_critical']['text'],d['source']['text']);self.assertEqual(build_enoch_prompt(13,6).source_payload['text'],d['source']['text'])
 def test_current_parser_uses_exact_new_source_not_retained_raw_ocr(self):
  from tools.enoch import verse_parser
  d=record();row,_=verse_parser.load_verse(13,6);self.assertEqual(row.text,d['source']['text']);self.assertEqual(row.source_confidence,'low');self.assertIn(P.name,row.chapter_file)
  raw,_=verse_parser.parse_ocr_chapter(13);self.assertTrue(next(r.text for r in raw if r.verse==6).endswith('ወአስተ።'));self.assertTrue(row.text.endswith('ወኑሐተ።'))
 def test_rehashed_source_english_and_explanation_tampering_rejected(self):
  for mode in('source','English','note'):
   with self.subTest(mode=mode),tempfile.TemporaryDirectory()as directory:
    p=Path(directory)/'package';shutil.copytree(P,p);file=p/'013-006.candidate.yaml';d=yaml.load(file.read_bytes(),Loader=t.LOADER)
    if mode=='source':d['source']['text']=d['source']['text'].replace('ኑሐተ','ኑኀተ')
    elif mode=='English':d['translation']['text']=d['translation']['text'].replace('forbearance','extension')
    else:d['translation']['footnotes'][0]['text']='Unreviewed claim.'
    file.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False));m=json.loads((p/'manifest.json').read_text());m['files'][file.name]=t.sha(file.read_bytes());(p/'manifest.json').write_text(json.dumps(m))
    with self.assertRaises(ValueError):t.verify(p,evidence_only=True)
 def test_no_new_unit_count_or_chapter_credit_and_actual_CI_git_fetch(self):
  from tools.enoch.full_repair_progress import build
  r=build();self.assertEqual(r['canonical_file_count'],966);self.assertEqual(r['current_units_with_imported_review_evidence'],478);self.assertEqual(len(r['chapters_with_complete_imported_selected_edition_review']),36);self.assertEqual(r['evidence_inventory_warnings'],[]);self.assertFalse(r['completion_proven']);workflow=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text();self.assertIn('git fetch --no-tags --depth=1 origin '+BASE,workflow);self.assertIn("python -m unittest discover -s tests -p 'test_enoch_full_repair_batch33.py'",workflow)
