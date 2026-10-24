"""Selected XX has seven counted units, not seven new wording approvals."""
import datetime
import json
from pathlib import Path
from tools.enoch import bounded_application as t

INDEX='sources/enoch/coverage/count20-azure-20261023/index.json'
INDEX_SHA='5ecf9b7772e84b45005f645a421bc6c609cf4416bfc9a117da46139c8009a3b6'


def load():
    raw=t.artifact(t.ROOT,INDEX).read_bytes()
    if t.sha(raw)!=INDEX_SHA:raise ValueError('20 fixed structural count index differs')
    d=json.loads(raw);prefix=d['artifact_prefix']+'/'
    if d.get('kind')!='enoch20-original-author-and-blind-Azure-structural-count-v1' or d.get('primary_pdf_sha256')!=t.PRIMARY_SHA or(d.get('chapter'),d.get('count'),d.get('independent_actor_count'))!=(20,7,2) or d.get('unit_pages')!={str(v):[90]for v in range(1,8)} or d.get('wording_approval')is not False or d.get('reader_release_policy_changed')is not False or d.get('canonical_English_votes_imported')!=0:
        raise ValueError('20 structural-only scope differs')
    for p,h in d['files'].items():
        if t.sha(t.artifact(t.ROOT,p).read_bytes())!=h:raise ValueError('20 original count artifact differs: '+p)
    def read(name):
        p=prefix+name
        if p not in d['files']:raise ValueError('Unpinned20 count artifact')
        return json.loads(t.artifact(t.ROOT,p).read_text())
    author=read('author-own-source-first-ledger.json');pv=read('author-provenance.json');review=read('author-author-review.json');inputs=read('author-review-input.json')
    manifest=read('request-manifest.json');start=read('submission-started.json');result=read('raw-model-text.json');terminal=read('provider-terminal-response.json');done=read('completed-receipt.json');live=read('live-deployment.json');project=read('request-with-image-hashes.json')
    if author['reviewer_id']!=pv['reviewer_id']or pv['reviewer_id']!=review['reviewer_id']or author['role']!='author' or any(author[k]is not False for k in('current_english_or_source_read','old_chapter20_reviews_read','OCR_or_lexical_locators_read'))or author['own_actual_count']['count']!=7 or author['own_actual_count']['units']!=list(range(1,8))or author['own_actual_count']['all_unit_pdf_pages']!=d['unit_pages']:
        raise ValueError('20 actual source-first author count differs')
    if any(p['source_pdf_sha256']!=t.PRIMARY_SHA for p in(author,pv,manifest))or pv['input_sha256']!=d['files'][prefix+'author-review-input.json']or review['input_sha256']!=pv['input_sha256']or pv['review_sha256']!=d['files'][prefix+'author-author-review.json']or [r['reference']for r in inputs]!=[f'1 Enoch 20:{v}'for v in range(1,8)]:
        raise ValueError('20 original author input/result binding differs')
    if [(r['reference'],r['verdict'])for r in review['reviews']]!=[(f'1 Enoch 20:{v}','hold'if v==6 else'accept')for v in range(1,8)]:raise ValueError('20 original whole6 hold differs')
    if sorted(Path(p).name for p in manifest['scan_image_sha256'])!=[f'charles-pdf{p}-300.png'for p in(88,90,92)]or any(author['personally_viewed_photos'].get(p)!=h or pv['scan_image_sha256'].get(p)!=h for p,h in manifest['scan_image_sha256'].items())or manifest['candidate_English_or_prior_votes_supplied']is not False:
        raise ValueError('20 actual API photos/count exposure differs')
    if datetime.datetime.fromisoformat(author['frozen_at_utc'])>=datetime.datetime.fromisoformat(start['at'])or start['request_sha256']!=manifest['request_sha256']or project['original_full_request_sha256']!=manifest['request_sha256']or project['no_expected_count_or_author_candidate_supplied']is not True:
        raise ValueError('20 author-before-independent-API request binding differs')
    projected=project['request_projection'];images=[x for x in projected['input'][0]['content']if x['type']=='input_image']
    if projected['model']!='gpt-6-1-sol-review'or len(images)!=3 or sorted(x['image_bytes_sha256']for x in images)!=sorted(manifest['scan_image_sha256'].values())or any('image_url'in x for x in images):raise ValueError('20 hash-projected actual API image payload differs')
    if live['model']['name']!='gpt-6.1-sol'or live['model']['version']!='2026-09-29'or live['state']!='Succeeded'or terminal['status']!='completed'or terminal['model']!='gpt-6-1-sol-review'or terminal['id']!=done['id']or terminal['usage']!=done['usage']or terminal['usage']['total_tokens']!=3959:raise ValueError('20 actual provider terminal/model/usage differs')
    texts=[x['text']for row in terminal['output']for x in row.get('content',[])if x.get('type')=='output_text']
    if texts!=[t.artifact(t.ROOT,prefix+'raw-model-text.json').read_text()]or result['wording_approved']is not False or result['publication_approved']is not False:raise ValueError('20 raw structural result changed or gained wording approval')
    if len(result['chapters'])!=1:raise ValueError('20 source-only chapter scope differs')
    row=result['chapters'][0]
    if(row['chapter'],row['verdict'],row['actual_printed_unit_count'])!=(20,'accept',7)or row['uncertainties']or [u['verse']for u in row['units']]!=list(range(1,8))or any(u['pdf_pages']!=[90]for u in row['units']):raise ValueError('20 independent actual printed count/spans differ')
    return {20:{'chapter':20,'units':list(range(1,8)),'artifact':INDEX,'independent_count_confirmation':True,'kind':'original_source_first_and_blind_API_structural_count_only','wording_approval':False,'reader_release_policy_changed':False}}
