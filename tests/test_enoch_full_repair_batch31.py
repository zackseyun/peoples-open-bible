"""Exact54:1/55:2 correction pair, not a generic historical-hold waiver."""
import json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t,selected_edition_sources as sources
from tools.enoch.current_evidence import verify_current
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader
P=t.APPLICATIONS/'enoch_full_repair_batch31_20261025';PREVIOUS=t.APPLICATIONS/'enoch_full_repair_batch30_20261025';OLD=t.APPLICATIONS/'enoch_full_repair_batch08_20261022';SHA='61249360ac72fadc13d650c67f42ab47c443d0dff96e2bd4262ef4c7eb496d21';REFS=['1 Enoch 54:1','1 Enoch 55:2'];INPUTS=['cc64e61fc5c6b499106253b1a2f1d3c444bccee2b139fe14055fce3a36054d31','c46ada44007adebb04402d324574ad4693483d0a8144bd1ecc9335ac9b8e8340']
def record(c,v):return yaml.load((t.TRANSLATION/f'{c:03d}/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)
def assert_current_batch31(case):
 case.assertEqual(t.sha((P/'manifest.json').read_bytes()),SHA);m=t.load_manifest(P);case.assertEqual(m['references'],REFS)
 previous=json.loads((PREVIOUS/'application.json').read_text());case.assertEqual(m['canonical_baseline_sha256'],previous['canonical_after_sha256']);case.assertEqual(len(m['canonical_baseline_sha256']),966)
 expected=dict(m['canonical_baseline_sha256'])
 for ref in REFS:
  c,v=t.parse_ref(ref);expected[f'{c:03d}/{v:03d}.yaml']=m['files'][f'{c:03d}-{v:03d}.candidate.yaml']
 receipt=json.loads((P/'application.json').read_text());case.assertEqual(receipt['canonical_after_sha256'],expected);case.assertEqual(t.corpus_hashes(),expected);case.assertEqual(t.verify(P,applied=True,check_corpus=True)['references'],REFS)
 case.assertEqual(m['retirements'],[]);case.assertEqual(receipt['snapshot_file_count'],966);case.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application']);return m,expected
class Batch31Test(unittest.TestCase):
 def test_exact_current966_postmap_only_two_existing_changes(self):
  m,after=assert_current_batch31(self);self.assertEqual({k for k in after if after[k]!=m['canonical_baseline_sha256'][k]},{'054/001.yaml','055/002.yaml'});self.assertEqual(m['source_baseline_git_commit'],'b86c6a52cebc16c554f5b0192572fca9cf05e1c1')
 def test_exact_B08_owner_and_preimage_no_false55_supersession(self):
  m=t.load_manifest(P);old=t.load_manifest(OLD);self.assertEqual(set(m['supersedes']),{'1 Enoch 54:1'});self.assertEqual(m['supersedes']['1 Enoch 54:1'],{'package':OLD.name,'manifest_sha256':t.sha((OLD/'manifest.json').read_bytes()),'candidate_sha256':old['files']['054-001.candidate.yaml']})
  self.assertEqual(m['canonical_baseline_sha256']['054/001.yaml'],old['files']['054-001.candidate.yaml']);self.assertNotIn('1 Enoch 55:2',old['references']);self.assertIn({'reference':'1 Enoch 54:1','superseded_by':P.name},verify_current(OLD)['reviewed_supersessions'])
 def test_actual_final_pair_same_full_payload_new_hashes_not_old_votes(self):
  m=t.load_manifest(P)
  for ref,digest in zip(REFS,INPUTS):
   bindings=m['review_bindings'][ref];self.assertEqual(len({b['reviewer_id']for b in bindings}),2);rows=t.reviewed_rows(P,bindings,ref,m['files']);self.assertEqual(rows[0],rows[1]);self.assertEqual({m['files'][b['input']]for b in bindings},{digest});c,v=t.parse_ref(ref);self.assertEqual(record(c,v)['translation'],rows[0]['translation']);self.assertEqual(record(c,v)['source']['confidence'],'low');self.assertTrue(rows[0]['source']['transcription_uncertainties'])
 def test_541_look_turn_other_geographic_face_and_circumstantial_fire(self):
  d=record(54,1);old=yaml.load((OLD/'054-001.candidate.yaml').read_bytes(),Loader=t.LOADER);self.assertTrue(d['source']['text'].startswith('ወነጸርኩ፡'));self.assertIn('ካልእ፡ ገጸ፡ ምድር',d['source']['text']);self.assertIn('ቆላ፡ ዕሙቀ',d['source']['text']);self.assertTrue(old['source']['text'].startswith('ወገጽኩ፡'));self.assertEqual(d['translation']['text'],'I looked and turned to another part of the earth, and there I saw a deep valley with fire burning.[a]');self.assertNotIn('ኀበ',d['source']['text'])
 def test_552_main_plural_not_singular_apparatus_and_jussive_person(self):
  d=record(55,2);self.assertIn('በሰማያት፡ ወይኩን',d['source']['text']);self.assertIn('in the heavens',d['translation']['text']);self.assertIn('caused a sign to circle',d['translation']['text']);self.assertIn('Let there be faithfulness between me and them',d['translation']['text']);self.assertRegex(d['source']['note'].lower(),r'third.person.*jussive');self.assertIn('the singular form is recorded as a variant in the printed apparatus',d['translation']['footnotes'][0]['text']);self.assertTrue(d['source']['text'].endswith('።]'))
 def test_raw55_v2_whole_holds_and_main_variant_mistake_not_erased(self):
  raw=json.loads((P/'history/batch31-final-whole-author-20261025/ch55-2/author-review.json').read_text());self.assertEqual(next(x['verdict']for x in t.review_entries(raw)if x['reference']=='1 Enoch 55:2'),'hold')
  old=json.loads((P/'history/batch31-final-input-metadata-drafts-v1/055-002.review-input.json').read_text())[0];self.assertIn('በሰማይ፡ ወይኩን',old['source']['text']);self.assertEqual(t.sha((P/'history/ch55-unit2-new-exact-peer-20261025/independent-review.json').read_bytes()),'df98bb483f29ecabe176cabf5731e740cb8e40782b475da121a7e52af8c273a9')
 def test_compatible_serializers_copy_raw_explicit_decisions_and_add_zero_passes(self):
  for group,role,rawpath,pvpath,mapkey,digest in [('ch54-1','independent','history/ch54-unit1-new-exact-peer-20261025/new-informed-resume-v2/independent-review.json','history/ch54-unit1-new-exact-peer-20261025/new-informed-resume-v2/provenance.json','actualscan_image_sha256','8833106add7a926d86eb1bc50c6d936e6d9e3c1cf02671b1e459300847e31fbe'),('ch55-2','author','history/ch55-unit2-corrective-author-v3-20261025/author-review.json','history/ch55-unit2-corrective-author-v3-20261025/author-review.pv.json','scan_image_sha256','02a8d0b8d9b77d1f21702284c2d9d918ffcc907ceff34c8b64449d4c73c6d177')]:
   raw=json.loads((P/rawpath).read_text());oldpv=json.loads((P/pvpath).read_text());review=json.loads((P/f'final/{group}/{role}-review.json').read_text());pv=json.loads((P/f'final/{group}/{role}-provenance.json').read_text());self.assertEqual(t.sha((P/rawpath).read_bytes()),digest);self.assertTrue(raw['decision'].lower()in('accept','approve'));self.assertEqual(review['raw_review_sha256'],digest);self.assertEqual(pv['reviewer_id'],oldpv['reviewer_id']);self.assertEqual(pv['scan_image_sha256'],oldpv[mapkey]);self.assertEqual(pv['review_sha256'],t.sha((P/f'final/{group}/{role}-review.json').read_bytes()));self.assertTrue(pv['serialization_only'])
   for key,value in pv.items():
    if 'extra_'in key:self.assertEqual(value,0)
 def test_source_unit_registration_only_and_all_neighbor_bytes_preserved(self):
  m,after=assert_current_batch31(self);reg=sources.registry_data();self.assertEqual(m['chapter_inventories'],[]);self.assertEqual(m['source_only_count_inventories'],[])
  for c,v in((54,1),(55,2)):
   self.assertEqual(reg['units'][f'{c}:{v}'],P.name);self.assertNotIn(str(c),reg['chapters']);self.assertFalse(record(c,v)['source_correction']['selected_edition_chapter_reviewed'])
  self.assertNotIn('55:4',reg['units'])
  for c,v in((54,2),(54,8),(55,1),(55,3),(55,4)):
   rel=f'{c:03d}/{v:03d}.yaml';self.assertEqual(after.get(rel),m['canonical_baseline_sha256'].get(rel))
 def test_exact_export_source_prompt_and_quiet_explanations(self):
  for c,v in((54,1),(55,2)):
   d=record(c,v);out=reader._export_record_verse(v,d);self.assertEqual(out['text'],d['translation']['text']);self.assertEqual(out['footnotes'],d['translation']['footnotes']);self.assertEqual(out['footnote_review'],reader.PROTOCOL);self.assertEqual(out['source_critical']['text'],d['source']['text']);self.assertEqual(build_enoch_prompt(c,v).source_payload['text'],d['source']['text'])
 def test_rehashed_source_or_english_or_scope_tampering_cannot_get_review(self):
  for mode in('singular','removed_negative','raised_confidence','missing_qualifier'):
   with self.subTest(mode=mode),tempfile.TemporaryDirectory()as directory:
    q=Path(directory)/'package';shutil.copytree(P,q);f=q/'055-002.candidate.yaml';d=yaml.load(f.read_bytes(),Loader=t.LOADER)
    if mode=='singular':d['source']['text']=d['source']['text'].replace('በሰማያት','በሰማይ')
    elif mode=='removed_negative':d['translation']['text']=d['translation']['text'].replace('would not do','would do')
    elif mode=='raised_confidence':d['source']['confidence']='medium'
    else:d['source']['transcription_uncertainties']=[]
    f.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False));m=json.loads((q/'manifest.json').read_text());m['files'][f.name]=t.sha(f.read_bytes());(q/'manifest.json').write_text(json.dumps(m))
    with self.assertRaises(ValueError):t.verify(q,evidence_only=True)
 def test_strict_current_helper_is_not_a_generic_historical_hold_waiver(self):
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);shutil.copytree(t.TRANSLATION,root/'corpus');target=root/'corpus/055/002.yaml';target.write_bytes(target.read_bytes().replace('በሰማያት'.encode(),'በሰማይ'.encode()))
   with patch.object(t,'TRANSLATION',root/'corpus'):
    with self.assertRaises(AssertionError):assert_current_batch31(self)
 def test_real_one_review_increment_not_complete_chapter_or_book(self):
  from tools.enoch.full_repair_progress import build
  d=build();self.assertEqual(d['canonical_file_count'],966);self.assertEqual(d['current_units_with_imported_review_evidence'],477);self.assertEqual(len(d['chapters_with_complete_imported_selected_edition_review']),36);self.assertEqual(len(d['chapters_with_imported_paired_count_inventory']),108);self.assertEqual(d['evidence_inventory_warnings'],[]);self.assertFalse(d['completion_proven'])

 def test_CI_fetches_actual_published_preimage_and_runs_new_guards(self):
  workflow=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text()
  self.assertIn('git fetch --no-tags --depth=1 origin b86c6a52cebc16c554f5b0192572fca9cf05e1c1',workflow)
  for pattern in ['test_enoch_full_repair_batch31.py','test_enoch_review_input_preflight.py']:self.assertIn("python -m unittest discover -s tests -p '"+pattern+"'",workflow)
