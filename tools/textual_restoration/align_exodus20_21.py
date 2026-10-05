#!/usr/bin/env python3
"""Metadata-only validation of a declared, lossless Exodus 20:21 SP alignment."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "exodus_alignment_pinned_reader", Path(__file__).with_name("build_samaritan_screen.py"))
BASE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)
ROOT, FROZEN = BASE.ROOT, BASE.OUT
FROZEN_SHA = "1ae6bb318ed9304e3e853322a8012023c4863fee7656cbb9fd874521540e9d8a"
SCRIPT = "tools/textual_restoration/align_exodus20_21.py"
OUT = FROZEN.with_name("exodus20_21_declared_alignment.v1.json")
TARGET = "Exod.20.21"
# Each tuple is (target start, target end, control, reference, source span).
# None denotes the whole source node with terminal spaces removed, not a search.
DECLARED = (
    (0, 46, "WLC", TARGET, None),
    (47, 69, "SP", "Exod.20.22", (0, 22)),
    (70, 127, "SP", "Deut.5.28", (51, 108)),
    (128, 213, "SP", "Deut.5.29", None),
    (214, 286, "SP", "Deut.18.18", None),
    (287, 346, "SP", "Deut.18.19", None),
    (347, 441, "SP", "Deut.18.20", None),
    (442, 490, "SP", "Deut.18.21", None),
    (491, 592, "SP", "Deut.18.22", None),
    (593, 620, "SP", "Deut.5.30", None),
    (621, 719, "SP", "Deut.5.31", None),
)


def metadata(raw: str, start: int, end: int) -> dict:
    if not 0 <= start < end <= len(raw):
        raise ValueError("invalid nonempty character span")
    value = raw[start:end]
    normalized = BASE.consonants(value)
    return {"character_span": [start, end], "raw_character_count": end - start,
            "consonant_count": len(normalized), "raw_sha256": BASE.sha(value.encode()),
            "consonants_sha256": BASE.sha(normalized.encode())}


def align(sp: dict[str, str], wlc: dict[str, str], declared=DECLARED) -> dict:
    # Declarations are a fixed human-inspected hypothesis, not discovered matches.
    if tuple(declared) != DECLARED:
        raise ValueError("declared block spans or order differ from the fixed alignment")
    if TARGET not in sp or TARGET not in wlc:
        raise ValueError("target missing from a comparison control")
    raw = sp[TARGET]
    if len(raw) != 720 or len(BASE.consonants(raw)) != 567:
        raise ValueError("target raw extent or consonantal count differs")
    if any(char != " " and not ("א" <= char <= "ת") for char in raw):
        raise ValueError("target SP alphabet differs")
    if len(BASE.consonants(wlc[TARGET])) != 37:
        raise ValueError("WLC retained-core consonantal count differs")
    blocks, partition, cursor = [], [], 0
    for number, (start, end, control, ref, declared_source_span) in enumerate(declared, 1):
        if start != cursor:
            raise ValueError("declared partition does not cover the target in order")
        if raw[start] == " " or raw[end - 1] == " ":
            raise ValueError("block extent includes an outer space")
        source = sp if control == "SP" else wlc
        if ref not in source:
            raise ValueError(f"missing declared source reference: {control} {ref}")
        source_raw = source[ref]
        source_start, source_end = declared_source_span or (0, len(source_raw.rstrip(" ")))
        target_value, source_value = raw[start:end], source_raw[source_start:source_end]
        source_meta = metadata(source_raw, source_start, source_end)
        if control == "SP":
            if target_value != source_value:
                raise ValueError(f"declared SP raw block equality failed: {ref}")
            comparison = "raw-identical"
        else:
            if BASE.consonants(target_value) != BASE.consonants(source_value):
                raise ValueError("retained WLC core consonantal equality failed")
            comparison = "written-consonants-identical"
        block_id = f"b{number:02d}"
        block = {"block_id": block_id, "target": metadata(raw, start, end),
                 "role": "retained-core" if number == 1 else "declared-added-block",
                 "source": {"control": control, "reference_label": ref, **source_meta},
                 "comparison": comparison}
        blocks.append(block)
        partition.append({"kind": "declared-block", "block_id": block_id,
                          **metadata(raw, start, end)})
        if raw[end:end + 1] != " ":
            raise ValueError("declared block must be followed by exactly one accounted space")
        partition.append({"kind": "inter-block-or-terminal-space", "block_id": None,
                          **metadata(raw, end, end + 1)})
        cursor = end + 1
    if cursor != len(raw):
        raise ValueError("declared partition leaves target characters unaccounted")
    if "".join(raw[p["character_span"][0]:p["character_span"][1]] for p in partition) != raw:
        raise ValueError("lossless target reconstruction failed")
    return {"target_reference": TARGET, "target": metadata(raw, 0, len(raw)),
            "summary": {"declared_blocks": len(blocks), "partition_parts": len(partition),
                        "raw_characters": len(raw), "consonants": len(BASE.consonants(raw)),
                        "retained_core_consonants": blocks[0]["target"]["consonant_count"],
                        "added_block_consonants": sum(b["target"]["consonant_count"] for b in blocks[1:]),
                        "accounted_spaces_outside_blocks": len(blocks),
                        "unaccounted_raw_characters": 0},
            "blocks": blocks, "partition": partition}


def build(directory: Path, root: Path = ROOT) -> dict:
    frozen_raw = (root / FROZEN.relative_to(ROOT)).read_bytes()
    if BASE.sha(frozen_raw) != FROZEN_SHA:
        raise ValueError("frozen Samaritan screen receipt hash mismatch")
    frozen = json.loads(frozen_raw)
    if BASE.build(directory, root) != frozen:
        raise ValueError("frozen Samaritan screen differs from pinned recomputation")
    sp, sp_inputs = BASE.load_sp(directory)
    wlc, wlc_inputs = BASE.load_wlc(root / "sources/ot/wlc")
    if len(sp) != 5841 or len(wlc) != 5853:
        raise ValueError("pinned comparison control extent differs")
    return {"schema_version": "1.0.0",
            "scope": "Fixed human-declared Exodus 20:21 alignment only; validation of eleven selected blocks, not exhaustive discovery or historical adjudication",
            "generator": {"repo_path": SCRIPT, "sha256": BASE.sha(Path(__file__).read_bytes()),
                          "pinned_reader_repo_path": "tools/textual_restoration/build_samaritan_screen.py",
                          "pinned_reader_sha256": BASE.sha(Path(BASE.__file__).read_bytes())},
            "source": {**frozen["source"], "sp_inputs": sp_inputs, "wlc_inputs": wlc_inputs,
                       "frozen_screen_repo_path": str(FROZEN.relative_to(ROOT)),
                       "frozen_screen_sha256": FROZEN_SHA, "frozen_screen_reproduced": True},
            "normalization": frozen["normalization"],
            "offsets": "Zero-based half-open Python character offsets; SP block endpoints omit surrounding spaces, while all eleven following spaces, including the terminal space, are separate partition parts. Partial source clauses retain explicit offsets. Full SP source nodes omit terminal spaces only.",
            "limitations": "Declared internal SP parallels validate repeated wording in one edition/transcription, not independent ancient witnesses. Full raw accounting does not establish semantic equivalence, historical direction, priority, or original wording. No manuscript pixels, retroversion, source restoration, or new ancient text is produced.",
            "policy": {"export_contains_source_text": False, "exhaustive_discovery_claimed": False,
                       "historical_selection_applied": False, "semantic_equivalence_claimed": False,
                       "canonical_change_applied": False, "new_ancient_reading_demonstrated": False,
                       "fresh_manuscript_reading": False, "publication_approved": False,
                       "generated_images_used_as_evidence": False},
            **align(sp, wlc)}


def validate_output(path: Path, directory: Path, verify_only: bool = False) -> Path:
    absolute = path.absolute()
    if any(p.is_symlink() for p in (absolute, *absolute.parents)):
        raise ValueError("output path cannot contain a symlink")
    output = absolute.resolve()
    discovery = (ROOT / "sources/textual_restoration/discovery").resolve()
    if output.suffix != ".json":
        raise ValueError("output must be a JSON metadata receipt")
    if output in {FROZEN.resolve(), BASE.INCENSE_OUT.resolve()}:
        raise ValueError("output cannot overwrite a pinned receipt")
    if ROOT.resolve() in output.parents and discovery not in output.parents:
        raise ValueError("repository output must be a metadata receipt in discovery")
    private_root = directory.resolve().parent.parent
    if output == private_root or private_root in output.parents:
        raise ValueError("output cannot be inside the private SP dataset")
    if output.exists():
        try:
            saved = json.loads(output.read_text())
        except (ValueError, UnicodeError, OSError) as error:
            raise ValueError("existing output is not an alignment receipt") from error
        if not isinstance(saved, dict) or saved.get("generator", {}).get("repo_path") != SCRIPT:
            raise ValueError("output cannot overwrite an unrelated receipt")
    elif verify_only:
        raise ValueError("saved receipt absent; verify-only never writes")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sp_tf_directory", type=Path)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    try:
        output = validate_output(args.output, args.sp_tf_directory, args.verify_only)
    except ValueError as error:
        parser.error(str(error))
    result = build(args.sp_tf_directory)
    if args.verify_only:
        if json.loads(output.read_text()) != result:
            raise SystemExit("Saved declared alignment differs from pinned recomputation")
        print(f"Verified {output.name} against pinned inputs and the frozen screen")
    else:
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
