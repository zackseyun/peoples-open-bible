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
        assert next(r for r in rows if r["unit_id"] == "S.9.xviii")["source_status"] == "printed_body_restored_pending_collation"

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
        assert eighteenth.text.endswith("τῶν δώδεκα ἐθνῶν.")

    def test_complete_printed_ending_is_latin_not_an_invented_greek_retroversion(self):
        mixed = hermas.load_normalized_unit("S.9.xxx")
        latin = hermas.load_normalized_unit("S.10.iv")
        assert mixed.source_language == "Greek and Latin"
        assert "3. quodsi de ceteris montibus" in mixed.text
        assert "†posse eos veritati favere,†" in mixed.text
        assert latin.source_language == "Latin"
        assert latin.source_pages == [417, 418]
        assert latin.text.endswith("remissurum se pastorem illum et virgines in domum meam.")
        assert "festinetis" in latin.text
        assert "conmunda domum tuam" in hermas.load_unit("S.10.iii").text
        assert "SIMILITUDO DECIMA" not in hermas.load_unit("S.9.xxxiii").text
        assert "SIMILITUDO DECIMA" not in hermas.load_unit("S.10.i").text
        assert "νοεῖ⸢τε⸣" in hermas.load_unit("S.9.xxviii").text
        rows = json.loads((hermas.REPO_ROOT / "sources/shepherd_of_hermas/repair/coverage.v1.json").read_text())["units"]
        assert not any(r["source_status"] == "absent_after_cutoff" for r in rows)

    def test_drafting_prompt_uses_actual_latin_source_and_warns_about_version_evidence(self):
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, str(hermas.REPO_ROOT / "tools/build_shepherd_of_hermas_prompt.py"),
             "--unit-id", "S.10.iv", "--json"],
            cwd=hermas.REPO_ROOT, capture_output=True, text=True, check=True,
        )
        payload = json.loads(result.stdout)
        assert payload["source"]["language"] == "Latin"
        assert payload["source"]["text"].startswith("Ait deinde mihi: Viriliter")
        assert "not surviving original Greek" in payload["prompt"]
        assert any("final printed Latin" in note for note in payload["source_warnings"])

    def test_restored_boundaries_have_explicit_legacy_reader_crosswalk(self):
        import yaml
        path = hermas.REPO_ROOT / "sources/shepherd_of_hermas/repair/coverage.v1.json"
        rows = json.loads(path.read_text())["units"]
        current = {u.unit_id: i for i, u in enumerate(hermas.parse_units(), 1)}
        cross = json.loads((path.parent / "reader-source-crosswalk-20261103.v4.json").read_text())
        assert not cross["reader_ids_renumbered"]
        assert not cross["reader_english_changed"]
        by_legacy = {r["legacy_reader_chapter"]: r for r in cross["legacy_readers"]}
        assert len(by_legacy) == 63
        for legacy in by_legacy.values():
            assert legacy["current_index_of_legacy_label"] == current[legacy["legacy_source_label"]]
        for row in rows:
            assert row["current_source_sequence"] == current.get(row["unit_id"])
            if row["imported_sequence"] is not None:
                legacy = by_legacy[row["imported_sequence"]]
                assert legacy["legacy_source_label"] == row["unit_id"]
                doc = yaml.safe_load((hermas.REPO_ROOT / legacy["legacy_record_path"]).read_text())
                assert doc["id"] == legacy["legacy_record_id"] == "HERM." + row["unit_id"]
        assert current["S.8.iv"] == 70
        assert by_legacy[63]["legacy_source_label"] == "S.8.iv"
        assert cross["new_source_units"][0]["new_reader_slot"] is None

    def test_earlier_scan_repairs_recover_text_without_swallowing_next_chapters(self):
        ninth = hermas.load_unit("V.3.ix")
        tenth = hermas.load_unit("V.3.x")
        assert ninth.source_pages == [326, 327]
        assert "ἀπὸ πάσης πονηρίας" in ninth.text
        assert ninth.text.endswith("τῷ Κυρίῳ ὑμῶν.")
        assert tenth.text.startswith("Ὅτε οὖν ἐπαύσατο")
        assert "AP. FATH." not in hermas.load_unit("V.3.iii").text
        third = hermas.load_unit("M.12.iii")
        fourth = hermas.load_unit("M.12.iv")
        sixth = hermas.load_unit("M.12.vi")
        assert "εὐφρᾶναι καρδίαν ἀνθρώπου" in third.text
        assert third.text.endswith("ὑπὸ ἀνθρώπου φυλαχθῆναι.")
        assert fourth.text.startswith("Καὶ ταῦτά μοι λίαν ὀργίλως")
        assert "[πάντων καὶ] πασῶν" in fourth.text
        assert sixth.source_pages == [356, 357]
        assert "ἰσχυροποιῆσαι αὐτοὺς" in sixth.text
        assert sixth.text.endswith("καὶ ζήσονται τῷ Θεῷ.")
        first = hermas.load_unit("S.1")
        second = hermas.load_unit("S.2")
        third_sim = hermas.load_unit("S.3")
        fourth_sim = hermas.load_unit("S.4")
        assert first.text.startswith("Λέγει μοι· Οἴδατε")
        assert first.text.endswith("τὸ δὲ σὸν ἔργον ἐργάζου, καὶ σωθήσῃ.")
        assert second.text.startswith("Περιπατοῦντός μου")
        assert "πληροφοροῦσι τὰς εὐχὰς αὐτῶν" in second.text
        assert second.text.endswith("δυνήσονται ἀγαθόν τι ἐργάζεσθαι.")
        assert third_sim.source_pages == [361]
        assert third_sim.text.endswith("ἀλλὰ πάντες ὅμοιοί εἰσιν.")
        assert fourth_sim.text.startswith("1. Ἔδειξέ μοι πάλιν")

    def test_mandate_scan_repairs_separate_missing_chapters_and_preserve_variants(self):
        third = hermas.load_unit("M.4.iii")
        fourth = hermas.load_unit("M.4.iv")
        assert third.source_pages == [338]
        assert "μίαν μετάνοιαν ἔχει" in third.text
        assert third.text.endswith("καὶ πάντες ὅσοι ἐὰν ταῦτα ποιήσωσιν.")
        assert fourth.source_pages == [338, 339]
        assert fourth.text.startswith("Ἠρώτησα αὐτὸν πάλιν λέγων· Κύριε, ἐπεὶ ἅπαξ ἀνέχῃ μου")
        assert any("negation" in n and "οὐ" in n for n in third.notes)
        fifth_first = hermas.load_unit("M.5.i")
        fifth_second = hermas.load_unit("M.5.ii")
        assert fifth_first.text.endswith("ἐδικαιώθησαν γὰρ πάντες ὑπὸ τοῦ σεμνοτάτου ἀγγέλου.")
        assert fifth_second.source_pages == [340, 341]
        assert "δοξάζουσα τὸν Κύριον ἐν παντὶ καιρῷ" in fifth_second.text
        sixth_first = hermas.load_unit("M.6.i")
        sixth_second = hermas.load_unit("M.6.ii")
        assert sixth_first.text.endswith("πορεύσεται ἐν αὐτῇ.")
        assert sixth_second.source_pages == [342, 343]
        assert "[ταῦτα οὖν ἐστὶ τὰ ἔργα τοῦ ἀγγέλου τῆς δικαιοσύνης.]" in sixth_second.text
        assert "APPARATUS" not in sixth_second.text
        assert "Ἐντολὴ" not in sixth_second.text

    def test_similitude_five_restoration_preserves_complete_boundaries_and_supplies(self):
        units = {u.unit_id: u for u in hermas.parse_units()}
        ledger = json.loads((hermas.REPO_ROOT / "sources/shepherd_of_hermas/repair/coverage.v1.json").read_text())
        assert set(units) == {r["unit_id"] for r in ledger["units"]}
        assert len(units) == 114
        assert not ledger["complete"]  # representation alone is not completion
        assert units["S.4"].text.endswith("καρποφορήσει.")
        first = units["S.5.i"]
        assert first.source_pages == [362, 363]
        assert "λέγοντα Τί ὀρθρινὸς ὧδε ἐλήλυθας;" in first.text
        assert first.text.endswith("μεγάλην νηστείαν τελέσεις καὶ δεκτὴν τῷ Θεῷ.")
        second = units["S.5.ii"]
        assert second.source_pages == [363, 364, 365]
        assert second.text.startswith("Ἄκουε τὴν παραβολὴν")
        assert "τὰ λοιπὰ δὲ τοῖς συνδούλοις αὐτοῦ διέδωκεν" in second.text
        third = units["S.5.iii"]
        assert third.text.count("|") == 2
        assert "ταπεινοφροσύνης σου" in third.text
        assert third.text.endswith("ὅσα ἂν αἰτήσωνται παρὰ τοῦ Κυρίου λήψονται.")
        fourth = units["S.5.iv"]
        assert fourth.source_pages == [366, 367]
        assert fourth.text.startswith("Ἐδεήθην αὐτοῦ πολλὰ")
        assert fourth.text.endswith("ἵνα μοι δηλωθῇ.")
        fifth = units["S.5.v"]
        assert fifth.source_pages == [367]
        assert fifth.text.endswith("εἰς δούλου τρόπον κεῖται ἐν τῇ παραβολῇ;")
        sixth = units["S.5.vi"]
        assert sixth.source_pages == [367, 368]
        assert "κατέστησε τοὺς ἀγγέλους ἐπ᾽ αὐτοὺς" in sixth.text
        assert "VII." not in sixth.text
        assert any("negation" in n and "absent in A" in n for n in sixth.notes)
        assert units["S.5.vii"].text.startswith("Ηὐφράνθην")

    def test_earlier_leaves_recover_missing_body_even_when_end_marker_existed(self):
        second_vision = hermas.load_unit("V.4.ii")
        assert "τὸ ὄνομά ἐστιν Σεγρί" in second_vision.text
        assert "καὶ τῇ πολυσπλαγχνίᾳ αὐτοῦ ἐξέφυγον αὐτό" in second_vision.text
        mandate = hermas.load_unit("M.4.i")
        assert "ἀλλὰ δεῖ παραδεχθῆναι" in mandate.text
        assert "μετανοήσῃ [ἡ γυνὴ]" in mandate.text
        eleventh = hermas.load_unit("M.11")
        assert "τὸ πνεῦμα τὸ ἐπίγειον ὑπὸ τοῦ φόβου φεύγει" in eleventh.text
        assert "καὶ σιφώνισον εἰς τὸν οὐρανόν" in eleventh.text
        assert any("holy" in n and "ἅγιον" in n for n in eleventh.notes)
        sixth_second = hermas.load_unit("S.6.ii")
        assert "ἄγγελος τρυφῆς καὶ ἀπάτης" in sixth_second.text
        assert "τῶν τοιούτων ἡ ζωὴ θάνατός ἐστιν" in sixth_second.text
        sixth_fourth = hermas.load_unit("S.6.iv")
        assert "| Ἐλάχιστον, φημί, κύριε, βασανίζονται· |" in sixth_fourth.text
        seventh = hermas.load_unit("S.7")
        eighth_first = hermas.load_unit("S.8.i")
        assert seventh.source_pages == [374, 375]
        assert "δυνήσεταί σου ἡ μετάνοια ἰσχυρὰ καὶ καθαρὰ εἶναι" in seventh.text
        assert eighth_first.text.startswith("Ἔδειξέ μοι ἰτέαν [μεγάλην]")
        assert "15. ἑτέρων δὲ ἦν ἐλάχιστον χλωρόν" in eighth_first.text
        assert eighth_first.text.count("|") == 4  # two existing bars plus the restored377 pair
        eighth_second = hermas.load_unit("S.8.ii")
        assert "δοὺς αὐτοῖς σφραγῖδα." in eighth_second.text
        assert "ἱματισμὸν [λευκὸν] καὶ σφραγῖδας" in eighth_second.text
        assert "6. καὶ μετὰ τὸ ἀπελθεῖν τὸν ἄγγελον" in eighth_second.text
        record = json.loads((hermas.REPO_ROOT / "sources/shepherd_of_hermas/repair/earlier-leaves-20261103.v1.json").read_text())
        page351 = next(c for c in record["raw_changes"] if c["physical_page"] == 351)
        assert not page351["body_changed"]
        assert not record["complete"]

    def test_primary_scan_restoration_replaces_only_the_five_web_patch_bodies(self):
        overrides = {u.unit_id for u in hermas.load_manual_unit_overrides()}
        assert overrides == {"S.8.x", "S.9.iii"}
        eighth = hermas.load_unit("M.8")
        assert eighth.source_pages == [344, 345, 346]
        assert eighth.text.count("|") == 2
        assert "ἀφ᾽ ὧν [ἡμᾶς]" in eighth.text
        assert "[καὶ] μνησικακίας" in eighth.text
        assert "[φησί,] τοῖς δούλοις τοῦ Θεοῦ;" in eighth.text
        assert "χήραις ὑπηρετεῖν" in eighth.text
        assert eighth.text.endswith("πορευθῶσιν ἐν αὐταῖς.")
        ninth = hermas.load_unit("M.9")
        assert ninth.source_pages == [346, 347]
        assert "τὴν πολυευσπλαγχνίαν αὐτοῦ" in ninth.text
        assert ninth.text.endswith("οἱ ταῦτα φρονοῦντες.")
        first = hermas.load_unit("M.10.i")
        second = hermas.load_unit("M.10.ii")
        third = hermas.load_unit("M.10.iii")
        assert first.source_pages == [347, 348]
        assert first.text.startswith("Ἆρον ἀπὸ σεαυτοῦ")
        assert first.text.endswith("καὶ πάντα συνήσεις καὶ νοήσεις.")
        assert second.source_pages == [348, 349]
        assert second.text.startswith("Ἄκουε νῦν, φησίν, ἀνόητε")
        assert "μήποτε ἐντεύξηται [κατὰ σοῦ] τῷ Θεῷ" in second.text
        assert third.source_pages == [349, 350]
        assert third.text.startswith("Ἔνδυσαι οὖν τὴν ἱλαρότητα")
        assert "Ἐντολὴ" not in third.text
        for unit in [eighth, ninth, first, second, third]:
            assert "manual unit override" not in unit.source_edition
            assert not any("greekdoc" in n for n in unit.notes)
        record = json.loads((hermas.REPO_ROOT / "sources/shepherd_of_hermas/repair/override-provenance-20261103.v1.json").read_text())
        assert len(record["retired_overrides"]) == 5
        assert not record["complete"]

    def test_source_reordering_cannot_overwrite_a_different_legacy_reader_id(self):
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        from tools import draft_shepherd_of_hermas as drafter
        unit = hermas.load_normalized_unit("S.3")
        with TemporaryDirectory() as tmp, patch.object(drafter, "TRANSLATION_ROOT", Path(tmp)):
            path = Path(tmp) / f"{unit.sequence:03d}.yaml"
            before = "id: HERM.S.4\ntranslation:\n  text: Historical reader text\n"
            path.write_text(before)
            with self.assertRaisesRegex(ValueError, "another legacy reader unit"):
                drafter.output_path_for_unit(unit)
            assert path.read_text() == before

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
