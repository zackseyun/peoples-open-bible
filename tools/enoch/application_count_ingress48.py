"""Reuse exactly B07's already-paired48 inventory for a fresh individual unit.

No new count, language acceptance, chapter registration, or reader-release rule.
The existing same-input full-count gate and52–69 profile remain unchanged.
"""
import json
from tools.enoch import bounded_application as t

KEY='existing_paired_application_count_ingress'
NAME='enoch_full_repair_batch07_20261021'
MANIFEST_SHA='7dce558be3a42df4ccc2ab0cdd6e7bfb738b6a232d2c182f24f39c6010d4e6e1'
COUNT_ARTIFACT='source-only-count-inventory.json'
COUNT_SHA='4be1b11f9095938080905fa6ab9d120bf39b9c2de2ffab4aa973104160da5a0f'
UNITS=list(range(1,11))
DECLARATION={'chapter':48,'package':NAME,'package_manifest_sha256':MANIFEST_SHA,
 'count_artifact':COUNT_ARTIFACT,'count_artifact_sha256':COUNT_SHA,'units':UNITS,
 'independent_count_confirmation':True,'wording_approval':False,'reader_release_policy_changed':False}

def validate(manifest):
    declarations=manifest.get(KEY,[])
    if not isinstance(declarations,list):raise ValueError('Existing application-count ingress must be an explicit list')
    if not declarations:return {}
    if len(declarations)!=1 or declarations[0]!=DECLARATION:
        raise ValueError('Only exact paired B07 chapter48 count reuse is supported')
    if any(type(u)is not int for u in declarations[0]['units']):raise ValueError('Historical48 units must be exact integer addresses')
    if type(declarations[0].get('chapter'))is not int or any(type(declarations[0].get(k))is not bool for k in('independent_count_confirmation','wording_approval','reader_release_policy_changed')):
        raise ValueError('Application-count approval flags must have exact types')
    refs=[t.parse_ref(ref)for ref in manifest['references']]
    if not any(c==48 for c,v in refs)or any(v not in UNITS for c,v in refs if c==48):
        raise ValueError('Individual48 source unit exceeds or lacks the historical count scope')
    other={r['chapter']for k in('chapter_inventories','source_only_count_inventories','existing_paired_count_ingress')for r in manifest.get(k,[])}
    if 48 in other:raise ValueError('Historical48 count ingress overlaps another count declaration')
    package=t.artifact(t.APPLICATIONS,NAME)
    if package.parent!=t.APPLICATIONS.resolve()or t.sha((package/'manifest.json').read_bytes())!=MANIFEST_SHA:
        raise ValueError('Historical48 application manifest differs')
    # Re-run the original full paired-input/count checks; a new one-row input
    # cannot impersonate those historical ten-unit reviews.
    old=t.load_manifest(package)
    if old['files'].get(COUNT_ARTIFACT)!=COUNT_SHA:
        raise ValueError('Historical48 count artifact is not pinned')
    raw=t.artifact(package,COUNT_ARTIFACT).read_bytes()
    if t.sha(raw)!=COUNT_SHA:raise ValueError('Historical48 count artifact changed')
    certs=[r for r in old.get('source_only_count_inventories',[])if r['chapter']==48]
    expected={'chapter':48,'units':UNITS,'artifact':COUNT_ARTIFACT,'independent_count_confirmation':True}
    if certs!=[expected]:raise ValueError('Historical48 paired certificate differs')
    data=json.loads(raw);rows=[r for r in data['chapters']if r['chapter']==48]
    receipt=json.loads((package/'application.json').read_text())
    if (data.get('kind')!='enoch-source-ingress-counts-v1'or data.get('primary_pdf_sha256')!=t.PRIMARY_SHA
        or data.get('wording_approval')is not False or data.get('reader_release_policy_changed')is not False
        or len(rows)!=1 or rows[0]['units']!=UNITS or receipt.get('status')!='applied_verified'
        or receipt.get('manifest_sha256')!=MANIFEST_SHA):
        raise ValueError('Historical48 count proof or installed receipt differs')
    return {48:{'chapter':48,'units':list(UNITS),'artifact':str(package.relative_to(t.ROOT))+'/'+COUNT_ARTIFACT,'independent_count_confirmation':True,'wording_approval':False,'reader_release_policy_changed':False,'basis':'Existing exact paired application count; no new structural or language credit.'}}
