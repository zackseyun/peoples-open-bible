"""Six source-only counts and five exact window repairs; zero English votes."""
import copy
import datetime
import json
from pathlib import Path
import subprocess
from tools.enoch import bounded_application as t

INDEX='sources/enoch/coverage/count85-90-azure-20261024/index.json'
INDEX_SHA='a3706218e11dad4c65a971b36e279f5d8dc7812e7c2f2a4a793131b30841199c'
COUNTS={85:10,86:6,87:4,88:3,89:77,90:42}
BASE='6499ede72eea063ebc8574ff56e029bb66768f5f'
PATH='sources/enoch/ethiopic/page_map.json'
JOBS={'85-88':('resp_0351f2e3d6482c35006add15e8819c8197b13e58672d50545f',8526,list(range(200,207)),[85,86,87,88]),'89':('resp_032eba9cd60ee2cf006add1693e1e08196ae0860f82a11a4a7',18869,list(range(204,221)),[89]),'90':('resp_0123ff3ba6ffbe9e006add1625b61481948bd1e26415c825a5',12796,list(range(218,229)),[90])}


def evidence():
    raw=t.artifact(t.ROOT,INDEX).read_bytes()
    if t.sha(raw)!=INDEX_SHA:raise ValueError('85-90 fixed structural index differs')
    d=json.loads(raw);prefix=d['artifact_prefix']+'/'
    if (d.get('kind')!='enoch85-90-author-and-blind-Azure-counts-with-existing53-window-v1' or d.get('primary_pdf_sha256')!=t.PRIMARY_SHA
            or d.get('counts')!={str(c):n for c,n in COUNTS.items()} or d.get('registered_new_count_chapters')!=list(COUNTS)
            or d.get('context_only_window_chapter')!=53 or d.get('independent_count_actor_count')!=2
            or d.get('new_language_votes')!=0 or d.get('wording_approval')is not False or d.get('reader_release_policy_changed')is not False):
        raise ValueError('85-90 source-only scope differs')
    for name,digest in d['files'].items():
        if t.sha(t.artifact(t.ROOT,name).read_bytes())!=digest:raise ValueError('Original85-90 artifact differs: '+name)
    def read(name):
        if prefix+name not in d['files']:raise ValueError('Unpinned85-90 artifact')
        return json.loads(t.artifact(t.ROOT,prefix+name).read_text())
    author=read('author/author-inventory.json');pv=read('author/provenance.json');freeze=read('author/independent-freeze.json')
    if (author.get('counter_id')!=pv.get('counter_id') or author.get('source',{}).get('sha256')!=t.PRIMARY_SHA
            or pv.get('source',{}).get('sha256')!=t.PRIMARY_SHA or author['freeze_sha256']!=d['files'][prefix+'author/independent-freeze.json']
            or author.get('ambiguity_holds') or author.get('external_count_answers_consulted_before_freeze')is not False
            or author.get('english_current_yaml_prior_reviews_consulted')is not False
            or any(author.get(k)is not False for k in('wording_approval','reader_release_policy_changed','canonical_changed','git_changed'))):
        raise ValueError('85-90 source-first actual author scope differs')
    if (freeze['counter_id']!=author['counter_id'] or freeze['source_sha256']!=t.PRIMARY_SHA
            or freeze['counts']!={str(c):n for c,n in COUNTS.items()} or freeze['frozen_at_utc']!=author['independent_counts_frozen_at_utc']
            or any(freeze.get(k)is not False for k in('external_count_answers_consulted_before_freeze','english_current_yaml_prior_reviews_consulted','wording_approval','reader_release_policy_changed','canonical_changed'))):
        raise ValueError('85-90 original cold freeze differs')
    photos=pv['all_actually_viewed_images'];photo_map={r['pdf_page_1_based']:r['sha256']for r in photos}
    if (len(photos)!=29 or set(photo_map)!=set(range(200,229)) or any(r['actually_viewed']is not True or r['printed_page']!=r['pdf_page_1_based']-38 for r in photos)
            or {c['chapter']:c['count']for c in author['chapters']}!=COUNTS):
        raise ValueError('85-90 full photo/count binding differs')
    actual={};physical={}
    for c in author['chapters']:
        n=COUNTS[c['chapter']]
        if [u['unit']for u in c['units']]!=list(range(1,n+1)):raise ValueError('85-90 actual unit sequence differs')
        for u in c['units']:
            ref=f"{c['chapter']}:{u['unit']}";pages=[s['pdf_page_1_based']for s in u['main_text_segments']]
            if not pages or pages!=sorted(set(pages)):raise ValueError('85-90 empty/duplicate main-body span')
            intervening=u['intervening_non_main_text_pdf_pages']
            if (set(pages)&set(intervening) or sorted(pages+intervening)!=u['physical_pdf_pages_inclusive']
                    or any(p not in(213,215)for p in intervening)):
                raise ValueError('Physical Greek interleave incorrectly projected as Ethiopic body')
            actual[ref]=pages;physical[ref]=intervening
    if actual!=d['unit_pages']or len(actual)!=142 or {k:v for k,v in physical.items()if v}!={'89:48':[213],'89:57':[215]}:
        raise ValueError('85-90 main-body projection/interleaves differ')
    live=read('live-deployment.json')
    if live['properties']['model']!={'format':'OpenAI','name':'gpt-6.1-sol','version':'2026-09-29'}or live['properties']['provisioningState']!='Succeeded':
        raise ValueError('85-90 actual Azure deployment differs')
    observed={}
    for key,(response_id,tokens,pages,chapters)in JOBS.items():
        manifest=read(f'azure/{key}/request-manifest.json');start=read(f'azure/{key}/submission-started.json');project=read(f'azure/{key}/request-with-image-hashes.json')
        result=read(f'azure/{key}/raw-model-text.json');terminal=read(f'azure/{key}/provider-terminal-response.json');done=read(f'azure/{key}/completed-receipt.json')
        if (manifest.get('source_pdf_sha256')!=t.PRIMARY_SHA or manifest.get('candidate_English_or_prior_votes_supplied')is not False
                or manifest.get('logical_post_attempt_limit')!=1 or manifest['request_sha256']!=start['request_sha256']
                or project['original_full_request_sha256']!=manifest['request_sha256']or project.get('no_expected_count_or_author_candidate_supplied')is not True
                or datetime.datetime.fromisoformat(author['independent_counts_frozen_at_utc'])>=datetime.datetime.fromisoformat(start['at'])
                or {int(Path(p).stem.split('-')[1]):v for p,v in manifest['scan_image_sha256'].items()}!={p:photo_map[p]for p in pages}):
            raise ValueError('85-90 source-first/request/image exposure differs')
        request=project['request_projection'];images=[r for r in request['input'][0]['content']if r['type']=='input_image']
        if (request['model']!='gpt-6-1-sol-review'or len(images)!=len(pages)or sorted(r['image_bytes_sha256']for r in images)!=sorted(photo_map[p]for p in pages)
                or any('image_url'in r for r in images)):
            raise ValueError('85-90 actual hash-projected API images differ')
        if (terminal['status']!='completed'or terminal['id']!=response_id or terminal['id']!=done['id']or terminal['model']!='gpt-6-1-sol-review'
                or terminal['usage']!=done['usage']or terminal['usage']['total_tokens']!=tokens
                or result['wording_approved']is not False or result['publication_approved']is not False):
            raise ValueError('85-90 actual provider terminal/usage scope differs')
        texts=[r['text']for row in terminal['output']for r in row.get('content',[])if r.get('type')=='output_text']
        if texts!=[t.artifact(t.ROOT,prefix+f'azure/{key}/raw-model-text.json').read_text()]or [c['chapter']for c in result['chapters']]!=chapters:
            raise ValueError('85-90 raw provider text/chapter scope differs')
        for c in result['chapters']:
            if (c['verdict']!='accept'or c['uncertainties']or c['actual_printed_unit_count']!=COUNTS[c['chapter']]
                    or [u['verse']for u in c['units']]!=list(range(1,COUNTS[c['chapter']]+1))):
                raise ValueError('85-90 whole count not accepted')
            observed.update({f"{c['chapter']}:{u['verse']}":u['pdf_pages']for u in c['units']})
    if observed!=actual:raise ValueError('85-90 independently observed main-body spans differ')
    profile=d['existing53_paired_count_profile'];profile_raw=t.artifact(t.ROOT,profile).read_bytes()
    if t.sha(profile_raw)!=d['existing53_paired_count_profile_sha256']or json.loads(profile_raw)['files']!=d['existing53_profile_files']:
        raise ValueError('Existing53 paired source profile differs')
    from tools.enoch import structural_count_profiles
    old=structural_count_profiles.load(t.artifact(t.ROOT,profile))
    if old[53]['units']!=list(range(1,8)):raise ValueError('Existing53 source inventory incomplete')
    oldspans=json.loads(t.artifact(t.ROOT,'sources/enoch/coverage/count52-69-20261022/independent-unit-spans.json').read_text())
    spans53={str(r['verse']):r['pdf_pages']for r in oldspans if r['chapter']==53}
    if spans53!={'1':[134],'2':[134],'3':[134,135],'4':[135],'5':[135],'6':[135],'7':[135]}:
        raise ValueError('Existing53 continuation differs')
    windows={str(c):sorted({p for ref,pp in actual.items()if ref.startswith(str(c)+':')for p in pp})for c in COUNTS};windows['53']=[134,135]
    if windows!=d['chapter_pages']:raise ValueError('85-90/53 complete windows differ')
    before=read('page-map-before.json');after=read('page-map-after.json');proof=read('page-map-application-proof.json')
    if (proof['baseline_commit']!=BASE or proof['canonical_path']!=PATH
            or proof['before_sha256']!=d['files'][prefix+'page-map-before.json']or proof['after_sha256']!=d['files'][prefix+'page-map-after.json']
            or proof['source_count_scope']!=list(COUNTS)or proof['context_only_window_chapter']!=53 or proof['new_count_inventories']!=6
            or proof['new_language_votes']!=0 or proof['canonical_YAML_changes']!=0 or proof['wording_approval']is not False
            or proof['reader_release_policy_changed']is not False):
        raise ValueError('85-90/53 bounded window receipt differs')
    raw=subprocess.check_output(['git','show',BASE+':'+PATH],cwd=t.ROOT)
    if t.sha(raw)!=proof['before_sha256']:raise ValueError('85-90 actual Git predecessor map differs')
    expected=copy.deepcopy(before);changes=[]
    for c in(53,*COUNTS):
        row=expected['editions']['charles_1906']['chapters'][f'{c:03d}'];new=windows[str(c)]
        if row['pages']!=new:changes.append({'json_path':f'$.editions.charles_1906.chapters.{c:03d}.pages','before':row['pages'],'after':new});row['pages']=new
    if expected!=after or proof['changes']!=changes or len(changes)!=5:raise ValueError('85-90/53 source-window changes exceed five exact arrays')
    return d,after


def window_successor(before_sha256):
    d,_=evidence()
    if d['files'][d['artifact_prefix']+'/page-map-before.json']!=before_sha256:raise ValueError('85-90/53 window successor has a different predecessor')
    return d['files'][d['artifact_prefix']+'/page-map-after.json']


def verify_current_windows():
    d,_=evidence()
    if t.sha(t.artifact(t.ROOT,PATH).read_bytes())!=d['files'][d['artifact_prefix']+'/page-map-after.json']:
        raise ValueError('Current full source map needs an explicit reviewed window successor')
    return True


def load():
    verify_current_windows()
    return {c:{'chapter':c,'units':list(range(1,n+1)),'artifact':INDEX,'independent_count_confirmation':True,'kind':'actual_author_and_blind_Azure_source_only_count','wording_approval':False,'reader_release_policy_changed':False}for c,n in COUNTS.items()}
