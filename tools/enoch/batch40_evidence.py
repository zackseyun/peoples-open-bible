"""Exact paired chapter-32 successor, with no standalone 32:6 or release waiver."""
import json
import subprocess
from tools.enoch import bounded_application as t

NAME = 'enoch_full_repair_batch40_20261105'
BASE = '46a314605d5dd37d826ebee8dc7edf23cee0de69'
MANIFEST_SHA = '2f9c8c71b39ca0aa332cc595f8fd606ad5690e2ae4a06874f2f97b1b7fbbe739'
REFS = ['1 Enoch 32:3', '1 Enoch 32:6']
CHANGED_PATHS = {'032/003.yaml','032/006.yaml'}


def historical_postmap():
    from tools.enoch import batch39_evidence as prior
    package=t.APPLICATIONS/NAME
    if t.sha((package/'manifest.json').read_bytes())!=MANIFEST_SHA:
        raise ValueError('Fixed B40 manifest differs')
    m=t.load_manifest(package)
    before=prior.historical_postmap()['current_postmap']
    if m['references']!=REFS or m['canonical_baseline_sha256']!=before or m['source_baseline_git_commit']!=BASE:
        raise ValueError('B40 exact paired scope/predecessor differs')
    new_path='032/006.yaml'
    git_path=t.TRANSLATION.relative_to(t.ROOT)/new_path
    if new_path in before or subprocess.check_output(['git','ls-tree','-r',BASE,'--',str(git_path)],cwd=t.ROOT):
        raise ValueError('B40 restoration requires exact absent 32:6 preimage')
    current=dict(before)
    for v in (3,6):
        current[f'032/{v:03d}.yaml']=m['files'][f'032-{v:03d}.candidate.yaml']
    if {k for k in current if current[k]!=before.get(k)}!=CHANGED_PATHS:
        raise ValueError('B40 changed verse scope differs')
    receipt=json.loads((package/'application.json').read_text())
    if (receipt.get('status')!='applied_verified' or receipt.get('manifest_sha256')!=MANIFEST_SHA
        or receipt.get('canonical_after_sha256')!=current or receipt.get('references')!=REFS
        or receipt.get('snapshot_file_count')!=968 or receipt.get('candidate_files')!=2
        or receipt.get('retired_references')!=[]
        or receipt.get('unrelated_canonical_files_unchanged_at_application') is not True
        or any(receipt.get(k) is not False for k in ('deployed_by_transaction','full_book_verified','graphic_publication_approved'))):
        raise ValueError('B40 exact application receipt differs')
    proof=t.verify(package,evidence_only=True)
    return {**proof,'manifest':m,'current_postmap':current,'actual_current_postmap':current}


def verify_current():
    proof=historical_postmap()
    from tools.enoch import batch41_evidence as successor
    if (t.APPLICATIONS/successor.NAME/'application.json').is_file():
        current=successor.verify_current()['actual_current_postmap']
        return {**proof,'actual_current_postmap':current,'verified_current_successor':successor.NAME}
    from tools.enoch.selected_edition_sources import REGISTRY, registry_data
    package=t.APPLICATIONS/NAME
    wanted=json.loads(subprocess.check_output(['git','show',BASE+':'+str(REGISTRY.relative_to(t.ROOT))],cwd=t.ROOT))
    wanted['units'].update({'32:3':NAME,'32:6':NAME})
    if registry_data()!=wanted:
        raise ValueError('B40 registry differs beyond 32:3 and 32:6')
    return {**proof,**t.verify(package,applied=True,check_corpus=True)}
