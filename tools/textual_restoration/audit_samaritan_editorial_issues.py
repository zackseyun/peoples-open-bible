#!/usr/bin/env python3
"""Reference-level audit of pinned SP issue annotations; not a diplomatic text."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from tools.textual_restoration import build_samaritan_screen as S

ROOT = S.ROOT
OUT = ROOT / "sources/textual_restoration/discovery/samaritan_editorial_audit.2026-10-10.v1.json"
ISSUES_SHA = "b6ad6cf611fa065986d177674902136db30c145f210b17f21a34088641b7c47a"
SCREEN_PATH = "sources/textual_restoration/discovery/samaritan_wlc_screen.v1.json"
SCREEN_SHA = "1ae6bb318ed9304e3e853322a8012023c4863fee7656cbb9fd874521540e9d8a"
PARALLEL_PATH = "sources/textual_restoration/discovery/samaritan_parallel_blocks.v1.json"
PARALLEL_SHA = "e9b4f42664bf0ff5a37ddeb5e0ce18ec2924f4cb194e0bb1a5a9e903789c0068"


def pinned_json(path: Path, expected: str) -> dict:
    raw = path.read_bytes()
    if S.sha(raw) != expected:
        raise ValueError(f"{path.name}: pinned hash mismatch")
    return json.loads(raw)


def issue_rows(issues: dict) -> list[dict]:
    rows = []
    if not issues:
        raise ValueError("empty issue inventory")
    for key, item in sorted(issues.items(), key=lambda pair: int(pair[0])):
        if set(item) != {"data_version", "tf_node", "section", "explanation"}:
            raise ValueError("issue fields changed")
        section = item["section"]
        if (not isinstance(section, list) or len(section) != 3
                or section[0] not in S.BOOKS
                or any(type(n) is not int or n < 1 for n in section[1:])
                or type(item["tf_node"]) is not int or item["tf_node"] < 1
                or not isinstance(item["data_version"], str)
                or not isinstance(item["explanation"], str)):
            raise ValueError("invalid issue locator")
        explanation = item["explanation"]
        if "harmonized" not in explanation:
            category = "other-analysis-or-reading-concern"
        elif "MT" in explanation:
            category = "reported-harmonization-to-mt"
        elif "core SP tradition" in explanation:
            category = "reported-harmonization-to-core-sp"
        else:
            raise ValueError("unrecognized harmonization target")
        rows.append({"issue_id": key,
                     "annotation_data_version": item["data_version"],
                     "annotation_tf_node": item["tf_node"],
                     "reference_label": f"{S.BOOKS[section[0]]}.{section[1]}.{section[2]}",
                     "category": category})
    return rows


def reference_pools(screen: dict, parallel: dict) -> dict[str, set[str]]:
    pools = {
        "large_length_targets": {r["reference_label"] for r in screen["largest_length_difference_leads"]},
        "numbering_or_repetition_targets": {r["reference_label"] for r in screen["numbering_or_repetition_review"]},
        "numbering_or_repetition_wlc_candidates": {
            ref for row in screen["numbering_or_repetition_review"]
            for ref in row["other_exact_wlc_reference_candidates"]},
        "parallel_targets": {n["sp_reference"] for n in parallel["nodes"]},
        "parallel_sp_alternatives": set(), "parallel_wlc_alternatives": set(),
    }
    for node in parallel["nodes"]:
        for span in node["candidate_spans"]:
            for alternative in span["parallel_reference_candidates"]:
                control = alternative["control"]
                if control not in {"SP", "WLC"}:
                    raise ValueError("unknown parallel control")
                pools[f"parallel_{control.lower()}_alternatives"].add(alternative["reference_label"])
    return pools


def audit(issues: dict, sp: dict, wlc: dict, screen: dict, parallel: dict) -> dict:
    rows = issue_rows(issues)
    refs = {row["reference_label"] for row in rows}
    if not refs <= (sp.keys() & wlc.keys()):
        raise ValueError("annotation section absent from current controls")
    pools = reference_pools(screen, parallel)
    units = []
    for ref in sorted(refs, key=S.ref_key):
        units.append({
            "reference_label": ref,
            "issue_ids": [r["issue_id"] for r in rows if r["reference_label"] == ref],
            "current_sp_sign_text_sha256": S.sha(sp[ref].encode()),
            "current_wlc_written_text_sha256": S.sha(wlc[ref].encode()),
            "same_label_consonantal_comparison": "equal" if S.consonants(sp[ref]) == S.consonants(wlc[ref]) else "different",
        })
    return {
        "summary": {"issue_annotations": len(rows), "unique_reference_sections": len(refs),
                    "annotation_versions": dict(sorted(Counter(r["annotation_data_version"] for r in rows).items())),
                    "annotation_categories": dict(sorted(Counter(r["category"] for r in rows).items())),
                    "current_section_comparisons": dict(sorted(Counter(u["same_label_consonantal_comparison"] for u in units).items()))},
        "annotations": rows, "current_sections": units,
        "lead_intersections": [
            {"pool": name, "distinct_reference_labels": len(pool),
             "annotated_reference_labels": sorted(pool & refs, key=S.ref_key)}
            for name, pool in pools.items()],
    }


def build(sp_directory: Path, issues_path: Path, root: Path = ROOT) -> dict:
    issues = pinned_json(issues_path, ISSUES_SHA)
    frozen = pinned_json(root / SCREEN_PATH, SCREEN_SHA)
    parallel = pinned_json(root / PARALLEL_PATH, PARALLEL_SHA)
    # Reproduce the entire frozen discovery screen, not just its lead counts.
    if S.build(sp_directory, root) != frozen:
        raise ValueError("frozen whole-Torah screen not reproduced")
    sp, sp_inputs = S.load_sp(sp_directory)
    wlc, wlc_inputs = S.load_wlc(root / "sources/ot/wlc")
    return {
        "schema_version": "1.0.0", "checked_date": "2026-10-10",
        "scope": "All annotations in one pinned issues.json mapped by section to current SP7.1.3/WLC and existing frozen lead reference pools; not a manuscript census or token-level edit audit",
        "source": {"commit": S.COMMIT, "version": S.VERSION,
                   "url": f"https://github.com/DT-UCPH/sp/tree/{S.COMMIT}",
                   "issues_url": f"https://raw.githubusercontent.com/DT-UCPH/sp/{S.COMMIT}/textual_issues/issues.json",
                   "issues_sha256": ISSUES_SHA,
                   "attribution": "Højgaard, Naaijer and Schorch (2023), Text-Fabric Dataset of the Samaritan Pentateuch; Naaijer, Højgaard, Schorch and Ehrensvärd (2024), dataset paper",
                   "rights": "CC BY-NC 4.0; private input retained outside POB; only metadata and derived audit exported",
                   "sp_inputs": sp_inputs, "wlc_inputs": wlc_inputs,
                   "frozen_screen": {"repo_path": SCREEN_PATH, "sha256": SCREEN_SHA, "reproduced": True},
                   "frozen_parallel": {"repo_path": PARALLEL_PATH, "sha256": PARALLEL_SHA}},
        "mapping": "Issue IDs, annotation data versions and historical node numbers are retained as upstream locators. Only the declared book/chapter/verse section is mapped. Node numbers are not promoted to stable token identities in7.1.3. Parallel pools count distinct labels, not occurrences or independent witnesses.",
        "limitations": "A reported harmonization annotation does not establish which feature layer was altered, whether current sign.tf was altered, the unedited manuscript spelling, or the number of raw text edits. Whole-verse difference from WLC cannot answer these questions. No overlap means only no matching section in this issue list; the list is not certified complete. Word division, pointing and linguistic analyses are outside the consonantal screen.",
        "policy": {"unannotated_section_is_diplomatic": False,
                   "harmonization_annotation_proves_sign_edit": False,
                   "raw_sign_changes_verified": False,
                   "historical_nodes_remapped": False,
                   "manuscript_text_reconstructed": False,
                   "historical_selection_applied": False,
                   "canonical_change_applied": False,
                   "generated_images_used": False,
                   "export_contains_source_text": False},
        **audit(issues, sp, wlc, frozen, parallel),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sp_tf_directory", type=Path)
    parser.add_argument("issues_json", type=Path)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    result = build(args.sp_tf_directory, args.issues_json)
    if args.verify_only:
        if json.loads(OUT.read_text()) != result:
            raise SystemExit("Saved editorial audit differs from recomputation")
        print("Verified editorial audit from pinned private inputs and frozen leads")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
