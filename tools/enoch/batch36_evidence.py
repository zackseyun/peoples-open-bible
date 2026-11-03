"""Fixed atomic96:3 successor of the unmerged B35 draft; no release waiver."""
import json
import subprocess
import yaml
from tools.enoch import bounded_application as t

NAME = 'enoch_full_repair_batch36_20261101'
MANIFEST_SHA = 'ad0d91dd03411069ddd67656ed8ae5561d83bb66ef92cc6adf26685cc7f372be'
BASE = '3ca33e73a8b5dc73b98852a1add96cbb58fb63a1'
PRIOR = 'enoch_full_repair_batch35_20261031'
PRIOR_SHA = '0949de859c43f638bc3211c601bdb1e0ea414d26b77ea86296218d9ec549a961'
REF = '1 Enoch 96:3'
REFS = [REF]
PATH = '096/003.yaml'
CHANGED_PATHS = {PATH}
INPUT_SHA = '2ab8b962dfa1eb727fdca6d0b5482cfa13abba3ec5f740236b218d26cf8cd222'
PAIRS = {
    'author': ('/root','corrective_author',
               '9107abe384cb551fbbeef5e15aabadba28dfb63ef209721c9770159c562863ac',
               'a414b028d6b7aac68163de7ee6e7f8ccbbb67d8a3ad42aa281b47aa1c0d7dd2d'),
    'independent': ('/root/author72_34_resume','independent_reviewer',
                    '91834782f13b86853e1c9a9d651338c748ace0b8a98e33fdc6867e89144401c2',
                    '524a889af6ec2ce7ad465ce9c69d8de75efb52e43b5a2a9197392611ca53ca44')}
COUNT_INDEX = 'sources/enoch/coverage/count91-103-20261022/paired-count-index-v2.json'
COUNT_SHA = 'c72f8a27a25e4f5245422740934102fe5d55dc253454ab2098c0f0b6217b932d'


def prior_postmap():
    from tools.enoch import batch35_evidence as prior
    if (prior.NAME,prior.MANIFEST_SHA) != (PRIOR,PRIOR_SHA):
        raise ValueError('Fixed B36 predecessor identity differs')
    return prior.historical_postmap()


def _pair(package, manifest):
    refs = [f'1 Enoch 96:{v}' for v in range(1,9)]
    original = json.loads((t.APPLICATIONS/PRIOR/'final/ch96/author-input.json').read_text())
    bindings = []
    for who,(identity,role,review_sha,pv_sha) in PAIRS.items():
        prefix = 'final/ch96/'+who
        binding = {'input':prefix+'-input.json','review':prefix+'-review.json',
                   'provenance':prefix+'-provenance.json','reviewer_id':identity}
        bindings.append(binding)
        if any(manifest['files'].get(binding[key]) != value for key,value in
               [('input',INPUT_SHA),('review',review_sha),('provenance',pv_sha)]):
            raise ValueError('B36 fixed full8 input/review/PV hashes differ')
        data = json.loads((package/binding['input']).read_text())
        review = json.loads((package/binding['review']).read_text())
        pv = json.loads((package/binding['provenance']).read_text())
        decisions = t.review_entries(review)
        expected = [(ref,'accept' if v == 3 or (who == 'author' and v == 1) else 'hold')
                    for v,ref in enumerate(refs,1)]
        if ([r['reference'] for r in data] != refs or
                [(r['reference'],r['verdict']) for r in decisions] != expected or
                (review.get('reviewer_id'),review.get('role')) != (identity,role) or
                (pv.get('reviewer_id'),pv.get('role')) != (identity,role) or
                pv.get('input_sha256') != INPUT_SHA or pv.get('review_sha256') != review_sha or
                pv.get('source_pdf_sha256') != t.PRIMARY_SHA or not pv.get('scan_image_sha256')):
            raise ValueError('B36 atomic scope, roles or actual view bindings differ')
        if any(data[v-1] != original[v-1] for v in [1,2,4,5,6,7,8]):
            raise ValueError('B36 changed an out-of-scope raw96 input')
        decision = decisions[2]
        if any(decision.get(k) is not True for k in
               ['source_approved','translation_approved','notes_approved','whole_unit_approved']):
            raise ValueError('B36 lacks whole source/English/all-notes approval')
    if manifest['review_bindings'][REF] != bindings:
        raise ValueError('B36 exact actor binding differs')


def historical_postmap():
    package = t.APPLICATIONS/NAME
    if t.sha((package/'manifest.json').read_bytes()) != MANIFEST_SHA:
        raise ValueError('Fixed B36 manifest differs')
    manifest = t.load_manifest(package)
    before = prior_postmap()['current_postmap']
    if (manifest['references'] != REFS or manifest['retirements'] != [] or
            manifest.get('supersedes') != {} or manifest.get('chapter_inventories') != [] or
            manifest['source_baseline_git_commit'] != BASE or
            manifest['canonical_baseline_sha256'] != before or len(before) != 966):
        raise ValueError('B36 is not the exact sole-existing96:3 successor of draft B35')
    t.verify_git_preimage(manifest,PATH,before[PATH])
    expected = dict(before)
    expected[PATH] = manifest['files']['096-003.candidate.yaml']
    if {key for key in before if before[key] != expected[key]} != CHANGED_PATHS:
        raise ValueError('B36 changed record scope differs')
    candidate = yaml.load((package/'096-003.candidate.yaml').read_bytes(), Loader=t.LOADER)
    correction = candidate['source_correction']
    if correction.get('individual_unit_application_approved') is not True or any(
            correction.get(k) is not False for k in ['selected_edition_chapter_reviewed',
            'chapter_publication_approval','full_book_verified','human_specialist_certification',
            'manuscript_witness_certification','graphic_publication_approved']):
        raise ValueError('B36 individual treatment gained chapter/publication certification')
    _pair(package,manifest)
    from tools.enoch import structural_count_profiles, count95_window_evidence
    if t.sha(t.artifact(t.ROOT,COUNT_INDEX).read_bytes()) != COUNT_SHA or \
            t.sha((package/'original-count91-103-index.json').read_bytes()) != COUNT_SHA:
        raise ValueError('B36 existing structural index differs')
    counts = structural_count_profiles.load(t.artifact(t.ROOT,COUNT_INDEX),root=t.ROOT)
    count95_window_evidence.verify_applied()
    inventory = json.loads((package/'source-only-count-inventory.json').read_text())
    wanted = {'chapter':96,'units':list(range(1,9)),'pdf_pages':[238,239],
              'count_evidence_index':COUNT_INDEX,'count_evidence_index_sha256':COUNT_SHA,
              'basis':'Existing immutable independent structural profile; heldlanguageunits do not gain approval.'}
    if (counts[96]['units'] != list(range(1,9)) or inventory.get('chapters') != [wanted] or
            inventory.get('primary_pdf_sha256') != t.PRIMARY_SHA or
            type(inventory.get('new_count_votes')) is not int or inventory['new_count_votes'] != 0 or
            inventory.get('wording_approval') is not False or
            inventory.get('reader_release_policy_changed') is not False or
            manifest.get('source_only_count_inventories') != [
                {'chapter':96,'units':list(range(1,9)),'artifact':'source-only-count-inventory.json',
                 'independent_count_confirmation':True}]):
        raise ValueError('B36 source-only count became a new vote/chapter/release waiver')
    receipt = json.loads((package/'application.json').read_text())
    if (receipt.get('status') != 'applied_verified' or
            receipt.get('manifest_sha256') != MANIFEST_SHA or
            receipt.get('canonical_after_sha256') != expected or
            receipt.get('references') != REFS or receipt.get('retired_references') != [] or
            receipt.get('candidate_files') != 1 or receipt.get('snapshot_file_count') != 966 or
            any(receipt.get(k) is not True for k in ['canonical_targets_checked','canonical_changed',
                'unrelated_canonical_files_unchanged_at_application']) or
            any(receipt.get(k) is not False for k in
                ['deployed_by_transaction','full_book_verified','graphic_publication_approved'])):
        raise ValueError('B36 applied receipt/full966 postmap differs')
    from tools.enoch.selected_edition_sources import registry_data
    if registry_data().get('units',{}).get('96:3') != NAME:
        raise ValueError('B36 own exact individual source registration differs')
    proof = t.verify(package,applied=True,check_corpus=False)
    return {**proof,'manifest':manifest,'prior_historical_postmap':before,
            'current_postmap':expected,'actual_current_postmap':expected,
            'new_language_review_units':1,'new_structural_count_votes':0}


def verify_current():
    """Only fixed, applied B37 may extend the historical B36 snapshot."""
    proof = historical_postmap()
    from tools.enoch import batch37_evidence as successor
    if (t.APPLICATIONS/successor.NAME/'application.json').is_file():
        current = successor.verify_current()['current_postmap']
        name = successor.NAME
    else:
        t.verify(t.APPLICATIONS/NAME,applied=True,check_corpus=True)
        from tools.enoch.selected_edition_sources import REGISTRY,registry_data
        wanted = json.loads(subprocess.check_output(['git','show',BASE+':'+str(REGISTRY.relative_to(t.ROOT))],cwd=t.ROOT))
        wanted.setdefault('units',{})['96:3'] = NAME
        if registry_data() != wanted:
            raise ValueError('B36 has an unapproved registry successor')
        current = proof['current_postmap']
        name = None
    return {**proof,'actual_current_postmap':current,'verified_current_successor':name}
