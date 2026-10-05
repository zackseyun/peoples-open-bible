#!/usr/bin/env python3
"""Reproducible mechanical queue, not a semantic or source-priority decision."""
import argparse
from collections import Counter
import json
from pathlib import Path
import unicodedata

from tools.textual_restoration import compare_uxlc_wlc as screen

ROOT = screen.ROOT
OUTPUT = screen.DIR / "uxlc_pointing_triage.2026-10-05.v1.json"
SCREEN_SHA256 = "f893ce50894b4f6890e218a3bd1ea44c3166e44abe4efba59e6d9fba66dca4e6"
METHOD = ROOT / "docs/TEXTUAL_ADJUDICATION_METHOD.md"
CATEGORIES = (
    "token_alignment_hold", "qere_involved_hold", "dagesh_rafe_only",
    "shin_sin_dots_only", "other_pointing",
)


def without(text, marks):
    return unicodedata.normalize("NFD", "".join(c for c in text if c not in marks))


def classify(row):
    if row["written_difference"] != "pointing":
        raise ValueError("not a pointing row")
    if screen.comparison(row["wlc"], row["uxlc"])["written_difference"] != "pointing":
        raise ValueError("pointing classification drift")
    a, b = row["wlc"]["written"], row["uxlc"]["written"]
    aligned = len(a) == len(b) and all(
        screen.normalized(x["text"], "consonants") == screen.normalized(y["text"], "consonants")
        for x, y in zip(a, b)
    )
    pairs = []
    if aligned:
        for index, (x, y) in enumerate(zip(a, b), 1):
            old, new = (screen.normalized(w["text"], "pointing") for w in (x, y))
            if old != new:
                pairs.append({"written_word_number": index,
                              "wlc_position": x["position"], "uxlc_position": y["position"],
                              "wlc_raw": x["text"], "uxlc_raw": y["text"],
                              "wlc_pointing": old, "uxlc_pointing": new})
        if not pairs:
            raise ValueError("pointing row without changed aligned words")
    qere = bool(row["wlc"]["qere"] or row["uxlc"]["qere"])

    def only(marks):
        return all(without(p["wlc_pointing"], marks) == without(p["uxlc_pointing"], marks)
                   for p in pairs)

    if not aligned:
        category = "token_alignment_hold"
    elif qere:
        category = "qere_involved_hold"
    elif only("\u05bc\u05bf"):
        category = "dagesh_rafe_only"
    elif only("\u05c1\u05c2"):
        category = "shin_sin_dots_only"
    else:
        category = "other_pointing"
    return {"book": row["book"], "chapter": row["chapter"], "verse": row["verse"],
            "category": category, "token_alignment_verified": aligned,
            "contains_qere": qere,
            # Chapter context is a navigation flag, not a decision about a verse's points.
            "decalogue_chapter_context": (row["book"], row["chapter"]) in
                                          (("exodus", 20), ("deuteronomy", 5)),
            "changed_written_words": pairs, "semantic_review": "not_adjudicated"}


def load_screen():
    raw = screen.OUTPUT.read_bytes()
    if screen.digest(raw) != SCREEN_SHA256:
        raise ValueError("frozen screen pin mismatch")
    frozen = json.loads(raw)
    required = [screen.PROTOCOL, screen.BOOKMAP, Path(screen.__file__)]
    required += [ROOT / p for p in frozen["inputs"] if p.startswith("sources/ot/wlc/")]
    if len(required) != 42:
        raise ValueError("expected 39 WLC books and three screen controls")
    for path in required:
        rel = str(path.relative_to(ROOT))
        if screen.digest(path.read_bytes()) != frozen["inputs"][rel]:
            raise ValueError("screen input drift: " + rel)
    seen = set()
    for row in frozen["differences"]:
        key = row["book"], row["chapter"], row["verse"]
        if key in seen:
            raise ValueError("duplicate frozen verse label")
        seen.add(key)
        for flag, actual in screen.comparison(row["wlc"], row["uxlc"]).items():
            if actual != row[flag]:
                raise ValueError("frozen flag drift: " + str(key))
    return frozen, required


def verify_archive(archive, frozen):
    rebuilt = screen.build(archive)
    # Current canonical joins are intentionally outside this historical RAW-input check.
    # Their preserved historical pins are not rewritten or represented as current approval.
    for key in ("protocol", "archive_members", "summary", "books", "unmatched_labels", "differences"):
        if rebuilt[key] != frozen[key]:
            raise ValueError("raw archive reproduction drift: " + key)


def build():
    frozen, required = load_screen()
    rows = [classify(r) for r in frozen["differences"] if r["written_difference"] == "pointing"]
    if len(rows) != 374 or len(rows) != frozen["summary"]["counts"]["pointing"]:
        raise ValueError("pointing denominator drift")
    counts = Counter(r["category"] for r in rows)
    flags = Counter()
    for row in rows:
        flags["aligned_changed_written_words"] += len(row["changed_written_words"])
        flags["decalogue_chapter_rows"] += row["decalogue_chapter_context"]
    required += [screen.OUTPUT, Path(__file__).resolve(), METHOD]
    return {
        "schema_version": "1.0.0", "checked_date": "2026-10-05",
        "scope": "All 374 pointing-first verse rows in the pinned two-input OT screen; not all manuscripts or semantic errors.",
        "design": "Post-hoc operational triage after exploratory inspection, not a predeclared blind experiment or improvement-rate sample.",
        "inputs": {str(p.relative_to(ROOT)): screen.digest(p.read_bytes()) for p in required},
        "rules_in_order": [
            "Unequal written-word counts or consonants per paired word: no token alignment inferred.",
            "Any qere in either verse: qere-involved hold, even if the changed word itself is not qere.",
            "Every changed aligned word equals after removing only dagesh U+05BC and rafe U+05BF.",
            "Every changed aligned word equals after removing only shin/sin dots U+05C1/U+05C2.",
            "All remaining aligned, qere-free pointing rows.",
        ],
        "summary": {"verse_rows": len(rows), "categories": {k: counts[k] for k in CATEGORIES},
                    "nonexclusive_diagnostics": dict(flags),
                    "by_book": dict(sorted(Counter(r["book"] for r in rows).items()))},
        "rows": rows,
        "limits": [
            "Every category still requires semantic review; dagesh can distinguish morphology and shin/sin dots can distinguish lexemes.",
            "The Decalogue chapter flag is navigation only; it excludes no row and proves no convention-specific explanation.",
            "Qere presence is not equivalent to all differences being qere conventions.",
            "Written word numbers count direct written words, not XML child positions or independent manuscript witnesses.",
            "No canonical source, English, note, historical priority, restored ink or publication approval follows from this queue.",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="Also reproduce all raw screen rows from the pinned ZIP.")
    parser.add_argument("--write", action="store_true", help="Create a new receipt; never overwrite an existing one.")
    args = parser.parse_args()
    if args.archive:
        frozen, _ = load_screen()
        verify_archive(args.archive, frozen)
    result = build()
    if args.write:
        with OUTPUT.open("x") as out:
            out.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    elif result != json.loads(OUTPUT.read_text()):
        raise ValueError("saved triage drift")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
