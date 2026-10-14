"""Explicit, evidence-bound print corrections and authorized PD Greek variants.

Never modifies the original page transcription or fabricates a review. Every
changed passage retains the exact former reading and primary-source receipts.
Fresh English generation and independent translation review remain required.
"""
from __future__ import annotations
import copy,json,re,unicodedata
from pathlib import Path
from tools.extra_texts import pseudo_clementine_pages as p


def normalize(text: str) -> str:
    text=re.sub(r'-\n(?=[\u0370-\u03ff\u1f00-\u1fff])','',text)
    return unicodedata.normalize('NFC',re.sub(r'\s+',' ',text).strip())


def verified_reading(evidence: dict) -> str:
    def read(relative):
        path=(p.ROOT/relative).resolve();path.relative_to(p.ROOT.resolve())
        return path
    response_path=read(evidence['response']);request_path=read(evidence['request']);receipt_path=read(evidence['receipt'])
    for name,path in [('response',response_path),('request',request_path),('receipt',receipt_path)]:
        if p.sha(path.read_bytes())!=evidence[name+'_sha256']:raise ValueError('Curation evidence changed')
    response=json.loads(response_path.read_text());request=json.loads(request_path.read_text());receipt=json.loads(receipt_path.read_text())
    if not str(response.get('model','')).startswith('gpt-6.1-sol-') or not request.get('initial_transcription_was_not_supplied'):
        raise ValueError('Curation requires independent blind Sol6.1 primary-image reading')
    if receipt.get('status')!='success' or receipt.get('request_sha256')!=request['request_sha256'] or receipt.get('response')!=response:
        raise ValueError('Curation lacks actual matching model receipt')
    output=p.parse_response(response);values=[]
    for field in evidence['fields']:
        value=output[field]
        if isinstance(value,list) and all(isinstance(v,str) for v in value):value='\n'.join(value)
        if not isinstance(value,str):raise ValueError('Curation reading field is not text')
        values.append(value)
    result=normalize('\n'.join(values))
    if not evidence.get('verified_excerpt') or evidence['verified_excerpt'] not in result:
        raise ValueError('Curation excerpt is absent from actual primary-image readback')
    return evidence['verified_excerpt']


def apply_curations(rows: list[dict]) -> list[dict]:
    path=p.SOURCE/'source-curations.json'
    if not path.exists():return rows
    result=copy.deepcopy(rows);by_ref={row['reference']:row for row in result}
    for item in json.loads(path.read_text()):
        if item['reference'] not in by_ref:continue  # scoped per-homily assembly
        if item.get('kind') not in {'primary_print_variant','verified_layout_correction'} or not item.get('authorization') or not item.get('translation_requirement'):
            raise ValueError('Undocumented or unauthorized source curation')
        if item.get('source_license')!='public_domain_print':raise ValueError('Curation cannot silently import licensed XML')
        readings=[verified_reading(e) for e in item['evidence']]
        if normalize(' '.join(readings))!=item['after']:
            raise ValueError('Curated Greek is not the verified primary-print reading')
        row=by_ref[item['reference']]
        if row['source_text'].count(item['before'])!=1:raise ValueError('Curation no longer targets exact former Greek')
        row['source_text']=row['source_text'].replace(item['before'],item['after'],1)
        row['source_text_sha256']=p.sha(row['source_text'].encode())
        row.setdefault('source_curations',[]).append(copy.deepcopy(item))
    return result
