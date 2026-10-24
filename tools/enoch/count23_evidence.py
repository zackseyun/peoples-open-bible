"""Two actual chapter23 count observations, never a held wording approval."""
import json
from pathlib import Path
from tools.enoch import bounded_application as t

INDEX='sources/enoch/coverage/count23-20261023/index.json'
INDEX_SHA='f69ade2a4b024a9c1fe13b0c10d3839c7b7b6dc13c196f00d4541c1ef2b743be'


def load():
    raw=t.artifact(t.ROOT,INDEX).read_bytes()
    if t.sha(raw)!=INDEX_SHA:raise ValueError('Chapter23 fixed count index differs')
    d=json.loads(raw);prefix=d['artifact_prefix']+'/'
    if d.get('kind')!='enoch23-paired-independent-count-observations-v1' or d.get('primary_pdf_sha256')!=t.PRIMARY_SHA or (d.get('chapter'),d.get('count'),d.get('independent_actor_count'))!=(23,4,2) or d.get('unit_pages')!={str(v):[98]for v in range(1,5)} or d.get('wording_approval')is not False or d.get('reader_release_policy_changed')is not False:
        raise ValueError('Chapter23 count-only scope differs')
    for path,digest in d['files'].items():
        if t.sha(t.artifact(t.ROOT,path).read_bytes())!=digest:raise ValueError('Chapter23 original count artifact differs: '+path)
    def read(name):
        path=prefix+name
        if path not in d['files']:raise ValueError('Unpinned chapter23 count artifact')
        return json.loads(t.artifact(t.ROOT,path).read_text())
    a=read('root-source-first-ledger.json');b=read('other-source-first-ledger.json')
    ap=read('root-count-provenance.json');bp=read('other-provenance.json');comparison=read('paired-count-comparison.json')
    inputs=read('other-review-input.json');review=read('other-author-review.json');held=read('other-remaining-constraint.json')
    if a['reviewer_id']==b['reviewer_id'] or a['reviewer_id']!=ap['reviewer_id'] or b['reviewer_id']!=bp['reviewer_id'] or bp['reviewer_id']!=review['reviewer_id'] or ap['role']!='independent_structural_count_observer' or bp['role']!='author':
        raise ValueError('Chapter23 distinct observation actors differ')
    if any(p.get('source_pdf_sha256')!=t.PRIMARY_SHA for p in(ap,bp)) or a['primary_pdf_sha256']!=t.PRIMARY_SHA or a['observed_printed_unit_count']!=4 or b['observations']['chapter_count']!=4 or b['observations']['all_chapter_pages']!=[98] or b['observations']['unit4_pages']!=[98]:
        raise ValueError('Chapter23 actual printed count/page observation differs')
    if a['observed_units']!=[{'verse':v,'pages':[98],'cross_page_continuation':False}for v in range(1,5)] or a['before_current_canonical_English_source_oldreviews_OCR_or_lexical_locators']is not True or a['publication_approved']is not False or a['full_glyph_transcription_or_English_review']is not False:
        raise ValueError('Chapter23 root source-first structural scope differs')
    if ap['source_first_ledger_sha256']!=d['files'][prefix+'root-source-first-ledger.json'] or ap['paired_comparison_sha256']!=d['files'][prefix+'paired-count-comparison.json'] or ap['scan_image_sha256']!=a['images_personally_viewed'] or ap['exact_wording_approval']is not False or ap['publication_approval']is not False:
        raise ValueError('Chapter23 root count/photo provenance differs')
    if sorted(Path(p).name for p in ap['scan_image_sha256'])!=['pdf100.png','pdf96.png','pdf98.png'] or not b['actual_images'] or any(bp['scan_image_sha256'].get(x['path'])!=x['sha256']for x in b['actual_images']):
        raise ValueError('Chapter23 original full-page photo binding differs')
    if comparison['root_ledger_sha256']!=d['files'][prefix+'root-source-first-ledger.json'] or comparison['other_actor_ledger_sha256']!=d['files'][prefix+'other-source-first-ledger.json'] or comparison['other_actor_provenance_sha256']!=d['files'][prefix+'other-provenance.json'] or comparison['source_pdf_sha256']!=t.PRIMARY_SHA or comparison['verse_pages']!=d['unit_pages'] or comparison['source_English_semantic_acceptance']is not False or comparison['publication_approved']is not False:
        raise ValueError('Chapter23 structural comparison binding differs')
    expected='1 Enoch 23:4';input_sha=d['files'][prefix+'other-review-input.json']
    if len(inputs)!=1 or inputs[0]['reference']!=expected or bp['input_sha256']!=input_sha or review['input_sha256']!=input_sha or bp['review_sha256']!=d['files'][prefix+'other-author-review.json'] or held['input_sha256']!=input_sha or held['whole_unit_status']!='hold' or held['accepted_repairs']!=[]:
        raise ValueError('Chapter23 original whole4-hold binding differs')
    if len(review['reviews'])!=1 or review['reviews'][0]['reference']!=expected or review['reviews'][0]['verdict']!='hold' or review['reviews'][0]['input_sha256']!=input_sha:
        raise ValueError('Chapter23 held one-unit input is not four English approvals')
    return {23:{'chapter':23,'units':[1,2,3,4],'artifact':INDEX,'independent_count_confirmation':True,'kind':'paired_independent_actual_count_observations_not_wording_approval','wording_approval':False,'reader_release_policy_changed':False}}
