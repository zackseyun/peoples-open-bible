"""Verify actual current targets or exact reviewed supersession chains.

Historical acceptance does not license arbitrary later changes. A replacement
must explicitly bind the old manifest, old candidate and exact preimage, retain
its own accepted inputs, and itself match current bytes or a verified successor.
Strict transaction.verify(applied=True) continues to reject changed targets.
"""
import json
from pathlib import Path

from tools.enoch import bounded_application as transaction

PREVIOUS = 'enoch_source_repairs_20261020'


def verify_current(package: Path, *, seen: tuple[str, ...] = ()) -> dict:
    name = package.name
    from tools.enoch import legacy12_evidence as legacy12
    if legacy12.registered(package):
        return legacy12.verify_current(package, seen=seen)
    from tools.enoch import legacy21_evidence as legacy21
    if legacy21.registered(package):
        return legacy21.verify_current(package, seen=seen)
    from tools.enoch import legacy32_evidence as legacy32
    if legacy32.registered(package):
        return legacy32.verify_current(package, seen=seen)
    from tools.enoch import legacy97_evidence as legacy97
    if legacy97.registered(package):
        return legacy97.verify_current(package, seen=seen)
    from tools.enoch import legacy_individual_evidence as legacy
    if legacy.registered(package):
        return legacy.verify_current(package,seen=seen)
    if name in seen:
        raise ValueError('Reviewed supersession cycle')
    seen = (*seen,name)
    if name == PREVIOUS:
        from tools.textual_restoration import enoch_20261020_transaction as previous
        if package.resolve() != previous.PACKAGE.resolve():
            raise ValueError('Earlier application path differs')
        historical = previous.verify(evidence_only=True)
        manifest = previous.load_manifest()
    else:
        historical = transaction.verify(package, evidence_only=True)
        manifest = transaction.load_manifest(package)
    receipt = json.loads((package/'application.json').read_text())
    if receipt.get('status') != 'applied_verified':
        raise ValueError('Historical application was not installed')
    manifest_hash = transaction.sha((package/'manifest.json').read_bytes())
    if name != PREVIOUS and receipt.get('manifest_sha256') != manifest_hash:
        raise ValueError('Historical receipt does not bind this manifest')
    current, superseded = [], []
    for ref in manifest['references']:
        c,v = transaction.parse_ref(ref)
        old_hash = transaction.sha((package/f'{c:03d}-{v:03d}.candidate.yaml').read_bytes())
        if receipt.get('canonical_after_sha256',{}).get(f'{c:03d}/{v:03d}.yaml') != old_hash:
            raise ValueError('Application receipt does not attest its historical candidate')
        target = transaction.TRANSLATION/f'{c:03d}/{v:03d}.yaml'
        if target.exists() and transaction.sha(target.read_bytes()) == old_hash:
            current.append(ref)
            continue
        expected = {'package':name, 'manifest_sha256':manifest_hash,
                    'candidate_sha256':old_hash}
        replacements = []
        for candidate in sorted(transaction.APPLICATIONS.glob('enoch_full_repair_batch*')):
            if not (candidate/'application.json').exists():
                continue
            data = json.loads((candidate/'manifest.json').read_text())
            if data.get('supersedes',{}).get(ref) == expected:
                replacements.append(candidate)
        if len(replacements) != 1:
            raise ValueError(f'No unique explicitly reviewed current supersession: {ref}')
        next_result = verify_current(replacements[0], seen=seen)
        if ref not in next_result['references']:
            raise ValueError('Superseding package does not cover the changed reference')
        superseded.append({'reference':ref, 'superseded_by':replacements[0].name})
        current.append(ref)
    # Retirement checks remain strict. Legitimately adding a different unit
    # here requires a new explicit addressing transaction, not resurrection.
    for row in manifest.get('retirements',[]):
        c,v = transaction.parse_ref(row['reference'])
        if (transaction.TRANSLATION/f'{c:03d}/{v:03d}.yaml').exists():
            raise ValueError(f'Retired wrong address reappeared: {row["reference"]}')
    return {**historical, 'references':current, 'canonical_targets_checked':True,
            'current_targets_or_reviewed_successors_verified':True,
            'reviewed_supersessions':superseded}
