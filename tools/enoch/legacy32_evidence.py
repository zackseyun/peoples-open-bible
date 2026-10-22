"""Bind two distinct historical32 cases without upgrading their old scope.

32:1 was a bounded directional correction with adverse whole-unit reviews.
32:5 had two accepted individual cross-page reviews, not chapter approval.
Their raw artifacts remain immutable; current changes need new paired reviews.
"""
import json
import subprocess
import yaml
from tools.enoch import bounded_application as t

INDEX = 'sources/enoch/coverage/legacy-individuals/enoch32-two-cases-v1.json'
INDEX_SHA = '91c7d90ad4251120e6d0ee3735eeaa771c82141ab3044383a1df2b866388ea8e'
NAMES = ('enoch_32_review_hold_20261017', 'enoch_32_5_20261017')
REFS = ('1 Enoch 32:1', '1 Enoch 32:5')


def registered(package):
    return package.name in NAMES


def read_index():
    raw = t.artifact(t.ROOT, INDEX).read_bytes()
    if t.sha(raw) != INDEX_SHA:
        raise ValueError('Legacy32 artifact index differs')
    data = json.loads(raw)
    if data.get('kind') != 'enoch32-two-historical-cases-v1' or \
            set(data.get('cases', {})) != set(REFS) or \
            data.get('full_chapter_approval') is not False:
        raise ValueError('Legacy32 historical scope differs')
    for name, digest in data['files'].items():
        if t.sha(t.artifact(t.ROOT, name).read_bytes()) != digest:
            raise ValueError('Legacy32 original artifact differs: '+name)
    return data


def historical_record(reference, index=None):
    data = read_index() if index is None else index
    case = data['cases'][reference]
    c, v = t.parse_ref(reference)
    path = f'translation/extra_canonical/1_enoch/{c:03d}/{v:03d}.yaml'
    raw = subprocess.check_output(['git', '--no-replace-objects', 'show',
                                   case['applied_commit']+':'+path], cwd=t.ROOT)
    if t.sha(raw) != case['canonical_sha256']:
        raise ValueError('Legacy32 actual applied Git record differs')
    return yaml.load(raw, Loader=t.LOADER)


def verify_historical(package):
    if not registered(package) or package.resolve() != (t.APPLICATIONS/package.name).resolve():
        raise ValueError('Unregistered legacy32 package')
    data = read_index()
    ref = REFS[NAMES.index(package.name)]
    case = data['cases'][ref]
    record = historical_record(ref, data)
    app = json.loads((package/case['receipt']).read_text())
    if ref == REFS[0]:
        if app.get('status') != 'bounded_translation_correction_chapter_held' or \
                app.get('corrected_sha256') != case['canonical_sha256'] or \
                app.get('source_text_unchanged') is not True or \
                record['translation_correction'].get('scope') != 'bounded_north_and_aromatics_only':
            raise ValueError('Legacy32 north correction scope differs')
        path = 'translation/extra_canonical/1_enoch/032/001.yaml'
        raw = subprocess.check_output(['git', '--no-replace-objects', 'show',
                         case['applied_commit']+'^:'+path], cwd=t.ROOT)
        before = yaml.load(raw, Loader=t.LOADER)
        if t.sha(raw) != app['baseline_sha256'] or before['source'] != record['source']:
            raise ValueError('Legacy32 north source changed in bounded correction')
        folders = ('pass1', 'pass2', 'bounded-followup')
        expected = ('hold', 'revise', 'hold')
        historical_passes = 0
    else:
        if app.get('status') != 'individual_unit_applied_chapter_held' or \
                app.get('canonical_sha256') != case['canonical_sha256'] or \
                app.get('source_text_sha256') != t.sha(record['source']['text'].encode()) or \
                app.get('review_passes') != 2 or \
                app.get('before_sha256') != t.sha((package/'before.yaml').read_bytes()):
            raise ValueError('Legacy32 individual receipt differs')
        folders = ('review-pass1', 'review-pass2')
        expected = ('accept', 'accept')
        historical_passes = 2
    for n, (folder, verdict) in enumerate(zip(folders, expected)):
        root = package/folder
        review = json.loads((root/'review.json').read_text())
        pv = json.loads((root/'provenance.json').read_text())
        digest = t.sha((root/'review.json').read_bytes())
        if pv['review_sha256'] != digest or not pv.get('scan_image_sha256') or \
                review.get('chapter_complete') is not False:
            raise ValueError('Legacy32 review/scan provenance differs')
        if folder == 'bounded-followup':
            if app['bounded_followup_review_sha256'] != digest:
                raise ValueError('Legacy32 bounded followup hash differs')
        elif app['review_sha256'][n] != digest:
            raise ValueError('Legacy32 receipt does not bind original review')
        for name, expected_hash in pv['package_input_sha256'].items():
            if t.sha(t.artifact(root, name).read_bytes()) != expected_hash:
                raise ValueError('Legacy32 exact original input differs')
        rows = json.loads((root/'review-input.json').read_text())
        votes = [r for r in review['reviews'] if r['reference'] == ref]
        if len(votes) != 1 or votes[0]['verdict'] != verdict:
            raise ValueError('Legacy32 original adverse/accepted decision differs')
        if not historical_passes:
            expected_refs = [f'1 Enoch 32:{v}' for v in range(1, 7)] \
                if folder in ('pass1', 'pass2') else [ref]
            if [r['reference'] for r in rows] != expected_refs or \
                    [r['reference'] for r in review['reviews']] != expected_refs:
                raise ValueError('Legacy32 adverse full/individual scope differs')
        if historical_passes:
            if len(rows) != 1 or rows[0]['reference'] != ref or \
                    rows[0]['translation'] != record['translation'] or \
                    any(rows[0]['source'].get(k) != record['source'].get(k)
                        for k in ('edition', 'language', 'text', 'pages')):
                raise ValueError('Legacy32 individual reviewed payload differs')
    return {'references': [ref], 'historical_artifacts_verified': True,
            'historical_accepted_individual_review_passes': historical_passes,
            'historical_scope': case['historical_scope'],
            'historical_canonical_sha256': {ref: case['canonical_sha256']},
            'full_book_verified': False, 'chapter_publication_approval': False,
            'human_specialist_certification': False, 'graphic_publication_approved': False}


def descriptor(reference):
    data = read_index()
    case = data['cases'][reference]
    package = t.APPLICATIONS/case['package']
    return {'kind': 'enoch32-explicit-historical-successor-v1',
            'package': case['package'], 'historical_scope': case['historical_scope'],
            'receipt_sha256': t.sha((package/case['receipt']).read_bytes()),
            'canonical_sha256': case['canonical_sha256'],
            'change_scope': 'new_paired_complete_individual_source_english_explanations'}


def validate_declared_successor(package, manifest):
    entries = manifest['supersedes_legacy32']
    if not isinstance(entries, dict) or set(entries) != set(REFS) or \
            not set(REFS) <= set(manifest['references']):
        raise ValueError('Legacy32 successor must bind both historical cases')
    if any(c['chapter'] == 32 for c in manifest.get('chapter_inventories', [])) or \
            '1 Enoch 32:3' in manifest['references'] or '1 Enoch 32:6' in manifest['references']:
        raise ValueError('Partial32 successor cannot clear held3 or expose isolated6')
    if '032/006.yaml' in manifest['canonical_baseline_sha256']:
        raise ValueError('Legacy32 partial successor baseline no longer has absent6')
    for ref, entry in entries.items():
        if entry != descriptor(ref) or package.name == entry['package']:
            raise ValueError('Legacy32 successor scope differs')
        verify_historical(t.APPLICATIONS/entry['package'])
        rel = '%03d/%03d.yaml' % t.parse_ref(ref)
        if manifest['canonical_baseline_sha256'].get(rel) != entry['canonical_sha256']:
            raise ValueError('Legacy32 successor preimage differs from old receipt')
        t.verify_git_preimage(manifest, rel, entry['canonical_sha256'])


def verify_current(package, *, seen=()):
    if package.name in seen:
        raise ValueError('Legacy32 supersession cycle')
    historical = verify_historical(package)
    ref = historical['references'][0]
    target = t.TRANSLATION/('%03d/%03d.yaml' % t.parse_ref(ref))
    expected = descriptor(ref)
    successors = []
    if not target.exists() or t.sha(target.read_bytes()) != expected['canonical_sha256']:
        matches = []
        for candidate in sorted(t.APPLICATIONS.glob('enoch_full_repair_batch*')):
            if not (candidate/'application.json').is_file():
                continue
            manifest = json.loads((candidate/'manifest.json').read_text())
            if manifest.get('supersedes_legacy32', {}).get(ref) == expected:
                matches.append(candidate)
        if len(matches) != 1:
            raise ValueError('No unique installed paired legacy32 successor: '+ref)
        from tools.enoch.current_evidence import verify_current as verify_new
        result = verify_new(matches[0], seen=(*seen, package.name))
        if ref not in result['references']:
            raise ValueError('Legacy32 successor omits reference')
        successors.append({'reference': ref, 'superseded_by': matches[0].name})
    return {**historical, 'current_canonical_sha256': {ref: t.sha(target.read_bytes())},
            'canonical_targets_checked': True, 'reviewed_supersessions': successors}
