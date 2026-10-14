"""Consolidate actual current-source Homilies reviews, never publish or invent approval.

Each response bundle is validated against the complete checked source first.
Selections remain subject to the existing collector's later-adverse-review gate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.extra_texts import pseudo_clementine_acceptance as acceptance
from tools.extra_texts import pseudo_clementine_pages as pages
from tools.extra_texts import pseudo_clementine_translation as translation
from tools.extra_texts.pseudo_clementine_selected import load_selected

WORK = "pseudo_clementine_homilies"


def choose_selections(candidates: list[dict], references: list[str]) -> list[dict]:
    """Choose only validated acceptances, not an older favorable identical text.

    This function supplies no approval itself. Its caller must validate every
    bundle before selection and run acceptance.collect afterwards.
    """
    chosen, adverse = {}, set()
    for candidate in sorted(candidates, key=lambda c: c["review"]["recorded_at"], reverse=True):
        draft = {r["reference"]: r for r in candidate["draft"]["output"]["passages"]}
        for reviewed in candidate["review"]["output"]["passages"]:
            ref = reviewed["reference"]
            row = draft[ref]
            key = (ref, row["text"])
            if not acceptance.accepted_passage(reviewed) or any(i["blocks_publication"] for i in row["source_issues"]):
                adverse.add(key)
                continue
            if ref in references and ref not in chosen and key not in adverse:
                chosen[ref] = (candidate["draft_path"], candidate["review_path"])
    selections = []
    for ref in references:
        if ref not in chosen:
            continue
        draft_path, review_path = chosen[ref]
        if selections and (selections[-1]["draft"], selections[-1]["review"]) == (draft_path, review_path):
            selections[-1]["references"].append(ref)
        else:
            selections.append({"references": [ref], "draft": draft_path, "review": review_path})
    return selections


def consolidate(*, complete: bool = False) -> dict:
    source = load_selected(WORK)  # Missing pages or stale source snapshots fail closed.
    workflow = translation.source.SOURCE_ROOT / WORK / "translation_workflow"
    draft_index = {}
    for path in workflow.rglob("*.draft.record.json"):
        record = json.loads(path.read_text())
        draft_index.setdefault(record["output_hash"], []).append(path)
    candidates, rejected = [], []
    for review_path in workflow.rglob("*.review.record.json"):
        review = json.loads(review_path.read_text())
        matched = False
        for draft_path in draft_index.get(review.get("draft_output_hash"), []):
            draft_relative = str(draft_path.relative_to(translation.source.ROOT))
            review_relative = str(review_path.relative_to(translation.source.ROOT))
            try:
                draft, checked_review = acceptance.validate_bundle(WORK, source["passages"], draft_relative, review_relative)
            except (ValueError, KeyError, FileNotFoundError) as exc:
                rejected.append({"draft": draft_relative, "review": review_relative, "reason": str(exc)})
                continue
            candidates.append({"draft": draft, "review": checked_review,
                               "draft_path": draft_relative, "review_path": review_relative})
            matched = True
            break
        if not matched and review.get("draft_output_hash") not in draft_index:
            rejected.append({"review": str(review_path.relative_to(translation.source.ROOT)), "reason": "No matching draft record"})
    references = [row["reference"] for row in source["passages"]]
    selections = choose_selections(candidates, references)
    # Rechecks actual responses, all hash bindings, source issues and every
    # later adverse record. No fabricated acceptance can enter the output.
    result = acceptance.collect(WORK, selections, complete=complete)
    result["consolidation"] = {"validated_bundles": len(candidates), "ineligible_evidence": rejected}
    stem = "accepted-complete" if complete else "accepted-partial"
    pages.save(workflow / (stem + ".selections.json"), selections)
    pages.save(workflow / (stem + ".json"), result)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--complete", action="store_true", help="Require every source section; never allow a partial-work approval")
    args = parser.parse_args()
    result = consolidate(complete=args.complete)
    print(json.dumps({"work": WORK, "accepted_sections": len(result["passages"]),
                      "expected_sections": len(result["expected_references"]),
                      "missing_references": result["missing_references"],
                      "publication_status": "not_published"}, indent=2))
