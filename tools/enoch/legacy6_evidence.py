"""Original6:6-8 parent transaction, not invented independent source proof.

Pin every raw artifact and actual applied/parent Git byte. A later change must
bind its exact old manifest/candidate/preimage and have new paired evidence.
"""
import json
from tools.enoch import bounded_application as t
from tools.enoch.legacy_editorial_evidence import _blobs

NAME='enoch_6_20260930'
INDEX='sources/enoch/coverage/legacy-individuals/enoch6-parent-transaction-v1.json'
INDEX_SHA='7dd9dfd86520f6a5182ea34da63d4391fb7fa3995a137ae13827ff00ff86add8'
REFS=[f'1 Enoch 6:{v}'for v in(6,7,8)]


def registered(package):return package.name==NAME


def read_index():
    raw=t.artifact(t.ROOT,INDEX).read_bytes()
    if t.sha(raw)!=INDEX_SHA:raise ValueError('Legacy6 raw index differs')
    d=json.loads(raw)
    if d.get('kind')!='enoch6-parent-transaction-history-v1' or d.get('package')!=NAME or d.get('references')!=REFS or d.get('historical_independent_review_passes_proven')!=0 or d.get('full_chapter_wording_approval')is not False:
        raise ValueError('Legacy6 scope differs')
    for path,digest in d['files'].items():
        if t.sha(t.artifact(t.ROOT,path).read_bytes())!=digest:raise ValueError('Legacy6 original raw artifact differs: '+path)
    return d


def verify_historical(package):
    if not registered(package)or package.resolve()!=(t.APPLICATIONS/NAME).resolve():raise ValueError('Unregistered legacy6 package')
    d=read_index();m=json.loads((package/'manifest.json').read_text());r=json.loads((package/'application.json').read_text());review=json.loads((package/'final-source-review.json').read_text())
    if m.get('primary_scan_sha256')!=t.PRIMARY_SHA or m.get('final_source_review_sha256')!=t.sha((package/'final-source-review.json').read_bytes()) or r.get('manifest_sha256')!=t.sha((package/'manifest.json').read_bytes()) or r.get('status')!='applied_verified' or r.get('refs')!=['6:6','6:7','6:8'] or set(review['reviews'])!={'006-006','006-007','006-008'}:
        raise ValueError('Legacy6 original receipt binding differs')
    paths={ref:'translation/extra_canonical/1_enoch/%03d/%03d.yaml'%t.parse_ref(ref)for ref in REFS}
    queries=[commit+':'+path for path in paths.values()for commit in(d['applied_commit'],d['applied_commit']+'^')];blobs=_blobs(queries)
    for ref,path in paths.items():
        _,v=t.parse_ref(ref);key=f'006-{v:03d}';raw=(package/(key+'.candidate.yaml')).read_bytes();digest=t.sha(raw)
        before=blobs[d['applied_commit']+'^:'+path]
        if digest!=d['historical_canonical_sha256'][ref] or digest!=m['files'].get(key+'.candidate.yaml') or digest!=r['candidate_sha256'].get(key) or raw!=blobs[d['applied_commit']+':'+path] or review['reviews'][key]['verdict']!='accept' or (t.sha(before)if before is not None else None)!=d['actual_parent_preimages'][ref]:
            raise ValueError('Legacy6 actual applied/parent candidate differs')
        if v==6 and before!=(package/'006-006.baseline.yaml').read_bytes():raise ValueError('Legacy6 original baseline differs')
    return {'references':REFS,'historical_canonical_sha256':d['historical_canonical_sha256'],'historical_artifacts_verified':True,'actual_parent_preimages_verified':True,'historical_independent_review_passes_proven':0,'historical_scope':d['scope'],'full_book_verified':False,'chapter_publication_approval':False,'graphic_publication_approved':False,'human_specialist_certification':False}


def verify_current(package,*,seen=()):
    if NAME in seen:raise ValueError('Legacy6 successor cycle')
    old=verify_historical(package);manifest_hash=t.sha((package/'manifest.json').read_bytes());superseded=[];current={};checked={}
    from tools.enoch.current_evidence import verify_current as verify_new
    for ref,digest in old['historical_canonical_sha256'].items():
        c,v=t.parse_ref(ref);target=t.TRANSLATION/f'{c:03d}/{v:03d}.yaml'
        if not target.is_file():raise ValueError('Legacy6 current target missing')
        current[ref]=t.sha(target.read_bytes())
        if current[ref]==digest:continue
        expected={'package':NAME,'manifest_sha256':manifest_hash,'candidate_sha256':digest};matches=[]
        for candidate in sorted(t.APPLICATIONS.glob('enoch_full_repair_batch*')):
            if not(candidate/'application.json').is_file():continue
            m=json.loads((candidate/'manifest.json').read_text())
            if m.get('supersedes',{}).get(ref)==expected:matches.append(candidate)
        if len(matches)!=1:raise ValueError('No unique paired legacy6 successor: '+ref)
        name=matches[0].name
        if name not in checked:checked[name]=verify_new(matches[0],seen=(*seen,NAME))
        if ref not in checked[name]['references']:raise ValueError('Legacy6 successor omits reference')
        superseded.append({'reference':ref,'superseded_by':name})
    return {**old,'current_canonical_sha256':current,'canonical_targets_checked':True,'reviewed_supersessions':superseded}
