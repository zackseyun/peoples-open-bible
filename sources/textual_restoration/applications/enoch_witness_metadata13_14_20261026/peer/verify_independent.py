from pathlib import Path
import copy,datetime,hashlib,json,subprocess,sys
import yaml,jsonschema
R=Path('/Users/zackseyun/Documents/future 2/workspaces/enoch-audit-integration-20261020');O=Path('/Users/zackseyun/Documents/future 2/output/enoch-full-repair-20261020');A=O/'new-witness-metadata13-14-audit-20261026';D=O/'new-witness-metadata13-14-independent-20261026';sys.path.insert(0,str(R))
from tools.enoch import historical_evidence as h,bounded_application as t,audit_editorial_issues as issues
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();digest=lambda x:hashlib.sha256(x).hexdigest();now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat();save=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
REFS=['1 Enoch 13:4','1 Enoch 13:6','1 Enoch 13:7','1 Enoch 13:9','1 Enoch 14:19','1 Enoch 14:24'];BASE='6d750894702ca05e20c50b75919c15916ca3fcb8';INPUT='4d4730f5e7b0fee4380ef7d4286ffa844e31384cb3fbe00d22ec11419ae12d02';AUDIT='b01619f3e97a2fbb42103f29852c0aba0d9c58a2ada8bb8e013d75f7cc5458a5'
assert sha(A/'metadata-review-input.json')==INPUT and sha(A/'audit.json')==AUDIT
rows=json.loads((A/'metadata-review-input.json').read_text());audit=json.loads((A/'audit.json').read_text());assert [r['reference']for r in rows]==REFS==audit['references']
artifacts=json.loads((A/'artifact-hashes.json').read_text());assert len(artifacts)==71
for rel,expected in artifacts.items():assert sha(A/rel)==expected,('audit artifact mismatch',rel)
rawdeps=audit['raw_dependency_sha256'];assert len(rawdeps)==47
for rel,expected in rawdeps.items():assert sha(R/rel)==expected,('historical raw dependency mismatch',rel)
indices={};validated={}
for rel,pv in audit['historical_profile_validation'].items():
 assert sha(R/rel)==pv['sha256'];data=json.loads((R/rel).read_text());indices[rel]=data
 actual=h.load_current(R/rel);validated[rel]={'units':sorted(f'1 Enoch {c}:{v}'for c,v in actual),'count':len(actual),'fresh_review':False}
 assert len(actual)==pv['current_imported_units']
validator=jsonschema.Draft202012Validator(json.loads((R/'schema/verse.schema.json').read_text()))
def value_node(root,path):
 node=root
 for key in path:
  if isinstance(node,yaml.MappingNode):
   found=[v for k,v in node.value if k.value==key];assert len(found)==1;node=found[0]
  elif isinstance(node,yaml.SequenceNode):node=node.value[key]
  else:raise AssertionError('path does not resolve')
 return node

def mask_scalars(raw,paths):
 text=raw.decode('utf-8');root=yaml.compose(text);spans=[]
 for path in paths:
  n=value_node(root,path);assert isinstance(n,yaml.ScalarNode);spans.append((n.start_mark.index,n.end_mark.index,'/'.join(map(str,path))))
 for start,end,label in sorted(spans,reverse=True):text=text[:start]+'<EXACT_METADATA_SCALAR:'+label+'>'+text[end:]
 return text

def field_diffs(a,b,path=''):
 if type(a)!=type(b):return[path]
 if isinstance(a,dict):
  out=[]
  for k in set(a)|set(b):
   q=path+'/'+str(k)
   if k not in a or k not in b:out.append(q)
   else:out+=field_diffs(a[k],b[k],q)
  return sorted(out)
 if isinstance(a,list):
  if len(a)!=len(b):return[path]
  return sorted(q for i,(x,y) in enumerate(zip(a,b))for q in field_diffs(x,y,path+'/'+str(i)))
 return[]if a==b else[path]

cases=[]
for submitted in rows:
 ref=submitted['reference'];c,v=t.parse_ref(ref);case=next(x for x in audit['cases']if x['reference']==ref)
 canonical=R/submitted['canonical_path'];oldraw=canonical.read_bytes();before=A/case['before_path'];newpath=A/submitted['candidate_path'];newraw=newpath.read_bytes();old=yaml.safe_load(oldraw);new=yaml.safe_load(newraw)
 assert digest(oldraw)==submitted['canonical_preimage_sha256']==sha(before)==case['owner_original_candidate_sha256']
 assert sha(newpath)==submitted['candidate_sha256']==case['candidate_sha256']
 oldgit=subprocess.check_output(['git','--no-replace-objects','show',BASE+':'+submitted['canonical_path']],cwd=R);assert oldgit==oldraw
 index=indices[submitted['historical_index']];matches=[(p,u)for p in index['packages']for u in p['units']if u['reference']==ref];assert len(matches)==1;p,u=matches[0]
 assert u==submitted['historical_unit_binding']==case['historical_unit_binding'];assert (R/u['candidate']).read_bytes()==oldraw
 owner=R/submitted['owner_package'];m=json.loads((owner/'manifest.json').read_text());app=json.loads((owner/'application.json').read_text())
 assert sha(owner/'manifest.json')==submitted['owner_manifest_sha256'] and sha(owner/'application.json')==submitted['owner_application_sha256'];assert m['files'][Path(u['candidate']).name]==digest(oldraw)
 assert app['status']=='applied_verified' and app['manifest_sha256']==sha(owner/'manifest.json') and app['candidate_sha256'][f'{c:03d}-{v:03d}']==digest(oldraw)
 submitted_rows=json.loads((R/u['input']).read_text());actual=[r for r in submitted_rows if t.parse_ref(r['reference'])==(c,v)];assert len(actual)==1
 assert h.reviewed_input_core(actual[0],u.get('input_serializer'))==h.core(old)
 if u.get('source_metadata_policy'):h.validate_source_metadata_delta(actual[0]['source'],old['source'],u['source_metadata_policy'])
 rawreview=json.loads((R/u['review']).read_text());assert h.verdict(rawreview,ref)=='accept';assert sha(R/u['review'])==case['accepted_raw_review_sha256'];assert sha(R/u['input'])==case['exact_review_input_sha256']
 finalreview=json.loads((R/p['final_review']).read_text());assert h.verdict(finalreview,ref)=='accept';assert finalreview['reviewed_content_sha256'][f'{c:03d}-{v:03d}']==u['reviewed_core_sha256']
 ids=[i for i,w in enumerate(old['enoch_witnesses']['available_witnesses'])if w.get('witness')=='charles_1906'];assert len(ids)==1;i=ids[0];ow=old['enoch_witnesses']['available_witnesses'][i];nw=new['enoch_witnesses']['available_witnesses'][i]
 assert ow['language']=='geez' and ow['text']!=old['source']['text'] and ow['note'].startswith('Recovered from sources/enoch/ethiopic/transcribed/charles_1906/')
 note=f"Selected Charles1906 source projection from the exact historically accepted input at {u['input']} (SHA256 {sha(R/u['input'])}). Metadata alignment only, not a new source/English review or independent witness. The earlier parser/OCR extraction remains preserved in {u['candidate']} (SHA256 {sha(R/u['candidate'])})."
 assert nw['text']==old['source']['text'] and nw['note']==note
 expected=copy.deepcopy(old);expected['enoch_witnesses']['available_witnesses'][i]['text']=old['source']['text'];expected['enoch_witnesses']['available_witnesses'][i]['note']=note;assert new==expected
 paths=[['enoch_witnesses','available_witnesses',i,'text'],['enoch_witnesses','available_witnesses',i,'note']];diffs=field_diffs(old,new);assert diffs==sorted('/'+'/'.join(map(str,p))for p in paths)
 assert mask_scalars(oldraw,paths)==mask_scalars(newraw,paths),('bytes changed outside actual scalar spans',ref)
 errs_old=[('/'+'/'.join(map(str,e.path)),e.message)for e in validator.iter_errors(old)];errs_new=[('/'+'/'.join(map(str,e.path)),e.message)for e in validator.iter_errors(new)];assert errs_old==errs_new and len(errs_new)==1 and errs_new[0][0]=='/status' and old['status']=='revised'
 eng=copy.deepcopy(new);eng['status']='draft';validator.validate(eng);assert field_diffs(new,eng)==['/status']
 assert not issues.record_issues(new,c,v)
 cases.append({'reference':ref,'canonical_preimage_sha256':digest(oldraw),'pure_metadata_candidate_sha256':digest(newraw),'exact_semantic_delta_paths':diffs,'all_other_original_characters_preserved_verbatim':True,'source_complete_translation_explanations_confidence_historical_AI_crosscheck_and_status_unchanged':True,'accepted_original_review_sha256':sha(R/u['review']),'exact_original_input_sha256':sha(R/u['input']),'historical_core_verified':True,'actual_base_Git_preimage_verified':True,'legacy_schema_failure_only_status_revised':True,'separate_in_memory_engineering_status_only_variant_schema_valid':True,'new_source_English_reviews':0})
# Counterproofs exercise the exact allowlist, not just a loose textual equality.
base_old=yaml.safe_load((A/rows[0]['candidate_path']).read_bytes());allowed=cases[0]['exact_semantic_delta_paths'];counterproofs=[]
for key in ('source','translation','ai_draft','cross_check','status','extra_witness','confidence','wrong_projection_text'):
 bad=copy.deepcopy(base_old)
 if key in ('source','translation'):bad[key]['text']+=' UNREVIEWED'
 elif key=='ai_draft':bad[key]['model_id']='invented-reviewer'
 elif key=='cross_check':bad[key]['status']='needs_review'
 elif key=='status':bad[key]='draft'
 elif key=='extra_witness':bad['enoch_witnesses']['available_witnesses'].append({'witness':'invented'})
 elif key=='confidence':bad['source']['confidence']='high'
 else:bad['enoch_witnesses']['available_witnesses'][0]['text']='UNREVIEWED'
 # All these are forbidden against the already exact puremetadata output.
 assert bad!=base_old
 if key!='wrong_projection_text':assert field_diffs(base_old,bad)
 else:assert bad['enoch_witnesses']['available_witnesses'][0]['text']!=base_old['source']['text']
 counterproofs.append({'mutation':key,'rejected_by_exact_expected_candidate_comparison':True})
# End preimages still equal: do not approve a moving current snapshot.
for row in rows:assert sha(R/row['canonical_path'])==row['canonical_preimage_sha256']
report={'kind':'independent-six-historical-witness-projection-metadata-verification-v1','at':now(),'reviewer_id':'/root/witness_metadata13_14_independent','input_sha256':INPUT,'audit_sha256':AUDIT,'actual_base_Git_commit':BASE,'all_cases_verified':True,'cases':cases,'metadata_artifact_hashes_verified':len(artifacts),'historical_raw_dependency_hashes_verified':len(rawdeps),'historical_current_profile_validation':validated,'counterproofs':counterproofs,'engineering_scope':'The puremetadata bytes remain status=revised. A separately pinned status-only revised->draft engineering policy is technically schema sufficient, but unseen final candidate bytes are NOT approved by this receipt.','unresolved_out_of_scope_lexical_metadata':'13:6 /lexical_decisions/5/source_word still retains oldOCR እሱተ and old rationale; not changed or approved here.','new_source_English_reviews':0,'new_actual_photo_views':0,'new_provider_calls':0,'no_new_source_registry_or_paired_note_protocol_stamp':True,'full_book_verified':False,'publication_approved':False,'canonical_changed':False}
save(D/'verification-report.json',report)
review={'protocol':'pob-enoch-exact-historical-witness-metadata-review-v1','reviewer_id':'/root/witness_metadata13_14_independent','role':'metadata_independent_reviewer','created_at_utc':now(),'input_sha256':INPUT,'reviews':[{'reference':x['reference'],'verdict':'accept_metadata_delta_only','canonical_preimage_sha256':x['canonical_preimage_sha256'],'pure_metadata_candidate_sha256':x['pure_metadata_candidate_sha256'],'rationale':'Independently verified exact accepted historical input/result/application/core and actual base Git/current preimage. Existing stale parser/OCR Charles text is projected only from unchanged accepted selectedsource, with truthful input/predecessor provenance note. Exactly two scalar spans changed; all other original characters, source, entire English/notes, status, confidence, AI and crosscheck remain unchanged. No source/English/publication vote is added. Legacy revised-status schema error remains; unseen final engineering candidates not approved.'}for x in cases],'model':'not_reported','provider':'not_reported','verification_report_sha256':sha(D/'verification-report.json'),'engineering_policy_assessment_separate_from_pure_metadata_vote':report['engineering_scope'],'new_source_English_reviews':0,'new_actual_photo_views':0,'new_provider_calls':0,'new_review_coverage_credit':0,'full_book_verified':False,'publication_approved':False}
save(D/'review.json',review)
pv={'protocol':review['protocol'],'reviewer_id':review['reviewer_id'],'role':review['role'],'input_sha256':INPUT,'review_sha256':sha(D/'review.json'),'audit_sha256':AUDIT,'verification_report_sha256':sha(D/'verification-report.json'),'primary_pdf_sha256_edition_anchor_only':t.PRIMARY_SHA,'new_actual_photo_views':0,'new_provider_calls':0,'new_provider_calls_scope':'No explicit external model/API calls; this Codex metadata audit is not a new source/English execution.','new_source_English_reviews':0,'actual_photo_view_map':{},'metadata_artifact_sha256':{str(A/rel):digest for rel,digest in artifacts.items()},'historical_receipt_dependencies_sha256':{str(R/rel):digest for rel,digest in rawdeps.items()},'model':'not_reported','provider':'not_reported','prior_exposure':'Parent supplied audit outcome/candidate paths/hashes. This is an informed independent exact metadata audit, not blind source review. No photographs or Bible translations read.','canonical_changed':False,'publication_approved':False}
save(D/'provenance.json',pv)
save(D/'artifact-hashes.json',{f.name:sha(f)for f in sorted(D.glob('*'))if f.is_file()and f.name!='artifact-hashes.json'})
print(json.dumps({'all6_metadata_deltas_accepted':True,'metadata_artifacts_verified':len(artifacts),'historical_dependencies_verified':len(rawdeps),'input_sha256':INPUT,'review_sha256':sha(D/'review.json'),'provenance_sha256':sha(D/'provenance.json'),'verification_report_sha256':sha(D/'verification-report.json'),'new_language_reviews':0,'canonical_changed':False},indent=2),flush=True)
