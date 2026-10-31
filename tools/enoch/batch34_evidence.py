"""Exact B33 historical postmap followed only by the fixed fresh44 treatment.

This is not a generic later-edit waiver. Missing receipts, changed artifacts,
wrong predecessor maps and any unrelated canonical drift still fail closed.
"""
import json
from tools.enoch import bounded_application as t, count41_44_evidence as count

NAME = 'enoch_full_repair_batch34_20261031'
MANIFEST_SHA = '53d842f144cef8646a66ad64ac7b94d1b0f053773d66c79c12e841cfd99b83f9'
REF = '1 Enoch 44:1'
INPUT_SHA = 'a1149d13d2397c6f3d56e7a2c365d69c0bdd8457eb61e46104dc9b1d0f6d7e0c'
BASE = '5a6633695bfcc3264f508974c104ad556892c036'
PRIOR = 'enoch_full_repair_batch33_20261027'
PRIOR_SHA = '113b61f03934b82eca38023d0d4eb62bb3a78b0c454013d3f12bb4210d6296cc'


def prior_postmap():
    package = t.APPLICATIONS/PRIOR
    if t.sha((package/'manifest.json').read_bytes()) != PRIOR_SHA:
        raise ValueError('Fixed B33 predecessor manifest differs')
    m = t.load_manifest(package)
    expected = dict(m['canonical_baseline_sha256'])
    expected['013/006.yaml'] = m['files']['013-006.candidate.yaml']
    receipt = json.loads((package/'application.json').read_text())
    if (receipt.get('status') != 'applied_verified' or
            receipt.get('manifest_sha256') != PRIOR_SHA or
            receipt.get('canonical_after_sha256') != expected or len(expected) != 966):
        raise ValueError('Fixed B33 historical receipt/postmap differs')
    # Its own exact13:6 must remain current; disabling full-corpus comparison
    # here never allows a change to that individually owned current target.
    t.verify(package, applied=True, check_corpus=False)
    return m, expected


def verify_current():
    package = t.APPLICATIONS/NAME
    if t.sha((package/'manifest.json').read_bytes()) != MANIFEST_SHA:
        raise ValueError('Fixed B34 manifest differs')
    m = t.load_manifest(package)
    _, before = prior_postmap()
    if (m['references'] != [REF] or m['retirements'] != [] or
            m.get('supersedes') != {} or m['canonical_baseline_sha256'] != before or
            m['source_baseline_git_commit'] != BASE):
        raise ValueError('B34 does not follow exact B33 with sole44 scope')
    expected = dict(before)
    expected['044/001.yaml'] = m['files']['044-001.candidate.yaml']
    if {k for k in expected if expected[k] != before[k]} != {'044/001.yaml'}:
        raise ValueError('B34 changed-record scope differs')
    bindings = m['review_bindings'][REF]
    if len(bindings) != 2 or {m['files'][b['input']] for b in bindings} != {INPUT_SHA}:
        raise ValueError('B34 exact new whole-input pair differs')
    receipt = json.loads((package/'application.json').read_text())
    if (receipt.get('status') != 'applied_verified' or
            receipt.get('manifest_sha256') != MANIFEST_SHA or
            receipt.get('canonical_after_sha256') != expected):
        raise ValueError('B34 exact applied receipt/postmap differs')
    inventory = json.loads((package/'source-only-count-inventory.json').read_text())
    index, _ = count.evidence()
    wanted = {'chapter': 44, 'units': [1], 'pdf_pages': [122, 123],
              'basis': 'Existing immutable actual root/Azure independent structural count, not a new count or language vote.',
              'count_evidence_index': count.INDEX, 'count_evidence_index_sha256': count.INDEX_SHA}
    if (inventory.get('chapters') != [wanted] or inventory.get('new_count_votes') != 0 or
            inventory.get('wording_approval') is not False or
            inventory.get('reader_release_policy_changed') is not False or
            index['counts']['44'] != 1 or index['chapter_pages']['44'] != [122, 123] or
            t.sha((package/'original-count41-44-index.json').read_bytes()) != count.INDEX_SHA):
        raise ValueError('B34 existing structural-only count binding differs')
    proof = t.verify(package, applied=True, check_corpus=True)
    return {**proof, 'prior_historical_postmap': before, 'current_postmap': expected,
            'new_language_review_units': 1, 'new_structural_count_votes': 0}


def verify_batch33_postmap_or_fixed_successor():
    m, expected = prior_postmap()
    if (t.APPLICATIONS/NAME/'application.json').is_file():
        verify_current()
    else:
        # An unapplied B34 proposal supplies no permission to change anything.
        t.verify(t.APPLICATIONS/PRIOR, applied=True, check_corpus=True)
    return m, expected


def assert_current_progress(case, report):
    """Keep old478/36 claims unless the exact sole44 successor is installed."""
    if (t.APPLICATIONS/NAME/'application.json').is_file():
        verify_current()
        case.assertEqual(report['current_units_with_imported_review_evidence'], 479)
        case.assertEqual(len(report['chapters_with_complete_imported_selected_edition_review']), 37)
        case.assertIn(44, report['chapters_with_complete_imported_selected_edition_review'])
    else:
        case.assertEqual(report['current_units_with_imported_review_evidence'], 478)
        case.assertEqual(len(report['chapters_with_complete_imported_selected_edition_review']), 36)
