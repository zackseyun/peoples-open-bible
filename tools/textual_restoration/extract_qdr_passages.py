#!/usr/bin/env python3
"""Extract manuscript-level passage hits from a QDR biblical JSON snapshot.

The QDR corpus stores a biblical reference on each word, not on the scroll or
line. This extractor deliberately walks every nested word so fragmentary lines
and verses spanning more than one line cannot be silently missed.

The reference-only excerpt is not self-contained preservation evidence: an
opening supply bracket may belong to another verse. Request line context and
consult the edition before deciding which letters survive. Line context itself
may begin inside a lacuna opened on an earlier physical line.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def reference_annotation_audit(corpus: list[dict]) -> dict:
    """Describe indexing capability, not manuscript or preservation coverage."""
    annotated = empty = unusable = records_with_references = 0
    for scroll in corpus:
        record_has_reference = False
        for fragment in scroll.get("fragments", []):
            for line in fragment.get("lines", []):
                for word in line.get("words", []):
                    if (not isinstance(word, (list, tuple)) or len(word) < 6
                            or not isinstance(word[5], str)):
                        unusable += 1
                    elif word[5].strip():
                        annotated += 1
                        record_has_reference = True
                    else:
                        empty += 1
        records_with_references += record_has_reference
    total = annotated + empty + unusable
    status = "none" if not annotated else "complete" if annotated == total else "partial"
    return {
        "status": status, "records": len(corpus), "words": total,
        "annotated_words": annotated, "empty_reference_slots": empty,
        "unusable_reference_slots": unusable,
        "records_with_references": records_with_references,
        "warning": ("No usable reference annotations: a zero-result verse search "
                    "cannot establish absence of quotations or allusions."
                    if status == "none" else
                    "Only indexed words are searched; reference hits do not "
                    "establish preserved letters or exhaustive passage coverage."),
    }


def extract_passages(corpus: list[dict], references: set[str], *,
                     include_line_context: bool = False) -> dict[str, list[dict]]:
    """Return exact index matches; reject snapshots with no usable reference index."""
    audit = reference_annotation_audit(corpus)
    if audit["status"] == "none":
        raise ValueError(audit["warning"])
    results: dict[str, list[dict]] = {reference: [] for reference in sorted(references)}
    for scroll in corpus:
        by_reference: dict[str, list[dict]] = {}
        for fragment in scroll.get("fragments", []):
            for line in fragment.get("lines", []):
                words_by_reference: dict[str, list[str]] = {}
                for word in line.get("words", []):
                    if (not isinstance(word, (list, tuple)) or len(word) < 6
                            or not isinstance(word[5], str) or word[5] not in references):
                        continue
                    words_by_reference.setdefault(word[5], []).append(word[1])
                for reference, words in words_by_reference.items():
                    item = {
                        "fragment": fragment.get("id", ""),
                        "line": line.get("n", ""),
                        "diplomatic_text": " ".join(words),
                    }
                    if include_line_context:
                        item["line_context"] = {
                            "diplomatic_text": " ".join(w[1] for w in line.get("words", [])
                                                         if isinstance(w, (list, tuple)) and len(w) >= 2),
                            "selected_word_indices": [
                                index for index, w in enumerate(line.get("words", []))
                                if isinstance(w, (list, tuple)) and len(w) >= 6 and w[5] == reference
                            ],
                            "index_basis": "zero-based positions in original line words",
                            "preservation_assessed": False,
                            "warning": "Full current line only; supply may start on an earlier physical line. Check edition context.",
                        }
                    by_reference.setdefault(reference, []).append(item)
        for reference, lines in by_reference.items():
            results[reference].append({"manuscript_id": scroll.get("scroll", ""), "lines": lines})
    return results


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("qdr_json", type=Path, help="Path to qdr.*.biblical.json")
    parser.add_argument("--reference", action="append", required=True, dest="references")
    parser.add_argument("--include-line-context", action="store_true",
                        help="Include unfiltered physical-line context; does not adjudicate preservation")
    args = parser.parse_args(argv)

    corpus = json.loads(args.qdr_json.read_text())
    try:
        results = extract_passages(corpus, set(args.references), include_line_context=args.include_line_context)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps({"source": str(args.qdr_json),
                      "reference_annotations": reference_annotation_audit(corpus),
                      "results": results}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
