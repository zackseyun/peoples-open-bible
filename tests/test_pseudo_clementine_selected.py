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

    def test_boundary_shift_fails_closed(self):
        first, proof1 = selected.load_page(45)
        second, proof2 = selected.load_page(46)
        second = [line for line in second if not line.startswith("Διαμαρτυρία")]
        with patch.object(selected, "load_page", side_effect=[(first, proof1), (second, proof2)]):
            with self.assertRaisesRegex(ValueError, "boundary"):
                selected.assemble_peter()


if __name__ == "__main__":
    unittest.main()
