"""Bind original21:10 and its held chapter without inventing broader approval.

Raw inputs/decisions/receipt and original applied Git bytes stay immutable.
Fresh paired individual evidence is mandatory for a substantive successor.
"""
import json
import subprocess
import yaml
from tools.enoch import bounded_application as t

NAME = 'enoch_21_10_20261017'
REVIEW = 'enoch_21_review_hold_20261017'
REF = '1 Enoch 21:10'
INDEX = 'sources/enoch/coverage/legacy-individuals/enoch21-10-v1.json'
INDEX_SHA = '239d32b2afd23dd46991aa57b96c179327eddeef0d36e3cabe4b0d86cd8b92fa'
PATH = 'translation/extra_canonical/1_enoch/021/010.yaml'


def registered(package):
    return package.name == NAME


def read_index():
    raw = t.artifact(t.ROOT, INDEX).read_bytes()
    if t.sha(raw) != INDEX_SHA:
        raise ValueError('Legacy21 original artifact index differs')
    d = json.loads(raw)
    if d.get('kind') != 'enoch21-historical-individual-v1' or \
            d.get('reference') != REF or d.get('package') != NAME or \
            d.get('review_package') != REVIEW or d.get('full_chapter_approval') is not False:
        raise ValueError('Legacy21 historical scope differs')
    for path, digest in d['files'].items():
        if t.sha(t.artifact(t.ROOT, path).read_bytes()) != digest:
            raise ValueError('Legacy21 original artifact differs: '+path)
    return d


def historical_record():
    d = read_index()
    raw = subprocess.check_output(['git', '--no-replace-objects', 'show',
                                   d['applied_commit']+':'+PATH], cwd=t.ROOT)
    if t.sha(raw) != d['canonical_sha256']:
        raise ValueError('Legacy21 actual applied Git record differs')
    return yaml.load(raw, Loader=t.LOADER)


def verify_historical(package):
    if not registered(package) or package.resolve() != (t.APPLICATIONS/NAME).resolve():
        raise ValueError('Unregistered legacy21 package')
    d = read_index()
    app = json.loads((package/'application.json').read_text())
    record = historical_record()
    if app.get('status') != 'individual_unit_applied_chapter_held' or \
            app.get('reference') != REF or app.get('canonical_file') != PATH or \
            app.get('canonical_sha256') != d['canonical_sha256'] or \
            app.get('source_text_sha256') != t.sha(record['source']['text'].encode()) or \
            app.get('review_passes') != 2 or app.get('chapter_editorially_accepted') is not False or \
            app.get('graphic_publication_approved') is not False or \
            app.get('held_reference') != '1 Enoch 21:6' or \
            app.get('clipped_existing_reference') != '1 Enoch 21:9':
        raise ValueError('Legacy21 individual receipt/held scope differs')
    for n in (1, 2):
        root = t.APPLICATIONS/REVIEW/f'pass{n}'
        pv = json.loads((root/'provenance.json').read_text())
        result = json.loads((root/'review.json').read_text())
        digest = t.sha((root/'review.json').read_bytes())
        if pv.get('review_sha256') != digest or app['review_sha256'][n-1] != digest or \
                not pv.get('scan_image_sha256') or result.get('chapter_complete') is not True:
            raise ValueError('Legacy21 original review/source binding differs')
        for name, expected in pv['package_input_sha256'].items():
            if t.sha(t.artifact(root, name).read_bytes()) != expected:
                raise ValueError('Legacy21 exact original input differs')
        inputs = json.loads((root/'review-input.json').read_text())
        decisions = t.review_entries(result)
        refs = [f'1 Enoch 21:{v}' for v in range(1, 11)]
        if [r['reference'] for r in inputs] != refs or [r['reference'] for r in decisions] != refs or \
                decisions[9]['verdict'] != 'accept' or decisions[5]['verdict'] != 'hold':
            raise ValueError('Legacy21 original accepted/held decisions differ')
        row = inputs[9]
        if row['translation'] != record['translation'] or any(
                row['source'].get(k) != record['source'].get(k)
                for k in ('edition', 'language', 'text', 'pages')):
            raise ValueError('Legacy21 historical reviewed payload differs')
    return {'references': [REF], 'historical_artifacts_verified': True,
            'historical_accepted_individual_review_passes': 2,
            'historical_scope': d['historical_scope'],
            'historical_canonical_sha256': d['canonical_sha256'],
            'full_book_verified': False, 'chapter_publication_approval': False,
            'graphic_publication_approved': False, 'human_specialist_certification': False}


def descriptor():
    d = read_index()
    return {'kind': 'enoch21-explicit-individual-successor-v1', 'package': NAME,
            'receipt_sha256': t.sha((t.APPLICATIONS/NAME/'application.json').read_bytes()),
            'canonical_sha256': d['canonical_sha256'],
            'historical_scope': d['historical_scope'],
            'change_scope': 'new_paired_individual_source_english_explanations'}


def validate_declared_successor(package, manifest):
    entries = manifest['supersedes_legacy21']
    if entries != {REF: descriptor()} or REF not in manifest['references'] or package.name == NAME:
        raise ValueError('Legacy21 successor scope differs')
    verify_historical(t.APPLICATIONS/NAME)
    if manifest['canonical_baseline_sha256'].get('021/010.yaml') != descriptor()['canonical_sha256']:
        raise ValueError('Legacy21 successor preimage differs')
    t.verify_git_preimage(manifest, '021/010.yaml', descriptor()['canonical_sha256'])


def verify_current(package, *, seen=()):
    if NAME in seen:
        raise ValueError('Legacy21 successor cycle')
    result = verify_historical(package)
    target = t.ROOT/PATH
    successors = []
    if not target.exists() or t.sha(target.read_bytes()) != result['historical_canonical_sha256']:
        matches = []
        for candidate in sorted(t.APPLICATIONS.glob('enoch_full_repair_batch*')):
            if not (candidate/'application.json').is_file():
                continue
            manifest = json.loads((candidate/'manifest.json').read_text())
            if manifest.get('supersedes_legacy21') == {REF: descriptor()}:
                matches.append(candidate)
        if len(matches) != 1:
            raise ValueError('No unique installed paired legacy21 successor')
        from tools.enoch.current_evidence import verify_current as verify_new
        current = verify_new(matches[0], seen=(*seen, NAME))
        if REF not in current['references']:
            raise ValueError('Legacy21 successor omits reference')
        successors.append({'reference': REF, 'superseded_by': matches[0].name})
    return {**result, 'current_canonical_sha256': t.sha(target.read_bytes()),
            'canonical_targets_checked': True, 'reviewed_supersessions': successors}
