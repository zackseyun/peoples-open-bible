"""Export a complete checked historical-reader candidate; never deploy or publish."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import subprocess

from tools.extra_texts import pseudo_clementine_acceptance as acceptance
from tools.extra_texts import pseudo_clementine_pages as pages
from tools.extra_texts import pseudo_clementine_translation as tr
from tools.extra_texts.pseudo_clementine_selected import load_selected


def pinned_bytes(relative: str, commit: str) -> bytes:
    if not re.fullmatch(r"[a-f0-9]{40}", commit):
        raise ValueError("Export requires a full pinned commit")
    path = acceptance.safe_path(relative)
    result = subprocess.run(["git", "show", f"{commit}:{relative}"], cwd=tr.source.ROOT,
                            capture_output=True, check=False)
    if result.returncode or result.stdout != path.read_bytes():
        raise ValueError("Evidence is absent or changed from pinned commit: " + relative)
    return result.stdout


def render_text(title: str, source: dict, accepted: dict) -> str:
    if accepted["status"] != "complete_model_checked_candidate" or accepted["missing_references"]:
        raise ValueError("Partial acceptance cannot become a reader candidate")
    blocks = [
        title.upper(),
        "Historical early-Christian literature, not additional canonical Scripture.\nTraditional attribution is not a claim of genuine apostolic authorship.",
        "People's Open Bible AI-assisted English draft, translated from the image-checked Greek of "
        + source["edition"] + ". Separately compared with the Greek by GPT-6.1 Sol. "
        "This is automated source/translation review, not human scholarly sign-off or a stable-edition claim.",
        "Source scan: " + source["source_snapshot"]["url"],
        "The ancient Greek and 1865 edition are public domain. Original POB English contributions and notes are offered under CC BY 4.0; no upstream XML is relicensed by this edition.",
    ]
    if any(tr.printed_gap_lengths(row["source_text"]) for row in source["passages"]):
        blocks.append("Coverage follows all surviving wording of the selected edition. Printed lacunae remain explicit gaps and are explained in the translator's notes. Lost wording has not been reconstructed; this is not a claim that the original survives unbroken.")
    homily = None
    for row in accepted["passages"]:
        reference = row["reference"]
        tr.validate_printed_gaps(next(p["source_text"] for p in source["passages"] if p["reference"] == reference), row)
        if "." in reference:
            current = int(reference.split(".")[0])
            if current != homily:
                blocks.append(f"HOMILY {current}")
                homily = current
        blocks.extend([f"SECTION {reference}", row["text"]])
        if row["source_issues"] or row.get("lexical_decisions"):
            blocks.append(f"Translator's notes for section {reference} (not part of the ancient text):")
            for n, issue in enumerate(row["source_issues"], 1):
                if issue["blocks_publication"]:
                    raise ValueError("Unresolved source issue in reader text")
                blocks.append(f"{n}. Greek: {issue['source_quote']}\n{issue['issue']}")
            for n, decision in enumerate(row.get("lexical_decisions", []), len(row["source_issues"])+1):
                blocks.append(f"{n}. Translation choice — Greek: {decision['source_quote']}\nRendered as: {decision['chosen']}\n{decision['rationale']}")
    blocks.append("End of " + title + ".")
    return "\n\n".join(blocks) + "\n"


def export(work: str, selections_path: Path, commit: str, destination: Path) -> dict:
    selections = json.loads(selections_path.read_text())
    # Completion is checked before any output is written.
    accepted = acceptance.collect(work, selections, complete=True)
    source = load_selected(work)
    title = tr.source.WORKS[work][2]
    identity = work.replace("_", "-")
    evidence_paths = set()
    def pin(path: Path | str):
        relative = str(path.relative_to(tr.source.ROOT)) if isinstance(path, Path) else path
        if relative not in evidence_paths:
            pinned_bytes(relative, commit)
            evidence_paths.add(relative)
    pin(selections_path.resolve())
    pin(pages.SOURCE / "selected" / (work + ".json"))
    pin(pages.SOURCE / "manifest.json")
    for evidence in source["page_evidence"]:
        checked_path = acceptance.safe_path(evidence["checked_path"])
        for path in checked_path.parent.glob("*.json"):
            pin(path)
        for adjudication in evidence.get("adjudications", []):
            pin(adjudication["review_request"])
            pin(adjudication["review_response"])
    records, raw_responses, references = [], [], []
    bundle_indices = {}
    for selection in selections:
        pair = (selection["draft"], selection["review"])
        if pair not in bundle_indices:
            draft, review = acceptance.validate_bundle(work, source["passages"], *pair)
            for path in (*pair, review["evidence_files"]["request"], review["evidence_files"]["response"]):
                pin(path)
            request = json.loads(acceptance.safe_path(review["evidence_files"]["request"]).read_text())
            response = json.loads(acceptance.safe_path(review["evidence_files"]["response"]).read_text())
            bundle_indices[pair] = len(records)
            records.append({"draft": draft, "review": review, "review_request": request})
            raw_responses.append(response)
        references.extend({"reference": ref, "bundle": bundle_indices[pair]} for ref in selection["references"])
    if len({record["review"]["model"] for record in records}) != 1:
        raise ValueError("Mixed review model versions require an explicit archive schema update")
    order = accepted["expected_references"]
    references.sort(key=lambda item: order.index(item["reference"]))
    raw_bytes = (json.dumps({"responses": raw_responses}, ensure_ascii=False, indent=2) + "\n").encode()
    text = render_text(title, source, accepted)
    proof = {
        "schema_version": 2, "kind": "pob_source_checked_translation",
        "canonical_repository": "https://github.com/zackseyun/peoples-open-bible",
        "canonical_commit": commit, "source": source, "review_bundles": records,
        "selections": references, "raw_review_path": f"/historical-library/provenance/{identity}.review-response.json",
        "raw_review_sha256": pages.sha(raw_bytes), "pinned_evidence_paths": sorted(evidence_paths),
    }
    proof_bytes = (json.dumps(proof, ensure_ascii=False, indent=2) + "\n").encode()
    manifest = {
        "work": work, "title": title, "canonical_commit": commit, "canon_effect": "none",
        "status": "complete_model_checked_candidate", "live_publication_verified": False,
        "review_model": records[0]["review"]["model"], "section_count": len(order),
        "text_sha256": pages.sha(text.encode()), "text_bytes": len(text.encode()),
        "provenance_sha256": pages.sha(proof_bytes), "raw_review_sha256": pages.sha(raw_bytes),
        "remaining_checks": ["Website integrity verifier", "Reader rendering and section navigation",
                             "Rights and disclosure display", "Main integration", "Authorized deployment and live verification"],
    }
    if work == "pseudo_clementine_homilies":
        manifest["homily_section_counts"] = [sum(ref.startswith(f"{h}.") for ref in order) for h in range(1,21)]
    outputs = {
        identity + ".txt": text.encode(), identity + ".json": proof_bytes,
        identity + ".review-response.json": raw_bytes,
        identity + ".candidate.json": (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode(),
    }
    for name, data in outputs.items():
        path = destination / name
        if path.exists() and path.read_bytes() != data:
            raise ValueError("Refusing to overwrite a different candidate: " + str(path))
    destination.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        (destination / name).write_bytes(data)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", choices=tr.source.WORKS, required=True)
    parser.add_argument("--selections", type=Path, required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.work, args.selections, args.commit, args.destination), ensure_ascii=False, indent=2))
