from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]
PRIORITY_BOOKS = {
    "nt": ("matthew", "mark", "luke", "john", "acts", "revelation"),
    "ot": ("genesis", "exodus", "leviticus", "numbers", "deuteronomy", "joshua", "judges", "ruth", "1_samuel", "2_samuel"),
}
VISIBLE_SUBSCRIPT_OR_SUPERSCRIPT = set("⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉")

class SpanishPriorityReaderTextTest(unittest.TestCase):
    def test_priority_books_have_no_parentheses_or_unicode_note_scripts(self):
        checked = 0
        for testament, books in PRIORITY_BOOKS.items():
            for book in books:
                for path in (ROOT / "translation_es" / testament / book).rglob("*.yaml"):
                    lines = path.read_text().splitlines()
                    in_translation = False
                    text = None
                    for line in lines:
                        if line == "translation:":
                            in_translation = True
                            continue
                        if in_translation and line and not line.startswith(" "):
                            break
                        if in_translation and line.startswith("  text:"):
                            text = line.split(":", 1)[1].strip()
                            break
                    self.assertIsNotNone(text, str(path))
                    self.assertNotIn("(", text, str(path))
                    self.assertNotIn(")", text, str(path))
                    self.assertFalse(VISIBLE_SUBSCRIPT_OR_SUPERSCRIPT.intersection(text), str(path))
                    checked += 1
        self.assertEqual(checked, 13910)

    def test_spot_checked_accuracy_and_naturalness_repairs(self):
        acts = yaml.safe_load((ROOT / "translation_es/nt/acts/009/003.yaml").read_text())
        john = yaml.safe_load((ROOT / "translation_es/nt/john/001/041.yaml").read_text())
        self.assertEqual(
            acts["translation"]["text"],
            "Mientras iba de camino y se acercaba a Damasco, de repente una luz del cielo[a] brilló a su alrededor.",
        )
        self.assertIn("que significa Cristo", john["translation"]["text"])
        self.assertNotIn("significa Mesías", john["translation"]["text"])

if __name__ == "__main__":
    unittest.main()
