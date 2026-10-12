"""Assemble selected Greek from checked print lines, never unreviewed OCR."""
from __future__ import annotations

import json
from pathlib import Path
import re
import unicodedata

from tools.extra_texts import pseudo_clementine_pages as pages


def normalized_lines(lines: list[str]) -> str:
    text = "\n".join(lines).replace("|", "")
    # Join only a physical line-ending hyphen, not an internal lexical dash.
    text = re.sub(r"-\n(?=[\u0370-\u03ff\u1f00-\u1fff])", "", text)
    return unicodedata.normalize("NFC", re.sub(r"\s+", " ", text).strip())


def load_page(number: int) -> tuple[list[str], dict]:
    selections_path = pages.SOURCE / "page_selections.json"
    selections = json.loads(selections_path.read_text()) if selections_path.exists() else {}
    series = selections.get(str(number), "pages-blind")
    if not re.fullmatch(r"pages-[a-z-]+", series):
        raise ValueError("Invalid selected page-evidence series")
    directory = pages.SOURCE / series / f"{number:03d}"
    checked = pages.verify_checked(directory, None)
    lines = list(checked["body_lines"])
    proof = {"pdf_page": number, "printed_page": checked["printed_page"],
             "checked_path": str((directory / "checked.json").relative_to(pages.ROOT)),
             "checked_sha256": pages.sha((directory / "checked.json").read_bytes()),
             "adjudications": []}
    if checked.get("supplemental_source"):
        proof["supplemental_source"] = checked["supplemental_source"]
    adjudication_file = directory / "line-adjudications.json"
    if adjudication_file.exists():
        for item in json.loads(adjudication_file.read_text()):
            index = item["line"] - 1
            if lines[index] != item["before"]:
                raise ValueError("Adjudication no longer targets the exact reviewed line")
            response_path = pages.ROOT / item["review_response"]
            if pages.sha(response_path.read_bytes()) != item["review_response_sha256"]:
                raise ValueError("Crop-review evidence changed")
            response = json.loads(response_path.read_text())
            if not str(response.get("model", "")).startswith("gpt-6.1-sol-"):
                raise ValueError("Adjudication lacks requested review model")
            readback = pages.parse_response(response)["text"]
            readback = re.sub(r"^\d+\s+", "", readback)  # disclosed printed margin number
            if item.get("scope") == "single_word":
                before_word, after_word = item["before_word"], item["after_word"]
                if any(c.isspace() for c in before_word + after_word) or not before_word or not after_word:
                    raise ValueError("Word adjudication cannot replace an unreviewed clause")
                if item["before"].count(before_word) != 1 or item["after"] != item["before"].replace(before_word, after_word, 1):
                    raise ValueError("Scoped correction changed more than its reviewed word")
                if unicodedata.normalize("NFC", after_word) not in unicodedata.normalize("NFC", readback):
                    raise ValueError("Corrected word is absent from crop review")
            elif unicodedata.normalize("NFC", readback) != unicodedata.normalize("NFC", item["after"]):
                raise ValueError("Adjudicated text is not the actual blind crop reading")
            request_path = pages.ROOT / item["review_request"]
            if pages.sha(request_path.read_bytes()) != item["review_request_sha256"]:
                raise ValueError("Crop request evidence changed")
            request = json.loads(request_path.read_text())
            if request["pdf_page"] != number or request["crop_sha256"] != item["crop_sha256"]:
                raise ValueError("Crop review is for another source page")
            lines[index] = item["after"]
            proof["adjudications"].append(item)
    return lines, proof


DOCUMENTS = {
    "pseudo_clementine_contestation": (46, 48, "Διαμαρτυρία", "Ἐπιστολὴ Κλήμεντος", 5),
    "pseudo_clementine_clement_to_james": (48, 54, "Ἐπιστολὴ Κλήμεντος", "Κλήμεντος τῶν Πέτρου ἐπιδημίων", 20),
}
# Some section numbers are printed at the start of a physical line without
# a period (Clement section 11, verified on printed p.9 / PDF p.51).
SECTION_MARKER = re.compile(r"(?<!\S)(\d{1,2})\.\s*|^(\d{1,2})\s+(?=[\u0370-\u03ff\u1f00-\u1fff])")


def assemble_document(work: str) -> dict:
    first, last, opening, closing, expected = DOCUMENTS[work]
    all_lines, proofs = [], []
    for number in range(first, last + 1):
        lines, proof = load_page(number)
        all_lines.extend((number, line) for line in lines)
        proofs.append(proof)
    starts = [i for i, (_, line) in enumerate(all_lines) if line.startswith(opening)]
    ends = [i for i, (_, line) in enumerate(all_lines) if line.startswith(closing)]
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        raise ValueError("Work boundaries are missing, duplicated or reversed")
    rows, fragments, cited_pages, current = [], [], set(), 1

    def finish() -> None:
        greek = normalized_lines(fragments)
        if not greek:
            raise ValueError("Empty source section")
        rows.append({"reference": str(current), "source_text": greek,
                     "source_text_sha256": pages.sha(greek.encode()),
                     "printed_pages": sorted(cited_pages)})

    for number, line in all_lines[starts[0] + 1:ends[0]]:
        cursor = 0
        for marker in SECTION_MARKER.finditer(line):
            prefix = line[cursor:marker.start()].strip()
            if prefix:
                fragments.append(prefix); cited_pages.add(number - 42)
            index = int(marker[1] or marker[2])
            if index == 1 and current == 1 and not fragments:
                pass  # Contestation prints its initial section number.
            else:
                if index != current + 1:
                    raise ValueError("Source section numbering is not contiguous")
                finish(); fragments = []; cited_pages = set(); current = index
            cursor = marker.end()
        tail = line[cursor:].strip()
        if tail:
            fragments.append(tail); cited_pages.add(number - 42)
    finish()
    if [r["reference"] for r in rows] != [str(i) for i in range(1, expected + 1)]:
        raise ValueError("Work's complete section inventory did not survive extraction")
    # No words may be dropped while separating printed section markers.
    without_markers = normalized_lines([SECTION_MARKER.sub("", line) for _, line in all_lines[starts[0] + 1:ends[0]]])
    if " ".join(r["source_text"] for r in rows) != without_markers:
        raise ValueError("Section extraction changed the normalized source text")
    manifest = json.loads((pages.SOURCE / "manifest.json").read_text())
    return {"work": work, "edition": manifest["edition"],
            "source_snapshot": {"url": manifest["pdf_url"], "sha256": manifest["pdf_sha256"], "kind": "independent_image_checked_print_transcription"},
            "source_license": "Public-domain ancient Greek and 1865 edition; original POB notes/contributions CC BY 4.0",
            "coverage": {"status": "complete_work", "sections": [r["reference"] for r in rows], "basis": "Verified printed work heading through the following work heading"},
            "normalization": "NFC; join physical end-line hyphens; collapse layout whitespace; remove old-edition pagination bars and section numerals; preserve printed wording, punctuation, spelling and gaps",
            "page_evidence": proofs, "passages": rows,
            "status": "checked_print_source_for_translation_not_reader_release"}



HOMILY_NUMERALS = {
    "Α": 1, "Β": 2, "Γ": 3, "Δ": 4, "Ε": 5, "Ϛ": 6, "ϛ": 6,
    "ΣΤ": 6, "Ζ": 7, "Η": 8, "Θ": 9, "Ι": 10, "ΙΑ": 11,
    "ΙΒ": 12, "ΙΓ": 13, "ΙΔ": 14, "ΙΕ": 15, "ΙϚ": 16,
    "Ιϛ": 16, "ΙΣΤ": 16, "ΙΖ": 17, "ΙΗ": 18, "ΙΘ": 19, "Κ": 20,
}


def extract_homilies(all_lines: list[tuple[int, str]], expected_homilies: int = 20) -> list[dict]:
    """Separate exact printed homily/section markers without dropping prose."""
    rows, fragments, cited_pages, body_lines = [], [], set(), []
    homily, section = 0, 1

    def finish() -> None:
        greek = normalized_lines(fragments)
        if not greek:
            raise ValueError("Empty Homilies section")
        rows.append({"reference": f"{homily}.{section}", "homily": homily,
                     "section": section, "source_text": greek,
                     "source_text_sha256": pages.sha(greek.encode()),
                     "printed_pages": sorted(cited_pages)})

    for number, line in all_lines:
        label = line.strip()
        chapter = HOMILY_NUMERALS.get(label)
        if chapter is not None:
            if chapter != homily + 1:
                raise ValueError("Homily numbering is not contiguous")
            if homily:
                finish()
            homily, section = chapter, 1
            fragments, cited_pages = [], set()
            continue
        if not homily:
            raise ValueError("Homilies text precedes its opening numeral")
        body_lines.append(SECTION_MARKER.sub("", line))
        cursor = 0
        for marker in SECTION_MARKER.finditer(line):
            prefix = line[cursor:marker.start()].strip()
            if prefix:
                fragments.append(prefix); cited_pages.add(number - 42)
            index = int(marker[1] or marker[2])
            if index == 1 and section == 1 and not fragments:
                pass
            else:
                if index != section + 1:
                    raise ValueError("Homilies section numbering is not contiguous")
                finish()
                fragments, cited_pages, section = [], set(), index
            cursor = marker.end()
        tail = line[cursor:].strip()
        if tail:
            fragments.append(tail); cited_pages.add(number - 42)
    if homily != expected_homilies:
        raise ValueError("Incomplete Homilies inventory")
    finish()
    if " ".join(row["source_text"] for row in rows) != normalized_lines(body_lines):
        raise ValueError("Homilies extraction changed normalized source words")
    return rows


def assemble_homilies() -> dict:
    all_lines, proofs = [], []
    for number in range(54, 242):
        lines, proof = load_page(number)  # Missing/unaccepted pages fail closed.
        all_lines.extend((number, line) for line in lines)
        proofs.append(proof)
    title = "Κλήμεντος τῶν Πέτρου ἐπιδημίων κηρυγμάτων ἐπιτομή."
    starts = [i for i, (_, line) in enumerate(all_lines) if line == title]
    if len(starts) != 1:
        raise ValueError("Homilies printed opening is missing or duplicated")
    rows = extract_homilies(all_lines[starts[0] + 1:])
    if rows[-1]["reference"] != "20.23" or not rows[-1]["source_text"].endswith("ἔσπευσεν."):
        raise ValueError("Homilies final section and ending are not verified")
    if rows[-1]["printed_pages"][-1] != 199:
        raise ValueError("Homilies ending moved from the final print page")
    manifest = json.loads((pages.SOURCE / "manifest.json").read_text())
    return {
        "work": "pseudo_clementine_homilies", "edition": manifest["edition"],
        "source_snapshot": {"url": manifest["pdf_url"], "sha256": manifest["pdf_sha256"],
                            "kind": "independent_image_checked_print_transcription"},
        "source_license": "Public-domain ancient Greek and 1865 edition; original POB notes/contributions CC BY 4.0",
        "coverage": {"status": "complete_work", "sections": [r["reference"] for r in rows],
                     "homilies": list(range(1, 21)),
                     "basis": "All checked print pages from the work heading through Homily 20.23 on printed page 199"},
        "normalization": "NFC; join physical end-line hyphens; collapse layout whitespace; remove old-edition pagination bars and section numerals; preserve printed wording, punctuation, spelling and gaps",
        "page_evidence": proofs, "passages": rows,
        "status": "checked_print_source_for_translation_not_reader_release",
    }

def assemble_peter() -> dict:
    first, first_proof = load_page(45)
    second, second_proof = load_page(46)
    if not first[0].startswith("Ἐπιστολὴ Πέτρου") or not first[1].startswith("Πέτρος"):
        raise ValueError("Peter-letter opening moved")
    boundary = [i for i, line in enumerate(second) if line.startswith("Διαμαρτυρία")]
    if len(boundary) != 1 or not second[boundary[0] - 1].endswith("ἔρρωσο."):
        raise ValueError("Peter-letter/Contestation boundary is not verified")
    text = normalized_lines(first[1:] + second[:boundary[0]])
    chunks = re.split(r" (?=[23]\. )", text)
    if len(chunks) != 3 or not chunks[1].startswith("2. ") or not chunks[2].startswith("3. "):
        raise ValueError("Peter-letter section inventory changed")
    rows = []
    for number, chunk in enumerate(chunks, 1):
        greek = re.sub(r"^[23]\. ", "", chunk)
        rows.append({"reference": str(number), "source_text": greek,
                     "source_text_sha256": pages.sha(greek.encode()), "printed_pages": [3, 4]})
    manifest = json.loads((pages.SOURCE / "manifest.json").read_text())
    return {"work": "pseudo_clementine_peter_to_james", "edition": manifest["edition"],
            "source_snapshot": {"url": manifest["pdf_url"], "sha256": manifest["pdf_sha256"],
                                "kind": "independent_image_checked_print_transcription"},
            "source_license": "Public-domain ancient Greek and 1865 edition; original POB notes/contributions CC BY 4.0",
            "coverage": {"status": "complete_work", "sections": ["1", "2", "3"], "basis": "printed heading through closing farewell before Contestation"},
            "normalization": "NFC; join physical end-line hyphens; collapse layout whitespace; remove old-edition pagination bars; preserve printed wording, spelling, punctuation and editorial gaps",
            "confirmed_print_features": [{"reference": "2", "source_quote": "ἐφοδιάζειν ἐφοδιάζωσιν", "evidence": "Both verbal forms are visibly printed on PDF p.45 body line 20 and retained by the checked independent transcription.", "translation_requirement": "Preserve the repetition and disclose its syntactic uncertainty. It is not an unverified OCR correction; do not silently delete a verb or assert that a conjectural shorter reading is the selected print."}],
            "page_evidence": [first_proof, second_proof], "passages": rows,
            "status": "checked_print_source_for_translation_not_reader_release"}


def load_selected(work: str) -> dict:
    if work == "pseudo_clementine_peter_to_james":
        actual = assemble_peter()
    elif work == "pseudo_clementine_homilies":
        actual = assemble_homilies()
    elif work in DOCUMENTS:
        actual = assemble_document(work)
    else:
        raise ValueError("This work has no complete selected-print-source assembler yet")
    path = pages.SOURCE / "selected" / f"{work}.json"
    if not path.exists() or json.loads(path.read_text()) != actual:
        raise ValueError("Selected source snapshot is missing or stale")
    return actual


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", choices=["pseudo_clementine_peter_to_james", "pseudo_clementine_homilies", *DOCUMENTS], default="pseudo_clementine_peter_to_james")
    args = parser.parse_args()
    result = (assemble_peter() if args.work == "pseudo_clementine_peter_to_james" else
              assemble_homilies() if args.work == "pseudo_clementine_homilies" else assemble_document(args.work))
    pages.save(pages.SOURCE / "selected" / f"{result['work']}.json", result)
    print(f"Selected {result['work']} source assembled from verified print evidence ({len(result['passages'])} sections).")
