"""Six fixed metadata projections retain historical inputs, not new language votes."""
import copy,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t,historical_evidence as historical,witness_projection_metadata as m
from tools.enoch.current_evidence import verify_current
from tools import export_reader_bible as reader
class WitnessProjectionMetadataTest(unittest.TestCase):
 def test_exact_scope_old_bytes_and_only_three_metadata_fields(self):
  d=m.read_manifest();self.assertEqual(d['references'],m.REFS);self.assertEqual(len(d['cases']),6)
  for ref,case in d['cases'].items():
   old=yaml.load(t.artifact(t.ROOT,case['original_candidate']).read_bytes(),Loader=t.LOADER);new=yaml.load(t.artifact(t.APPLICATIONS/m.NAME,case['candidate']).read_bytes(),Loader=t.LOADER);expected=copy.deepcopy(new);i=case['witness_index'];expected['enoch_witnesses']['available_witnesses'][i]['text']=old['enoch_witnesses']['available_witnesses'][i]['text'];expected['enoch_witnesses']['available_witnesses'][i]['note']=old['enoch_witnesses']['available_witnesses'][i]['note'];expected['status']='revised';self.assertEqual(expected,old)
 def test_metadata_actors_are_not_source_english_or_photo_reviewers(self):
  d=m.read_manifest();self.assertEqual(len({b['reviewer_id']for b in d['metadata_reviews']}),2)
  for b in d['metadata_reviews']:
   pv=json.loads((t.APPLICATIONS/m.NAME/b['provenance']).read_text());self.assertEqual(pv['new_source_English_reviews'],0);self.assertEqual(pv['new_actual_photo_views'],0);self.assertEqual(pv['new_provider_calls'],0);self.assertEqual(pv['actual_photo_view_map'],{})
 def test_applied_exact966_postmap_and_original_input_evidence_preserved(self):
  d=m.read_manifest();r=m.verify(applied=True,check_corpus=False);self.assertTrue(r['inherited_historical_review_only']);self.assertEqual(r['new_full_source_or_English_reviews'],0);self.assertEqual(verify_current(t.APPLICATIONS/m.NAME)['references'],m.REFS)
  receipt=json.loads((t.APPLICATIONS/m.NAME/'application.json').read_text());expected=dict(d['canonical_baseline_sha256'])
  for ref,case in d['cases'].items():expected['%03d/%03d.yaml'%t.parse_ref(ref)]=case['candidate_sha256']
  self.assertEqual(receipt['canonical_after_sha256'],expected)
  successor=t.APPLICATIONS/'enoch_full_repair_batch33_20261027'
  if (successor/'application.json').is_file():
   from test_enoch_full_repair_batch33 import assert_current_batch33
   newer,_=assert_current_batch33(self);self.assertEqual(newer['canonical_baseline_sha256'],expected)
  else:self.assertEqual(t.corpus_hashes(),expected)
  imported=historical.load_all_current()
  for ref in m.REFS:
   if ref=='1 Enoch 13:6' and (successor/'application.json').is_file():self.assertNotIn((13,6),imported);continue
   evidence=imported[t.parse_ref(ref)];self.assertFalse(evidence['fresh_review']);self.assertFalse(evidence['full_chapter_count_certified_by_import'])
 def test_projection_never_adds_new_reader_protocol_or_source_registry_claim(self):
  from tools.enoch.selected_edition_sources import registry_data
  d=m.read_manifest();reg=registry_data()
  for ref,case in d['cases'].items():
   c,v=t.parse_ref(ref);old=yaml.load(t.artifact(t.ROOT,case['original_candidate']).read_bytes(),Loader=t.LOADER);new=yaml.load(t.artifact(t.APPLICATIONS/m.NAME,case['candidate']).read_bytes(),Loader=t.LOADER);self.assertEqual(reader._export_record_verse(v,old),reader._export_record_verse(v,new));self.assertEqual(old['source_correction'],new['source_correction']);self.assertFalse(new['source_correction'].get('individual_unit_application_approved',False))
   if ref=='1 Enoch 13:6' and (t.APPLICATIONS/'enoch_full_repair_batch33_20261027/application.json').is_file():
    from test_enoch_full_repair_batch33 import assert_current_batch33
    assert_current_batch33(self);self.assertEqual(reg['units']['13:6'],'enoch_full_repair_batch33_20261027')
   else:self.assertNotIn(f'{c}:{v}',reg['units'])
 def fixture(self,directory):
  root=Path(directory);package=root/m.NAME;shutil.copytree(t.APPLICATIONS/m.NAME,package);return root,package,json.loads((package/'manifest.json').read_text())
 def rebound(self,p,d):
  (p/'manifest.json').write_text(json.dumps(d));return patch.object(m,'MANIFEST_SHA',t.sha((p/'manifest.json').read_bytes()))
 def test_rehashed_source_english_notes_confidence_greek_ai_and_extra_witness_rejected(self):
  for mode in ('source','English','note','confidence','Greek','AI','crosscheck','witness','status','protocol'):
   with self.subTest(mode=mode),tempfile.TemporaryDirectory()as directory:
    root,p,d=self.fixture(directory);case=d['cases']['1 Enoch 14:24'];file=p/case['candidate'];new=yaml.load(file.read_bytes(),Loader=t.LOADER)
    if mode=='source':new['source']['text']+=' ሀ'
    elif mode=='English':new['translation']['text']+=' Invented sentence.'
    elif mode=='note':new['translation']['footnotes'][0]['text']='Invented note.'
    elif mode=='confidence':new['source']['confidence']='high'
    elif mode=='Greek':new['source']['additional_translation_input']=[]
    elif mode=='AI':new['ai_draft']['model_id']='invented-new-review'
    elif mode=='crosscheck':new['cross_check']['status']='needs_review'
    elif mode=='witness':new['enoch_witnesses']['available_witnesses'].append(copy.deepcopy(new['enoch_witnesses']['available_witnesses'][0]))
    elif mode=='status':new['status']='revised'
    else:new['source_correction']['individual_unit_application_approved']=True
    file.write_text(yaml.safe_dump(new,allow_unicode=True,sort_keys=False));case['candidate_sha256']=d['files'][case['candidate']]=t.sha(file.read_bytes())
    with patch.object(t,'APPLICATIONS',root),self.rebound(p,d),self.assertRaises(ValueError):m.read_manifest()
 def test_rehashed_wrong_projection_text_or_note_rejected(self):
  for field in ('text','note'):
   with self.subTest(field=field),tempfile.TemporaryDirectory()as directory:
    root,p,d=self.fixture(directory);case=d['cases'][m.REFS[0]];file=p/case['candidate'];new=yaml.load(file.read_bytes(),Loader=t.LOADER);new['enoch_witnesses']['available_witnesses'][case['witness_index']][field]='Unreviewed wrong projection';file.write_text(yaml.safe_dump(new,allow_unicode=True));case['candidate_sha256']=d['files'][case['candidate']]=t.sha(file.read_bytes())
    with patch.object(t,'APPLICATIONS',root),self.rebound(p,d),self.assertRaises(ValueError):m.read_manifest()
 def test_missing_or_duplicate_metadata_peer_and_extra_reference_rejected(self):
  for mode in ('missing','duplicate','extra'):
   with self.subTest(mode=mode),tempfile.TemporaryDirectory()as directory:
    root,p,d=self.fixture(directory)
    if mode=='missing':d['metadata_reviews']=d['metadata_reviews'][:1]
    elif mode=='duplicate':d['metadata_reviews'].append(copy.deepcopy(d['metadata_reviews'][0]))
    else:d['references'].append('1 Enoch 14:20')
    with patch.object(t,'APPLICATIONS',root),self.rebound(p,d),self.assertRaises(ValueError):m.read_manifest()
 def test_fabricated_photo_language_or_provider_count_rejected(self):
  for key in ('new_actual_photo_views','new_provider_calls','new_source_English_reviews'):
   with self.subTest(key=key),tempfile.TemporaryDirectory()as directory:
    root,p,d=self.fixture(directory);b=d['metadata_reviews'][1];file=p/b['provenance'];pv=json.loads(file.read_text());pv[key]=1;file.write_text(json.dumps(pv));d['files'][b['provenance']]=t.sha(file.read_bytes())
    with patch.object(t,'APPLICATIONS',root),self.rebound(p,d),self.assertRaises(ValueError):m.read_manifest()
 def test_original_raw_review_or_index_whitespace_drift_rejected(self):
  d=m.read_manifest();actual=t.artifact
  for rel in (next(iter(d['historical_indexes'])),next(k for k in d['historical_dependencies']if k.endswith('original-review.json'))):
   with self.subTest(rel=rel),tempfile.TemporaryDirectory()as directory:
    changed=Path(directory)/'changed';changed.write_bytes((t.ROOT/rel).read_bytes()+b'\n')
    with patch.object(t,'artifact',side_effect=lambda root,path:changed if Path(root)==t.ROOT and path==rel else actual(root,path)),self.assertRaises(ValueError):m.read_manifest()
 def test_current_arbitrary_metadata_or_semantic_drift_does_not_inherit_evidence(self):
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);shutil.copytree(t.TRANSLATION,root/'corpus');target=root/'corpus/014/019.yaml';target.write_bytes(target.read_bytes()+b'\n# arbitrary drift\n')
   with patch.object(t,'TRANSLATION',root/'corpus'):
    if (t.APPLICATIONS/'enoch_full_repair_batch33_20261027/application.json').is_file():
     from test_enoch_full_repair_batch33 import assert_current_batch33
     with self.assertRaises((AssertionError,ValueError)):assert_current_batch33(self)
    else:
     with self.assertRaises(ValueError):m.verify(applied=True)
    with self.assertRaises(ValueError):verify_current(t.APPLICATIONS/m.NAME)
    imported=historical.load_current(t.ROOT/'sources/enoch/coverage/historical-input-bindings-20261023.json');self.assertNotIn((14,19),imported);self.assertEqual(len(imported),5)
 def test_wrong_old_hash_and_outside_six_reference_cannot_use_projection(self):
  d=m.read_manifest();ref=m.REFS[0];case=d['cases'][ref];old=yaml.load(t.artifact(t.ROOT,case['original_candidate']).read_bytes(),Loader=t.LOADER);target=t.TRANSLATION/('%03d/%03d.yaml'%t.parse_ref(ref));self.assertFalse(m.matches_declared_successor(ref,'0'*64,old,target));self.assertFalse(m.matches_declared_successor('1 Enoch 14:20',case['original_sha256'],old,target))
 def test_13_6_stale_lexical_object_is_reported_not_silently_retargeted(self):
  d=m.read_manifest();case=d['cases']['1 Enoch 13:6'];old=yaml.load(t.artifact(t.ROOT,case['original_candidate']).read_bytes(),Loader=t.LOADER);new=yaml.load((t.APPLICATIONS/m.NAME/case['candidate']).read_bytes(),Loader=t.LOADER);self.assertEqual(new['lexical_decisions'],old['lexical_decisions']);self.assertEqual(new['lexical_decisions'][5]['source_word'],'እሱተ')
 def test_delivery_metadata_boundary_precedes_future_language_batches(self):
  from tools.enoch.delivery_candidates import ordered_packages
  packages=ordered_packages();d=m.read_manifest();i=packages.index(t.APPLICATIONS/m.NAME);self.assertEqual(packages[i-1],t.APPLICATIONS/d['source_application']);self.assertTrue(all('batch'not in p.name or int(p.name.split('batch')[1].split('_')[0])>32 for p in packages[i+1:]))
 def test_repeat_apply_refuses_before_any_write(self):
  before=t.corpus_hashes()
  with self.assertRaisesRegex(ValueError,'already has an application receipt'):m.apply()
  self.assertEqual(t.corpus_hashes(),before)
 def writer_fixture(self,directory):
  root,package,data=self.fixture(directory);(package/'application.json').unlink(missing_ok=True);corpus=root/'corpus';shutil.copytree(t.TRANSLATION,corpus)
  for ref,case in data['cases'].items():(corpus/('%03d/%03d.yaml'%t.parse_ref(ref))).write_bytes(t.artifact(t.ROOT,case['original_candidate']).read_bytes())
  # Reconstruct this historical writer's exact preimage, not a mixture of
  # old six metadata targets and a later unrelated44 language successor.
  drift={k for k,v in t.corpus_hashes(corpus).items()if data['canonical_baseline_sha256'].get(k)!=v}
  if drift:
   from tools.enoch import batch34_evidence,legacy44_evidence
   batch34_evidence.verify_current();self.assertEqual(drift,{'044/001.yaml'})
   raw=legacy44_evidence.historical_bytes();self.assertEqual(t.sha(raw),data['canonical_baseline_sha256']['044/001.yaml']);(corpus/'044/001.yaml').write_bytes(raw)
  self.assertEqual(t.corpus_hashes(corpus),data['canonical_baseline_sha256'])
  return root,package,data,corpus
 def test_writer_uses_atomic_receipt_and_keeps_exact_whole_postmap(self):
  with tempfile.TemporaryDirectory()as directory:
   root,p,d,corpus=self.writer_fixture(directory)
   with patch.object(t,'APPLICATIONS',root),patch.object(t,'TRANSLATION',corpus),patch.object(m,'verify',return_value={'writer_unit_test_only':True}):
    receipt=m.apply();self.assertEqual(receipt['canonical_after_sha256'],t.corpus_hashes());self.assertFalse((p/'application.json.pending').exists());self.assertTrue((p/'application.json').is_file())
    for ref,case in d['cases'].items():self.assertEqual(t.sha((corpus/('%03d/%03d.yaml'%t.parse_ref(ref))).read_bytes()),case['candidate_sha256'])
 def test_writer_receipt_rename_failure_rolls_back_without_partial_receipt(self):
  with tempfile.TemporaryDirectory()as directory:
   root,p,d,corpus=self.writer_fixture(directory);rename=m.os.replace
   def fail_receipt(src,dst):
    if Path(dst).name=='application.json':raise OSError('test injected receipt rename failure')
    return rename(src,dst)
   with patch.object(t,'APPLICATIONS',root),patch.object(t,'TRANSLATION',corpus),patch.object(m,'verify',return_value={}),patch.object(m.os,'replace',side_effect=fail_receipt):
    with self.assertRaises(OSError):m.apply()
    self.assertEqual(t.corpus_hashes(),d['canonical_baseline_sha256']);self.assertFalse((p/'application.json').exists());self.assertFalse((p/'application.json.pending').exists());self.assertFalse(list(corpus.rglob('*.metadata-pending')))
 def test_writer_immediate_preimage_recheck_preserves_concurrent_edit(self):
  with tempfile.TemporaryDirectory()as directory:
   root,p,d,corpus=self.writer_fixture(directory);target=corpus/'013/006.yaml';before=target.read_bytes();external=before+b'\n# test external edit after initial verification\n'
   def after_initial_verify(**kwargs):target.write_bytes(external);return{}
   with patch.object(t,'APPLICATIONS',root),patch.object(t,'TRANSLATION',corpus),patch.object(m,'verify',side_effect=after_initial_verify):
    with self.assertRaisesRegex(ValueError,'immediately before replacement'):m.apply()
    self.assertEqual(target.read_bytes(),external);self.assertEqual(t.sha((corpus/'013/004.yaml').read_bytes()),d['cases']['1 Enoch 13:4']['original_sha256']);self.assertFalse((p/'application.json').exists())
 def test_writer_rollback_does_not_overwrite_concurrent_postwrite_change(self):
  with tempfile.TemporaryDirectory()as directory:
   root,p,d,corpus=self.writer_fixture(directory);target=corpus/'013/004.yaml';external=[]
   def verify_then_conflict(**kwargs):
    if kwargs.get('applied'):
     external.append(target.read_bytes()+b'\n# test external edit after replacement\n');target.write_bytes(external[0]);raise ValueError('test injected final verification failure')
    return{}
   with patch.object(t,'APPLICATIONS',root),patch.object(t,'TRANSLATION',corpus),patch.object(m,'verify',side_effect=verify_then_conflict):
    with self.assertRaisesRegex(RuntimeError,'Concurrent metadata target edits preserved'):m.apply()
    self.assertEqual(target.read_bytes(),external[0]);self.assertFalse((p/'application.json').exists());self.assertFalse((p/'application.json.pending').exists())
    for ref,case in d['cases'].items():
     if ref!='1 Enoch 13:4':self.assertEqual(t.sha((corpus/('%03d/%03d.yaml'%t.parse_ref(ref))).read_bytes()),case['original_sha256'])
 def test_foreign_application_root_cannot_supply_an_isolated_fixture_approval(self):
  d=m.read_manifest();ref=m.REFS[0];case=d['cases'][ref];old=yaml.load(t.artifact(t.ROOT,case['original_candidate']).read_bytes(),Loader=t.LOADER);target=t.TRANSLATION/('%03d/%03d.yaml'%t.parse_ref(ref))
  with tempfile.TemporaryDirectory()as directory,patch.object(t,'ROOT',Path(directory)):
   self.assertFalse(m.matches_declared_successor(ref,case['original_sha256'],old,target))
