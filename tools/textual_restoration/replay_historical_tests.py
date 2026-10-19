"""Run receipt-bound historical tests against one trusted immutable Git snapshot.

Never validates or authorizes the current corpus. No current code is substituted
into the snapshot; current behavior needs separate tests. Requires local Git
history, Python's current installed dependencies, and temporary disk space.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from tools.textual_restoration.replay_unflagged_sample import extract_regular, git

ROOT = Path(__file__).resolve().parents[2]
COMMIT = "7637f998fd1edd9f7ab1acabf1e3037f2024b7e7"
ESDRAS8_COMMIT = "756074bd3e0bd97c5d849c5ff47125972f4684b2"
ESDRAS8_BASE = "97194d2b4c691514373896490110246b0b024219"
_REGISTRY = "test_ot_witness_registry.OtWitnessRegistryTests."
SUITES = {
    "esdras8_partition": (["test_1esdras8_partition_application"], 6),
    "genesis": (["test_genesis_note_transaction"], 28),
    "unflagged": (["test_unflagged_english_sample"], 4),
    "registry_genesis": ([_REGISTRY + name for name in (
        "test_historical_pentateuch_comparison_with_named_genesis_baseline_view",
        "test_live_pentateuch_snapshot_reports_applied_genesis_note_drift",
        "test_historical_comparison_rejects_unknown_genesis_canonical_bytes",
        "test_historical_comparison_does_not_hide_unrelated_canonical_drift",
        "test_historical_control_comparison_detects_specific_mutated_baseline_hash",
    )], 5),
    "registry_samuel_psalms": ([_REGISTRY + name for name in (
        "test_current_registry_coverage_and_selections",
        "test_psalms_case_and_coverage_validate",
    )], 2),
}


def _esdras8_archive_paths(repo):
    """Keep the six original checks and every input at their applied checkpoint.

    Their whole-book assertions intentionally describe the pre-chapter-5-repair
    state. Never repin those historical assertions to authorize a successor.
    """
    evidence_path = "sources/textual_restoration/comparisons/1esdras8_application.2026-10-19.v1.json"
    evidence = json.loads(git(repo, "show", f"{ESDRAS8_COMMIT}:{evidence_path}"))
    if evidence["baseline_commit"] != ESDRAS8_BASE:
        raise ValueError("Historical Esdras baseline mismatch")
    paths = {
        "tools", "tests/test_1esdras8_partition_application.py",
        "translation/deuterocanon/1_esdras", "schema/verse.schema.json",
        "sources/early_christian_texts/catalog.json",
        ".github/workflows/corpus-integrity.yml", evidence_path,
        # The frozen scoped-generator check also evaluates these raw counts.
        "sources/lxx/swete/final_corpus_adjudicated/WIS.jsonl",
        "sources/lxx/swete/final_corpus_adjudicated/BAR.jsonl",
        "sources/lxx/swete/final_corpus_adjudicated/ADA.jsonl",
        *evidence["reviewed_file_pins"], *evidence["unchanged_live_inputs"],
    }
    for path in paths:
        if (not isinstance(path, str) or Path(path).is_absolute()
                or ".." in Path(path).parts or any(c in path for c in "*?[:\\")
                or not (path == "tools" or path == ".github/workflows/corpus-integrity.yml"
                        or path == "translation/deuterocanon/1_esdras"
                        or path.startswith(("tools/", "tests/", "schema/", "sources/", "docs/")))):
            raise ValueError(f"Invalid historical Esdras dependency path: {path}")
    return sorted(paths)
ARCHIVE_ROOTS = (
    "tools", "tests", "docs", "schema", "schemas", "translation/ot",
    "sources/ot", "sources/nt", "sources/lxx/swete",
    "sources/textual_restoration", "sources/dead_sea_scrolls",
    "sources/early_christian_texts/catalog.json",
    "METHODOLOGY.md", "REVISION_METHODOLOGY.md", "DOCTRINE.md",
)
_CHILD = """
import json, pathlib, sys, unittest
root = pathlib.Path.cwd()
sys.path[:0] = [str(root / 'tests'), str(root)]
suite = unittest.defaultTestLoader.loadTestsFromNames(json.loads(sys.argv[1]))
result = unittest.TextTestRunner(stream=sys.stderr, verbosity=1).run(suite)
print(json.dumps({'passed': result.wasSuccessful(), 'tests_run': result.testsRun,
                  'skipped': len(result.skipped),
                  'expected_failures': len(result.expectedFailures)}))
sys.exit(0 if result.wasSuccessful() else 1)
"""


def _archive_paths(repo):
    """Include exact derivative pins from the committed manifest, not live data."""
    rel = "sources/textual_restoration/applications/genesis4_8_newtransaction_inputs.v1.json"
    inputs = json.loads(git(repo, "show", f"{COMMIT}:{rel}"))
    extra = inputs["unchanged_derivative_context_pins"]
    # These are data only; refuse pathspec syntax, traversal and arbitrary roots.
    for path in extra:
        parts = Path(path).parts
        if (not path.startswith("translation_") or Path(path).is_absolute()
                or ".." in parts or any(c in path for c in "*?[:\\")):
            raise ValueError(f"Invalid historical derivative path: {path}")
    return [*ARCHIVE_ROOTS, *sorted(extra)]


def _registry_controls_archive_paths(repo):
    """Exact original assertions and their inputs, not a whole-corpus archive.

    The Samuel receipt subsequently gained evidence metadata. This replay uses
    its original immutable version, not current receipts or current code.
    """
    prefix = "sources/textual_restoration/"
    comparisons = ("pentateuch_controls", "samuel_controls", "psalms_controls")
    paths = ["tools", "tests/test_ot_witness_registry.py",
             "sources/ot/wlc", "sources/ot/uwhb", "sources/lxx/swete",
             "sources/early_christian_texts/catalog.json"]
    paths += [prefix + "ot_witness_registry.v1.json",
              prefix + "selections/ot_critical_source_pilot.v1.json",
              prefix + "decisions/hebrew_pilot.v1.json"]
    paths += [prefix + "coverage/" + name + "_pilot.v1.json"
              for name in ("pentateuch", "samuel", "psalms")]
    targets = set()
    checked = 0
    for name in comparisons:
        rel = prefix + "comparisons/" + name + ".v1.json"
        paths.append(rel)
        data = json.loads(git(repo, "show", f"{COMMIT}:{rel}"))
        for case in data["cases"]:
            baseline = case["baseline"]
            target = baseline["repo_path"]
            if (not target.startswith("translation/ot/")
                    or ".." in Path(target).parts
                    or any(c in target for c in "*?[:\\")):
                raise ValueError("Invalid historical control baseline path")
            targets.add(target)
            if name != "pentateuch_controls":
                raw = git(repo, "show", f"{COMMIT}:{target}")
                if hashlib.sha256(raw).hexdigest() != baseline["sha256"]:
                    raise ValueError(f"Historical control baseline drift: {case['id']}")
                checked += 1
    if checked != 6:
        raise ValueError("Historical Samuel/Psalms baseline coverage mismatch")
    return [*paths, *sorted(targets)]


def _registry_genesis_archive_paths(repo):
    """Dependency-complete archive for the five original Genesis controls.

    Only the parent archive selection changes. Child code, original assertions,
    and every input still come from COMMIT; no current records are substituted.
    These tests do not need a full-Genesis export or whole-corpus extraction.
    """
    prefix = "sources/textual_restoration/"

    def read_json(path):
        return json.loads(git(repo, "show", f"{COMMIT}:{path}"))

    inputs = read_json(prefix + "applications/genesis4_8_newtransaction_inputs.v1.json")
    preflight = read_json(prefix + "applications/genesis_4_8_note_preflight.v1.json")
    paths = {
        "tools", "tests/test_ot_witness_registry.py",
        "sources/early_christian_texts/catalog.json",
        "tests/test_genesis_note_transaction.py",
        "tests/test_unflagged_english_sample.py",
        "docs/GENESIS_4_8_NOTE_APPLICATION_2026-09-06.md",
        "METHODOLOGY.md", "REVISION_METHODOLOGY.md",
    }
    paths.update(preflight["input_pins"])
    paths.update(inputs["prior_package_input_pins"])
    paths.update(inputs["unchanged_derivative_context_pins"])
    paths.update(prefix + "applications/" + name for name in (
        "genesis_4_8_note_baseline.v1.yaml",
        "genesis_4_8_note_candidate.v1.yaml",
        "genesis_4_8_note_preflight.v1.json",
        "genesis_4_8_note_judgment.v1.json",
        "genesis4_8_newtransaction_inputs.v1.json",
        "genesis4_8_newtransaction_review.v1.json",
        "genesis4_8_newtransaction_intent.v1.json",
        "genesis_4_8_note_application.v1.json",
        "genesis4_8_newtransaction_test_migration.v1.json",
    ))
    paths.update(prefix + path for path in (
        "ot_witness_registry.v1.json",
        "coverage/pentateuch_pilot.v1.json",
        "coverage/samuel_pilot.v1.json",
        "comparisons/pentateuch_controls.v1.json",
        "comparisons/samuel_controls.v1.json",
        "selections/ot_critical_source_pilot.v1.json",
        "decisions/hebrew_pilot.v1.json",
    ))
    comparison = read_json(prefix + "comparisons/pentateuch_controls.v1.json")
    paths.update(case["baseline"]["repo_path"] for case in comparison["cases"])
    paths.update(("translation/ot/numbers/022/019.yaml",
                  "translation/ot/jeremiah/010/010.yaml"))
    allowed = ("tools/", "tests/", "docs/", "schema/", "schemas/",
               "sources/", "translation/ot/", "translation_")
    for path in paths:
        if (not isinstance(path, str) or Path(path).is_absolute()
                or ".." in Path(path).parts or any(c in path for c in "*?[:\\")
                or not (path == "tools" or path in ("METHODOLOGY.md", "REVISION_METHODOLOGY.md", "DOCTRINE.md")
                        or path.startswith(allowed))):
            raise ValueError(f"Invalid historical Genesis dependency path: {path}")
    return sorted(paths)

def run_suite(name: str, *, repo: Path = ROOT):
    """A nonzero child, missing test, skipped check or wrong count is a failure."""
    if name not in SUITES:
        raise ValueError(f"Unknown historical suite: {name}")
    if sys.flags.optimize:
        raise ValueError("Historical replay requires non-optimized Python")
    commit = ESDRAS8_COMMIT if name == "esdras8_partition" else COMMIT
    resolved = git(repo, "rev-parse", "--verify", f"{commit}^{{commit}}").decode().strip()
    if resolved != commit:
        raise ValueError("Historical commit resolution mismatch")
    names, count = SUITES[name]
    child_options = {}
    if name == "esdras8_partition":
        baseline = git(repo, "rev-parse", "--verify", f"{ESDRAS8_BASE}^{{commit}}").decode().strip()
        if baseline != ESDRAS8_BASE:
            raise ValueError("Historical Esdras baseline resolution mismatch")
        paths = _esdras8_archive_paths(repo)
        # Frozen tests issue only read-only `git show` and `git archive` calls.
        # Resolve their original BASE from local history, not a current checkout.
        child_options["env"] = dict(
            os.environ, GIT_DIR=git(repo, "rev-parse", "--absolute-git-dir").decode().strip(),
            GIT_OPTIONAL_LOCKS="0", GIT_NO_REPLACE_OBJECTS="1",
        )
    elif name == "registry_samuel_psalms":
        paths = _registry_controls_archive_paths(repo)
    elif name == "registry_genesis":
        paths = _registry_genesis_archive_paths(repo)
    else:
        paths = _archive_paths(repo)
    archive = git(repo, "archive", "--format=tar", commit, "--", *paths)
    with tempfile.TemporaryDirectory(prefix="pob-historical-tests-") as directory:
        extract_regular(archive, Path(directory))
        del archive
        if name == "esdras8_partition":
            child_options["env"]["GIT_WORK_TREE"] = directory
        child = subprocess.run(
            [sys.executable, "-I", "-c", _CHILD, json.dumps(names)],
            cwd=directory, capture_output=True, text=True, timeout=600, **child_options,
        )
    if child.returncode:
        raise RuntimeError(f"Historical {name} failed ({child.returncode}):\n{child.stderr}\n{child.stdout}")
    try:
        result = json.loads(child.stdout)
    except (ValueError, TypeError) as exc:
        raise RuntimeError("Historical child did not return its test result") from exc
    if (result.get("passed") is not True or result.get("tests_run") != count
            or result.get("skipped") != 0 or result.get("expected_failures") != 0):
        raise RuntimeError(f"Historical test coverage mismatch: {result}")
    return {**result, "suite": name, "commit": commit,
            "current_corpus_validated": False, "application_approved": False}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", choices=tuple(SUITES))
    print(json.dumps(run_suite(parser.parse_args().suite), indent=2))
