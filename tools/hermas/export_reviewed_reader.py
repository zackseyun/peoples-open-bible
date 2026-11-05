#!/usr/bin/env python3
"""Export the complete reviewed Hermas reading edition without rewriting archives.

A release manifest binds each flat standard/simplified pair to an actual Azure
acceptance. Legacy nested records remain the historical artwork snapshot.
"""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.hermas.review_repair_draft import load_pair,sha,validate_result
from tools import shepherd_of_hermas as hermas

MARKER=re.compile(r'\[([a-z]|\d+)\]')

def read_json(path):return json.loads(path.read_text())

def verified_pair(row):
    receipt_path=ROOT/row['receipt']
    receipt=read_json(receipt_path)
    if sha(receipt_path.read_bytes())!=row['receipt_sha256']:
        raise ValueError('Changed review receipt')
    if receipt.get('status')!='reviewed' or receipt.get('verdicts')!={'standard':'accept','simplified':'accept'}:
        raise ValueError('Both editions require Azure acceptance')
    docs,manifest=load_pair(*(ROOT/x['path'] for x in receipt['input_manifest']))
    if manifest!=receipt['input_manifest']:raise ValueError('Reviewed pair changed')
    request_path=receipt_path.parent/'request.json'
    if sha(request_path.read_bytes())!=receipt['request_sha256']:raise ValueError('Changed review request')
    context=json.loads(read_json(request_path)['messages'][1]['content'])
    if context['input_manifest']!=manifest or context['source']!=docs[0]['source']:
        raise ValueError('Request is not bound to this source and pair')
    result_path=receipt_path.parent/'review.json';response_path=receipt_path.parent/'response.json'
    if sha(result_path.read_bytes())!=receipt['review_sha256'] or sha(response_path.read_bytes())!=receipt['response_sha256']:
        raise ValueError('Changed provider evidence')
    result=read_json(result_path);validate_result(result,docs)
    raw=read_json(response_path)
    if len(raw.get('choices',[]))!=1 or raw['choices'][0]['finish_reason']!='stop' or json.loads(raw['choices'][0]['message']['content'])!=result:
        raise ValueError('Review does not match actual provider result')
    if receipt.get('supplemental_evidence'):
        evidence=receipt['supplemental_evidence']
        if sha((ROOT/evidence['path']).read_bytes())!=evidence['file_sha256']:raise ValueError('Changed review evidence')
    return docs

def paragraphs(doc):
    text=doc['translation']['text'];notes=doc['translation'].get('footnotes',[])
    by_marker={str(n['marker']):n for n in notes}
    if len(by_marker)!=len(notes):raise ValueError('Repeated footnote marker')
    calls=set(MARKER.findall(text))
    if calls!=set(by_marker):raise ValueError(f'Orphaned/unanchored footnotes: {calls ^ set(by_marker)}')
    rows=[]
    for i,p in enumerate(re.split(r'\n\s*\n',text.strip()),1):
        if not p.strip():raise ValueError('Empty paragraph')
        out={'verse':i,'text':p.strip()}
        used=[copy.deepcopy(n) for n in notes if str(n['marker']) in MARKER.findall(p)]
        if used:out['footnotes']=used
        rows.append(out)
    return rows

def export(manifest_path):
    manifest=read_json(manifest_path)
    if manifest.get('status')!='reviewed_complete_reading_edition':raise ValueError('Unfinished release manifest')
    books=[{'name':'Shepherd of Hermas','slug':'shepherd-of-hermas','metadata':{
        'division_note':'Reader chapter IDs retain the legacy edition and reserved continuation slots. Numbered reading units are modern paragraphs; historical references appear in the text and chapter headings.',
        'edition_note':'Complete reading edition reviewed against the selected working sources. Manuscript gaps, editorial supplements and alternatives are disclosed in notes. Further critical collation remains open.',
        'historical_chapters':114,'independent_scholar_review':False,
        'reader_edition':'hermas-complete-written-20261105',
        'reference_note':'Paragraph numbers belong to this complete written edition and differ from the earlier incomplete reader. Historical section references are retained in the chapter headings and prose.',
        'artwork_note':'The graphic edition retains its earlier text snapshot. New and repaired reading paragraphs do not imply new or reassigned artwork.'},'chapters':[]} for _ in range(2)]
    seen=set();slots=set()
    for row in manifest['pairs']:
        slot=row['reader_slot']
        if type(slot)is not int or slot in slots:raise ValueError('Duplicate or invalid reader slot')
        slots.add(slot);docs=verified_pair(row);source=docs[0]['source']
        ids=[x['unit_id'] for x in source.get('source_unit_spans',[])] or [source['unit_id']]
        if seen.intersection(ids):raise ValueError('Repeated historical source coverage')
        seen.update(ids)
        for kind,book,doc in zip(['standard','simplified'],books,docs):
            verses=paragraphs(doc)
            for verse in verses:
                verse['footnote_review']='pob-hermas-complete-reading-review-v1'
                verse['source_critical']={'working_source_sha256':sha(source['text']),
                    'edition_kind':kind,'historical_units':ids,
                    'review_receipt':row['receipt']}
            book['chapters'].append({'chapter':slot,'reference':doc['reference'],'historical_units':ids,'verses':verses})
    expected={u['unit_id'] for u in hermas.load_unit_map()['units']}
    if seen!=expected or len(expected)!=114:raise ValueError(f'Incomplete historical source coverage: {expected-seen}')
    for book in books:book['chapters'].sort(key=lambda c:c['chapter'])
    return books

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    books=export(args.manifest);args.output.mkdir(parents=True,exist_ok=True)
    for name,book in zip(['standard','simplified'],books):(args.output/f'hermas-{name}.json').write_text(json.dumps(book,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'historical_chapters':114,'reader_chapters':len(books[0]['chapters']),'paragraphs':sum(len(c['verses']) for c in books[0]['chapters'])}))
if __name__=='__main__':main()
