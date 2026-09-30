#!/usr/bin/env python3
"""Read-only 1 Enoch POB inventory and source-alignment audit.

The expected verse numbers below follow Charles 1917's public-domain
versification; English wording is never used as POB source text. The primary
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
}


def audit(chapters: list[int], pob_root: Path = POB_ROOT) -> dict:
    rows = []
    for chapter in chapters:
        expected = EXPECTED_VERSES[chapter]
        source_rows, source_warnings = verse_parser.parse_chapter(chapter)
        source_by_verse = {row.verse: row for row in source_rows}
        present = sorted(int(path.stem) for path in (pob_root / f"{chapter:03d}").glob("[0-9][0-9][0-9].yaml"))
        missing = sorted(set(range(1, expected + 1)) - set(present))
        source_review = []
        for verse in present:
            recovered = source_by_verse.get(verse)
            if recovered is None:
                source_review.append(f"{chapter}:{verse}: no primary Geʿez row")
                continue
            record = yaml.safe_load((pob_root / f"{chapter:03d}/{verse:03d}.yaml").read_text())
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
            "primary_source_verses": len(source_rows),
            "pob_verses": len(present),
            "missing_verse_numbers": missing,
            "existing_source_review": source_review,
            "primary_source_warnings": source_warnings,
        })
    return {
        "scope": "source inventory and review signals only; not translation approval",
        "chapters": rows,
        "missing_verse_total": sum(len(row["missing_verse_numbers"]) for row in rows),
        "source_review_total": sum(len(row["existing_source_review"]) for row in rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapters", default="1-17", help="Inclusive range, e.g. 6-17")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    start, end = map(int, args.chapters.split("-", 1))
    chapters = list(range(start, end + 1))
    if not chapters or any(chapter not in EXPECTED_VERSES for chapter in chapters):
        parser.error("The audited versification currently covers chapters 1-17")
    result = audit(chapters)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.require_complete and (result["missing_verse_total"] or result["source_review_total"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
