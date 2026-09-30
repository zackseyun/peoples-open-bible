#!/usr/bin/env python3
"""Draft replacements for clipped 1 Enoch verses without overwriting POB.

Every candidate is written to an external review directory with the original
YAML digest. An editor must compare the new source and English, archive stale
review metadata, and use the normal source/release workflow before publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml

try:
    from . import draft_enoch
except ImportError:
    import draft_enoch  # type: ignore


def parse_refs(spec: str) -> list[tuple[int, int]]:
    refs = []
    for part in spec.split(","):
        chapter, verse = map(int, part.strip().split(":", 1))
        if not (1 <= chapter <= 108 and verse >= 1):
            raise ValueError(f"Invalid 1 Enoch reference: {part}")
        if (chapter, verse) not in refs:
            refs.append((chapter, verse))
    return refs


def draft_candidates(refs: list[tuple[int, int]], output_root: Path,
                     *, backend: str, model: str) -> dict:
    output_root.mkdir(parents=True, exist_ok=True)
    manifest_path = output_root / "manifest.json"
    completed = json.loads(manifest_path.read_text()).get("rows", []) if manifest_path.exists() else []
    for chapter, verse in refs:
        original = draft_enoch.output_path_for_verse(chapter, verse)
        if not original.is_file():
            raise FileNotFoundError(f"Only existing verse corrections belong here: {original}")
        original_bytes = original.read_bytes()
        original_sha = hashlib.sha256(original_bytes).hexdigest()
        candidate = output_root / f"{chapter:03d}-{verse:03d}.yaml"
        previous = next((row for row in completed if row["reference"] == f"1 Enoch {chapter}:{verse}"), None)
        if previous:
            if previous["original_sha256"] != original_sha or not candidate.is_file() or \
                    hashlib.sha256(candidate.read_bytes()).hexdigest() != previous["candidate_sha256"]:
                raise RuntimeError(f"Stored candidate/source changed for {chapter}:{verse}")
            print(f"skip verified candidate {chapter}:{verse}", flush=True)
            continue
        if candidate.exists():
            raise FileExistsError(f"Unrecorded candidate already exists: {candidate}")
        result = draft_enoch.draft_verse(
            chapter, verse, backend=backend, model=model, write=False,
        )
        if original.read_bytes() != original_bytes:
            raise RuntimeError(f"Concurrent source change while drafting {chapter}:{verse}")
        candidate.write_text(yaml.safe_dump(
            result.record, sort_keys=False, allow_unicode=True,
        ))
        completed.append({
            "reference": f"1 Enoch {chapter}:{verse}",
            "original_path": str(original),
            "original_sha256": original_sha,
            "candidate_path": str(candidate),
            "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
            "prompt_sha256": result.prompt_sha256,
            "model_version": result.model_version,
        })
        print(f"drafted {chapter}:{verse} -> {candidate}", flush=True)
        manifest = {"scope": "review candidates only; no POB files changed", "rows": completed}
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    manifest = {"scope": "review candidates only; no POB files changed", "rows": completed}
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refs", required=True, help="Comma-separated C:V references")
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--backend", default="codex-cli")
    parser.add_argument("--model", default="gpt-6-sol")
    args = parser.parse_args()
    manifest = draft_candidates(parse_refs(args.refs), args.output_root,
                                backend=args.backend, model=args.model)
    print(f"Drafted {len(manifest['rows'])} review candidates; canonical source unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
