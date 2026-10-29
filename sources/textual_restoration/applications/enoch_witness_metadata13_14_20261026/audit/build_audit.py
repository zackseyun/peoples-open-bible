from pathlib import Path
import copy,datetime,difflib,hashlib,json,shutil,subprocess,sys
import yaml,jsonschema
R=Path('/Users/zackseyun/Documents/future 2/workspaces/enoch-audit-integration-20261020');sys.path.insert(0,str(R))
O=Path('/Users/zackseyun/Documents/future 2/output/enoch-full-repair-20261020/new-witness-metadata13-14-audit-20261026')
from tools.enoch import bounded_application as t,historical_evidence as h
from tools.enoch.audit_editorial_issues import record_issues
REFS=['1 Enoch 13:4','1 Enoch 13:6','1 Enoch 13:7','1 Enoch 13:9','1 Enoch 14:19','1 Enoch 14:24']
sha=lambda raw:hashlib.sha256(raw).hexdigest()
write=lambda p,d:p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip();current_before={ref:t.sha((t.TRANSLATION/('%03d/%03d.yaml'%t.parse_ref(ref))).read_bytes())for ref in REFS}
indices=[R/'sources/enoch/coverage/historical-input-bindings-20261022.json',R/'sources/enoch/coverage/historical-input-bindings-20261023.json'];checks={};cases={};dependencies={}
for index in indices:
 validated=h.load_current(index);checks[str(index.relative_to(R))]={'sha256':t.sha(index.read_bytes()),'validator':'historical_evidence.load_current','current_imported_units':len(validated),'validation_completed':True}
 data=json.loads(index.read_text())
 for package in data['packages']:
  for u in package['units']:
   if u['reference']not in REFS:continue
   assert u['reference']not in cases;cases[u['reference']]=(index,package,u)
assert set(cases)==set(REFS)
for folder in ['before','candidate','diff','raw']: (O/folder).mkdir(exist_ok=True)
def at(node,keys):
 for k in keys:
  if isinstance(k,int):node=node.value[k]
  else:node=next(v for key,v in node.value if key.value==k)
 return node
schema=json.loads((R/'schema/verse.schema.json').read_text());validator=jsonschema.Draft202012Validator(schema)
rows=[]
for ref in REFS:
 c,v=t.parse_ref(ref);rel=f'translation/extra_canonical/1_enoch/{c:03}/{v:03}.yaml';path=R/rel;raw=path.read_bytes();text=raw.decode();old=yaml.safe_load(text);tree=yaml.compose(text)
 index,package,u=cases[ref];orig=R/u['candidate'];assert raw==orig.read_bytes() and current_before[ref]==u['canonical_sha256_at_import'];assert package['files'][u['candidate']]==sha(raw)
 owner=R/package['package'];manifest=json.loads((owner/'manifest.json').read_text());receipt=json.loads((owner/'application.json').read_text());assert receipt['manifest_sha256']==t.sha((owner/'manifest.json').read_bytes())
 inputrows=json.loads((R/u['input']).read_text());submitted=next(r for r in inputrows if r['reference']==ref);assert h.reviewed_input_core(submitted,u.get('input_serializer'))==h.core(old)
 assert h.verdict(json.loads((R/u['review']).read_text()),ref)=='accept';assert h.verdict(json.loads((R/package['final_review']).read_text()),ref)=='accept'
 witnesses=old['enoch_witnesses']['available_witnesses'];matching=[i for i,x in enumerate(witnesses)if x.get('witness')=='charles_1906'];assert len(matching)==1;i=matching[0];w=witnesses[i];assert w['text']!=old['source']['text'];assert w['source_edition']=='Charles 1906 Ethiopic Enoch'and'Recovered from sources/enoch/ethiopic/transcribed/charles_1906/'in w['note']and'via tools/enoch/verse_parser.py'in w['note']
 note=(f"Selected Charles1906 source projection from the exact historically accepted input at {u['input']} (SHA256 {t.sha((R/u['input']).read_bytes())}). Metadata alignment only, not a new source/English review or independent witness. The earlier parser/OCR extraction remains preserved in {u['candidate']} (SHA256 {sha(raw)}).")
 expected=copy.deepcopy(old);expected['enoch_witnesses']['available_witnesses'][i]['text']=old['source']['text'];expected['enoch_witnesses']['available_witnesses'][i]['note']=note
 replacements=[]
 for key,value in [('text',old['source']['text']),('note',note)]:
  keys=['enoch_witnesses','available_witnesses',i,key];n=at(tree,keys);assert n.value==w[key];replacements.append((n.start_mark.index,n.end_mark.index,json.dumps(value,ensure_ascii=False),'/'+ '/'.join(map(str,keys))))
 patched=text
 for start,end,value,field in sorted(replacements,reverse=True):patched=patched[:start]+value+patched[end:]
 after=patched.encode();assert yaml.safe_load(after)==expected
 # Both substitutions are scalar spans. All other original characters, including
 # source/English/note/status block formatting, are copied verbatim.
 rebuilt=[];cursor=0;segments=[]
 for start,end,value,field in sorted(replacements):
  rebuilt.extend([text[cursor:start],value]);segments.append({'path':field,'before_character_start':start,'before_character_end':end,'before_scalar_sha256':sha(text[start:end].encode()),'after_scalar_sha256':sha(value.encode()),'old':w[field.rsplit('/',1)[1]],'new':expected['enoch_witnesses']['available_witnesses'][i][field.rsplit('/',1)[1]]});cursor=end
 rebuilt.append(text[cursor:]);assert ''.join(rebuilt)==patched
 for k in old:
  if k!='enoch_witnesses':assert old[k]==expected[k]
 unpatched=patched
 for start,end,value,field in sorted(replacements,reverse=True):pass
 candidate_name=f'{c:03}-{v:03}.candidate.yaml';before_name=f'{c:03}-{v:03}.before.yaml';(O/'candidate'/candidate_name).write_bytes(after);(O/'before'/before_name).write_bytes(raw);(O/'diff'/f'{c:03}-{v:03}.patch').write_text(''.join(difflib.unified_diff(text.splitlines(True),patched.splitlines(True),fromfile=rel,tofile='candidate/'+candidate_name)))
 errors=[{'path':'/'+ '/'.join(map(str,e.path)),'message':e.message}for e in validator.iter_errors(expected)];assert errors==[{'path':'/status','message':"'revised' is not one of ['draft']"}],errors
 eng=copy.deepcopy(expected);eng['status']='draft';assert not list(validator.iter_errors(eng))
 oldissues=record_issues(old,c,v);newissues=record_issues(expected,c,v);assert [x['kind']for x in oldissues]==['charles_witness_source_mismatch'];assert newissues==[]
 meaningful={key:{'before_sha256':sha(text[at(tree,[key]).start_mark.index:at(tree,[key]).end_mark.index].encode()),'same_object':old[key]==expected[key],'same_original_bytes_outside_scalar_spans':True}for key in ['source','translation','status']}
 # Freeze all actual imported historical file dependencies, including original
 # raw adverse/accepted decisions and original input hashes, without edits.
 for name,digest in package['files'].items():
  p=R/name;assert t.sha(p.read_bytes())==digest;dependencies[name]=digest;q=O/'raw'/name;q.parent.mkdir(parents=True,exist_ok=True)
  if not q.exists():shutil.copyfile(p,q)
 name=str(index.relative_to(R));dependencies[name]=t.sha(index.read_bytes());q=O/'raw'/name;q.parent.mkdir(parents=True,exist_ok=True)
 if not q.exists():shutil.copyfile(index,q)
 row={'reference':ref,'canonical_path':rel,'canonical_preimage_sha256':sha(raw),'candidate_path':'candidate/'+candidate_name,'candidate_sha256':sha(after),'before_path':'before/'+before_name,'owner_package':package['package'],'owner_manifest_sha256':t.sha((owner/'manifest.json').read_bytes()),'owner_application_sha256':t.sha((owner/'application.json').read_bytes()),'owner_original_candidate_sha256':sha(orig.read_bytes()),'historical_index':name,'historical_index_sha256':t.sha(index.read_bytes()),'historical_unit_binding':u,'accepted_raw_review_sha256':t.sha((R/u['review']).read_bytes()),'exact_review_input_sha256':t.sha((R/u['input']).read_bytes()),'historical_source_text_exact_match':True,'historical_complete_translation_exact_match':True,'selected_source_and_complete_translation_semantic_hash':sha(json.dumps(h.core(old),ensure_ascii=False,sort_keys=True).encode()),'changed_fields':segments,'unaltered_fields':meaningful,'other_fields_semantically_identical':True,'all_other_original_characters_preserved_verbatim':True,'stale_entry_kind':'same-selected-edition parser/OCR projection; not an independent manuscript/variant witness','schema_validation_errors_unchanged_from_preimage':errors,'would_be_schema_valid_after_separately_authorized_status_only_downgrade':True,'mechanical_record_issues_before':oldissues,'mechanical_record_issues_after':newissues,'fresh_source_English_reviews':0,'extra_provider_calls':0,'extra_photo_views':0,'new_review_coverage_credit':0,'metadata_audit_decision':'mechanical_delta_justified_not_applied_or_published'}
 if ref=='1 Enoch 13:6':row['additional_out_of_scope_issue']={'path':'/lexical_decisions/5/source_word','old_value':old['lexical_decisions'][5]['source_word'],'reviewed_selected_final_source_token':'አስተ','action':'Untouched. Separate lexical/source-word metadata review needed; source.note and actualEnglish/notes already carry provisional extension treatment.'}
 rows.append(row)
assert {ref:t.sha((t.TRANSLATION/('%03d/%03d.yaml'%t.parse_ref(ref))).read_bytes())for ref in REFS}==current_before
report={'kind':'enoch-six-historical-witness-projection-metadata-audit-v1','created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'auditor':'/root/witness_metadata13_14_audit','integration_head_at_audit':HEAD,'references':REFS,'primary_pdf_sha256_edition_anchor_not_new_photo_review':t.PRIMARY_SHA,'historical_profile_validation':checks,'raw_dependency_sha256':dependencies,'cases':rows,'canonical_changed':False,'source_fields_or_complete_English_or_explanations_changed':False,'status_or_confidence_changed':False,'new_source_English_reviews':0,'new_provider_calls':0,'new_photo_views':0,'new_review_coverage_credit':0,'wording_or_publication_approval':False,'full_book_verified':False,'requires_independent_exact_metadata_delta_review_and_parent_bounded_transaction':True,'limits':'Mechanical copying ONLY from already accepted exact reviewed selected source into an existing stale same-edition parser/OCR witness projection; no fresh source-content verification. All6 legacy status=revised schema errors deliberately preserved; separate engineering-only lifecycle policy required before current-schema integration.'}
write(O/'audit.json',report);write(O/'metadata-review-input.json',[{k:r[k]for k in ['reference','canonical_path','canonical_preimage_sha256','candidate_path','candidate_sha256','owner_package','owner_manifest_sha256','owner_application_sha256','historical_index','historical_index_sha256','historical_unit_binding','changed_fields','schema_validation_errors_unchanged_from_preimage']}for r in rows])
print(json.dumps({'audit_sha256':t.sha((O/'audit.json').read_bytes()),'metadata_input_sha256':t.sha((O/'metadata-review-input.json').read_bytes()),'refs':REFS,'all_six_metadata_mismatches_removed_in_outside_candidates_only':True,'unchanged_legacy_schema_status_errors':6,'canonical_changed':False},indent=2))
