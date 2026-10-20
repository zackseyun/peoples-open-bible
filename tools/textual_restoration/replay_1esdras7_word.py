"""Replay the six original 1 Esdras 7 word-repair checks at their applied commit.

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

ESDRAS7_COMMIT = "9f4f2198128fa969948b4822cc423dba6f352228"
ESDRAS7_BASE = "8ad14030bcedcdc533a74724afcdd672bdbf89ed"


def _archive_paths(repo):
    """Keep original chapter7 proof and every chapter5/6/8 pinned dependency.

    All files come from one applied checkpoint. Its original code reads the
    earlier baseline separately from Git history; current files never enter
    the extracted tree, including its original workflow and shared runner.
    """
    prefix = "sources/textual_restoration/comparisons/"
    evidence_paths = [prefix + f"1esdras{chapter}_application.2026-10-19.v1.json"
                      for chapter in (7, 6, 5, 8)]
    evidence = [json.loads(git(repo, "show", f"{ESDRAS7_COMMIT}:{path}"))
                for path in evidence_paths]
    if evidence[0]["baseline_commit"] != ESDRAS7_BASE:
        raise ValueError("Historical Esdras7 baseline mismatch")
    paths = {
        "tools", "tests/test_1esdras7_word_application.py",
        "translation/deuterocanon/1_esdras", "schema/verse.schema.json",
        "sources/early_christian_texts/catalog.json",
        ".github/workflows/corpus-integrity.yml", *evidence_paths,
        # The original scoped-generator check also evaluates these raw counts.
        "sources/lxx/swete/final_corpus_adjudicated/WIS.jsonl",
        "sources/lxx/swete/final_corpus_adjudicated/BAR.jsonl",
        "sources/lxx/swete/final_corpus_adjudicated/ADA.jsonl",
    }
    for item in evidence:
        paths.update(item["historical_input_pins"])
        paths.update(item["reviewed_file_pins"])
        paths.update(item["unchanged_live_inputs"])
    for path in paths:
        if (not isinstance(path, str) or Path(path).is_absolute()
                or ".." in Path(path).parts or any(c in path for c in "*?[:\\")
                or not (path == "tools" or path == ".github/workflows/corpus-integrity.yml"
                        or path == "translation/deuterocanon/1_esdras"
                        or path.startswith(("tools/", "tests/", "schema/", "sources/", "docs/",
                                            "translation/deuterocanon/1_esdras/")))):
            raise ValueError(f"Invalid historical Esdras7 dependency path: {path}")
    return sorted(paths)


def run_suite(name: str = "esdras7_word", *, repo: Path = ROOT):
    """Reject a missing original check, skipped check, failure or wrong count."""
    if name != "esdras7_word":
        raise ValueError(f"Unknown historical suite: {name}")
    if sys.flags.optimize:
        raise ValueError("Historical replay requires non-optimized Python")
    commit = ESDRAS7_COMMIT
    resolved = git(repo, "rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip()
    if resolved != commit:
        raise ValueError("Historical commit resolution mismatch")
    baseline = git(repo, "rev-parse", "--verify", f"{ESDRAS7_BASE}^{{commit}}").decode().strip()
    if baseline != ESDRAS7_BASE:
        raise ValueError("Historical Esdras7 baseline resolution mismatch")
    paths = _archive_paths(repo)
    env = dict(os.environ,
               GIT_DIR=git(repo, "rev-parse", "--absolute-git-dir").decode().strip(),
               GIT_OPTIONAL_LOCKS="0", GIT_NO_REPLACE_OBJECTS="1")
    archive = git(repo, "archive", "--format=tar", commit, "--", *paths)
    with tempfile.TemporaryDirectory(prefix="pob-historical-esdras7-tests-") as directory:
        extract_regular(archive, Path(directory))
        del archive
        env["GIT_WORK_TREE"] = directory
        child = subprocess.run(
            [sys.executable, "-I", "-c", _CHILD, json.dumps(["test_1esdras7_word_application"])],
            cwd=directory, capture_output=True, text=True, timeout=600, env=env,
        )
    if child.returncode:
        raise RuntimeError(f"Historical {name} failed ({child.returncode}):\n{child.stderr}\n{child.stdout}")
    try:
        result = json.loads(child.stdout)
    except (ValueError, TypeError) as exc:
        raise RuntimeError("Historical child did not return its test result") from exc
    if (result.get("passed") is not True or result.get("tests_run") != 6
            or result.get("skipped") != 0 or result.get("expected_failures") != 0):
        raise RuntimeError(f"Historical test coverage mismatch: {result}")
    return {**result, "suite": name, "commit": commit,
            "current_corpus_validated": False, "application_approved": False}


if __name__ == "__main__":
    import argparse
    argparse.ArgumentParser(description=__doc__).parse_args()
    print(json.dumps(run_suite(), indent=2))
