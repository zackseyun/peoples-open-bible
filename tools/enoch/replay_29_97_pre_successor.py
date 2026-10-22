"""Run exact unchanged old29/97 tests at their pinned pre-successor tree.

No historical pass is current source approval. Require the installed, verified
full29/full97 and named17 successors before this narrow sixteen-case replay.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from tools.enoch import bounded_application as t
from tools.enoch.replay_84_pre_critical_gate import CHILD
from tools.textual_restoration.replay_unflagged_sample import git, extract_regular

COMMIT = '49ed7c66243a8e7697d684dad283b07dbf93666c'
SUCCESSOR = 'enoch_full_repair_batch11_20261022'
DESCRIPTOR = t.ROOT/'sources/enoch/coverage/frozen-mechanical-gates/29-97-pre-critical-successor-v1.json'
CASES = {'29:test_full_two_unit_printed_source_and_review_bindings': ('tests/test_enoch_29_transaction.py', 'test_enoch_29_transaction.Enoch29Transaction.test_full_two_unit_printed_source_and_review_bindings', '7c9836299a09ee37ff40737cc956f18e32302b946fa2c64942612189558af555'), '29:test_history_preserves_rejection_before_acceptance': ('tests/test_enoch_29_transaction.py', 'test_enoch_29_transaction.Enoch29Transaction.test_history_preserves_rejection_before_acceptance', '7c9836299a09ee37ff40737cc956f18e32302b946fa2c64942612189558af555'), '29:test_changed_review_hash_fails_closed': ('tests/test_enoch_29_transaction.py', 'test_enoch_29_transaction.Enoch29Transaction.test_changed_review_hash_fails_closed', '7c9836299a09ee37ff40737cc956f18e32302b946fa2c64942612189558af555'), '29:test_source_review_scope_never_claims_human_or_manuscript_certification': ('tests/test_enoch_29_transaction.py', 'test_enoch_29_transaction.Enoch29Transaction.test_source_review_scope_never_claims_human_or_manuscript_certification', '7c9836299a09ee37ff40737cc956f18e32302b946fa2c64942612189558af555'), '97:test_reviewed_scope_and_source_hold': ('tests/test_enoch97_partial_transaction.py', 'test_enoch97_partial_transaction.Enoch97PartialTransactionTest.test_reviewed_scope_and_source_hold', '159ce42b3e40791677b2f586a027398006527da98b11ab04cd3752b5da59085e'), '97:test_transaction_or_installed_bytes_and_export_hold': ('tests/test_enoch97_partial_transaction.py', 'test_enoch97_partial_transaction.Enoch97PartialTransactionTest.test_transaction_or_installed_bytes_and_export_hold', '159ce42b3e40791677b2f586a027398006527da98b11ab04cd3752b5da59085e'), '97:test_applied_verifier_rejects_review_and_receipt_drift': ('tests/test_enoch97_partial_transaction.py', 'test_enoch97_partial_transaction.Enoch97PartialTransactionTest.test_applied_verifier_rejects_review_and_receipt_drift', '159ce42b3e40791677b2f586a027398006527da98b11ab04cd3752b5da59085e'), '97:test_clean_checkout_can_verify_installed_evidence_but_not_apply_without_pdf': ('tests/test_enoch97_partial_transaction.py', 'test_enoch97_partial_transaction.Enoch97PartialTransactionTest.test_clean_checkout_can_verify_installed_evidence_but_not_apply_without_pdf', '159ce42b3e40791677b2f586a027398006527da98b11ab04cd3752b5da59085e'), '97:test_present_bad_primary_pdf_is_not_skipped_by_installed_verification': ('tests/test_enoch97_partial_transaction.py', 'test_enoch97_partial_transaction.Enoch97PartialTransactionTest.test_present_bad_primary_pdf_is_not_skipped_by_installed_verification', '159ce42b3e40791677b2f586a027398006527da98b11ab04cd3752b5da59085e'), '97:test_source_identity_is_pinned_even_when_primary_binary_is_absent': ('tests/test_enoch97_partial_transaction.py', 'test_enoch97_partial_transaction.Enoch97PartialTransactionTest.test_source_identity_is_pinned_even_when_primary_binary_is_absent', '159ce42b3e40791677b2f586a027398006527da98b11ab04cd3752b5da59085e'), 'inventory97': ('tests/test_enoch_completeness.py', 'test_enoch_completeness.EnochCompletenessTest.test_chapter_97_tenth_unit_is_declared_but_not_complete', '5277f1aead4ae3a58737ebf5992709fdd2675fb9beca9c6e768e4aa001cfb17a'), 'historical29': ('tests/test_enoch_historical_evidence.py', 'test_enoch_historical_evidence.HistoricalEvidenceTest.test_exact29_older_units_are_imported_without_fresh_review_claim', 'c5574bdb221c3a27a9f3fc631c11a00536fd887da64343489761f30664091af9'), 'historical-drift': ('tests/test_enoch_historical_evidence.py', 'test_enoch_historical_evidence.HistoricalEvidenceTest.test_current_canonical_drift_is_not_approved_by_old_review', 'c5574bdb221c3a27a9f3fc631c11a00536fd887da64343489761f30664091af9'), 'historical-raw': ('tests/test_enoch_historical_raw_receipts.py', 'test_enoch_historical_raw_receipts.HistoricalRawReceiptsTest.test_exact_original_output8_unit_bindings_do_not_approve_other_units', '58731d415a70975531a041074535d7e3b74e6b3d75d0ad19d4edb49de92f2d27'), 'legacy17': ('tests/test_enoch_low_risk_transaction.py', 'test_enoch_low_risk_transaction.EnochLowRiskTransactionTest.test_frozen_source_and_review_package', '24465153c92605c0afdff10f7eca1543b25a2bee485593638bef456b8135574d'), 'raw17-continuation': ('tests/test_enoch_verse_inventory.py', 'test_enoch_verse_inventory.EnochVerseInventoryTest.test_cross_file_continuation_is_not_lost', 'd513d8edf18d0ce5b28506f0401bba24715a2bd192fe3d254427f24823df8536')}


def replay(case):
    if sys.flags.optimize or case not in CASES:
        raise ValueError('Historical29/97 replay needs a registered case and non-optimized Python')
    data = json.loads(DESCRIPTOR.read_text())
    expected = {'kind': 'enoch29-97-pre-critical-successor-gates-v1', 'commit': COMMIT,
                'successor': SUCCESSOR, 'cases': {k: {'test': v[0], 'method': v[1],
                'test_sha256': v[2], 'expected_tests': 1} for k, v in CASES.items()}}
    if data != expected:
        raise ValueError('Historical29/97 descriptor differs')
    if git(t.ROOT, 'rev-parse', '--verify', COMMIT+'^{commit}').decode().strip() != COMMIT:
        raise ValueError('Historical29/97 commit unavailable')
    for test, _, digest in set(CASES.values()):
        if t.sha(git(t.ROOT, 'show', COMMIT+':'+test)) != digest:
            raise ValueError('Unchanged historical29/97 test source differs')
    from tools.enoch.current_evidence import verify_current
    package = t.APPLICATIONS/SUCCESSOR
    if not (package/'application.json').is_file():
        raise ValueError('Installed paired full29/full97 successor missing')
    current = verify_current(package)
    manifest = t.load_manifest(package)
    required = {f'1 Enoch {c}:{v}' for c, n in ((29, 2), (97, 10)) for v in range(1, n+1)}
    required.update({'1 Enoch 17:7', '1 Enoch 17:8'})
    certificates = {c['chapter']: c['units'] for c in manifest['chapter_inventories']}
    if not required <= set(current['references']) or \
            certificates.get(29) != [1, 2] or certificates.get(97) != list(range(1, 11)):
        raise ValueError('Installed paired full29/full97 successor missing')
    names = git(t.ROOT, 'ls-tree', '-r', '--name-only', COMMIT).decode().splitlines()
    roots = ('tools', 'lib', 'schema', 'shared', 'data', 'sources/enoch',
             'sources/early_christian_texts', 'translation/extra_canonical/1_enoch')
    paths = [r for r in roots if any(n.startswith(r+'/') for n in names)]
    paths += sorted({'/'.join(n.split('/')[:4]) for n in names
                     if n.startswith('sources/textual_restoration/applications/enoch')})
    paths += sorted({v[0] for v in CASES.values()})
    with tempfile.TemporaryDirectory(prefix='pob29-97-pre-successor-') as directory:
        extract_regular(git(t.ROOT, 'archive', '--format=tar', COMMIT, '--', *paths), Path(directory))
        env = dict(os.environ, GIT_DIR=git(t.ROOT, 'rev-parse', '--absolute-git-dir').decode().strip(),
                   GIT_WORK_TREE=directory, GIT_NO_LAZY_FETCH='1')
        env.pop('GIT_INDEX_FILE', None)
        child = subprocess.run([sys.executable, '-I', '-c', CHILD, CASES[case][1]],
                               cwd=directory, env=env, capture_output=True, text=True, timeout=900)
    if child.returncode:
        raise ValueError('Unchanged historical29/97 case failed: '+child.stderr[-8000:])
    result = json.loads(child.stdout)
    if result != {'passed': True, 'tests_run': 1, 'skipped': 0, 'expected_failures': 0}:
        raise ValueError('Historical29/97 original coverage differs')
    return {**result, 'commit': COMMIT, 'original_test_sha256': CASES[case][2],
            'current_corpus_validated': False, 'publication_approved': False}


if __name__ == '__main__':
    print(json.dumps(replay(sys.argv[1]), indent=2))
