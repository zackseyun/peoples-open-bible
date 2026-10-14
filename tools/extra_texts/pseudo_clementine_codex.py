"""Ingest an explicitly authorized Codex Greek draft without fabricating an API response.

This establishes generation provenance only. The ordinary separate Sol6.1
request/response and acceptance gates remain mandatory and unchanged.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from tools.extra_texts import pseudo_clementine_pages as pages
from tools.extra_texts import pseudo_clementine_translation as tr
from tools.extra_texts.pseudo_clementine_selected import load_selected


def validate_output(packet: dict, output: dict, current_rows: list[dict]) -> None:
    if packet.get("kind") != "codex_subagent_translation_request" or packet.get("publication_status") != "candidate_only_not_reviewed":
        raise ValueError("Invalid Codex generation scope")
    refs = packet["references"]
    selected = [row for row in current_rows if row["reference"] in refs]
    if not refs or len(set(refs)) != len(refs) or selected != packet["passages"] or tr.digest(selected) != packet["source_hash"]:
        raise ValueError("Codex packet source changed or references are invalid")
    if set(output) != {"passages"} or [row.get("reference") for row in output["passages"]] != refs:
        raise ValueError("Codex output coverage/order mismatch or self-certification")
    for row in output["passages"]:
        if set(row) != {"reference", "text", "lexical_decisions", "source_issues"}:
            raise ValueError("Unexpected Codex output fields")
        if not isinstance(row["text"], str) or not row["text"].strip():
            raise ValueError("Empty Codex English draft")
        greek = next(r["source_text"] for r in selected if r["reference"] == row["reference"])
        if not isinstance(row["lexical_decisions"], list) or not isinstance(row["source_issues"], list):
            raise ValueError("Missing Codex lexical/source audit")
        for item in [*row["lexical_decisions"], *row["source_issues"]]:
            if not tr.quotation_matches(item.get("source_quote"), greek):
                raise ValueError("Codex audit quotation is not present in supplied Greek")
        for item in row["lexical_decisions"]:
            if not all(isinstance(item.get(k), str) and item[k].strip() for k in ["chosen", "rationale"]):
                raise ValueError("Incomplete Codex lexical decision")
        for item in row["source_issues"]:
            if not isinstance(item.get("issue"), str) or not item["issue"].strip() or type(item.get("blocks_publication")) is not bool:
                raise ValueError("Incomplete Codex source issue")
        tr.validate_printed_gaps(greek, row)
        tr.validate_curation_disclosures(next(r for r in selected if r["reference"] == row["reference"]), row)


def ingest(packet_path: Path, output_path: Path, destination: Path, agent_task: str, *, references: list[str] | None = None) -> dict:
    packet_path, output_path, destination = (path.resolve() for path in (packet_path, output_path, destination))
    for path in [packet_path, output_path, destination]:
        path.resolve().relative_to(pages.ROOT.resolve())
    if not agent_task.startswith("/root/translate_filtered_"):
        raise ValueError("Actual authorized translation-agent task identity required")
    packet, output = json.loads(packet_path.read_text()), json.loads(output_path.read_text())
    if packet.get("work") != "pseudo_clementine_homilies" or not packet.get("authorization"):
        raise ValueError("Codex translation authorization/scope missing")
    source = load_selected(packet["work"])
    validate_output(packet, output, source["passages"] if references is None else packet["passages"])
    # Smaller independent-review batches retain the untouched full generation
    # packet and output as their actual evidence, not a synthetic API response.
    refs = packet["references"] if references is None else references
    if not refs or [ref for ref in packet["references"] if ref in refs] != refs:
        raise ValueError("Invalid or out-of-order generation subset")
    selected_output = {"passages": [row for row in output["passages"] if row["reference"] in refs]}
    selected_source = [row for row in packet["passages"] if row["reference"] in refs]
    if selected_source != [row for row in source["passages"] if row["reference"] in refs]:
        raise ValueError("Selected Codex generation subset source changed")
    record = {
        "version": 2, "kind": "codex_subagent_greek_draft", "work": packet["work"], "stage": "draft",
        "references": refs, "source_hash": tr.digest(selected_source),
        "request_hash": tr.digest(packet), "output_hash": tr.digest(selected_output), "output": selected_output,
        "model": "Codex translation subagent; exact inherited model version not exposed",
        "backend": "codex_subagent", "source_variant": "lagarde1865",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "generation_provenance": {"agent_task": agent_task, "method": "Fresh translation directly from supplied checked Greek",
            "authorization": packet["authorization"], "exact_model_version": "not_exposed",
            "output_type": "Codex-generated JSON, not an Azure API response",
            "packet_file_sha256": pages.sha(packet_path.read_bytes()),
            "output_file_sha256": pages.sha(output_path.read_bytes())},
        "evidence_files": {"request": str(packet_path.relative_to(pages.ROOT)), "response": str(output_path.relative_to(pages.ROOT))},
        "publication_status": "candidate_only_not_reviewed",
    }
    if references is not None:
        record["generation_provenance"]["full_generation_references"] = packet["references"]
        record["generation_provenance"]["full_generation_output_hash"] = tr.digest(output)
        record["generation_provenance"]["selection_method"] = "Exact unchanged passage subset for bounded independent review"
    for index, evidence in enumerate(packet.get("supplemental_evidence_files", [])):
        path = (pages.ROOT / evidence["path"]).resolve()
        path.relative_to(pages.ROOT.resolve())
        if pages.sha(path.read_bytes()) != evidence["sha256"]:
            raise ValueError("Supplemental generation evidence changed")
        record["evidence_files"][f"supplemental_{index}"] = str(path.relative_to(pages.ROOT))
    if destination.exists():
        old = json.loads(destination.read_text())
        if any(old.get(k) != v for k, v in record.items() if k != "recorded_at"):
            raise ValueError("Refusing to overwrite different Codex generation evidence")
        return old
    pages.save(destination, record)
    return record
