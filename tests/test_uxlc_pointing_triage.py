import copy
import json
import unittest
from unittest.mock import patch

from tools.textual_restoration import compare_uxlc_wlc as screen
from tools.textual_restoration import triage_uxlc_pointing as triage


def row(a, b, book="genesis", chapter=1, qere=False):
    def words(texts):
        return {"written": [{"text": t, "position": i} for i, t in enumerate(texts)],
                "qere": [{"text": "אב", "position": 10}] if qere else [],
                "annotations": []}
    left, right = words(a), words(b)
    return {"book": book, "chapter": chapter, "verse": 1,
            "wlc": left, "uxlc": right, **screen.comparison(left, right)}


class PointingTriageTests(unittest.TestCase):
    def test_dagesh_is_not_semantically_dismissed(self):
        r = triage.classify(row(["בַ"], ["בַּ"]))
        self.assertEqual(r["category"], "dagesh_rafe_only")
        self.assertEqual(r["semantic_review"], "not_adjudicated")

    def test_shin_sin_not_declared_same_lexeme(self):
        r = triage.classify(row(["שֶׂ"], ["שֶׁ"]))
        self.assertEqual(r["category"], "shin_sin_dots_only")
        self.assertEqual(r["semantic_review"], "not_adjudicated")

    def test_other_vowel_change(self):
        r = triage.classify(row(["טָבַח"], ["טֶבַח"]))
        self.assertEqual(r["category"], "other_pointing")
        self.assertEqual(r["changed_written_words"][0]["written_word_number"], 1)

    def test_qere_hold_precedes_point_class(self):
        r = triage.classify(row(["בַ"], ["בַּ"], qere=True))
        self.assertEqual(r["category"], "qere_involved_hold")
        self.assertEqual(len(r["changed_written_words"]), 1)

    def test_alignment_hold_precedes_qere(self):
        r = triage.classify(row(["בַב"], ["בֶ", "ב"], qere=True))
        self.assertEqual(r["category"], "token_alignment_hold")
        self.assertFalse(r["token_alignment_verified"])
        self.assertEqual(r["changed_written_words"], [])

    def test_decalogue_chapter_flag_never_discards_a_change(self):
        r = triage.classify(row(["בַ"], ["בַּ"], book="exodus", chapter=20))
        self.assertTrue(r["decalogue_chapter_context"])
        self.assertEqual(r["category"], "dagesh_rafe_only")

    def test_false_pointing_and_nonpointing_rows_fail(self):
        r = row(["אב"], ["אב"])
        with self.assertRaises(ValueError):
            triage.classify(r)
        r["written_difference"] = "pointing"
        with self.assertRaises(ValueError):
            triage.classify(r)

    def test_removed_marks_are_renormalized(self):
        self.assertEqual(triage.without("בָ\u05bcִ", "\u05bc"), triage.without("בִָ", ""))

    def test_actual_complete_queue_reproduces(self):
        actual = triage.build()
        self.assertEqual(actual, json.loads(triage.OUTPUT.read_text()))
        self.assertEqual(actual["summary"]["verse_rows"], 374)
        self.assertEqual(actual["summary"]["categories"], {
            "token_alignment_hold": 3, "qere_involved_hold": 37,
            "dagesh_rafe_only": 225, "shin_sin_dots_only": 2, "other_pointing": 107})
        self.assertEqual(sum(actual["summary"]["categories"].values()), 374)
        self.assertEqual(len({(r["book"], r["chapter"], r["verse"]) for r in actual["rows"]}), 374)
        proverbs = next(r for r in actual["rows"] if (r["book"], r["chapter"], r["verse"]) == ("proverbs", 7, 22))
        self.assertEqual([(p["wlc_pointing"], p["uxlc_pointing"]) for p in proverbs["changed_written_words"]], [("טָבַח", "טֶבַח")])

    def test_archive_reproduction_checks_raw_rows_not_changed_canonical_joins(self):
        frozen = {k: [] for k in ("protocol", "archive_members", "summary", "books", "unmatched_labels", "differences")}
        rebuilt = copy.deepcopy(frozen)
        rebuilt["pob_joins"] = ["current canonical record is allowed to differ"]
        with patch.object(screen, "build", return_value=rebuilt):
            triage.verify_archive(None, frozen)
        rebuilt["differences"] = ["bad raw text"]
        with patch.object(screen, "build", return_value=rebuilt):
            with self.assertRaisesRegex(ValueError, "raw archive reproduction drift"):
                triage.verify_archive(None, frozen)


if __name__ == "__main__":
    unittest.main()
