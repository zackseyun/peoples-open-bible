"""Collect explicit per-section model acceptance without inventing whole-book approval."""
from __future__ import annotations
import json
from pathlib import Path

from tools.extra_texts import pseudo_clementine_translation as tr
from tools.extra_texts.pseudo_clementine_selected import load_selected

CHECKS = tr.CHECKS


def accepted_passage(row: dict) -> bool:
    return (row.get("verdict") == "accept"
            and all(row.get("checks", {}).get(key) is True for key in CHECKS)
            and not any(item.get("severity") in {"blocking", "major"} for item in row.get("findings", [])))


def safe_path(relative: str) -> Path:
    path = (tr.source.ROOT / relative).resolve()
    path.relative_to(tr.source.ROOT.resolve())
    if not path.is_file():
        raise ValueError("Acceptance evidence file is missing")
    return path


def validate_bundle(work: str, source_rows: list[dict], draft_path: str, review_path: str) -> tuple[dict, dict]:
    draft = json.loads(safe_path(draft_path).read_text())
    review = json.loads(safe_path(review_path).read_text())
    if draft["work"] != work or review["work"] != work:
        raise ValueError("Acceptance work identity mismatch")
    if draft.get("stage") != "draft" or review.get("stage") != "review" or review.get("review_kind") != "automated_model_comparison_not_human_scholarly_signoff":
        raise ValueError("Acceptance review scope changed")
    refs = draft["references"]
    if not refs or len(set(refs)) != len(refs) or review["references"] != refs:
        raise ValueError("Acceptance batch references changed")
    expected = [row for row in source_rows if row["reference"] in refs]
    if [row["reference"] for row in expected] != refs:
        raise ValueError("Acceptance batch source order changed")
    if draft["source_hash"] != tr.digest(expected) or review["source_hash"] != tr.digest(expected):
        raise ValueError("Acceptance source is stale")
    if draft["output_hash"] != tr.digest(draft["output"]) or review["draft_output_hash"] != draft["output_hash"]:
        raise ValueError("Accepted English changed")
    if review["output_hash"] != tr.digest(review["output"]):
        raise ValueError("Review output changed")
    if [row["reference"] for row in draft["output"]["passages"]] != refs or [row["reference"] for row in review["output"]["passages"]] != refs:
        raise ValueError("Batch response coverage changed")
    files = review["evidence_files"]
    request = json.loads(safe_path(files["request"]).read_text())
    response = json.loads(safe_path(files["response"]).read_text())
    if request["context"]["passages"] != expected or request["context"]["draft"] != draft["output"]:
        raise ValueError("Reviewer did not receive the selected Greek and English")
    if request["request_hash"] != tr.digest(request["params"]) or review["request_hash"] != request["request_hash"]:
        raise ValueError("Review request changed")
    actual = tr.validate_response(request, response)
    if (actual["output_hash"] != review["output_hash"]
            or actual["response_hash"] != review["response_hash"]
            or actual["model"] != review["model"]
            or not actual["model"].startswith("gpt-6.1-sol-")):
        raise ValueError("Acceptance is not bound to the actual requested model response")
    return draft, review


def collect(work: str, selections: list[dict], *, complete: bool = True) -> dict:
    source = load_selected(work)
    source_rows = source["passages"]
    expected = [row["reference"] for row in source_rows]
    chosen = {}
    workflow = tr.source.SOURCE_ROOT / work / "translation_workflow"
    review_files = list(workflow.rglob("*.review.record.json"))
    for selection in selections:
        draft, review = validate_bundle(work, source_rows, selection["draft"], selection["review"])
        drafts = {row["reference"]: row for row in draft["output"]["passages"]}
        reviews = {row["reference"]: row for row in review["output"]["passages"]}
        for ref in selection["references"]:
            if ref in chosen or ref not in drafts:
                raise ValueError("Duplicate or invented selected section")
            if not accepted_passage(reviews[ref]):
                raise ValueError("Selected section has not passed independent review")
            row = drafts[ref]
            if any(issue["blocks_publication"] for issue in row["source_issues"]):
                raise ValueError("Selected section has an unresolved source issue")
            # Do not select an older favorable verdict over a later adverse one.
            # Metadata-only edits do not erase a later concern about identical text.
            for later_path in review_files:
                later = json.loads(later_path.read_text())
                if later.get("recorded_at", "") <= review["recorded_at"]:
                    continue
                findings = [p for p in later["output"]["passages"] if p["reference"] == ref and not accepted_passage(p)]
                if not findings:
                    continue
                files = later.get("evidence_files")
                if not files:
                    raise ValueError("Later adverse finding lacks evidence and requires inspection")
                packet = json.loads(safe_path(files["request"]).read_text())
                later_rows = [p for p in packet["context"]["draft"]["passages"] if p["reference"] == ref]
                if later_rows and later_rows[0]["text"] == row["text"]:
                    raise ValueError("Later unresolved review finding must be reconciled")
            chosen[ref] = {
                "reference": ref, "text": row["text"], "source_issues": row["source_issues"],
                "lexical_decisions": row["lexical_decisions"],
                "draft_passage_hash": tr.digest(row), "review_passage_hash": tr.digest(reviews[ref]),
                "draft_record": selection["draft"], "review_record": selection["review"],
                "source_text_sha256": next(p["source_text_sha256"] for p in source_rows if p["reference"] == ref),
            }
    missing = [ref for ref in expected if ref not in chosen]
    if complete and missing:
        raise ValueError("Complete work still lacks accepted sections: " + ", ".join(missing))
    return {"work": work, "source_hash": tr.digest(source_rows),
            "status": "complete_model_checked_candidate" if not missing else "partial_model_checked_candidate",
            "publication_status": "not_published", "review_kind": "automated_model_comparison_not_human_scholarly_signoff",
            "expected_references": expected, "missing_references": missing,
            "passages": [chosen[ref] for ref in expected if ref in chosen]}
