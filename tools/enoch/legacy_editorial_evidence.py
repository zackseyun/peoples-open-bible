"""Two original parent-editorial receipts, not independent source approvals.

Raw receipts/drafts and actual applied/before Git records remain immutable.
Only explicitly bound fresh paired replacements may change each current target.
"""
import io
import json
import re
import subprocess
import yaml
from tools.enoch import bounded_application as t

INDEX='sources/enoch/coverage/legacy-individuals/enoch7-10-editorial-v1.json'
INDEX_SHA='b1408d43d850855d0eba4d864937a47e2fa45e7bd368ce4ebeb40c66d7778157'
NAMES=('enoch7_8.2026-10-06.v1.json','enoch9_10.2026-10-07.v1.json')


def registered(package):return package.name in NAMES


def read_index():
    raw=t.artifact(t.ROOT,INDEX).read_bytes()
    if t.sha(raw)!=INDEX_SHA:raise ValueError('Legacy7-10 editorial artifact index differs')
    d=json.loads(raw)
    if d.get('kind')!='enoch7-10-parent-editorial-history-v1' or set(d.get('cases',{}))!={'7-8','9-10'} or d.get('full_chapter_wording_approval')is not False:
        raise ValueError('Legacy7-10 editorial scope differs')
    for path,digest in d['files'].items():
        if t.sha(t.artifact(t.ROOT,path).read_bytes())!=digest:
            raise ValueError('Legacy7-10 original artifact differs: '+path)
    return d


def _blobs(queries):
    # One actual Git-object read for the finite pinned historical record set.
    # No cache across calls; subsequent reads must detect raw/target drift.
    p=subprocess.run(['git','--no-replace-objects','cat-file','--batch'],cwd=t.ROOT,
                     input=('\n'.join(queries)+'\n').encode(),capture_output=True,check=True)
    data=io.BytesIO(p.stdout);out={}
    for query in queries:
        header=data.readline().decode().rstrip('\n')
        if header.endswith(' missing'):out[query]=None;continue
        parts=header.split()
        if len(parts)!=3 or parts[1]!='blob':raise ValueError('Legacy7-10 expected Git blob missing')
        raw=data.read(int(parts[2]))
        if data.read(1)!=b'\n':raise ValueError('Legacy7-10 Git blob framing differs')
        out[query]=raw
    if data.read():raise ValueError('Legacy7-10 unexpected Git object output')
    return out


def _case(package):
    d=read_index()
    if not registered(package)or package.resolve()!=(t.APPLICATIONS/package.name).resolve():
        raise ValueError('Unregistered legacy editorial receipt')
    case=next(c for c in d['cases'].values()if c['receipt']==package.name)
    receipt=json.loads(package.read_text())
    chapters=(7,8)if package.name==NAMES[0]else(9,10)
    refs=[f'1 Enoch {c}:{v}'for c,n in zip(chapters,(6,4)if chapters==(7,8)else(11,22))for v in range(1,n+1)]
    if receipt.get('status')!='applied_locally_pending_required_ci_and_main_merge' or receipt.get('baseline_commit')!=case['baseline_commit'] or \
            [r['reference']for r in receipt['applications']]!=refs or \
            any(receipt.get(k)is not False for k in ('fresh_manuscript_reading','full_book_complete','reader_published')) or \
            case.get('historical_independent_review_passes_proven')!=0 or case.get('original_applied_parent_matches_claimed_before')is not True or case.get('applied_parent_differences')!=[]:
        raise ValueError('Legacy7-10 original parent-only scope differs')
    return case,receipt


def verify_historical(package):
    case,r=_case(package);queries=[]
    for row in r['applications']:
        c,v=t.parse_ref(row['reference']);path=f'translation/extra_canonical/1_enoch/{c:03d}/{v:03d}.yaml'
        if row['target']!=path:raise ValueError('Legacy7-10 original target identity differs')
        queries.extend([case['applied_commit']+':'+path,case['applied_commit']+'^:'+path,case['baseline_commit']+':'+path])
    blobs=_blobs(queries)
    for row in r['applications']:
        path=row['target'];raw=blobs[case['applied_commit']+':'+path]
        if raw is None or t.sha(raw)!=row['after_sha256']:raise ValueError('Legacy7-10 actual applied Git record differs')
        record=yaml.load(raw,Loader=t.LOADER)
        if record['reference']!=row['reference'] or record['source']['text']!=row['source_text'] or record['source']['pages']!=row['source_pages'] or record['translation']['text']!=row['english']:
            raise ValueError('Legacy7-10 parent receipt payload differs from actual applied bytes')
        for commit in (case['applied_commit']+'^',case['baseline_commit']):
            before=blobs[commit+':'+path]
            if (before is None)!=(row['before_sha256']is None)or before is not None and t.sha(before)!=row['before_sha256']:
                raise ValueError('Legacy7-10 actual parent/baseline preimage or absence differs')
    return {'references':[r['reference']for r in r['applications']],
            'historical_canonical_sha256':{r['reference']:r['after_sha256']for r in r['applications']},
            'historical_artifacts_verified':True,'historical_independent_review_passes_proven':0,
            'historical_scope':case['scope'],'chapter_publication_approval':False,
            'full_book_verified':False,'human_specialist_certification':False,'graphic_publication_approved':False}


def descriptor(reference):
    c,_=t.parse_ref(reference);name=NAMES[0]if c in(7,8)else NAMES[1]if c in(9,10)else None
    if name is None:raise ValueError('Unregistered legacy editorial reference')
    case,r=_case(t.APPLICATIONS/name);rows=[x for x in r['applications']if x['reference']==reference]
    if len(rows)!=1:raise ValueError('Unregistered legacy editorial target')
    return {'kind':'enoch-parent-editorial-explicit-successor-v1','receipt':name,
            'receipt_sha256':t.sha((t.APPLICATIONS/name).read_bytes()),
            'canonical_sha256':rows[0]['after_sha256'],'historical_scope':case['scope'],
            'change_scope':'new_paired_individual_source_English_explanations'}


def validate_declared_successors(package,manifest):
    entries=manifest['supersedes_legacy_editorial'];checked=set()
    if not isinstance(entries,dict)or not entries:raise ValueError('Legacy editorial successor set empty')
    for ref,entry in entries.items():
        if ref not in manifest['references']or entry!=descriptor(ref):raise ValueError('Legacy editorial successor does not bind exact original scope')
        if entry['receipt']not in checked:
            verify_historical(t.APPLICATIONS/entry['receipt']);checked.add(entry['receipt'])
        rel='%03d/%03d.yaml'%t.parse_ref(ref)
        if manifest['canonical_baseline_sha256'].get(rel)!=entry['canonical_sha256']:
            raise ValueError('Legacy editorial successor preimage differs')
        t.verify_git_preimage(manifest,rel,entry['canonical_sha256'])


def verify_current(package,*,seen=()):
    if package.name in seen:raise ValueError('Legacy editorial successor cycle')
    historical=verify_historical(package);superseded=[];current={};checked={}
    from tools.enoch.current_evidence import verify_current as verify_new
    for ref,digest in historical['historical_canonical_sha256'].items():
        target=t.TRANSLATION/('%03d/%03d.yaml'%t.parse_ref(ref))
        if not target.exists():raise ValueError('Legacy editorial current target missing')
        current[ref]=t.sha(target.read_bytes())
        if current[ref]==digest:continue
        matches=[]
        for candidate in sorted(t.APPLICATIONS.glob('enoch_full_repair_batch*')):
            if not(candidate/'application.json').is_file():continue
            m=json.loads((candidate/'manifest.json').read_text())
            if m.get('supersedes_legacy_editorial',{}).get(ref)==descriptor(ref):matches.append(candidate)
        if len(matches)!=1:raise ValueError('No unique paired editorial successor: '+ref)
        name=matches[0].name
        if name not in checked:checked[name]=verify_new(matches[0],seen=(*seen,package.name))
        if ref not in checked[name]['references']:raise ValueError('Legacy editorial successor omits reference')
        superseded.append({'reference':ref,'superseded_by':name})
    return {**historical,'current_canonical_sha256':current,'canonical_targets_checked':True,'reviewed_supersessions':superseded}
