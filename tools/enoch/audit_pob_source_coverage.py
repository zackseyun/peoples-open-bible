#!/usr/bin/env python3
"""Read-only 1 Enoch POB inventory and source-alignment audit.

The expected verse numbers below follow the recovered Charles 1906 primary
witness, with the documented editorial boundary at 6:8. In particular chapter
20 has seven units in this witness, not the eight in Charles's later English
edition. English wording is never used as POB source text. The primary
Geʿez comparison uses separately paired-reviewed source inputs for registered
complete chapters, otherwise recovered Charles1906 OCR with cross-page
continuations. Reviewed inputs are never read from canonical verse outputs.
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
    # Paired scan-boundary inventories, PDF pp.113-118 / printed75-80.
    # Exact sources and assessments: enoch_full_repair_batch02_20261020.
    36: 4, 37: 5, 38: 6, 39: 14,
    # Actual PDF118-122 boundaries counted by author and separate reader.
    # Complete40 and only named41/42/43 units have wording acceptance; holds remain.
    40: 10, 41: 9, 42: 3, 43: 4,
    # Charles 1906 printed p. 86 / PDF p. 124 labels XLV.6, then XLVI;
    # the Geʿez parser recovers the sixth unit across its OCR-file boundary.
    # This is a count boundary only, not approval of 45:6's wording.
    45: 6,
    # Paired full selected-edition reviews; no47/48 release count inferred.
    46: 8, 49: 4,
    # Full paired source/count reviews, PDF130-132 and165-166.
    50: 5, 51: 5, 70: 4,
    # Allthree57units source/English/explanations independently accepted inbatch08.
    # Pure52–56 structural counts remain separate; held neighbors not released.
    57: 3,
    # Allsix58 units have exact paired selected-edition review inbatch09.
    # Pure59–64 structural counts do not release held neighbors.
    58: 6,
    # Paired79/80 source/count observations;80:5 remains held and8 deferred.
    79: 6, 80: 8,
    # Whole83 accepted scan markers1-11, including4/11 continuations.
    # sources/textual_restoration/applications/enoch_83_20261013/
    83: 11,
    # Charles 1906 printed pp. 161-163 / PDF 199-201 explicitly numbers
    # LXXXIV.1-6, then LXXXV. The count is independent of the unresolved
    # royal noun and throne-location readings in 84:2-3.
    84: 6,
    # Charles 1906 printed p. 203 / PDF p. 241 labels XCVII.10, then
    # XCVIII; OCR recovers the tenth unit across the ch98 file boundary.
    # This certifies the count, not the unapproved wording of 97:10.
    97: 10,
    # Actual CIV/CV/CVI boundaries on printed216-219 / PDF254-257.
    # Old105:1 continued104:1, and old105:2-11 were104:2-11.
    # Paired full selected-edition repair: enoch_full_repair_batch03_20261020.
    104: 13, 105: 2,
    # Actual CVII.1-3, PDF260-261; 1 continues across the page.
    107: 3,
}


def audit(chapters: list[int], pob_root: Path = POB_ROOT, *,
          diagnostic_counts: dict[int, int] | None = None) -> dict:
    # Optional read-only observations do not mutate reader/export release counts.
    diagnostic_counts = diagnostic_counts or {}
    counts = {**EXPECTED_VERSES, **diagnostic_counts}
    rows = []
    for chapter in chapters:
        source_rows, source_warnings = verse_parser.parse_chapter(chapter)
        source_by_verse = {row.verse: row for row in source_rows}
        verified_inventory = chapter in counts
        expected = counts.get(chapter, max(source_by_verse, default=0))
        present = sorted(int(path.stem) for path in (pob_root / f"{chapter:03d}").glob("[0-9][0-9][0-9].yaml"))
        missing = sorted(set(range(1, expected + 1)) - set(present))
        unexpected = sorted(set(present) - set(range(1, expected + 1)))
        primary_missing = sorted(set(range(1, expected + 1)) - set(source_by_verse))
        primary_unexpected = sorted(set(source_by_verse) - set(range(1, expected + 1)))
        empty_translation = []
        source_review = []
        for verse in present:
            record = yaml.safe_load((pob_root / f"{chapter:03d}/{verse:03d}.yaml").read_text())
            if not str((record.get("translation") or {}).get("text") or "").strip():
                empty_translation.append(verse)
            recovered = source_by_verse.get(verse)
            if recovered is None:
                source_review.append(f"{chapter}:{verse}: no primary Geʿez row")
                continue
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
            "expected_count_basis": ("separately_paired_structural_count" if chapter in diagnostic_counts else
                                     "declared_primary_inventory" if verified_inventory else
                                     "unverified_recovered_primary_maximum"),
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
            "translation_verified_by_this_audit": False,
            "existing_source_review": source_review,
            "primary_source_warnings": source_warnings,
        })
    return {
        "scope": "Source inventory and review signals only, not wording or reader-release approval. Explicit declared or separately paired counts are distinguished from unverified parser maxima in each row.",
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
    from tools.enoch.structural_counts import load_inventories
    result = audit(chapters, diagnostic_counts={c: len(v['units']) for c, v in load_inventories().items()})
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.require_complete and result["incomplete_chapters"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
