#!/usr/bin/env python3
"""Restore cut-off and missing 1 Enoch source text from the page transcription.

The Charles 1906 page transcription (sources/enoch/ethiopic/transcribed/
charles_1906/pages/) was first split into chapter files by page. A verse that
ran onto the next page was cut off, and the verses at the top of that page were
filed under the next chapter or dropped. Read in page order, the transcription
holds all 1,060 printed units: 107 Roman chapter numerals and 953 numbered
verses (POB adds one reader address by splitting 6:7, for 1,061).

This tool reads the pages in order, splits them at the printed chapter and verse
numbers, and compares each unit with translation/extra_canonical/1_enoch/:

- review-accepted source text is never changed;
- a parser-derived source that is a cut-off prefix of the page text is replaced;
- a printed verse with no file gets a new record (source only; the English
  comes from the meaning pass, tools/pob_meaning_pass.py).

Where the October-November source review left a clean collated draft of the
verse (no unresolved-glyph marks, close to the page text), that draft is used
instead of the raw transcription.

  python3 tools/enoch/restore_sources.py plan  [--drafts drafts.json]
  python3 tools/enoch/restore_sources.py apply [--drafts drafts.json]
  python3 tools/enoch/restore_sources.py finalize --run <meaning-pass run>
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import pathlib
import re
import sys
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
PAGES = ROOT / "sources/enoch/ethiopic/transcribed/charles_1906/pages"
BOOK = ROOT / "translation/extra_canonical/1_enoch"
VALIDATION = "page_order_transcription_restored"
ROMAN = {"I": 1, "V": 5, "X": 10, "L": 50, "C": 100}
SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"
ETH = "ሀ-፿"
TOKEN = re.compile(
    r"(?<![A-Za-z])(?P<rom>[IVXLC]{1,8})\.(?=\s)"
    r"|(?<![\d፡A-Za-z])(?P<num>\d{1,3})\.(?=\s)"
    r"|@@PAGE (?P<page>\d+)@@"
)


def roman(s: str) -> int:
    total = 0
    for a, b in zip(s, s[1:] + " "):
        v = ROMAN[a]
        total += -v if b != " " and ROMAN.get(b, 0) > v else v
    return total


def norm(s: str) -> str:
    return re.sub(r"[\s*†\[\]" + SUP + "]", "", s or "")


def clean(s: str) -> str:
    s = re.sub("[" + SUP + "]+", "", s)
    # A line that ends without a word divider continues the same word.
    s = re.sub(rf"(?<=[{ETH}])[ \t]*\n\s*(?=[{ETH}])", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    s = re.sub(r"\s+([፡።])", r"\1", s)
    s = s.replace("፡፡", "።")
    s = re.sub(r"፡(?=[^\s።፡])", "፡ ", s)
    s = re.sub(r"\s+\d{1,3}$", "", s)  # stray page/line number after the verse
    return s.strip()


def segment() -> dict[str, dict[str, Any]]:
    pages = sorted(PAGES.glob("p*.txt"))
    if not pages:
        raise SystemExit(f"no page transcription under {PAGES}")
    text = "".join(f"\n@@PAGE {int(p.stem[1:])}@@\n{p.read_text(encoding='utf-8')}" for p in pages)
    text = text.replace("መጽሐፈ ፡ ሄኖክ ፡", "", 1)
    out: dict[str, dict[str, Any]] = {}
    cur: dict[str, Any] | None = None
    chapter, page, pos = 1, None, 0
    for m in TOKEN.finditer(text):
        if cur is not None:
            cur["raw"] += text[pos:m.start()]
        pos = m.end()
        if m.group("page"):
            page = int(m.group("page"))
            if cur is not None and page not in cur["pages"]:
                cur["pages"].append(page)
            continue
        if m.group("rom"):
            chapter, verse = roman(m.group("rom")), 1
        else:
            verse = int(m.group("num"))
        cur = {"chapter": chapter, "verse": verse, "raw": "", "pages": [page]}
        out[f"{chapter}:{verse}"] = cur
    if cur is not None:
        cur["raw"] += text[pos:]
    for unit in out.values():
        unit["text"] = clean(unit.pop("raw"))
    return out


def usable_draft(drafts: dict[str, Any], ref: str, page_text: str) -> str | None:
    d = drafts.get(f"1 Enoch {ref}")
    if not d:
        return None
    text = d.get("text") or ""
    if "⟦" in text or "hold" in str(d.get("validation") or ""):
        return None
    if difflib.SequenceMatcher(None, norm(text), norm(page_text)).ratio() < 0.8:
        return None
    return text


def plan(drafts: dict[str, Any]) -> list[dict[str, Any]]:
    actions = []
    for ref, unit in segment().items():
        ch, vs = unit["chapter"], unit["verse"]
        path = BOOK / f"{ch:03d}" / f"{vs:03d}.yaml"
        draft = usable_draft(drafts, ref, unit["text"])
        new_text, basis = (draft, "collated_draft") if draft else (unit["text"], "page_transcription")
        row = {"ref": ref, "path": str(path.relative_to(ROOT)), "pages": unit["pages"],
               "text": new_text, "basis": basis}
        if not path.exists():
            actions.append({**row, "action": "create"})
            continue
        src = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("source") or {}
        if src.get("validation") not in (None, "verse_parser_ok"):
            continue  # review-accepted text stays as it is
        old, page_text = norm(src.get("text")), norm(unit["text"])
        if old != page_text and page_text.startswith(old):
            actions.append({**row, "action": "restore", "old": src.get("text")})
    return actions


SECTIONS = [
    (36, "Book of the Watchers"), (71, "Book of Parables"), (82, "Astronomical Book"),
    (90, "Book of Dreams / Animal Apocalypse"), (108, "Epistle of Enoch"),
]


def section(ch: int) -> str:
    return next(name for last, name in SECTIONS if ch <= last)


def note(basis: str, action: str) -> str:
    where = ("collated against the printed page in the 2026 source review"
             if basis == "collated_draft" else "read from the Charles 1906 page transcription in page order")
    why = ("The earlier text stopped at a page break." if action == "restore"
           else "This printed verse had no record; it had been lost at a page break.")
    return f"{why} Restored 2026-11-09, {where}. Not independently reviewed."


def cmd_plan(args: argparse.Namespace) -> int:
    actions = plan(load_drafts(args.drafts))
    out = pathlib.Path(args.out)
    out.write_text(json.dumps(actions, ensure_ascii=False, indent=1))
    from collections import Counter
    print(Counter((a["action"], a["basis"]) for a in actions), out)
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    actions = plan(load_drafts(args.drafts))
    for a in actions:
        path = ROOT / a["path"]
        ch, vs = (int(x) for x in a["ref"].split(":"))
        source = {
            "edition": "charles-1906-enoch", "text": a["text"], "language": "Geez", "pages": a["pages"],
            "confidence": "medium", "validation": VALIDATION, "note": note(a["basis"], a["action"]),
        }
        if a["action"] == "restore":
            rec = yaml.safe_load(path.read_text(encoding="utf-8"))
            rec["source"].update({k: source[k] for k in ("text", "pages", "validation", "note")})
            rec["source"]["previous_text"] = a["old"]
            for w in (rec.get("enoch_witnesses") or {}).get("available_witnesses") or []:
                if w.get("witness") == "charles_1906":
                    w["text"] = a["text"]
                    w["note"] = source["note"]
        else:
            rec = {
                "id": f"1EN.{ch}.{vs}", "reference": f"1 Enoch {ch}:{vs}", "book": "1 Enoch",
                "source": source, "translation": {"text": "", "philosophy": "dynamic"}, "status": "draft",
                "enoch_witnesses": {
                    "section": section(ch),
                    "loaded_witnesses_by_language": {"geez": ["charles_1906"]},
                    "available_witnesses": [{
                        "language": "geez", "witness": "charles_1906", "source_edition": "Charles 1906 Ethiopic Enoch",
                        "text": a["text"], "confidence": "medium", "note": source["note"],
                    }],
                },
            }
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(rec, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")
    print(f"restored={sum(a['action'] == 'restore' for a in actions)} created={sum(a['action'] == 'create' for a in actions)}")
    return 0


def cmd_finalize(args: argparse.Namespace) -> int:
    """Give records without an ai_draft block one from the meaning pass that wrote their English.

    That covers the records created here and a few older records that never had one.
    """
    done = 0
    for path in sorted(BOOK.rglob("*.yaml")):
        rec = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if rec.get("ai_draft"):
            continue
        mp = rec.get("meaning_pass") or {}
        if mp.get("run") != args.run or not (rec.get("translation") or {}).get("text"):
            raise SystemExit(f"{path}: no English from meaning-pass run {args.run}")
        rec["ai_draft"] = {
            "model_id": "gpt-6.1-sol", "model_version": str(mp.get("model") or "gpt-6.1-sol"),
            "prompt_id": mp["prompt_id"], "prompt_sha256": mp["prompt_sha256"], "timestamp": mp["timestamp"],
            "output_hash": hashlib.sha256(rec["translation"]["text"].encode("utf-8")).hexdigest(),
            "zone1_sources_at_draft": [f"Charles 1906 Ethiopic Enoch ({rec['source'].get('validation')})"],
        }
        path.write_text(yaml.safe_dump(rec, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")
        done += 1
    print(f"finalized={done}")
    return 0


def load_drafts(path: str | None) -> dict[str, Any]:
    return json.loads(pathlib.Path(path).read_text()) if path else {}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("plan", cmd_plan), ("apply", cmd_apply)):
        p = sub.add_parser(name)
        p.add_argument("--drafts", help="JSON of collated drafts by reference: {ref: {text, validation}}")
        if name == "plan":
            p.add_argument("--out", default="/dev/stdout")
        p.set_defaults(func=fn)
    f = sub.add_parser("finalize")
    f.add_argument("--run", required=True)
    f.set_defaults(func=cmd_finalize)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
