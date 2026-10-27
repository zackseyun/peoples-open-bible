"""Whole source repairs, not a broad waiver of historical source uncertainty."""
import json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t,selected_edition_sources as sources,verse_parser
from tools.enoch.current_evidence import verify_current
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader
P=t.APPLICATIONS/'enoch_full_repair_batch32_20261026'
PREVIOUS=t.APPLICATIONS/'enoch_full_repair_batch31_20261025'
SHA='9a9e769fb163d592a51e46479d5c6075796abab0e923d80a9529ef6b87965041'
REFS=['1 Enoch 18:8','1 Enoch 54:8','1 Enoch 84:2']
INPUTS={'1 Enoch 18:8':'3adb5bfa39eb7d159141c6f8b08a63aec855a4044ec48d47bc8b2000fd5f280d','1 Enoch 54:8':'6fa6285d51cd488393d0887a5b50cf50755151bd4dd65252f86e36e69f983210','1 Enoch 84:2':'139b59ffd901cd8f29b290f03ba5fe54f74f3a56c8bb150b6ce1da2c4ce5cc13'}
def record(c,v):return yaml.load((t.TRANSLATION/f'{c:03d}/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)
def assert_current_batch32(case):
 case.assertEqual(t.sha((P/'manifest.json').read_bytes()),SHA);m=t.load_manifest(P);case.assertEqual(m['references'],REFS)
 prior=json.loads((PREVIOUS/'application.json').read_text());case.assertEqual(m['canonical_baseline_sha256'],prior['canonical_after_sha256']);case.assertEqual(len(m['canonical_baseline_sha256']),966)
 expected=dict(m['canonical_baseline_sha256'])
 for ref in REFS:
  c,v=t.parse_ref(ref);expected[f'{c:03d}/{v:03d}.yaml']=m['files'][f'{c:03d}-{v:03d}.candidate.yaml']
 receipt=json.loads((P/'application.json').read_text());case.assertEqual(receipt['canonical_after_sha256'],expected);case.assertEqual(receipt['snapshot_file_count'],966);case.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
 case.assertEqual(t.verify(P,applied=True)['references'],REFS)
 metadata=t.APPLICATIONS/'enoch_witness_metadata13_14_20261026'
 if (metadata/'application.json').is_file():
  from tools.enoch import witness_projection_metadata as projection
  case.assertEqual(projection.read_manifest()['canonical_baseline_sha256'],expected);case.assertEqual(projection.verify(applied=True)['snapshot_file_count'],966)
 else:case.assertEqual(t.corpus_hashes(),expected)
 return m,expected
class Batch32Test(unittest.TestCase):
 def test_exact966_preimage_and_only_named_existing_source_changes(self):
  m,after=assert_current_batch32(self);self.assertEqual({k for k in after if after[k]!=m['canonical_baseline_sha256'][k]},{'%03d/%03d.yaml'%t.parse_ref(r)for r in REFS});self.assertEqual(m['source_baseline_git_commit'],'6d750894702ca05e20c50b75919c15916ca3fcb8');self.assertEqual(m['retirements'],[])
 def test_actual_whole_pair_hashes_distinct_actors_full_source_english_notes(self):
  m=t.load_manifest(P)
  for ref in REFS:
   bindings=m['review_bindings'][ref];self.assertEqual(len({b['reviewer_id']for b in bindings}),2);self.assertEqual({m['files'][b['input']]for b in bindings},{INPUTS[ref]});rows=t.reviewed_rows(P,bindings,ref,m['files']);self.assertEqual(rows[0],rows[1]);c,v=t.parse_ref(ref);self.assertEqual(record(c,v)['translation'],rows[0]['translation']);self.assertEqual(record(c,v)['source']['text'],rows[0]['source']['text']);self.assertEqual(record(c,v)['source']['confidence'],'low');self.assertTrue(rows[0]['source']['transcription_uncertainties'])
 def test_exact_historical_owners_not_generic_uncertainty_waiver(self):
  m=t.load_manifest(P);self.assertEqual(set(m['supersedes']),{'1 Enoch 18:8','1 Enoch 84:2'})
  for ref,name in [('1 Enoch 18:8','enoch_full_repair_batch10_20261022'),('1 Enoch 84:2','enoch_full_repair_batch08_20261022')]:
   old=t.APPLICATIONS/name;om=t.load_manifest(old);c,v=t.parse_ref(ref);digest=om['files'][f'{c:03d}-{v:03d}.candidate.yaml'];self.assertEqual(m['supersedes'][ref],{'package':name,'manifest_sha256':t.sha((old/'manifest.json').read_bytes()),'candidate_sha256':digest});self.assertEqual(m['canonical_baseline_sha256'][f'{c:03d}/{v:03d}.yaml'],digest);self.assertIn({'reference':ref,'superseded_by':P.name},verify_current(old)['reviewed_supersessions'])
 def test18_actual_fidels_contrastive_particle_reach_stone_and_summit(self):
  d=record(18,8);s=d['source']['text'];self.assertTrue(s.startswith('ወማእከላይሰ'));self.assertIn('ወድማሑ',s);self.assertIn('ፔካ',s);self.assertNotIn('⟦',s);self.assertTrue(d['translation']['text'].startswith('But the middle one[a] reaches'));self.assertIn('pēkā-stone',d['translation']['text']);self.assertIn('top of the throne',d['translation']['text']);self.assertEqual(len(d['translation']['footnotes']),3);self.assertIn('asterisk',d['translation']['footnotes'][2]['text']);self.assertIn('eske',d['translation']['footnotes'][2]['text'])
 def test84_whole39_tokens_not_only_target_glyph(self):
  d=record(84,2);s=d['source']['text'];self.assertIn('መለኮትከ',s);self.assertIn('ምንበርከ',s);self.assertNotIn('⟦',s);self.assertEqual(s.count('*'),5);self.assertIn('your authority endures through every generation',d['translation']['text']);self.assertEqual(len(d['translation']['footnotes']),3)
 def test54_only_exact_fresh_pair_may_restore_full_clipped_unit(self):
  if '1 Enoch 54:8'not in REFS:
   self.assertEqual(t.sha((t.TRANSLATION/'054/008.yaml').read_bytes()),t.load_manifest(P)['canonical_baseline_sha256']['054/008.yaml']);return
  d=record(54,8);self.assertIn('አንስታይት',d['source']['text']);self.assertNotIn('እንስታይት',d['source']['text']);self.assertIn('ወማይ፡',d['source']['text']);self.assertIn('ወይዴመሩ',d['source']['text']);self.assertIn('[ዘ]ምስለ',d['source']['text']);self.assertIn('female',d['translation']['text']);self.assertIn('above the heavens',d['translation']['text']);self.assertIn('54:7',json.dumps(d['translation']['footnotes']));self.assertIn('55:2',json.dumps(d['translation']['footnotes']))
 def test_low_confidence_not_unknown_marker_or_confidence_increase(self):
  for ref in REFS:
   d=record(*t.parse_ref(ref));self.assertEqual(d['source']['confidence'],'low');self.assertTrue(d['source']['transcription_uncertainties']);self.assertNotIn('⟦',d['source']['text']);self.assertFalse(d['source_correction']['full_book_verified']);self.assertFalse(d['source_correction']['human_specialist_certification']);self.assertFalse(d['source_correction']['manuscript_witness_certification'])
 def test_only_individual_overrides_existing_chapter_counts_unchanged(self):
  m=t.load_manifest(P);reg=sources.registry_data();self.assertEqual(m['chapter_inventories'],[]);self.assertEqual(m['source_only_count_inventories'],[]);self.assertNotIn('existing_paired_application_count_ingress',m)
  for ref in REFS:
   c,v=t.parse_ref(ref);self.assertEqual(reg['units'][f'{c}:{v}'],P.name);self.assertFalse(record(c,v)['source_correction']['selected_edition_chapter_reviewed']);self.assertEqual(next(r['source']['text']for r in sources.load_unit_overrides(c)if r['verse']==v),record(c,v)['source']['text']);self.assertEqual(next(r.text for r in verse_parser.parse_chapter(c)[0]if r.verse==v),record(c,v)['source']['text'])
  self.assertEqual(reg['chapters']['18'],'enoch_full_repair_batch10_20261022');self.assertEqual(reg['chapters']['84'],'enoch_full_repair_batch08_20261022');self.assertNotIn('48:7',reg['units'])
 def test_quiet_details_export_and_source_prompt_preserve_complete_controls(self):
  for ref in REFS:
   c,v=t.parse_ref(ref);d=record(c,v);out=reader._export_record_verse(v,d);self.assertEqual(out['text'],d['translation']['text']);self.assertEqual(out['footnotes'],d['translation']['footnotes']);self.assertEqual(out['footnote_review'],reader.PROTOCOL);self.assertEqual(out['source_critical']['text'],d['source']['text']);self.assertEqual(build_enoch_prompt(c,v).source_payload['text'],d['source']['text'])
 def test_rehashed_source_english_note_and_confidence_changes_fail_closed(self):
  for mode in ['source','English','note','confidence']:
   with self.subTest(mode=mode),tempfile.TemporaryDirectory()as directory:
    q=Path(directory)/'package';shutil.copytree(P,q);p=q/'084-002.candidate.yaml';d=yaml.load(p.read_bytes(),Loader=t.LOADER)
    if mode=='source':d['source']['text']=d['source']['text'].replace('መለኮትከ','መለከትከ')
    elif mode=='English':d['translation']['text']=d['translation']['text'].replace('sovereign power','rainbow')
    elif mode=='note':d['translation']['footnotes'][0]['text']='Unreviewed explanation.'
    else:d['source']['confidence']='medium'
    p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False));m=json.loads((q/'manifest.json').read_text());m['files'][p.name]=t.sha(p.read_bytes());(q/'manifest.json').write_text(json.dumps(m))
    with self.assertRaises(ValueError):t.verify(q,evidence_only=True)
 def test_arbitrary_actual_current_edit_cannot_pass_strict_successor_chain(self):
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);shutil.copytree(t.TRANSLATION,root/'corpus');p=root/'corpus/018/008.yaml';p.write_bytes(p.read_bytes()+b'\n# arbitrary current drift\n')
   with patch.object(t,'TRANSLATION',root/'corpus'):
    with self.assertRaises((AssertionError,ValueError)):assert_current_batch32(self)
 def test_CI_fetches_actual_baseline_and_runs_new_guards(self):
  workflow=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text();self.assertIn('git fetch --no-tags --depth=1 origin 6d750894702ca05e20c50b75919c15916ca3fcb8',workflow)
  for pattern in ['test_enoch_full_repair_batch32.py','test_enoch_application_count_ingress48.py','test_enoch_witness_projection_metadata.py']:self.assertIn("python -m unittest discover -s tests -p '"+pattern+"'",workflow)
