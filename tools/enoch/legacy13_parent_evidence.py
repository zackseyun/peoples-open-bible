"""Original13:1-3 editorial bytes and a separately bound fresh successor.

No raw receipt, original test or current batch17 application is reapproved or
rewritten. A dated three-unit parent claim is not a new independent source pass.
"""
import json
import yaml
from tools.enoch import bounded_application as t
from tools.enoch.legacy_editorial_evidence import _blobs

NAME='enoch13_legacy.2026-10-09.v1'
SUCCESSOR='enoch_full_repair_batch17_20261023'
INDEX='sources/enoch/coverage/legacy-individuals/enoch13-first3-detached-successor-v1.json'
INDEX_SHA='1161f0f6e97f7fca9751dd3483b589d92680fbbc5f318191aaa55303569d1429'
REFS=[f'1 Enoch 13:{v}'for v in(1,2,3)]


def registered(package):return package.name==NAME


def read_index():
    raw=t.artifact(t.ROOT,INDEX).read_bytes()
    if t.sha(raw)!=INDEX_SHA:raise ValueError('Legacy13 fixed detached index differs')
    d=json.loads(raw)
    if d.get('kind')!='enoch13-first3-parent-editorial-detached-successor-v1' or d.get('legacy_package')!=NAME or d.get('successor_package')!=SUCCESSOR or d.get('references')!=REFS or d.get('raw_receipt_reference_serializer')!='literal-1-Enoch13-colon-v-no-space-v1' or d.get('historical_independent_source_review_passes_proven')!=0 or d.get('full_chapter_approval')is not False:
        raise ValueError('Legacy13 original editorial/detached scope differs')
    for path,digest in d['legacy_files'].items():
        if t.sha(t.artifact(t.ROOT,path).read_bytes())!=digest:raise ValueError('Legacy13 original artifact differs: '+path)
    return d


def verify_historical(package):
    if not registered(package)or package.resolve()!=(t.APPLICATIONS/NAME).resolve():raise ValueError('Unregistered legacy13package')
    d=read_index();receipt=json.loads((package/'application.json').read_text());review=json.loads((package/'editorial-review.json').read_text())
    if receipt.get('status')!='applied_locally_pending_required_ci_and_main_merge' or receipt.get('baseline_commit')!=d['legacy_baseline_commit'] or receipt.get('editorial_review_sha256')!=t.sha((package/'editorial-review.json').read_bytes()) or review.get('primary_scan_sha256')!=t.PRIMARY_SHA or review.get('source_glyph_changes')is not False or any(receipt.get(k)is not False for k in('human_specialist_certification','fresh_manuscript_reading','reader_published','full_book_complete')):
        raise ValueError('Legacy13 original editorial receipt binding differs')
    queries=[]
    for row,v in zip(receipt['applications'],(1,2,3)):
        path=f'translation/extra_canonical/1_enoch/013/{v:03d}.yaml'
        if row['reference']!=f'1 Enoch13:{v}'or row['target']!=path or row.get('source_glyphs_unchanged')is not True:raise ValueError('Legacy13 exact raw reference serializer/source scope differs')
        queries.extend(c+':'+path for c in(d['legacy_applied_commit'],d['legacy_applied_commit']+'^',d['legacy_baseline_commit']))
    if len(receipt['applications'])!=3:raise ValueError('Legacy13 original bounded reference count differs')
    blobs=_blobs(queries);hashes={}
    for row,v in zip(receipt['applications'],(1,2,3)):
        path=row['target'];after=blobs[d['legacy_applied_commit']+':'+path];before=blobs[d['legacy_applied_commit']+'^:'+path]
        if after is None or before is None or t.sha(after)!=row['after_sha256'] or t.sha(before)!=row['before_sha256'] or blobs[d['legacy_baseline_commit']+':'+path]!=before or (package/f'013-{v:03d}.baseline.yaml').read_bytes()!=before or (package/f'013-{v:03d}.candidate.yaml').read_bytes()!=after:
            raise ValueError('Legacy13 actual applied/parent/baseline bytes differ')
        a=yaml.load(after,Loader=t.LOADER);b=yaml.load(before,Loader=t.LOADER)
        if a['source']['text']!=b['source']['text']or a['reference']!=f'1 Enoch 13:{v}':raise ValueError('Legacy13 original source-unchanged claim differs')
        hashes[f'1 Enoch 13:{v}']=row['after_sha256']
    return {'references':REFS,'historical_canonical_sha256':hashes,'actual_parent_and_baseline_preimages_verified':True,'historical_artifacts_verified':True,'historical_independent_source_review_passes_proven':0,'full_chapter_approval':False,'full_book_verified':False,'graphic_publication_approved':False,'human_specialist_certification':False}


def verify_current(package,*,seen=()):
    if NAME in seen:raise ValueError('Legacy13 successor cycle')
    d=read_index();old=verify_historical(package);new=t.APPLICATIONS/SUCCESSOR
    if t.sha((new/'manifest.json').read_bytes())!=d['successor_manifest_sha256']:raise ValueError('Legacy13 detached successor manifest differs')
    from tools.enoch.current_evidence import verify_current as verify_new
    current=verify_new(new,seen=(*seen,NAME));manifest=t.load_manifest(new)
    if not set(REFS)<=set(current['references']):raise ValueError('Legacy13 current paired successor omits original targets')
    for ref,digest in old['historical_canonical_sha256'].items():
        rel='%03d/%03d.yaml'%t.parse_ref(ref)
        if manifest['canonical_baseline_sha256'].get(rel)!=digest or d['successor_exact_preimages'].get(ref)!=digest:raise ValueError('Legacy13 detached exact preimage differs')
        t.verify_git_preimage(manifest,rel,digest)
    return {**old,'canonical_targets_checked':True,'reviewed_supersessions':[{'reference':ref,'superseded_by':SUCCESSOR}for ref in REFS]}
