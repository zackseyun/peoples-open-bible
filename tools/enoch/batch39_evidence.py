"""Fixed three-unit successor: two corrected and one restored unit, no release authority."""
import json
import subprocess
from tools.enoch import bounded_application as t

NAME = 'enoch_full_repair_batch39_20261105'
BASE = '661a61a3b19f2d16819a5f7cd7916f5bedc9b814'
MANIFEST_SHA = '1650c36fad62c2a9cfeb87585628ac6aef32105305cb2be308148853c423533f'
REFS = ['1 Enoch 7:3', '1 Enoch 66:1', '1 Enoch 66:2']
CHANGED_PATHS = {'007/003.yaml', '066/001.yaml', '066/002.yaml'}


def historical_postmap():
    from tools.enoch import batch38_evidence as prior
    package = t.APPLICATIONS / NAME
    if t.sha((package / 'manifest.json').read_bytes()) != MANIFEST_SHA:
        raise ValueError('Fixed B39 manifest differs')
    manifest = t.load_manifest(package)
    before = prior.historical_postmap()['current_postmap']
    if manifest['canonical_baseline_sha256'] != before or manifest['source_baseline_git_commit'] != BASE:
        raise ValueError('B39 predecessor differs')
    new_path = '066/002.yaml'
    if new_path in before or '066/001.yaml' not in before:
        raise ValueError('B39 preimage must have 66:1 and lack 66:2')
    git_path = t.TRANSLATION.relative_to(t.ROOT) / new_path
    if subprocess.check_output(['git', 'ls-tree', '-r', BASE, '--', str(git_path)], cwd=t.ROOT):
        raise ValueError('66:2 was not absent from the exact Git preimage')
    current = dict(before)
    for c,v in ((7,3),(66,1),(66,2)):
        current[f'{c:03d}/{v:03d}.yaml'] = manifest['files'][f'{c:03d}-{v:03d}.candidate.yaml']
    if set(current)-set(before) != {new_path} or {k for k in current if current[k] != before.get(k)} != CHANGED_PATHS:
        raise ValueError('B39 verse scope differs')
    receipt = json.loads((package / 'application.json').read_text())
    if (receipt.get('status') != 'applied_verified' or receipt.get('manifest_sha256') != MANIFEST_SHA
        or receipt.get('canonical_after_sha256') != current or receipt.get('references') != REFS
        or receipt.get('snapshot_file_count') != 967 or receipt.get('candidate_files') != 3
        or receipt.get('retired_references') != []
        or receipt.get('unrelated_canonical_files_unchanged_at_application') is not True
        or any(receipt.get(k) is not False for k in ('deployed_by_transaction','full_book_verified','graphic_publication_approved'))):
        raise ValueError('B39 receipt differs')
    proof = t.verify(package, evidence_only=True)
    return {**proof, 'manifest': manifest, 'current_postmap': current, 'actual_current_postmap': current}


def verify_current():
    proof = historical_postmap()
    from tools.enoch import batch40_evidence as successor
    if (t.APPLICATIONS/successor.NAME/'application.json').is_file():
        current=successor.verify_current()['actual_current_postmap']
        return {**proof,'actual_current_postmap':current,'verified_current_successor':successor.NAME}
    from tools.enoch.selected_edition_sources import REGISTRY, registry_data
    package=t.APPLICATIONS/NAME
    wanted = json.loads(subprocess.check_output(
        ['git','show',BASE+':'+str(REGISTRY.relative_to(t.ROOT))],cwd=t.ROOT))
    wanted['units'].update({'7:3':NAME,'66:1':NAME,'66:2':NAME})
    if registry_data() != wanted:
        raise ValueError('B39 source registry differs beyond 7:3 and 66:1–2')
    return {**proof, **t.verify(package, applied=True, check_corpus=True)}
