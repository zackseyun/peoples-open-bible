"""Versioned import of historical exact input/result/current-candidate evidence.

This performs no writes, no fresh source review and no full-chapter count
certification. A legacy chapter_complete flag never closes a chapter here.
"""
import json
from pathlib import Path
import yaml
from tools.enoch import bounded_application as transaction

INDEX=transaction.ROOT/'sources/enoch/coverage/historical-input-bindings-v1.json'


def core(record):
    return {'reference':record['reference'],'source_text':record['source']['text'],
            'additional_translation_input':record['source'].get('additional_translation_input'),
            'translation':record['translation']}


def reviewed_input_core(record, serializer):
    if serializer is None:
        return core(record)
    if serializer != 'flat-source-text-v1' or 'source' in record or \
            set(record)-{'reference','source_text','translation','source_pages'} or \
            not isinstance(record.get('source_text'),str) or not record.get('source_pages'):
        raise ValueError('Historical input serializer differs')
    return {'reference':record['reference'],'source_text':record['source_text'],
            'additional_translation_input':None,'translation':record['translation']}


def verdict(review, reference):
    raw=review.get('reviews',[])
    if isinstance(raw,dict):
        items=[dict(v,reference=v.get('reference') or
                    '1 Enoch '+k.replace('-',':')) for k,v in raw.items()]
    else:items=raw
    matching=[]
    for item in items:
        try:same=transaction.parse_ref(item['reference'])==transaction.parse_ref(reference)
        except (ValueError,KeyError):continue
        if same:matching.append(item.get('verdict',item.get('decision')))
    if len(matching)!=1:raise ValueError('Historical review lacks one exact unit verdict')
    return matching[0]


def load_current(index=INDEX):
    """Return accepted *current bytes* only; missing chains raise, drift skips."""
    data=json.loads(index.read_text())
    if data.get('kind')!='enoch-historical-current-input-bindings-v1' or \
            data.get('primary_pdf_sha256')!=transaction.PRIMARY_SHA:
        raise ValueError('Historical index source/kind differs')
    accepted={};seen=set()
    for package in data['packages']:
        files=package['files']
        def path(name):
            if name not in files:raise ValueError('Unpinned historical artifact')
            return transaction.artifact(transaction.ROOT,name)
        def read(name):return json.loads(path(name).read_text())
        for name,digest in files.items():
            if transaction.sha(path(name).read_bytes())!=digest:
                raise ValueError('Historical artifact hash differs: '+name)
        manifest=read(package['manifest']);final=read(package['final_review']);receipt=read(package['receipt'])
        if receipt.get('status')!='applied_verified' or \
                receipt.get('manifest_sha256')!=files[package['manifest']] or \
                manifest.get('final_source_review_sha256')!=files[package['final_review']]:
            raise ValueError('Historical manifest/review/receipt binding differs')
        for unit in package['units']:
            reference=unit['reference'];cv=transaction.parse_ref(reference)
            if cv in seen:raise ValueError('Duplicate historical unit')
            seen.add(cv)
            name=Path(unit['candidate']).name;key=name.split('.')[0]
            digest=files[unit['candidate']]
            if digest!=unit['canonical_sha256_at_import'] or \
                    manifest['files'].get(name)!=digest or receipt['candidate_sha256'].get(key)!=digest:
                raise ValueError('Historical candidate application binding differs')
            candidate=yaml.load(path(unit['candidate']).read_bytes(),Loader=transaction.LOADER)
            c=core(candidate)
            compact=lambda x:transaction.sha(json.dumps(x,sort_keys=True,ensure_ascii=False).encode())
            expected=unit['reviewed_core_sha256']
            c3={k:v for k,v in c.items() if k!='additional_translation_input'}
            if expected not in [compact(c),compact(c3)] or \
                    final['reviewed_content_sha256'].get(key)!=expected or verdict(final,reference)!='accept':
                raise ValueError('Historical accepted core differs')
            pv=read(unit['provenance'])
            for k in unit['provenance_node'].split('.')[1:]:pv=pv[k]
            if pv.get('review_sha256')!=files[unit['review']] or \
                    set(pv['package_input_sha256'])!=set(unit['package_inputs']):
                raise ValueError('Historical raw review provenance differs')
            for input_name,rel in unit['package_inputs'].items():
                if pv['package_input_sha256'][input_name]!=files[rel]:
                    raise ValueError('Historical original package input differs')
            if pv['package_input_sha256'].get('review-input.json')!=files[unit['input']]:
                raise ValueError('Historical exact input hash differs')
            rows=[x for x in read(unit['input']) if transaction.parse_ref(x['reference'])==cv]
            if len(rows)!=1 or reviewed_input_core(rows[0],unit.get('input_serializer'))!=c or \
                    (unit.get('input_serializer')=='flat-source-text-v1' and rows[0]['source_pages']!=candidate['source']['pages']) or \
                    verdict(read(unit['review']),reference)!='accept':
                raise ValueError('Historical actual reviewed input/result differs')
            current=transaction.TRANSLATION/f'{cv[0]:03d}/{cv[1]:03d}.yaml'
            if current.exists() and transaction.sha(current.read_bytes())==digest:
                accepted[cv]={'application':package['package'],
                              'kind':'historical_exact_accepted_input_result_current_candidate',
                              'fresh_review':False,'full_chapter_count_certified_by_import':False}
    return accepted


def load_count_inventories(index=INDEX):
    """Separate newly paired actual-page counts; never infer from old labels."""
    data=json.loads(index.read_text())
    if data.get('kind')!='enoch-historical-current-input-bindings-v1' or \
            data.get('primary_pdf_sha256')!=transaction.PRIMARY_SHA:
        raise ValueError('Historical index source/kind differs')
    bundle=data.get('paired_count_review')
    if bundle is None:return {}
    if set(bundle['files'])!={bundle[k] for k in ('input','review','provenance')}:
        raise ValueError('Historical count artifact scope differs')
    def read(name):
        if name not in bundle['files']:raise ValueError('Unpinned historical count artifact')
        path=transaction.artifact(transaction.ROOT,name)
        if transaction.sha(path.read_bytes())!=bundle['files'][name]:
            raise ValueError('Historical count artifact hash differs')
        return json.loads(path.read_text())
    original=read(bundle['input']);review=read(bundle['review']);pv=read(bundle['provenance'])
    if original.get('primary_pdf_sha256')!=transaction.PRIMARY_SHA or \
            review.get('source_pdf_sha256')!=transaction.PRIMARY_SHA or \
            pv.get('source_pdf_sha256')!=transaction.PRIMARY_SHA or \
            pv.get('reviewer_id')!=review.get('reviewer_id') or \
            not pv.get('reviewer_id') or pv['reviewer_id']==original.get('reviewer_id') or \
            pv.get('role')!='independent_structural_count_reviewer' or \
            pv.get('input_sha256')!=bundle['files'][bundle['input']] or \
            review.get('input_sha256')!=pv['input_sha256'] or \
            pv.get('review_sha256')!=bundle['files'][bundle['review']] or review.get('mismatches')!=[]:
        raise ValueError('Historical paired count provenance differs')
    images=pv.get('scan_image_sha256',{})
    if not images or len(images)!=len(original.get('image_sha256',{})) or \
            {Path(p).name:h for p,h in images.items()}!=original['image_sha256']:
        raise ValueError('Historical count photographed evidence differs')
    output={}
    if len(review['reviews'])!=len(original['chapters']):
        raise ValueError('Historical count chapter scope differs')
    for chapter in original['chapters']:
        c=chapter['chapter'];units=chapter['units']
        matched=[r for r in review['reviews'] if r['chapter']==c]
        if type(c) is not int or not 1<=c<=108 or c in output or units!=list(range(1,len(units)+1)) or not units or len(matched)!=1:
            raise ValueError('Historical count addresses differ')
        r=matched[0]
        if r.get('verdict')!='accept' or r.get('parent_inventory_match') is not True or \
                r.get('printed_unit_count')!=len(units) or \
                [transaction.parse_ref(u['reference']) for u in r['units']]!=[(c,v) for v in units] or \
                any(not u.get('pdf_pages') or
                    any(type(p) is not int or p<=0 or f'pdf-{p:03d}.png' not in original['image_sha256'] for p in u['pdf_pages'])
                    for u in r['units']) or \
                sorted({p for u in r['units'] for p in u['pdf_pages']})!=chapter['main_pages']:
            raise ValueError('Historical actual unit count review differs')
        output[c]={'chapter':c,'units':units,'artifact':bundle['review'],
                   'independent_count_confirmation':True,
                   'kind':'fresh_paired_structural_count_separate_from_historical_wording_review'}
    return output


def load_all_current():
    """Import exact prior receipts only, without changing either frozen index."""
    output=load_current()
    added=load_current(transaction.ROOT/'sources/enoch/coverage/historical-input-bindings-20261022.json')
    if set(output)&set(added):raise ValueError('Historical current input scopes overlap')
    output.update(added)
    return output
