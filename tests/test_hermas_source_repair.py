"""Source-import omissions must not silently return during normalization."""
import json
import unittest

from tools import shepherd_of_hermas as hermas


class HermasSourceRepairTests(unittest.TestCase):
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
        assert sum(r["source_status"] == "absent_after_cutoff" for r in rows) == 44
        assert not ledger["complete"]
