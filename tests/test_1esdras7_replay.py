"""Standalone historical Esdras7 replay guards; synthetic passes are not evidence."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import unittest
from unittest.mock import patch

from tools.textual_restoration import replay_1esdras7_word as module


class Esdras7ReplayTests(unittest.TestCase):
    def run_mocked(self, result=None, *, missing_baseline=False, returncode=0, side_effect=None):
        payload = result or {"passed": True, "tests_run": 6, "skipped": 0, "expected_failures": 0}
        reply = subprocess.CompletedProcess([], returncode, json.dumps(payload), "esdras7 child diagnostic")
        outputs = [module.ESDRAS7_COMMIT.encode(),
                   ("0" * 40 if missing_baseline else module.ESDRAS7_BASE).encode(),
                   b"/private/frozen-history.git", b"archive"]
        with patch.object(module, "git", side_effect=outputs) as git, \
             patch.object(module, "_archive_paths", return_value=["tests"]) as paths, \
             patch.object(module, "extract_regular") as extract, \
             patch.object(module.subprocess, "run", return_value=reply, side_effect=side_effect) as child:
            try:
                actual = module.run_suite()
                return actual, child.call_args, git.call_args_list
            finally:
                if missing_baseline:
                    paths.assert_not_called()
                    child.assert_not_called()
                if extract.called:
                    self.assertFalse(extract.call_args.args[1].exists(), "private tree leaked")

    def test_literal_applied_checkpoint_original_six_tests_and_private_git_context(self):
        self.assertEqual(module.ESDRAS7_COMMIT, "9f4f2198128fa969948b4822cc423dba6f352228")
        self.assertEqual(module.ESDRAS7_BASE, "8ad14030bcedcdc533a74724afcdd672bdbf89ed")
        self.assertNotEqual(module.ESDRAS7_COMMIT, module.ESDRAS7_BASE)
        result, call, calls = self.run_mocked()
        self.assertEqual(result["commit"], module.ESDRAS7_COMMIT)
        self.assertEqual(result["tests_run"], 6)
        self.assertFalse(result["current_corpus_validated"])
        self.assertFalse(result["application_approved"])
        self.assertEqual(call.args[0][:3], [module.sys.executable, "-I", "-c"])
        self.assertEqual(json.loads(call.args[0][-1]), ["test_1esdras7_word_application"])
        self.assertEqual(call.kwargs["timeout"], 600)
        env = call.kwargs["env"]
        self.assertEqual(env["GIT_DIR"], "/private/frozen-history.git")
        self.assertEqual(env["GIT_WORK_TREE"], call.kwargs["cwd"])
        self.assertNotEqual(Path(env["GIT_WORK_TREE"]), module.ROOT)
        self.assertFalse(Path(env["GIT_WORK_TREE"]).exists())
        self.assertEqual(env["GIT_OPTIONAL_LOCKS"], "0")
        self.assertEqual(env["GIT_NO_REPLACE_OBJECTS"], "1")
        for call, commit in zip(calls[:2], (module.ESDRAS7_COMMIT, module.ESDRAS7_BASE)):
            self.assertEqual(call.args[1:], ("rev-parse", "--verify", f"{commit}^{{commit}}"))
        self.assertEqual(calls[-1].args[1:5], ("archive", "--format=tar", module.ESDRAS7_COMMIT, "--"))

    def test_missing_baseline_failure_timeout_and_partial_results_fail(self):
        with self.assertRaisesRegex(ValueError, "baseline resolution mismatch"):
            self.run_mocked(missing_baseline=True)
        with self.assertRaisesRegex(RuntimeError, "esdras7 child diagnostic"):
            self.run_mocked(returncode=1)
        with self.assertRaises(subprocess.TimeoutExpired):
            self.run_mocked(side_effect=subprocess.TimeoutExpired("child", 600))
        valid = {"passed": True, "tests_run": 6, "skipped": 0, "expected_failures": 0}
        for field, value in (("passed", False), ("tests_run", 5), ("tests_run", 7),
                             ("skipped", 1), ("expected_failures", 1)):
            with self.subTest(field=field, value=value), self.assertRaisesRegex(RuntimeError, "coverage mismatch"):
                self.run_mocked({**valid, field: value})

    def test_archive_has_complete_book_all_four_frozen_evidence_sets_and_original_workflow(self):
        paths = module._archive_paths(module.ROOT)
        self.assertEqual(paths, sorted(set(paths)))
        self.assertNotIn("translation/deuterocanon", paths)
        self.assertNotIn("sources/lxx/swete", paths)
        self.assertNotIn("docs", paths)
        evidence = []
        for chapter in (7, 6, 5, 8):
            path = f"sources/textual_restoration/comparisons/1esdras{chapter}_application.2026-10-19.v1.json"
            self.assertIn(path, paths)
            item = json.loads(module.git(module.ROOT, "show", f"{module.ESDRAS7_COMMIT}:{path}"))
            evidence.append(item)
            for field in ("historical_input_pins", "reviewed_file_pins", "unchanged_live_inputs"):
                self.assertTrue(set(item[field]).issubset(paths), (chapter, field))
        for path in ("tools", "translation/deuterocanon/1_esdras", "schema/verse.schema.json",
                     "sources/early_christian_texts/catalog.json",
                     "sources/lxx/swete/final_corpus_adjudicated/WIS.jsonl",
                     "sources/lxx/swete/final_corpus_adjudicated/BAR.jsonl",
                     "sources/lxx/swete/final_corpus_adjudicated/ADA.jsonl"):
            self.assertIn(path, paths)
        archive = module.git(module.ROOT, "archive", "--format=tar", module.ESDRAS7_COMMIT, "--", *paths)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tree:
            self.assertEqual(sum(m.isfile() and m.name.startswith("translation/deuterocanon/1_esdras/")
                                 and m.name.endswith(".yaml") for m in tree.getmembers()), 495)
            for path, pin in evidence[0]["reviewed_file_pins"].items():
                self.assertEqual(hashlib.sha256(tree.extractfile(path).read()).hexdigest(), pin, path)
            self.assertEqual(evidence[0]["baseline_commit"], module.ESDRAS7_BASE)
            proof = "tests/test_1esdras7_word_application.py"
            self.assertEqual(evidence[0]["reviewed_file_pins"][proof],
                             "a96b633ccd84789aedc671566609b34e91286939e8b982a05c8cfb34ef4c2449")
            workflow = ".github/workflows/corpus-integrity.yml"
            raw = tree.extractfile(workflow).read()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),
                             "03ead066041aad1eb380430644a6972312b93816164337bdcce5f1c0d18e95e9")
            self.assertIn(f"git fetch --no-tags --depth=1 origin {module.ESDRAS7_BASE}", raw.decode())
            self.assertIn("python -m unittest discover -s tests -p 'test_1esdras7_word_application.py'", raw.decode())

    def test_changed_baseline_and_unsafe_dependency_paths_fail_closed(self):
        valid = {"baseline_commit": module.ESDRAS7_BASE,
                 "historical_input_pins": {}, "reviewed_file_pins": {}, "unchanged_live_inputs": []}
        replies = [{**valid, "baseline_commit": "0" * 40}, valid, valid, valid]
        with patch.object(module, "git", side_effect=[json.dumps(item).encode() for item in replies]):
            with self.assertRaisesRegex(ValueError, "Esdras7 baseline mismatch"):
                module._archive_paths(module.ROOT)
        for index in range(4):
            for field in ("historical_input_pins", "reviewed_file_pins", "unchanged_live_inputs"):
                for path in ("../outside", "sources/../outside", "sources/[ab]", "/sources/a",
                             "sources/*", "sources/a?", "sources/a:b", "sources/a\\b", "unrelated/a",
                             "translation/deuterocanon/letter_of_jeremiah"):
                    value = [path] if field == "unchanged_live_inputs" else {path: "0" * 64}
                    replies = [valid] * 4
                    replies[index] = {**valid, field: value}
                    with self.subTest(index=index, field=field, path=path), \
                         patch.object(module, "git", side_effect=[json.dumps(item).encode() for item in replies]):
                        with self.assertRaisesRegex(ValueError, "Esdras7 dependency path"):
                            module._archive_paths(module.ROOT)

    def test_single_suite_and_literal_commit_resolution_fail_closed(self):
        with patch.object(module, "git") as git:
            with self.assertRaisesRegex(ValueError, "Unknown historical suite"):
                module.run_suite("unittest.__main__")
            git.assert_not_called()
        with patch.object(module, "git", return_value=b"0" * 40), \
             patch.object(module, "_archive_paths") as paths, \
             patch.object(module.subprocess, "run") as child:
            with self.assertRaisesRegex(ValueError, "commit resolution mismatch"):
                module.run_suite()
            paths.assert_not_called()
            child.assert_not_called()


if __name__ == "__main__":
    unittest.main()
