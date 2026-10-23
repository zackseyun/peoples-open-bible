"""Fixed30/31/35 primary-photo counts; six held units gain no wording approval."""
import json
from tools.enoch import bounded_application as t

INDEX='sources/enoch/coverage/count30-31-35-20261023.json'
INDEX_SHA='f90a1f4e8575bdc9d6652181bba6e8542f0cd0a5743dfc41a327613974207681'
COUNTS={30:3,31:3,35:1}


def load():
    raw=t.artifact(t.ROOT,INDEX).read_bytes()
    if t.sha(raw)!=INDEX_SHA:raise ValueError('Short Watchers fixed count index differs')
    d=json.loads(raw)
    if d.get('kind')!='enoch30-31-35-fixed-source-only-count-profile-v1' or d.get('counts')!={str(c):n for c,n in COUNTS.items()} or d.get('primary_pdf_sha256')!=t.PRIMARY_SHA or d.get('wording_approval')is not False or d.get('reader_release_policy_changed')is not False:
        raise ValueError('Short Watchers structural-only scope differs')
    for path,digest in d['files'].items():
        if t.sha(t.artifact(t.ROOT,path).read_bytes())!=digest:raise ValueError('Short Watchers original count artifact differs')
    def read(path):
        if path not in d['files']:raise ValueError('Unpinned short count input')
        return json.loads(t.artifact(t.ROOT,path).read_text())
    a=read(d['author_ledger']);b=read(d['independent_ledger']);inputs=read(d['source_input'])
    if a['reviewer_id']==b['reviewer_id']or a['observations']['counts']!={str(c):n for c,n in COUNTS.items()} or b.get('source_pdf_sha256')!=t.PRIMARY_SHA or b['counts']!={str(c):list(range(1,n+1))for c,n in COUNTS.items()}:
        raise ValueError('Short Watchers independent source counts differ')
    expected=[f'1 Enoch {c}:{v}'for c,n in COUNTS.items()for v in range(1,n+1)]
    if [r['reference']for r in inputs]!=expected:raise ValueError('Short Watchers full structural input scope differs')
    spans={f'{c}:{v}':[113 if c==35 else 108]for c,n in COUNTS.items()for v in range(1,n+1)}
    if a['observations']['unit_pages']!=spans or b['unit_pages']!=spans:
        raise ValueError('Short Watchers actual unit spans differ')
    package=t.APPLICATIONS/d['package'];prefix=str(package.relative_to(t.ROOT))+'/final/ch30-31-35/'
    for role,ledger in(('author',a),('independent',b)):
        review=read(prefix+role+'-review.json');pv=read(prefix+role+'-provenance.json')
        expected_role='author'if role=='author'else'independent_reviewer'
        images=(ledger.get('personally_viewed_image_sha256')or{x['path']:x['sha256']for x in ledger['personally_viewed_images']})
        if pv.get('source_pdf_sha256')!=t.PRIMARY_SHA or (pv.get('reviewer_id'),pv.get('role'))!=(ledger['reviewer_id'],expected_role) or review.get('reviewer_id')!=pv['reviewer_id'] or pv.get('input_sha256')!=d['files'][d['source_input']] or review.get('input_sha256')!=pv['input_sha256'] or pv.get('review_sha256')!=d['files'][prefix+role+'-review.json'] or not images or any(pv['scan_image_sha256'].get(p)!=h for p,h in images.items()):
            raise ValueError('Short Watchers exact source/count/photo provenance differs')
        if [r['reference']for r in review['reviews']]!=expected or review['chapter_inventory_only']!={str(c):{'count':n,'pages':[113 if c==35 else 108]}for c,n in COUNTS.items()}:
            raise ValueError('Short Watchers paired explicit count statement differs')
        if [r['reference']for r in review['reviews']if r['verdict']=='hold']!=expected[:-1]:
            raise ValueError('Short Watchers source-count profile lost six whole wording holds')
    return {c:{'chapter':c,'units':list(range(1,n+1)),'artifact':INDEX,'independent_count_confirmation':True,'kind':'paired_primary_count_only_six_wording_holds_not_promoted','wording_approval':False,'reader_release_policy_changed':False}for c,n in COUNTS.items()}
