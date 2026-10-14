"""Inventory editorial uncertainty, not newly recovered manuscript readings."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

NS = "{http://www.tei-c.org/ns/1.0}"
UPSTREAM = "https://github.com/itsee-birmingham/codex-zacynthius-xml"
REVISION = "1dceaa3f798abda1b2df74ffbc0ed47abce40a7f"
EXPECTED_SHA256 = "789dbe9d7840b8d224f925c7ce50d79aca260b6adabc326b646a9efa8e56bdd0"


def inventory(data):
    root = ET.fromstring(data)
    if root.tag != NS + "TEI":
        raise ValueError("Expected TEI XML, not an archive error page")
    parents = {child: parent for parent in root.iter() for child in parent}
    counts = Counter()
    candidates = []
    folio = line = None
    for node in root.iter():
        tag = node.tag.removeprefix(NS)
        if tag == "pb":
            folio, line = node.get("n"), None
        elif tag == "lb":
            line = node.get("n")
        if tag not in {"unclear", "supplied", "gap"}:
            continue
        counts[(tag, node.get("reason", ""), node.get("source", ""))] += 1
        # Keep all unclear spans and transcriber supplements, without silently
        # promoting either category to a genuinely unresolved biblical word.
        if tag != "unclear" and not (tag == "supplied" and node.get("source") == "transcriber"):
            continue
        ancestors = []
        parent = parents.get(node)
        while parent is not None:
            ancestors.append(parent)
            parent = parents.get(parent)
        verse = next((p.get("n") for p in ancestors if p.tag == NS + "ab"), None)
        word = next((p for p in ancestors if p.tag == NS + "w"), None)
        reading = next((p for p in ancestors if p.tag == NS + "rdg"), None)
        marginal = any(p.tag == NS + "seg" and p.get("type") == "margin" for p in ancestors)
        placement = next((p for p in ancestors if p.tag == NS + "seg"), None)
        paratext = marginal or any(p.tag == NS + "fw" or
                                   (p.tag == NS + "num" and p.get("type") == "chapNum")
                                   for p in ancestors)
        candidates.append({
            "folio": folio, "line_label": line, "verse_label": verse,
            "element": tag, "reason": node.get("reason"), "source": node.get("source"),
            "editorial_text": "".join(node.itertext()),
            "word_context": " ".join("".join(word.itertext()).split()) if word is not None else None,
            "marginal": marginal,
            "paratext": paratext,
            "placement_target": placement.get("n") if placement is not None else None,
            "hand": reading.get("hand") if reading is not None else None,
            "reading_type": reading.get("type") if reading is not None else None,
            "status": "published_editorial_annotation_not_new_observation",
        })
    return {
        "source": {"repository": UPSTREAM, "revision": REVISION,
                   "filename": "Zacynthius-gospel.xml", "sha256": hashlib.sha256(data).hexdigest(),
                   "attribution": "Codex Zacynthius Project; R. Kevern, P. Manafis, A.C. Myshrall, H.A.G. Houghton",
                   "license": "CC BY 4.0", "modification": "Derived annotation inventory; not a transcription revision"},
        "count_unit": "XML elements, not letters, words, or independent readings",
        "selection": "All unclear elements and supplied elements with source=transcriber",
        "accepted_new_characters": 0,
        "counts": [{"element": key[0], "reason": key[1] or None, "source": key[2] or None, "count": count}
                   for key, count in sorted(counts.items())],
        "candidates": candidates,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xml", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = args.xml.read_bytes()
    if hashlib.sha256(data).hexdigest() != EXPECTED_SHA256:
        parser.error("Input differs from the pinned upstream transcription; provenance must be reviewed")
    result = inventory(data)
    args.output.write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded {len(result['candidates'])} editorial annotations; zero new readings.")


if __name__ == "__main__":
    main()
