"""Guard the verse-boundary inventory of the first 17 Enoch chapters.

Counts follow the public-domain Charles 1917 English reference, used for
versification only, not for the POB translation text.
"""

import unittest
import subprocess
import sys
from pathlib import Path

from tools.enoch import build_translation_prompt, verse_parser


EXPECTED = {
    1: 9, 2: 3, 3: 1, 4: 1, 5: 9, 6: 8, 7: 6, 8: 4, 9: 11,
    10: 22, 11: 2, 12: 6, 13: 10, 14: 25, 15: 12, 16: 4, 17: 8,
}


class EnochVerseInventoryTest(unittest.TestCase):
    def test_unsafe_oracle_patcher_is_retired(self):
        script = Path(__file__).resolve().parents[1] / "tools/enoch/gap_audit.py"
        result = subprocess.run([sys.executable, str(script), "--dry-run"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("oracle-derived patcher is retired", result.stderr)

    def test_every_primary_ocr_verse_is_present_in_order(self):
        for chapter, count in EXPECTED.items():
            with self.subTest(chapter=chapter):
                rows, _warnings = verse_parser.parse_chapter(chapter)
                self.assertEqual([row.verse for row in rows], list(range(1, count + 1)))
                self.assertTrue(all(row.text for row in rows))

    def test_cross_file_continuation_is_not_lost(self):
        for chapter, verse in ((5, 9), (6, 6), (7, 1), (9, 9), (10, 16),
                               (12, 1), (13, 4), (14, 19), (15, 9),
                               (16, 1), (17, 7)):
            with self.subTest(reference=f"{chapter}:{verse}"):
                row, _warnings = verse_parser.load_verse(chapter, verse)
                self.assertIn(f"ch{chapter + 1:02d}.txt", row.chapter_file)

    def test_chapter_six_final_sentence_has_its_own_verse(self):
        verse_7, _ = verse_parser.load_verse(6, 7)
        verse_8, warnings = verse_parser.load_verse(6, 8)
        self.assertNotIn("እሉ፡ እሙንቱ፡", verse_7.text)
        self.assertTrue(verse_8.text.startswith("እሉ፡ እሙንቱ፡"))
        self.assertIn("editorial boundary", verse_8.marker_raw)
        self.assertTrue(any("verse 8 boundary" in warning for warning in warnings))

    def test_prompt_records_both_scanned_page_windows_for_split_verse(self):
        bundle = build_translation_prompt.build_enoch_prompt(6, 6)
        self.assertEqual(bundle.source_payload["pages"], [50, 52])
        self.assertIn("ch06.txt +", bundle.source_payload["note"])
        self.assertIn("ch07.txt", bundle.source_payload["note"])


if __name__ == "__main__":
    unittest.main()
