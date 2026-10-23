"""Exact paired astronomical-section counts, never automatic wording release."""
import json
from pathlib import Path
from tools.enoch import bounded_application as transaction

INDEX=transaction.ROOT/'sources/enoch/coverage/count72-82-20261020/paired-count-index.json'


def load_inventories(index=INDEX):
    data=json.loads(index.read_text())
    if data.get('kind')!='enoch-paired-structural-counts-72-82-v1' or data.get('wording_approval') is not False:
        raise ValueError('Structural count index scope differs')
    files=data['files']
    def read(name):
        if name not in files:raise ValueError('Unpinned structural count artifact')
        return json.loads(transaction.artifact(transaction.ROOT,name).read_text())
    for name,digest in files.items():
        if transaction.sha(transaction.artifact(transaction.ROOT,name).read_bytes())!=digest:
            raise ValueError('Structural count artifact hash differs')
    original=read(data['input']);author=read(data['author_provenance']);derivation=read(data['derivation'])
    review=read(data['review']);pv=read(data['provenance']);observed=read(data['observed_units'])
    if any(x.get('source_pdf_sha256')!=transaction.PRIMARY_SHA for x in (original,author,review,pv)) or \
            not author.get('reviewer_id') or author['reviewer_id']==pv.get('reviewer_id') or \
            pv.get('reviewer_id')!=review.get('reviewer_id') or \
            pv.get('role')!='independent_structural_count_reviewer' or \
            pv.get('input_sha256')!=files[data['input']] or review.get('input_sha256')!=pv['input_sha256'] or \
            pv.get('review_sha256')!=files[data['review']] or review.get('verdict')!='accept' or \
            author.get('inventory_sha256')!=derivation.get('original_inventory_sha256') or \
            derivation.get('structural_derivative_sha256')!=files[data['input']]:
        raise ValueError('Structural count primary/input/result provenance differs')
    images=pv.get('scan_image_sha256',[])
    declared=author.get('scan_image_sha256',{})
    if not declared or len({x['path'] for x in images})!=len(images) or \
            {x['path']:x['sha256'] for x in images}!=declared:
        raise ValueError('Structural count photo bindings differ')
    full=[x for x in images if x.get('viewed_full_page') and
          Path(x['path']).name==f"pdf-{x['pdf_page']:03d}.png"]
    if sorted(x['pdf_page'] for x in full)!=list(range(169,198)):
        raise ValueError('Structural count full-page scope differs')
    span_proofs=[x for x in pv.get('derived_artifacts',[])
                 if Path(x['path']).name==Path(data['observed_units']).name]
    if len(span_proofs)!=1 or span_proofs[0]['sha256']!=files[data['observed_units']]:
        raise ValueError('Structural independently observed span artifact differs')
    def units(rows):
        return [(r['reference'],r['chapter'],r['verse'],r['pdf_pages'],r['printed_pages']) for r in rows]
    if units(original['units'])!=units(observed) or any(r.get('wording_approval') is not False or
            r.get('structural_verdict')!='accept' for r in observed):
        raise ValueError('Independently observed unit spans differ')
    counts={int(k):v for k,v in original['actual_counts'].items()}
    if set(counts)!=set(range(72,83)) or sum(counts.values())!=original['total_printed_units'] or \
            len(observed)!=sum(counts.values()) or len(review['chapter_reviews'])!=len(counts):
        raise ValueError('Structural chapter scope differs')
    output={}
    for c,count in counts.items():
        rows=[r for r in observed if r['chapter']==c]
        matches=[r for r in review['chapter_reviews'] if r['chapter']==c]
        if [transaction.parse_ref(r['reference']) for r in rows]!=[(c,v) for v in range(1,count+1)] or \
                len(matches)!=1 or matches[0].get('actual_printed_units')!=count or \
                matches[0].get('verdict')!='accept' or matches[0].get('wording_approval') is not False:
            raise ValueError('Structural numbered-unit acceptance differs')
        output[c]={'chapter':c,'units':list(range(1,count+1)),
                   'artifact':data['review'],'independent_count_confirmation':True,
                   'kind':'paired_structural_only_not_wording_or_reader_release_approval'}
    return output


def load_all_inventories():
    """Diagnostic/progress union; never changes reader release declarations.

    Keep the original72–82 loader and its raw serializer contract intact.
    Each added profile validates its own distinct author/reader receipts.
    """
    from tools.enoch import structural_count_profiles
    output=load_inventories()
    for name in ('count52-69-20261022','count91-103-20261022'):
        index=transaction.ROOT/'sources/enoch/coverage'/name/'paired-count-index-v2.json'
        current=structural_count_profiles.load(index,transaction.ROOT)
        if set(current)&set(output):
            raise ValueError('Diagnostic structural inventory scopes overlap')
        output.update(current)
    from tools.enoch import interleaved_structural_counts
    for name in ('count1-8-20261022','count9-14-20261022'):
        index=transaction.ROOT/'sources/enoch/coverage'/name/'paired-count-index-v3.json'
        current=interleaved_structural_counts.load(index,transaction.ROOT)
        if set(current)&set(output):
            raise ValueError('Interleaved structural inventory scopes overlap')
        output.update(current)
    from tools.enoch.canonical_address_maps import apply_reviewed_maps
    return apply_reviewed_maps(output)
