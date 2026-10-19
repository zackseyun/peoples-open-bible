#!/usr/bin/env python3
"""build_normalized_deuterocanon_corpus.py

Create translation-ready overrides for deuterocanonical books whose raw
scan-adjudicated verse stream still contains known numbering contamination
or still needs canonical partitioning into reader-facing units.

The historical raw/adjudicated baseline remains preserved at:
  sources/lxx/swete/final_corpus_adjudicated/

This script writes only the cleaned override files needed by the
translation layer under:
  sources/lxx/swete/final_corpus_normalized/

Current outputs:
- 1ES: chapters 5, 6 and 8 import/partition restored to the selected printed edition
- WIS: canonical Wisdom only (drop duplicate chapter 20 and Sirach spill)
- BAR: canonical Baruch only (trim back to 1:1-5:9)
- PAZ: Prayer of Azariah + Song of the Three (standalone extraction)
- SUS: Susanna (standalone extraction)
- BEL: Bel and the Dragon (standalone extraction)

Intentionally NOT output yet:
- ESG (Additions to Esther) — still needs a fuller additions-only
  partition, especially the middle of Addition E.
"""
from __future__ import annotations

import json
import argparse
import copy
import hashlib
import pathlib
import re
from collections import Counter

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "sources" / "lxx" / "swete" / "final_corpus_adjudicated"
OUT_DIR = REPO_ROOT / "sources" / "lxx" / "swete" / "final_corpus_normalized"
TRANSCRIBED_DIR = REPO_ROOT / "sources" / "lxx" / "swete" / "transcribed"
ESDRAS_PARTITION = REPO_ROOT / "sources/textual_restoration/candidates/1esdras8_source_partition.2026-10-19.v1.json"
ESDRAS_AFFECTED = {13, 14, 17, 18, 25, *range(39, 63), *range(76, 93)}
ESDRAS5_PARTITION = REPO_ROOT / "sources/textual_restoration/candidates/1esdras5_source_partition.2026-10-19.v1.json"
ESDRAS5_AFFECTED = {25, 28, 29, 31, 38, 39}
ESDRAS6_PARTITION = REPO_ROOT / "sources/textual_restoration/candidates/1esdras6_source_partition.2026-10-19.v1.json"
ESDRAS6_AFFECTED = {1, 8, 9, 10, 24, 26, 30, 31}
ESDRAS7_IMPORT = REPO_ROOT / "sources/textual_restoration/candidates/1esdras7_source_import.2026-10-19.v1.json"
ESDRAS7_AFFECTED = {4, 6}

import lxx_swete  # noqa: E402

VERSE_RE = re.compile(r"(?<!\d)(\d+)(?:[a-zαβ])?\s+")


def load_book(book: str) -> list[dict]:
    path = SRC_DIR / f"{book}.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write_book(book: str, records: list[dict]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / f"{book}.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def chapter_counts(records: list[dict]) -> dict[int, int]:
    counts: Counter[int] = Counter()
    for rec in records:
        counts[int(rec["chapter"])] += 1
    return dict(sorted(counts.items()))


def body_text(vol: int, page: int) -> str:
    raw = (TRANSCRIBED_DIR / f"vol{vol}_p{page:04d}.txt").read_text(encoding="utf-8")
    return lxx_swete.extract_body(raw)


def normalize_greek_text(text: str) -> str:
    text = text.replace("¶", " ")
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"([Α-Ωα-ωἀ-ῼ])[-‐]\s+([Α-Ωα-ωἀ-ῼ])", r"\1\2", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def mark_record(
    rec: dict,
    *,
    book: str | None = None,
    chapter: int | None = None,
    verse: int | None = None,
    rule: str,
    note: str,
    source_note: str | None = None,
) -> dict:
    out = dict(rec)
    if book is not None:
        out["book"] = book
    if chapter is not None:
        out["chapter"] = chapter
    if verse is not None:
        out["verse"] = verse
    out["normalization"] = {
        "rule": rule,
        "note": note,
    }
    if source_note:
        out["source_note"] = source_note
    return out


def make_direct_record(
    *,
    book: str,
    chapter: int,
    verse: int,
    greek: str,
    source_pages: list[int],
    rule: str,
    note: str,
    confidence: str = "high",
) -> dict:
    return {
        "book": book,
        "chapter": chapter,
        "verse": verse,
        "greek": normalize_greek_text(greek),
        "ocr_method": "ai_vision",
        "source_pages": source_pages,
        "validation": "normalized_direct_extract",
        "adjudication": {
            "verdict": "normalized_direct_extract",
            "reasoning": note,
            "confidence": confidence,
            "prompt_version": "normalized_partition_2026-04-21",
        },
        "source_note": note,
        "normalization": {
            "rule": rule,
            "note": note,
        },
    }


def normalize_wis(records: list[dict]) -> tuple[list[dict], list[str]]:
    kept: list[dict] = []
    dropped: list[str] = []
    for rec in records:
        ch = int(rec["chapter"])
        vs = int(rec["verse"])
        ref = f"WIS {ch}:{vs}"
        if ch == 20:
            dropped.append(f"{ref} — duplicate of canonical Wisdom 19 from the raw parser stream")
            continue
        if ch == 19 and vs >= 23:
            dropped.append(f"{ref} — adjacent Sirach contamination beyond canonical Wisdom 19:22")
            continue
        kept.append(
            mark_record(
                rec,
                rule="wisdom_trim_to_canonical_19",
                note="Translation-ready override derived from final_corpus_adjudicated; dropped duplicate chapter 20 and spillover beyond Wisdom 19:22.",
            )
        )
    return kept, dropped


def normalize_1es(records: list[dict]) -> tuple[list[dict], list[str]]:
    """Replay a bounded printed-source correction, not an ancient-text emendation.

    Historical parser/adjudicator receipts remain in their original lane. Reject
    drift rather than applying this partition to an unreviewed source stream.
    """
    source = SRC_DIR / "1ES.jsonl"
    if hashlib.sha256(source.read_bytes()).hexdigest() != "ce3c44488397c44c3af51178d22cc644ae5541e551cb814c7d1e59e2bb5aee74":
        raise ValueError("1ES historical source differs from the reviewed partition baseline")
    if records != load_book("1ES"):
        raise ValueError("1ES supplied records differ from the pinned historical source")
    candidate = json.loads(ESDRAS_PARTITION.read_text(encoding="utf-8"))
    units = candidate["records"]
    if set(units) != {str(v) for v in range(1, 93)}:
        raise ValueError("1ES 8 requires all 92 unique printed units")
    chapter = [r for r in records if int(r["chapter"]) == 8]
    if [int(r["verse"]) for r in chapter] != list(range(1, 93)):
        raise ValueError("1ES 8 historical source identity/order changed")
    out = []
    for rec in records:
        v = int(rec["verse"])
        if int(rec["chapter"]) != 8 or v not in ESDRAS_AFFECTED:
            if int(rec["chapter"]) == 8 and rec["greek"] != units[str(v)]["greek"]:
                raise ValueError(f"Unexpected Greek change outside reviewed scope: 1ES 8:{v}")
            out.append(rec)
            continue
        unit = units[str(v)]
        new = copy.deepcopy(rec)
        for field in list(new):
            if field in ("similarity", "adjudication") or field.startswith("pre_adjudication"):
                new.pop(field, None)
        note = (
            f"1 Esdras 8:{v}, Swete II printed pp. {unit['printed_pages']}; "
            f"PDF pp. {unit['pdf_pages']}; raw scan-leaf indices {unit['source_pages']}. "
            "PDF SHA256 945c5b15bf0f9dfc93890b28ee5b66a388acbf4597f1f2be5430ac6cba9c30b0. "
            "Printed partition correction; not an ancient variant or a full lexical collation. "
            "See docs/1ESDRAS_8_PARTITION_REPAIR_2026-10-19.md."
        )
        new.update(greek=unit["greek"], source_pages=unit["source_pages"],
                   ocr_method="printed_partition_correction",
                   validation="scan_partition_correction_pending_full_review", confidence="medium",
                   source_note=note,
                   adjudication={"verdict": "printed_partition_correction", "confidence": "medium",
                                 "reasoning": note},
                   normalization={"rule": "1esdras8_printed_partition_2026-10-19", "note": note})
        new.setdefault("source_correction_history", []).append({
            "baseline_commit": "97194d2b4c691514373896490110246b0b024219",
            "record": copy.deepcopy(rec), "certifies_corrected_record": False,
            "contributors": unit["contributors"],
        })
        out.append(new)
    out, dropped = normalize_1es5(out)
    return normalize_1es7(normalize_1es6(out)), dropped


def normalize_1es5(records: list[dict]) -> tuple[list[dict], list[str]]:
    """Apply only the six reviewed chapter-5 units and omit its redundant145.

    Called after the chapter-8 correction, so all other rows (including8)
    remain exactly as supplied. The discarded historical row remains in the
    immutable adjudicated corpus; its canonical YAML has a separate quarantine.
    """
    candidate = json.loads(ESDRAS5_PARTITION.read_text(encoding="utf-8"))
    units = candidate["records"]
    if set(units) != {str(v) for v in range(1, 71)}:
        raise ValueError("1ES 5 requires all 70 unique printed units")
    chapter = [r for r in records if int(r["chapter"]) == 5]
    if [int(r["verse"]) for r in chapter] != [*range(1, 71), 145]:
        raise ValueError("1ES 5 historical source identity/order changed")
    by_verse = {int(r["verse"]): r for r in chapter}
    if by_verse[145]["greek"] != by_verse[47]["greek"]:
        raise ValueError("1ES 5:145 no longer exactly duplicates47")
    out = []
    for rec in records:
        v = int(rec["verse"])
        if int(rec["chapter"]) != 5:
            out.append(rec)
            continue
        if v == 145:
            continue
        unit = units[str(v)]
        if v not in ESDRAS5_AFFECTED:
            if rec["greek"] != unit["greek"]:
                raise ValueError(f"Unexpected Greek change outside reviewed scope: 1ES 5:{v}")
            out.append(rec)
            continue
        new = copy.deepcopy(rec)
        for field in list(new):
            if field in ("similarity", "adjudication") or field.startswith("pre_adjudication"):
                new.pop(field, None)
        note = (
            f"1 Esdras 5:{v}, Swete II printed pp. {unit['printed_pages']}; "
            f"PDF pp. {unit['pdf_pages']}; raw scan-leaf indices {unit['source_pages']}. "
            "PDF SHA256 945c5b15bf0f9dfc93890b28ee5b66a388acbf4597f1f2be5430ac6cba9c30b0. "
            "Printed partition/import correction, not an ancient-priority decision or full lexical collation. "
            "See docs/1ESDRAS_5_PARTITION_REPAIR_2026-10-19.md."
        )
        new.update(greek=unit["greek"], source_pages=unit["source_pages"],
                   ocr_method="printed_partition_correction",
                   validation="scan_partition_correction_pending_full_review", confidence="medium",
                   source_note=note,
                   adjudication={"verdict": "printed_partition_correction", "confidence": "medium",
                                 "reasoning": note},
                   normalization={"rule": "1esdras5_printed_partition_2026-10-19", "note": note})
        new.setdefault("source_correction_history", []).append({
            "baseline_commit": "756074bd3e0bd97c5d849c5ff47125972f4684b2",
            "record": copy.deepcopy(rec), "certifies_corrected_record": False,
            "contributors": unit["contributors"],
        })
        out.append(new)
    return out, ["1ES 5:145 — exact Greek duplicate of5:47; historical row retained, canonical YAML quarantined"]


def normalize_1es6(records: list[dict]) -> list[dict]:
    """Replay chapter6's explicit additions, moves and modern-error corrections.

    The source candidate accounts for each retained, replaced or excluded old
    codepoint. Raw source and all unaffected normalized rows remain unchanged.
    """
    candidate = json.loads(ESDRAS6_PARTITION.read_text(encoding="utf-8"))
    units = candidate["records"]
    if set(units) != {str(v) for v in range(1, 34)}:
        raise ValueError("1ES 6 requires all 33 unique printed units")
    chapter = [r for r in records if int(r["chapter"]) == 6]
    if [int(r["verse"]) for r in chapter] != list(range(1, 34)):
        raise ValueError("1ES 6 historical source identity/order changed")
    out = []
    for rec in records:
        v = int(rec["verse"])
        if int(rec["chapter"]) != 6:
            out.append(rec)
            continue
        unit = units[str(v)]
        if v not in ESDRAS6_AFFECTED:
            if rec["greek"] != unit["greek"]:
                raise ValueError(f"Unexpected Greek change outside reviewed scope: 1ES 6:{v}")
            out.append(rec)
            continue
        new = copy.deepcopy(rec)
        for field in list(new):
            if field in ("similarity", "adjudication") or field.startswith("pre_adjudication"):
                new.pop(field, None)
        note = (
            f"1 Esdras 6:{v}, Swete II printed pp. {unit['printed_pages']}; "
            f"PDF pp. {unit['pdf_pages']}; raw scan-leaf indices {unit['source_pages']}. "
            "PDF SHA256 945c5b15bf0f9dfc93890b28ee5b66a388acbf4597f1f2be5430ac6cba9c30b0. "
            "Printed import/partition correction: two whole clauses restored, two modern duplicate slices "
            "excluded with originals archived, one specified accent corrected; not ancient priority or full lexical collation. "
            "See docs/1ESDRAS_6_PARTITION_REPAIR_2026-10-19.md."
        )
        new.update(greek=unit["greek"], source_pages=unit["source_pages"],
                   ocr_method="printed_partition_correction",
                   validation="scan_partition_correction_pending_full_review", confidence="medium",
                   source_note=note,
                   adjudication={"verdict": "printed_partition_correction", "confidence": "medium",
                                 "reasoning": note},
                   normalization={"rule": "1esdras6_printed_partition_2026-10-19", "note": note})
        new.setdefault("source_correction_history", []).append({
            "baseline_commit": "08a8a4cc05fcb8eb91580e01fb506a90de9799a9",
            "record": copy.deepcopy(rec), "certifies_corrected_record": False,
            "contributors": unit["contributors"],
        })
        out.append(new)
    return out


def normalize_1es7(records: list[dict]) -> list[dict]:
    """Replace two printed words; preserve every boundary and all other rows."""
    candidate = json.loads(ESDRAS7_IMPORT.read_text(encoding="utf-8"))
    units = candidate["records"]
    if set(units) != {str(v) for v in range(1, 16)}:
        raise ValueError("1ES 7 requires all 15 unique printed units")
    chapter = [r for r in records if int(r["chapter"]) == 7]
    if [int(r["verse"]) for r in chapter] != list(range(1, 16)):
        raise ValueError("1ES 7 historical source identity/order changed")
    replacements = {4: ("προτάγματος", "προστάγματος"),
                    6: ("προσενεχθέντες", "προστεθέντες")}
    out = []
    for rec in records:
        v = int(rec["verse"])
        if int(rec["chapter"]) != 7:
            out.append(rec)
            continue
        unit = units[str(v)]
        old = rec["greek"]
        if (old != unit["old_greek"]
                or hashlib.sha256(old.encode()).hexdigest() != unit["old_greek_sha256"]):
            raise ValueError(f"1ES 7:{v} historical Greek changed")
        if v not in ESDRAS7_AFFECTED:
            if unit["greek"] != old:
                raise ValueError(f"Unexpected Greek change outside reviewed scope: 1ES 7:{v}")
            out.append(rec)
            continue
        before, after = replacements[v]
        if old.count(before) != 1 or unit["greek"] != old.replace(before, after):
            raise ValueError(f"1ES 7:{v} exceeds the single reviewed word correction")
        new = copy.deepcopy(rec)
        for field in list(new):
            if field in ("similarity", "adjudication") or field.startswith("pre_adjudication"):
                new.pop(field, None)
        note = (
            f"1 Esdras 7:{v}, Swete II printed150; one-based PDF168; raw scan leaf167. "
            "PDF SHA256 945c5b15bf0f9dfc93890b28ee5b66a388acbf4597f1f2be5430ac6cba9c30b0. "
            "One specified printed-word import correction, with historical row archived; "
            "not an ancient-priority decision or full lexical collation. "
            "See docs/1ESDRAS_7_WORD_REPAIR_2026-10-19.md."
        )
        new.update(greek=unit["greek"], source_pages=unit["source_pages"],
                   ocr_method="printed_word_import_correction",
                   validation="scan_word_correction_pending_full_review", confidence="medium",
                   source_note=note,
                   adjudication={"verdict": "printed_word_import_correction", "confidence": "medium",
                                 "reasoning": note},
                   normalization={"rule": "1esdras7_printed_words_2026-10-19", "note": note})
        new.setdefault("source_correction_history", []).append({
            "baseline_commit": "8ad14030bcedcdc533a74724afcdd672bdbf89ed",
            "record": copy.deepcopy(rec), "certifies_corrected_record": False,
            "contributors": unit["contributors"],
        })
        out.append(new)
    return out


def normalize_bar(records: list[dict]) -> tuple[list[dict], list[str]]:
    kept: list[dict] = []
    dropped: list[str] = []
    for rec in records:
        ch = int(rec["chapter"])
        vs = int(rec["verse"])
        ref = f"BAR {ch}:{vs}"
        keep = False
        if ch == 1 and vs <= 22:
            keep = True
        elif ch == 2 and vs <= 35:
            keep = True
        elif ch == 3 and vs <= 38:
            keep = True
        elif ch == 4 and vs <= 37:
            keep = True
        elif ch == 5 and vs <= 9:
            keep = True

        if not keep:
            reason = "removed by canonical Baruch chapter/verse boundaries"
            if ch == 1 and vs >= 23:
                reason = "raw chapter-1 tail is actually Baruch 3:23-38"
            elif ch == 5 and vs >= 10:
                reason = "raw chapter-5 tail spills into Lamentations material"
            dropped.append(f"{ref} — {reason}")
            continue

        kept.append(
            mark_record(
                rec,
                rule="baruch_trim_to_canonical_5",
                note="Translation-ready override derived from final_corpus_adjudicated; kept canonical Baruch 1:1-5:9 only, with Letter of Jeremiah handled separately as LJE.",
            )
        )
    return kept, dropped


def normalize_paz(records: list[dict]) -> tuple[list[dict], list[str]]:
    kept: list[dict] = []
    dropped: list[str] = []
    note = (
        "Standalone PAZ extraction from the curated ADA stream, using Daniel 3:24-90 as the source span and renumbering it to PAZ 1:1-67."
    )
    for rec in records:
        if int(rec["chapter"]) == 3 and 24 <= int(rec["verse"]) <= 90:
            kept.append(
                mark_record(
                    rec,
                    book="PAZ",
                    chapter=1,
                    verse=int(rec["verse"]) - 23,
                    rule="paz_extract_from_ada_ch3",
                    note=note,
                    source_note=note,
                )
            )
        else:
            dropped.append(f"ADA {rec['chapter']}:{rec['verse']} — outside PAZ extraction window")
    return kept, dropped


def sus_tail_records() -> list[dict]:
    out: list[dict] = []
    note = (
        "Standalone Susanna extraction currently follows the complete Theodotion stream in Swete, because that stream is the cleanest fully numbered extract available in the current corpus."
    )

    body606 = normalize_greek_text(body_text(3, 606))
    body606 = body606[body606.find("51 καὶ εἶπεν") :]
    positions = {int(m.group(1)): m.start() for m in VERSE_RE.finditer(body606) if 51 <= int(m.group(1)) <= 59}
    order = sorted(positions)
    for i, verse in enumerate(order):
        end = positions[order[i + 1]] if i + 1 < len(order) else body606.find("Καὶ ἀνεβόησεν πᾶσα ἡ συναγωγὴ")
        text = body606[positions[verse] : end]
        text = text[text.find(str(verse)) + len(str(verse)) :]
        out.append(
            make_direct_record(
                book="SUS",
                chapter=1,
                verse=verse,
                greek=text,
                source_pages=[606],
                rule="sus_partition_theodotion_tail",
                note=note,
            )
        )
    tail_start = body606.find("Καὶ ἀνεβόησεν πᾶσα ἡ συναγωγὴ")
    tail = body606[tail_start:]
    out.append(
        make_direct_record(
            book="SUS",
            chapter=1,
            verse=60,
            greek=tail,
            source_pages=[606],
            rule="sus_partition_theodotion_tail",
            note=note,
            confidence="medium",
        )
    )

    body608 = normalize_greek_text(body_text(3, 608))
    body608 = body608[body608.find("61 ") :]
    positions = {int(m.group(1)): m.start() for m in VERSE_RE.finditer(body608) if 61 <= int(m.group(1)) <= 64}
    order = sorted(positions)
    for i, verse in enumerate(order):
        end = positions[order[i + 1]] if i + 1 < len(order) else len(body608)
        text = body608[positions[verse] : end]
        text = text[text.find(str(verse)) + len(str(verse)) :]
        out.append(
            make_direct_record(
                book="SUS",
                chapter=1,
                verse=verse,
                greek=text,
                source_pages=[608],
                rule="sus_partition_theodotion_tail",
                note=note,
            )
        )
    return out


def normalize_sus(records: list[dict]) -> tuple[list[dict], list[str]]:
    kept: list[dict] = []
    dropped: list[str] = []
    note = (
        "Standalone Susanna extraction currently follows the complete Theodotion stream in Swete, because that stream is the cleanest fully numbered extract available in the current corpus."
    )
    for rec in records:
        ch = int(rec["chapter"])
        vs = int(rec["verse"])
        if ch == 1 and 1 <= vs <= 50:
            kept.append(
                mark_record(
                    rec,
                    book="SUS",
                    chapter=1,
                    verse=vs,
                    rule="sus_partition_theodotion",
                    note=note,
                    source_note=note,
                )
            )
        else:
            dropped.append(f"ADA {ch}:{vs} — outside Susanna 1:1-50 carry-over window")
    kept.extend(sus_tail_records())
    kept.sort(key=lambda r: (int(r["chapter"]), int(r["verse"])))
    return kept, dropped


def _parse_bel_page(page: int, start_verse: int, end_verse: int) -> list[dict]:
    body = normalize_greek_text(body_text(3, page))
    note = (
        "Standalone Bel extraction currently follows the complete Theodotion stream in Swete, because that stream is the cleanest fully numbered extract available in the current corpus."
    )
    if page == 610:
        body = body.replace("I. ", "", 1)
    if page == 616 and "37 καὶ ἐβόησεν" in body:
        body = body[body.find("37 καὶ ἐβόησεν") :]
    positions: dict[int, int] = {}
    for m in VERSE_RE.finditer(body):
        num = int(m.group(1))
        if start_verse <= num <= end_verse and num not in positions:
            positions[num] = m.start()
    order = sorted(positions)
    out: list[dict] = []

    if order and start_verse not in positions:
        first_end = positions[order[0]]
        first_text = body[:first_end]
        out.append(
            make_direct_record(
                book="BEL",
                chapter=1,
                verse=start_verse,
                greek=first_text,
                source_pages=[page],
                rule="bel_partition_theodotion",
                note=note,
            )
        )

    for i, verse in enumerate(order):
        end = positions[order[i + 1]] if i + 1 < len(order) else len(body)
        text = body[positions[verse] : end]
        text = text[text.find(str(verse)) + len(str(verse)) :]
        text = re.sub(rf"(?<!\d){verse}\s+", "", text)
        out.append(
            make_direct_record(
                book="BEL",
                chapter=1,
                verse=verse,
                greek=text,
                source_pages=[page],
                rule="bel_partition_theodotion",
                note=note,
            )
        )
    return out


def normalize_bel() -> tuple[list[dict], list[str]]:
    kept: list[dict] = []
    for page, start, end in [(610, 1, 10), (612, 11, 23), (614, 24, 36), (616, 37, 42)]:
        kept.extend(_parse_bel_page(page, start, end))
    kept.sort(key=lambda r: (int(r["chapter"]), int(r["verse"])))
    return kept, []


def summarize_job(summary_lines: list[str], *, book: str, raw_count: int | None, normalized: list[dict], dropped: list[str], note: str | None = None) -> None:
    summary_lines.append(f"## {book}")
    summary_lines.append("")
    if raw_count is not None:
        summary_lines.append(f"- Raw verses: **{raw_count}**")
    summary_lines.append(f"- Normalized verses: **{len(normalized)}**")
    summary_lines.append(f"- Dropped contaminated / duplicate refs: **{len(dropped)}**")
    summary_lines.append(f"- Chapter counts after normalization: `{chapter_counts(normalized)}`")
    if note:
        summary_lines.append(f"- Note: {note}")
    summary_lines.append("")
    for line in dropped[:120]:
        summary_lines.append(f"  - {line}")
    if len(dropped) > 120:
        summary_lines.append(f"  - … {len(dropped) - 120} more omitted from this summary")
    summary_lines.append("")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book", choices=["1ES", "WIS", "BAR", "PAZ", "SUS", "BEL"],
                        help="Write only this override; leave other outputs and SUMMARY.md untouched")
    args = parser.parse_args(argv)
    summary_lines = [
        "# Normalized deuterocanonical corpus overrides",
        "",
        "These files are translation-ready overrides derived from `final_corpus_adjudicated/`.",
        "The raw adjudicated corpus remains untouched for audit. The translation layer prefers these overrides when present.",
        "",
    ]

    jobs = {
        "1ES": lambda: normalize_1es(load_book("1ES")),
        "WIS": lambda: normalize_wis(load_book("WIS")),
        "BAR": lambda: normalize_bar(load_book("BAR")),
        "PAZ": lambda: normalize_paz(load_book("ADA")),
        "SUS": lambda: normalize_sus(load_book("ADA")),
        "BEL": normalize_bel,
    }
    raw_counts = {
        "1ES": len(load_book("1ES")),
        "WIS": len(load_book("WIS")),
        "BAR": len(load_book("BAR")),
        "PAZ": len(load_book("ADA")),
        "SUS": len(load_book("ADA")),
        "BEL": None,
    }
    notes = {
        "1ES": "Chapter 8 printed partition and two omitted clauses restored; historical adjudicated stream preserved.",
        "PAZ": "Standalone extraction from Daniel 3:24-90.",
        "SUS": "Standalone extraction currently follows the Theodotion stream because it is the cleanest complete extract in the current corpus.",
        "BEL": "Standalone extraction currently follows the Theodotion stream because it is the cleanest complete extract in the current corpus.",
    }

    for book, fn in jobs.items():
        if args.book and args.book != book:
            continue
        normalized, dropped = fn()
        write_book(book, normalized)
        summarize_job(
            summary_lines,
            book=book,
            raw_count=raw_counts[book],
            normalized=normalized,
            dropped=dropped,
            note=notes.get(book),
        )

    summary_lines.extend(
        [
            "## Still not emitted",
            "",
            "- ESG (Additions to Esther) is intentionally still blocked. The outer boundaries are now understood, but Addition E 1-16 still needs a fuller additions-only verse segmentation pass before we should draft from it safely.",
            "",
        ]
    )

    if not args.book:
        (OUT_DIR / "SUMMARY.md").write_text("\n".join(summary_lines).rstrip() + "\n", encoding="utf-8")
    print(f"Wrote normalized overrides to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
