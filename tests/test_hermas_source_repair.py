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
        assert sixth.text.endswith("τὸ δὲ μὴ μετανοῆσαι θάνατον.")
        assert "πολυευσπλαγχνίαν" in sixth.text
        assert "ἔδωκε πνεῦμα" in sixth.text
        assert "τῶν ἁμαρτιῶν ζωὴν ἔχει" in sixth.text
        assert "EDITORIAL TRANSCRIPTION" not in sixth.text

    def test_completed_similitude_eight_does_not_swallow_nine(self):
        eighth = hermas.load_unit("S.8.viii")
        tenth = hermas.load_unit("S.8.x")
        last = hermas.load_unit("S.8.xi")
        first_nine = hermas.load_unit("S.9.i")
        assert "οὗτοι τὸ ζῆν εἰς τέλος ἀπώλεσαν." in eighth.text
        assert "ξηρὰς ἐπιδεδωκότες" in tenth.text
        assert "[καὶ λαλήσας]" in last.text
        assert last.text.endswith("μετ᾿ ὀλίγας ἡμέρας.")
        assert "Παραβολὴ" not in last.text
        assert first_nine.source_pages == [386, 387]
        assert first_nine.text.startswith("Μετὰ τὸ γράψαι")
        assert first_nine.text.endswith("εὐπρεπέστατον ἦν ἑαυτῷ τὸ ὄρος.")

    def test_new_chapters_preserve_editorial_negation_and_partial_boundary(self):
        second = hermas.load_unit("S.9.ii")
        third = hermas.load_unit("S.9.iii")
        fourth = hermas.load_unit("S.9.iv")
        assert "πύλην ἐκκεκομμένην" in second.text
        assert "διηπόρουν" in second.text
        assert "λαμπροί, [μὴ] λελατομημένοι." in third.text
        assert any("absent" in n and "μὴ" in n for n in third.notes)
        assert third.text.endswith("κατὰ ἕνα λίθον ἐβάσταζον ὁμοῦ.")
        assert fourth.source_pages == [388, 389, 390]
        assert fourth.text.startswith("Καθὼς δὲ ἐστάθησαν ὁμοῦ κύκλῳ τῆς πύλης, οὕτως")
        assert fourth.text.endswith("μὴ κοπιᾶτε οὖν, [φασίν,] εἰς μάτην.")

    def test_supplements_and_uncertain_text_survive_cross_page_normalization(self):
        fourth = hermas.load_unit("S.9.iv")
        sixth = hermas.load_unit("S.9.vi")
        eighth = hermas.load_unit("S.9.viii")
        assert "| καὶ ἀνέπλησαν ὅλην τὴν πέτραν." in fourth.text
        assert sixth.text.count("|") == 6
        assert "6. | καὶ ἐπηρώτησαν αὐτὸν οἱ οἰκοδομοῦντες" in sixth.text
        assert eighth.text.count("†") == 2
        assert "[εὑρέθησαν καὶ]" in eighth.text
        assert "[τῶν παρθένων]" in eighth.text
        assert any("Vertical bars" in note for note in sixth.notes)

    def test_nine_continuation_keeps_complete_chapters_and_partial_tail_distinct(self):
        fifth = hermas.load_unit("S.9.v")
        tenth = hermas.load_unit("S.9.x")
        eleventh = hermas.load_unit("S.9.xi")
        assert "καὶ μὴ λελατομημένων" in fifth.text
        assert "ταῖς δὲ παρθένοις ἐπέταξαν" in fifth.text
        assert "παρεγεγόνει" in fifth.text
        assert tenth.text.endswith("αἱ ἐνδοξότεραι αὐτῶν.")
        assert eleventh.text.endswith("καὶ οὐδὲν ὅλως ἀποκρύψω ἀπὸ σοῦ.")
        assert eleventh.source_pages == [396, 397]
        twelfth = hermas.load_unit("S.9.xii")
        thirteenth = hermas.load_unit("S.9.xiii")
        partial = hermas.load_unit("S.9.xiv")
        assert "Ἡ πέτρα, φησίν, αὕτη καὶ ἡ πύλη ὁ υἱὸς τοῦ Θεοῦ ἐστί." in twelfth.text
        assert "διῆλθον γὰρ διὰ τῆς πύλης" in thirteenth.text
        assert "ἐνδιδυσκόμενοι τὰ πνεύματα" in thirteenth.text
        assert partial.text.endswith("τὸ ὄνομα αὐτοῦ φορεῖν.")
        rows = json.loads((hermas.REPO_ROOT / "sources/shepherd_of_hermas/repair/coverage.v1.json").read_text())["units"]
        assert next(r for r in rows if r["unit_id"] == "S.9.xviii")["source_status"] == "partially_transcribed"

    def test_damaged_letters_and_quotation_evidence_are_not_silently_certified(self):
        fifteenth = hermas.load_unit("S.9.xv")
        sixteenth = hermas.load_unit("S.9.xvi")
        seventeenth = hermas.load_unit("S.9.xvii")
        eighteenth = hermas.load_unit("S.9.xviii")
        assert fifteenth.text.startswith("⸢Δήλωσόν μοι⸣")
        assert "ἐσχήκει⸢σαν⸣, ⸢οὐκ ἂν⸣" in fifteenth.text
        assert "| ἀλλ᾿ οὗτοι ζῶντες κατέβησαν, [καὶ πάλιν ζῶντες ἀνέβησαν]" in sixteenth.text
        assert any("Clement" in n and "indirect Greek" in n for n in sixteenth.notes)
        assert "ἀλατόμητοι συνῳκοδομήθησαν" in sixteenth.text
        assert seventeenth.source_pages == [403, 404]
        assert "ἐγνωκ⸢ό⸣τες" in eighteenth.text
        assert "⸢ἠρ⸣μένους" in eighteenth.text
        assert eighteenth.text.endswith("βλασφήμους καὶ")

    def test_cutoff_extension_does_not_renumber_imported_units(self):
        path = hermas.REPO_ROOT / "sources/shepherd_of_hermas/repair/coverage.v1.json"
        rows = json.loads(path.read_text())["units"]
        current = {u.unit_id: i for i, u in enumerate(hermas.parse_units(), 1)}
        for row in rows:
            if row["imported_sequence"] is not None:
                assert current[row["unit_id"]] == row["imported_sequence"]

    def test_bounded_selections_keep_working_print_and_manuscript_evidence_separate(self):
        tenth = hermas.load_unit("S.8.x")
        third = hermas.load_unit("S.9.iii")
        raw_tenth = hermas.load_raw_page(385)
        raw_third = hermas.load_raw_page(388)
        assert "παθοῦνται" in tenth.text
        assert "ἑκόντες θλίβονται" not in tenth.text
        assert any("ἑκόντες θλίβονται" in line for line in raw_tenth.body_lines)
        assert "ἐπάνω τῆς πέτρας πύργον τινά" in third.text
        assert any("πύλης πύργον τινά" in line for line in raw_third.body_lines)
        path = hermas.REPO_ROOT / "sources/shepherd_of_hermas/repair/manuscript-selection-20261103.v1.json"
        selection = json.loads(path.read_text())
        assert {d["unit_id"] for d in selection["decisions"]} == {"S.8.x", "S.9.iii"}
        negation = next(c for c in selection["open_cases"] if c["passage"] == "S.9.iii.3")
        assert "lost leaf" in negation["observation"]
