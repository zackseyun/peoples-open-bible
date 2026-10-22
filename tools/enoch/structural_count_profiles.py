"""Versioned raw structural receipt profiles; never wording/release approval."""
import json
from pathlib import Path
import re
from tools.enoch import bounded_application as t

def integer(value):
    return type(value) is int

def digest(value):
    return isinstance(value,str) and re.fullmatch('[0-9a-f]{64}',value) is not None

def photo_map(values):
    result={}
    for name,value in values.items():
        match=re.fullmatch(r'pdf(\d{3})\.png',name) if isinstance(name,str) else None
        if not match or not digest(value):
            raise ValueError('Structural photo name/digest differs')
        result[int(match[1])]=value
    return result

def chapter_counts(rows,key):
    if any(not integer(r.get('chapter')) or not integer(r.get(key)) or r[key]<1 for r in rows):
        raise ValueError('Structural chapter/count must be positive integers')
    counts={r['chapter']:r[key] for r in rows}
    if len(counts)!=len(rows):
        raise ValueError('Structural chapter count duplicated')
    return counts

PROFILES={
 'charles1906-52-69-v1':(set(range(52,70)),set(range(132,166))),
 'charles1906-91-103-excluding97-v1':(set(range(91,104))-{97},set(range(227,240))|set(range(241,255))),
}

def load(index,root=t.ROOT):
    data=json.loads(Path(index).read_text());profile=data.get('profile')
    if data.get('kind')!='enoch-paired-structural-counts-v2' or profile not in PROFILES or \
            data.get('wording_approval') is not False or data.get('reader_release_policy_changed') is not False:
        raise ValueError('Versioned count profile scope or approval limit differs')
    chapters,pages=PROFILES[profile];root=Path(root).resolve()
    def read(key):
        name=data[key]
        if name not in data['files']:raise ValueError('Unpinned count-profile input')
        return json.loads(t.artifact(root,name).read_text())
    for name,expected_digest in data['files'].items():
        if not digest(expected_digest) or t.sha(t.artifact(root,name).read_bytes())!=expected_digest:
            raise ValueError('Count-profile artifact hash differs')
    original=read('input');author=read('author_provenance');review=read('review');pv=read('provenance')
    if any(x.get('source_pdf_sha256')!=t.PRIMARY_SHA for x in (original,author,review,pv)) or \
            author.get('inventory_sha256')!=data['files'][data['input']] or \
            review.get('input_sha256')!=data['files'][data['input']] or pv.get('input_sha256')!=review.get('input_sha256') or \
            pv.get('review_sha256')!=data['files'][data['review']]:
        raise ValueError('Count-profile primary/input/result binding differs')
    if profile=='charles1906-52-69-v1':
        ids=(author.get('counter_id'),pv.get('reviewer_id'))
        if author.get('role')!='first_structural_counter' or pv.get('role')!='independent_structural_count_reviewer' or \
                review.get('reviewer_id')!=ids[1] or review.get('role')!=pv['role'] or \
                original.get('counter_id')!=ids[0] or original.get('source_count_completed_before_canonical_comparison') is not True or \
                review.get('verdict')!='agree_count_only' or \
                any(pv.get(k) is not False for k in ('wording_approval','manuscript_approval','publication_approval')):
            raise ValueError('52-69 counter roles or count-only verdict differ')
        observed=read('observed_units');photos=read('photo_hashes')
        if pv.get('observed_unit_spans_sha256')!=data['files'][data['observed_units']] or \
                pv.get('photo_hashes_sha256')!=data['files'][data['photo_hashes']]:
            raise ValueError('52-69 independent span/photo proof differs')
        counts=chapter_counts(original['chapters'],'actual_unit_count');units=original['units']
        if original.get('total_units')!=sum(counts.values()) or any(
                r.get('numbered_units')!=list(range(1,counts[r['chapter']]+1)) for r in original['chapters']) or \
                any(review.get(k) is not False for k in ('wording_approval','manuscript_approval','publication_approval')):
            raise ValueError('52-69 original total/numbered-unit scope differs')
        first=author['scan_image_sha256']
        firstmap={r['pdf_page']:(r['path'],r['sha256']) for r in first}
        secondmap={r['pdf_page']:(r['path'],r['sha256']) for r in photos}
        if len(firstmap)!=len(first) or len(secondmap)!=len(photos) or firstmap!=secondmap or set(firstmap)!=pages or \
                any(not r.get('matches_independent_rerender') or r['independent_rerender_sha256']!=r['sha256'] or
                    r.get('printed_page')!=r['pdf_page']-38 or Path(r['path']).name!=f"pdf-{r['pdf_page']:03d}.png" for r in photos):
            raise ValueError('52-69 full photo/rerender bindings differ')
        if review.get('actual_printed_units')!=sum(counts.values()) or len(review['chapter_reviews'])!=len(counts):
            raise ValueError('52-69 review total differs')
        for c,n in counts.items():
            rows=[r for r in review['chapter_reviews'] if r['chapter']==c]
            if len(rows)!=1:raise ValueError('52-69 review chapter duplicated/missing')
            r=rows[0]
            if r.get('actual_printed_units')!=n or r.get('observed_unit_numbers')!=list(range(1,n+1)) or \
                    r.get('verdict')!='agree_count_only' or any(r.get(k) is not False for k in ('wording_approval','manuscript_approval','publication_approval')):
                raise ValueError('52-69 chapter decision differs')
    else:
        ids=(author.get('reader_id'),pv.get('reader_id'))
        if author.get('role')!='first_structural_source_reader' or pv.get('role')!='independent_structural_source_reader' or \
                review.get('reader_id')!=ids[1] or review.get('role')!=pv['role'] or original.get('reader_id')!=ids[0] or \
                pv.get('author_provenance_sha256')!=data['files'][data['author_provenance']] or \
                review.get('verdict')!='accept_count_inventory_only' or review.get('chapter97_excluded') is not True or \
                review.get('unit_span_equality_checked') is not True or \
                any(review.get(k) is not False for k in ('wording_approval','chapter_publication_approved','full_book_verified')):
            raise ValueError('91-103 counter roles or exclusion/count-only decision differ')
        counts=chapter_counts(original['chapters'],'actual_count')
        summary=original.get('summary',{})
        if summary.get('printed_units')!=sum(counts.values()) or summary.get('chapters')!=len(counts) or \
                summary.get('counts_by_chapter')!={str(c):n for c,n in counts.items()} or \
                original.get('scope',{}).get('chapters')!=sorted(chapters) or \
                original.get('scope',{}).get('excluded_chapters')!=[97]:
            raise ValueError('91-103 original total/exclusion scope differs')
        units=[u for r in original['chapters'] for u in r['units']];observed=review['units']
        if {int(c):n for c,n in review['chapter_counts'].items()}!=counts or set(review['body_photos_inspected'])!=pages or \
                len(review['body_photos_inspected'])!=len(pages):
            raise ValueError('91-103 observed counts/full-page scope differ')
        first=author['scan_image_sha256'];second=pv['scan_image_sha256']
        firstmap=photo_map(first)
        secondmap=photo_map(second)
        if set(secondmap)!=pages or not pages<=set(firstmap) or set(firstmap)-pages!={226,240} or \
                any(firstmap[p]!=secondmap[p] for p in pages):
            raise ValueError('91-103 actual body/context photo bindings differ')
        photos=[{'sha256':v} for v in secondmap.values()]
    if not ids[0] or not ids[1] or ids[0]==ids[1] or set(counts)!=chapters or \
            any(not digest(r['sha256']) for r in photos):
        raise ValueError('Structural identity/scope/photo digest differs')
    def normalized(rows):
        out=[]
        for row in rows:
            c,v=t.parse_ref(row['reference']);pp=row['pdf_pages']
            if ('chapter' in row and (not integer(row['chapter']) or row['chapter']!=c)) or \
                    ('verse' in row and (not integer(row['verse']) or row['verse']!=v)):
                raise ValueError('Structural explicit unit identity differs')
            if not isinstance(pp,list) or any(not integer(p) for p in pp) or c not in chapters or not pp or pp!=sorted(set(pp)) or not set(pp)<=pages or \
                    pp!=list(range(pp[0],pp[-1]+1)) or \
                    ('printed_pages' in row and row['printed_pages']!=[p-38 for p in pp]):
                raise ValueError('Structural unit identity/page span differs')
            out.append((c,v,pp))
        return out
    a,b=normalized(units),normalized(observed)
    if a!=b or len(a)!=sum(counts.values()) or {p for _,_,pp in a for p in pp}!=pages:
        raise ValueError('Independent unit spans/full-page coverage differ')
    for row in original['chapters']:
        c=row['chapter'];actual=sorted({p for cc,_,pp in a if cc==c for p in pp})
        if profile=='charles1906-52-69-v1':
            if (row.get('pdf_start'),row.get('pdf_end'),row.get('printed_start'),row.get('printed_end')) != \
                    (actual[0],actual[-1],actual[0]-38,actual[-1]-38):
                raise ValueError('52-69 chapter boundary pages differ')
        elif row.get('chapter_pdf_pages')!=actual or row.get('chapter_printed_pages')!=[p-38 for p in actual]:
            raise ValueError('91-103 chapter boundary pages differ')
    output={}
    for c,n in counts.items():
        if n<1 or [(cc,v) for cc,v,_ in a if cc==c]!=[(c,v) for v in range(1,n+1)]:
            raise ValueError('Printed structural sequence is not complete')
        output[c]={'chapter':c,'units':list(range(1,n+1)),'artifact':data['review'],
                   'independent_count_confirmation':True,'kind':'paired_structural_only_not_wording_or_reader_release_approval'}
    return output
