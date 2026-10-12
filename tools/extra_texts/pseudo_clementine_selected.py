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
    directory = pages.SOURCE / "pages-blind" / f"{number:03d}"
    checked = pages.verify_checked(directory, None)
    lines = list(checked["body_lines"])
    proof = {"pdf_page": number, "printed_page": checked["printed_page"],
             "checked_path": str((directory / "checked.json").relative_to(pages.ROOT)),
             "checked_sha256": pages.sha((directory / "checked.json").read_bytes()),
             "adjudications": []}
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
    if work != "pseudo_clementine_peter_to_james":
        raise ValueError("This work has no complete selected-print-source assembler yet")
    actual = assemble_peter()
    path = pages.SOURCE / "selected" / f"{work}.json"
    if not path.exists() or json.loads(path.read_text()) != actual:
        raise ValueError("Selected source snapshot is missing or stale")
    return actual


if __name__ == "__main__":
    result = assemble_peter()
    pages.save(pages.SOURCE / "selected" / f"{result['work']}.json", result)
    print("Selected Peter-letter source assembled from verified print evidence (3 sections).")
