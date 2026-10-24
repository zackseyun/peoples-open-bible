"""Three independent source counts and two bounded windows, no English votes."""
import copy
import datetime
import json
from pathlib import Path
import subprocess
from tools.enoch import bounded_application as t

INDEX = 'sources/enoch/coverage/count26-27-33-azure-20261024/index.json'
INDEX_SHA = 'be132c28e56eef58bd242899d5187cf515f2c7a60c08f0f981db056fa8330945'
COUNTS = {26: 6, 27: 5, 33: 4}
BASE = 'd03dadea03d61bccea631399659c794532d619fd'
PATH = 'sources/enoch/ethiopic/page_map.json'


def evidence():
    raw = t.artifact(t.ROOT, INDEX).read_bytes()
    if t.sha(raw) != INDEX_SHA:
        raise ValueError('26/27/33 fixed structural index differs')
    d = json.loads(raw)
    prefix = d['artifact_prefix'] + '/'
    if (d.get('kind') != 'enoch26-27-33-root-and-Azure-counts-with-paired17-window-v1'
            or d.get('primary_pdf_sha256') != t.PRIMARY_SHA
            or d.get('counts') != {str(c): n for c, n in COUNTS.items()}
            or d.get('registered_new_count_chapters') != [26, 27, 33]
            or d.get('context_only_window_chapter') != 17
            or d.get('independent_count_actor_count') != 2
            or d.get('wording_approval') is not False
            or d.get('reader_release_policy_changed') is not False
            or d.get('canonical_English_votes_imported') != 0):
        raise ValueError('26/27/33 structural-only scope differs')
    for path, digest in d['files'].items():
        if t.sha(t.artifact(t.ROOT, path).read_bytes()) != digest:
            raise ValueError('26/27/33 original count artifact differs: ' + path)

    def read(name):
        path = prefix + name
        if path not in d['files']:
            raise ValueError('Unpinned26/27/33 artifact')
        return json.loads(t.artifact(t.ROOT, path).read_text())

    root = read('root-source-first-ledger.json')
    manifest = read('request-manifest.json')
    start = read('submission-started.json')
    project = read('request-with-image-hashes.json')
    result = read('raw-model-text.json')
    terminal = read('provider-terminal-response.json')
    done = read('completed-receipt.json')
    live = read('live-deployment.json')
    if (root.get('reviewer_id') != '/root'
            or root.get('primary_pdf_sha256') != t.PRIMARY_SHA
            or manifest.get('source_pdf_sha256') != t.PRIMARY_SHA
            or root.get('English_or_publication_approval') is not False
            or root.get('canonical_changed') is not False
            or root['personally_viewed_actual_photos'] != manifest['scan_image_sha256']
            or manifest.get('candidate_English_or_prior_votes_supplied') is not False):
        raise ValueError('26/27/33 actual source-first/photo exposure differs')
    actual_root = {f"{c['chapter']}:{u['verse']}": u['pdf_pages']
                   for c in root['chapters'] for u in c['units']}
    if (actual_root != d['unit_pages']
            or {c['chapter']: c['actual_printed_unit_count'] for c in root['chapters']} != COUNTS
            or datetime.datetime.fromisoformat(root['at']) >= datetime.datetime.fromisoformat(start['at'])
            or start['request_sha256'] != manifest['request_sha256']
            or project['original_full_request_sha256'] != manifest['request_sha256']
            or project.get('no_expected_count_or_author_candidate_supplied') is not True):
        raise ValueError('26/27/33 root-before-independent-API binding differs')
    request = project['request_projection']
    images = [r for r in request['input'][0]['content'] if r['type'] == 'input_image']
    if (request['model'] != 'gpt-6-1-sol-review' or len(images) != 10
            or sorted(r['image_bytes_sha256'] for r in images) != sorted(manifest['scan_image_sha256'].values())
            or any('image_url' in r for r in images)):
        raise ValueError('26/27/33 actual hash-projected API images differ')
    if (live['properties']['model']['name'] != 'gpt-6.1-sol'
            or live['properties']['model']['version'] != '2026-09-29'
            or live['properties']['provisioningState'] != 'Succeeded'
            or terminal['status'] != 'completed'
            or terminal['model'] != 'gpt-6-1-sol-review'
            or terminal['id'] != 'resp_0d45f9e90159d49d006adc3dad24c08194ba4028e4d7c3bb47'
            or terminal['id'] != done['id'] or terminal['usage'] != done['usage']
            or terminal['usage']['total_tokens'] != 10892):
        raise ValueError('26/27/33 actual provider/model/usage differs')
    texts = [r['text'] for row in terminal['output'] for r in row.get('content', [])
             if r.get('type') == 'output_text']
    if (texts != [t.artifact(t.ROOT, prefix + 'raw-model-text.json').read_text()]
            or result['wording_approved'] is not False or result['publication_approved'] is not False
            or len(result['chapters']) != 3):
        raise ValueError('26/27/33 raw result changed or gained English approval')
    observed = {}
    for row in result['chapters']:
        c = row['chapter']
        if (c not in COUNTS or row['verdict'] != 'accept' or row['uncertainties']
                or row['actual_printed_unit_count'] != COUNTS[c]
                or [u['verse'] for u in row['units']] != list(range(1, COUNTS[c] + 1))):
            raise ValueError('26/27/33 entire printed count not accepted')
        observed.update({f"{c}:{u['verse']}": u['pdf_pages'] for u in row['units']})
    if observed != d['unit_pages']:
        raise ValueError('26/27/33 independent continuation spans differ')
    # 17 is a separate two-actor source observation, not an API26/27/33 vote.
    author = read('ch17-full-author-source-first.json')
    peer = read('ch17-full-exact-peer-source-first.json')
    spans = {str(v): [84] if v < 7 else [84, 86] if v == 7 else [86] for v in range(1, 9)}
    if (author['reviewer_id'] == peer['reviewer_id'] or author['source_pdf_sha256'] != t.PRIMARY_SHA
            or author['actual_count'] != 8 or author['actual_spans'] != spans
            or peer['count'] != 8 or {str(r['unit']): r['pages'] for r in peer['spans']} != spans
            or any(author[k] is not False for k in ('current17_source_or_English_read', 'old17_review_or_votes_read', 'OCR_or_lexical_locators_read'))
            or not peer['stage'].startswith('Before candidate/current chapter17')):
        raise ValueError('Separate paired17 source count/spans differ')
    if not set(peer['personally_viewed_images'].items()) <= set(author['personally_viewed_photos'].items()):
        raise ValueError('Separate17 actual primary-photo bindings differ')
    before = read('page-map-before.json')
    after = read('page-map-after.json')
    proof = read('page-map-application-proof.json')
    if (proof['baseline_commit'] != BASE or proof['canonical_path'] != PATH
            or proof['before_sha256'] != d['files'][prefix + 'page-map-before.json']
            or proof['after_sha256'] != d['files'][prefix + 'page-map-after.json']
            or proof['wording_approval'] is not False or proof['new_language_votes'] != 0
            or proof['canonical_YAML_changes'] != 0 or proof['source_count_model_response'] != terminal['id']
            or proof['model_scope_chapters'] != [26, 27, 33]
            or proof['separate_paired17_source_ledgers'] != ['ch17-full-author-source-first.json', 'ch17-full-exact-peer-source-first.json']):
        raise ValueError('17/26 bounded source-window proof differs')
    actual = subprocess.check_output(['git', 'show', BASE + ':' + PATH], cwd=t.ROOT)
    if t.sha(actual) != proof['before_sha256']:
        raise ValueError('17/26 actual Git source-window predecessor differs')
    expected = copy.deepcopy(before)
    changes = []
    for c in (17, 26):
        key = f'{c:03d}'
        row = expected['editions']['charles_1906']['chapters'][key]
        new = d['chapter_pages'][str(c)]
        changes.append({'json_path': f'$.editions.charles_1906.chapters.{key}.pages', 'before': row['pages'], 'after': new})
        row['pages'] = new
    if expected != after or proof['changes'] != changes:
        raise ValueError('17/26 source-window edits exceed two exact arrays')
    return d, after


def window_successor(before_sha256):
    d, _ = evidence()
    if d['files'][d['artifact_prefix'] + '/page-map-before.json'] != before_sha256:
        raise ValueError('17/26 typed window successor has a different predecessor')
    return d['files'][d['artifact_prefix'] + '/page-map-after.json']


def verify_current_windows():
    d, after = evidence()
    raw = t.artifact(t.ROOT, PATH).read_bytes()
    from tools.enoch.count85_90_evidence import window_successor as last_window
    expected = last_window(d['files'][d['artifact_prefix'] + '/page-map-after.json'])
    if t.sha(raw) != expected:
        raise ValueError('Current full source map needs an explicit reviewed window successor')
    return True


def load():
    verify_current_windows()
    return {c: {'chapter': c, 'units': list(range(1, n + 1)), 'artifact': INDEX,
                'independent_count_confirmation': True,
                'kind': 'actual_root_and_blind_Azure_structural_count_only',
                'wording_approval': False, 'reader_release_policy_changed': False}
            for c, n in COUNTS.items()}
