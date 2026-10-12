import copy
import json
import unittest

from tools.textual_restoration.greek_catalogue_screen import (
    BOOKS, CONTROLS, book_labels, detail_payload, summarize, validate_pages,
)


def page(rows, *, number=1, total=None, limit=None):
    total = len(rows) if total is None else total
    limit = total if limit is None else limit
    count_pages = (total + limit - 1) // limit
    return {"results": rows, "count": total, "limit": limit, "numPages": count_pages,
            "page": number, "startIndex": (number - 1) * limit + 1,
            "endIndex": min(number * limit, total), "hasPrevious": number > 1,
            "hasNext": number < count_pages, "previousPage": number - 1 if number > 1 else None,
            "nextPage": number + 1 if number < count_pages else None, "emptyDateMatch": False}


def row(identifier, name="943"):
    return {"id": identifier, "name": name, "url": f"/catalogue/Ra_{name}/",
            "state": "1", "contentDescription": "", "hasImages": True, "hasIiif": True}


class GreekCatalogueScreenTests(unittest.TestCase):
    def test_complete_pagination_keeps_distinct_blank_names(self):
        rows = [row(1, "–"), row(2, "–"), row(3, "S")]
        rows[0]["url"] = "/catalogue/D123/"
        rows[1]["url"] = "/catalogue/D124/"
        pages = [page(rows[:2], total=3, limit=2), page(rows[2:], number=2, total=3, limit=2)]
        self.assertEqual(validate_pages(pages), rows)

    def test_missing_or_inconsistent_page_is_not_completeness(self):
        p = page([row(1)], total=2, limit=1)
        with self.assertRaisesRegex(ValueError, "Missing"):
            validate_pages([p])
        q = page([row(2)], number=2, total=2, limit=1)
        p["nextPage"] = None
        with self.assertRaisesRegex(ValueError, "Inconsistent"):
            validate_pages([p, q])

    def test_duplicate_stable_id_or_unsafe_url_rejected(self):
        for rows in [[row(1), row(1)], [{**row(1), "url": "https://other.example/a"}],
                     [{**row(1), "url": "/catalogue/../private/"}]]:
            with self.assertRaises(ValueError):
                validate_pages([page(rows)])

    def test_payload_requires_single_explicit_access_flag(self):
        def html(d):
            return '<script id="manuscript-description-data" type="application/json">' + json.dumps(d) + '</script>'
        self.assertFalse(detail_payload(html({"canRead": False}))["canRead"])
        for raw in [html({}), html({"canRead": "true"}), html({"canRead": True}) * 2]:
            with self.assertRaises(ValueError):
                detail_payload(raw)

    def test_explicit_book_prefixes_and_greek_kingdom_numbering(self):
        examples = [("<em>Gen.</em> 1:1–5", ["Gen"]), ("Reg. II 15:1–3", ["2Sam"]),
                    ("III–IV Reg.: fragments", ["1Kgs", "2Kgs"]),
                    ("I–II Paralip.: lacunae", ["1Chr", "2Chr"]), ("Psalmi", ["Ps"]),
                    ("Iud. 20:22–28. Ruth 2:19–3:7 (both fragmentary)", ["Judg", "Ruth"])]
        for text, expected in examples:
            with self.subTest(text=text):
                self.assertEqual(book_labels({"contentHtml": text})[0], expected)
        self.assertEqual(book_labels({"folioRangeHtml": "Hab.", "contentHtml": "1:5–1:11"})[0], ["Hab"])

    def test_groups_other_corpus_typos_and_inherited_rows_are_held(self):
        for text in ["IIV Reg.", "II Esdras", "III Esdras", "Duodecim prophetae", "Corpus Ieremiae",
                     "Ioel–Mal. (Greek order)", "Ps.Sal. 1", "Ps.Od. fragm.", "Bel et Dr. 20–41",
                     "1:1–3", "106:1–3", "Prologue to Sir.", "N.T. + Barnabas",
                     "A fragment; cf. Gen. 1:1 in the bibliography.",
                     "Bibliography e.g. Ruth 2:1 is discussed."]:
            with self.subTest(text=text):
                self.assertEqual(book_labels({"contentHtml": text})[0], [])
        self.assertEqual(book_labels({"contentHtml": "Gen. 1:1 discussed. Ruth 2:1 is a comparison."})[0], ["Gen"])

    def fixture(self):
        r = row(1)
        p = page([r])
        registry = {"witnesses": [{"id": v} for v in CONTROLS.values()]}
        d = {"canRead": True, "manuscript": {"id": 1, "rid": "Ra_0943"},
             "contentOverview": [{"folioRangeHtml": "Hab.", "contentHtml": "1:5–1:11"}],
             "description": {"generalHtml": "not exported", "commentHtml": "not exported"}}
        return [p], p, copy.deepcopy(p), {1: {"access_status": "readable", "data": d}}, registry

    def test_all_book_rows_and_no_description_or_ink_claim(self):
        result = summarize(*self.fixture())
        self.assertEqual(len(result["pob_book_navigation"]), 39)
        self.assertEqual({r["book"] for r in result["pob_book_navigation"]}, set(BOOKS))
        hab = next(r for r in result["pob_book_navigation"] if r["book"] == "Hab")
        self.assertEqual(hab["specific_structured_detail_ids"], [1])
        self.assertNotIn("not exported", json.dumps(result))
        self.assertFalse(result["candidates"][0]["passage_letter_survival_verified"])

    def test_filter_missing_details_identity_and_registry_guards(self):
        for mutate in [lambda f: f[1].update(emptyDateMatch=True),
                       lambda f: f[3].clear(),
                       lambda f: f[3][1]["data"]["manuscript"].update(id=2),
                       lambda f: f[4]["witnesses"].clear()]:
            f = self.fixture()
            mutate(f)
            with self.assertRaises(ValueError):
                summarize(*f)

    def test_unavailable_payload_is_not_read_even_if_fields_exist(self):
        f = self.fixture()
        f[3][1] = {"access_status": "unavailable", "data": f[3][1]["data"]}
        result = summarize(*f)
        self.assertEqual(result["detail_status_counts"], {"unavailable": 1})
        self.assertEqual(result["candidates"][0]["specific_book_navigation"], [])

    def test_blank_overview_is_not_absence_and_flags_are_not_rights(self):
        f = self.fixture()
        f[3][1]["data"]["contentOverview"] = []
        result = summarize(*f)
        self.assertTrue(result["candidates"][0]["missing_structured_ranges"])
        self.assertTrue(result["candidates"][0]["list_image_flag"])
        self.assertFalse(result["policy"]["images_or_transcriptions_imported"])
