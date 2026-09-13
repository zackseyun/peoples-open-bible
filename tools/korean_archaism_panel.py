#!/usr/bin/env python3
"""korean_archaism_panel.py — detect Gaeyeok-line register leaking into POB-ko.

`docs/internationalization/KOREAN_COMPARISON_PANEL.md` explains why the Korean
Bible 1910 (`kor`, ebible.org, public domain) is vendored here as a *negative
control* rather than as a translation target. Its register — 문어체 endings,
`이르되`, `대저` — is exactly what `KOREAN_PIPELINE.md` rules out, so a POB-ko
verse that closely resembles the 1910 wording is a readability smell, not a
reassurance.

Two subcommands:

    vendor    download kor_vpl.txt and write sources/references_ko/kor1910.json
    scan      score every POB-ko verse against its 1910 counterpart

`scan` reports two independent signals per verse:

  similarity   character-trigram Jaccard against the 1910 verse. High values
               mean the POB-ko wording is close to the archaic text.
  markers      direct hits on Gaeyeok-line forms (-니라, -더라, -나이다, 이르되,
               가로되, 대저, 하옵, 하사). These do not depend on alignment and
               are the more reliable of the two.

Neither is a verdict. Per `docs/SOURCE_NEAR_EDITORIAL_STANDARD.md`, a
comparator surfaces a divergence for an editor to adjudicate; it never votes.

Usage:
    python3 tools/korean_archaism_panel.py vendor
    python3 tools/korean_archaism_panel.py scan --min-similarity 0.5
    python3 tools/korean_archaism_panel.py scan --markers-only --area ot
"""
from __future__ import annotations

import argparse
import io
import json
import pathlib
import re
import sys
import urllib.request
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build_reference_panel as refs  # noqa: E402

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
PANEL_DIR = REPO_ROOT / "sources" / "references_ko"
PANEL_PATH = PANEL_DIR / "kor1910.json"
VPL_URL = "https://ebible.org/Scriptures/kor_vpl.zip"

# Gaeyeok-line forms that KOREAN_PIPELINE.md excludes. Anchored where the form
# is only archaic in final position, loose where it is archaic anywhere.
MARKERS: dict[str, re.Pattern[str]] = {
    "-니라": re.compile(r"니라[.\"'」”]*\s*$"),
    "-더라": re.compile(r"더라[.\"'」”]*\s*$"),
    "-러라": re.compile(r"러라[.\"'」”]*\s*$"),
    "-나이다": re.compile(r"나이다"),
    "이르되": re.compile(r"이르되|가로되|가라사대"),
    "대저/무릇": re.compile(r"(^|\s)(대저|무릇)(\s|$)"),
    "하옵": re.compile(r"하옵"),
    "-하사": re.compile(r"하사(\s|$)"),
}

CODE_BY_SLUG = refs.BOOK_USFM_CODES


# Leading verse numbers in chapter-level aggregates, e.g. "12. " or "1[a]. ".
VERSE_SEGMENT = re.compile(r"(?m)(?=^\s*\d+(?:\[[0-9a-z]{1,2}\])?\.\s)")


def verse_segments(text: str) -> list[str]:
    """Split a chapter-level aggregate into its numbered verse segments."""
    parts = [part.strip() for part in VERSE_SEGMENT.split(text) if part.strip()]
    return parts or [text]


def trigrams(text: str) -> set[str]:
    squished = re.sub(r"[\s\W_]+", "", text)
    if len(squished) < 3:
        return {squished} if squished else set()
    return {squished[i : i + 3] for i in range(len(squished) - 2)}


def similarity(a: str, b: str) -> float:
    ta, tb = trigrams(a), trigrams(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def vendor(local_zip: str | None = None) -> None:
    if local_zip:
        print(f"reading {local_zip}")
        payload = pathlib.Path(local_zip).read_bytes()
    else:
        print(f"downloading {VPL_URL}")
        # ebible.org returns 403 to urllib's default User-Agent.
        request = urllib.request.Request(VPL_URL, headers={"User-Agent": "curl/8.4.0"})
        with urllib.request.urlopen(request, timeout=180) as response:
            payload = response.read()
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        name = next(n for n in archive.namelist() if n.endswith("_vpl.txt"))
        raw = archive.read(name).decode("utf-8")

    verses: dict[str, str] = {}
    for line in raw.splitlines():
        match = re.match(r"^([A-Z0-9]{3})\s+(\d+):(\d+)\s+(.*)$", line.strip())
        if not match:
            continue
        code, chapter, verse, text = match.groups()
        if text.strip():
            verses[f"{code} {int(chapter)}:{int(verse)}"] = text.strip()

    PANEL_DIR.mkdir(parents=True, exist_ok=True)
    PANEL_PATH.write_text(
        json.dumps(
            {
                "translation": "Korean Bible 1910",
                "id": "kor1910",
                "license": "public domain",
                "source": "https://ebible.org/kor/",
                "role": "negative control — archaic register detector, not a translation target",
                "verses": verses,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"wrote {PANEL_PATH} with {len(verses)} verses")


def load_panel() -> dict[str, str]:
    if not PANEL_PATH.exists():
        sys.exit(f"{PANEL_PATH} missing — run: python3 {sys.argv[0]} vendor")
    return json.loads(PANEL_PATH.read_text(encoding="utf-8"))["verses"]


def pob_text(path: pathlib.Path) -> str | None:
    import yaml

    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(doc, dict):
        return None
    translation = doc.get("translation")
    if not isinstance(translation, dict):
        return None
    text = translation.get("text")
    return text if isinstance(text, str) else None


def scan(args: argparse.Namespace) -> int:
    panel = load_panel()
    rows = []
    areas = [args.area] if args.area else ["ot", "nt", "extra_canonical"]
    for area in areas:
        root = REPO_ROOT / "translation_ko" / area
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.yaml")):
            parts = path.relative_to(root).parts
            slug = parts[0]
            code = CODE_BY_SLUG.get(slug)
            # ot/nt are always <book>/<chapter>/<verse>.yaml and always have a
            # 1910 counterpart. extra_canonical is looser: chapter-level
            # aggregates (<book>/<NNN>.yaml), an extra grouping level for the
            # Testaments (<book>/<tribe>/<NNN>/<VVV>.yaml), and no 1910 panel
            # entry at all. Keep the strict shape where it holds, and fall back
            # to markers-only elsewhere rather than skipping the file.
            chapter = verse = None
            if len(parts) == 3:
                try:
                    chapter, verse = int(parts[1]), int(parts[2].split(".")[0])
                except ValueError:
                    chapter = verse = None
            if area in ("ot", "nt") and (code is None or chapter is None):
                continue
            text = pob_text(path)
            if not text:
                continue

            hits = sorted(name for name, pattern in MARKERS.items() if pattern.search(text))
            # Chapter-level aggregates hold many verses in one string, so a
            # form that is only archaic in final position (-니라, -더라, -러라)
            # sits mid-string and the anchored patterns never fire. Re-test each
            # numbered verse segment so those files are not silently clean.
            for segment in verse_segments(text):
                hits = sorted(
                    set(hits)
                    | {name for name, pattern in MARKERS.items() if pattern.search(segment)}
                )

            score = 0.0
            if not args.markers_only and code is not None and chapter is not None:
                try:
                    mapped_chapter, mapped_verse = refs.panel_reference(slug, "kjv", chapter, verse)
                except Exception:
                    mapped_chapter, mapped_verse = chapter, verse
                reference = panel.get(f"{code} {mapped_chapter}:{mapped_verse}")
                if reference:
                    score = similarity(text, reference)

            # Genealogies and name lists converge in any faithful translation,
            # so the similarity signal is only meaningful on prose of some length.
            long_enough = len(re.sub(r"\s+", "", text)) >= args.min_length
            if hits or (long_enough and score >= args.min_similarity):
                rows.append(
                    {
                        "path": str(path.relative_to(REPO_ROOT)),
                        "similarity": round(score, 3),
                        "markers": hits,
                        "text": text[:140],
                    }
                )

    rows.sort(key=lambda r: (-len(r["markers"]), -r["similarity"]))
    for row in rows[: args.limit]:
        flags = ",".join(row["markers"]) or "-"
        print(f"{row['similarity']:.3f}  [{flags}]  {row['path']}")
        print(f"        {row['text']}")
    print(f"\n{len(rows)} flagged  (marker hits: {sum(1 for r in rows if r['markers'])})")
    if args.json_out:
        pathlib.Path(args.json_out).write_text(
            json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print(f"wrote {args.json_out}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    vendor_parser = sub.add_parser("vendor", help="download and vendor the public-domain 1910 text")
    vendor_parser.add_argument("--local-zip", help="use an already-downloaded kor_vpl.zip instead of fetching")

    scan_parser = sub.add_parser("scan", help="flag archaic-register verses in translation_ko")
    scan_parser.add_argument("--min-similarity", type=float, default=0.55)
    scan_parser.add_argument("--min-length", type=int, default=45,
                             help="ignore the similarity signal below this many non-space characters")
    scan_parser.add_argument("--markers-only", action="store_true")
    scan_parser.add_argument("--area", choices=["ot", "nt", "extra_canonical"])
    scan_parser.add_argument("--limit", type=int, default=60)
    scan_parser.add_argument("--json-out")

    args = parser.parse_args()
    if args.command == "vendor":
        vendor(args.local_zip)
        return 0
    return scan(args)


if __name__ == "__main__":
    raise SystemExit(main())
