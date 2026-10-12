#!/usr/bin/env python3
"""Index Qumran Digital primary-row locators and displayed parallel links.

This is navigation metadata, not a quotation detector or preservation analysis.
No transcription or morphology is exported. A parallel label never becomes a
primary witness reading. Interpret quotation boundaries in the actual edition.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlsplit


class Element:
    def __init__(self, tag="", attrs=None):
        self.tag = tag
        self.attrs = dict(attrs or [])
        self.children = []

    def has_class(self, name):
        return name in self.attrs.get("class", "").split()

    def walk(self, *, exclude_alternatives=False):
        for child in self.children:
            if isinstance(child, Element):
                if exclude_alternatives and child.has_class("alternative-reading"):
                    continue
                yield child
                yield from child.walk(exclude_alternatives=exclude_alternatives)

    def text(self):
        return "".join(c.text() if isinstance(c, Element) else c for c in self.children)


class Document(HTMLParser):
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
            "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Element()
        self.stack = [self.root]
        self.repairs = {"implicit_span_closures": 0, "extra_final_table_end": 0}
        self.awaiting_main_end = False

    def handle_starttag(self, tag, attrs):
        if self.awaiting_main_end:
            raise ValueError("content after extra final table end")
        node = Element(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self.awaiting_main_end:
            if tag != "main":
                raise ValueError("extra table end is not final")
            self.awaiting_main_end = False
        # The published HTML leaves some decorative spans unclosed before li.
        # Permit only those span closures, never infer missing row/table ends.
        while len(self.stack) > 1 and self.stack[-1].tag == "span" and tag != "span":
            self.stack.pop()
            self.repairs["implicit_span_closures"] += 1
        if (tag == "table" and self.stack[-1].tag == "main"
                and not self.repairs["extra_final_table_end"]):
            self.repairs["extra_final_table_end"] = 1
            self.awaiting_main_end = True
            return
        if len(self.stack) < 2 or self.stack[-1].tag != tag:
            raise ValueError(f"unexpected closing tag {tag}")
        self.stack.pop()

    def handle_data(self, data):
        if self.awaiting_main_end and data.strip():
            raise ValueError("text after extra final table end")
        self.stack[-1].children.append(data)


def document(raw):
    parser = Document()
    parser.feed(raw.decode("utf-8"))
    parser.close()
    if len(parser.stack) != 1:
        raise ValueError("truncated HTML")
    parser.root.repairs = parser.repairs
    return parser.root


def primary_rows(root):
    """Yield only table's own primary rows, never navigation or parallel rows."""
    for table in root.walk():
        if table.tag != "table" or not table.has_class("chapter-column"):
            continue
        for body in table.children:
            if not isinstance(body, Element) or body.tag != "tbody":
                continue
            primary = None
            for row in body.children:
                if not isinstance(row, Element) or row.tag != "tr":
                    continue
                if row.has_class("line-verse"):
                    primary = row
                    yield table, row
                elif row.has_class("parallel-line") and primary is None:
                    raise ValueError("parallel row without preceding primary row")
                elif row.has_class("parallel-line"):
                    primary = None  # Only one parallel row per primary row.


def direct_text_cell(row):
    cells = [c for c in row.children if isinstance(c, Element)
             and c.tag == "td" and c.has_class("line-text")]
    if len(cells) != 1:
        raise ValueError("primary row requires exactly one text cell")
    return cells[0]


def index_document(raw):
    root = document(raw)
    bodies = [n for n in root.walk() if n.tag == "body"]
    times = [n for n in root.walk() if n.tag == "time"]
    if len(bodies) != 1 or len(times) != 1:
        raise ValueError("ambiguous manuscript or release metadata")
    manuscript_id = bodies[0].attrs.get("id", "")
    release = times[0].attrs.get("datetime", "")
    if (not re.fullmatch(r"transcription_id_\d+", manuscript_id)
            or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", release)):
        raise ValueError("invalid manuscript or release metadata")
    result = []
    seen_rows = set()
    seen_words = set()
    for table, row in primary_rows(root):
        row_id = row.attrs.get("id", "")
        if not row_id or row_id in seen_rows:
            raise ValueError("missing or duplicate primary row ID")
        seen_rows.add(row_id)
        word_ids = [n.attrs.get("data-word-id", "") for n in direct_text_cell(row).walk(exclude_alternatives=True)
                    if n.has_class("word")]
        alternate_ids = [n.attrs.get("data-word-id", "")
                         for a in direct_text_cell(row).walk() if a.has_class("alternative-reading")
                         for n in a.walk() if n.has_class("word")]
        if any(not w or w in seen_words for w in word_ids) or len(word_ids) != len(set(word_ids)):
            raise ValueError("missing or duplicate primary word ID")
        seen_words.update(word_ids)
        # The observed schema places one optional parallel row immediately after
        # its primary row. Do not infer a quotation from its links or word joins.
        body = next(c for c in table.children if isinstance(c, Element)
                    and c.tag == "tbody" and row in c.children)
        siblings = [c for c in body.children if isinstance(c, Element) and c.tag == "tr"]
        position = siblings.index(row)
        parallel = siblings[position + 1] if position + 1 < len(siblings) else None
        groups = []
        if parallel is not None and parallel.has_class("parallel-line"):
            for item in parallel.walk():
                if item.tag != "li" or "data-manuscript-id" not in item.attrs:
                    continue
                group = None
                for node in item.walk(exclude_alternatives=True):
                    if node.tag == "a":
                        href = node.attrs.get("href", "")
                        parts = urlsplit(href)
                        if (parts.scheme or parts.netloc
                                or not parts.path.startswith("/transcriptions/") or not parts.fragment):
                            raise ValueError("unexpected parallel reference URL")
                        group = {"parallel_manuscript_id": item.attrs["data-manuscript-id"],
                                 "reference_label": " ".join(node.text().split()),
                                 "href": href, "primary_word_ids": []}
                        groups.append(group)
                    elif node.has_class("word"):
                        if (node.attrs.get("data-word-id") == "0"
                                and "data-parallel-id" not in node.attrs):
                            continue  # Display ellipsis, not a manuscript word.
                        if group is None:
                            raise ValueError("parallel word before reference label")
                        linked = node.attrs.get("data-parallel-id")
                        if linked is not None:
                            if linked not in word_ids:
                                raise ValueError("parallel word links outside current primary row")
                            if linked not in group["primary_word_ids"]:
                                group["primary_word_ids"].append(linked)
        result.append({"column": table.attrs.get("data-name", ""),
                       "line": row.attrs.get("data-name", ""), "row_id": row_id,
                       "primary_word_ids": word_ids,
                       "alternative_word_ids": list(dict.fromkeys(alternate_ids)),
                       "parallel_groups": groups})
    if not result:
        raise ValueError("no primary rows")
    return {"html_sha256": hashlib.sha256(raw).hexdigest(),
            "manuscript_html_id": manuscript_id,
            "release": times[0].attrs.get("datetime", ""),
            "html_repairs": root.repairs, "rows": result,
            "policy": {"transcription_exported": False, "quotations_adjudicated": False,
                       "preservation_assessed": False, "parallel_links_are_primary_readings": False}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    args = parser.parse_args(argv)
    try:
        result = index_document(args.html.read_bytes())
    except (ValueError, UnicodeError) as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
