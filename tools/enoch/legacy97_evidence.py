"""Typed adapter for the immutable four-unit97 application, not old whole97 approval.

The unchanged original verifier runs against its exact historical four targets.
Current changes require a fresh paired all-ten successor and exact preimages.
Neither diagnostic whole-chapter rejection becomes an acceptance here.
"""
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
from tools.enoch import bounded_application as t

NAME = 'enoch_97_1_3_5_8_20261019'
VERSES = (1, 3, 5, 8)
REFS = [f'1 Enoch 97:{v}' for v in VERSES]
INDEX_REL = 'sources/enoch/coverage/legacy-individuals/enoch97-four-unit-v1.json'
INDEX_SHA = '75a74c1f96a1737ae915604703265a000b504e1f7384f80e229cadb0810a53ab'
VERIFIER = 'tools/textual_restoration/enoch_97_partial_transaction.py'
VERIFIER_SHA = 'c42ae6077a23913266b265c75c5f3d77c7d162f5d618f57c82c546ef4fd45462'


def registered(package):
    return package.name == NAME


def verify_historical(package):
    if package.resolve() != (t.APPLICATIONS/NAME).resolve():
        raise ValueError('Unregistered legacy97 package')
    raw = t.artifact(t.ROOT, INDEX_REL).read_bytes()
    if t.sha(raw) != INDEX_SHA:
        raise ValueError('Legacy97 artifact index differs')
    index = json.loads(raw)
    if index.get('kind') != 'enoch97-four-unit-historical-artifacts-v1' or \
            index.get('package') != NAME or index.get('references') != REFS or \
            index.get('accepted_individual_review_passes') != 1 or \
            index.get('diagnostic_whole_chapter_reviews_are_not_acceptances') is not True:
        raise ValueError('Legacy97 historical scope differs')
    for name, digest in index['files'].items():
        if t.sha(t.artifact(t.ROOT, name).read_bytes()) != digest:
            raise ValueError('Legacy97 historical artifact differs: '+name)
    if t.sha(t.artifact(t.ROOT, VERIFIER).read_bytes()) != VERIFIER_SHA:
        raise ValueError('Original legacy97 verifier differs')
    from tools.textual_restoration import enoch_97_partial_transaction as old
    if old.PACKAGE.resolve() != package.resolve() or \
            old.REVIEW.resolve() != (t.APPLICATIONS/'enoch_97_review_20261019/individual_1_3_5_8').resolve():
        raise ValueError('Original legacy97 verifier paths differ')
    # Only historical canonical targets are isolated. No review, receipt,
    # source PDF identity or original verifier assertion is patched or waived.
    with tempfile.TemporaryDirectory(prefix='pob97-historical-targets-') as directory:
        root = Path(directory); (root/'097').mkdir()
        for v in VERSES:
            (root/f'097/{v:03d}.yaml').write_bytes((package/f'097-{v:03d}.candidate.yaml').read_bytes())
        with patch.object(old, 'TRANSLATION', root):
            receipt = old.verify_applied()
    return {'references': REFS, 'historical_artifacts_verified': True,
            'historical_accepted_individual_review_passes': 1,
            'diagnostic_whole_chapter_reviews': 2,
            'canonical_sha256': {f'1 Enoch 97:{v}': receipt['installed_sha256'][f'097-{v:03d}'] for v in VERSES},
            'full_book_verified': False, 'chapter_publication_approval': False,
            'graphic_publication_approved': False, 'human_specialist_certification': False}


def descriptor(package, reference):
    if reference not in REFS:
        raise ValueError('Unregistered legacy97 reference')
    v = t.parse_ref(reference)[1]
    return {'kind': 'enoch97-four-unit-historical-successor-v1', 'package': NAME,
            'manifest_sha256': t.sha((package/'manifest.json').read_bytes()),
            'receipt_sha256': t.sha((package/'application.json').read_bytes()),
            'candidate_sha256': t.sha((package/f'097-{v:03d}.candidate.yaml').read_bytes()),
            'change_scope': 'fresh_paired_source_english_explanations_full97_critical_treatment'}


def validate_declared_successor(package, manifest):
    entries = manifest['supersedes_legacy97']
    if set(entries) != set(REFS) or not set(REFS) <= set(manifest['references']):
        raise ValueError('Legacy97 successor must bind all four historical units')
    full = [c for c in manifest.get('chapter_inventories', []) if c['chapter'] == 97]
    if len(full) != 1 or full[0]['units'] != list(range(1, 11)) or \
            [t.parse_ref(r)[1] for r in manifest['references'] if t.parse_ref(r)[0] == 97] != list(range(1, 11)):
        raise ValueError('Legacy97 successor requires fresh complete ten-unit treatment')
    historical = t.APPLICATIONS/NAME
    if historical.resolve() == package.resolve():
        raise ValueError('Legacy97 cannot supersede itself')
    verify_historical(historical)
    for ref, entry in entries.items():
        rel = '%03d/%03d.yaml' % t.parse_ref(ref)
        if entry != descriptor(historical, ref) or \
                manifest['canonical_baseline_sha256'].get(rel) != entry['candidate_sha256']:
            raise ValueError('Legacy97 successor receipt/scope/preimage differs')
        t.verify_git_preimage(manifest, rel, entry['candidate_sha256'])


def verify_current(package, *, seen=()):
    if NAME in seen:
        raise ValueError('Legacy97 supersession cycle')
    historical = verify_historical(package); successors = []
    for ref in REFS:
        target = t.TRANSLATION/('%03d/%03d.yaml' % t.parse_ref(ref))
        if target.exists() and t.sha(target.read_bytes()) == historical['canonical_sha256'][ref]:
            continue
        expected = descriptor(package, ref); matches = []
        for candidate in sorted(t.APPLICATIONS.glob('enoch_full_repair_batch*')):
            if not (candidate/'application.json').is_file():
                continue
            data = json.loads((candidate/'manifest.json').read_text())
            if data.get('supersedes_legacy97', {}).get(ref) == expected:
                matches.append(candidate)
        if len(matches) != 1:
            raise ValueError('No unique installed paired legacy97 successor: '+ref)
        from tools.enoch.current_evidence import verify_current as verify_new
        result = verify_new(matches[0], seen=(*seen, NAME))
        if ref not in result['references']:
            raise ValueError('Legacy97 successor omits reference')
        successors.append({'reference': ref, 'superseded_by': matches[0].name})
    historical_hashes = historical.pop('canonical_sha256')
    current_hashes = {ref: t.sha((t.TRANSLATION/('%03d/%03d.yaml' % t.parse_ref(ref))).read_bytes())
                      for ref in REFS}
    return {**historical, 'historical_canonical_sha256': historical_hashes,
            'current_canonical_sha256': current_hashes, 'canonical_targets_checked': True,
            'current_targets_or_reviewed_successors_verified': True,
            'reviewed_supersessions': successors}
