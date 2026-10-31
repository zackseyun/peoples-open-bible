"""Fixed original44 parent-editorial history, never a paired wording vote.

The original file receipt and actual before/applied Git bytes stay immutable.
A new paired application may supersede only that exact canonical preimage.
"""
import json
import subprocess
import yaml
from tools.enoch import bounded_application as t

REF = '1 Enoch 44:1'
RECEIPT = 'enoch44_1.2026-10-06.v1.json'
RECEIPT_SHA = 'ca86da66cec2848a79fe467b4244c9d475b946fa9f13c14c80c5a355546f93bf'
PATH = 'translation/extra_canonical/1_enoch/044/001.yaml'
RELATIVE = '044/001.yaml'
BASE = '21faf461feba9970d651bb70fa8d88aabeab43fe'
APPLIED = 'e978b6dc47e16886ea0c7b8efb3ee4665e457a60'
BEFORE_SHA = 'ac9c85e60f615e0f0e98ec50e3b71d21bbc8fa8849c8ac6679330e30693ed49e'
AFTER_SHA = '81006512ac9fddfaa608ef3f5b3378ddb9dcbf4b2c9cdaee2b2e729fce6fd607'
SCOPE = 'parent_editorial_cross_page_closure_only_no_paired_independent_approval'


def declaration():
    """Exact manifest supersedes_legacy44 mapping; no old manifest invented."""
    return {REF: {'kind': 'enoch44-parent-editorial-explicit-successor-v1',
                  'receipt': RECEIPT, 'receipt_sha256': RECEIPT_SHA,
                  'canonical_sha256': AFTER_SHA, 'historical_scope': SCOPE,
                  'change_scope': 'new_paired_individual_source_English_explanations'}}


def historical_bytes(*, before=False):
    commit, digest = (BASE, BEFORE_SHA) if before else (APPLIED, AFTER_SHA)
    raw = subprocess.check_output(['git', '--no-replace-objects', 'show',
                                   commit+':'+PATH], cwd=t.ROOT)
    if t.sha(raw) != digest:
        raise ValueError('Legacy44 actual historical Git record differs')
    return raw


def verify_historical():
    raw = (t.APPLICATIONS/RECEIPT).read_bytes()
    if t.sha(raw) != RECEIPT_SHA:
        raise ValueError('Legacy44 original receipt hash differs')
    receipt = json.loads(raw)
    before_raw, applied_raw = historical_bytes(before=True), historical_bytes()
    parent = subprocess.check_output(['git', '--no-replace-objects', 'show',
                                     APPLIED+'^:'+PATH], cwd=t.ROOT)
    if parent != before_raw:
        raise ValueError('Legacy44 applied parent differs from original baseline')
    before = yaml.load(before_raw, Loader=t.LOADER)
    applied = yaml.load(applied_raw, Loader=t.LOADER)
    if (receipt.get('target') != PATH or receipt.get('before_sha256') != BEFORE_SHA
            or receipt.get('after_sha256') != AFTER_SHA
            or receipt.get('source_before') != before['source']['text']
            or receipt.get('source_after') != applied['source']['text']
            or receipt.get('english_before') != before['translation']['text']
            or receipt.get('english_after') != applied['translation']['text']
            or before.get('reference') != REF or applied.get('reference') != REF
            or receipt.get('canonical_reference_changed') is not False
            or receipt.get('human_specialist_review') is not False
            or receipt.get('full_corpus_or_manuscript_certified') is not False
            or receipt.get('reader_deployed') is not False):
        raise ValueError('Legacy44 original parent-editorial payload/scope differs')
    return {'references': [REF], 'historical_canonical_sha256': AFTER_SHA,
            'historical_artifacts_verified': True, 'historical_scope': SCOPE,
            'historical_independent_review_passes_proven': 0,
            'new_source_or_English_reviews': 0, 'full_book_verified': False,
            'graphic_publication_approved': False,
            'human_specialist_certification': False}


def validate_declared_successor(manifest):
    """Validate only history/preimage here; outer transaction checks new pair."""
    if manifest.get('supersedes_legacy44') != declaration() or \
            REF not in manifest.get('references', []):
        raise ValueError('Legacy44 successor declaration differs')
    verify_historical()
    if manifest.get('canonical_baseline_sha256', {}).get(RELATIVE) != AFTER_SHA:
        raise ValueError('Legacy44 successor canonical preimage differs')
    t.verify_git_preimage(manifest, RELATIVE, AFTER_SHA)
