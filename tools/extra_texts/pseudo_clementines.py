#!/usr/bin/env python3
"""Acquire/check pinned Greek sources; prepare prompts, never publish translations.

The First1KGreek TEI is licensed CC BY-SA 4.0. Raw bytes are preserved;
sections.json is a whitespace-normalized derivative under the same license.
No model or credential access is needed by this source-only tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = ROOT / "sources/early_christian_texts"
UPSTREAM_COMMIT = "03776b39f4047c5cff06f5296fae4b2bae4b08fb"
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"
STRATEGY = "first1k_greek_tei_source_only"
NS = {"t": "http://www.tei-c.org/ns/1.0"}
WORKS = {
    "pseudo_clementine_peter_to_james": ("003", "PCPET", "Pseudo-Clementine Letter of Peter to James", [3]),
    "pseudo_clementine_contestation": ("004", "PCDIA", "Pseudo-Clementine Contestation", [5]),
    "pseudo_clementine_clement_to_james": ("005", "PCCLE", "Pseudo-Clementine Letter of Clement to James", [20]),
    "pseudo_clementine_homilies": ("006", "PCHOM", "Pseudo-Clementine Homilies", [22, 53, 73, 25, 30, 26, 12, 24, 23, 26, 36, 33, 21, 12, 11, 21, 20, 23, 14]),
}
TRANSLATION_POLICY = {
    "status": "not_generated",
    "draft_basis": "Greek source text, not an existing English translation",
    "source_check": "required_before_reader_publication",
    "review_status": "not_started",
    "required_review_evidence": [
        "source XML SHA-256 and exact CTS passage reference",
        "normalized Greek passage SHA-256 and English draft SHA-256",
        "generator model, prompt hash and generation timestamp",
        "separate source-comparison pass with reviewer identity, method and timestamp",
        "clause-by-clause coverage, lexical decisions, additions and omissions checked",
        "unresolved issues, source defects and proposed corrections explicitly recorded",
        "accepted verdict bound to the current source and translation hashes",
        "output rights and attribution reviewed before CC BY-only reader export",
    ],
    "publication": "blocked; source registration and structural checks are not translation approval",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def dump(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def source_url(text_id: str) -> str:
    number = WORKS[text_id][0]
    return f"https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/{UPSTREAM_COMMIT}/data/tlg1271/tlg{number}/tlg1271.tlg{number}.1st1K-grc1.xml"


def parse_source(raw: bytes, text_id: str) -> list[dict]:
    """Preserve section numbering, headings and pb tails; reject unknown markup."""
    number, _, _, counts = WORKS[text_id]
    tree = ET.fromstring(raw)
    license_node = tree.find(".//t:publicationStmt/t:availability/t:licence", NS)
    if license_node is None or license_node.get("target") != LICENSE_URL:
        raise ValueError("Missing or changed upstream license")
    edition = tree.find("t:text/t:body/t:div[@type='edition']", NS)
    urn = f"urn:cts:greekLit:tlg1271.tlg{number}.1st1K-grc1"
    if edition is None or edition.get("n") != urn:
        raise ValueError("Unexpected edition identity")
    if edition.get("{http://www.w3.org/XML/1998/namespace}lang") != "grc":
        raise ValueError("Expected Greek edition")
    allowed = {f"{{{NS['t']}}}{name}" for name in ("div", "p", "head", "pb")}
    if any(node.tag not in allowed for node in edition.iter()):
        raise ValueError("Unrecognized TEI markup requires parser review")
    rows = []
    extracted_blocks = []

    def walk(node: ET.Element, parents: list[str]) -> None:
        ref = parents + ([node.attrib["n"]] if node.get("type") == "textpart" else [])
        if node.get("subtype") == "section":
            if node.findall("t:div", NS):
                raise ValueError("Unexpected nested section")
            blocks = [child for child in node if child.tag in {f"{{{NS['t']}}}p", f"{{{NS['t']}}}head"}]
            extracted_blocks.extend(blocks)
            text = "\n\n".join(
                re.sub(r"\s+", " ", "".join(child.itertext())).strip()
                for child in blocks
            )
            if not text:
                raise ValueError("Empty Greek section")
            reference = ".".join(ref)
            rows.append({
                "reference": reference, "cts_urn": f"{urn}:{reference}",
                "source_text": text, "source_text_sha256": sha256(text.encode()),
                "page_breaks_within_section": [p.attrib for p in node.findall(".//t:pb", NS)],
            })
        else:
            for child in node.findall("t:div", NS):
                walk(child, ref)

    walk(edition, [])
    all_blocks = [node for node in edition.iter() if node.tag in {f"{{{NS['t']}}}p", f"{{{NS['t']}}}head"}]
    if extracted_blocks != all_blocks:
        raise ValueError("Unmapped prose or headings require parser review")
    expected = (
        [f"{ch}.{s}" for ch, count in enumerate(counts, 1) for s in range(1, count + 1)]
        if number == "006" else [str(s) for s in range(1, counts[0] + 1)]
    )
    if [r["reference"] for r in rows] != expected:
        raise ValueError("Source passage inventory changed: review gaps/order before updating")
    return rows


def coverage(text_id: str) -> dict:
    incomplete = WORKS[text_id][0] == "006"
    return {
        "status": "incomplete_work" if incomplete else "supplied_file_structurally_complete",
        "last_supplied_reference": "19.14" if incomplete else str(WORKS[text_id][3][0]),
        "expected_homilies": 20 if incomplete else None,
        "supplied_homilies": 19 if incomplete else None,
        "missing": ["remainder after Homily 19.14, including Homily 20"] if incomplete else [],
        "note": "Coverage is of the supplied 1847 edition file, not a claim of manuscript collation or philological accuracy. Never generate missing Greek or English to fill this source gap.",
    }


def acquire(text_id: str, root: Path = SOURCE_ROOT) -> None:
    directory = root / text_id
    if any((directory / name).exists() for name in ("source.xml", "sections.json", "manifest.json")):
        raise ValueError(f"Refusing to overwrite an acquired source: {text_id}")
    with urllib.request.urlopen(source_url(text_id), timeout=60) as response:
        raw = response.read()
    rows = parse_source(raw, text_id)
    number, _, title, _ = WORKS[text_id]
    manifest = {
        "text_id": text_id, "title": title, "collection": "pseudo_clementine_literature",
        "historical_status": "Historical early-Christian literature; not an attribution of genuine authorship to Peter or Clement, and not additional canonical Scripture.",
        "source_language": "Greek", "unit": "editorial_section", "expected_units": len(rows),
        "upstream": {"repository": "OpenGreekAndLatin/First1KGreek", "commit": UPSTREAM_COMMIT,
                     "url": source_url(text_id), "sha256": sha256(raw), "snapshot": "source.xml"},
        "edition": {"editor": "Albert Schwegler", "title": "Clementis Romani quae feruntur homiliae", "year": 1847},
        "rights": {"license": "CC-BY-SA-4.0", "license_url": LICENSE_URL,
                   "scope": "Imported XML and normalized Greek sections; not relicensed under the repository's CC BY 4.0 license.",
                   "attribution": "Open Greek and Latin / First1KGreek; Albert Schwegler (1847 edition). Full contributors, funding, proofreading, conversion, and revision credits retained in the TEI header.",
                   "changes": "XML unchanged; sections.json extracts headings/prose with normalized whitespace and preserves CTS references. Page-break metadata retained separately. No spelling corrections or gap filling."},
        "coverage": coverage(text_id), "translation_policy": TRANSLATION_POLICY,
        "review": {"structural": "parsed_and_inventory_checked", "philological": "not_started", "manuscript_collation": "not_performed"},
    }
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "source.xml").write_bytes(raw)
    (directory / "sections.json").write_text(dump(rows), encoding="utf-8")
    (directory / "manifest.json").write_text(dump(manifest), encoding="utf-8")


def validate_source(text_id: str, root: Path = SOURCE_ROOT) -> list[str]:
    try:
        directory = root / text_id
        manifest = json.loads((directory / "manifest.json").read_text())
        raw = (directory / "source.xml").read_bytes()
        rows = parse_source(raw, text_id)
        checks = {
            "identity": manifest["text_id"] == text_id and manifest["title"] == WORKS[text_id][2],
            "source hash": manifest["upstream"]["sha256"] == sha256(raw),
            "pinned source": manifest["upstream"]["commit"] == UPSTREAM_COMMIT and manifest["upstream"]["url"] == source_url(text_id),
            "normalized source": json.loads((directory / "sections.json").read_text()) == rows,
            "inventory": manifest["expected_units"] == len(rows) and manifest["unit"] == "editorial_section",
            "license": manifest["rights"]["license"] == "CC-BY-SA-4.0" and manifest["rights"]["license_url"] == LICENSE_URL,
            "coverage": manifest["coverage"] == coverage(text_id),
            "translation gate": manifest["translation_policy"] == TRANSLATION_POLICY,
            "review status": manifest["review"] == {"structural": "parsed_and_inventory_checked", "philological": "not_started", "manuscript_collation": "not_performed"},
        }
        return [f"{text_id}: invalid {name}" for name, ok in checks.items() if not ok]
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as exc:
        return [f"{text_id}: {exc}"]


def draft_prompt(text_id: str, reference: str, root: Path = SOURCE_ROOT) -> dict:
    errors = validate_source(text_id, root)
    if errors:
        raise ValueError("; ".join(errors))
    rows = json.loads((root / text_id / "sections.json").read_text())
    row = next((r for r in rows if r["reference"] == reference), None)
    if row is None:
        raise ValueError("Passage is not present in the acquired Greek source; do not invent it")
    return {
        "work": WORKS[text_id][2], "source": row,
        "source_snapshot": json.loads((root / text_id / "manifest.json").read_text())["upstream"],
        "instructions": "Generate a fresh English draft directly from this Greek passage. Preserve every clause, argument, quotation, ambiguity and heading. Do not harmonize its theology with Scripture or another tradition. Do not copy an existing English translation, silently repair apparent Greek errors, or invent missing passages. Record lexical choices and source uncertainties separately. This is a draft, not an approved translation.",
        "required_followup": TRANSLATION_POLICY,
        "rights_notice": "This Greek source is CC BY-SA 4.0. Preserve its attribution; resolve English output rights before publication. A generated draft is not automatically eligible for the CC BY-only reader.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("acquire", "check", "prompt"))
    parser.add_argument("--work", choices=WORKS)
    parser.add_argument("--reference")
    args = parser.parse_args()
    if args.action == "prompt":
        if not args.work or not args.reference:
            parser.error("prompt requires --work and --reference")
        print(dump(draft_prompt(args.work, args.reference)), end="")
        return 0
    errors = []
    for text_id in ([args.work] if args.work else WORKS):
        if args.action == "acquire":
            acquire(text_id)
        errors.extend(validate_source(text_id))
    if errors:
        print("\n".join(errors))
        return 1
    print("Greek source hashes, section inventories, licensing and translation gates validated. No English translation generated or approved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
