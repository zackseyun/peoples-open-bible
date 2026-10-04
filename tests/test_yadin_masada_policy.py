"""Guard Masada consultation scope and non-automatic source priority."""
import unittest
from unittest.mock import patch

from tools import hebrew_parallels, yadin_masada


class MasadaConsultPolicyTests(unittest.TestCase):
    def test_outer_span_keeps_chapter_44_but_not_51(self):
        for ref in [(39, 27), (43, 30), (44, 1), (44, 17)]:
            self.assertTrue(yadin_masada.in_coverage(*ref))
        for ref in [(4, 1), (39, 26), (44, 18), (49, 1), (51, 17)]:
            self.assertFalse(yadin_masada.in_coverage(*ref))

    def test_outside_span_rejected_before_index_lookup(self):
        with patch.object(yadin_masada, "is_available", return_value=True), \
             patch.object(yadin_masada, "_ensure_index") as index:
            for ref in [(4, 1), (49, 1), (51, 17)]:
                self.assertIsNone(yadin_masada.lookup(*ref))
            index.assert_not_called()

    def test_reference_registry_is_explicit_about_scope(self):
        entry = next(e for e in hebrew_parallels.consult_sources("SIR")
                     if e["name"].startswith("Yadin 1965"))
        self.assertEqual(entry["verse_range"],
                         "Surviving portions within Sir 39:27-44:17; not Sir 51")
        self.assertIn("not automatic priority", entry["guidance"])
        self.assertIn("Page-index associations do not prove", entry["guidance"])
        self.assertNotIn("usually wins", entry["guidance"])

    def test_live_note_does_not_certify_attestation_or_priority(self):
        note = {"hebrew_text": "fixture only", "scholarly_notes": "fixture",
                "page_in_yadin": 1, "also_on": [], "confidence": "fixture"}
        with patch.object(yadin_masada, "is_available", return_value=True), \
             patch.object(yadin_masada, "_ensure_index", return_value={(44, 17): note}):
            result = yadin_masada.lookup(44, 17)
        self.assertTrue(result["available"])
        self.assertIn("not automatic priority", result["guidance"])
        self.assertIn("not proof that a verse or reading survives", result["guidance"])
        self.assertNotIn("typically wins", result["guidance"])


if __name__ == "__main__":
    unittest.main()
