"""Review a blocked print page against an explicitly mapped second copy.

This does not infer alternate-page offsets, repair Greek, or approve a reading.
Both PDFs must match the registered source hashes. A complete new image review
is required, with the added evidence retained in the selected-page artifact.
"""
import argparse
import base64
import fcntl
import json
from pathlib import Path
import subprocess

from tools.extra_texts import pseudo_clementine_pages as p


def run(page: int, alternate_page: int, printed: int, parent: str,
        scope: str, pdf: Path, alternate: Path, cache: Path) -> dict:
    manifest = json.loads((p.SOURCE / "manifest.json").read_text())
    metadata = json.loads((p.SOURCE / "alternate-scan.json").read_text())
    if p.sha(pdf.read_bytes()) != manifest["pdf_sha256"] or p.sha(alternate.read_bytes()) != metadata["pdf_sha256"]:
        raise ValueError("Source PDF differs from registered scan")
    if printed != page - 42:
        raise ValueError("Primary printed page mapping is inconsistent")
    if not parent.startswith("review-") or "/" in parent or not parent.endswith(".json"):
        raise ValueError("Invalid parent review filename")
    parent_path = p.SOURCE / "pages-blind" / f"{page:03d}" / parent
    prior = json.loads(parent_path.read_text())
    if prior["pdf_page"] != page:
        raise ValueError("Parent review belongs to another page")
    lines = list(prior["input_lines"])
    directory = p.SOURCE / "pages-supplemented" / f"{page:03d}"
    directory.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    with (directory / ".lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        image = cache / f"lagarde1865-{page:03d}.png"
        alt = cache / f"alternate-{alternate_page:03d}.png"
        for source, number, target, scale in ((pdf, page, image, 2400), (alternate, alternate_page, alt, 1800)):
            subprocess.run(["pdftoppm", "-f", str(number), "-l", str(number), "-scale-to", str(scale),
                            "-png", "-singlefile", str(source), str(target.with_suffix(""))], check=True, capture_output=True)
        tiles = p.render_tiles(pdf, page, cache)
        if (directory / "checked.json").exists():
            return p.verify_checked(directory, image, tiles)
        supplement = {"source_url": metadata["pdf_url"], "pdf_sha256": metadata["pdf_sha256"],
                      "pdf_page": alternate_page, "printed_page": printed,
                      "image_sha256": p.sha(alt.read_bytes()),
                      "mapping": f"Alternate PDF p.{alternate_page} and primary PDF p.{page} show the same printed p.{printed}; visually verified before this request.",
                      "scope": scope}
        p.save(directory / "supplement.json", supplement)
        for iteration in range(1, 6):
            body = p.request_for(image, page, lines, tiles)
            added = (f"The following is a SECOND COPY of the SAME printed page {printed} in the SAME Lagarde 1865 edition, "
                     f"publicly available at {metadata['item_url']}, alternate PDF page {alternate_page}. "
                     f"Mapping has been visually checked. Evidence scope: {scope} "
                     "Use visible ink, not grammar or a remembered text. No proposed word is presumed correct. "
                     "All lines require the ordinary complete image comparison. Do not duplicate the text.")
            body["messages"][1]["content"] += [{"type": "text", "text": added},
                {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(alt.read_bytes()).decode(), "detail": "high"}}]
            response = p.invoke(body, cache, directory / f"review-{iteration}.response")
            if not response.get("model", "").startswith("gpt-6.1-sol-"):
                raise ValueError("Unexpected review model")
            review = p.parse_response(response)
            p.validate_review(review, lines)
            record = {"pdf_page": page, "image_sha256": p.sha(image.read_bytes()), "input_lines": lines,
                      "input_lines_sha256": p.sha(p.canonical(lines)), "request_sha256": p.sha(p.canonical(body)),
                      "model": response["model"], "zoom_sha256": [p.sha(t.read_bytes()) for t in tiles],
                      "review": review, "supplemental_source": supplement,
                      "parent_review": str(parent_path.relative_to(p.ROOT)),
                      "parent_review_sha256": p.sha(parent_path.read_bytes()),
                      "text_prompt": body["messages"][0]["content"] + "\n" + body["messages"][1]["content"][0]["text"] + "\n" + added}
            p.save(directory / f"review-{iteration}.json", record)
            print(json.dumps({"page": page, "review": iteration, "verdict": review["verdict"]}), flush=True)
            if review["verdict"] == "accept":
                if any("[?]" in line for line in lines):
                    raise ValueError("Unresolved ink cannot be certified")
                checked = {"pdf_page": page, "printed_page": printed, "body_lines": lines,
                           "body_lines_sha256": p.sha(p.canonical(lines)), "image_sha256": record["image_sha256"],
                           "review_record": f"review-{iteration}.json", "review_record_sha256": p.sha(p.canonical(record)),
                           "supplemental_source": supplement, "status": "automated_image_check_passed_not_human_signoff"}
                p.save(directory / "checked.candidate.json", checked)
                p.verify_checked(directory, image, tiles, "checked.candidate.json")
                (directory / "checked.candidate.json").replace(directory / "checked.json")
                return checked
            if review["verdict"] == "blocked":
                raise ValueError("Alternate copy did not resolve the source problem")
            lines = review["corrected_lines"]
        raise ValueError("Supplement review limit reached")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page", type=int, required=True)
    parser.add_argument("--alternate-page", type=int, required=True)
    parser.add_argument("--printed-page", type=int, required=True)
    parser.add_argument("--parent", required=True)
    parser.add_argument("--scope", required=True)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--alternate-pdf", type=Path, required=True)
    parser.add_argument("--cache", type=Path, required=True)
    args = parser.parse_args()
    run(args.page, args.alternate_page, args.printed_page, args.parent,
        args.scope, args.pdf, args.alternate_pdf, args.cache)
