#!/usr/bin/env python3
"""Audit translation YAMLs for footnote markers that aren't anchored in
the verse text. The publisher Lambda silently filters those out, so any
orphaned footnote never reaches readers.

Usage:
  python3 tools/audit_footnotes.py                     # report on translation/
  python3 tools/audit_footnotes.py --root translation_ko
  python3 tools/audit_footnotes.py translation/ot translation/nt
  python3 tools/audit_footnotes.py --list orphaned
  python3 tools/audit_footnotes.py --anchor-plan       # show proposed anchors
  python3 tools/audit_footnotes.py --anchor-plan --apply

What counts as a marker
-----------------------
A marker is whatever the record itself declares in
``translation.footnotes[].marker``. It is NOT a fixed character class.
The editions localise the marker (Hindi ``[क]``, Arabic ``[أ]``, Russian
``[а]``, Korean ``[주1]``), and the extra-canonical books use markers
with digits and hyphens (``[13]``, ``[5-6]``, ``[v14-15]``). An earlier
version of this tool matched only ``\\[([a-z])\\]`` and so reported
correctly anchored notes as orphans — that is what inflated the
corpus-wide figure to 2,146.

Phrase-keyed records
--------------------
Some records (Gospel of Thomas, Gospel of Philip, Thunder Perfect Mind)
key a footnote to a phrase that appears verbatim in the text rather than
to a bracketed token. Those notes are anchored and are NOT orphans. Such
records are reported separately as ``phrase_keyed`` and are never
touched by the anchor planner.

Anchoring
---------
``--anchor-plan`` proposes a position for each orphaned marker *from the
note's own content*: it extracts the alternative rendering the note
quotes, matches that quote against the verse's
``lexical_decisions[].alternatives`` to recover the ``chosen`` phrase the
note discusses, and anchors the marker immediately after that phrase in
``translation.text``. Nothing is written unless ``--apply`` is passed.

Do not anchor from clause position or from prior revision history.
Earlier passes did that and clustered markers at clause starts with no
relation to what each note discusses (see the 2026-09-13 section of
docs/internationalization/KOREAN_COMPARISON_PANEL.md).
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

try:  # libyaml is ~20x faster over a 40k-file corpus
    from yaml import CSafeLoader as _Loader
except ImportError:  # pragma: no cover
    from yaml import SafeLoader as _Loader  # type: ignore

REPO = Path(__file__).resolve().parent.parent
DEFAULT_ROOT = REPO / "translation"

# Any bracketed run that contains no nested bracket. Used only to spot
# inline tokens that LOOK like this record's own markers but aren't
# declared — never to decide what a marker is.
BRACKETED_RE = re.compile(r"\[([^\[\]]{1,40})\]")

# Quoted alternative inside a footnote: “…”, ‘…’, "…" or '…'.
QUOTE_RE = re.compile(r"[“\"']([^“”\"']{2,200})[”\"']|‘([^‘’]{2,200})’")

STATUSES = [
    "ok",
    "no_footnotes",
    "phrase_keyed",
    "orphaned",
    "partial",
    "extra_marker",
    "duplicate_marker",
    "blank_marker",
    "parse_error",
]


def marker_shape(marker: str) -> str:
    """Coarse class of a marker token, used only to spot stray inline
    tokens of the same shape as a record's declared markers."""
    if re.fullmatch(r"[a-z]", marker):
        return "lower"
    if re.fullmatch(r"[A-Z]", marker):
        return "upper"
    if re.fullmatch(r"\d+", marker):
        return "num"
    if re.fullmatch(r"\d+[-.]\d+", marker):
        return "numrange"
    if re.fullmatch(r"[A-Za-z]+\d+(?:[-.]\d+)?", marker):
        return "alnum"
    if re.fullmatch(r"\w", marker, re.UNICODE):
        return "script-letter"
    if re.fullmatch(r"\w{2,4}", marker, re.UNICODE):
        return "script-token"
    return "phrase"


def is_phrase_like(marker: str) -> bool:
    """True when the marker reads as a quoted phrase rather than a token."""
    return marker_shape(marker) == "phrase"


def load_record(path: Path):
    with open(path) as f:
        return yaml.load(f, Loader=_Loader)


def audit_one(path: Path) -> dict:
    """Classify one YAML record.

    Returns a dict with keys: status, text, declared, orphans,
    extras, footnotes.
    """
    out = {
        "path": path,
        "status": "no_footnotes",
        "text": "",
        "declared": [],
        "orphans": [],
        "extras": [],
        "footnotes": [],
    }
    try:
        doc = load_record(path)
    except Exception:
        out["status"] = "parse_error"
        return out
    tr = doc.get("translation") if isinstance(doc, dict) else None
    if not isinstance(tr, dict):
        return out
    text = str(tr.get("text") or "")
    footnotes = tr.get("footnotes") or []
    if not isinstance(footnotes, list) or not footnotes:
        return out
    out["text"] = text
    out["footnotes"] = footnotes

    raw = [str(f.get("marker", "")) for f in footnotes if isinstance(f, dict)]
    declared = [m.strip() for m in raw]
    if any(not m for m in declared):
        # e.g. two translation_simplified records declare a single space
        # as the marker key. Nothing can anchor that; it is a marker-key
        # defect, not an anchoring one.
        out["status"] = "blank_marker"
        out["declared"] = declared
        return out

    out["declared"] = declared
    unique = list(dict.fromkeys(declared))
    dupes = [m for m, n in Counter(declared).items() if n > 1]
    if dupes:
        # Anchoring these would emit the same inline marker twice
        # (jubilees 20:2, 21:13, 37:14; thunder_perfect_mind/093), so the
        # duplicate keys have to be resolved first. Still record which
        # markers are unanchored, so the report can say how many of these
        # records are also carrying orphaned notes.
        out["status"] = "duplicate_marker"
        out["declared"] = dupes
        out["orphans"] = [m for m in unique if f"[{m}]" not in text]
        return out

    anchored = [m for m in unique if f"[{m}]" in text]
    unanchored = [m for m in unique if m not in anchored]

    # Phrase-keyed: the note is keyed to wording that appears verbatim in
    # the text rather than to a bracketed token. Not an orphan.
    phrase_keyed = [m for m in unanchored if is_phrase_like(m) and m in text]
    if phrase_keyed:
        out["status"] = "phrase_keyed"
        return out

    # Stray inline tokens: bracketed runs that match the shape of one of
    # this record's own declared markers but aren't declared.
    shapes = {marker_shape(m) for m in unique}
    extras = [
        tok
        for tok in dict.fromkeys(BRACKETED_RE.findall(text))
        # `tok not in unique`: declared, so anchored.
        # `f"[{tok}]" not in unique`: some markers carry their own
        # brackets (`[God and man]`), so the inline form is `[[…]]` and
        # the inner run is not a stray token.
        if tok not in unique
        and f"[{tok}]" not in unique
        and marker_shape(tok) in shapes
    ]
    out["extras"] = extras
    out["orphans"] = unanchored

    if not unanchored and not extras:
        out["status"] = "ok"
    elif extras:
        out["status"] = "extra_marker"
    elif len(unanchored) == len(unique):
        out["status"] = "orphaned"
    else:
        out["status"] = "partial"
    return out


# ---------------------------------------------------------------------------
# Anchoring from the note's own content
# ---------------------------------------------------------------------------


def _norm(s: str) -> str:
    s = s.strip().strip(".,;:!?")
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).lower()


def quoted_alternatives(note_text: str) -> list[str]:
    """Every quoted run in a footnote, longest first."""
    found = []
    for m in QUOTE_RE.finditer(note_text or ""):
        q = m.group(1) or m.group(2)
        if q and q.strip():
            found.append(q.strip())
    return sorted(set(found), key=len, reverse=True)


def anchor_phrase_for(note: dict, lexical_decisions: list) -> str | None:
    """Recover the phrase in translation.text that a note discusses.

    The note quotes an alternative rendering; that quote is matched
    against each lexical decision's `alternatives` (and its `chosen`),
    and the decision's `chosen` phrase is what the note is about.
    """
    quotes = quoted_alternatives(str(note.get("text", "")))
    if not quotes:
        return None
    decisions = [d for d in (lexical_decisions or []) if isinstance(d, dict)]
    for q in quotes:
        nq = _norm(q)
        if not nq:
            continue
        for d in decisions:
            chosen = str(d.get("chosen") or "").strip()
            if not chosen:
                continue
            alts = [str(a) for a in (d.get("alternatives") or [])]
            if any(_norm(a) == nq for a in alts) or _norm(chosen) == nq:
                return chosen
    # Fall back to a quote that is itself the chosen wording already in
    # the text (notes that quote what they comment on rather than the
    # alternative).
    for q in quotes:
        for d in decisions:
            chosen = str(d.get("chosen") or "").strip()
            if chosen and _norm(chosen) == _norm(q):
                return chosen
    return None


def plan_anchors(record: dict, doc: dict) -> tuple[str, list[tuple[str, str]], list[str]]:
    """Return (new_text, placed, unplaceable) for one orphaned record.

    `placed` is a list of (marker, phrase) actually anchored.
    """
    text = record["text"]
    lexical = doc.get("lexical_decisions") or []
    by_marker = {
        str(f.get("marker", "")).strip(): f
        for f in record["footnotes"]
        if isinstance(f, dict)
    }
    placed: list[tuple[str, str]] = []
    unplaceable: list[str] = []
    # Collect insertions first so offsets stay valid, then apply
    # right-to-left.
    insertions: list[tuple[int, str, str]] = []
    for marker in record["orphans"]:
        note = by_marker.get(marker)
        if note is None:
            unplaceable.append(marker)
            continue
        phrase = anchor_phrase_for(note, lexical)
        if not phrase:
            unplaceable.append(marker)
            continue
        idx = text.find(phrase)
        if idx < 0:
            # The chosen wording was revised after the note was written.
            unplaceable.append(marker)
            continue
        insertions.append((idx + len(phrase), marker, phrase))

    new_text = text
    for pos, marker, phrase in sorted(insertions, key=lambda t: t[0], reverse=True):
        new_text = new_text[:pos] + f"[{marker}]" + new_text[pos:]
        placed.append((marker, phrase))
    placed.reverse()
    return new_text, placed, unplaceable


def apply_anchors(path: Path, new_text: str) -> None:
    doc = load_record(path)
    doc["translation"]["text"] = new_text
    with open(path, "w") as f:
        yaml.safe_dump(
            doc,
            f,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
            width=10_000,
        )


# ---------------------------------------------------------------------------


def iter_yaml(targets: list[Path]):
    for t in targets:
        if t.is_file():
            yield t
        else:
            yield from sorted(t.rglob("*.yaml"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="*", help="files or directories to audit "
                                            "(default: the --root edition)")
    ap.add_argument("--root", default=str(DEFAULT_ROOT),
                    help="edition directory to audit (default: translation/)")
    ap.add_argument("--list", dest="list_status", choices=STATUSES,
                    help="print every record with this status")
    ap.add_argument("--limit", type=int, default=25,
                    help="how many paths to print per list (0 = all)")
    ap.add_argument("--anchor-plan", action="store_true",
                    help="propose an anchor for each orphaned marker, from "
                         "the note's quoted alternative matched against the "
                         "verse's lexical_decisions")
    ap.add_argument("--apply", action="store_true",
                    help="with --anchor-plan, write the proposed anchors")
    args = ap.parse_args()

    targets = [Path(p) for p in args.paths] or [Path(args.root)]
    missing = [t for t in targets if not t.exists()]
    if missing:
        print("no such path: " + ", ".join(str(m) for m in missing), file=sys.stderr)
        return 2

    counts = Counter()
    records: dict[str, list[dict]] = {s: [] for s in STATUSES}
    orphan_markers = 0
    for p in iter_yaml(targets):
        rec = audit_one(p)
        counts[rec["status"]] += 1
        records[rec["status"]].append(rec)
        if rec["status"] in ("orphaned", "partial"):
            orphan_markers += len(rec["orphans"])

    total = sum(counts.values())
    scope = ", ".join(str(t) for t in targets)
    print(f"Audited {total:,} YAMLs under {scope}:")
    for s in STATUSES:
        print(f"  {s:17s}: {counts[s]:,}")
    print()
    orphan_records = counts["orphaned"] + counts["partial"]
    print(f"Orphaned records: {orphan_records:,} "
          f"({orphan_markers:,} unanchored markers)")
    print(f"  fully orphaned          : {counts['orphaned']:,}")
    print(f"  partially orphaned      : {counts['partial']:,}")
    dup_orphaned = sum(1 for r in records["duplicate_marker"] if r["orphans"])
    print(f"Skipped, need a key repair first:")
    print(f"  duplicate marker key    : {counts['duplicate_marker']:,} "
          f"({dup_orphaned:,} also unanchored)")
    print(f"  blank marker key        : {counts['blank_marker']:,}")
    print(f"Phrase-keyed (anchored by the phrase, not a token): "
          f"{counts['phrase_keyed']:,}")
    print(f"Stray inline markers      : {counts['extra_marker']:,}")

    if args.list_status:
        sel = records[args.list_status]
        print(f"\n{args.list_status} ({len(sel):,}):")
        shown = sel if args.limit == 0 else sel[: args.limit]
        for rec in shown:
            detail = rec["orphans"] or rec["extras"] or rec["declared"]
            print(f"  {rec['path']}  {detail}")
        if len(shown) < len(sel):
            print(f"  ... and {len(sel) - len(shown):,} more")

    if args.anchor_plan:
        candidates = records["orphaned"] + records["partial"]
        planned = written = 0
        unplaceable_markers = 0
        print(f"\nAnchor plan for {len(candidates):,} orphaned records "
              f"({'writing' if args.apply else 'dry run'}):")
        for rec in candidates:
            try:
                doc = load_record(rec["path"])
            except Exception:
                continue
            new_text, placed, unplaceable = plan_anchors(rec, doc)
            unplaceable_markers += len(unplaceable)
            if not placed:
                continue
            planned += 1
            if planned <= args.limit or args.limit == 0:
                rel = rec["path"]
                print(f"  {rel}")
                for marker, phrase in placed:
                    print(f"    [{marker}] after {phrase!r}")
            if args.apply:
                apply_anchors(rec["path"], new_text)
                written += 1
        if args.limit and planned > args.limit:
            print(f"  ... and {planned - args.limit:,} more records")
        print(f"\n  records with at least one placeable marker: {planned:,}")
        print(f"  markers with no recoverable anchor phrase : "
              f"{unplaceable_markers:,}")
        if args.apply:
            print(f"  records rewritten: {written:,}")
        else:
            print("  (dry run — pass --apply to write)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
