"""Source-import omissions must not silently return during normalization."""
import json
import unittest

from tools import shepherd_of_hermas as hermas


class HermasSourceRepairTests(unittest.TestCase):
    def test_editorial_notes_are_not_source_body_without_apparatus(self):
        page = "[BODY]\nGreek body\n[EDITORIAL TRANSCRIPTION NOTES]\nEditorial warning\n---END-PAGE---"
        assert hermas.extract_body(page) == "Greek body"

    def test_opening_leaf_keeps_editorial_context_out_of_printed_heading(self):
        page = hermas.load_raw_page(313)
        assert page is not None
        assert page.running_head == ""
        assert page.page_hint == hermas.HermasUnitKey("V", 1, "i")
        assert page.body_lines[0].startswith("I. Ὁ θρέψας")


    def test_opening_joins_the_previously_orphaned_question_on_next_leaf(self):
        unit = hermas.load_unit("V.1.i")
        assert unit is not None
        assert unit.source_pages == [313, 314]
        assert unit.text.startswith("Ὁ θρέψας με πέπρακέν με Ῥόδῃ")
        assert "αἰσχρὸν ῥῆμα ἐλάλησα;" in unit.text
        assert "ἀνοδίας τινός" in unit.text  # printed line-end hyphen is joined
        assert "ΠΟΙΜΗΝ" not in unit.text
        assert "V.1.i" not in unit.text
        assert "II." not in unit.text  # next chapter remains separate
        assert unit.text.endswith("καὶ πάντων τῶν ἁγίων.")
        assert hermas.load_unit("V.1.ii").text.startswith("Μετὰ τὸ λαλῆσαι")


    def test_checked_in_sources_match_normalization(self):
        for unit in hermas.parse_units():
            _, text = hermas._parse_normalized_file(unit.output_path)
            assert text == unit.text, unit.unit_id
        checked_in = json.loads(hermas.UNIT_MAP_PATH.read_text())
        assert checked_in == hermas.unit_map_payload()


    def test_full_book_queue_includes_the_unimported_ending(self):
        path = hermas.REPO_ROOT / "sources/shepherd_of_hermas/repair/coverage.v1.json"
        ledger = json.loads(path.read_text())
        rows = ledger["units"]
        assert len(rows) == len({r["unit_id"] for r in rows}) == 114
        assert rows[-1]["unit_id"] == "S.10.iv"
        assert sum(r["baseline_source_status"] == "absent_after_cutoff" for r in rows) == 44
        assert not ledger["complete"]

    def test_cutoff_repair_preserves_boundaries_and_editorial_brackets(self):
        fourth = hermas.load_unit("S.8.iv")
        fifth = hermas.load_unit("S.8.v")
        sixth = hermas.load_unit("S.8.vi")
        assert "6. εἶτα" in fourth.text
        assert fourth.text.endswith("τοὺς δὲ χωρίς.")
        assert fifth.source_pages == [380, 381]
        assert "καὶ βεβρωμένας, τινὲς δὲ ἡμιξήρους" in fifth.text
        assert "[4. εἶτα" in fifth.text
        assert "ἴδιον τάγμα.] 5." in fifth.text
        assert fifth.text.endswith("εἰς τὸ ἴδιον τάγμα.")
        assert any("not an extant continuous Greek reading of A" in n for n in fifth.notes)
        assert sixth.text.startswith("Μετὰ τὸ πάντων")
        assert sixth.text.endswith("προδόται τῆς ἐκκλησίας")
        assert "EDITORIAL TRANSCRIPTION" not in sixth.text

    def test_cutoff_extension_does_not_renumber_imported_units(self):
        path = hermas.REPO_ROOT / "sources/shepherd_of_hermas/repair/coverage.v1.json"
        rows = json.loads(path.read_text())["units"]
        current = {u.unit_id: i for i, u in enumerate(hermas.parse_units(), 1)}
        for row in rows:
            if row["imported_sequence"] is not None:
                assert current[row["unit_id"]] == row["imported_sequence"]
