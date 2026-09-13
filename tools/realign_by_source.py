#!/usr/bin/env python3
"""realign_by_source.py — find and repair verse records filed at the wrong reference.

Some derived-edition records were drafted against the wrong verse: the record at
`<book>/<chapter>/<verse>.yaml` carries the *neighbouring* verse's source text,
and its rendering is a translation of that neighbour. The reader then sees one
verse twice and never sees another.

The record's own `source.text` is the evidence of which verse it actually
translates, so a chapter can be re-keyed from it: match each record's source
against the English record that carries the same source, and that English path
is where the record's content belongs.

This is deliberately conservative. `--apply` refuses any chapter whose mapping
is not a clean permutation — a collision (two records claiming one reference) or
a gap (a reference no record claims) means content is missing or duplicated, and
that needs a human, not a shuffle.

    # what is misfiled, and which chapters could be repaired safely
    python3 tools/realign_by_source.py report --edition translation_ko --book ot/psalms

    # show the exact moves for one chapter
    python3 tools/realign_by_source.py plan --edition translation_ko --book ot/psalms --chapter 084

    # perform them (clean permutations only)
    python3 tools/realign_by_source.py apply --edition translation_ko --book ot/psalms --chapter 084
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
HEBREW_ONLY = re.compile(r"[^א-ת]")
GREEK_ONLY = re.compile(r"[^Ͱ-Ͽἀ-῿]")


def normalize_source(text: str) -> str:
    """Consonantal skeleton: drops vowel points, cantillation, and word dividers.

    Those differ between editions for the same verse, so comparing raw source
    strings produces false mismatches.
    """
    if not text:
        return ""
    stripped = HEBREW_ONLY.sub("", text)
    if stripped:
        return stripped
    return GREEK_ONLY.sub("", text)


def load(path: pathlib.Path) -> dict | None:
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return doc if isinstance(doc, dict) else None


def source_of(doc: dict) -> str:
    return normalize_source(((doc.get("source") or {}).get("text") or ""))


def chapter_of(path: pathlib.Path) -> str:
    return path.parent.name


def build_index(book_root: pathlib.Path) -> dict[str, list[pathlib.Path]]:
    index: dict[str, list[pathlib.Path]] = collections.defaultdict(list)
    for path in sorted(book_root.rglob("*.yaml")):
        doc = load(path)
        if not doc:
            continue
        src = source_of(doc)
        if src:
            index[src].append(path)
    return index


def analyse(edition: str, book: str) -> dict:
    en_root = REPO_ROOT / "translation" / book
    ed_root = REPO_ROOT / edition / book
    en_index = build_index(en_root)
    moves: list[tuple[pathlib.Path, pathlib.Path]] = []
    stayed = 0
    unmatched: list[pathlib.Path] = []
    ambiguous: list[pathlib.Path] = []

    for path in sorted(ed_root.rglob("*.yaml")):
        doc = load(path)
        if not doc:
            continue
        src = source_of(doc)
        if not src:
            continue
        candidates = en_index.get(src) or []
        if not candidates:
            unmatched.append(path)
            continue
        if len(candidates) > 1:
            ambiguous.append(path)
            continue
        target_rel = candidates[0].relative_to(REPO_ROOT / "translation")
        own_rel = path.relative_to(REPO_ROOT / edition)
        if str(target_rel) == str(own_rel):
            stayed += 1
        else:
            moves.append((path, REPO_ROOT / edition / target_rel))
    return {
        "moves": moves,
        "stayed": stayed,
        "unmatched": unmatched,
        "ambiguous": ambiguous,
    }


def chapter_permutations(moves: list[tuple[pathlib.Path, pathlib.Path]]) -> dict[str, dict]:
    by_chapter: dict[str, dict] = collections.defaultdict(
        lambda: {"moves": [], "targets": collections.Counter(), "cross_chapter": 0}
    )
    for src, dst in moves:
        ch = chapter_of(src)
        entry = by_chapter[ch]
        entry["moves"].append((src, dst))
        entry["targets"][str(dst)] += 1
        if chapter_of(dst) != ch:
            entry["cross_chapter"] += 1
    return by_chapter


def is_clean(chapter: str, entry: dict, all_sources: set[str]) -> tuple[bool, str]:
    dupes = [t for t, n in entry["targets"].items() if n > 1]
    if dupes:
        return False, f"{len(dupes)} target(s) claimed by more than one record"
    if entry["cross_chapter"]:
        return False, f"{entry['cross_chapter']} move(s) cross a chapter boundary"
    # every vacated reference must be re-filled by some move in this chapter
    vacated = {str(s) for s, _ in entry["moves"]}
    filled = {str(d) for _, d in entry["moves"]}
    orphaned = vacated - filled
    incoming_new = filled - vacated
    if orphaned or incoming_new:
        return False, (
            f"not a closed permutation: {len(orphaned)} reference(s) left empty, "
            f"{len(incoming_new)} target(s) outside the moved set"
        )
    return True, "clean permutation"


def cmd_report(args: argparse.Namespace) -> int:
    res = analyse(args.edition, args.book)
    per_ch = chapter_permutations(res["moves"])
    all_sources = set()
    clean, dirty = [], []
    for ch, entry in sorted(per_ch.items()):
        ok, why = is_clean(ch, entry, all_sources)
        (clean if ok else dirty).append((ch, len(entry["moves"]), why))
    print(f"{args.edition}/{args.book}")
    print(f"  records already at the right reference : {res['stayed']}")
    print(f"  records filed at the wrong reference   : {len(res['moves'])}")
    print(f"  source not found in the English tree   : {len(res['unmatched'])}")
    print(f"  source ambiguous (repeated in English) : {len(res['ambiguous'])}")
    print(f"\n  chapters repairable automatically: {len(clean)}")
    for ch, n, _ in clean:
        print(f"      {ch}: {n} move(s)")
    print(f"\n  chapters needing a human: {len(dirty)}")
    for ch, n, why in dirty:
        print(f"      {ch}: {n} move(s) — {why}")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    res = analyse(args.edition, args.book)
    per_ch = chapter_permutations(res["moves"])
    entry = per_ch.get(args.chapter)
    if not entry:
        print(f"chapter {args.chapter}: nothing misfiled")
        return 0
    ok, why = is_clean(args.chapter, entry, set())
    print(f"chapter {args.chapter}: {len(entry['moves'])} move(s) — {why}")
    for src, dst in sorted(entry["moves"]):
        doc = load(src) or {}
        text = ((doc.get("translation") or {}).get("text") or "")[:70]
        print(f"  {src.name} -> {dst.name}   {text}")
    if not ok:
        print("\n  apply would refuse this chapter.")
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    res = analyse(args.edition, args.book)
    per_ch = chapter_permutations(res["moves"])
    entry = per_ch.get(args.chapter)
    if not entry:
        print(f"chapter {args.chapter}: nothing to do")
        return 0
    ok, why = is_clean(args.chapter, entry, set())
    if not ok:
        print(f"refusing chapter {args.chapter}: {why}")
        return 1
    payloads = {}
    for src, dst in entry["moves"]:
        doc = load(src)
        if not doc:
            print(f"refusing: cannot read {src}")
            return 1
        payloads[str(dst)] = {
            "translation": doc.get("translation"),
            "source": doc.get("source"),
            "from": str(src.relative_to(REPO_ROOT)),
        }
    for dst_str, payload in payloads.items():
        dst = pathlib.Path(dst_str)
        doc = load(dst)
        if doc is None:
            print(f"refusing: cannot read {dst}")
            return 1
        doc["translation"] = payload["translation"]
        doc["source"] = payload["source"]
        doc.setdefault("revisions", [])
        doc["revisions"].insert(0, {
            "from": "<record filed at the wrong reference>",
            "to": (payload["translation"] or {}).get("text", ""),
            "category": "verse_boundary_redraft",
            "rationale": (
                "This record's source.text identified a different verse from the one its "
                "path names, so the rendering was a translation of that other verse. "
                f"Content re-keyed from {payload['from']} by matching source.text against "
                "the English record carrying the same source. Applied only because the "
                "whole chapter formed a closed permutation, with no reference left empty "
                "and none claimed twice."
            ),
            "adjudicator": "claude-opus-5-source-realignment",
            "reviewer_model": "claude-opus-5",
            "tier": "3",
            "timestamp": args.timestamp,
        })
        dst.write_text(
            yaml.dump(doc, allow_unicode=True, sort_keys=False, width=10**9), encoding="utf-8"
        )
    print(f"chapter {args.chapter}: re-keyed {len(payloads)} record(s)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("report", "plan", "apply"):
        p = sub.add_parser(name)
        p.add_argument("--edition", required=True)
        p.add_argument("--book", required=True)
        if name != "report":
            p.add_argument("--chapter", required=True)
        if name == "apply":
            p.add_argument("--timestamp", default="2026-09-13T00:00:00Z")
    args = ap.parse_args()
    return {"report": cmd_report, "plan": cmd_plan, "apply": cmd_apply}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
