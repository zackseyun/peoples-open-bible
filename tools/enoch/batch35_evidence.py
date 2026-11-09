"""Fixed six-unit B35 successor, never a partial-chapter release waiver.

B34 retains its immutable historical map. Only this exact applied successor
may explain the six later changes, and the complete current966 map is checked.
"""
import json
import subprocess
import yaml
from tools.enoch import bounded_application as t

NAME = 'enoch_full_repair_batch35_20261031'
MANIFEST_SHA = '0949de859c43f638bc3211c601bdb1e0ea414d26b77ea86296218d9ec549a961'
BASE = 'a3681961d91c1eb1a609e12cec312a644148f9bb'
PRIOR = 'enoch_full_repair_batch34_20261031'
PRIOR_SHA = '53d842f144cef8646a66ad64ac7b94d1b0f053773d66c79c12e841cfd99b83f9'
REFS = [f'1 Enoch 95:{v}' for v in range(1, 6)] + ['1 Enoch 96:1']
CHANGED_PATHS = {f'{c:03d}/{v:03d}.yaml' for c, v in map(t.parse_ref, REFS)}
INPUT_SHAS = {95: '5032d2c0b9e89381c8a7fea54c93fee7d9dae52f8fecbc294fb499219565373e',
              96: '9371a3fd66599d1b462835448405222299a93d3421d968aeb2155a6d1112c11b'}
COUNT_INDEX = 'sources/enoch/coverage/count91-103-20261022/paired-count-index-v2.json'
COUNT_INDEX_SHA = 'c72f8a27a25e4f5245422740934102fe5d55dc253454ab2098c0f0b6217b932d'
CHAPTER_UNITS = {95: list(range(1, 8)), 96: list(range(1, 9))}
CHAPTER_PAGES = {95: [237, 238], 96: [238, 239]}
ACCEPTED_UNITS = {95: list(range(1, 6)), 96: [1]}
PAIRS = {
    95: {
        'author': ('/root/author72_35_semantic_resume', 'corrective_author',
                   '1586007d52b626f25edb42f8d3df8f946305a18e30b8ea344dae96dcc92fa8da',
                   '789b231436365688c55adbad7a6dc0408613923c0e978f9d5f80ba7f523f8b53'),
        'independent': ('/root/grammar_acquisition_receipt_resume', 'independent_reviewer',
                        'f66db9e47d8847e6dabc884f44cc69c1e625a9f491d5bc0aadffd98b58a4da25',
                        '79b88b4292b973f64be2cac8ba0415da841466bf5e87cba6e624089b5d81ee50')},
    96: {
        'author': ('/root/author72_34_resume', 'corrective_author',
                   'acc5bb06038370b4f9a03403027c78b5a8844b9c5c1a67cc0cb47e408a2a4dc1',
                   '4dfe792f7e137240000595838dded3efbb28b6b1db38e69843bebcf717fa9c6e'),
        'independent': ('/root/author72_35_semantic_resume', 'independent_reviewer',
                        'eda40b9bb3e9d0741ba67935794458cbfb07745fee605fb1e7c591008c36ed96',
                        '4dbff48a1f29e51ca8f460d54246a626a5471df0ae74a2f0ff78e24304cbf1ad')}}


def prior_postmap():
    # Do not call B34.verify_current(): that function reaches this successor.
    from tools.enoch import batch34_evidence as prior
    if prior.NAME != PRIOR or prior.MANIFEST_SHA != PRIOR_SHA:
        raise ValueError('Fixed B35 predecessor identity differs')
    proof = prior.historical_postmap()
    return proof['manifest'], proof['current_postmap']


def _binding(chapter, who):
    identity = PAIRS[chapter][who][0]
    prefix = f'final/ch{chapter}/{who}'
    return {'input': prefix + '-input.json', 'review': prefix + '-review.json',
            'provenance': prefix + '-provenance.json', 'reviewer_id': identity}


def _paired_scope(package, manifest, chapter):
    expected_refs = [f'1 Enoch {chapter}:{v}' for v in CHAPTER_UNITS[chapter]]
    expected_decisions = [(ref, 'accept' if v in ACCEPTED_UNITS[chapter] else 'hold')
                          for ref, v in zip(expected_refs, CHAPTER_UNITS[chapter])]
    wanted_bindings = [_binding(chapter, who) for who in ('author', 'independent')]
    for v in ACCEPTED_UNITS[chapter]:
        if manifest['review_bindings'][f'1 Enoch {chapter}:{v}'] != wanted_bindings:
            raise ValueError('B35 exact per-chapter actor bindings differ')
    for who, binding in zip(('author', 'independent'), wanted_bindings):
        identity, role, review_sha, pv_sha = PAIRS[chapter][who]
        if (manifest['files'].get(binding['input']) != INPUT_SHAS[chapter] or
                manifest['files'].get(binding['review']) != review_sha or
                manifest['files'].get(binding['provenance']) != pv_sha):
            raise ValueError('B35 fixed full-input/review/provenance pair hashes differ')
        inputs = json.loads((package/binding['input']).read_text())
        review = json.loads((package/binding['review']).read_text())
        pv = json.loads((package/binding['provenance']).read_text())
        decisions = t.review_entries(review)
        if ([row.get('reference') for row in inputs] != expected_refs or
                [(row['reference'], row['verdict']) for row in decisions] != expected_decisions or
                (review.get('reviewer_id'), review.get('role')) != (identity, role) or
                (pv.get('reviewer_id'), pv.get('role')) != (identity, role) or
                pv.get('input_sha256') != INPUT_SHAS[chapter] or
                pv.get('review_sha256') != review_sha or
                pv.get('source_pdf_sha256') != t.PRIMARY_SHA or not pv.get('scan_image_sha256')):
            raise ValueError('B35 full7/8 scope, explicit HOLDs, roles or actual views differ')
        for row, (_, verdict) in zip(inputs, expected_decisions):
            if verdict == 'hold' and (row['translation']['text'] != '' or
                                      row['translation']['footnotes'] != []):
                raise ValueError('B35 held neighboring input gained English or notes')


def _source_counts(package, manifest):
    from tools.enoch import structural_count_profiles, count95_window_evidence as window
    index_raw = t.artifact(t.ROOT, COUNT_INDEX).read_bytes()
    if (t.sha(index_raw) != COUNT_INDEX_SHA or
            t.sha((package/'original-count91-103-index.json').read_bytes()) != COUNT_INDEX_SHA):
        raise ValueError('B35 original existing structural index differs')
    counts = structural_count_profiles.load(t.artifact(t.ROOT, COUNT_INDEX), root=t.ROOT)
    index = json.loads(index_raw)
    original = json.loads(t.artifact(t.ROOT, index['input']).read_text())
    wanted_certificates = [
        {'chapter': c, 'units': CHAPTER_UNITS[c], 'artifact': 'source-only-count-inventory.json',
         'independent_count_confirmation': True} for c in (95, 96)]
    inventory = json.loads((package/'source-only-count-inventory.json').read_text())
    wanted_rows = [
        {'chapter': c, 'units': CHAPTER_UNITS[c], 'pdf_pages': CHAPTER_PAGES[c],
         'count_evidence_index': COUNT_INDEX, 'count_evidence_index_sha256': COUNT_INDEX_SHA,
         'basis': 'Existing immutable independent structural profile; heldlanguageunits do not gain approval.'}
        for c in (95, 96)]
    if (manifest.get('chapter_inventories') != [] or
            manifest.get('source_only_count_inventories') != wanted_certificates or
            inventory.get('kind') != 'enoch-source-ingress-counts-v1' or
            inventory.get('primary_pdf_sha256') != t.PRIMARY_SHA or
            inventory.get('chapters') != wanted_rows or
            type(inventory.get('new_count_votes')) is not int or inventory['new_count_votes'] != 0 or
            inventory.get('wording_approval') is not False or
            inventory.get('reader_release_policy_changed') is not False):
        raise ValueError('B35 existing source-only counts or no-release limits differ')
    for c in (95, 96):
        rows = [row for row in original['chapters'] if row['chapter'] == c]
        if (counts[c]['units'] != CHAPTER_UNITS[c] or len(rows) != 1 or
                rows[0]['chapter_pdf_pages'] != CHAPTER_PAGES[c]):
            raise ValueError('B35 original paired chapter95/96 scope differs')
    # The window was a separately applied structural transaction, not a
    # language vote and not an ignored field of this YAML-only manifest.
    window.verify_applied()


def historical_postmap():
    package = t.APPLICATIONS/NAME
    if t.sha((package/'manifest.json').read_bytes()) != MANIFEST_SHA:
        raise ValueError('Fixed B35 manifest differs')
    manifest = t.load_manifest(package)
    _, before = prior_postmap()
    if (manifest['references'] != REFS or manifest['retirements'] != [] or
            manifest.get('supersedes') != {} or
            manifest['source_baseline_git_commit'] != BASE or
            manifest['canonical_baseline_sha256'] != before or len(before) != 966):
        raise ValueError('B35 does not follow exact B34 with sole six-existing-unit scope')
    expected = dict(before)
    for ref in REFS:
        c, v = t.parse_ref(ref)
        relative = f'{c:03d}/{v:03d}.yaml'
        if relative not in before:
            raise ValueError('B35 cannot add a missing canonical record')
        blob = manifest['baseline_git_blobs'].get(relative, {})
        git_path = 'translation/extra_canonical/1_enoch/' + relative
        if blob.get('commit') != BASE or blob.get('path') != git_path:
            raise ValueError('B35 actual Git preimage identity differs')
        preimage = subprocess.check_output(['git', 'show', BASE + ':' + git_path], cwd=t.ROOT)
        actual_blob = subprocess.check_output(
            ['git', 'rev-parse', BASE + ':' + git_path], cwd=t.ROOT, text=True).strip()
        if t.sha(preimage) != before[relative] or blob.get('blob') != actual_blob:
            raise ValueError('B35 actual Git preimage bytes/blob differ')
        expected[relative] = manifest['files'][f'{c:03d}-{v:03d}.candidate.yaml']
        candidate = yaml.load((package/f'{c:03d}-{v:03d}.candidate.yaml').read_bytes(), Loader=t.LOADER)
        correction = candidate['source_correction']
        if any(correction.get(key) is not False for key in
               ('selected_edition_chapter_reviewed', 'chapter_publication_approval',
                'full_book_verified', 'human_specialist_certification',
                'manuscript_witness_certification', 'graphic_publication_approved')):
            raise ValueError('B35 individual treatment gained chapter/publication approval')
    if (set(expected) != set(before) or len(expected) != 966 or
            {k for k in expected if expected[k] != before[k]} != CHANGED_PATHS):
        raise ValueError('B35 changed-record scope differs from the exact six files')
    for c in (95, 96):
        _paired_scope(package, manifest, c)
    _source_counts(package, manifest)
    receipt = json.loads((package/'application.json').read_text())
    if (receipt.get('status') != 'applied_verified' or
            receipt.get('manifest_sha256') != MANIFEST_SHA or
            receipt.get('canonical_after_sha256') != expected or
            receipt.get('references') != REFS or receipt.get('retired_references') != [] or
            receipt.get('candidate_files') != 6 or receipt.get('snapshot_file_count') != 966 or
            receipt.get('unrelated_canonical_files_unchanged_at_application') is not True or
            receipt.get('canonical_targets_checked') is not True or
            receipt.get('canonical_changed') is not True or
            receipt.get('full_book_verified') is not False or
            receipt.get('graphic_publication_approved') is not False or
            receipt.get('deployed_by_transaction') is not False):
        raise ValueError('B35 exact applied receipt/full966 postmap differs')
    from tools.enoch.selected_edition_sources import registry_data
    registry = registry_data()
    wanted = {f'{c}:{v}': NAME for c in (95, 96) for v in ACCEPTED_UNITS[c]}
    if (registry is None or any(str(c) in registry['chapters'] for c in (95, 96)) or
            {key: value for key, value in registry.get('units', {}).items() if value == NAME} != wanted or
            any(registry.get('units', {}).get(key) != value for key, value in wanted.items())):
        raise ValueError('B35 individual source registry exceeds six accepted units')
    proof = t.verify(package, applied=True, check_corpus=False)
    return {**proof, 'manifest': manifest, 'prior_historical_postmap': before,
            'current_postmap': expected, 'actual_current_postmap': expected,
            'new_language_review_units': 6, 'new_structural_count_votes': 0}


def verify_current():
    """Only the fixed applied B36 may extend the immutable historical B35 map."""
    proof = historical_postmap()
    from tools.enoch import batch36_evidence as successor
    if (t.APPLICATIONS/successor.NAME/'application.json').is_file():
        current = successor.verify_current()['actual_current_postmap']
        name = successor.NAME
    else:
        t.verify(t.APPLICATIONS/NAME, applied=True, check_corpus=True)
        from tools.enoch.selected_edition_sources import registry_data
        registry = registry_data()
        wanted = {f'{c}:{v}': NAME for c in (95,96) for v in ACCEPTED_UNITS[c]}
        if {key:value for key,value in registry.get('units',{}).items()
            if key.startswith(('95:', '96:')) or value == NAME} != wanted:
            raise ValueError('B35 has an unapproved registry successor')
        current = proof['current_postmap']
        name = None
    return {**proof, 'actual_current_postmap': current,
            'verified_current_successor': name}
