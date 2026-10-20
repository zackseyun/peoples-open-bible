"""Standalone historical Letter replay guards; synthetic passes are not research evidence."""
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from tools.textual_restoration import replay_letter_jeremiah69_70 as module


class LetterJeremiahReplayTests(unittest.TestCase):
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


    def test_single_suite_and_literal_commit_resolution_fail_closed(self):
        with patch.object(module, "git") as git:
            with self.assertRaisesRegex(ValueError, "Unknown historical suite"):
                module.run_suite("unittest.__main__")
            git.assert_not_called()
        with patch.object(module, "git", return_value=b"0" * 40), \
             patch.object(module, "_letter_jeremiah69_70_archive_paths") as paths, \
             patch.object(module.subprocess, "run") as child:
            with self.assertRaisesRegex(ValueError, "commit resolution mismatch"):
                module.run_suite()
            paths.assert_not_called()
            child.assert_not_called()


if __name__ == "__main__":
    unittest.main()
