"""Opt-in ordered OSHB/WLC XML research projection; never a canonical writer.

Ordered units preserve direct XML word/segment order. The existing comparison
parser's written stream, qere and annotations remain distinct; neither stream
is a reconstruction of manuscript layout or the earliest Hebrew text.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as E

from tools import wlc
from tools.textual_restoration import compare_uxlc_wlc as comparison

ROOT = Path(__file__).resolve().parents[2]
ATTRIBUTION = ("Original work of the Open Scriptures Hebrew Bible available at "
               "https://github.com/openscriptures/morphhb")
LIMITS = (
    "Projection of the vendored OSHB/WLC digital edition, not a newly read "
    "manuscript, full manuscript-diplomatic transcription, variant adjudication, "
    "restored ink, earliest-text claim or canonical source rewrite. Ordered "
    "XML text concatenates units without inserting spaces; paragraph symbols "
    "are typed segments, not lexical letters. Qere is never merged into written. "
    "XML text is preserved without Unicode normalization; XML lexical escaping "
    "and source-file indentation are not reconstructed."
)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def json_bytes(value):
    """The digest recipe: UTF-8, sorted keys, compact JSON, no final newline."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def _path_label(path):
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path.resolve())


def _xml_content(element):
    """Retain note structure/attributes, including catchwords and non-qere notes."""
    return {"tag": comparison.tag(element), "attributes": dict(element.attrib),
            "text": element.text, "tail": element.tail,
            "children": [_xml_content(child) for child in element]}


def _word(element, position):
    # Reuse the established assembly and validation; do not fork normalization.
    text = comparison.wlc_word(element, [], position)
    _, inline = wlc.word_text(element)
    inline = [{**annotation, "attributes": dict(child.attrib)}
              for annotation, child in zip(inline, element)]
    return {"kind": "word", "position": position,
            "attributes": dict(element.attrib), "text": text,
            "inline_annotations": inline}


def _segment(element, position):
    if len(element):
        raise ValueError("nested direct WLC segment")
    return {"kind": "segment", "position": position,
            "attributes": dict(element.attrib), "text": element.text or ""}


def build_book(code, sources_root=ROOT / "sources"):
    """Read one explicitly named book; return all its XML verse contexts."""
    if code not in wlc.OT_BOOKS:
        raise ValueError(f"Unknown OT book code: {code!r}")
    path = wlc.wlc_file_for(code, Path(sources_root))
    raw = path.read_bytes()
    root = E.fromstring(raw)
    expected = wlc.OT_BOOKS[code][0]
    elements, word_ids = [], set()
    # Validate reference identity before the legacy parser discards its book part.
    for verse in root.iter():
        if comparison.tag(verse) != "verse":
            continue
        identifier = verse.get("osisID", "")
        if not re.fullmatch(re.escape(expected) + r"\.[1-9][0-9]*\.[0-9]+", identifier):
            raise ValueError(f"Unexpected or foreign verse ID: {identifier!r}")
        if (verse.text or "").strip():
            raise ValueError("unexpected text outside direct verse words/segments")
        if any((child.tail or "").strip() for child in verse):
            raise ValueError("unexpected tail outside direct verse words/segments")
        for word in verse.iter():
            if comparison.tag(word) == "w" and word.get("id"):
                if word.get("id") in word_ids:
                    raise ValueError(f"Duplicate word ID: {word.get('id')!r}")
                word_ids.add(word.get("id"))
        elements.append(verse)
    if not elements:
        raise ValueError("no WLC verse contexts")
    parsed = comparison.parse_wlc(raw)
    verses = []
    for verse in elements:
        _, chapter, number = verse.get("osisID").split(".")
        row = parsed[(int(chapter), int(number))]
        units, notes, qere = [], [], []
        for position, child in enumerate(verse):
            kind = comparison.tag(child)
            if kind == "w":
                units.append(_word(child, position))
            elif kind == "seg":
                units.append(_segment(child, position))
            elif kind == "note":
                notes.append({"position": position, "kind": "note",
                              "content": _xml_content(child)})
                if child.get("type") == "variant":
                    for reading_position, reading in enumerate(child):
                        if (comparison.tag(reading) != "rdg"
                                or reading.get("type") != "x-qere"):
                            continue
                        if (reading.text or "").strip():
                            raise ValueError("unexpected text outside qere words/segments")
                        if any((item.tail or "").strip() for item in reading):
                            raise ValueError("unexpected tail outside qere words/segments")
                        group = dict(row["qere"][len(qere)])
                        qere_units = []
                        for j, item in enumerate(reading):
                            if comparison.tag(item) == "w":
                                qere_units.append(_word(item, j))
                            elif comparison.tag(item) == "seg":
                                qere_units.append(_segment(item, j))
                            else:
                                raise ValueError("unexpected qere child " + comparison.tag(item))
                        group.update(note_attributes=dict(child.attrib),
                                     reading_attributes=dict(reading.attrib),
                                     reading_position=reading_position, units=qere_units)
                        qere.append(group)
            # parse_wlc has already rejected unknown direct children.
        verses.append({"osis_id": verse.get("osisID"),
                       "reference_id": f"{code}.{int(chapter)}.{int(number)}",
                       "chapter": int(chapter), "verse": int(number),
                       "verse_attributes": dict(verse.attrib),
                       "ordered_units": units,
                       "ordered_xml_text": "".join(unit["text"] for unit in units),
                       "written": row["written"],
                       "written_text": comparison.written_stream(row),
                       "qere": qere, "annotations": row["annotations"],
                       "notes": notes, "other_note_types": row["other_note_types"]})
    return {"schema_version": "1.0.0", "scope": "complete-vendored-book",
            "book_code": code, "book_slug": wlc.OT_BOOKS[code][1],
            "source": {"path": _path_label(path), "sha256": digest(raw),
                       "edition": "vendored OSHB/WLC OSIS XML",
                       "attribution": ATTRIBUTION,
                       "biblical_text_license": "Public Domain",
                       "annotation_and_morphology_license": "CC BY 4.0",
                       "license_path": "sources/ot/wlc/LICENSE.md"},
            "limits": LIMITS,
            "position_basis": "Zero-based direct XML child index within verse or qere reading; inline offsets are Unicode code points within the unnormalized assembled word.",
            "counts": _counts(verses), "verses": verses}


def _counts(verses):
    return {"verse_contexts": len(verses),
            "written_words": sum(len(v["written"]) for v in verses),
            "direct_segments": sum(sum(u["kind"] == "segment" for u in v["ordered_units"]) for v in verses),
            "qere_groups": sum(len(v["qere"]) for v in verses),
            "qere_words": sum(sum(q["word_count"] for q in v["qere"]) for v in verses),
            "notes": sum(len(v["notes"]) for v in verses),
            "inline_word_segments": sum(sum(len(u["inline_annotations"]) for u in v["ordered_units"] if u["kind"] == "word") for v in verses)}


def all_summary(sources_root=ROOT / "sources"):
    """Execute all 39 complete book exports, without saving bulky corpus JSON."""
    books, totals = [], Counter()
    for code in wlc.OT_BOOKS:
        book = build_book(code, sources_root)
        totals.update(book["counts"])
        books.append({"book_code": code, "source_path": book["source"]["path"],
                      "source_sha256": book["source"]["sha256"],
                      "export_sha256": digest(json_bytes(book)),
                      "counts": book["counts"]})
    inputs = {str(path.relative_to(ROOT)): digest(path.read_bytes()) for path in (
        Path(__file__).resolve(), Path(comparison.__file__).resolve(),
        Path(wlc.__file__).resolve(), ROOT / "sources/ot/wlc/README.md",
        ROOT / "sources/ot/wlc/LICENSE.md")}
    source = {key: value for key, value in book["source"].items()
              if key not in ("path", "sha256")}
    return {"schema_version": "1.0.0", "scope": "all-vendored-WLC-XML-books",
            "source": source, "position_basis": book["position_basis"],
            "limits": LIMITS, "digest_recipe": "UTF-8 sorted-key compact JSON; no final newline",
            "inputs": inputs, "summary": {"books": len(books), **dict(totals)},
            "books": books}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--book", choices=list(wlc.OT_BOOKS))
    mode.add_argument("--all-summary", action="store_true")
    parser.add_argument("--verse", help="XML chapter:verse label, not POB numbering")
    args = parser.parse_args(argv)
    if args.verse and not args.book:
        parser.error("--verse requires --book")
    try:
        result = all_summary() if args.all_summary else build_book(args.book)
        if args.verse:
            if not re.fullmatch(r"[1-9][0-9]*:[0-9]+", args.verse):
                raise ValueError("--verse must be chapter:verse")
            chapter, verse = map(int, args.verse.split(":"))
            selected = [v for v in result["verses"] if (v["chapter"], v["verse"]) == (chapter, verse)]
            if not selected:
                raise ValueError("XML verse context not found")
            result.update(scope="selected-vendored-verse", verses=selected,
                          counts=_counts(selected), selected_xml_reference=args.verse)
    except (ValueError, OSError, E.ParseError) as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
