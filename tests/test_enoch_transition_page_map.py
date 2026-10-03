"""Keep witnessed chapter-transition tails in the Enoch OCR page map."""

import json
import unittest
from pathlib import Path

from tools.enoch import build_page_map, verse_parser


ROOT = Path(__file__).resolve().parents[1]
OVERLAPS = {77: 186, 79: 190, 80: 191, 86: 204}


class EnochTransitionPageMapTest(unittest.TestCase):
    def test_committed_map_includes_witnessed_transition_pages(self):
        page_map = json.loads((ROOT / "sources/enoch/ethiopic/page_map.json").read_text())
        chapters = page_map["editions"]["charles_1906"]["chapters"]
        for chapter, page in OVERLAPS.items():
            with self.subTest(chapter=chapter):
                self.assertIn(page, chapters[f"{chapter:03d}"]["pages"])
                self.assertIn(page, chapters[f"{chapter + 1:03d}"]["pages"])

    def test_map_builder_does_not_erase_witnessed_overlaps(self):
        detected = build_page_map.load_detection("charles_1906")
        chapters, warnings = build_page_map.assemble_chapters(detected, edition="charles_1906")
        self.assertEqual(warnings, [])
        for chapter, page in OVERLAPS.items():
            with self.subTest(chapter=chapter):
                self.assertIn(page, chapters[chapter])

    def test_transcribed_verse_tails_cross_into_next_page_window(self):
        for chapter, final_verse in ((77, 8), (79, 6), (80, 8), (86, 6)):
            with self.subTest(chapter=chapter):
                row, warnings = verse_parser.load_verse(chapter, final_verse)
                self.assertIn(f"ch{chapter + 1:02d}.txt", row.chapter_file)
                self.assertTrue(any("Continued chapter" in warning for warning in warnings))


if __name__ == "__main__":
    unittest.main()
