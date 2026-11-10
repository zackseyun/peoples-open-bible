"""An existing seven-unit count permits one window, never language release."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from tools.enoch import bounded_application as t
from tools.enoch import count95_window_evidence as window


class Existing95WindowTest(unittest.TestCase):
    @contextmanager
    def fixture(self):
        """Route only the new transaction, map, and old count copies to /tmp."""
        real_artifact = t.artifact
        original = json.loads(real_artifact(t.ROOT, window.COUNT_INDEX).read_text())
        count_files = {window.COUNT_INDEX, *original['files']}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            shutil.copytree(real_artifact(t.ROOT, window.PREFIX), root/window.PREFIX)
            (root/window.RECEIPT).unlink(missing_ok=True)
            for name in count_files:
                target = root/name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(real_artifact(t.ROOT, name), target)
            target = root/window.PATH
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((root/window.PREFIX/'page-map-before.json').read_bytes())

            def routed(base, name):
                name = str(name)
                if name == window.PATH or name.startswith(window.PREFIX + '/') or name in count_files:
                    return real_artifact(root, name)
                return real_artifact(base, name)

            with patch.object(t, 'artifact', side_effect=routed), \
                    patch.object(window, '_lock_path', return_value=root/'apply.lock'):
                yield root

    def guards(self):
        from tools.enoch import count41_44_evidence, count106_108_evidence
        from tools.enoch import count26_27_33_evidence, count85_90_evidence
        return (count41_44_evidence, count106_108_evidence,
                count26_27_33_evidence, count85_90_evidence)

    def write_json(self, path, value):
        path.write_bytes(window._json_bytes(value))

    def index_patch(self, root):
        return patch.object(window, 'INDEX_SHA', t.sha((root/window.INDEX).read_bytes()))

    def test_fixed_proposal_actual_git_preimage_and_only_one_array(self):
        data, after = window.evidence()
        self.assertEqual(t.sha((t.ROOT/window.INDEX).read_bytes()), window.INDEX_SHA)
        before = json.loads((t.ROOT/window.PREFIX/'page-map-before.json').read_text())
        self.assertEqual(t.sha(window._git_before_bytes()), window.BEFORE_SHA)
        expected = copy.deepcopy(before)
        expected['editions']['charles_1906']['chapters']['095']['pages'] = [237, 238]
        self.assertEqual(after, expected)
        self.assertEqual(t.sha(window._json_bytes(after)), window.AFTER_SHA)
        for key, value in window.LIMITS.items():
            self.assertEqual(data[key], value)
            self.assertIs(type(data[key]), type(value))

    def test_fixed_index_and_each_snapshot_byte_hash_are_enforced(self):
        for name in ('index.json', 'page-map-before.json', 'page-map-after.json', 'window-proof.json'):
            with self.subTest(name=name), self.fixture() as root:
                path = root/window.PREFIX/name
                path.write_bytes(path.read_bytes() + b'\n')
                with self.assertRaisesRegex(ValueError, 'fixed source-window index|pinned source-window artifact'):
                    window.evidence()

    def test_proposal_alone_keeps_prior_hash_and_all_four_full_map_guards(self):
        with self.fixture() as root:
            self.assertFalse((root/window.RECEIPT).exists())
            self.assertEqual(window.window_successor(window.BEFORE_SHA), window.BEFORE_SHA)
            for module in self.guards():
                self.assertTrue(module.verify_current_windows())
            (root/window.PATH).write_bytes((root/window.PREFIX/'page-map-after.json').read_bytes())
            for module in (*self.guards(), window):
                with self.subTest(module=module.__name__), self.assertRaisesRegex(
                        ValueError, 'explicit reviewed window successor'):
                    module.verify_current_windows()

    def test_negative_caller_predecessor_fails(self):
        with self.assertRaisesRegex(ValueError, 'different predecessor'):
            window.window_successor('0'*64)

    def test_apply_fixture_receipt_exact_after_map_and_no_language_promotion(self):
        with self.fixture() as root:
            proof = window.apply()
            self.assertEqual(proof, window._expected_receipt())
            self.assertEqual((root/window.RECEIPT).read_bytes(), window._json_bytes(proof))
            self.assertEqual(t.sha((root/window.PATH).read_bytes()), window.AFTER_SHA)
            self.assertEqual(window.window_successor(window.BEFORE_SHA), window.AFTER_SHA)
            self.assertEqual(window.verify_applied(), proof)
            for module in self.guards():
                self.assertTrue(module.verify_current_windows())
            self.assertFalse(proof['wording_approval'])
            self.assertFalse(proof['reader_release_policy_changed'])
            self.assertEqual(proof['new_count_inventories'], 0)
            self.assertEqual(proof['new_count_votes'], 0)
            self.assertEqual(proof['new_language_votes'], 0)
            self.assertEqual(proof['canonical_YAML_changes'], 0)
            self.assertFalse(list(root.rglob('*.yaml')))

    def test_applied_receipt_without_actual_postimage_fails(self):
        with self.fixture() as root:
            self.write_json(root/window.RECEIPT, window._expected_receipt())
            with self.assertRaisesRegex(ValueError, 'explicit reviewed window successor'):
                window.window_successor(window.BEFORE_SHA)

    def test_applied_receipt_changes_and_byte_drift_fail(self):
        for mode in ('status', 'index', 'proof', 'after', 'scope', 'whitespace'):
            with self.subTest(mode=mode), self.fixture() as root:
                receipt = window.apply()
                path = root/window.RECEIPT
                if mode == 'whitespace':
                    path.write_bytes(path.read_bytes() + b'\n')
                else:
                    field = {'status': 'status', 'index': 'index_sha256',
                             'proof': 'proof_sha256', 'after': 'after_sha256',
                             'scope': 'new_language_votes'}[mode]
                    receipt[field] = 1 if mode == 'scope' else 'wrong'
                    self.write_json(path, receipt)
                with self.assertRaisesRegex(ValueError, 'exact applied.*receipt'):
                    window.window_successor(window.BEFORE_SHA)

    def test_every_global_guard_rejects_unrelated_array_and_metadata_after_apply(self):
        for mode in ('other_chapter', 'same_chapter_hint', 'other_edition', 'timestamp'):
            with self.subTest(mode=mode), self.fixture() as root:
                window.apply()
                path = root/window.PATH
                data = json.loads(path.read_text())
                if mode == 'other_chapter':
                    data['editions']['charles_1906']['chapters']['001']['pages'] = [1]
                elif mode == 'same_chapter_hint':
                    data['editions']['charles_1906']['chapters']['095']['opening_hint'] = 'unreviewed'
                elif mode == 'other_edition':
                    other = next(k for k in data['editions'] if k != 'charles_1906')
                    data['editions'][other]['unreviewed'] = True
                else:
                    data['updated'] = 'unreviewed'
                self.write_json(path, data)
                for module in (*self.guards(), window):
                    with self.assertRaisesRegex(ValueError, 'explicit reviewed window successor'):
                        module.verify_current_windows()

    def test_false95_scope_and_count_language_release_promotions_rejected_after_rehash(self):
        mutations = [('chapter', 96), ('chapter', 95.0),
                     ('units', list(range(1, 6))), ('units', [float(n) for n in range(1, 8)]),
                     ('chapter_pages', [237]), ('new_count_votes', 1),
                     ('new_count_inventories', 1), ('new_language_votes', 1),
                     ('canonical_YAML_changes', 5), ('wording_approval', True),
                     ('reader_release_policy_changed', True), ('publication_approved', True),
                     ('new_language_votes', False)]
        for key, value in mutations:
            with self.subTest(key=key, value=value), self.fixture() as root:
                path = root/window.INDEX
                data = json.loads(path.read_text())
                data[key] = value
                self.write_json(path, data)
                with self.index_patch(root), self.assertRaisesRegex(ValueError, 'scope or approval limits'):
                    window.evidence()

    def test_rehashed_unrelated_snapshot_cannot_hide_behind_correct95_array(self):
        with self.fixture() as root:
            after_path = root/window.PREFIX/'page-map-after.json'
            after = json.loads(after_path.read_text())
            after['editions']['charles_1906']['chapters']['001']['opening_hint'] = 'unreviewed'
            self.write_json(after_path, after)
            after_sha = t.sha(after_path.read_bytes())
            proof_path = root/window.PREFIX/'window-proof.json'
            proof = json.loads(proof_path.read_text())
            proof['after_sha256'] = after_sha
            self.write_json(proof_path, proof)
            proof_sha = t.sha(proof_path.read_bytes())
            index_path = root/window.INDEX
            data = json.loads(index_path.read_text())
            data['after_sha256'] = after_sha
            data['files'][window.PREFIX+'/page-map-after.json'] = after_sha
            data['files'][window.PREFIX+'/window-proof.json'] = proof_sha
            self.write_json(index_path, data)
            with self.index_patch(root), patch.object(window, 'AFTER_SHA', after_sha), \
                    patch.object(window, 'PROOF_SHA', proof_sha), \
                    self.assertRaisesRegex(ValueError, 'exceeds one exact array'):
                window.evidence()

    def test_rehashed_false_proof_is_rejected(self):
        with self.fixture() as root:
            proof_path = root/window.PREFIX/'window-proof.json'
            proof = json.loads(proof_path.read_text())
            proof['changes'][0]['after'] = [237]
            self.write_json(proof_path, proof)
            proof_sha = t.sha(proof_path.read_bytes())
            index = root/window.INDEX
            data = json.loads(index.read_text())
            data['files'][window.PREFIX+'/window-proof.json'] = proof_sha
            self.write_json(index, data)
            with self.index_patch(root), patch.object(window, 'PROOF_SHA', proof_sha), \
                    self.assertRaisesRegex(ValueError, 'bounded window proof'):
                window.evidence()

    def test_rehashed_proof_cannot_promote_existing_count_or_language_scope(self):
        for key in ('new_count_inventories', 'new_count_votes', 'new_language_votes',
                    'canonical_YAML_changes', 'wording_approval', 'reader_release_policy_changed'):
            with self.subTest(key=key), self.fixture() as root:
                path = root/window.PREFIX/'window-proof.json'
                proof = json.loads(path.read_text())
                proof[key] = True if isinstance(window.LIMITS[key], bool) else 1
                self.write_json(path, proof)
                proof_sha = t.sha(path.read_bytes())
                index_path = root/window.INDEX
                index = json.loads(index_path.read_text())
                index['files'][window.PREFIX+'/window-proof.json'] = proof_sha
                self.write_json(index_path, index)
                with self.index_patch(root), patch.object(window, 'PROOF_SHA', proof_sha), \
                        self.assertRaisesRegex(ValueError, 'bounded window proof'):
                    window.evidence()

    def test_original_count_index_and_raw_receipts_remain_pinned(self):
        for name in ('index', 'input', 'review', 'provenance', 'author_provenance'):
            with self.subTest(name=name), self.fixture() as root:
                index = json.loads((root/window.COUNT_INDEX).read_text())
                path = root/window.COUNT_INDEX if name == 'index' else root/index[name]
                path.write_bytes(path.read_bytes() + b'\n')
                with self.assertRaisesRegex(ValueError, 'original paired count index|Count-profile artifact hash'):
                    window.evidence()

    def test_actual_git_preimage_is_not_merely_a_claim_in_proof(self):
        with self.fixture(), patch.object(window, '_git_before_bytes', return_value=b'not the Git preimage'):
            with self.assertRaisesRegex(ValueError, 'actual Git window predecessor'):
                window.evidence()

    def test_direct_full_profile_no_global_count_loader_cycle(self):
        from tools.enoch import structural_count_profiles, structural_counts
        real = structural_count_profiles.load
        with self.fixture(), patch.object(structural_counts, 'load_all_inventories',
                                          side_effect=AssertionError('global loader cycle')), \
                patch.object(structural_count_profiles, 'load', wraps=real) as loaded:
            window.evidence()
            self.assertEqual(loaded.call_count, 1)
            self.assertEqual(Path(loaded.call_args.args[0]).name, 'paired-count-index-v2.json')

    def test_all108_original_structural_inventories_unchanged(self):
        from tools.enoch.structural_counts import load_all_inventories
        from tools.enoch.full_repair_progress import build
        result = load_all_inventories()
        self.assertEqual(result[95]['units'], list(range(1, 8)))
        self.assertNotIn(window.INDEX, [v['artifact'] for v in result.values()])
        # The structural-only loader is one part of the union. Older paired
        # chapter inventories also enter through historical/application evidence.
        report = build()
        self.assertEqual(report['chapters_with_imported_paired_count_inventory'], list(range(1, 109)))
        self.assertEqual(report['evidence_inventory_warnings'], [])

    def test_receipt_write_failure_rolls_back_exact_map(self):
        with self.fixture() as root:
            real = window._atomic_write

            def fail_receipt(path, raw, expected):
                if path == root/window.RECEIPT:
                    raise OSError('injected receipt write failure')
                return real(path, raw, expected)

            with patch.object(window, '_atomic_write', side_effect=fail_receipt), \
                    self.assertRaisesRegex(OSError, 'injected receipt'):
                window.apply()
            self.assertEqual(t.sha((root/window.PATH).read_bytes()), window.BEFORE_SHA)
            self.assertFalse((root/window.RECEIPT).exists())
            self.assertFalse(list(root.rglob('*.count95-*')))

    def test_post_receipt_verification_failure_rolls_back_both(self):
        with self.fixture() as root, patch.object(window, 'verify_applied',
                                                  side_effect=ValueError('injected postcheck')):
            with self.assertRaisesRegex(ValueError, 'injected postcheck'):
                window.apply()
            self.assertEqual(t.sha((root/window.PATH).read_bytes()), window.BEFORE_SHA)
            self.assertFalse((root/window.RECEIPT).exists())

    def test_post_rename_directory_sync_failure_is_known_committed_and_rolled_back(self):
        with self.fixture() as root:
            fsync = window.os.fsync
            calls = 0

            def fail_second(fd):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError('injected directory sync failure')
                return fsync(fd)

            with patch.object(window.os, 'fsync', side_effect=fail_second), \
                    self.assertRaisesRegex(window.AtomicWriteError, 'directory sync'):
                window.apply()
            self.assertEqual(t.sha((root/window.PATH).read_bytes()), window.BEFORE_SHA)
            self.assertFalse((root/window.RECEIPT).exists())

    def test_fresh_preimage_check_and_rollback_never_overwrite_concurrent_map(self):
        for phase in ('before_map_replace', 'receipt_failure'):
            with self.subTest(phase=phase), self.fixture() as root:
                real = window._atomic_write
                foreign = b'concurrent external map bytes\n'
                injected = False

                def interfere(path, raw, expected):
                    nonlocal injected
                    if not injected and ((phase == 'before_map_replace' and path == root/window.PATH) or
                                         (phase == 'receipt_failure' and path == root/window.RECEIPT)):
                        injected = True
                        (root/window.PATH).write_bytes(foreign)
                        if phase == 'receipt_failure':
                            raise OSError('injected after concurrent writer')
                    return real(path, raw, expected)

                with patch.object(window, '_atomic_write', side_effect=interfere), \
                        self.assertRaises((window.AtomicWriteError, OSError)):
                    window.apply()
                self.assertEqual((root/window.PATH).read_bytes(), foreign)
                self.assertFalse((root/window.RECEIPT).exists())

    def test_concurrent_receipt_is_not_removed_or_overwritten_by_rollback(self):
        with self.fixture() as root:
            real = window._atomic_write
            foreign = b'concurrent receipt\n'

            def interfere(path, raw, expected):
                if path == root/window.RECEIPT:
                    path.write_bytes(foreign)
                return real(path, raw, expected)

            with patch.object(window, '_atomic_write', side_effect=interfere), \
                    self.assertRaisesRegex(RuntimeError, 'concurrent receipt.*rollback refused'):
                window.apply()
            self.assertEqual((root/window.RECEIPT).read_bytes(), foreign)
            with self.assertRaisesRegex(ValueError, 'exact applied.*receipt'):
                window.verify_current_windows()

    def test_two_cooperating_callers_are_serialized_and_repeat_refuses(self):
        with self.fixture() as root:
            def call():
                try:
                    window.apply()
                    return 'applied'
                except ValueError as error:
                    self.assertIn('already has an application receipt', str(error))
                    return 'already applied'

            with ThreadPoolExecutor(max_workers=2) as executor:
                result = list(executor.map(lambda _: call(), range(2)))
            self.assertCountEqual(result, ['applied', 'already applied'])
            before = (root/window.PATH).read_bytes(), (root/window.RECEIPT).read_bytes()
            with self.assertRaisesRegex(ValueError, 'already has an application receipt'):
                window.apply()
            self.assertEqual(before, ((root/window.PATH).read_bytes(), (root/window.RECEIPT).read_bytes()))


if __name__ == '__main__':
    unittest.main()
