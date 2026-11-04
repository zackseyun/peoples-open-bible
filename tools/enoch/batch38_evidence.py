"""Fixed single-unit 1:9 successor; no release authority."""
import json
import subprocess
from tools.enoch import bounded_application as t

NAME = 'enoch_full_repair_batch38_20261103'
BASE = 'b9e9148f63b3396c13ef2502e14353a071e3b44b'
MANIFEST_SHA = 'a2b07b8601a92c3cea051069119839e3f886f1c2168987bd86242ac47982272c'
PATH = '001/009.yaml'
CHANGED_PATHS = {PATH}
REFS = ['1 Enoch 1:9']


def verify_current():
    from tools.enoch import batch37_evidence as prior
    from tools.enoch.selected_edition_sources import REGISTRY, registry_data
    package = t.APPLICATIONS / NAME
    if t.sha((package / 'manifest.json').read_bytes()) != MANIFEST_SHA:
        raise ValueError('Fixed B38 manifest differs')
    manifest = t.load_manifest(package)
    before = prior.historical_postmap()['current_postmap']
    if manifest['canonical_baseline_sha256'] != before or manifest['source_baseline_git_commit'] != BASE:
        raise ValueError('B38 predecessor differs')
    current = dict(before)
    current[PATH] = manifest['files']['001-009.candidate.yaml']
    if {k for k in before if current[k] != before[k]} != CHANGED_PATHS:
        raise ValueError('B38 verse scope differs')
    receipt = json.loads((package / 'application.json').read_text())
    if (receipt.get('status') != 'applied_verified' or receipt.get('manifest_sha256') != MANIFEST_SHA
        or receipt.get('canonical_after_sha256') != current or receipt.get('references') != REFS
        or receipt.get('snapshot_file_count') != 966 or receipt.get('candidate_files') != 1
        or receipt.get('retired_references') != []
        or receipt.get('unrelated_canonical_files_unchanged_at_application') is not True
        or any(receipt.get(k) is not False for k in ('deployed_by_transaction','full_book_verified','graphic_publication_approved'))):
        raise ValueError('B38 receipt differs')
    wanted = json.loads(subprocess.check_output(['git','show',BASE+':'+str(REGISTRY.relative_to(t.ROOT))],cwd=t.ROOT))
    wanted['units']['1:9'] = NAME
    if registry_data() != wanted:
        raise ValueError('B38 source registry differs beyond 1:9')
    proof = t.verify(package, applied=True, check_corpus=True)
    return {**proof, 'manifest': manifest, 'current_postmap': current, 'actual_current_postmap': current}
