"""Immutable original12 parent transaction plus a detached exact successor.

The original parent editorial decision is NOT imported as exact independent
source-review evidence. No old receipt or batch13 application is rewritten.
A versioned code-pinned declaration binds fresh paired five-unit replacements
and requires held4 to remain the original bytes. Old strict verify_applied
continues to reject changed targets; its original test runs at its old tree.
"""
import json
import subprocess
import yaml
from tools.enoch import bounded_application as t

NAME = 'enoch_12_20260930'
SUCCESSOR = 'enoch_full_repair_batch13_20261023'
INDEX = 'sources/enoch/coverage/legacy-individuals/enoch12-parent-application-successor-v1.json'
INDEX_SHA = '0e25790b784b26be4959904053f972dc8fc8d8ad4b0c48278c663376d8a43ee3'


def registered(package):
    return package.name == NAME


def read_declaration():
    raw=t.artifact(t.ROOT,INDEX).read_bytes()
    if t.sha(raw)!=INDEX_SHA:
        raise ValueError('Legacy12 exact detached successor declaration differs')
    d=json.loads(raw)
    if d.get('kind')!='enoch12-parent-editorial-history-explicit-successor-v1' or \
            d.get('legacy_package')!=NAME or d.get('successor_package')!=SUCCESSOR or \
            d.get('historical_independent_review_passes_proven_by_this_adapter')!=0 or \
            d.get('changed_references')!=[f'1 Enoch 12:{v}'for v in (1,2,3,5,6)] or \
            d.get('held_reference')!='1 Enoch 12:4':
        raise ValueError('Legacy12 detached declaration scope differs')
    for path,digest in d['legacy_files'].items():
        if t.sha(t.artifact(t.ROOT,path).read_bytes())!=digest:
            raise ValueError('Legacy12 original raw artifact differs: '+path)
    return d


def verify_historical(package):
    if not registered(package)or package.resolve()!=(t.APPLICATIONS/NAME).resolve():
        raise ValueError('Unregistered legacy12 transaction')
    d=read_declaration();m=json.loads((package/'manifest.json').read_text())
    receipt=json.loads((package/'application.json').read_text())
    editorial=json.loads((package/'final-source-review.json').read_text())
    if m.get('primary_scan_sha256')!=t.PRIMARY_SHA or \
            m.get('final_source_review_sha256')!=t.sha((package/'final-source-review.json').read_bytes()) or \
            receipt.get('manifest_sha256')!=t.sha((package/'manifest.json').read_bytes()) or \
            receipt.get('status')!='applied_verified' or receipt.get('refs')!=[f'12:{v}'for v in range(1,7)]:
        raise ValueError('Legacy12 original parent manifest/receipt binding differs')
    hashes={}
    for v in range(1,7):
        name=f'012-{v:03d}';path=f'translation/extra_canonical/1_enoch/012/{v:03d}.yaml'
        raw=(package/(name+'.candidate.yaml')).read_bytes();digest=t.sha(raw)
        applied=subprocess.check_output(['git','--no-replace-objects','show',d['legacy_applied_commit']+':'+path],cwd=t.ROOT)
        record=yaml.load(raw,Loader=t.LOADER)
        if digest!=m['files'].get(name+'.candidate.yaml') or digest!=receipt['candidate_sha256'].get(name) or \
                applied!=raw or record.get('reference')!=f'1 Enoch 12:{v}' or \
                editorial['reviews'][name]['verdict']!='accept':
            raise ValueError('Legacy12 original applied candidate/editorial record differs')
        hashes[f'012/{v:03d}.yaml']=digest
    return {'references':[f'1 Enoch 12:{v}'for v in range(1,7)],
            'historical_canonical_sha256':hashes,'historical_artifacts_verified':True,
            'historical_independent_review_passes_proven':0,
            'original_parent_editorial_decisions_preserved':6,
            'historical_scope':d['historical_scope'],'full_book_verified':False,
            'chapter_publication_approval':False,'human_specialist_certification':False,
            'graphic_publication_approved':False}


def verify_current(package,*,seen=()):
    if NAME in seen:raise ValueError('Legacy12 detached successor cycle')
    d=read_declaration();old=verify_historical(package);new=t.APPLICATIONS/SUCCESSOR
    if t.sha((new/'manifest.json').read_bytes())!=d['successor_manifest_sha256']:
        raise ValueError('Legacy12 detached successor manifest differs')
    from tools.enoch.current_evidence import verify_current as verify_new
    result=verify_new(new,seen=(*seen,NAME));manifest=t.load_manifest(new)
    if not set(d['changed_references'])<=set(result['references']) or d['held_reference']in manifest['references']:
        raise ValueError('Legacy12 successor changed accepted/held scope')
    not_applied=[r for r in manifest['not_applied']if r['reference']==d['held_reference']]
    if len(not_applied)!=1 or not_applied[0]['verdicts']!=['hold','hold']:
        raise ValueError('Legacy12 whole held4 declaration differs')
    for ref in d['changed_references']:
        _,v=t.parse_ref(ref);rel=f'012/{v:03d}.yaml'
        if manifest['canonical_baseline_sha256'].get(rel)!=old['historical_canonical_sha256'][rel]:
            raise ValueError('Legacy12 explicit successor preimage differs')
        t.verify_git_preimage(manifest,rel,old['historical_canonical_sha256'][rel])
    held=t.TRANSLATION/'012/004.yaml'
    if t.sha(held.read_bytes())!=d['held_canonical_sha256'] or \
            d['held_canonical_sha256']!=old['historical_canonical_sha256']['012/004.yaml']:
        raise ValueError('Legacy12 held4 original preimage changed')
    return {**old,'canonical_targets_checked':True,
            'reviewed_supersessions':[{'reference':ref,'superseded_by':SUCCESSOR}for ref in d['changed_references']],
            'current_canonical_sha256':{f'012/{v:03d}.yaml':t.sha((t.TRANSLATION/f'012/{v:03d}.yaml').read_bytes())for v in range(1,7)},
            'held_preimage_unchanged':True,'detached_declaration_sha256':INDEX_SHA}
