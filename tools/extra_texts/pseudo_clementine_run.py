#!/usr/bin/env python3
"""Run bounded direct-Greek draft/review/revision batches with preserved receipts.

Uses the existing Azure CLI identity through the source pipeline's request
transport. No API keys/tokens are retrieved or printed. Does not publish.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
import fcntl
import json
from pathlib import Path

from tools.extra_texts import pseudo_clementine_pages as transport
from tools.extra_texts import pseudo_clementine_translation as translation
from tools.extra_texts.pseudo_clementine_selected import load_selected, load_first_homily, load_print_variant


def rehash(request: dict) -> None:
    request["request_hash"] = translation.digest(request["params"])
    request["packet_hash"] = translation.digest({k: v for k, v in request.items() if k != "packet_hash"})


def format_repairable(error: Exception) -> bool:
    """Model output repair must never repair away a source/evidence invariant."""
    return isinstance(error, json.JSONDecodeError) or str(error).startswith((
        "Audit quotation is not present", "Output passage coverage/order mismatch",
        "Empty English draft", "Missing lexical/source audit fields",
        "Incomplete lexical decision", "Incomplete source issue",
        "Missing review verdict", "Missing or non-boolean source checks",
        "Missing review findings", "Incomplete review finding", "Malformed fenced output",
    ))


def execute(request: dict, directory: Path, stem: str, cache: Path) -> dict:
    """Preserve malformed results; bounded format repair is not an approval."""
    request = copy.deepcopy(request)
    record_path = directory / f"{stem}.record.json"
    if record_path.exists():
        cached = json.loads(record_path.read_text())
        initial = directory / f"{stem}.request.initial.json"
        if not initial.exists() or json.loads(initial.read_text()) != request:
            raise ValueError("Existing record belongs to a different request plan; use a new run name")
        evidence = cached["evidence_files"]
        saved_request = json.loads((transport.ROOT / evidence["request"]).read_text())
        saved_response = json.loads((transport.ROOT / evidence["response"]).read_text())
        actual = translation.validate_response(saved_request, saved_response)
        ignored = {"recorded_at", "evidence_files"}
        if any(cached.get(key) != actual.get(key) for key in (set(cached) | set(actual)) - ignored):
            raise ValueError("Cached record no longer matches actual current-source evidence")
        # Replaying a validated receipt must not make an old verdict appear
        # newer than a subsequent adverse review or overwrite its chronology.
        return cached
    for attempt in range(1, 4):
        label = stem if attempt == 1 else f"{stem}.format-{attempt}"
        existing = directory / f"{label}.request.initial.json"
        if existing.exists() and json.loads(existing.read_text()) != request:
            # Keep prior repair attempts intact after a validator fix changes
            # the repair explanation. Never rewrite their request evidence.
            label += ".request-" + request["packet_hash"][:12]
        transport.save(directory / f"{label}.request.initial.json", request)
        response = transport.invoke(request["params"], cache, directory / f"{label}.rpc")
        rehash(request)  # transport may increase max tokens after actual truncation.
        transport.save(directory / f"{label}.request.json", request)
        transport.save(directory / f"{label}.response.json", response)
        try:
            record = translation.validate_response(request, response)
        except (ValueError, KeyError, TypeError, StopIteration) as exc:
            transport.save(directory / f"{label}.validation-error.{translation.digest(str(exc))[:12]}.json", {"error": str(exc), "publication_status": "not_approved"})
            if not format_repairable(exc):
                raise
            choices = response.get("choices", [])
            if len(choices) != 1 or choices[0].get("finish_reason") != "stop":
                raise
            if attempt == 3:
                raise
            request["params"]["messages"] += [
                {"role": "assistant", "content": choices[0]["message"]["content"]},
                {"role": "user", "content": "The structured result failed validation: " + str(exc) + ". Re-submit the complete JSON for exactly the requested references. Every source_quote must be a literal Greek span, or literal ordered spans separated by explicit spaced ellipses. Do not silently omit particles or normalize quoted spelling. Preserve every source clause and all honest uncertainties. This is format/evidence repair, not an instruction to accept a draft or clear any substantive finding."},
            ]
            rehash(request)
            continue
        record["evidence_files"] = {"request": str((directory / f"{label}.request.json").relative_to(transport.ROOT)), "response": str((directory / f"{label}.response.json").relative_to(transport.ROOT))}
        if record_path.exists():
            raise ValueError("Refusing to overwrite an existing draft/review record")
        transport.save(record_path, record)
        return record
    raise RuntimeError("Format repair limit exhausted")


def accepted(draft: dict, review: dict) -> bool:
    refs = draft.get("references", [])
    return (
        bool(refs) and len(set(refs)) == len(refs)
        and review.get("references") == refs
        and [p["reference"] for p in draft["output"]["passages"]] == refs
        and [p["reference"] for p in review["output"]["passages"]] == refs
        and draft["output_hash"] == translation.digest(draft["output"])
        and review["output_hash"] == translation.digest(review["output"])
        and draft["source_hash"] == review["source_hash"]
        and str(review.get("model", "")).startswith("gpt-6.1-sol-")
        and not any(f["severity"] in {"major", "blocking"} for p in review["output"]["passages"] for f in p["findings"])
        and review["draft_output_hash"] == translation.digest(draft["output"])
        and all(p["verdict"] == "accept" and all(p["checks"].get(k) is True for k in translation.CHECKS) for p in review["output"]["passages"])
        and not any(issue["blocks_publication"] for p in draft["output"]["passages"] for issue in p["source_issues"])
    )


def run_batch(work: str, refs: list[str], directory: Path, cache: Path, max_revisions: int, source_variant: str = "lagarde1865") -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ".lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        ready = directory / "accepted.json"
        if ready.exists():
            result = json.loads(ready.read_text())
            draft = json.loads((directory / result["draft"]).read_text())
            review = json.loads((directory / result["review"]).read_text())
            # Source changes invalidate a cached English acceptance.
            translation.prepare(work, refs, transport.REVIEWER, draft, source_variant=source_variant)
            if not accepted(draft, review):
                raise ValueError("Cached batch no longer has accepted current English")
            return {"references": refs, "status": "already_accepted"}
        previous_draft = previous_review = None
        for revision in range(max_revisions + 1):
            packet = translation.prepare(work, refs, transport.DRAFTER, source_variant=source_variant)
            if previous_draft is not None:
                packet["context"]["revision_of"] = previous_draft["output_hash"]
                packet["context"]["review_findings"] = previous_review["output"]
                packet["params"]["messages"].append({"role": "user", "content": "Revise the preceding draft to address the independent review below, then return the same complete draft JSON schema. Keep the supplied Greek unchanged. Preserve uncertainty and interpretive alternatives for readers; do not erase a source problem merely to pass review. Confirmed printed oddities are not necessarily OCR defects, but their interpretation must remain explicitly provisional. Any actual unresolved source corruption still blocks publication. Return fresh exact source quotations; no approval is implied by a suggested replacement.\nPREVIOUS DRAFT:\n" + json.dumps(previous_draft["output"], ensure_ascii=False) + "\nINDEPENDENT REVIEW:\n" + json.dumps(previous_review["output"], ensure_ascii=False)})
                rehash(packet)
            draft = execute(packet, directory, f"v{revision}.draft", cache)
            review_packet = translation.prepare(work, refs, transport.REVIEWER, draft, source_variant=source_variant)
            review = execute(review_packet, directory, f"v{revision}.review", cache)
            if accepted(draft, review):
                result = {"references": refs, "status": "accepted", "source_hash": draft["source_hash"], "draft_output_hash": draft["output_hash"], "review_output_hash": review["output_hash"], "draft": f"v{revision}.draft.record.json", "review": f"v{revision}.review.record.json", "revision": revision, "publication_status": "not_published"}
                transport.save(ready, result)
                return result
            previous_draft, previous_review = draft, review
        result = {"references": refs, "status": "needs_editorial_attention", "draft": f"v{max_revisions}.draft.record.json", "review": f"v{max_revisions}.review.record.json", "publication_status": "not_published"}
        transport.save(directory / "needs-attention.json", result)
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", required=True)
    parser.add_argument("--run", required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--source-variant", choices=["lagarde1865", *[f"lagarde1865-homily-{n}" for n in range(1,21)]], default="lagarde1865")
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--max-revisions", type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.batch_size <= 8 or not 1 <= args.workers <= 2 or not 0 <= args.max_revisions <= 4:
        parser.error("Unbounded batch/concurrency/revision request refused")
    import re
    if not re.fullmatch(r"[a-z0-9-]+", args.run):
        parser.error("Invalid run name")
    if args.source_variant != "lagarde1865" and args.work != "pseudo_clementine_homilies":
        parser.error("Partial Homily source belongs to another work")
    rows = load_print_variant(args.work, args.source_variant)["passages"]
    refs = [r["reference"] for r in rows]
    batches = [refs[i:i + args.batch_size] for i in range(0, len(refs), args.batch_size)]
    directory = translation.source.SOURCE_ROOT / args.work / "translation_workflow" / args.run
    args.cache.mkdir(parents=True, exist_ok=True)
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        jobs = {pool.submit(run_batch, args.work, batch, directory / f"batch-{i+1:03d}", args.cache, args.max_revisions, args.source_variant): batch for i, batch in enumerate(batches)}
        for future in as_completed(jobs):
            try:
                result = future.result()
            except Exception as exc:
                result = {"references": jobs[future], "status": "error", "error": str(exc)}
            results.append(result)
            transport.save(directory / "status.json", {"work": args.work, "expected_references": refs, "results": results, "publication_status": "not_published"})
            print(json.dumps(result), flush=True)
    return 0 if all(r["status"] in {"accepted", "already_accepted"} for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
