#!/usr/bin/env python3
"""Read-only 1 Enoch POB inventory and source-alignment audit.

The expected verse numbers below follow the recovered Charles 1906 primary
witness, with the documented editorial boundary at 6:8. In particular chapter
20 has seven units in this witness, not the eight in Charles's later English
edition. English wording is never used as POB source text. The primary
Geʿez comparison is the recovered Charles 1906 OCR, including cross-page
continuations from ``verse_parser``.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

try:
    from . import verse_parser
except ImportError:
    import verse_parser  # type: ignore


REPO_ROOT = Path(__file__).resolve().parents[2]
POB_ROOT = REPO_ROOT / "translation/extra_canonical/1_enoch"
EXPECTED_VERSES = {
    1: 9, 2: 3, 3: 1, 4: 1, 5: 9, 6: 8, 7: 6, 8: 4, 9: 11,
    10: 22, 11: 2, 12: 6, 13: 10, 14: 25, 15: 12, 16: 4, 17: 8,
    18: 16, 19: 3, 20: 7, 21: 10, 22: 14, 23: 4, 24: 6, 25: 7,
    26: 6, 27: 5, 28: 3, 29: 2, 30: 3, 31: 3, 32: 6, 33: 4,
    34: 3, 35: 1,
}


def audit(chapters: list[int], pob_root: Path = POB_ROOT) -> dict:
    rows = []
    for chapter in chapters:
        source_rows, source_warnings = verse_parser.parse_chapter(chapter)
        source_by_verse = {row.verse: row for row in source_rows}
        verified_inventory = chapter in EXPECTED_VERSES
        expected = EXPECTED_VERSES.get(chapter, max(source_by_verse, default=0))
        present = sorted(int(path.stem) for path in (pob_root / f"{chapter:03d}").glob("[0-9][0-9][0-9].yaml"))
        missing = sorted(set(range(1, expected + 1)) - set(present))
        unexpected = sorted(set(present) - set(range(1, expected + 1)))
        primary_missing = sorted(set(range(1, expected + 1)) - set(source_by_verse))
        primary_unexpected = sorted(set(source_by_verse) - set(range(1, expected + 1)))
        empty_translation = []
        source_review = []
        for verse in present:
            recovered = source_by_verse.get(verse)
            if recovered is None:
                source_review.append(f"{chapter}:{verse}: no primary Geʿez row")
                continue
            record = yaml.safe_load((pob_root / f"{chapter:03d}/{verse:03d}.yaml").read_text())
            if not str(record.get("translation", {}).get("text", "")).strip():
                empty_translation.append(verse)
            saved = str(record.get("source", {}).get("text", "")).strip()
            current = recovered.text.strip()
            # This is a conservative signal for editorial review, not an
            # automated declaration that every textual variant is an error.
            if len(current) - len(saved) > 5 or len(saved) - len(current) > 30:
                source_review.append(f"{chapter}:{verse}: source length differs ({len(saved)} -> {len(current)})")
            elif saved and not saved.endswith(("።", "፡፡", ".")) and current.endswith(("።", "፡፡", ".")) and saved != current:
                source_review.append(f"{chapter}:{verse}: saved source may stop mid-sentence")
        rows.append({
            "chapter": chapter,
            "expected_verses": expected,
            "expected_count_basis": "declared_primary_inventory" if verified_inventory else "unverified_recovered_primary_maximum",
            "versification_inventory_declared": verified_inventory,
            "primary_source_verses": len(source_rows),
            "pob_verses": len(present),
            "missing_verse_numbers": missing,
            "unexpected_verse_numbers": unexpected,
            "primary_missing_verse_numbers": primary_missing,
            "primary_unexpected_verse_numbers": primary_unexpected,
            "empty_translation_verse_numbers": empty_translation,
            "inventory_complete": verified_inventory and not (missing or unexpected or primary_missing
                                       or primary_unexpected or empty_translation or source_review),
            "existing_source_review": source_review,
            "primary_source_warnings": source_warnings,
        })
    return {
        "scope": "source inventory and review signals only; not translation approval. Counts beyond 35 are primary-parser leads, not a certified versification inventory.",
        "chapters": rows,
        "missing_verse_total": sum(len(row["missing_verse_numbers"]) for row in rows),
        "source_review_total": sum(len(row["existing_source_review"]) for row in rows),
        "incomplete_chapters": [row["chapter"] for row in rows if not row["inventory_complete"]],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapters", default="1-35", help="Inclusive range, e.g. 6-17")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    start, end = map(int, args.chapters.split("-", 1))
    chapters = list(range(start, end + 1))
    if not chapters or any(not 1 <= chapter <= 108 for chapter in chapters):
        parser.error("Chapter range must be within 1-108")
    result = audit(chapters)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.require_complete and result["incomplete_chapters"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
