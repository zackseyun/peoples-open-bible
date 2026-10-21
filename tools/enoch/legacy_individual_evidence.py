"""Narrow v1 adapter for the original 25:7 individual application receipt.

Old artifacts and the old applied Git record stay immutable. Only an explicitly
bound, freshly paired metadata/reason-enum successor can replace that record.
This does not invent a legacy manifest or upgrade old chapter-wide acceptance.
"""
import copy
import json
from pathlib import Path
import subprocess
import yaml
from tools.enoch import bounded_application as transaction

NAME='enoch_25_7_20261017'
REFERENCE='1 Enoch 25:7'
COMMIT='e535f38cf637133f09519899049fbf374c44a29c'
INDEX_REL='sources/enoch/coverage/legacy-individuals/enoch25-7-v1.json'
INDEX_SHA='956233815d45c238750a370f39fc1a61bd26fba33cf5c1f199caf9ccdbdefa05'
HISTORY_ROOT=transaction.ROOT
SCOPE='workflow_and_footnote_reason_enum_only'


def registered(package):
    return package.name==NAME


def read_case(package):
    if package.resolve()!=(transaction.APPLICATIONS/NAME).resolve():
        raise ValueError('Unregistered legacy individual application')
    raw=transaction.artifact(transaction.ROOT,INDEX_REL).read_bytes()
    if transaction.sha(raw)!=INDEX_SHA:
        raise ValueError('Versioned legacy artifact index differs')
    data=json.loads(raw)
    if data.get('kind')!='enoch-individual-25-7-artifacts-v1' or \
            data.get('reference')!=REFERENCE or data.get('package')!=NAME:
        raise ValueError('Legacy case identity differs')
    for name,digest in data['files'].items():
        if transaction.sha(transaction.artifact(package,name).read_bytes())!=digest:
            raise ValueError('Legacy individual artifact hash differs: '+name)
    app=json.loads((package/'application.json').read_text())
    if app.get('status')!='individual_unit_applied_chapter_held' or \
            app.get('reference')!=REFERENCE or \
            app.get('canonical_file')!='translation/extra_canonical/1_enoch/025/007.yaml' or \
            app.get('chapter_complete') is not False or app.get('review_passes')!=2:
        raise ValueError('Legacy receipt scope differs')
    return data,app


def historical_record(package):
    _,app=read_case(package)
    raw=subprocess.check_output(['git','--no-replace-objects','show',COMMIT+':'+app['canonical_file']],
                                cwd=HISTORY_ROOT)
    if transaction.sha(raw)!=app['canonical_sha256']:
        raise ValueError('Legacy applied Git record differs from receipt')
    return yaml.load(raw,Loader=transaction.LOADER)


def verify_historical(package):
    _,app=read_case(package);record=historical_record(package)
    if record.get('reference')!=REFERENCE or \
            transaction.sha(record['source']['text'].encode())!=app['source_text_sha256']:
        raise ValueError('Legacy applied source identity differs')
    for n in (1,2):
        folder=package/f'review-pass{n}'
        pv=json.loads((folder/'provenance.json').read_text())
        if pv.get('review_sha256')!=app['review_sha256'][n-1] or \
                pv['review_sha256']!=transaction.sha((folder/'review.json').read_bytes()) or \
                pv.get('scan_image_sha256')!=app['scan_sha256']:
            raise ValueError('Legacy raw review/scan provenance differs')
        for name,digest in pv['package_input_sha256'].items():
            if transaction.sha(transaction.artifact(folder,name).read_bytes())!=digest:
                raise ValueError('Legacy original input dependency differs')
        rows=json.loads((folder/'review-input.json').read_text())
        review=json.loads((folder/'review.json').read_text())
        if len(rows)!=1 or rows[0].get('reference')!=REFERENCE or \
                len(review['reviews'])!=1 or review['reviews'][0].get('reference')!=REFERENCE or \
                review['reviews'][0].get('verdict')!='accept' or review.get('chapter_complete') is not False:
            raise ValueError('Legacy exact individual verdict differs')
        row=rows[0]
        if any(row['source'].get(k)!=record['source'].get(k) for k in ('edition','language','text','pages','additional_translation_input')) or \
                row['translation']!=record['translation']:
            raise ValueError('Legacy reviewed payload differs from applied record')
    return {'references':[REFERENCE],'canonical_sha256':app['canonical_sha256'],
            'historical_review_passes':2,'historical_artifacts_verified':True,
            'full_book_verified':False,'chapter_publication_approval':False,
            'graphic_publication_approved':False,'human_specialist_certification':False}


def descriptor(package):
    data,app=read_case(package)
    return {'kind':'enoch-individual-application-v1','package':NAME,
            'receipt_sha256':data['files']['application.json'],
            'canonical_sha256':app['canonical_sha256'],'change_scope':SCOPE}


def check_metadata_payload(old,new):
    if new.get('reference')!=REFERENCE or any(old['source'].get(k)!=new['source'].get(k)
            for k in ('edition','language','text','pages','additional_translation_input')):
        raise ValueError('Legacy metadata successor changed substantive source')
    normalized=copy.deepcopy(new['translation']);before=old['translation']
    if len(normalized.get('footnotes',[]))!=len(before.get('footnotes',[])):
        raise ValueError('Legacy metadata successor changed note set')
    changes=[]
    for a,b in zip(before.get('footnotes',[]),normalized.get('footnotes',[])):
        if a.get('reason')!=b.get('reason'):
            changes.append((a.get('reason'),b.get('reason')))
            b['reason']=a.get('reason')
    if normalized!=before or changes!=[('textual_uncertainty','textual_variant')]:
        raise ValueError('Legacy successor exceeds exact enum/workflow scope')


def validate_declared_successor(package,manifest,reference):
    if reference!=REFERENCE or reference not in manifest['references']:
        raise ValueError('Unregistered legacy successor reference')
    entry=manifest['supersedes_legacy_individuals'][reference]
    old=transaction.artifact(transaction.APPLICATIONS,entry['package'])
    if old==package.resolve() or entry!=descriptor(old):
        raise ValueError('Legacy successor does not pin the exact receipt/scope')
    verify_historical(old)
    relative='025/007.yaml'
    if manifest['canonical_baseline_sha256'].get(relative)!=entry['canonical_sha256']:
        raise ValueError('Legacy successor preimage differs from receipt')
    transaction.verify_git_preimage(manifest,relative,entry['canonical_sha256'])
    candidate=yaml.load(transaction.artifact(package,'025-007.candidate.yaml').read_bytes(),Loader=transaction.LOADER)
    check_metadata_payload(historical_record(old),candidate)


def verify_applied(package):
    result=verify_historical(package)
    target=transaction.TRANSLATION/'025/007.yaml'
    if not target.exists() or transaction.sha(target.read_bytes())!=result['canonical_sha256']:
        raise ValueError('Legacy installed candidate differs')
    return {**result,'canonical_targets_checked':True}


def verify_current(package,*,seen=()):
    if NAME in seen:raise ValueError('Reviewed legacy supersession cycle')
    result=verify_historical(package);target=transaction.TRANSLATION/'025/007.yaml'
    successors=[]
    if not target.exists() or transaction.sha(target.read_bytes())!=result['canonical_sha256']:
        expected=descriptor(package);matches=[]
        for candidate in sorted(transaction.APPLICATIONS.glob('enoch_full_repair_batch*')):
            if not (candidate/'application.json').exists():continue
            m=json.loads((candidate/'manifest.json').read_text())
            if m.get('supersedes_legacy_individuals',{}).get(REFERENCE)==expected:matches.append(candidate)
        if len(matches)!=1:raise ValueError('No unique installed legacy metadata successor')
        from tools.enoch.current_evidence import verify_current as verify_new
        new=verify_new(matches[0],seen=(*seen,NAME))
        if REFERENCE not in new['references']:raise ValueError('Legacy successor omits its reference')
        successors.append({'reference':REFERENCE,'superseded_by':matches[0].name})
    historical_hash=result.pop('canonical_sha256')
    return {**result,'historical_canonical_sha256':historical_hash,
            'current_canonical_sha256':transaction.sha(target.read_bytes()),
            'canonical_targets_checked':True,
            'current_targets_or_reviewed_successors_verified':True,'reviewed_supersessions':successors}
