"""Fixed whole97:1 correction of B36; no new count or release authority."""
import json
import subprocess
import yaml
from tools.enoch import bounded_application as t

NAME='enoch_full_repair_batch37_20261102'
MANIFEST_SHA='ee2cb68b9468c6844e38c28eaa76acc84acf83ff4a2a90662612babf3602d9b7'
BASE='ab73737d415d953359073b63a8eea3878af75d8c'
PRIOR='enoch_full_repair_batch36_20261101'
PRIOR_SHA='ad0d91dd03411069ddd67656ed8ae5561d83bb66ef92cc6adf26685cc7f372be'
OLD='enoch_full_repair_batch11_20261022'
OLD_SHA='4f3153e9ad27ddfc2943992c5a902f16eb4cbfc3a4ae595c1b8f177c85c15956'
REF='1 Enoch 97:1'
REFS=[REF]
PATH='097/001.yaml'
CHANGED_PATHS={PATH}
INPUT_SHA='d38815cb56afcfd82e6ee5ecbbfcae7436ffd480fdedfb53a72f4b4cc06d2f81'
PAIRS={
 'author':('/root','corrective_author','0cad65af7de6a095052f6ab8c24e155648d15186125754d09e816855ff33d134','1ce8b869f226b4a97b9cf567fb536b0032ec4ef51eacbee724a3cab3dacee921'),
 'independent':('/root/author72_34_resume','independent_reviewer','57a43a21a3823fa00f754535c250188dc7dc4d2cdf1d3fc80bb26ad1b2d2e7ee','765228f03c2b5db16a1328a1ec76d963203a2e51064846d98ee8c4637d12b229')}


def prior_postmap():
    from tools.enoch import batch36_evidence as prior
    if (prior.NAME,prior.MANIFEST_SHA)!=(PRIOR,PRIOR_SHA):
        raise ValueError('Fixed B37 predecessor identity differs')
    return prior.historical_postmap()


def _pair(package,manifest):
    refs=[f'1 Enoch 97:{v}'for v in range(1,11)]
    bindings=[]
    for who,(identity,role,review_sha,pv_sha)in PAIRS.items():
        prefix='final/ch97/'+who
        binding={'input':prefix+'-input.json','review':prefix+'-review.json','provenance':prefix+'-provenance.json','reviewer_id':identity}
        bindings.append(binding)
        if any(manifest['files'].get(binding[k])!=v for k,v in [('input',INPUT_SHA),('review',review_sha),('provenance',pv_sha)]):
            raise ValueError('B37 fixed full10 input/review/PV hashes differ')
        data=json.loads((package/binding['input']).read_text())
        review=json.loads((package/binding['review']).read_text())
        pv=json.loads((package/binding['provenance']).read_text())
        decisions=t.review_entries(review)
        if ([r['reference']for r in data]!=refs or
            [(r['reference'],r['verdict'])for r in decisions]!=[(r,'accept'if i==0 else'hold')for i,r in enumerate(refs)] or
            (review.get('reviewer_id'),review.get('role'))!=(identity,role) or
            (pv.get('reviewer_id'),pv.get('role'))!=(identity,role) or
            pv.get('input_sha256')!=INPUT_SHA or pv.get('review_sha256')!=review_sha or
            pv.get('source_pdf_sha256')!=t.PRIMARY_SHA or not pv.get('scan_image_sha256')):
            raise ValueError('B37 full10 atomic scope or roles differ')
        if any(decisions[0].get(k)is not True for k in ['source_approved','translation_approved','notes_approved','whole_unit_approved']):
            raise ValueError('B37 lacks whole source/English/all-notes approval')
    if manifest['review_bindings'][REF]!=bindings:
        raise ValueError('B37 exact actor bindings differ')


def historical_postmap():
    package=t.APPLICATIONS/NAME
    if t.sha((package/'manifest.json').read_bytes())!=MANIFEST_SHA:
        raise ValueError('Fixed B37 manifest differs')
    manifest=t.load_manifest(package)
    before=prior_postmap()['current_postmap']
    if (manifest['references']!=REFS or manifest['retirements']!=[] or manifest.get('chapter_inventories')!=[] or
        manifest['source_baseline_git_commit']!=BASE or manifest['canonical_baseline_sha256']!=before or len(before)!=966):
        raise ValueError('B37 is not the exact sole-existing97:1 successor of B36')
    t.verify_git_preimage(manifest,PATH,before[PATH])
    if manifest.get('supersedes')!={REF:{'package':OLD,'manifest_sha256':OLD_SHA,'candidate_sha256':before[PATH]}}:
        raise ValueError('B37 lacks exact immutable B11 supersession')
    expected=dict(before);expected[PATH]=manifest['files']['097-001.candidate.yaml']
    if {k for k in before if before[k]!=expected[k]}!=CHANGED_PATHS:
        raise ValueError('B37 changed-record scope differs')
    _pair(package,manifest)
    candidate=yaml.load((package/'097-001.candidate.yaml').read_bytes(),Loader=t.LOADER)
    correction=candidate['source_correction']
    if correction.get('individual_unit_application_approved')is not True or any(correction.get(k)is not False for k in
        ['selected_edition_chapter_reviewed','chapter_publication_approval','full_book_verified','human_specialist_certification','manuscript_witness_certification','graphic_publication_approved']):
        raise ValueError('B37 gained chapter/publication certification')
    old=t.APPLICATIONS/OLD;old_manifest=t.load_manifest(old)
    for original,copied in [('manifest.json','original-batch11-manifest.json'),('count-inventory.json','original-batch11-count-inventory.json')]:
        if (package/copied).read_bytes()!=(old/original).read_bytes():
            raise ValueError('B37 historical count evidence copy differs')
    if t.sha((old/'manifest.json').read_bytes())!=OLD_SHA:
        raise ValueError('B37 historical count owner differs')
    old_count=json.loads((old/'count-inventory.json').read_text())
    if ([c for c in old_count['chapters']if c['chapter']==97][0]['units']!=list(range(1,11)) or
        {'chapter':97,'units':list(range(1,11)),'artifact':'count-inventory.json','independent_count_confirmation':True}not in old_manifest['chapter_inventories']):
        raise ValueError('B37 historical97 count differs')
    inventory=json.loads((package/'source-only-count-inventory.json').read_text())
    if (inventory.get('primary_pdf_sha256')!=t.PRIMARY_SHA or inventory.get('new_count_votes')!=0 or
        inventory.get('wording_approval')is not False or inventory.get('reader_release_policy_changed')is not False or
        len(inventory.get('chapters',[]))!=1 or inventory['chapters'][0]['units']!=list(range(1,11)) or
        inventory['chapters'][0]['pdf_pages']!=[239,240,241]):
        raise ValueError('B37 count reuse became new review/release permission')
    receipt=json.loads((package/'application.json').read_text())
    if (receipt.get('status')!='applied_verified' or receipt.get('manifest_sha256')!=MANIFEST_SHA or
        receipt.get('canonical_after_sha256')!=expected or receipt.get('references')!=REFS or receipt.get('retired_references')!=[] or
        receipt.get('candidate_files')!=1 or receipt.get('snapshot_file_count')!=966 or
        any(receipt.get(k)is not True for k in ['canonical_targets_checked','canonical_changed','unrelated_canonical_files_unchanged_at_application']) or
        any(receipt.get(k)is not False for k in ['deployed_by_transaction','full_book_verified','graphic_publication_approved'])):
        raise ValueError('B37 applied receipt/full966 postmap differs')
    from tools.enoch.selected_edition_sources import registry_data
    if registry_data()['units'].get('97:1') != NAME:
        raise ValueError('B37 registration differs')
    proof=t.verify(package,applied=True,check_corpus=False)
    return {**proof,'manifest':manifest,'prior_historical_postmap':before,'current_postmap':expected,
            'actual_current_postmap':expected,'new_language_review_units':1,'new_structural_count_votes':0}


def verify_current():
    proof=historical_postmap()
    from tools.enoch import batch38_evidence as successor
    if (t.APPLICATIONS/successor.NAME/"application.json").is_file():
        current=successor.verify_current()["actual_current_postmap"]
        return {**proof,"actual_current_postmap":current,"verified_current_successor":successor.NAME}
    package=t.APPLICATIONS/NAME
    from tools.enoch.selected_edition_sources import REGISTRY,registry_data
    wanted=json.loads(subprocess.check_output(['git','show',BASE+':'+str(REGISTRY.relative_to(t.ROOT))],cwd=t.ROOT))
    wanted.setdefault('units',{})['97:1']=NAME
    if registry_data()!=wanted:
        raise ValueError('B37 registry differs beyond exact97:1 override')
    proof=t.verify(package,applied=True,check_corpus=True)
    return proof
