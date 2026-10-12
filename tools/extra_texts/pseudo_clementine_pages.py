#!/usr/bin/env python3
"""Transcribe Lagarde page images and require independent Sol 6.1 image review.

Uses existing Azure CLI authorization through az rest; never retrieves keys or
tokens. Requests containing image pixels stay in the local cache, not the repo.
Repo receipts retain request/image/PDF hashes, text prompts and raw responses.
This is source preparation, not English generation or reader publication.
"""
from __future__ import annotations

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
import re
from pathlib import Path
import subprocess
import time
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "sources/pseudo_clementines/lagarde1865"
ENDPOINT = "https://cartha-aoai-truth-1c9177c8.openai.azure.com"
DRAFTER = "gpt-5-6-sol-atlas"
REVIEWER = "gpt-6-1-sol-review"
CHECKS = ["body_complete", "no_apparatus", "no_invented_text", "punctuation_and_diacritics", "printed_gaps_preserved"]


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def save(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def valid_lines(value: object) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError("Missing body lines")
    if any(not isinstance(line, str) or not line.strip() for line in value):
        raise ValueError("Invalid or blank body line")
    text = " ".join(value)
    if len(text) < 100 or not any("\u0370" <= c <= "\u03ff" or "\u1f00" <= c <= "\u1fff" for c in text):
        raise ValueError("Expected substantive Greek text")


def parse_response(response: dict) -> dict:
    choices = response.get("choices", [])
    if len(choices) != 1 or choices[0].get("finish_reason") != "stop":
        raise ValueError("Missing or truncated model result")
    content = choices[0].get("message", {}).get("content")
    if not isinstance(content, str):
        raise ValueError("No model text")
    return json.loads(content)


def validate_review(review: dict, lines: list[str]) -> None:
    if review.get("verdict") not in {"accept", "revise", "blocked"}:
        raise ValueError("Invalid source-review verdict")
    checks = review.get("checks", {})
    if set(checks) != set(CHECKS) or any(type(v) is not bool for v in checks.values()):
        raise ValueError("Missing image-review checks")
    if not isinstance(review.get("findings"), list) or not isinstance(review.get("corrected_lines"), list):
        raise ValueError("Incomplete source-review result")
    if review["verdict"] == "accept":
        if not all(checks.values()) or review["corrected_lines"] or review["findings"]:
            raise ValueError("Acceptance contradicts findings or changes")
    if review["verdict"] == "revise":
        valid_lines(review["corrected_lines"])
        if review["corrected_lines"] == lines:
            raise ValueError("Revision did not change transcription")


def verify_checked(directory: Path, image: Path, tiles: list[Path] | None = None, artifact: str = "checked.json") -> dict:
    checked = json.loads((directory / artifact).read_text())
    valid_lines(checked["body_lines"])
    if checked["body_lines_sha256"] != sha(canonical(checked["body_lines"])) or checked["image_sha256"] != sha(image.read_bytes()):
        raise ValueError("Checked text or source image changed")
    review_path = directory / checked["review_record"]
    if review_path.parent != directory or not review_path.name.startswith("review-"):
        raise ValueError("Invalid review evidence path")
    record = json.loads(review_path.read_text())
    if sha(canonical(record)) != checked["review_record_sha256"]:
        raise ValueError("Review evidence changed")
    if record["input_lines"] != checked["body_lines"] or record["image_sha256"] != checked["image_sha256"] or record["pdf_page"] != checked["pdf_page"]:
        raise ValueError("Review is not bound to this text/image")
    if record.get("zoom_sha256") != ([sha(p.read_bytes()) for p in tiles] if tiles else None):
        raise ValueError("Zoom evidence changed or was not supplied")
    if not str(record.get("model", "")).startswith("gpt-6.1-sol-") or record["review"]["verdict"] != "accept":
        raise ValueError("Missing accepted GPT-6.1 Sol image review")
    matched = False
    for response_path in directory.glob(review_path.stem + ".response.attempt*.json"):
        receipt = json.loads(response_path.read_text())
        if receipt.get("status") != "success" or receipt.get("request_sha256") != record["request_sha256"]:
            continue
        response = receipt["response"]
        if response.get("model") == record["model"] and parse_response(response) == record["review"]:
            matched = True
    if not matched:
        raise ValueError("Accepted review has no matching actual model response")
    if record.get("blind_lines_sha256"):
        blind = json.loads((directory / "blind.json").read_text())
        if not blind.get("initial_draft_was_not_supplied") or sha(canonical(blind["output"]["body_lines"])) != record["blind_lines_sha256"]:
            raise ValueError("Independent blind transcription evidence changed")
    validate_review(record["review"], checked["body_lines"])
    observations = SOURCE / "visual_controls.json"
    if observations.exists():
        controls = json.loads(observations.read_text()).get(str(checked["pdf_page"]), {})
        text = unicodedata.normalize("NFC", " ".join(checked["body_lines"]).replace("|", ""))
        for term in controls.get("required_readings", []):
            if unicodedata.normalize("NFC", term) not in text:
                raise ValueError(f"Model acceptance misses visually verified reading: {term}")
    return checked


def invoke(body: dict, cache: Path, evidence: Path) -> dict:
    """A completed HTTP error may be retried. A timeout is never restarted here."""
    request_hash = sha(canonical(body))
    request_file = cache / f"{request_hash}.request.json"
    save(request_file, body)
    request_file.chmod(0o600)
    for attempt in range(1, 4):
        path = evidence.with_name(evidence.name + f".attempt{attempt}.json")
        if path.exists():
            saved = json.loads(path.read_text())
            if saved["request_sha256"] != request_hash:
                raise ValueError("Existing response belongs to a different request")
            if saved["status"] == "success":
                return saved["response"]
            if not saved.get("retryable"):
                raise RuntimeError("Prior terminal request failure requires inspection")
            continue
        command = ["az", "rest", "--method", "post", "--url",
                   f"{ENDPOINT}/openai/deployments/{body['model']}/chat/completions?api-version=2025-04-01-preview",
                   "--resource", "https://cognitiveservices.azure.com/", "--headers", "Content-Type=application/json",
                   "--body", "@" + str(request_file), "-o", "json"]
        started = datetime.now(timezone.utc).isoformat()
        # The runner is the live process handle. No observation timeout/restart.
        result = subprocess.run(command, capture_output=True, text=True)
        receipt = {"request_sha256": request_hash, "started_at": started,
                   "finished_at": datetime.now(timezone.utc).isoformat(), "attempt": attempt}
        if result.returncode:
            # Persist only the service failure text, never verbose CLI/debug output.
            retryable = any(token in result.stderr for token in ["Internal Server Error", "server_error", "Too Many Requests", "429", "503", "502", "504"])
            receipt.update(status="error", retryable=retryable,
                           error_kind="transient_service_error" if retryable else "terminal_cli_error")
            save(path, receipt)
            if not retryable:
                raise RuntimeError("Azure request failed; inspect access/service state without exposing credentials")
            time.sleep(attempt * 15)
            continue
        response = json.loads(result.stdout)
        receipt.update(status="success", response=response)
        save(path, receipt)
        return response
    raise RuntimeError("Three service-error attempts exhausted")


def request_for(image: Path, page: int, lines: list[str] | None, tiles: list[Path] | None = None) -> dict:
    shared = """Read the attached image of Paul de Lagarde's 1865 Greek Clementina. Work directly from visible print, not a remembered text, online OCR or translation. Transcribe only the large-font Greek primary text, including titles and section numbers printed INLINE in the body. EXCLUDE running headers, printed page numbers, marginal line numbers, margin letters and old-edition page numbers, scriptural cross-reference rows and the small-font critical apparatus beneath the body. Retain printed accents, breathings, iota subscripts, punctuation, brackets, lacuna dots, dashes and word-splitting hyphens exactly; do not normalize or restore them. Each array entry is ONE complete physical body line, including titles as separate lines. Never silently repair the author's or printer's wording. This is a print transcription, not a manuscript collation. Return only JSON."""
    if lines is None:
        task = 'Transcribe this page. Return {"printed_page":"visible page number or null if not printed","body_lines":["one exact physical body line", "next line"],"uncertainties":[{"line":1,"description":"specific unreadable/uncertain ink; not printed lacunae"}]}. Use [?] only for genuinely unreadable ink, and report it. Preserve printed lacuna dots rather than filling them.'
    else:
        task = """Independently compare EVERY line of this proposed transcription with the image. Check omitted lines, accidental apparatus/margin inclusions, Greek letters, accents/breathings, punctuation and printed lacunae. Return {"verdict":"accept|revise|blocked","checks":{"body_complete":true,"no_apparatus":true,"no_invented_text":true,"punctuation_and_diacritics":true,"printed_gaps_preserved":true},"findings":[{"line":1,"issue":"specific visible discrepancy and evidence"}],"corrected_lines":[]}. Accept ONLY when every check is true and findings/corrected_lines are empty. If you can read a needed correction, verdict revise and provide the COMPLETE corrected body_lines array (not just changed lines); every revision will receive another image review. If ink is genuinely unreadable, verdict blocked. Do not propose a change merely because a different reading seems grammatical. Printed editorial brackets and lacunae are evidence to preserve, not defects to reconstruct. PROPOSED LINES:\n""" + json.dumps(lines, ensure_ascii=False)
    content = [{"type": "text", "text": f"PDF page {page}.\n{task}"},
               {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(image.read_bytes()).decode(), "detail": "high"}}]
    if tiles:
        content.append({"type": "text", "text": "The next six overlapping high-resolution views are crops rendered directly from THIS SAME PDF PAGE, ordered top-left, top-right, middle-left, middle-right, bottom-left, bottom-right. Use them to read individual Greek letters, not to add duplicate lines. The full page above establishes line order and body/apparatus boundaries. Check words against zoomed ink even when the proposed text looks plausible."})
        for tile in tiles:
            content.append({"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(tile.read_bytes()).decode(), "detail": "high"}})
    return {"model": DRAFTER if lines is None else REVIEWER,
            "messages": [{"role": "system", "content": shared},
                         {"role": "user", "content": content}],
            "max_completion_tokens": 16000, "reasoning_effort": "high",
            "response_format": {"type": "json_object"}}


def render_tiles(pdf: Path, page: int, cache: Path) -> list[Path]:
    info = subprocess.check_output(["pdfinfo", "-f", str(page), "-l", str(page), str(pdf)], text=True)
    match = re.search(rf"Page\s+{page}\s+size:\s+([\d.]+) x ([\d.]+) pts", info)
    if not match:
        raise ValueError("Could not establish this PDF page's actual dimensions")
    width, height = [math.ceil(float(v) * 300 / 72) for v in match.groups()]
    tile_width, tile_height = math.ceil(width * 0.55), math.ceil(height * 0.39)
    result = []
    for y in [0, (height - tile_height) // 2, height - tile_height]:
        for x in [0, width - tile_width]:
            path = cache / f"lagarde1865-{page:03d}-{x}-{y}.png"
            subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-r", "300", "-x", str(x), "-y", str(y), "-W", str(tile_width), "-H", str(tile_height), "-png", "-singlefile", str(pdf), str(path.with_suffix(""))], check=True, capture_output=True)
            result.append(path)
    return result


def process_page(page: int, pdf: Path, cache: Path, max_reviews: int, series: str = "pages", zoom: bool = False, blind_review: bool = False) -> dict:
    directory = SOURCE / series / f"{page:03d}"
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ".lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        ready = directory / "checked.json"
        image = cache / f"lagarde1865-{page:03d}.png"
        subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-scale-to", "2400", "-png", "-singlefile", str(pdf), str(image.with_suffix(""))], check=True, capture_output=True)
        tiles = render_tiles(pdf, page, cache) if zoom else None
        if ready.exists():
            verify_checked(directory, image, tiles)
            return {"page": page, "status": "already_checked"}
        draft_request = request_for(image, page, None, tiles)
        draft = invoke(draft_request, cache, directory / "draft.response")
        if not str(draft.get("model", "")).startswith("gpt-5.6-sol-"):
            raise ValueError("Unexpected drafting model")
        parsed = parse_response(draft)
        lines = parsed.get("body_lines")
        valid_lines(lines)
        if not isinstance(parsed.get("uncertainties"), list):
            raise ValueError("Missing transcription uncertainty field")
        save(directory / "draft.json", {"output": parsed, "model": draft.get("model"),
             "image_sha256": sha(image.read_bytes()), "request_sha256": sha(canonical(draft_request)),
             "text_prompt": draft_request["messages"][0]["content"] + "\n" + draft_request["messages"][1]["content"][0]["text"]})
        blind_lines = None
        if blind_review:
            blind_request = request_for(image, page, None, tiles)
            blind_request["model"] = REVIEWER
            response = invoke(blind_request, cache, directory / "blind.response")
            if not str(response.get("model", "")).startswith("gpt-6.1-sol-"):
                raise ValueError("Unexpected independent transcription model")
            blind = parse_response(response)
            blind_lines = blind.get("body_lines")
            valid_lines(blind_lines)
            save(directory / "blind.json", {"output": blind, "model": response["model"], "image_sha256": sha(image.read_bytes()), "request_sha256": sha(canonical(blind_request)), "initial_draft_was_not_supplied": True})
        for iteration in range(1, max_reviews + 1):
            body = request_for(image, page, lines, tiles)
            if blind_lines is not None:
                body["messages"][1]["content"][0]["text"] += "\n\nA separate blind transcription of these same images (made WITHOUT seeing the proposed draft) follows. Neither candidate has authority over the ink. Investigate every disagreement against the zoomed image, especially plausible substitutions of different Greek words. Do not prefer the proposed draft just because it was presented first. Independent blind lines:\n" + json.dumps(blind_lines, ensure_ascii=False)
            response = invoke(body, cache, directory / f"review-{iteration}.response")
            if not str(response.get("model", "")).startswith("gpt-6.1-sol-"):
                raise ValueError("Unexpected review model; no substitution allowed")
            review = parse_response(response)
            validate_review(review, lines)
            record = {"pdf_page": page, "image_sha256": sha(image.read_bytes()),
                      "input_lines": lines, "input_lines_sha256": sha(canonical(lines)),
                      "request_sha256": sha(canonical(body)), "model": response.get("model"),
                      "zoom_sha256": [sha(p.read_bytes()) for p in tiles] if tiles else None,
                      "blind_lines_sha256": sha(canonical(blind_lines)) if blind_lines is not None else None,
                      "review": review, "text_prompt": body["messages"][0]["content"] + "\n" + body["messages"][1]["content"][0]["text"]}
            save(directory / f"review-{iteration}.json", record)
            if review["verdict"] == "accept":
                if any("[?]" in line for line in lines):
                    raise ValueError("Unreadable ink marker cannot be auto-approved")
                checked = {"pdf_page": page, "printed_page": page - 42, "draft_visible_page_label": parsed.get("printed_page"),
                           "body_lines": lines, "body_lines_sha256": sha(canonical(lines)),
                           "image_sha256": record["image_sha256"],
                           "review_record": f"review-{iteration}.json", "review_record_sha256": sha(canonical(record)),
                           "status": "automated_image_check_passed_not_human_signoff"}
                candidate = directory / "checked.candidate.json"
                save(candidate, checked)
                try:
                    verify_checked(directory, image, tiles, candidate.name)
                except ValueError as exc:
                    save(directory / "rejected-check.json", {"candidate": checked, "reason": str(exc), "release_eligible": False})
                    candidate.unlink()
                    raise
                candidate.replace(ready)
                return {"page": page, "status": "checked", "review_passes": iteration}
            if review["verdict"] == "blocked":
                return {"page": page, "status": "needs_manual_source_read"}
            lines = review["corrected_lines"]
        return {"page": page, "status": "review_limit_reached"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--pages", required=True, help="Comma-separated PDF page numbers or inclusive ranges")
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--max-reviews", type=int, default=3)
    parser.add_argument("--series", default="pages")
    parser.add_argument("--zoom", action="store_true")
    parser.add_argument("--blind-review", action="store_true")
    args = parser.parse_args()
    if not 1 <= args.workers <= 4 or not 1 <= args.max_reviews <= 5:
        parser.error("workers must be 1-4; max-reviews must be 1-5")
    if not re.fullmatch(r"[a-z0-9-]+", args.series):
        parser.error("series must be a simple lowercase directory name")
    manifest = json.loads((SOURCE / "manifest.json").read_text())
    if sha(args.pdf.read_bytes()) != manifest["pdf_sha256"]:
        parser.error("PDF does not match registered source hash")
    pages = []
    for part in args.pages.split(","):
        bounds = list(map(int, part.split("-")))
        pages.extend(range(bounds[0], bounds[-1] + 1))
    if len(set(pages)) != len(pages) or not set(pages) <= set(manifest["transcription_pdf_pages"]):
        parser.error("Duplicate or out-of-scope pages")
    args.cache.mkdir(parents=True, exist_ok=True)
    run = {"pid": os.getpid(), "started_at": datetime.now(timezone.utc).isoformat(), "pipeline_sha256": sha(Path(__file__).read_bytes()), "pages": pages, "series": args.series, "zoom": args.zoom, "blind_review": args.blind_review, "results": []}
    receipt = args.cache / f"run-{os.getpid()}.json"
    save(receipt, run)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        jobs = {pool.submit(process_page, p, args.pdf, args.cache, args.max_reviews, args.series, args.zoom, args.blind_review): p for p in pages}
        for future in as_completed(jobs):
            try:
                result = future.result()
            except Exception as exc:
                result = {"page": jobs[future], "status": "error", "error": str(exc)}
            run["results"].append(result)
            save(receipt, run)
            print(json.dumps(result), flush=True)
    run["finished_at"] = datetime.now(timezone.utc).isoformat()
    save(receipt, run)
    return 0 if all(r["status"] in {"checked", "already_checked"} for r in run["results"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
