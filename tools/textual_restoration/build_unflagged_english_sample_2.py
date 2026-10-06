#!/usr/bin/env python3
"""Second predeclared draw; reuse the frozen selector without editing it."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

from tools.textual_restoration import build_unflagged_english_sample as first

ROOT = Path(__file__).resolve().parents[2]
SEED = "POB-unflagged-2026-10-06-v2"
DECLARATION = "docs/UNFLAGGED_ENGLISH_SAMPLE_PREDECLARATION_2026-10-06.md"
RUNNER = "tools/textual_restoration/build_unflagged_english_sample_2.py"
PRIOR = "sources/textual_restoration/samples/unflagged_english_sample.selection.v1.json"


def build(root: Path = ROOT) -> dict:
    # This CLI runs serially; restore the shared module even if selection fails.
    previous_seed = first.SEED
    try:
        first.SEED = SEED
        result = first.build(root)
    finally:
        first.SEED = previous_seed
    result["record_version"] = 2
    result["baseline_revision"] = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    result["protocol_inputs"][DECLARATION] = first.sha((root / DECLARATION).read_bytes())
    result["protocol_inputs"][RUNNER] = first.sha((root / RUNNER).read_bytes())
    prior_raw = (root / PRIOR).read_bytes()
    prior = json.loads(prior_raw)
    previous_paths = {s["selected"]["path"] for s in prior["strata"].values()}
    result["prior_sample"] = {"path": PRIOR, "sha256": first.sha(prior_raw)}
    for row in result["strata"].values():
        row["selected"]["selected_in_first_sample"] = row["selected"]["path"] in previous_paths
    result["limits"] = {
        "project_unseen_held_out": False,
        "blind_english_review": False,
        "manuscript_priority_established": False,
        "application_approved": False,
        "scope": "Three strata, one verse each; new draw over previously model-reviewed POB"
    }
    return result


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False, indent=2))
