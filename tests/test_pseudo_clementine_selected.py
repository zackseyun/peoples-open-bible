import json
import unittest
from unittest.mock import patch

from tools.extra_texts import pseudo_clementine_selected as selected
from tools.extra_texts import pseudo_clementine_translation as translation


class SelectedGreekTests(unittest.TestCase):
    def test_layout_normalization_preserves_words_and_gaps(self):
        self.assertEqual(selected.normalized_lines(["ὁμό|εθνοι προ-", "φητῶν [.....] —"]), "ὁμόεθνοι προφητῶν [.....] —")

    def test_peter_is_complete_and_crop_correction_is_bound(self):
        result = selected.load_selected("pseudo_clementine_peter_to_james")
        self.assertEqual([r["reference"] for r in result["passages"]], ["1", "2", "3"])
        self.assertTrue(result["passages"][0]["source_text"].startswith("Πέτρος"))
        self.assertTrue(result["passages"][-1]["source_text"].endswith("ἔρρωσο."))
        self.assertIn("ἐνέγκωσιν", result["passages"][-1]["source_text"])
        self.assertNotIn("ἐνέγχωσιν", result["passages"][-1]["source_text"])
        self.assertEqual(len(result["page_evidence"][1]["adjudications"]), 2)
        self.assertIn("πρὶν ἂν τὰ πάντα γίνηται", result["passages"][1]["source_text"])

    def test_selected_edition_is_explicit_and_not_relicensed_xml(self):
        original = translation.prepare("pseudo_clementine_peter_to_james", ["1", "2", "3"], "test")
        new = translation.prepare("pseudo_clementine_peter_to_james", ["1", "2", "3"], "test", source_variant="lagarde1865")
        self.assertNotEqual(original["source_hash"], new["source_hash"])
        self.assertEqual(original["context"]["source_license"], "CC-BY-SA-4.0")
        self.assertIn("Public-domain", new["context"]["source_license"])
        old_draft = {"stage": "draft", "work": original["work"], "references": original["references"], "source_hash": original["source_hash"]}
        with self.assertRaisesRegex(ValueError, "source changed"):
            translation.prepare(original["work"], original["references"], "review", old_draft, source_variant="lagarde1865")

    def test_intro_work_inventory_and_undotted_section(self):
        for work, count in (("pseudo_clementine_contestation", 5), ("pseudo_clementine_clement_to_james", 20)):
            result = selected.load_selected(work)
            self.assertEqual([r["reference"] for r in result["passages"]], [str(n) for n in range(1, count+1)])
        self.assertIsNotNone(selected.SECTION_MARKER.match("11 διὸ"))
        self.assertIsNone(selected.SECTION_MARKER.search("λόγος 11 διὸ"))

    def test_homilies_preserve_page_continuation_and_numbering(self):
        lines = [(54, "Α"), (54, "1. λόγος προ-"), (55, "φητῶν [.....]. 2. ἀλήθεια."),
                 (56, "Β"), (56, "θεὸς. 2. εἰρήνη.")]
        rows = selected.extract_homilies(lines, expected_homilies=2)
        self.assertEqual([r["reference"] for r in rows], ["1.1", "1.2", "2.1", "2.2"])
        self.assertEqual(rows[0]["source_text"], "λόγος προφητῶν [.....].")
        self.assertEqual(rows[0]["printed_pages"], [12, 13])
        for malformed in (
            [(54, "Α"), (54, "λόγος. 3. κείμενον.")],
            [(54, "Α"), (54, "λόγος."), (55, "Γ"), (55, "κείμενον.")],
            [(54, "λόγος.")],
        ):
            with self.assertRaises(ValueError):
                selected.extract_homilies(malformed, expected_homilies=2)

    def test_clement_fifteen_uses_blindly_read_tau_not_a_conjectural_hyphen(self):
        source = selected.load_selected("pseudo_clementine_clement_to_james")
        row = next(r for r in source["passages"] if r["reference"] == "15")
        self.assertIn("τὰ χρῄζοντα", row["source_text"])
        self.assertNotIn("-ὰ χρῄζοντα", row["source_text"])
        evidence = next(p for p in source["page_evidence"] if p["pdf_page"] == 53)
        self.assertEqual(evidence["adjudications"][0]["scope"], "single_word")
        self.assertEqual(evidence["adjudications"][0]["after_word"], "τὰ")

    def test_first_homily_can_be_drafted_but_is_not_a_complete_work(self):
        result = selected.load_first_homily()
        self.assertEqual(result["coverage"]["status"], "complete_homily_partial_work")
        self.assertEqual(len(result["passages"]), 22)
        self.assertEqual(result["passages"][0]["reference"], "1.1")
        self.assertEqual(result["passages"][-1]["reference"], "1.22")
        packet = translation.prepare("pseudo_clementine_homilies", ["1.1", "1.2"], "test", source_variant="lagarde1865-homily-1")
        self.assertEqual(packet["context"]["source_coverage"]["status"], "complete_homily_partial_work")
        self.assertEqual(packet["context"]["source_coverage"]["required_homilies"], list(range(1,21)))
        response = {"model": "test", "choices": [{"finish_reason": "stop", "message": {"content": json.dumps({"passages": [
            {"reference": ref, "text": "Test draft, not approved.", "lexical_decisions": [], "source_issues": []}
            for ref in ["1.1", "1.2"]]})}}]}
        record = translation.validate_response(packet, response)
        self.assertEqual(record["source_hash"], packet["source_hash"])
        self.assertEqual(record["source_variant"], "lagarde1865-homily-1")

        with self.assertRaisesRegex(ValueError, "Missing"):
            translation.prepare("pseudo_clementine_homilies", ["2.1"], "test", source_variant="lagarde1865-homily-1")

    def test_partial_homily_two_keeps_original_reference_prefix(self):
        rows = selected.extract_homilies([(63, "Β"), (63, "λόγος. 2. κείμενον.")],
                                        expected_homilies=2, first_homily=2)
        self.assertEqual([r["reference"] for r in rows], ["2.1", "2.2"])
        with self.assertRaises(ValueError):
            selected.extract_homilies([(63, "Β"), (63, "λόγος.")], expected_homilies=2)

    def test_second_homily_variant_uses_same_source_at_preparation_and_ingestion(self):
        import copy
        fixture = copy.deepcopy(selected.load_first_homily())
        fixture["passages"] = [dict(fixture["passages"][0], reference="2.1", homily=2)]
        fixture["coverage"]["homilies"] = [2]
        fixture["coverage"]["sections"] = ["2.1"]
        with patch.object(selected, "load_second_homily", return_value=fixture):
            packet = translation.prepare("pseudo_clementine_homilies", ["2.1"], "test", source_variant="lagarde1865-homily-2")
            response = {"model":"test", "choices":[{"finish_reason":"stop", "message":{"content":json.dumps({"passages":[
                {"reference":"2.1", "text":"Test only.", "lexical_decisions":[], "source_issues":[]}]})}}]}
            result = translation.validate_response(packet, response)
            self.assertEqual(result["source_hash"], packet["source_hash"])
            self.assertEqual(packet["context"]["source_coverage"]["status"], "complete_homily_partial_work")

    def test_unknown_print_variant_is_not_silently_registered_xml(self):
        with self.assertRaisesRegex(ValueError, "Unknown"):
            translation.prepare("pseudo_clementine_homilies", ["1.1"], "test", source_variant="lagarde1865-unknown")

    def test_boundary_shift_fails_closed(self):
        first, proof1 = selected.load_page(45)
        second, proof2 = selected.load_page(46)
        second = [line for line in second if not line.startswith("Διαμαρτυρία")]
        with patch.object(selected, "load_page", side_effect=[(first, proof1), (second, proof2)]):
            with self.assertRaisesRegex(ValueError, "boundary"):
                selected.assemble_peter()


if __name__ == "__main__":
    unittest.main()
