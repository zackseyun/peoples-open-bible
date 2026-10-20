"""Replay the five original Letter of Jeremiah 69–70 checks at their applied commit.

No current code or documents are substituted into the private historical tree.
This validates historical reproducibility, never the current corpus or a new edit.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from tools.textual_restoration.replay_historical_tests import ROOT, _CHILD, extract_regular, git

LETTER_JEREMIAH69_70_COMMIT = "a0ae3c29b4525087faa1ceab1ed2822301aa2f37"
LETTER_JEREMIAH69_70_BASE = "b388ce5089ea64ecd3adac354dbd1118c7dbea85"


def _letter_jeremiah69_70_archive_paths(repo):
    """Keep the original five-check correction proof at its applied commit.

    The baseline predates the candidate, test and evidence. Archive their
    reviewed/applied checkpoint, including its original method and workflow;
    the frozen test reads the earlier baseline separately from Git history.
    """
    evidence_path = "sources/textual_restoration/comparisons/letter_jeremiah_69_70.2026-10-19.v1.json"
    evidence = json.loads(git(repo, "show", f"{LETTER_JEREMIAH69_70_COMMIT}:{evidence_path}"))
    if evidence["baseline_commit"] != LETTER_JEREMIAH69_70_BASE:
        raise ValueError("Historical Letter of Jeremiah baseline mismatch")
    paths = {
        "tools", "tests/test_letter_jeremiah_69_70_correction.py",
        "translation/deuterocanon/letter_of_jeremiah",
        "sources/lxx/swete/final_corpus_adjudicated/LJE.jsonl",
        "schema/verse.schema.json", "sources/early_christian_texts/catalog.json",
        ".github/workflows/corpus-integrity.yml", evidence_path,
        *evidence["historical_input_pins"], *evidence["reviewed_file_pins"],
        *evidence["unchanged_live_inputs"],
    }
    for path in paths:
        if (not isinstance(path, str) or Path(path).is_absolute()
                or ".." in Path(path).parts or any(c in path for c in "*?[:\\")
                or not (path == "tools" or path == ".github/workflows/corpus-integrity.yml"
                        or path == "translation/deuterocanon/letter_of_jeremiah"
                        or path.startswith(("tools/", "tests/", "schema/", "sources/", "docs/",
                                            "translation/deuterocanon/letter_of_jeremiah/")))):
            raise ValueError(f"Invalid historical Letter of Jeremiah dependency path: {path}")
    return sorted(paths)


def run_suite(name: str = "letter_jeremiah69_70", *, repo: Path = ROOT):
    """Reject a missing original check, skipped check, failure or wrong count."""
    if name != "letter_jeremiah69_70":
        raise ValueError(f"Unknown historical suite: {name}")
    if sys.flags.optimize:
        raise ValueError("Historical replay requires non-optimized Python")
    commit = LETTER_JEREMIAH69_70_COMMIT
    resolved = git(repo, "rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip()
    if resolved != commit:
        raise ValueError("Historical commit resolution mismatch")
    baseline = git(repo, "rev-parse", "--verify", f"{LETTER_JEREMIAH69_70_BASE}^{{commit}}").decode().strip()
    if baseline != LETTER_JEREMIAH69_70_BASE:
        raise ValueError("Historical Letter of Jeremiah baseline resolution mismatch")
    paths = _letter_jeremiah69_70_archive_paths(repo)
    # The original tests read only their fixed baseline with git show/archive.
    env = dict(os.environ,
               GIT_DIR=git(repo, "rev-parse", "--absolute-git-dir").decode().strip(),
               GIT_OPTIONAL_LOCKS="0", GIT_NO_REPLACE_OBJECTS="1")
    archive = git(repo, "archive", "--format=tar", commit, "--", *paths)
    with tempfile.TemporaryDirectory(prefix="pob-historical-letter-tests-") as directory:
        extract_regular(archive, Path(directory))
        del archive
        env["GIT_WORK_TREE"] = directory
        child = subprocess.run(
            [sys.executable, "-I", "-c", _CHILD, json.dumps(["test_letter_jeremiah_69_70_correction"])],
            cwd=directory, capture_output=True, text=True, timeout=600, env=env,
        )
    if child.returncode:
        raise RuntimeError(f"Historical {name} failed ({child.returncode}):\n{child.stderr}\n{child.stdout}")
    try:
        result = json.loads(child.stdout)
    except (ValueError, TypeError) as exc:
        raise RuntimeError("Historical child did not return its test result") from exc
    if (result.get("passed") is not True or result.get("tests_run") != 5
            or result.get("skipped") != 0 or result.get("expected_failures") != 0):
        raise RuntimeError(f"Historical test coverage mismatch: {result}")
    return {**result, "suite": name, "commit": commit,
            "current_corpus_validated": False, "application_approved": False}


if __name__ == "__main__":
    import argparse
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(json.dumps(run_suite(), indent=2))
