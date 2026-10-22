"""Paired printed-unit counts with explicit nonidentity-addressing limits.

Greek parallels occupy intervening odd pages. A count difference (VI7 printed
units versus8 declared POB addresses) is not authority to delete an address or
to declare missing ancient text. Canonical segmentation needs its own review.
"""
import json
from pathlib import Path
import re
from tools.enoch import bounded_application as t

PROFILES={
    'charles1906-1-8-interleaved-v1':(set(range(1,9)),set(range(40,57,2)),{6}),
    'charles1906-9-14-interleaved-v1':(set(range(9,15)),set(range(56,79,2)),set()),
}

def _photos(values,pages):
    result={}
    if not isinstance(values,dict):raise ValueError('Interleaved photo map differs')
    for name,digest in values.items():
        match=re.fullmatch(r'pdf-(\d{3})\.png',Path(name).name)
        if not match or not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest):
            raise ValueError('Interleaved photo name/digest differs')
        page=int(match[1])
        if page in result:raise ValueError('Interleaved photo page duplicated')
        result[page]=digest
    if set(result)!=pages:raise ValueError('Interleaved full-photo scope differs')
    return result

def _counts(rows,key,numbered):
    if any(type(r.get('chapter')) is not int or type(r.get(key)) is not int or r[key]<1 for r in rows):
        raise ValueError('Interleaved chapter/count types differ')
    output={r['chapter']:r[key] for r in rows}
    if len(output)!=len(rows) or any(r.get(numbered)!=list(range(1,r[key]+1)) for r in rows):
        raise ValueError('Interleaved numbered scope differs')
    return output

def _spans(rows,chapters,pages):
    output=[]
    for row in rows:
        c,v=t.parse_ref(row['reference']);pp=row['pdf_pages']
        if c not in chapters or not isinstance(pp,list) or not pp or \
                any(type(p) is not int for p in pp) or pp!=sorted(set(pp)) or \
                not set(pp)<=pages or pp!=list(range(pp[0],pp[-1]+1,2)) or \
                ('printed_pages' in row and row['printed_pages']!=[p-38 for p in pp]) or \
                ('chapter' in row and (type(row['chapter']) is not int or row['chapter']!=c)) or \
                ('unit' in row and (type(row['unit']) is not int or row['unit']!=v)) or \
                ('verse' in row and (type(row['verse']) is not int or row['verse']!=v)):
            raise ValueError('Interleaved unit/page span differs')
        output.append((c,v,pp))
    return output

def load(index,root=None):
    root=Path(root or t.ROOT);data=json.loads(Path(index).read_text());profile=data.get('profile')
    if data.get('kind')!='enoch-paired-interleaved-source-counts-v1' or profile not in PROFILES or \
            any(data.get(k) is not False for k in ('wording_approval','reader_release_policy_changed','canonical_versification_changed')):
        raise ValueError('Interleaved count profile/approval scope differs')
    chapters,pages,pending=PROFILES[profile]
    if data.get('canonical_mapping_pending_chapters')!=sorted(pending):
        raise ValueError('Interleaved canonical mapping limit differs')
    if set(data.get('files',{}))!={data.get(k) for k in ('input','review','provenance','own_observation')}:
        raise ValueError('Interleaved exact artifact scope differs')
    for name,digest in data['files'].items():
        if not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest) or \
                t.sha(t.artifact(root,name).read_bytes())!=digest:
            raise ValueError('Interleaved artifact hash differs')
    read=lambda key:json.loads(t.artifact(root,data[key]).read_text())
    first,review,pv,own=[read(k) for k in ('input','review','provenance','own_observation')]
    counts=_counts(first['chapters'],'observed_unit_count','units')
    if set(counts)!=chapters or first.get('total_observed_units')!=sum(counts.values()) or \
            first.get('role')!='first_structural_source_reader' or not first.get('reviewer_id') or \
            any(x.get('source_pdf_sha256')!=t.PRIMARY_SHA for x in (first,pv)) or \
            pv.get('input_sha256')!=data['files'][data['input']] or \
            review.get('input_sha256')!=pv['input_sha256'] or \
            pv.get('review_sha256')!=data['files'][data['review']] or \
            not pv.get('reviewer_id') or pv['reviewer_id']==first['reviewer_id'] or \
            review.get('reviewer_id')!=pv['reviewer_id'] or review.get('role')!=pv.get('role') or \
            any(first.get(k) is not False for k in ('wording_approval','manuscript_approval','publication_approval','canonical_changed','count_declaration_changed')):
        raise ValueError('Interleaved primary/identity/receipt binding differs')
    photographs=_photos(first['scan_image_sha256'],pages)
    if _photos(pv['scan_image_sha256'],pages)!=photographs:
        raise ValueError('Interleaved independent photo binding differs')
    if profile=='charles1906-1-8-interleaved-v1':
        if pv.get('role')!='independent_structural_count_reviewer' or \
                review.get('source_pdf_sha256')!=t.PRIMARY_SHA or \
                pv.get('own_span_ledger_sha256')!=data['files'][data['own_observation']] or \
                review.get('own_observation_sha256')!=data['files'][data['own_observation']] or \
                own.get('reviewer_id')!=pv['reviewer_id'] or own.get('role')!=pv['role'] or \
                own.get('recorded_before_first_inventory_opened') is not True or \
                own.get('canonical_or_source_or_english_bodies_opened') is not False or \
                own.get('actual_printed_unit_counts')!={str(c):n for c,n in counts.items()} or \
                review.get('total_actual_printed_units')!=sum(counts.values()) or \
                any(pv.get(k) is not False for k in ('wording_approval','publication_approved','source_count_map_changed')) or \
                _photos(own['photo_sha256'],pages)!=photographs:
            raise ValueError('Interleaved1-8 independent observation/limits differ')
        decisions=review['chapter_reviews']
        if len(decisions)!=len(chapters) or {r['chapter'] for r in decisions}!=chapters or any(
                r.get('actual_printed_units')!=counts.get(r['chapter']) or r.get('verdict')!='accept' or
                r.get('wording_approval') is not False for r in decisions):
            raise ValueError('Interleaved1-8 chapter decision differs')
        observed=review['unit_reviews']
        if any(r.get('verdict')!='accept' or r.get('wording_approval') is not False for r in observed):
            raise ValueError('Interleaved1-8 unit decision differs')
    else:
        if pv.get('role')!='independent_structural_counter' or \
                pv.get('own_photo_observation_sha256')!=data['files'][data['own_observation']] or \
                review.get('own_observation_sha256')!=data['files'][data['own_observation']] or \
                own.get('counter_id')!=pv['reviewer_id'] or own.get('role')!='second_structural_counter' or \
                own.get('comparison_inventory_opened') is not False or \
                review.get('verdict')!='accept_structure_only' or review.get('per_unit_span_differences')!=[] or \
                review.get('counts')!={str(c):n for c,n in counts.items()} or \
                _counts(own['chapters'],'count','units')!=counts or \
                own.get('total_units')!=sum(counts.values()) or review.get('total_units')!=sum(counts.values()) or \
                any(x.get(k) is not False for x in (pv,review,own) for k in ('wording_approved','publication_approved')) or \
                review.get('chapter_translation_complete') is not False or \
                _photos(own['scan_image_sha256'],pages)!=photographs:
            raise ValueError('Interleaved9-14 independent observation/limits differ')
        observed=own['unit_spans']
    a,b=_spans(first['units'],chapters,pages),_spans(observed,chapters,pages)
    if a!=b or len(a)!=sum(counts.values()) or {p for _,_,pp in a for p in pp}!=pages:
        raise ValueError('Interleaved independent complete spans differ')
    for c,n in counts.items():
        if [(cc,v) for cc,v,_ in a if cc==c]!=[(c,v) for v in range(1,n+1)]:
            raise ValueError('Interleaved complete unit sequence differs')
    return {c:{'chapter':c,'units':list(range(1,n+1)),
               'artifact':data['review'],'independent_count_confirmation':True,
               'canonical_mapping_pending':c in pending,
               'kind':'paired_printed_source_units_not_wording_or_reader_release_approval'}
            for c,n in counts.items()}
