"""Bounded, passage-focused follow-up of actual adverse Homilies reviews.

Never changes Greek, acceptance flags or old receipts. Provider-filtered
references are excluded, not retried or routed to another model.
"""
from __future__ import annotations

import argparse
import fcntl
import json
from pathlib import Path

from tools.extra_texts import pseudo_clementine_acceptance as acceptance
from tools.extra_texts import pseudo_clementine_consolidate as consolidate
from tools.extra_texts import pseudo_clementine_pages as transport
from tools.extra_texts import pseudo_clementine_run as runner
from tools.extra_texts import pseudo_clementine_translation as translation
from tools.extra_texts.pseudo_clementine_selected import load_selected

WORK = "pseudo_clementine_homilies"


def filtered_references(workflow: Path) -> set[str]:
    blocked = set()
    for response_path in workflow.rglob("*.response.json"):
        response = json.loads(response_path.read_text())
        if not any(c.get("finish_reason") == "content_filter" for c in response.get("choices", [])):
            continue
        request_path = response_path.with_name(response_path.name.replace(".response.json", ".request.json"))
        request = json.loads(request_path.read_text())
        refs = request.get("references")
        if not refs:
            raise ValueError("Filtered response lacks reference-bound request; inspect before further calls")
        blocked.update(refs)
    return blocked


def held_passages(workflow: Path, source_rows: list[dict], already_accepted: set[str]) -> list[dict]:
    filtered = filtered_references(workflow)
    held = {}
    for path in workflow.rglob("needs-attention.json"):
        summary = json.loads(path.read_text())
        if not summary.get("draft") or not summary.get("review"):
            continue
        draft_path, review_path = path.parent / summary["draft"], path.parent / summary["review"]
        draft, review = acceptance.validate_bundle(WORK, source_rows,
            str(draft_path.relative_to(translation.source.ROOT)),
            str(review_path.relative_to(translation.source.ROOT)))
        drafts = {row["reference"]: row for row in draft["output"]["passages"]}
        for row in review["output"]["passages"]:
            ref = row["reference"]
            if ref in filtered or ref in already_accepted or acceptance.accepted_passage(row):
                continue
            if ref not in held or review["recorded_at"] > held[ref]["recorded_at"]:
                held[ref] = {"reference": ref, "recorded_at": review["recorded_at"],
                             "draft": drafts[ref], "review": row,
                             "prior_review_record": str(review_path.relative_to(translation.source.ROOT))}
    return [held[row["reference"]] for row in source_rows if row["reference"] in held]


def _repair_locked(item: dict, source_rows: list[dict], workflow: Path, cache: Path, revisions: int) -> dict:
    ref = item["reference"]
    filtered = filtered_references(workflow)
    if ref in filtered:
        raise ValueError("Provider-filtered reference requires an authorized alternative, not a retry")
    directory = workflow / ("focused-followup-" + ref.replace(".", "-") + "-v1")
    if (directory / "accepted.json").exists() or (directory / "needs-attention.json").exists():
        return {"reference": ref, "status": "existing_terminal_followup_not_restarted"}
    directory.mkdir(parents=True, exist_ok=True)
    index = next(i for i, row in enumerate(source_rows) if row["reference"] == ref)
    context = {"previous_draft": item["draft"], "previous_review": item["review"],
               "prior_review_record": item["prior_review_record"],
               "adjacent_greek_for_context_only": [r for r in source_rows[max(0, index - 1):index + 2] if r["reference"] not in filtered]}
    for revision in range(revisions + 1):
        packet = translation.prepare(WORK, [ref], transport.DRAFTER, source_variant="lagarde1865")
        packet["context"]["focused_revision_evidence"] = context
        packet["params"]["messages"].append({"role": "user", "content":
            "Revise only this requested passage in direct response to the independent findings below. "
            "Keep accurate English and every valid uncertainty/lexical disclosure; do not gratuitously "
            "rewrite them. The Greek must not change. Adjacent Greek supplies context, not additional "
            "sentences to import into this passage or quote as its own wording. Preserve every printed "
            "gap and its dot count, without reconstructing lost text. A difficult reading that still "
            "has no defensible rendering remains blocked. Do not aim at an accept label: fresh independent "
            "review will assess the complete main text and notes. Return the ordinary complete draft "
            "JSON for exactly the one requested reference.\n" + json.dumps(context, ensure_ascii=False)})
        runner.rehash(packet)
        draft = runner.execute(packet, directory, f"v{revision}.draft", cache)
        packet = translation.prepare(WORK, [ref], transport.REVIEWER, draft, source_variant="lagarde1865")
        packet["context"]["adjacent_greek_for_context_only"] = context["adjacent_greek_for_context_only"]
        packet["params"]["messages"].append({"role": "user", "content":
            "The following adjacent Greek is context only. Independently verify the requested passage "
            "against its unchanged Greek; do not treat the prior proposed repair as authority. Findings "
            "must quote the requested passage itself, not its neighbors.\n" +
            json.dumps(context["adjacent_greek_for_context_only"], ensure_ascii=False)})
        runner.rehash(packet)
        review = runner.execute(packet, directory, f"v{revision}.review", cache)
        if runner.accepted(draft, review):
            result = {"references": [ref], "status": "accepted", "draft": f"v{revision}.draft.record.json",
                      "review": f"v{revision}.review.record.json", "source_hash": draft["source_hash"],
                      "draft_output_hash": draft["output_hash"], "review_output_hash": review["output_hash"],
                      "publication_status": "not_published"}
            transport.save(directory / "accepted.json", result)
            return {"reference": ref, "status": "accepted", "revision": revision}
        context["previous_draft"], context["previous_review"] = draft["output"]["passages"][0], review["output"]["passages"][0]
    result = {"references": [ref], "status": "needs_editorial_attention",
              "draft": f"v{revisions}.draft.record.json", "review": f"v{revisions}.review.record.json",
              "publication_status": "not_published"}
    transport.save(directory / "needs-attention.json", result)
    return {"reference": ref, "status": "needs_editorial_attention"}


def repair(item: dict, source_rows: list[dict], workflow: Path, cache: Path, revisions: int) -> dict:
    directory = workflow / ("focused-followup-" + item["reference"].replace(".", "-") + "-v1")
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ".lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return _repair_locked(item, source_rows, workflow, cache, revisions)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--max-revisions", type=int, default=1)
    parser.add_argument("--cache", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.limit <= 40 or not 0 <= args.max_revisions <= 2:
        parser.error("Refusing an unbounded follow-up request")
    source = load_selected(WORK)
    workflow = translation.source.SOURCE_ROOT / WORK / "translation_workflow"
    accepted = consolidate.consolidate(complete=False)
    todo = held_passages(workflow, source["passages"], {r["reference"] for r in accepted["passages"]})
    todo = [item for item in todo if not (workflow / ("focused-followup-" + item["reference"].replace(".", "-") + "-v1") / "needs-attention.json").exists()]
    for item in todo[:args.limit]:
        try:
            result = repair(item, source["passages"], workflow, args.cache, args.max_revisions)
        except (ValueError, KeyError, RuntimeError) as exc:
            result = {"reference": item["reference"], "status": "stopped_requires_inspection", "error": str(exc)}
        print(json.dumps(result), flush=True)
