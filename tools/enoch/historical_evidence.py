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
            if len(rows)!=1 or core(rows[0])!=c or verdict(read(unit['review']),reference)!='accept':
                raise ValueError('Historical actual reviewed input/result differs')
            current=transaction.TRANSLATION/f'{cv[0]:03d}/{cv[1]:03d}.yaml'
            if current.exists() and transaction.sha(current.read_bytes())==digest:
                accepted[cv]={'application':package['package'],
                              'kind':'historical_exact_accepted_input_result_current_candidate',
                              'fresh_review':False,'full_chapter_count_certified_by_import':False}
    return accepted
