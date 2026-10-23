"""Exact inherited26:5/6 payloads plus a bounded metadata-only successor.

This does not turn metadata reviewers into new source/English reviewers. Raw
historical inputs, adverse note request, actual Git bytes and model identities
remain distinct from the new control/provenance delta. No generic approve API.
"""
import copy
import json
import os
import re
import subprocess
import jsonschema
import yaml
from tools.enoch import bounded_application as t
from tools.enoch.legacy_editorial_evidence import _blobs

NAME = 'enoch_26_metadata_v3_20261023'
INDEX = 'sources/enoch/coverage/metadata26-v3-20261023/index.json'
INDEX_SHA = '7032c001b8945c6d49ff0c0102bb1ae6447dcb04614329681fe101e57ec2adaa'
REFS = ['1 Enoch 26:5', '1 Enoch 26:6']
LEGACY = ('enoch_26_5_20261017', 'enoch_26_6_20261017')


def registered(package):
    return package.name == NAME or package.name in LEGACY


def read_index():
    raw = t.artifact(t.ROOT, INDEX).read_bytes()
    if t.sha(raw) != INDEX_SHA:
        raise ValueError('Metadata26 frozen evidence index differs')
    data = json.loads(raw)
    if data.get('kind') != 'enoch26-exact-historical-payload-metadata-successor-v1' or \
            data.get('references') != REFS or list(data.get('cases', {})) != REFS or \
            data.get('metadata_package') != NAME or data.get('primary_pdf_sha256') != t.PRIMARY_SHA or \
            data.get('fresh_full_source_or_English_reviews') != 0 or \
            any(data.get(k) is not False for k in ('whole_chapter_count_or_wording_approval',
                'graphic_publication_approved', 'full_book_verified')):
        raise ValueError('Metadata26 historical/control scope differs')
    for path, digest in data['files'].items():
        if t.sha(t.artifact(t.ROOT, path).read_bytes()) != digest:
            raise ValueError('Metadata26 immutable artifact differs: ' + path)
    return data


def _read(data, path):
    if path not in data['files']:
        raise ValueError('Metadata26 unpinned artifact')
    return json.loads(t.artifact(t.ROOT, path).read_text())


def _originals(data):
    records = {}; proofs = {}
    for ref, case in data['cases'].items():
        c, v = t.parse_ref(ref); path = f'translation/extra_canonical/1_enoch/{c:03d}/{v:03d}.yaml'
        package = t.APPLICATIONS / case['package']; commit = case['applied_commit']
        blobs = _blobs([commit + ':' + path, commit + '^:' + path])
        raw = blobs[commit + ':' + path]
        if raw is None or t.sha(raw) != case['original_canonical_sha256'] or \
                case['actual_parent_absence_required'] is not True or blobs[commit + '^:' + path] is not None:
            raise ValueError('Metadata26 actual historical Git application/parent absence differs')
        old = yaml.load(raw, Loader=t.LOADER); records[ref] = old
        receipt = _read(data, str((package / 'application.json').relative_to(t.ROOT)))
        if receipt.get('reference') != ref or receipt.get('canonical_file') != path or \
                receipt.get('status') != 'individual_unit_applied_chapter_held' or \
                receipt.get('canonical_sha256') != t.sha(raw) or receipt.get('review_passes') != 2 or \
                receipt.get('source_text_sha256') != t.sha(old['source']['text'].encode()) or \
                any(receipt.get(k) is not False for k in ('chapter_complete', 'graphic_publication_approved',
                    'app_published', 'human_specialist_certification', 'manuscript_witness_certification')):
            raise ValueError('Metadata26 original individual receipt differs')
        full_matches = []
        for n in (1, 2):
            root = str((package / f'review-pass{n}').relative_to(t.ROOT))
            pv = _read(data, root + '/provenance.json'); review = _read(data, root + '/review.json')
            manifest = _read(data, root + '/review-manifest.json'); inputs = _read(data, root + '/review-input.json')
            if pv['review_sha256'] != data['files'][root + '/review.json'] or \
                    receipt['review_sha256'][n - 1] != pv['review_sha256'] or \
                    manifest.get('refs') != [ref] or manifest.get('whole_chapter_complete') is not False or \
                    review.get('chapter_complete') is not False or \
                    [(r['reference'], r['verdict']) for r in review['reviews']] != [(ref, 'accept')] or \
                    pv.get('scan_image_sha256') != receipt['scan_sha256'] or \
                    manifest.get('scan_sha256') != receipt['scan_sha256']:
                raise ValueError('Metadata26 actual old review/image binding differs')
            for name, digest in pv['package_input_sha256'].items():
                if data['files'].get(root + '/' + name) != digest:
                    raise ValueError('Metadata26 exact old submitted input differs')
            log = t.artifact(t.ROOT, root + '/review.log').read_text()
            model = 'gpt-6.1-sol' if v == 5 else 'gpt-6-astra'
            if pv.get('model') != model or not re.search(r'^model: ' + re.escape(model) + '$', log, re.M):
                raise ValueError('Metadata26 original model attribution differs')
            if len(inputs) != 1 or inputs[0]['reference'] != ref:
                raise ValueError('Metadata26 original input scope differs')
            submitted = inputs[0]; source = copy.deepcopy(submitted['source'])
            delta = case['reviewed_to_original_source_metadata'][str(n)]
            if set(delta) != {'note', 'validation'}:
                raise ValueError('Metadata26 original workflow delta scope differs')
            for key, values in delta.items():
                if source.get(key) != values['reviewed'] or old['source'].get(key) != values['original']:
                    raise ValueError('Metadata26 exact original source metadata delta differs')
                source[key] = values['original']
            if source != old['source']:
                raise ValueError('Metadata26 source differs beyond pinned original workflow metadata')
            if submitted['translation']['text'] != old['translation']['text']:
                raise ValueError('Metadata26 historical main English differs')
            full_matches.append(submitted['translation'] == old['translation'])
            if v == 6 and n == 1 and ('translation alternative' not in review['reviews'][0]['footnote_changes'] or full_matches[-1]):
                raise ValueError('Metadata26 first6 note clarification was lost')
        accepting = [n for n, matches in enumerate(full_matches, 1) if matches]
        if accepting != ([1, 2] if v == 5 else [2]) or \
                case['historical_full_final_payload_accepting_passes'] != accepting or \
                case['historical_execution_count'] != 2 or case['new_full_source_or_English_review_count'] != 0:
            raise ValueError('Metadata26 execution/final full-payload distinction differs')
        proofs[ref] = {'original_canonical_sha256': t.sha(raw), 'historical_execution_count': 2,
                       'historical_full_final_payload_accepting_passes': accepting,
                       'new_full_source_or_English_review_count': 0, 'actual_parent_absence_verified': True}
    return records, proofs


def _candidates(data, originals):
    inputs = _read(data, data['metadata_input'])
    spec = _read(data, data['metadata_delta_specification'])
    if [r['reference'] for r in inputs] != REFS or spec['input_sha256'] != data['files'][data['metadata_input']]:
        raise ValueError('Metadata26 exact new delta input differs')
    identities = set()
    for binding in data['metadata_reviews']:
        pv = _read(data, binding['provenance']); review = _read(data, binding['review'])
        if data['files'][binding['input']] != data['files'][data['metadata_input']] or \
                pv.get('input_sha256') != data['files'][data['metadata_input']] or \
                pv.get('review_sha256') != data['files'][binding['review']] or \
                pv.get('source_pdf_sha256') != t.PRIMARY_SHA or \
                (pv.get('reviewer_id'), pv.get('role')) != (binding['reviewer_id'], binding['role']) or \
                (review.get('reviewer_id'), review.get('role')) != (binding['reviewer_id'], binding['role']) or \
                not pv.get('scan_image_sha256') or \
                [(r['reference'], r['verdict']) for r in review['reviews']] != [(ref, 'accept') for ref in REFS] or \
                review.get('input_sha256') != pv['input_sha256']:
            raise ValueError('Metadata26 distinct bounded metadata review binding differs')
        if not all(re.fullmatch('[0-9a-f]{64}', h) for h in pv['scan_image_sha256'].values()):
            raise ValueError('Metadata26 actual metadata image hash map differs')
        identities.add(binding['reviewer_id'])
    if len(identities) != 2 or {r['role'] for r in data['metadata_reviews']} != {'author', 'independent_reviewer'}:
        raise ValueError('Metadata26 requires two distinct metadata actors')
    candidates = {}
    validator = jsonschema.Draft202012Validator(json.loads((t.ROOT / 'schema/verse.schema.json').read_text()))
    for row, detail in zip(inputs, spec['units']):
        ref = row['reference']; old = originals[ref]; candidate = yaml.load(
            t.artifact(t.ROOT, data['cases'][ref]['candidate']).read_bytes(), Loader=t.LOADER)
        if row['canonical_preimage_sha256'] != data['cases'][ref]['original_canonical_sha256'] or \
                row['translation'] != old['translation'] or detail['reference'] != ref:
            raise ValueError('Metadata26 unchanged complete translation/preimage differs')
        # Only these source metadata fields may differ; absence is not normalized.
        source = copy.deepcopy(row['source']); old_source = copy.deepcopy(old['source'])
        for key in ('note', 'transcription_uncertainties'):
            source.pop(key, None); old_source.pop(key, None)
        if source != old_source or (ref.endswith(':6') and
                row['source'].get('transcription_uncertainties') != old['source'].get('transcription_uncertainties')):
            raise ValueError('Metadata26 attempted source semantic/control change beyond exact delta')
        expected = copy.deepcopy(old); expected['source'] = row['source']; changed = []
        for key in set(old['source']) | set(row['source']):
            if old['source'].get(key) != row['source'].get(key) or (key in old['source']) != (key in row['source']):
                changed.append('/source/' + key)
        for key, delta in row['canonical_metadata_patch']['cross_check'].items():
            if (key in old['cross_check']) != delta['old_present'] or old['cross_check'].get(key) != delta['old']:
                raise ValueError('Metadata26 original cross-check preimage differs')
            expected['cross_check'][key] = delta['new']; changed.append('/cross_check/' + key)
        # Fill required provenance truthfully; never invent the original model
        # or recast a schema delta as a new provider/source/English invocation.
        ai = row.get('canonical_added_ai_draft')
        instructions = t.artifact(t.ROOT, data['integration_instructions']).read_bytes()
        output = {'source': row['source'], 'translation': row['translation'],
                  'canonical_metadata_patch': row['canonical_metadata_patch']}
        if 'ai_draft' in old or not isinstance(ai, dict) or \
                ai.get('model_id') != 'not_reported' or ai.get('model_version') != 'not_reported' or \
                ai.get('prompt_id') != 'enoch_bounded_metadata_only_integration_20261023' or \
                ai.get('prompt_sha256') != t.sha(instructions) or \
                ai.get('output_hash') != t.sha(json.dumps(output, sort_keys=True, ensure_ascii=False,
                                                          separators=(',', ':')).encode()):
            raise ValueError('Metadata26 required integration provenance invents/changes source facts')
        expected['ai_draft'] = ai; changed.append('/ai_draft')
        if sorted(changed) != sorted(d['path'] for d in detail['exact_changed_fields']):
            raise ValueError('Metadata26 reviewed metadata delta paths differ')
        # Engineering-only lifecycle downgrade is not a new language vote and
        # is deliberately NOT attributed to the source reviewers' exact input.
        policy = _read(data, data['engineering_workflow_policy'])
        exact = {'/status': {'old': 'revised', 'new': 'draft'},
                 '/cross_check/status': {'old': 'high_agreement_individual_unit', 'new': 'needs_review'}}
        if policy.get('kind') != 'enoch26-engineering-only-workflow-schema-downgrade-v1' or \
                policy.get('references') != REFS or policy.get('changes') != exact or \
                policy.get('new_source_or_English_reviews') != 0 or \
                policy.get('source_wording_or_notes_changed') is not False or \
                policy.get('publication_approval') is not False or \
                expected.get('status') != 'revised' or expected['cross_check'].get('status') != 'high_agreement_individual_unit':
            raise ValueError('Metadata26 engineering lifecycle normalization differs')
        expected['status'] = 'draft'; expected['cross_check']['status'] = 'needs_review'
        if candidate != expected:
            raise ValueError('Metadata26 whole candidate differs beyond exact reviewed metadata delta')
        validator.validate(candidate)
        if t.record_issues(candidate, *t.parse_ref(ref)):
            raise ValueError('Metadata26 candidate fails mechanical source/notes controls')
        candidates[ref] = candidate
    return candidates


def verify(*, check_targets=True, applied=False):
    data = read_index(); originals, history = _originals(data); candidates = _candidates(data, originals)
    package = t.APPLICATIONS / NAME; manifest = json.loads((package / 'manifest.json').read_text())
    if manifest.get('kind') != 'enoch26-bounded-metadata-application-v1' or manifest.get('references') != REFS or \
            manifest.get('evidence_index') != INDEX or manifest.get('evidence_index_sha256') != INDEX_SHA or \
            manifest.get('engineering_workflow_policy') != data['engineering_workflow_policy'] or \
            manifest.get('primary_pdf_sha256') != t.PRIMARY_SHA or manifest.get('new_full_source_English_approval_count') != 0 or \
            manifest.get('full_book_verified') is not False or manifest.get('graphic_publication_approved') is not False:
        raise ValueError('Metadata26 application scope differs')
    after = dict(manifest['canonical_baseline_sha256'])
    for ref, case in data['cases'].items():
        rel = '%03d/%03d.yaml' % t.parse_ref(ref); digest = data['files'][case['candidate']]
        if manifest['candidate_sha256'].get(ref) != digest or after.get(rel) != case['original_canonical_sha256']:
            raise ValueError('Metadata26 candidate/preimage declaration differs')
        t.verify_git_preimage(manifest, rel, case['original_canonical_sha256']); after[rel] = digest
        if check_targets and t.sha((t.TRANSLATION / rel).read_bytes()) != (digest if applied else case['original_canonical_sha256']):
            raise ValueError('Metadata26 current canonical target differs')
    if applied or (package / 'application.json').exists():
        receipt = json.loads((package / 'application.json').read_text())
        if receipt.get('status') != 'applied_verified_metadata_only' or receipt.get('references') != REFS or \
                receipt.get('manifest_sha256') != t.sha((package / 'manifest.json').read_bytes()) or \
                receipt.get('canonical_after_sha256') != after or receipt.get('new_full_source_English_reviews') != 0:
            raise ValueError('Metadata26 historical full application map/receipt differs')
    return {'references': REFS, 'historical_payloads': history, 'new_full_source_English_reviews': 0,
            'whole_chapter_approved': False, 'full_book_verified': False,
            'graphic_publication_approved': False, 'canonical_targets_checked': check_targets,
            'metadata_candidate_source': {ref: row['source'] for ref, row in candidates.items()}}


def verify_current(package, *, seen=()):
    if package.name in seen or package.resolve() != (t.APPLICATIONS / package.name).resolve() or not registered(package):
        raise ValueError('Metadata26 unregistered package or successor cycle')
    data = read_index(); result = verify(check_targets=False, applied=True)
    manifest_hash = t.sha((t.APPLICATIONS / NAME / 'manifest.json').read_bytes()); superseded = []
    refs = REFS if package.name == NAME else [REFS[LEGACY.index(package.name)]]
    from tools.enoch.current_evidence import verify_current as verify_new
    for ref in refs:
        rel = '%03d/%03d.yaml' % t.parse_ref(ref); digest = data['files'][data['cases'][ref]['candidate']]
        if t.sha((t.TRANSLATION / rel).read_bytes()) == digest:
            continue
        expected = {'package': NAME, 'manifest_sha256': manifest_hash, 'candidate_sha256': digest}
        matches = [p for p in sorted(t.APPLICATIONS.glob('enoch_full_repair_batch*'))
                   if (p / 'application.json').is_file() and
                   json.loads((p / 'manifest.json').read_text()).get('supersedes', {}).get(ref) == expected]
        if len(matches) != 1 or ref not in verify_new(matches[0], seen=(*seen, package.name))['references']:
            raise ValueError('Metadata26 no unique current reviewed successor: ' + ref)
        superseded.append({'reference': ref, 'superseded_by': matches[0].name})
    return {**result, 'references': refs, 'canonical_targets_checked': True,
            'current_targets_or_reviewed_successors_verified': True, 'reviewed_supersessions': superseded}


def current_units():
    data = read_index(); verify(check_targets=False, applied=True); output = {}
    for ref, case in data['cases'].items():
        cv = t.parse_ref(ref); target = t.TRANSLATION / ('%03d/%03d.yaml' % cv)
        if t.sha(target.read_bytes()) == data['files'][case['candidate']]:
            output[cv] = {'application': str((t.APPLICATIONS / NAME).relative_to(t.ROOT)),
                          'kind': 'historical_exact_payload_plus_paired_metadata_only_delta',
                          'historical_full_payload_accepted_passes': case['historical_full_final_payload_accepting_passes'],
                          'fresh_full_source_English_reviews': 0, 'full_chapter_count_certified_by_import': False}
    return output


def source_overrides(chapter):
    if chapter != 26:
        return []
    result = verify(check_targets=False, applied=True)
    return [{'reference': ref, 'verse': t.parse_ref(ref)[1], 'source': source,
             'evidence': INDEX + '#metadata-delta-on-exact-historical-payload'}
            for ref, source in result['metadata_candidate_source'].items()]


def apply():
    package = t.APPLICATIONS / NAME
    if (package / 'application.json').exists():
        raise ValueError('Metadata26 already has an application receipt; verify, do not reapply')
    verify(); data = read_index(); manifest = json.loads((package / 'manifest.json').read_text())
    before = t.corpus_hashes()
    if before != manifest['canonical_baseline_sha256']:
        raise ValueError('Metadata26 full canonical preimage changed')
    originals = {}; after = dict(before)
    for ref, case in data['cases'].items():
        rel = '%03d/%03d.yaml' % t.parse_ref(ref); target = t.TRANSLATION / rel
        originals[target] = target.read_bytes(); after[rel] = data['files'][case['candidate']]
    try:
        for ref, case in data['cases'].items():
            target = t.TRANSLATION / ('%03d/%03d.yaml' % t.parse_ref(ref)); temporary = target.with_suffix('.metadata26-pending')
            temporary.write_bytes(t.artifact(t.ROOT, case['candidate']).read_bytes()); os.replace(temporary, target)
        if t.corpus_hashes() != after:
            raise ValueError('Metadata26 unrelated canonical delta detected')
        receipt = {'status': 'applied_verified_metadata_only', 'references': REFS,
                   'manifest_sha256': t.sha((package / 'manifest.json').read_bytes()),
                   'canonical_after_sha256': after, 'new_full_source_English_reviews': 0,
                   'unrelated_canonical_files_unchanged_at_application': True, 'deployed': False}
        (package / 'application.json').write_text(json.dumps(receipt, indent=2) + '\n')
        return verify(applied=True)
    except Exception:
        for path, raw in originals.items():
            path.write_bytes(raw)
        (package / 'application.json').unlink(missing_ok=True)
        for target in originals:
            target.with_suffix('.metadata26-pending').unlink(missing_ok=True)
        raise
