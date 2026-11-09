"""Six existing units only: exact whole-input pairs, not a chapter release."""
from contextlib import contextmanager
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import yaml

from tools.enoch import bounded_application as t, batch34_evidence as prior
from tools.enoch import batch35_evidence as b, count95_window_evidence as window
from tools.enoch import selected_edition_sources as sources, verse_parser
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader


SHA = '0949de859c43f638bc3211c601bdb1e0ea414d26b77ea86296218d9ec549a961'
BASE = 'a3681961d91c1eb1a609e12cec312a644148f9bb'
INPUTS = {95: '5032d2c0b9e89381c8a7fea54c93fee7d9dae52f8fecbc294fb499219565373e',
          96: '9371a3fd66599d1b462835448405222299a93d3421d968aeb2155a6d1112c11b'}
REFS = [f'1 Enoch 95:{v}' for v in range(1, 6)] + ['1 Enoch 96:1']
HELD = ['1 Enoch 95:6', '1 Enoch 95:7'] + [f'1 Enoch 96:{v}' for v in range(2, 9)]
PATHS = {f'{c:03d}/{v:03d}.yaml' for c, v in map(t.parse_ref, REFS)}
P = t.APPLICATIONS / 'enoch_full_repair_batch35_20261031'
SOURCE96 = 'ተስፈዉ፡ ጻድቃን፡ እስመ፡ ፍጡነ፡ ይተሀጐሉ፡ ኃጥአን፡ እምቅድሜክሙ፡ ወሥልጣን፡ ይከውን፡ ለክሙ፡ ዲቤሆሙ፡ በከመ፡ ፈቀድክሙ።'
ENGLISH96 = 'Have hope, righteous ones,[a] for sinners will soon perish before you.[b] And authority over them will be yours, as you have wished.[c]'
MOBILE_SHA = '2258f72485099fe1014152eeb29394324415940467c2edd9d9da0d48a4a113c3'


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def record(ref):
    c, v = t.parse_ref(ref)
    return yaml.load((t.TRANSLATION / f'{c:03d}/{v:03d}.yaml').read_bytes(), Loader=t.LOADER)


class Batch35Test(unittest.TestCase):
    def package_fixture(self, root):
        package = Path(root) / b.NAME
        shutil.copytree(P, package)
        return package, read_json(package / 'manifest.json')

    def rehash(self, package, manifest, name):
        manifest['files'][name] = t.sha((package / name).read_bytes())

    @contextmanager
    def route_package(self, package, manifest, *, rebound_manifest=False):
        """Only /tmp evidence changes; canonical files and prior packages stay read-only."""
        write_json(package / 'manifest.json', manifest)
        digest = t.sha((package / 'manifest.json').read_bytes())
        if rebound_manifest and (package / 'application.json').exists():
            receipt = read_json(package / 'application.json')
            receipt['manifest_sha256'] = digest
            write_json(package / 'application.json', receipt)
        original = t.APPLICATIONS
        routed = MagicMock()
        routed.resolve.return_value = original.resolve()
        routed.__truediv__.side_effect = lambda name: package if name == b.NAME else original / name
        with patch.object(t, 'APPLICATIONS', routed), \
                patch.object(b, 'MANIFEST_SHA', digest if rebound_manifest else SHA):
            yield

    def test_fixed_full966_b34_baseline_and_only_six_existing_deltas(self):
        self.assertEqual(t.sha((P / 'manifest.json').read_bytes()), SHA)
        self.assertEqual(b.MANIFEST_SHA, SHA)
        self.assertEqual(b.BASE, BASE)
        self.assertEqual(b.REFS, REFS)
        self.assertEqual(b.INPUT_SHAS, INPUTS)
        proof = b.verify_current()
        manifest = t.load_manifest(P)
        before = prior.historical_postmap()['current_postmap']
        self.assertEqual(manifest['canonical_baseline_sha256'], before)
        self.assertEqual(proof['prior_historical_postmap'], before)
        self.assertEqual(len(before), 966)
        self.assertEqual(set(proof['current_postmap']), set(before))
        from tools.enoch import batch36_evidence as next_successor
        if proof.get('verified_current_successor'):
            self.assertEqual(proof['verified_current_successor'], next_successor.NAME)
            from tools.enoch import batch37_evidence as last_successor
            changes=set(next_successor.CHANGED_PATHS)
            if (t.APPLICATIONS/last_successor.NAME/'application.json').is_file():
                last_successor.verify_current()
                changes |= last_successor.CHANGED_PATHS
                from tools.enoch import batch38_evidence
                if (t.APPLICATIONS/batch38_evidence.NAME/'application.json').is_file():
                    batch38_evidence.verify_current();changes |= batch38_evidence.CHANGED_PATHS
                    from tools.enoch import batch39_evidence
                    if (t.APPLICATIONS/batch39_evidence.NAME/'application.json').is_file():
                        batch39_evidence.verify_current();changes |= batch39_evidence.CHANGED_PATHS
                        from tools.enoch import batch40_evidence
                        if (t.APPLICATIONS/batch40_evidence.NAME/'application.json').is_file():
                            batch40_evidence.verify_current();changes |= batch40_evidence.CHANGED_PATHS
                            from tools.enoch import batch41_evidence
                            if (t.APPLICATIONS/batch41_evidence.NAME/'application.json').is_file():
                                batch41_evidence.verify_current();changes |= batch41_evidence.CHANGED_PATHS
            self.assertEqual({k for k in proof['actual_current_postmap'] if proof['current_postmap'].get(k) != proof['actual_current_postmap'][k]}, changes)
        else:
            self.assertEqual(proof['current_postmap'], proof['actual_current_postmap'])
        self.assertEqual({k for k in before if before[k] != proof['current_postmap'][k]}, PATHS)
        self.assertEqual(manifest['references'], REFS)
        self.assertEqual(manifest['retirements'], [])
        self.assertEqual(manifest['supersedes'], {})
        for path in sorted(PATHS):
            t.verify_git_preimage(manifest, path, before[path])
        receipt = read_json(P / 'application.json')
        self.assertEqual(receipt['canonical_after_sha256'], proof['current_postmap'])
        self.assertEqual(proof['actual_current_postmap'], t.corpus_hashes())
        self.assertEqual(receipt['snapshot_file_count'], 966)
        self.assertEqual(receipt['candidate_files'], 6)
        self.assertEqual(receipt['retired_references'], [])
        self.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
        self.assertFalse(receipt['deployed_by_transaction'])
        self.assertEqual(proof['new_language_review_units'], 6)
        self.assertEqual(proof['new_structural_count_votes'], 0)

    def test_exact_full7_full8_pairs_distinct_roles_and_explicit_neighbor_holds(self):
        manifest = t.load_manifest(P)
        actors = {95: {'/root/author72_35_semantic_resume', '/root/grammar_acquisition_receipt_resume'},
                  96: {'/root/author72_34_resume', '/root/author72_35_semantic_resume'}}
        for ref in REFS:
            chapter, _ = t.parse_ref(ref)
            bindings = manifest['review_bindings'][ref]
            with self.subTest(ref=ref):
                self.assertEqual(len(bindings), 2)
                self.assertEqual({v['reviewer_id'] for v in bindings}, actors[chapter])
                rows = t.reviewed_rows(P, bindings, ref, manifest['files'])
                self.assertEqual(rows[0], rows[1])
                roles = set()
                for binding in bindings:
                    self.assertTrue(binding['input'].startswith(f'final/ch{chapter}/'))
                    self.assertEqual(t.sha((P / binding['input']).read_bytes()), INPUTS[chapter])
                    inputs = read_json(P / binding['input'])
                    review = read_json(P / binding['review'])
                    pv = read_json(P / binding['provenance'])
                    self.assertEqual(len(inputs), 7 if chapter == 95 else 8)
                    self.assertEqual(pv['input_sha256'], INPUTS[chapter])
                    self.assertEqual(pv['review_sha256'], t.sha((P / binding['review']).read_bytes()))
                    self.assertEqual(pv['source_pdf_sha256'], t.PRIMARY_SHA)
                    self.assertEqual(pv['reviewer_id'], binding['reviewer_id'])
                    self.assertEqual(review['reviewer_id'], binding['reviewer_id'])
                    self.assertEqual(review['role'], pv['role'])
                    self.assertTrue(pv['scan_image_sha256'])
                    roles.add(pv['role'])
                    decisions = {r['reference']: r['verdict'] for r in t.review_entries(review)}
                    self.assertEqual(set(decisions), {r['reference'] for r in inputs})
                    for row in inputs:
                        held = row['reference'] in HELD
                        self.assertEqual(decisions[row['reference']], 'hold' if held else 'accept')
                        if held:
                            self.assertEqual(row['translation']['text'], '')
                            self.assertEqual(row['translation']['footnotes'], [])
                self.assertEqual(roles, {'corrective_author', 'independent_reviewer'})

    def test_each_whole_source_english_and_final_note_matches_exact_pair(self):
        manifest = t.load_manifest(P)
        for ref in REFS:
            c, _ = t.parse_ref(ref)
            d = record(ref)
            rows = t.reviewed_rows(P, manifest['review_bindings'][ref], ref, manifest['files'])
            with self.subTest(ref=ref):
                self.assertEqual(d['translation'], rows[0]['translation'])
                self.assertEqual(d['source']['text'], rows[0]['source']['text'])
                self.assertEqual(d['source']['confidence'], 'medium' if c == 95 else 'low')
                self.assertEqual(d['source']['pages'], [237] if c == 95 else [238])
                self.assertEqual([n['marker'] for n in d['translation']['footnotes']],
                                 ['a'] if c == 95 else ['a', 'b', 'c'])
                witness = d['enoch_witnesses']['available_witnesses']
                self.assertEqual(len(witness), 1)
                self.assertEqual(witness[0]['witness'], 'charles_1906')
                self.assertEqual(witness[0]['text'], d['source']['text'])
                self.assertEqual(witness[0]['confidence'], d['source']['confidence'])
                self.assertEqual(witness[0]['language'], 'geez')
                self.assertIn('Selected printed edition', witness[0]['note'])
        d = record('1 Enoch 96:1')
        self.assertEqual(d['source']['text'], SOURCE96)
        self.assertEqual(d['translation']['text'], ENGLISH96)
        self.assertTrue(d['source']['note'])
        self.assertTrue(d['source']['transcription_uncertainties'])
        notes = d['translation']['footnotes']
        self.assertIn('asterisk', notes[0]['text'])
        self.assertIn('No agent', notes[1]['text'])
        self.assertIn('second-person plural perfect', notes[2]['text'])

    def test_clean_individual_metadata_never_promotes_partial_chapters(self):
        for ref in REFS:
            d = record(ref)
            with self.subTest(ref=ref):
                self.assertEqual(d['status'], 'draft')
                for key in ('lexical_decisions', 'theological_decisions', 'textual_comparison', 'previous_reviews'):
                    self.assertNotIn(key, d)
                correction = d['source_correction']
                self.assertTrue(correction['individual_unit_application_approved'])
                for key in ('selected_edition_chapter_reviewed', 'chapter_publication_approval',
                            'full_book_verified', 'human_specialist_certification',
                            'manuscript_witness_certification', 'graphic_publication_approved'):
                    self.assertIs(correction[key], False)

    def test_held_neighbors_cannot_be_selected_from_retained_raw_scopes(self):
        manifest = t.load_manifest(P)
        self.assertTrue(set(HELD) <= {v['reference'] for v in manifest['not_applied']})
        for ref in HELD:
            c, _ = t.parse_ref(ref)
            bindings = manifest['review_bindings'][f'1 Enoch {c}:1']
            with self.subTest(ref=ref), self.assertRaisesRegex(ValueError, 'not accepted'):
                t.reviewed_rows(P, bindings, ref, manifest['files'])

    def test_registry_units_only_accepted_input_not_canonical_echo(self):
        registry = sources.registry_data()
        wanted = {f'{c}:{v}': b.NAME for c, v in map(t.parse_ref, REFS)}
        from tools.enoch import batch36_evidence as next_successor
        installed = (t.APPLICATIONS/next_successor.NAME/'application.json').is_file()
        if installed:
            next_successor.verify_current()
            wanted['96:3'] = next_successor.NAME
        self.assertEqual({k: v for k, v in registry['units'].items()
                          if k.startswith(('95:', '96:')) or v == b.NAME}, wanted)
        for c in (95, 96):
            self.assertNotIn(str(c), registry['chapters'])
            self.assertIsNone(sources.load_chapter(c))
        with patch.object(t, 'TRANSLATION', Path('/nonexistent-canonical-source-proof')):
            for c, wanted_units in ((95, [1,2,3,4,5]), (96, [1,3] if installed else [1])):
                rows = sources.load_unit_overrides(c)
                self.assertEqual([r['verse'] for r in rows], wanted_units)
                for row in rows:
                    self.assertIn('/final/', row['evidence'])
                    self.assertNotIn('translation/extra_canonical', row['evidence'])
        parsed, _ = verse_parser.load_verse(96, 1)
        self.assertEqual(parsed.text, SOURCE96)
        self.assertEqual(parsed.source_confidence, 'low')
        self.assertEqual(build_enoch_prompt(96, 1).source_payload['text'], SOURCE96)
        raw, _ = verse_parser.parse_ocr_chapter(96)
        self.assertNotEqual(raw[0].text, SOURCE96)

    def test_original_source_only_counts_and_separate_strict95_window(self):
        manifest = t.load_manifest(P)
        self.assertEqual(manifest['chapter_inventories'], [])
        inventory = read_json(P / 'source-only-count-inventory.json')
        self.assertIs(type(inventory['new_count_votes']), int)
        self.assertEqual(inventory['new_count_votes'], 0)
        self.assertIs(inventory['wording_approval'], False)
        self.assertIs(inventory['reader_release_policy_changed'], False)
        self.assertEqual(t.sha((P / 'original-count91-103-index.json').read_bytes()),
                         'c72f8a27a25e4f5245422740934102fe5d55dc253454ab2098c0f0b6217b932d')
        for row, chapter, end, pages in zip(inventory['chapters'], (95, 96), (7, 8),
                                           ([237, 238], [238, 239])):
            self.assertEqual(row['chapter'], chapter)
            self.assertEqual(row['units'], list(range(1, end + 1)))
            self.assertEqual(row['pdf_pages'], pages)
            self.assertEqual(row['count_evidence_index'], b.COUNT_INDEX)
            self.assertEqual(row['count_evidence_index_sha256'], b.COUNT_INDEX_SHA)
        proof = window.verify_applied()
        self.assertEqual(proof['changes'], window.CHANGES)
        self.assertEqual(proof['new_count_votes'], 0)
        self.assertEqual(proof['new_language_votes'], 0)
        self.assertEqual(proof['canonical_YAML_changes'], 0)
        self.assertIs(proof['reader_release_policy_changed'], False)
        page_map = read_json(t.ROOT / window.PATH)
        self.assertEqual(page_map['editions']['charles_1906']['chapters']['095']['pages'], [237, 238])

    def test_reader_exact_notes_no_new95_96_release_mobile_unchanged(self):
        for ref in REFS:
            _, verse = t.parse_ref(ref)
            d = record(ref)
            exported = reader._export_record_verse(verse, d)
            with self.subTest(ref=ref):
                self.assertEqual(exported['footnote_review'], reader.PROTOCOL)
                self.assertEqual(exported['footnotes'], d['translation']['footnotes'])
                self.assertEqual(exported['source_critical']['text'], d['source']['text'])
                self.assertEqual(exported['source_critical']['confidence'], d['source']['confidence'])
        expected = reader._enoch_expected_verse_map()
        # Expected source counts exist; release requires complete actual YAML
        # coverage, not merely a source-only count or individual source override.
        self.assertEqual(expected[95], list(range(1, 8)))
        self.assertEqual(expected[96], list(range(1, 9)))
        payload = reader.export_extra_canonical_book('ENO')
        chapters = {row['chapter'] for row in (payload or {}).get('chapters', [])}
        self.assertNotIn(95, chapters)
        self.assertNotIn(96, chapters)
        self.assertEqual(t.sha((t.ROOT / 'tools/export_mobile_bible.py').read_bytes()), MOBILE_SHA)

    def test_progress485_37_fullbook_false(self):
        from tools.enoch.full_repair_progress import build
        report = build()
        prior.assert_current_progress(self, report)
        self.assertNotIn(95, report['chapters_with_complete_imported_selected_edition_review'])
        self.assertNotIn(96, report['chapters_with_complete_imported_selected_edition_review'])
        self.assertEqual(report['evidence_inventory_warnings'], [])
        self.assertIs(report['completion_proven'], False)

    def test_rehashed_source_english_and_every_explanation_rejected(self):
        for ref in REFS:
            c, v = t.parse_ref(ref)
            name = f'{c:03d}-{v:03d}.candidate.yaml'
            note_count = len(record(ref)['translation']['footnotes'])
            for mode in ('source', 'English', *range(note_count)):
                with self.subTest(ref=ref, mode=mode), tempfile.TemporaryDirectory() as root:
                    package, manifest = self.package_fixture(root)
                    path = package / name
                    d = yaml.load(path.read_bytes(), Loader=t.LOADER)
                    if mode == 'source':
                        d['source']['text'] += ' ወ'
                    elif mode == 'English':
                        d['translation']['text'] += ' Unreviewed addition.'
                    else:
                        d['translation']['footnotes'][mode]['text'] = 'Unreviewed replacement.'
                    path.write_text(yaml.safe_dump(d, allow_unicode=True, sort_keys=False))
                    self.rehash(package, manifest, name)
                    write_json(package / 'manifest.json', manifest)
                    with self.assertRaises(ValueError):
                        t.verify(package, evidence_only=True)

    def test_rehashed_full_input_even_held_neighbor_and_peer_tampering_rejected(self):
        for chapter in (95, 96):
            for mode in ('held_input', 'accepted_input', 'peer_verdict', 'peer_role', 'missing_peer'):
                with self.subTest(chapter=chapter, mode=mode), tempfile.TemporaryDirectory() as root:
                    package, manifest = self.package_fixture(root)
                    ref = f'1 Enoch {chapter}:1'
                    binding = manifest['review_bindings'][ref][1]
                    if mode == 'missing_peer':
                        manifest['review_bindings'][ref] = manifest['review_bindings'][ref][:1]
                    else:
                        pv_path = package / binding['provenance']
                        pv = read_json(pv_path)
                        if mode.endswith('input'):
                            path = package / binding['input']
                            inputs = read_json(path)
                            inputs[-1 if mode == 'held_input' else 0]['translation']['text'] += ' Unreviewed.'
                            write_json(path, inputs)
                            pv['input_sha256'] = t.sha(path.read_bytes())
                            self.rehash(package, manifest, binding['input'])
                        else:
                            path = package / binding['review']
                            review = read_json(path)
                            if mode == 'peer_verdict':
                                t.review_entries(review)[0]['verdict'] = 'hold'
                            else:
                                review['role'] = pv['role'] = 'corrective_author'
                            write_json(path, review)
                            pv['review_sha256'] = t.sha(path.read_bytes())
                            self.rehash(package, manifest, binding['review'])
                        write_json(pv_path, pv)
                        self.rehash(package, manifest, binding['provenance'])
                    with self.route_package(package, manifest, rebound_manifest=True), self.assertRaises(ValueError):
                        b.verify_current()

    def test_rebound_one_row_receipts_cannot_replace_whole7_8_scopes(self):
        # Exercise the semantic scope guard, not only fixed outer hash pins.
        # All altered bytes and mock pins live in /tmp; no historical raw
        # per-unit projection can erase the actual neighboring HOLD decisions.
        for chapter in (95, 96):
            with self.subTest(chapter=chapter), tempfile.TemporaryDirectory() as root:
                package, manifest = self.package_fixture(root)
                inputs_pin = dict(b.INPUT_SHAS)
                pairs_pin = copy.deepcopy(b.PAIRS)
                for who in ('author', 'independent'):
                    prefix = f'final/ch{chapter}/{who}'
                    input_name, review_name, pv_name = (prefix + suffix for suffix in
                                                       ('-input.json', '-review.json', '-provenance.json'))
                    inputs = read_json(package / input_name)[:1]
                    review = read_json(package / review_name)
                    key = 'reviews' if 'reviews' in review else 'results'
                    review[key] = t.review_entries(review)[:1]
                    write_json(package / input_name, inputs)
                    write_json(package / review_name, review)
                    pv = read_json(package / pv_name)
                    pv['input_sha256'] = t.sha((package / input_name).read_bytes())
                    pv['review_sha256'] = t.sha((package / review_name).read_bytes())
                    write_json(package / pv_name, pv)
                    for name in (input_name, review_name, pv_name):
                        self.rehash(package, manifest, name)
                    identity, role, _, _ = pairs_pin[chapter][who]
                    pairs_pin[chapter][who] = (identity, role, pv['review_sha256'],
                                               t.sha((package / pv_name).read_bytes()))
                    inputs_pin[chapter] = pv['input_sha256']
                with self.route_package(package, manifest, rebound_manifest=True), \
                        patch.object(b, 'INPUT_SHAS', inputs_pin), patch.object(b, 'PAIRS', pairs_pin):
                    with self.assertRaisesRegex(ValueError, 'full paired submitted scope|full7/8 scope'):
                        b.verify_current()

    def test_fixed_chain_missing_receipt_wrong_baseline_or_receipt_postmap_rejected(self):
        for mode in ('missing_receipt', 'stale_manifest', 'baseline', 'postmap', 'receipt_scope',
                     'git_commit', 'git_path', 'git_blob', 'receipt_publication', 'receipt_checked'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as root:
                package, manifest = self.package_fixture(root)
                receipt_path = package / 'application.json'
                if mode == 'missing_receipt':
                    receipt_path.unlink()
                elif mode == 'baseline':
                    manifest['canonical_baseline_sha256']['001/001.yaml'] = '0' * 64
                elif mode.startswith('git_'):
                    key = {'git_commit': 'commit', 'git_path': 'path', 'git_blob': 'blob'}[mode]
                    manifest['baseline_git_blobs']['095/001.yaml'][key] = 'wrong'
                else:
                    receipt = read_json(receipt_path)
                    if mode == 'stale_manifest':
                        receipt['manifest_sha256'] = '0' * 64
                    elif mode == 'postmap':
                        receipt['canonical_after_sha256']['001/001.yaml'] = '0' * 64
                    elif mode == 'receipt_publication':
                        receipt['graphic_publication_approved'] = True
                    elif mode == 'receipt_checked':
                        receipt['canonical_targets_checked'] = False
                    else:
                        receipt['candidate_files'] = 7
                    write_json(receipt_path, receipt)
                with self.route_package(package, manifest,
                                        rebound_manifest=mode == 'baseline' or mode.startswith('git_')):
                    with self.assertRaises((ValueError, OSError)):
                        b.verify_current()
                    if mode == 'missing_receipt':
                        with self.assertRaises((ValueError, OSError)):
                            prior.verify_current()

    def test_full_corpus_owned_unrelated_addition_and_retirement_drift_rejected(self):
        actual = t.corpus_hashes()
        maps = []
        for key in ('095/001.yaml', '096/001.yaml', '001/001.yaml'):
            changed = dict(actual)
            changed[key] = '0' * 64
            maps.append(changed)
        added = dict(actual)
        added['096/004.yaml'] = '0' * 64
        maps.append(added)
        retired = dict(actual)
        del retired['001/001.yaml']
        maps.append(retired)
        for i, changed in enumerate(maps):
            with self.subTest(mode=i), patch.object(t, 'corpus_hashes', return_value=changed):
                with self.assertRaisesRegex(ValueError, 'Canonical changes exceed'):
                    b.verify_current()

    def test_structural_and_registry_promotions_cannot_be_rehashed_away(self):
        for mode in ('count_vote', 'chapter_certificate', 'chapter_flag', 'held_selection'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as root:
                package, manifest = self.package_fixture(root)
                if mode == 'count_vote':
                    name = 'source-only-count-inventory.json'
                    data = read_json(package / name)
                    data['new_count_votes'] = 1
                    write_json(package / name, data)
                    self.rehash(package, manifest, name)
                elif mode == 'chapter_certificate':
                    manifest['chapter_inventories'] = copy.deepcopy(manifest['source_only_count_inventories'])
                elif mode == 'chapter_flag':
                    name = '096-001.candidate.yaml'
                    path = package / name
                    data = yaml.load(path.read_bytes(), Loader=t.LOADER)
                    data['source_correction']['selected_edition_chapter_reviewed'] = True
                    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False))
                    self.rehash(package, manifest, name)
                else:
                    manifest['references'].append('1 Enoch 95:6')
                    manifest['review_bindings']['1 Enoch 95:6'] = copy.deepcopy(manifest['review_bindings']['1 Enoch 95:1'])
                with self.route_package(package, manifest, rebound_manifest=True), self.assertRaises(ValueError):
                    b.verify_current()
        real = sources.registry_data()
        for mode in ('chapter', 'held_unit'):
            registry = copy.deepcopy(real)
            if mode == 'chapter':
                registry['chapters']['95'] = b.NAME
            else:
                registry['units']['96:2'] = b.NAME
            with self.subTest(registry=mode), patch.object(sources, 'registry_data', return_value=registry):
                with self.assertRaisesRegex(ValueError, 'registry'):
                    b.verify_current()
        with patch.object(window, 'verify_applied', side_effect=ValueError('Missing applied95window')):
            with self.assertRaisesRegex(ValueError, 'Missing applied95window'):
                b.verify_current()


if __name__ == '__main__':
    unittest.main()
