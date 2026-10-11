import copy
import json
from pathlib import Path
import subprocess
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

    def reproduce_frozen_queue(self):
        # Only the original review method is historical. The queue, generator,
        # screen controls and all WLC inputs must still match their live pins.
        frozen = json.loads(triage.OUTPUT.read_text())
        revision = "31a979f92629d06aab9002a9a4d0c92e47236fe3"
        method_path = "docs/TEXTUAL_ADJUDICATION_METHOD.md"
        method_raw = subprocess.check_output(
            ["git", "show", f"{revision}:{method_path}"], cwd=triage.ROOT)
        self.assertEqual(screen.digest(method_raw), frozen["inputs"][method_path],
                         "Historical review method drift")
        original = Path.read_bytes
        with patch.object(Path, "read_bytes",
                          new=lambda path: method_raw if path == triage.METHOD else original(path)):
            return triage.build()

    def test_corrupt_historical_method_cannot_reproduce_queue(self):
        original = subprocess.check_output

        def corrupt_method(args, **kwargs):
            raw = original(args, **kwargs)
            target = ("31a979f92629d06aab9002a9a4d0c92e47236fe3:"
                      "docs/TEXTUAL_ADJUDICATION_METHOD.md")
            return raw + b"corrupt" if args[-1] == target else raw

        with patch.object(subprocess, "check_output", side_effect=corrupt_method):
            with self.assertRaisesRegex(AssertionError, "Historical review method drift"):
                self.reproduce_frozen_queue()

    def test_changed_live_wlc_or_screen_cannot_hide_behind_historical_method(self):
        frozen = json.loads(triage.OUTPUT.read_text())
        wlc_path = next(name for name in sorted(frozen["inputs"])
                        if name.startswith("sources/ot/wlc/"))
        original = Path.read_bytes
        for target, message in ((triage.ROOT / wlc_path, "screen input drift"),
                                (screen.OUTPUT, "frozen screen pin mismatch")):
            def corrupt_live(path):
                raw = original(path)
                return raw + b"corrupt" if path == target else raw

            with self.subTest(path=str(target)), patch.object(Path, "read_bytes", new=corrupt_live):
                with self.assertRaisesRegex(ValueError, message):
                    self.reproduce_frozen_queue()

    def test_actual_complete_queue_reproduces(self):
        actual = self.reproduce_frozen_queue()
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
