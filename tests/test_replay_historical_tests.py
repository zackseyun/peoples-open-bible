"""Runner isolation tests; synthetic passes are not research evidence."""
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from tools.textual_restoration import replay_historical_tests as module


class HistoricalTestRunnerTests(unittest.TestCase):
    def run_mocked(self, result=None, returncode=0, side_effect=None):
        payload = result or {"passed": True, "tests_run": 5, "skipped": 0, "expected_failures": 0}
        reply = subprocess.CompletedProcess([], returncode, json.dumps(payload), "child diagnostic")
        with patch.object(module, "git", side_effect=[module.COMMIT.encode(), b"archive"]), \
             patch.object(module, "_registry_genesis_archive_paths", return_value=["tests"]), \
             patch.object(module, "extract_regular") as extract, \
             patch.object(module.subprocess, "run", return_value=reply, side_effect=side_effect) as child:
            try:
                actual = module.run_suite("registry_genesis")
                return actual, child.call_args
            finally:
                if extract.called:
                    self.assertFalse(extract.call_args.args[1].exists(), "private tree leaked")

    def test_unknown_suite_cannot_dispatch_arbitrary_code(self):
        with patch.object(module, "git") as git:
            with self.assertRaises(ValueError):
                module.run_suite("unittest.__main__")
            git.assert_not_called()

    def test_fixed_commit_resolution_required(self):
        with patch.object(module, "git", return_value=b"0" * 40):
            with self.assertRaisesRegex(ValueError, "resolution mismatch"):
                module.run_suite("genesis")

    def test_result_is_historical_and_child_is_isolated(self):
        result, call = self.run_mocked()
        self.assertEqual(result["commit"], module.COMMIT)
        self.assertFalse(result["current_corpus_validated"])
        self.assertFalse(result["application_approved"])
        self.assertEqual(call.args[0][:3], [module.sys.executable, "-I", "-c"])
        self.assertNotEqual(Path(call.kwargs["cwd"]), module.ROOT)
        self.assertFalse(Path(call.kwargs["cwd"]).exists())

    def test_child_failure_propagates_and_cleans_up(self):
        with self.assertRaisesRegex(RuntimeError, "child diagnostic"):
            self.run_mocked(returncode=1)

    def test_timeout_propagates_and_cleans_up(self):
        with self.assertRaises(subprocess.TimeoutExpired):
            self.run_mocked(side_effect=subprocess.TimeoutExpired("child", 600))

    def test_missing_skipped_and_expected_failure_checks_cannot_pass(self):
        valid = {"passed": True, "tests_run": 5, "skipped": 0, "expected_failures": 0}
        for field, value in (("passed", False), ("tests_run", 0), ("skipped", 1), ("expected_failures", 1)):
            with self.subTest(field=field), self.assertRaisesRegex(RuntimeError, "coverage mismatch"):
                self.run_mocked({**valid, field: value})

    def test_derivative_paths_come_from_commit_and_cannot_escape(self):
        for path in ("../translation_es/a", "translation_es/../../outside", "translation_es/[ab]", "/translation_es/a"):
            manifest = {"unchanged_derivative_context_pins": {path: "0" * 64}}
            with self.subTest(path=path), patch.object(module, "git", return_value=json.dumps(manifest).encode()):
                with self.assertRaisesRegex(ValueError, "derivative path"):
                    module._archive_paths(module.ROOT)


    def test_genesis_dependency_paths_use_only_frozen_manifests(self):
        paths = module._registry_genesis_archive_paths(module.ROOT)
        self.assertEqual(paths, sorted(set(paths)))
        self.assertIn("tools", paths)
        self.assertIn("translation/ot/numbers/022/019.yaml", paths)
        self.assertIn("translation/ot/jeremiah/010/010.yaml", paths)
        self.assertNotIn("translation/ot", paths)
        archive = module.git(module.ROOT, "archive", "--format=tar", module.COMMIT, "--", *paths)
        self.assertEqual(len(archive), 6932480)
        import hashlib
        self.assertEqual(hashlib.sha256(archive).hexdigest(),
                         "3f1c187c6a74f7b9bf219b2d9e59e6fde369ffc1e0fa536159e2847c2dc18f73")

    def test_genesis_dependency_paths_reject_escape_and_pathspec(self):
        for path in ("../outside", "sources/../outside", "sources/[ab]", "/sources/a", "unrelated/a"):
            replies = [
                {"prior_package_input_pins": {path: "0" * 64},
                 "unchanged_derivative_context_pins": {}},
                {"input_pins": {}}, {"cases": []},
            ]
            with self.subTest(path=path), patch.object(module, "git", side_effect=[json.dumps(x).encode() for x in replies]):
                with self.assertRaisesRegex(ValueError, "Genesis dependency path"):
                    module._registry_genesis_archive_paths(module.ROOT)

    def run_esdras_mocked(self, result=None, *, missing_baseline=False):
        payload = result or {"passed": True, "tests_run": 6, "skipped": 0, "expected_failures": 0}
        reply = subprocess.CompletedProcess([], 0, json.dumps(payload), "")
        outputs = [module.ESDRAS8_COMMIT.encode(),
                   ("0" * 40 if missing_baseline else module.ESDRAS8_BASE).encode(),
                   b"/private/frozen-history.git", b"archive"]
        with patch.object(module, "git", side_effect=outputs) as git, \
             patch.object(module, "_esdras8_archive_paths", return_value=["tests"]) as paths, \
             patch.object(module, "extract_regular") as extract, \
             patch.object(module.subprocess, "run", return_value=reply) as child:
            try:
                actual = module.run_suite("esdras8_partition")
                return actual, child.call_args, git.call_args_list
            finally:
                if missing_baseline:
                    paths.assert_not_called()
                    child.assert_not_called()
                if extract.called:
                    self.assertFalse(extract.call_args.args[1].exists(), "private tree leaked")

    def test_esdras_has_separate_fixed_checkpoint_and_exact_six_checks(self):
        result, call, calls = self.run_esdras_mocked()
        self.assertEqual(result["commit"], module.ESDRAS8_COMMIT)
        self.assertEqual(result["tests_run"], 6)
        self.assertFalse(result["current_corpus_validated"])
        self.assertFalse(result["application_approved"])
        self.assertEqual(call.args[0][:3], [module.sys.executable, "-I", "-c"])
        self.assertEqual(json.loads(call.args[0][-1]), ["test_1esdras8_partition_application"])
        env = call.kwargs["env"]
        self.assertEqual(env["GIT_DIR"], "/private/frozen-history.git")
        self.assertEqual(env["GIT_WORK_TREE"], call.kwargs["cwd"])
        self.assertNotEqual(Path(env["GIT_WORK_TREE"]), module.ROOT)
        self.assertFalse(Path(env["GIT_WORK_TREE"]).exists())
        self.assertEqual(env["GIT_OPTIONAL_LOCKS"], "0")
        self.assertEqual(env["GIT_NO_REPLACE_OBJECTS"], "1")
        self.assertEqual(calls[-1].args[1:5], ("archive", "--format=tar", module.ESDRAS8_COMMIT, "--"))

    def test_esdras_requires_original_base_and_rejects_partial_results(self):
        with self.assertRaisesRegex(ValueError, "baseline resolution mismatch"):
            self.run_esdras_mocked(missing_baseline=True)
        valid = {"passed": True, "tests_run": 6, "skipped": 0, "expected_failures": 0}
        for field, value in (("passed", False), ("tests_run", 5), ("tests_run", 7),
                             ("skipped", 1), ("expected_failures", 1)):
            with self.subTest(field=field, value=value), self.assertRaisesRegex(RuntimeError, "coverage mismatch"):
                self.run_esdras_mocked({**valid, field: value})

    def test_esdras_dependency_paths_are_frozen_and_reject_unsafe_manifests(self):
        paths = module._esdras8_archive_paths(module.ROOT)
        self.assertEqual(paths, sorted(set(paths)))
        self.assertIn("tools", paths)
        self.assertIn("translation/deuterocanon/1_esdras", paths)
        self.assertIn("sources/lxx/swete/final_corpus_normalized/1ES.jsonl", paths)
        self.assertIn(".github/workflows/corpus-integrity.yml", paths)
        self.assertNotIn("translation/deuterocanon", paths)
        for path in ("../outside", "sources/../outside", "sources/[ab]", "/sources/a", "unrelated/a"):
            evidence = {"baseline_commit": module.ESDRAS8_BASE,
                        "reviewed_file_pins": {path: "0" * 64}, "unchanged_live_inputs": []}
            with self.subTest(path=path), patch.object(module, "git", return_value=json.dumps(evidence).encode()):
                with self.assertRaisesRegex(ValueError, "Esdras dependency path"):
                    module._esdras8_archive_paths(module.ROOT)

    def run_esdras5_mocked(self, result=None, *, missing_baseline=False, returncode=0, chapter=5):
        payload = result or {"passed": True, "tests_run": 6, "skipped": 0, "expected_failures": 0}
        reply = subprocess.CompletedProcess([], returncode, json.dumps(payload), "esdras5 child diagnostic")
        commit = getattr(module, f"ESDRAS{chapter}_COMMIT")
        baseline = getattr(module, f"ESDRAS{chapter}_BASE")
        outputs = [commit.encode(),
                   ("0" * 40 if missing_baseline else baseline).encode(),
                   b"/private/frozen-history.git", b"archive"]
        with patch.object(module, "git", side_effect=outputs) as git, \
             patch.object(module, f"_esdras{chapter}_archive_paths", return_value=["tests"]) as paths, \
             patch.object(module, "extract_regular") as extract, \
             patch.object(module.subprocess, "run", return_value=reply) as child:
            try:
                actual = module.run_suite(f"esdras{chapter}_partition")
                return actual, child.call_args, git.call_args_list
            finally:
                if missing_baseline:
                    paths.assert_not_called()
                    child.assert_not_called()
                if extract.called:
                    self.assertFalse(extract.call_args.args[1].exists(), "private tree leaked")

    def test_esdras5_uses_distinct_snapshot_and_private_git_context(self):
        result, call, calls = self.run_esdras5_mocked()
        self.assertEqual(result["commit"], module.ESDRAS5_COMMIT)
        self.assertEqual(result["tests_run"], 6)
        self.assertFalse(result["current_corpus_validated"])
        self.assertFalse(result["application_approved"])
        self.assertEqual(call.args[0][:3], [module.sys.executable, "-I", "-c"])
        self.assertEqual(json.loads(call.args[0][-1]), ["test_1esdras5_partition_application"])
        env = call.kwargs["env"]
        self.assertEqual(env["GIT_DIR"], "/private/frozen-history.git")
        self.assertEqual(env["GIT_WORK_TREE"], call.kwargs["cwd"])
        self.assertNotEqual(Path(env["GIT_WORK_TREE"]), module.ROOT)
        self.assertFalse(Path(env["GIT_WORK_TREE"]).exists())
        self.assertEqual(env["GIT_OPTIONAL_LOCKS"], "0")
        self.assertEqual(env["GIT_NO_REPLACE_OBJECTS"], "1")
        self.assertEqual(calls[-1].args[1:5], ("archive", "--format=tar", module.ESDRAS5_COMMIT, "--"))

    def test_esdras5_rejects_missing_baseline_failure_and_wrong_test_counts(self):
        with self.assertRaisesRegex(ValueError, "baseline resolution mismatch"):
            self.run_esdras5_mocked(missing_baseline=True)
        with self.assertRaisesRegex(RuntimeError, "esdras5 child diagnostic"):
            self.run_esdras5_mocked(returncode=1)
        valid = {"passed": True, "tests_run": 6, "skipped": 0, "expected_failures": 0}
        for field, value in (("passed", False), ("tests_run", 5), ("tests_run", 7),
                             ("skipped", 1), ("expected_failures", 1)):
            with self.subTest(field=field, value=value), self.assertRaisesRegex(RuntimeError, "coverage mismatch"):
                self.run_esdras5_mocked({**valid, field: value})

    def test_esdras5_dependency_closure_is_frozen_and_cannot_escape(self):
        paths = module._esdras5_archive_paths(module.ROOT)
        self.assertEqual(paths, sorted(set(paths)))
        for path in ("tools", "translation/deuterocanon/1_esdras",
                     "sources/lxx/swete/final_corpus_normalized/1ES.jsonl",
                     "sources/lxx/swete/final_corpus_adjudicated/ADA.jsonl",
                     "sources/textual_restoration/candidates/1esdras8_source_partition.2026-10-19.v1.json",
                     "sources/textual_restoration/comparisons/1esdras8_application.2026-10-19.v1.json",
                     "sources/textual_restoration/quarantine/1esdras5_duplicate145.2026-10-19.v1.yaml"):
            self.assertIn(path, paths)
        self.assertNotIn("translation/deuterocanon", paths)
        for path in ("../outside", "sources/../outside", "sources/[ab]", "/sources/a", "unrelated/a"):
            evidence = {"baseline_commit": module.ESDRAS5_BASE,
                        "reviewed_file_pins": {path: "0" * 64}, "unchanged_live_inputs": []}
            with self.subTest(path=path), patch.object(module, "git", return_value=json.dumps(evidence).encode()):
                with self.assertRaisesRegex(ValueError, "Esdras5 dependency path"):
                    module._esdras5_archive_paths(module.ROOT)

    def test_esdras6_runs_only_original_six_tests_in_separate_snapshot(self):
        result, call, calls = self.run_esdras5_mocked(chapter=6)
        self.assertEqual(result['commit'], module.ESDRAS6_COMMIT)
        self.assertEqual(result['tests_run'], 6)
        self.assertFalse(result['current_corpus_validated'])
        self.assertFalse(result['application_approved'])
        self.assertEqual(call.args[0][:3], [module.sys.executable, '-I', '-c'])
        self.assertEqual(json.loads(call.args[0][-1]), ['test_1esdras6_partition_application'])
        env = call.kwargs['env']
        self.assertEqual(env['GIT_DIR'], '/private/frozen-history.git')
        self.assertEqual(env['GIT_WORK_TREE'], call.kwargs['cwd'])
        self.assertNotEqual(Path(env['GIT_WORK_TREE']), module.ROOT)
        self.assertFalse(Path(env['GIT_WORK_TREE']).exists())
        self.assertEqual(env['GIT_OPTIONAL_LOCKS'], '0')
        self.assertEqual(env['GIT_NO_REPLACE_OBJECTS'], '1')
        self.assertEqual(calls[-1].args[1:5], ('archive', '--format=tar', module.ESDRAS6_COMMIT, '--'))

    def test_esdras6_missing_baseline_child_failure_and_missing_checks_fail(self):
        with self.assertRaisesRegex(ValueError, 'baseline resolution mismatch'):
            self.run_esdras5_mocked(chapter=6, missing_baseline=True)
        with self.assertRaisesRegex(RuntimeError, 'child diagnostic'):
            self.run_esdras5_mocked(chapter=6, returncode=1)
        valid = {'passed': True, 'tests_run': 6, 'skipped': 0, 'expected_failures': 0}
        for field, value in (('passed', False), ('tests_run', 5), ('tests_run', 7),
                             ('skipped', 1), ('expected_failures', 1)):
            with self.subTest(field=field, value=value), self.assertRaisesRegex(RuntimeError, 'coverage mismatch'):
                self.run_esdras5_mocked({**valid, field: value}, chapter=6)

    def test_esdras6_archive_has_all_three_frozen_evidence_sets_and_safe_paths(self):
        paths = module._esdras6_archive_paths(module.ROOT)
        self.assertEqual(paths, sorted(set(paths)))
        for chapter in (5, 6, 8):
            self.assertIn(f'sources/textual_restoration/comparisons/1esdras{chapter}_application.2026-10-19.v1.json', paths)
            self.assertIn(f'sources/textual_restoration/candidates/1esdras{chapter}_source_partition.2026-10-19.v1.json', paths)
        self.assertIn('tools', paths)
        self.assertIn('translation/deuterocanon/1_esdras', paths)
        self.assertIn('sources/lxx/swete/final_corpus_adjudicated/ADA.jsonl', paths)
        self.assertIn('tests/test_1esdras6_partition_application.py', paths)
        self.assertNotIn('translation/deuterocanon', paths)
        for path in ('../outside', 'sources/../outside', 'sources/[ab]', '/sources/a', 'unrelated/a'):
            evidence = {'baseline_commit': module.ESDRAS6_BASE,
                        'reviewed_file_pins': {path: '0' * 64}, 'unchanged_live_inputs': []}
            with self.subTest(path=path), patch.object(module, 'git', return_value=json.dumps(evidence).encode()):
                with self.assertRaisesRegex(ValueError, 'Esdras6 dependency path'):
                    module._esdras6_archive_paths(module.ROOT)

    def run_letter_jeremiah_mocked(self, result=None, *, missing_baseline=False,
                                  returncode=0, side_effect=None):
        payload = result or {"passed": True, "tests_run": 5, "skipped": 0, "expected_failures": 0}
        reply = subprocess.CompletedProcess([], returncode, json.dumps(payload), "letter child diagnostic")
        outputs = [module.LETTER_JEREMIAH69_70_COMMIT.encode(),
                   ("0" * 40 if missing_baseline else module.LETTER_JEREMIAH69_70_BASE).encode(),
                   b"/private/frozen-history.git", b"archive"]
        with patch.object(module, "git", side_effect=outputs) as git, \
             patch.object(module, "_letter_jeremiah69_70_archive_paths", return_value=["tests"]) as paths, \
             patch.object(module, "extract_regular") as extract, \
             patch.object(module.subprocess, "run", return_value=reply, side_effect=side_effect) as child:
            try:
                actual = module.run_suite("letter_jeremiah69_70")
                return actual, child.call_args, git.call_args_list
            finally:
                if missing_baseline:
                    paths.assert_not_called()
                    child.assert_not_called()
                if extract.called:
                    self.assertFalse(extract.call_args.args[1].exists(), "private tree leaked")

    def test_letter_jeremiah_uses_literal_applied_checkpoint_and_original_five_tests(self):
        self.assertEqual(module.LETTER_JEREMIAH69_70_COMMIT,
                         "a0ae3c29b4525087faa1ceab1ed2822301aa2f37")
        self.assertEqual(module.LETTER_JEREMIAH69_70_BASE,
                         "b388ce5089ea64ecd3adac354dbd1118c7dbea85")
        self.assertNotEqual(module.LETTER_JEREMIAH69_70_COMMIT, module.LETTER_JEREMIAH69_70_BASE)
        result, call, calls = self.run_letter_jeremiah_mocked()
        self.assertEqual(result["commit"], module.LETTER_JEREMIAH69_70_COMMIT)
        self.assertEqual(result["tests_run"], 5)
        self.assertFalse(result["current_corpus_validated"])
        self.assertFalse(result["application_approved"])
        self.assertEqual(call.args[0][:3], [module.sys.executable, "-I", "-c"])
        self.assertEqual(json.loads(call.args[0][-1]), ["test_letter_jeremiah_69_70_correction"])
        env = call.kwargs["env"]
        self.assertEqual(env["GIT_DIR"], "/private/frozen-history.git")
        self.assertEqual(env["GIT_WORK_TREE"], call.kwargs["cwd"])
        self.assertNotEqual(Path(env["GIT_WORK_TREE"]), module.ROOT)
        self.assertFalse(Path(env["GIT_WORK_TREE"]).exists())
        self.assertEqual(env["GIT_OPTIONAL_LOCKS"], "0")
        self.assertEqual(env["GIT_NO_REPLACE_OBJECTS"], "1")
        self.assertEqual(calls[0].args[1:],
                         ("rev-parse", "--verify", f"{module.LETTER_JEREMIAH69_70_COMMIT}^{{commit}}"))
        self.assertEqual(calls[1].args[1:],
                         ("rev-parse", "--verify", f"{module.LETTER_JEREMIAH69_70_BASE}^{{commit}}"))
        self.assertEqual(calls[-1].args[1:5],
                         ("archive", "--format=tar", module.LETTER_JEREMIAH69_70_COMMIT, "--"))

    def test_letter_jeremiah_missing_baseline_child_failure_and_partial_results_fail(self):
        with self.assertRaisesRegex(ValueError, "baseline resolution mismatch"):
            self.run_letter_jeremiah_mocked(missing_baseline=True)
        with self.assertRaisesRegex(RuntimeError, "letter child diagnostic"):
            self.run_letter_jeremiah_mocked(returncode=1)
        with self.assertRaises(subprocess.TimeoutExpired):
            self.run_letter_jeremiah_mocked(side_effect=subprocess.TimeoutExpired("child", 600))
        valid = {"passed": True, "tests_run": 5, "skipped": 0, "expected_failures": 0}
        for field, value in (("passed", False), ("tests_run", 4), ("tests_run", 6),
                             ("skipped", 1), ("expected_failures", 1)):
            with self.subTest(field=field, value=value), self.assertRaisesRegex(RuntimeError, "coverage mismatch"):
                self.run_letter_jeremiah_mocked({**valid, field: value})

    def test_letter_jeremiah_archive_keeps_original_evidence_method_and_complete_book(self):
        import hashlib
        import io
        import tarfile

        paths = module._letter_jeremiah69_70_archive_paths(module.ROOT)
        self.assertEqual(paths, sorted(set(paths)))
        evidence_path = "sources/textual_restoration/comparisons/letter_jeremiah_69_70.2026-10-19.v1.json"
        raw = module.git(module.ROOT, "show", f"{module.LETTER_JEREMIAH69_70_COMMIT}:{evidence_path}")
        evidence = json.loads(raw)
        self.assertEqual(evidence["baseline_commit"], module.LETTER_JEREMIAH69_70_BASE)
        for field in ("historical_input_pins", "reviewed_file_pins", "unchanged_live_inputs"):
            self.assertTrue(set(evidence[field]).issubset(paths), field)
        for path in ("tools", "translation/deuterocanon/letter_of_jeremiah",
                     "sources/lxx/swete/final_corpus_adjudicated/LJE.jsonl",
                     "sources/early_christian_texts/catalog.json", "schema/verse.schema.json",
                     ".github/workflows/corpus-integrity.yml", evidence_path):
            self.assertIn(path, paths)
        self.assertNotIn("translation/deuterocanon", paths)
        self.assertNotIn("sources/lxx/swete", paths)
        self.assertNotIn("docs", paths)
        archive = module.git(module.ROOT, "archive", "--format=tar",
                             module.LETTER_JEREMIAH69_70_COMMIT, "--", *paths)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tree:
            book = "translation/deuterocanon/letter_of_jeremiah/"
            self.assertEqual(sum(m.isfile() and m.name.startswith(book) and m.name.endswith(".yaml")
                                 for m in tree.getmembers()), 72)
            for path, pin in evidence["reviewed_file_pins"].items():
                self.assertEqual(hashlib.sha256(tree.extractfile(path).read()).hexdigest(), pin)
            test = "tests/test_letter_jeremiah_69_70_correction.py"
            self.assertEqual(evidence["reviewed_file_pins"][test],
                             "22f466d1223a7b409cf1304e9af4b35e82ac9d3002281698f85487e6ead80eb9")
            method = "docs/TEXTUAL_ADJUDICATION_METHOD.md"
            method_pin = "89705fb3caab6c7b124e84e7adb6db4e7e4b7181b41c407135f7df1149b41a8e"
            self.assertEqual(evidence["historical_input_pins"][method], method_pin)
            self.assertEqual(hashlib.sha256(tree.extractfile(method).read()).hexdigest(), method_pin)
            self.assertIn(method, evidence["unchanged_live_inputs"])
            workflow = tree.extractfile(".github/workflows/corpus-integrity.yml").read().decode()
            self.assertIn(f"git fetch --no-tags --depth=1 origin {module.LETTER_JEREMIAH69_70_BASE}", workflow)
            self.assertIn("python -m unittest discover -s tests -p 'test_letter_jeremiah_69_70_correction.py'", workflow)

    def test_letter_jeremiah_archive_rejects_changed_baseline_and_unsafe_dependency_paths(self):
        valid = {"baseline_commit": module.LETTER_JEREMIAH69_70_BASE,
                 "historical_input_pins": {}, "reviewed_file_pins": {}, "unchanged_live_inputs": []}
        with patch.object(module, "git", return_value=json.dumps({**valid, "baseline_commit": "0" * 40}).encode()):
            with self.assertRaisesRegex(ValueError, "Letter of Jeremiah baseline mismatch"):
                module._letter_jeremiah69_70_archive_paths(module.ROOT)
        for field in ("historical_input_pins", "reviewed_file_pins", "unchanged_live_inputs"):
            for path in ("../outside", "sources/../outside", "sources/[ab]", "/sources/a",
                         "sources/*", "sources/a?", "sources/a:b", "sources/a\\b", "unrelated/a",
                         "translation/deuterocanon/1_esdras"):
                value = [path] if field == "unchanged_live_inputs" else {path: "0" * 64}
                evidence = {**valid, field: value}
                with self.subTest(field=field, path=path), \
                     patch.object(module, "git", return_value=json.dumps(evidence).encode()):
                    with self.assertRaisesRegex(ValueError, "Letter of Jeremiah dependency path"):
                        module._letter_jeremiah69_70_archive_paths(module.ROOT)


if __name__ == "__main__":
    unittest.main()
