"""Fixed 2:2 and 3:1 successor: exact qualified pairs, unchanged address set."""
import json
import subprocess
from tools.enoch import bounded_application as t

NAME='enoch_full_repair_batch41_20261105'
BASE='73c696e97e3d001c2f5f4d579b8299cec2760690'
MANIFEST_SHA='e842468e8f80694df1c348fb79dd29c815b42eb3a192246d3dd37e10820a6f13'
REFS=['1 Enoch 2:2','1 Enoch 3:1']
CHANGED_PATHS={'002/002.yaml','003/001.yaml'}


def verify_current():
    from tools.enoch import batch40_evidence as prior
    from tools.enoch.selected_edition_sources import REGISTRY,registry_data
    p=t.APPLICATIONS/NAME
    if t.sha((p/'manifest.json').read_bytes())!=MANIFEST_SHA:
        raise ValueError('Fixed B41 manifest differs')
    m=t.load_manifest(p)
    before=prior.historical_postmap()['current_postmap']
    if m['references']!=REFS or m['canonical_baseline_sha256']!=before or m['source_baseline_git_commit']!=BASE:
        raise ValueError('B41 exact paired scope/predecessor differs')
    current=dict(before)
    for c,v in ((2,2),(3,1)):
        current[f'{c:03d}/{v:03d}.yaml']=m['files'][f'{c:03d}-{v:03d}.candidate.yaml']
    if set(current)!=set(before) or {k for k in current if current[k]!=before[k]}!=CHANGED_PATHS:
        raise ValueError('B41 existing verse scope differs')
    receipt=json.loads((p/'application.json').read_text())
    if (receipt.get('status')!='applied_verified' or receipt.get('manifest_sha256')!=MANIFEST_SHA
        or receipt.get('canonical_after_sha256')!=current or receipt.get('references')!=REFS
        or receipt.get('snapshot_file_count')!=968 or receipt.get('candidate_files')!=2
        or receipt.get('retired_references')!=[]
        or receipt.get('unrelated_canonical_files_unchanged_at_application') is not True
        or any(receipt.get(k) is not False for k in ('deployed_by_transaction','full_book_verified','graphic_publication_approved'))):
        raise ValueError('B41 exact application receipt differs')
    wanted=json.loads(subprocess.check_output(['git','show',BASE+':'+str(REGISTRY.relative_to(t.ROOT))],cwd=t.ROOT))
    wanted['units'].update({'2:2':NAME,'3:1':NAME})
    if registry_data()!=wanted:
        raise ValueError('B41 registry differs beyond 2:2 and 3:1')
    proof=t.verify(p,applied=True,check_corpus=True)
    return {**proof,'manifest':m,'current_postmap':current,'actual_current_postmap':current}
