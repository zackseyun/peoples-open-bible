"""Six fixed historical reviewed-source projections, never six new language votes.

Original inputs, source/English/notes and attribution stay immutable. Only the
stale parser/OCR Charles projection and a separately declared lifecycle status
are changed. An arbitrary current edit cannot inherit the historical review.
"""
import copy
import json
import os
from pathlib import Path
import jsonschema
import yaml
from tools.enoch import bounded_application as t

NAME = 'enoch_witness_metadata13_14_20261026'
MANIFEST_SHA = '1bfc200b4176394bf2777f3cb27724f48db29a391979756fb0614352cf58e5e7'
REFS = ['1 Enoch 13:4','1 Enoch 13:6','1 Enoch 13:7','1 Enoch 13:9','1 Enoch 14:19','1 Enoch 14:24']
BASE = '6d750894702ca05e20c50b75919c15916ca3fcb8'


def registered(package):
    return package.name == NAME


def read_manifest():
    p=t.APPLICATIONS/NAME; raw=(p/'manifest.json').read_bytes()
    if t.sha(raw)!=MANIFEST_SHA:raise ValueError('Fixed six-unit witness metadata manifest differs')
    d=json.loads(raw)
    if (d.get('kind')!='enoch-fixed-witness-projection-metadata-v1' or d.get('references')!=REFS
        or d.get('primary_pdf_sha256')!=t.PRIMARY_SHA or d.get('source_baseline_git_commit')!=BASE
        or d.get('new_full_source_or_English_reviews')!=0
        or any(d.get(k)is not False for k in ('source_changed','translation_changed','new_source_ingress',
              'full_chapter_approval','graphic_publication_approved','full_book_verified'))):
        raise ValueError('Fixed witness metadata scope or approval limit differs')
    if list(d.get('cases',{}))!=REFS:raise ValueError('Witness metadata cases differ')
    for rel,digest in d['files'].items():
        if t.sha(t.artifact(p,rel).read_bytes())!=digest:raise ValueError('Witness metadata artifact changed: '+rel)
    for rel,digest in d['historical_indexes'].items():
        if t.sha(t.artifact(t.ROOT,rel).read_bytes())!=digest:raise ValueError('Historical witness input index changed')
    for rel,digest in d['historical_dependencies'].items():
        if t.sha(t.artifact(t.ROOT,rel).read_bytes())!=digest:raise ValueError('Historical witness raw dependency changed')
    metadata_inputs=json.loads(t.artifact(p,d['metadata_input']).read_text())
    if [r['reference']for r in metadata_inputs]!=REFS:raise ValueError('Pure metadata review input scope differs')
    identities=set()
    for b in d['metadata_reviews']:
        review=json.loads(t.artifact(p,b['review']).read_text());pv=json.loads(t.artifact(p,b['provenance']).read_text())
        if ((review.get('reviewer_id'),review.get('role'))!=(b['reviewer_id'],b['role'])
            or (pv.get('reviewer_id'),pv.get('role'))!=(b['reviewer_id'],b['role'])
            or review.get('input_sha256')!=d['files'][d['metadata_input']]
            or pv.get('input_sha256')!=d['files'][d['metadata_input']]
            or pv.get('review_sha256')!=d['files'][b['review']]
            or pv.get('primary_pdf_sha256_edition_anchor_only')!=t.PRIMARY_SHA
            or any(type(pv.get(k))is not int or pv[k]!=0 for k in('new_actual_photo_views','new_provider_calls','new_source_English_reviews'))
            or pv.get('actual_photo_view_map')!={}
):
            raise ValueError('Exact metadata-only review/provenance binding differs')
        deps=pv.get('historical_receipt_dependencies_sha256',{});prefix=b['dependency_key_prefix']
        if not isinstance(deps,dict) or any(not k.startswith(prefix)for k in deps) or {k[len(prefix):]:v for k,v in deps.items()}!=d['historical_dependencies']:raise ValueError('Metadata dependency-map encoding or hashes differ')
        decisions=review.get('reviews',[])
        if [r.get('reference')for r in decisions]!=REFS or any(r.get('verdict')!='accept_metadata_delta_only'for r in decisions):raise ValueError('Metadata delta lacks six exact metadata-only accepts')
        for decision,row in zip(decisions,metadata_inputs):
            if decision.get('canonical_preimage_sha256')!=row['canonical_preimage_sha256'] or decision.get('pure_metadata_candidate_sha256')!=row['candidate_sha256']:raise ValueError('Metadata vote preimage or pure candidate differs')
        identities.add(b['reviewer_id'])
    if len(d['metadata_reviews'])!=2 or len(identities)!=2 or {b['role']for b in d['metadata_reviews']}!={'metadata_author','metadata_independent_reviewer'}:raise ValueError('Metadata review actors/roles differ')
    policy=json.loads(t.artifact(p,d['engineering_policy']).read_text())
    if policy!={'kind':'enoch-six-record-lifecycle-only-schema-normalization-v1','references':REFS,
                'changes':{'/status':{'old':'revised','new':'draft'}},'new_language_reviews':0,
                'source_English_notes_confidence_historical_attribution_unchanged':True}:
        raise ValueError('Witness metadata separate engineering policy differs')
    baseline=d['canonical_baseline_sha256']
    if len(baseline)!=966 or len(set(baseline))!=966:raise ValueError('Witness metadata baseline scope differs')
    for ref,case in d['cases'].items():
        c,v=t.parse_ref(ref);rel=f'{c:03d}/{v:03d}.yaml'
        oldraw=t.artifact(t.ROOT,case['original_candidate']).read_bytes()
        if t.sha(oldraw)!=case['original_sha256'] or baseline.get(rel)!=case['original_sha256']:
            raise ValueError('Witness metadata historical/preimage bytes differ')
        old=yaml.load(oldraw,Loader=t.LOADER)
        if old.get('reference')!=ref or old.get('status')!='revised':raise ValueError('Witness metadata historical record differs')
        entries=old.get('enoch_witnesses',{}).get('available_witnesses',[])
        ids=[i for i,w in enumerate(entries)if w.get('witness')=='charles_1906']
        if len(ids)!=1 or ids[0]!=case['witness_index']:raise ValueError('Witness metadata Charles projection is not unique')
        i=ids[0];w=entries[i]
        if (w.get('language')!='geez' or w.get('text')==old['source']['text'] or
                not w.get('note','').startswith('Recovered from sources/enoch/ethiopic/transcribed/charles_1906/')):
            raise ValueError('Witness metadata old entry is not the declared stale OCR projection')
        expected=copy.deepcopy(old);expected['enoch_witnesses']['available_witnesses'][i]['text']=old['source']['text']
        expected_note=('Selected Charles1906 source projection from the exact historically accepted input at '+case['reviewed_input']+' (SHA256 '+case['reviewed_input_sha256']+'). Metadata alignment only, not a new source/English review or independent witness. The earlier parser/OCR extraction remains preserved in '+case['original_candidate']+' (SHA256 '+case['original_sha256']+').')
        expected['enoch_witnesses']['available_witnesses'][i]['note']=expected_note
        pure_row=next(r for r in metadata_inputs if r['reference']==ref)
        pure=t.artifact(p,'audit/'+pure_row['candidate_path']);pure_expected=copy.deepcopy(expected)
        if case['reviewed_input']!=pure_row['historical_unit_binding']['input'] or case['reviewed_input_sha256']!=d['historical_dependencies'][case['reviewed_input']]:raise ValueError('Metadata projection note cites wrong historical input')
        pure_expected['status']='revised'
        if t.sha(pure.read_bytes())!=pure_row['candidate_sha256'] or yaml.load(pure.read_bytes(),Loader=t.LOADER)!=pure_expected:raise ValueError('Pure reviewed metadata candidate differs')
        expected['status']='draft'  # Separately pinned engineering policy, not a source-review vote.
        candidate=t.artifact(p,case['candidate']);new=yaml.load(candidate.read_bytes(),Loader=t.LOADER)
        if d['files'].get(case['candidate'])!=case['candidate_sha256'] or new!=expected:
            raise ValueError('Witness metadata candidate differs beyond the three exact metadata fields')
        jsonschema.Draft202012Validator(json.loads((t.ROOT/'schema/verse.schema.json').read_text())).validate(new)
        if t.record_issues(new,c,v):raise ValueError('Witness metadata candidate fails mechanical controls')
    return d


def _receipt(d):
    p=t.APPLICATIONS/NAME;r=json.loads((p/'application.json').read_text())
    expected=dict(d['canonical_baseline_sha256'])
    for ref,case in d['cases'].items():expected['%03d/%03d.yaml'%t.parse_ref(ref)]=case['candidate_sha256']
    if (r.get('status')!='applied_verified' or r.get('manifest_sha256')!=MANIFEST_SHA
        or r.get('canonical_after_sha256')!=expected or r.get('new_full_source_or_English_reviews')!=0
        or r.get('source_English_notes_confidence_unchanged')is not True):
        raise ValueError('Witness metadata applied receipt differs')
    return r


def matches_declared_successor(reference, original_sha, original_candidate, target):
    """Called only AFTER original full historical input/review validation succeeds."""
    if reference not in REFS:return False
    package=t.APPLICATIONS/NAME
    # No receipt is not an approval. Before installation, original bytes still
    # take the ordinary historical path. Never accept an unapplied proposal.
    if not (package/'application.json').is_file():return False
    d=read_manifest();case=d['cases'][reference];_receipt(d)
    if original_sha!=case['original_sha256']:return False
    old=yaml.load(t.artifact(t.ROOT,case['original_candidate']).read_bytes(),Loader=t.LOADER)
    if original_candidate!=old:raise ValueError('Historical source proof differs from metadata predecessor')
    return target.is_file() and t.sha(target.read_bytes())==case['candidate_sha256']


def verify(*,applied=False,check_corpus=True):
    d=read_manifest();package=t.APPLICATIONS/NAME
    source=t.APPLICATIONS/d['source_application'];source_raw=(source/'manifest.json').read_bytes()
    if t.sha(source_raw)!=d['source_application_manifest_sha256']:raise ValueError('Witness metadata preceding source application differs')
    t.verify(source,evidence_only=True)
    source_receipt=json.loads((source/'application.json').read_text())
    if source_receipt.get('status')!='applied_verified' or source_receipt.get('manifest_sha256')!=d['source_application_manifest_sha256']:raise ValueError('Preceding source application lacks its exact applied receipt')
    if source_receipt['canonical_after_sha256']!=d['canonical_baseline_sha256']:
        raise ValueError('Witness metadata does not follow exact source-application postmap')
    # Actual base Git paths prove all six old candidate bytes, not a rewritten
    # historical receipt. Source B32 changes none of these six preimages.
    from tools.enoch.legacy_editorial_evidence import _blobs
    q={ref:BASE+':translation/extra_canonical/1_enoch/%03d/%03d.yaml'%t.parse_ref(ref) for ref in REFS}
    blobs=_blobs(list(q.values()))
    for ref,query in q.items():
        if blobs[query] is None or t.sha(blobs[query])!=d['cases'][ref]['original_sha256']:
            raise ValueError('Witness metadata actual Git preimage differs')
    expected=dict(d['canonical_baseline_sha256'])
    if applied:
        receipt=_receipt(d)
        expected=receipt['canonical_after_sha256']
    if check_corpus and t.corpus_hashes()!=expected:raise ValueError('Witness metadata exact966 current postmap/preimage differs')
    # Original full historical guards still prove every source/English/notes
    # input. The only new fallback is exact six current metadata byte hashes.
    from tools.enoch import historical_evidence as h
    covered=set()
    for rel in d['historical_indexes']:
        index=t.artifact(t.ROOT,rel);h.load_current(index)  # Every original input/raw-verdict guard runs even when a later current payload differs.
        for package_row in json.loads(index.read_text())['packages']:
            for unit in package_row['units']:
                ref=unit['reference']
                if ref in d['cases'] and unit['candidate']==d['cases'][ref]['original_candidate'] and unit['canonical_sha256_at_import']==d['cases'][ref]['original_sha256']:covered.add(ref)
    if covered!=set(REFS):raise ValueError('Witness metadata lacks unchanged historical accepted input evidence')
    return {'references':REFS,'canonical_targets_checked':check_corpus,'new_full_source_or_English_reviews':0,
            'inherited_historical_review_only':True,'source_English_notes_confidence_unchanged':True,
            'unrelated_canonical_files_unchanged':True,'snapshot_file_count':966,'full_book_verified':False,
            'graphic_publication_approved':False}


def apply():
    package=t.APPLICATIONS/NAME
    if (package/'application.json').exists():raise ValueError('Witness metadata already has an application receipt')
    pending=package/'application.json.pending'
    if pending.exists():raise ValueError('Pending metadata receipt exists; inspect interrupted transaction before any write')
    result=verify();d=read_manifest();originals={};intended={}
    try:
        for ref,case in d['cases'].items():
            target=t.TRANSLATION/('%03d/%03d.yaml'%t.parse_ref(ref))
            raw=target.read_bytes();candidate=t.artifact(package,case['candidate']).read_bytes()
            if t.sha(raw)!=case['original_sha256'] or t.sha(candidate)!=case['candidate_sha256']:
                raise ValueError('Metadata target/candidate changed immediately before replacement')
            temp=target.with_suffix('.yaml.metadata-pending')
            if temp.exists():raise ValueError('Pending metadata target exists; inspect interrupted transaction')
            originals[target]=raw;intended[target]=candidate
            temp.write_bytes(candidate);os.replace(temp,target)
        receipt={'status':'applied_verified','manifest_sha256':MANIFEST_SHA,'canonical_after_sha256':t.corpus_hashes(),
                 'new_full_source_or_English_reviews':0,'source_English_notes_confidence_unchanged':True,
                 'unrelated_canonical_files_unchanged':True,'deployed_by_transaction':False}
        with pending.open('wb')as handle:
            handle.write((json.dumps(receipt,indent=2)+'\n').encode());handle.flush();os.fsync(handle.fileno())
        os.replace(pending,package/'application.json')
        verify(applied=True)
        return receipt
    except Exception as error:
        conflicts=[]
        for target,raw in originals.items():
            target.with_suffix('.yaml.metadata-pending').unlink(missing_ok=True)
            current=target.read_bytes()if target.exists()else None
            if current==intended[target]:target.write_bytes(raw)
            elif current!=raw:conflicts.append(str(target))
        pending.unlink(missing_ok=True)
        (package/'application.json').unlink(missing_ok=True)
        if conflicts:raise RuntimeError('Concurrent metadata target edits preserved; manual recovery required: '+', '.join(conflicts))from error
        raise


def verify_current(package,*,seen=()):
    if not registered(package) or package.resolve()!=(t.APPLICATIONS/NAME).resolve():raise ValueError('Unregistered witness metadata package')
    if NAME in seen:raise ValueError('Witness metadata successor cycle')
    result=verify(applied=True,check_corpus=False);d=read_manifest();superseded=[]
    from tools.enoch.current_evidence import verify_current as verify_new
    for ref,case in d['cases'].items():
        target=t.TRANSLATION/('%03d/%03d.yaml'%t.parse_ref(ref))
        if target.exists() and t.sha(target.read_bytes())==case['candidate_sha256']:continue
        expected={'package':NAME,'manifest_sha256':MANIFEST_SHA,'candidate_sha256':case['candidate_sha256']}
        matches=[p for p in sorted(t.APPLICATIONS.glob('enoch_full_repair_batch*'))if (p/'application.json').is_file()and json.loads((p/'manifest.json').read_text()).get('supersedes',{}).get(ref)==expected]
        if len(matches)!=1 or ref not in verify_new(matches[0],seen=(*seen,NAME))['references']:raise ValueError('No unique explicitly reviewed witness-metadata successor: '+ref)
        superseded.append({'reference':ref,'superseded_by':matches[0].name})
    return {**result,'canonical_targets_checked':True,'current_targets_or_reviewed_successors_verified':True,'reviewed_supersessions':superseded}
