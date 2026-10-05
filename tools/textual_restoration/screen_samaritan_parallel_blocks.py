#!/usr/bin/env python3
"""Metadata-only exact full-verse discovery within the frozen 20 SP leads."""
from __future__ import annotations

import argparse
from collections import defaultdict
import importlib.util
import json
from pathlib import Path

# Load the existing pinned reader without changing its inputs or behavior.
SPEC = importlib.util.spec_from_file_location(
    "samaritan_screen_pinned", Path(__file__).with_name("build_samaritan_screen.py"))
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)
load_sp, load_wlc = BASE.load_sp, BASE.load_wlc
consonants, ref_key, sha = BASE.consonants, BASE.ref_key, BASE.sha
ROOT = BASE.ROOT
FROZEN = BASE.OUT
FROZEN_SHA = "1ae6bb318ed9304e3e853322a8012023c4863fee7656cbb9fd874521540e9d8a"
OUT = FROZEN.with_name("samaritan_parallel_blocks.v1.json")


def span_metadata(text: str, start: int, end: int) -> dict:
    raw = text[start:end]
    normalized = consonants(raw)
    return {"sp_character_span": [start, end], "raw_character_count": end - start,
            "consonant_count": len(normalized), "raw_sha256": sha(raw.encode()),
            "consonants_sha256": sha(normalized.encode())}


def source_index(verses: dict[str, str], control: str) -> dict[str, list[dict]]:
    index = defaultdict(list)
    for ref in sorted(verses, key=ref_key):
        raw = verses[ref]
        key = consonants(raw)
        if not key:
            raise ValueError(f"empty {control} consonantal verse: {ref}")
        index[key].append({"control": control, "reference_label": ref,
                           "source_character_span": [0, len(raw)],
                           "raw_character_count": len(raw), "consonant_count": len(key),
                           "raw_sha256": sha(raw.encode()),
                           "consonants_sha256": sha(key.encode())})
    return dict(index)


def wlc_index(wlc: dict[str, str]) -> dict[str, list[dict]]:
    return source_index(wlc, "WLC")


def discover_node(ref: str, text: str, index: dict[str, list[dict]]) -> dict:
    # The pinned SP sign reader admits only Hebrew letters and literal spaces.
    # Keep a raw offset for every normalized letter; never infer a word start
    # from the stripped stream, where within-word false hits would be possible.
    if any(char != " " and not ("א" <= char <= "ת") for char in text):
        raise ValueError(f"unexpected SP raw alphabet: {ref}")
    offsets = [i for i, char in enumerate(text) if char != " "]
    normalized = consonants(text)
    grouped = defaultdict(list)
    for key, alternatives in index.items():
        alternatives = [a for a in alternatives
                        if not (a["control"] == "SP" and a["reference_label"] == ref)]
        if not alternatives:
            continue
        cursor = 0
        while (position := normalized.find(key, cursor)) != -1:
            cursor = position + 1  # Retain overlapping and repeated occurrences.
            start, end = offsets[position], offsets[position + len(key) - 1] + 1
            if (start == 0 or text[start - 1] == " ") and (end == len(text) or text[end] == " "):
                grouped[(start, end)].extend(alternatives)
    candidates = []
    for number, ((start, end), alternatives) in enumerate(sorted(grouped.items()), 1):
        candidates.append({"candidate_id": f"m{number:03d}",
                           **span_metadata(text, start, end),
                           "parallel_reference_candidates": sorted(alternatives, key=lambda r: (r["control"], ref_key(r["reference_label"])))})
    # A disjoint, lossless partition describes coverage without choosing a
    # preferred candidate. Repeated reference alternatives remain in each ID.
    boundaries = sorted({0, len(text)} | {p for c in candidates for p in c["sp_character_span"]})
    partition = []
    for start, end in zip(boundaries, boundaries[1:]):
        active = [c["candidate_id"] for c in candidates
                  if c["sp_character_span"][0] <= start and end <= c["sp_character_span"][1]]
        partition.append({**span_metadata(text, start, end),
                          "coverage": "overlapping" if len(active) > 1 else "matched" if active else "unmatched",
                          "candidate_ids": active})
    assert sum(p["raw_character_count"] for p in partition) == len(text)
    assert sum(p["consonant_count"] for p in partition) == len(normalized)
    return {"sp_reference": ref, **span_metadata(text, 0, len(text)),
            "candidate_spans": candidates, "partition": partition}


def discover(sp: dict[str, str], wlc: dict[str, str], leads: list[dict]) -> list[dict]:
    refs = [lead["reference_label"] for lead in leads]
    if len(refs) != 20 or len(set(refs)) != 20:
        raise ValueError("frozen selection must contain exactly 20 distinct SP leads")
    if any(ref not in sp for ref in refs):
        raise ValueError("frozen SP lead absent from pinned source")
    index = wlc_index(wlc)
    for key, alternatives in source_index(sp, "SP").items():
        index.setdefault(key, []).extend(alternatives)
    return [discover_node(ref, sp[ref], index) for ref in refs]


def build(directory: Path, root: Path = ROOT) -> dict:
    frozen_path = root / FROZEN.relative_to(ROOT)
    frozen_raw = frozen_path.read_bytes()
    if sha(frozen_raw) != FROZEN_SHA:
        raise ValueError("frozen Samaritan screen receipt hash mismatch")
    frozen = json.loads(frozen_raw)
    if BASE.build(directory, root) != frozen:
        raise ValueError("frozen Samaritan screen differs from pinned recomputation")
    sp, sp_inputs = load_sp(directory)
    wlc, wlc_inputs = load_wlc(root / "sources/ot/wlc")
    if len(wlc) != 5853:
        raise ValueError("expected all 5853 WLC Torah verses")
    if len(sp) != 5841:
        raise ValueError("expected all 5841 SP verse nodes")
    nodes = discover(sp, wlc, frozen["largest_length_difference_leads"])
    spans = [c for node in nodes for c in node["candidate_spans"]]
    partition = [p for node in nodes for p in node["partition"]]
    return {
        "schema_version": "1.0.0",
        "scope": "All 20 frozen largest absolute length-difference SP leads; exact full-verse consonantal discovery against all 5853 WLC Torah verses and all 5841 SP verse nodes, excluding each target SP node from its own candidates",
        "generator": {"repo_path": "tools/textual_restoration/screen_samaritan_parallel_blocks.py",
                      "sha256": sha(Path(__file__).read_bytes()),
                      "pinned_reader_repo_path": "tools/textual_restoration/build_samaritan_screen.py",
                      "pinned_reader_sha256": sha(Path(BASE.__file__).read_bytes())},
        "source": {**frozen["source"], "sp_inputs": sp_inputs, "wlc_inputs": wlc_inputs,
                   "frozen_screen_repo_path": str(FROZEN.relative_to(ROOT)),
                   "frozen_screen_sha256": FROZEN_SHA,
                   "frozen_screen_reproduced": True},
        "lead_selection": frozen["lead_selection"],
        "normalization": frozen["normalization"],
        "matching": "Every full WLC written verse and full other SP node normalized to consonants is searched at every target SP occurrence across all five books. Each target SP node is excluded as its own source candidate. SP endpoints must be raw whole-word boundaries; internal word division is ignored. Identical spans retain all control/reference alternatives; repeated occurrences and overlapping spans are retained. No minimum length or ranking is applied.",
        "offsets": "Zero-based half-open Python character offsets in the raw SP sign text. Candidate spans exclude surrounding spaces; the disjoint partition retains every character, including leading, internal, and trailing spaces. Partition candidate_ids identify all covering spans and their control/reference alternatives. Source spans and raw hashes describe entire source verses/nodes, including SP trailing spaces.",
        "limitations": "Exact conservative discovery, not exhaustive alignment. Orthographic differences, partial-verse parallels and nonidentical wording are not found. SP intra-control parallels are internal verbal repetitions, not independent manuscript evidence. Generic short full-verse repetitions do not establish independent origin, alignment, historical priority or semantic equivalence. Unmatched spans are not evidence of unique origin.",
        "policy": {"canonical_change_applied": False, "export_contains_source_text": False,
                   "historical_selection_applied": False, "semantic_equivalence_claimed": False,
                   "automatic_greedy_selection_applied": False, "exhaustive_alignment_claimed": False},
        "summary": {"selected_sp_nodes": len(nodes), "searched_wlc_verses": len(wlc),
                    "searched_sp_nodes": len(sp), "eligible_sp_nodes_per_target": len(sp) - 1,
                    "nodes_with_candidates": sum(bool(n["candidate_spans"]) for n in nodes),
                    "candidate_spans": len(spans),
                    "reference_alternatives": sum(len(c["parallel_reference_candidates"]) for c in spans),
                    "by_control": {control: {
                        "nodes_with_candidates": sum(any(any(a["control"] == control for a in c["parallel_reference_candidates"]) for c in n["candidate_spans"]) for n in nodes),
                        "candidate_spans": sum(any(a["control"] == control for a in c["parallel_reference_candidates"]) for c in spans),
                        "reference_alternatives": sum(a["control"] == control for c in spans for a in c["parallel_reference_candidates"])}
                        for control in ("WLC", "SP")},
                    "sp_raw_characters": sum(n["raw_character_count"] for n in nodes),
                    "sp_consonants": sum(n["consonant_count"] for n in nodes),
                    "matched_raw_characters": sum(p["raw_character_count"] for p in partition if p["candidate_ids"]),
                    "unmatched_raw_characters": sum(p["raw_character_count"] for p in partition if not p["candidate_ids"]),
                    "matched_consonants": sum(p["consonant_count"] for p in partition if p["candidate_ids"]),
                    "unmatched_consonants": sum(p["consonant_count"] for p in partition if not p["candidate_ids"]),
                    "overlapping_partition_spans": sum(p["coverage"] == "overlapping" for p in partition)},
        "nodes": nodes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sp_tf_directory", type=Path)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    # Refuse destinations in the source corpus or pinned receipts.
    discovery = (ROOT / "sources/textual_restoration/discovery").resolve()
    output = args.output.resolve()
    if output == FROZEN.resolve() or output == BASE.INCENSE_OUT.resolve():
        parser.error("output cannot overwrite an existing pinned receipt")
    if ROOT.resolve() in output.parents and discovery not in output.parents:
        parser.error("repository output must be a new metadata receipt in the discovery directory")
    if args.sp_tf_directory.resolve().parent.parent in output.parents:
        parser.error("output cannot be inside the private SP dataset")
    if output.exists() and not args.verify_only:
        try:
            saved = json.loads(output.read_text())
        except (ValueError, UnicodeError):
            parser.error("output would overwrite a file that is not a parallel discovery receipt")
        if not isinstance(saved, dict) or saved.get("generator", {}).get("repo_path") != "tools/textual_restoration/screen_samaritan_parallel_blocks.py":
            parser.error("output would overwrite an unrelated receipt")
    result = build(args.sp_tf_directory)
    if args.verify_only:
        if json.loads(output.read_text()) != result:
            raise SystemExit("Saved parallel-block discovery differs from recomputation")
        print(f"Verified {output.name} against pinned inputs and the frozen screen")
    else:
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
