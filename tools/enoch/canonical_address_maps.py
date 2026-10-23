"""Selected print to POB addressing, separately paired from wording review.

VI has seven printed units and eight existing POB addresses. The final printed
unit has an explicitly reviewed head/coda split. Never delete an address, invent
a printed8, or grant wording approval from this structural mapping certificate.
"""
import copy
import json
from pathlib import Path
import re
import subprocess
import yaml
from tools.enoch import bounded_application as t

INDEX='sources/enoch/coverage/canonical-address-mapping6-20261023/mapping-index-v1.json'
INDEX_SHA='ea0b7f90f7096bf407075f8908d6ae75e8e2451470448b2888444082176285f2'
BASE='c0fe2efffb4ebe23968f8931df3d51fc04a918d6'


def load_chapter6():
    raw=t.artifact(t.ROOT,INDEX).read_bytes()
    if t.sha(raw)!=INDEX_SHA:raise ValueError('Canonical6 mapping index differs')
    d=json.loads(raw)
    if d.get('kind')!='enoch6-seven-print-eight-address-map-v1' or \
            d.get('primary_pdf_sha256')!=t.PRIMARY_SHA or type(d.get('source_count'))is not int or \
            d.get('source_count')!=7 or type(d.get('canonical_address_count'))is not int or \
            d.get('canonical_address_count')!=8 or d.get('wording_approval')is not False or \
            d.get('reader_release_policy_changed')is not False:
        raise ValueError('Canonical6 mapping counts/approval limits differ')
    for path,digest in d['files'].items():
        if t.sha(t.artifact(t.ROOT,path).read_bytes())!=digest:
            raise ValueError('Canonical6 raw mapping artifact differs: '+path)
    def read(key):
        if d.get(key)not in d['files']:raise ValueError('Canonical6 mapping dependency unpinned')
        return json.loads(t.artifact(t.ROOT,d[key]).read_text())
    inp,author,ap,peer,pv=[read(k)for k in ('input','author_review','author_provenance','review','provenance')]
    refs=[f'1 Enoch 6:{v}'for v in range(1,9)]
    if inp.get('base_commit')!=BASE or inp.get('source_pdf_sha256')!=t.PRIMARY_SHA or \
            inp.get('source_count')!=7 or inp.get('canonical_address_count')!=8 or \
            inp.get('wording_approval')is not False or inp.get('publication_approval')is not False:
        raise ValueError('Canonical6 original input scope differs')
    if ap.get('role')!='author' or pv.get('role')!='independent_reviewer' or \
            not ap.get('reviewer_id')or ap['reviewer_id']==pv.get('reviewer_id') or \
            inp.get('author_id')!=ap['reviewer_id']:
        raise ValueError('Canonical6 distinct source/mapping identities differ')
    for result,proof,key in ((author,ap,'author_review'),(peer,pv,'review')):
        if result.get('reviewer_id')!=proof['reviewer_id'] or \
                proof.get('input_sha256')!=d['files'][d['input']] or \
                result.get('input_sha256')!=proof['input_sha256'] or \
                proof.get('review_sha256')!=d['files'][d[key]] or \
                proof.get('source_pdf_sha256')!=t.PRIMARY_SHA or \
                not isinstance(proof.get('scan_image_sha256'),dict) or not proof['scan_image_sha256'] or \
                any(not re.fullmatch('[0-9a-f]{64}',v)for v in proof['scan_image_sha256'].values()):
            raise ValueError('Canonical6 exact source/input/review binding differs')
    if author.get('verdict')!='accept_mapping_only' or author.get('wording_approval')is not False or \
            peer.get('mapping_verdict')!='accept' or peer.get('adverse_findings')!=[] or \
            any(peer.get(k)is not False for k in ('wording_approval','english_approval','notes_approval','publication_approval','full_chapter_translation_approval')) or \
            any(peer.get(k)is not True for k in ('mapping_hold_may_be_cleared','no_overlap_or_dropped_printed_segment','heading_VII_excluded','page54_no_chapterVI_continuation')):
        raise ValueError('Canonical6 mapping-only decisions differ')
    if [(r.get('printed_unit'),r.get('verdict'))for r in peer['printed_unit_reviews']]!=[(v,'accept')for v in range(1,8)] or peer.get('canonical_references')!=refs:
        raise ValueError('Canonical6 independent complete mapping scope differs')
    rows=inp['canonical_to_print']
    if [r['reference']for r in rows]!=refs:raise ValueError('Canonical6 address sequence differs')
    expected=[(v,[f'1 Enoch 6:{v}'],'whole')for v in range(1,7)]+[(7,refs[6:],'ordered_contiguous_head_and_coda')]
    if [(r['printed_unit'],r['pob_references'],r['coverage'])for r in inp['print_to_pob']]!=expected:
        raise ValueError('Canonical6 head/coda crosswalk differs')
    split=inp['print_to_pob'][-1]['split']
    if split.get('page')!=52 or split.get('printed_marker8_present')is not False or split.get('before')!='እሉ፡ እሙንቱ፡':
        raise ValueError('Canonical6 editorial split locator differs')
    # These are the immutable exposed historical preimages, not new source or
    # current-English certificates. Later legitimate wording repairs may differ.
    for v,row in enumerate(rows,1):
        path=f'translation/extra_canonical/1_enoch/006/{v:03d}.yaml'
        raw=subprocess.check_output(['git','--no-replace-objects','show',BASE+':'+path],cwd=t.ROOT)
        record=yaml.load(raw,Loader=t.LOADER)
        expected_pages=[50]if v<=5 else [50,52]if v==6 else [52]
        segment='whole_printed_unit'if v<=6 else 'head_before_unnumbered_coda'if v==7 else 'unnumbered_coda_of_printed_unit7'
        if row.get('canonical_path')!=path or t.sha(raw)!=row['canonical_file_sha256'] or \
                record['source']['text']!=row['canonical_source_text'] or \
                t.sha(record['source']['text'].encode())!=row['canonical_source_text_sha256'] or \
                record['source']['pages']!=row['canonical_source_pages'] or \
                row.get('selected_edition_pages')!=expected_pages or \
                row.get('selected_edition_printed_unit')!=min(v,7) or \
                row.get('selected_edition_segment')!=segment or row.get('mapping_verdict')!='accept' or \
                row.get('wording_approval')is not False:
            raise ValueError('Canonical6 historical preimage/segment differs')
        a=author['unit_reviews'][v-1]
        if a.get('reference')!=row['reference']or a.get('selected_edition_printed_unit')!=min(v,7) or \
                a.get('selected_edition_segment')!=segment or a.get('verdict')!='accept' or a.get('wording_approval')is not False:
            raise ValueError('Canonical6 author complete mapping scope differs')
    return {'chapter':6,'selected_printed_units':list(range(1,8)),
            'canonical_address_units':list(range(1,9)),'mapping_artifact':d['review'],
            'canonical_mapping_pending':False,'wording_approval':False,
            'reader_release_policy_changed':False,'source_input_sha256':d['files'][d['input']]}


def apply_reviewed_maps(inventories):
    proof=load_chapter6();output=copy.deepcopy(inventories)
    old=output.get(6)
    if not old or old.get('units')!=proof['selected_printed_units']or old.get('canonical_mapping_pending')is not True:
        raise ValueError('Canonical6 mapping does not match unchanged printed-count certificate')
    old.update(canonical_address_units=proof['canonical_address_units'],
               raw_canonical_mapping_pending=True,canonical_mapping_pending=False,
               canonical_mapping_resolution=proof)
    return output


def reviewed_boundary_label(chapter,verse):
    if (chapter,verse)==(6,8):
        load_chapter6()
        return 'reviewed POB editorial boundary within Charles printed unit7; no printed numeral8'
    return 'reviewed printed unit boundary'
