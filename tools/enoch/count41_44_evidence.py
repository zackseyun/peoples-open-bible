"""Independent root/Azure photo counts and three source-window repairs only."""
import copy
import datetime
import json
from pathlib import Path
import subprocess
from tools.enoch import bounded_application as t

INDEX='sources/enoch/coverage/count41-44-azure-20261023/index.json'
INDEX_SHA='b94ae0842621d846a924ad5b7f5110c7d35ec80ec1932d171409e76f4eff6045'
COUNTS={41:9,42:3,43:4,44:1}
BASE='dfd1b8d7fae6dec36efebb67c0f923368150bf16'
PATH='sources/enoch/ethiopic/page_map.json'


def evidence():
    raw=t.artifact(t.ROOT,INDEX).read_bytes()
    if t.sha(raw)!=INDEX_SHA:raise ValueError('41-44 fixed structural count index differs')
    d=json.loads(raw);prefix=d['artifact_prefix']+'/'
    if d.get('kind')!='enoch41-44-root-and-azure-independent-source-counts-v1' or d.get('primary_pdf_sha256')!=t.PRIMARY_SHA or d.get('counts')!={str(c):n for c,n in COUNTS.items()} or d.get('wording_approval')is not False or d.get('reader_release_policy_changed')is not False or d.get('canonical_English_votes_imported')!=0 or d.get('independent_actor_count')!=2:
        raise ValueError('41-44 structural-only scope differs')
    for path,digest in d['files'].items():
        if t.sha(t.artifact(t.ROOT,path).read_bytes())!=digest:raise ValueError('41-44 original count artifact differs: '+path)
    def read(name):
        path=prefix+name
        if path not in d['files']:raise ValueError('Unpinned41-44 count artifact')
        return json.loads(t.artifact(t.ROOT,path).read_text())
    root=read('root-source-first-ledger.json');manifest=read('request-manifest.json');start=read('submission-started.json');terminal=read('provider-terminal-response.json');completed=read('completed-receipt.json');result=read('raw-model-text.json');live=read('live-deployment.json');project=read('request-with-image-hashes.json')
    if root.get('reviewer_id')!='/root' or root.get('source_pdf_sha256')!=t.PRIMARY_SHA or manifest.get('source_pdf_sha256')!=t.PRIMARY_SHA or root.get('counts')!=d['counts'] or root.get('unit_pages')!=d['unit_pages'] or root.get('chapter_pages')!=d['chapter_pages'] or root.get('before_current_canonical_source_English_oldreviews_OCR_or_lexical_locators')is not True or root.get('wording_approval')is not False:
        raise ValueError('41-44 root actual source-first count differs')
    if root['personally_viewed_image_sha256']!=manifest['scan_image_sha256'] or sorted(Path(p).name for p in manifest['scan_image_sha256'])!=[f'pdf{p}.png'for p in range(118,124)] or manifest['candidate_English_or_prior_votes_supplied']is not False:
        raise ValueError('41-44 actual API photo/count-exposure binding differs')
    if datetime.datetime.fromisoformat(root['at'])>=datetime.datetime.fromisoformat(start['at']) or project.get('no_expected_count_or_author_candidate_supplied')is not True or project['original_full_request_sha256']!=manifest['request_sha256'] or start['request_sha256']!=manifest['request_sha256']:
        raise ValueError('41-44 independent root-before-API request binding differs')
    projected=project['request_projection'];images=[r for r in projected['input'][0]['content']if r['type']=='input_image']
    if projected['model']!='gpt-6-1-sol-review' or len(images)!=6 or sorted(r['image_bytes_sha256']for r in images)!=sorted(manifest['scan_image_sha256'].values()) or any('image_url'in r for r in images):
        raise ValueError('41-44 hash-projected actual image payload differs')
    if live['model']['name']!='gpt-6.1-sol' or live['model']['version']!='2026-09-29' or live['state']!='Succeeded' or terminal['model']!='gpt-6-1-sol-review' or terminal['status']!='completed' or terminal['id']!=completed['id'] or terminal['usage']!=completed['usage'] or terminal['usage']['total_tokens']!=7294:
        raise ValueError('41-44 actual provider terminal/model/usage differs')
    texts=[r['text']for row in terminal['output']for r in row.get('content',[])if r.get('type')=='output_text']
    if texts!=[t.artifact(t.ROOT,prefix+'raw-model-text.json').read_text()] or result['wording_approved']is not False or result['publication_approved']is not False:
        raise ValueError('41-44 raw API result changed or gained wording approval')
    if len(result['chapters'])!=4 or {r['chapter']:r['actual_printed_unit_count']for r in result['chapters']}!=COUNTS:
        raise ValueError('41-44 independent actual model counts differ')
    observed={}
    for row in result['chapters']:
        c=row['chapter']
        if row['verdict']!='accept' or row['uncertainties'] or [u['verse']for u in row['units']]!=list(range(1,COUNTS[c]+1)):
            raise ValueError('41-44 whole structural chapter count not accepted')
        observed.update({f"{c}:{u['verse']}":u['pdf_pages']for u in row['units']})
    if observed!=d['unit_pages']:raise ValueError('41-44 independently observed continuation spans differ')
    before=read('page-map-before.json');after=read('page-map-after.json');proof=read('page-map-application-proof.json')
    if proof['baseline_commit']!=BASE or proof['canonical_path']!=PATH or proof['before_sha256']!=d['files'][prefix+'page-map-before.json'] or proof['after_sha256']!=d['files'][prefix+'page-map-after.json'] or proof['wording_approval']is not False or proof['new_language_votes']!=0 or proof['canonical_YAML_changes']!=0 or proof['source_count_model_response']!=terminal['id']:
        raise ValueError('41/42/44 bounded window receipt differs')
    actual=subprocess.check_output(['git','show',BASE+':'+PATH],cwd=t.ROOT)
    if t.sha(actual)!=proof['before_sha256']:raise ValueError('41/42/44 actual Git predecessor map differs')
    expected=copy.deepcopy(before);changes=[]
    for c in(41,42,44):
        key=f'{c:03d}';old=expected['editions']['charles_1906']['chapters'][key]['pages'];new=d['chapter_pages'][str(c)]
        changes.append({'json_path':f'$.editions.charles_1906.chapters.{key}.pages','before':old,'after':new});expected['editions']['charles_1906']['chapters'][key]['pages']=new
    if expected!=after or proof['changes']!=changes:raise ValueError('41/42/44 window change exceeds three exact arrays')
    return d,after


def load():
    verify_current_windows()
    return {c:{'chapter':c,'units':list(range(1,n+1)),'artifact':INDEX,'independent_count_confirmation':True,'kind':'actual_root_and_Azure_structural_count_only','wording_approval':False,'reader_release_policy_changed':False}for c,n in COUNTS.items()}


def verify_current_windows():
    d,after=evidence();raw=t.artifact(t.ROOT,PATH).read_bytes();current=json.loads(raw)
    # Any future legitimate map edit needs a separately pinned successor, not a
    # permissive ignore of arbitrary changes outside the three owned arrays.
    from tools.enoch.count106_108_evidence import window_successor
    expected=window_successor(d['files'][d['artifact_prefix']+'/page-map-after.json'])
    from tools.enoch.count26_27_33_evidence import window_successor as next_window
    expected=next_window(expected)
    from tools.enoch.count85_90_evidence import window_successor as last_window
    expected=last_window(expected)
    if t.sha(raw)!=expected:
        raise ValueError('Current full source map needs an explicit reviewed window successor')
    for c in(41,42,44):
        key=f'{c:03d}'
        if current['editions']['charles_1906']['chapters'][key]['pages']!=after['editions']['charles_1906']['chapters'][key]['pages']:
            raise ValueError('41/42/44 current reviewed window differs')
    return True
