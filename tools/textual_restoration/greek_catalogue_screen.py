"""Offline metadata screen of the primary Göttingen catalogue, never a collation.

Raw catalogue pages stay outside Git. Output contains factual identifiers,
counts and navigation only, not descriptions, bibliographies or transcriptions.
Date-filter matches are upstream discovery selections, not our date judgments.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

from tools.textual_restoration.build_qdr_discovery import BOOKS

BASE = "https://septuaginta.uni-goettingen.de"
CONTROLS = {
    "A": "codex-alexandrinus-ot", "B": "codex-vaticanus-1209",
    "S": "codex-sinaiticus", "801": "4q119-greek-leviticus",
    "802": "4q120-greek-leviticus", "803": "4q121-greek-numbers",
    "819": "4q122-greek-deuteronomy", "805": "7q1-greek-exodus",
    "943": "8hev-greek-minor-prophets",
}
# Exact catalogue abbreviations only: no guessed numbering/genre normalization.
BOOK_LABELS = {
    "Gen.": "Gen", "Exod.": "Exod", "Lev.": "Lev", "Num.": "Num",
    "Deut.": "Deut", "Ios.": "Josh", "Iud.": "Judg", "Ruth": "Ruth",
    "Esther": "Esth", "Est.": "Esth", "Iob": "Job", "Ps.": "Ps", "Ps": "Ps", "Psalmi": "Ps", "Prov.": "Prov",
    "Eccl.": "Eccl", "Cant.": "Song", "Is.": "Isa", "Ier.": "Jer",
    "Thren.": "Lam", "Thr.": "Lam", "Ez.": "Ezek", "Ezech.": "Ezek", "Dan.": "Dan", "Os.": "Hos",
    "Ioel": "Joel", "Am.": "Amos", "Abd.": "Obad", "Ion.": "Jonah",
    "Mich.": "Mic", "Nah.": "Nah", "Hab.": "Hab", "Soph.": "Zeph",
    "Agg.": "Hag", "Zach.": "Zech", "Mal.": "Mal",
}
BOOK_LABELS.update({"Ex.": "Exod", "Dtn.": "Deut", "I Reg.": "1Sam",
                    "II Reg.": "2Sam", "Reg. II": "2Sam", "III Reg.": "1Kgs",
                    "IV Reg.": "2Kgs", "I Paralip.": "1Chr", "I Par.": "1Chr",
                    "II Paralip.": "2Chr", "II Par.": "2Chr"})
GROUP_LABELS = {"I–II Reg.": ["1Sam", "2Sam"], "III–IV Reg.": ["1Kgs", "2Kgs"],
                "I–II Paralip.": ["1Chr", "2Chr"]}


class TextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def plain(value):
    p = TextParser()
    p.feed(value)
    return " ".join("".join(p.parts).split())


def book_labels(entry):
    """Explicit folio book-label or anchored content prefix, not inferred context."""
    folio, content = (plain(entry.get(k, "")) for k in ("folioRangeHtml", "contentHtml"))
    if folio in BOOK_LABELS:
        return [BOOK_LABELS[folio]], "explicit-book-label"
    assigned = []
    # A row may explicitly name two contents: "Iud. 20:22–28. Ruth 2:19–3:7".
    # Only sentence-start prefixes, never arbitrary incidental mentions.
    alternatives = "|".join(re.escape(label) for label in sorted(
        set(BOOK_LABELS) | set(GROUP_LABELS), key=len, reverse=True))
    first = re.match(r"^(" + alternatives + r")(?=\s|:|$)", content)
    if not first:
        return [], "unresolved"
    assigned.extend(GROUP_LABELS.get(first[1], [BOOK_LABELS.get(first[1])]))
    previous_end = first.end()
    for match in re.finditer(r"(?<=\.)\s+(" + alternatives + r")(?=\s|:|$)", content):
        separator = content[previous_end:match.start()]
        if not re.fullmatch(r"[0-9a-d:\s.,;()\[\]–—-]+", separator) or not re.search(r"[0-9]", separator):
            break
        label = match[1]
        assigned.extend(GROUP_LABELS.get(label, [BOOK_LABELS.get(label)]))
        previous_end = match.end()
    if assigned:
        return list(dict.fromkeys(assigned)), "explicit-content-prefix"
    return [], "unresolved"


class PayloadParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.active = False
        self.parts = []
        self.matches = 0

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("id") == "manuscript-description-data":
            self.active = True
            self.matches += 1

    def handle_endtag(self, tag):
        if tag == "script":
            self.active = False

    def handle_data(self, data):
        if self.active:
            self.parts.append(data)


def detail_payload(raw: str) -> dict:
    parser = PayloadParser()
    parser.feed(raw)
    if parser.matches != 1:
        raise ValueError("Exactly one advertised manuscript description payload required")
    result = json.loads("".join(parser.parts))
    if type(result.get("canRead")) is not bool:
        raise ValueError("Explicit boolean canRead required")
    return result


def validate_pages(pages: list[dict]) -> list[dict]:
    if not pages:
        raise ValueError("No catalogue pages")
    count, limit, number = (pages[0].get(k) for k in ("count", "limit", "numPages"))
    if any(type(v) is not int or v < 1 for v in (count, limit, number)):
        raise ValueError("Invalid pagination totals")
    if len(pages) != number or number != (count + limit - 1) // limit:
        raise ValueError("Missing catalogue pages")
    rows = []
    for index, page in enumerate(pages, 1):
        start, end = (index - 1) * limit + 1, min(index * limit, count)
        expected = {"count": count, "limit": limit, "numPages": number,
                    "page": index, "startIndex": start, "endIndex": end,
                    "hasPrevious": index > 1, "hasNext": index < number,
                    "previousPage": index - 1 if index > 1 else None,
                    "nextPage": index + 1 if index < number else None}
        if any(page.get(k) != v for k, v in expected.items()):
            raise ValueError(f"Inconsistent page {index}")
        if len(page.get("results", [])) != end - start + 1:
            raise ValueError(f"Truncated page {index}")
        rows.extend(page["results"])
    ids = [row.get("id") for row in rows]
    if any(type(i) is not int or i < 1 for i in ids) or len(set(ids)) != count:
        raise ValueError("Duplicate or missing catalogue IDs")
    for row in rows:
        if not isinstance(row.get("name"), str) or not row["name"]:
            raise ValueError("Missing catalogue name")
        if not isinstance(row.get("url"), str) or not re.fullmatch(r"/catalogue/[\w-]+/", row["url"]):
            raise ValueError("Unexpected catalogue URL")
    return rows


def summarize(all_pages: list[dict], overlap: dict, contained: dict,
              details: dict[int, dict], registry: dict) -> dict:
    all_rows = validate_pages(all_pages)
    early = validate_pages([overlap])
    strict = validate_pages([contained])
    if overlap.get("emptyDateMatch") is not False or contained.get("emptyDateMatch") is not False:
        raise ValueError("Date filter was not applied")
    all_by_id = {row["id"]: row for row in all_rows}
    early_ids, strict_ids = ({row["id"] for row in group} for group in (early, strict))
    if not strict_ids <= early_ids <= set(all_by_id):
        raise ValueError("Filter records are not subsets of full catalogue")
    if any(all_by_id[row["id"]]["name"] != row["name"] for row in early + strict):
        raise ValueError("Identity drift between snapshots")
    if set(details) != early_ids:
        raise ValueError("Every early candidate needs an explicit detail status")

    registry_ids = {row["id"] for row in registry["witnesses"]}
    if not set(CONTROLS.values()) <= registry_ids:
        raise ValueError("Existing registry control disappeared")
    by_name = {}
    for row in all_rows:
        by_name.setdefault(row["name"], []).append(row)
    if any(len(by_name.get(name, [])) > 1 for name in CONTROLS):
        raise ValueError("Ambiguous registry catalogue-name control")
    controls = []
    for name, identifier in CONTROLS.items():
        match = by_name.get(name, [])
        controls.append({"registry_id": identifier, "catalogue_name": name,
                         "catalogue_id": match[0]["id"] if match else None,
                         "present_in_full_list": bool(match),
                         "in_date_overlap": bool(match and match[0]["id"] in early_ids),
                         "absence_is_not_object_absence": True})

    candidates, books, statuses = [], {book: [] for book in BOOKS}, Counter()
    for row in early:
        payload = details[row["id"]]
        status = payload.get("access_status")
        if status not in {"readable", "unavailable", "fetch-failed"}:
            raise ValueError("Unknown detail status")
        statuses[status] += 1
        item = {"catalogue_id": row["id"], "catalogue_name": row["name"],
                "url": BASE + row["url"], "detail_access": status,
                "upstream_date_overlap": True, "upstream_date_contained": row["id"] in strict_ids,
                "list_content_blank": not row.get("contentDescription", "").strip(),
                "list_image_flag": bool(row.get("hasImages")),
                "list_iiif_flag": bool(row.get("hasIiif")),
                "specific_book_navigation": [], "unresolved_content_row_count": 0,
                "unresolved_content_row_ordinals": [],
                "passage_letter_survival_verified": False,
                "independent_physical_object_verified": False}
        if status == "readable":
            d = payload["data"]
            if d.get("canRead") is not True or d.get("manuscript", {}).get("id") != row["id"]:
                raise ValueError("Readable detail identity/access mismatch")
            item["rid"] = d["manuscript"]["rid"]
            item["license_url"] = d.get("footer", {}).get("licenseUrl", "")
            overview = d.get("contentOverview", [])
            item["content_overview_rows"] = len(overview)
            item["missing_structured_ranges"] = not overview
            for ri, entry in enumerate(overview):
                assigned, basis = book_labels(entry)
                # HTML/range markup and dual numbering are left for manual alignment.
                if assigned:
                    nav = {"books": assigned, "detail_row_zero_based": ri, "basis": basis,
                           "reported_range_sha256": hashlib.sha256(entry.get("contentHtml", "").encode()).hexdigest(),
                           "range_normalized_to_pob": False}
                    item["specific_book_navigation"].append(nav)
                    for book in assigned:
                        books[book].append(row["id"])
                else:
                    item["unresolved_content_row_count"] += 1
                    item["unresolved_content_row_ordinals"].append(ri)
        candidates.append(item)
    return {
        "record_version": 1,
        "scope": "Complete fetched catalogue-list snapshot and bounded upstream early-date Greek detail cohort; not all global OT witnesses",
        "full_list": {"records": len(all_rows), "pages": len(all_pages),
                      "unique_ids": len(all_by_id),
                      "state_counts": dict(sorted(Counter(row.get("state", "") for row in all_rows).items())),
                      "duplicate_name_count": sum(len(v) > 1 for v in by_name.values())},
        "date_screen": {"year_from": -400, "year_to": 400, "language": "grc",
                        "overlap_mode": "option3", "contained_mode": "option2",
                        "overlap_records": len(early), "contained_records": len(strict),
                        "overlap_only_ids": sorted(early_ids - strict_ids),
                        "is_independent_dating": False},
        "detail_status_counts": dict(sorted(statuses.items())),
        "registry_controls": controls,
        "candidates": candidates,
        "pob_book_navigation": [{"book": book, "folder": folder,
                                 "specific_structured_detail_ids": sorted(set(books[book])),
                                 "zero_is_not_witness_absence": True}
                                for book, folder in BOOKS.items()],
        "policy": {"catalogue_rows_are_independent_manuscripts": False,
                   "book_navigation_is_preserved_text": False,
                   "date_filter_is_complete_ancient_census": False,
                   "raw_description_exported": False,
                   "images_or_transcriptions_imported": False,
                   "canonical_source_or_english_changed": False,
                   "imagegen_is_evidence": False},
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--overlap", type=Path, required=True)
    parser.add_argument("--contained", type=Path, required=True)
    args = parser.parse_args(argv)
    manifest_raw = args.manifest.read_bytes()
    manifest = json.loads(manifest_raw)
    inputs = []

    def read(item):
        raw = Path(item["path"]).read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        if actual != item["sha256"]:
            raise ValueError(f"Input byte hash mismatch: {item['path']}")
        inputs.append({"path": item["path"], "sha256": actual, "url": item["url"]})
        return raw

    pages = [json.loads(read({**p, "url": manifest["list_query_template"].format(page=p["page"])}))
             for p in manifest["pages"]]
    def filter_read(path, mode):
        raw = path.read_bytes()
        inputs.append({"path": str(path), "sha256": hashlib.sha256(raw).hexdigest(),
                       "url": BASE + "/catalogue/data/?yearFrom=-400&yearTo=400&dateMatch="
                       + mode + "&language=grc&limit=200"})
        return json.loads(raw)
    overlap = filter_read(args.overlap, "option3")
    contained = filter_read(args.contained, "option2")
    details = {}
    for item in manifest["details"]:
        identifier = item["id"]
        if identifier in details:
            raise ValueError("Duplicate detail acquisition")
        if item.get("status") == "fetch-failed":
            details[identifier] = {"access_status": "fetch-failed"}
            continue
        d = detail_payload(read(item).decode())
        details[identifier] = {"access_status": "readable" if d["canRead"] else "unavailable"}
        if d["canRead"]:
            details[identifier]["data"] = d
    raw_registry = args.registry.read_bytes()
    result = summarize(pages, overlap, contained, details, json.loads(raw_registry))
    result["checked_date"] = manifest["checked_date"]
    result["acquisition_inputs"] = inputs
    control = manifest.get("supplemental_blocked_control")
    if control:
        d = detail_payload(read(control).decode())
        if d["canRead"] is not False:
            raise ValueError("Supplemental blocked control changed access state")
        result["supplemental_blocked_control"] = {
            "catalogue_name": control["name"], "url": control["url"],
            "can_read": False, "outside_early_cohort": True,
            "sha256": control["sha256"], "is_object_absence": False}
    result["rights"] = {"raw_records_retained_privately": True,
                        "readable_detail_license_counts": dict(Counter(
                            v["data"].get("footer", {}).get("licenseUrl", "")
                            for v in details.values() if v["access_status"] == "readable")),
                        "distinctive_descriptions_and_images_relicensed": False}
    result["private_manifest_sha256"] = hashlib.sha256(manifest_raw).hexdigest()
    result["registry_sha256"] = hashlib.sha256(raw_registry).hexdigest()
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
