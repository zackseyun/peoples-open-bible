from pathlib import Path
import unittest
import yaml
import re

ROOT = Path(__file__).resolve().parents[1]
PRIORITY_BOOKS = {
    "nt": ("matthew", "mark", "luke", "john", "acts", "revelation"),
    "ot": ("genesis", "exodus", "leviticus", "numbers", "deuteronomy", "joshua", "judges", "ruth", "1_samuel", "2_samuel"),
}
VISIBLE_SUBSCRIPT_OR_SUPERSCRIPT = set("⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉")
PENINSULAR_FORMS = re.compile(
    r"\b(?:vosotros|vosotras|vuestro|vuestra|vuestros|vuestras|os|sois|habéis|tenéis|"
    r"veréis|digáis|haced|reuníos|mirad|tomad|oiréis|fuerais|guardaréis|pondréis|"
    r"despojaréis|presentaréis|ofreceréis|levantaréis|concederéis|acerquéis|cobrad|"
    r"lleguéis|pelead|haréis)\b",
    re.IGNORECASE,
)
PENINSULAR_VERB_ENDING = re.compile(r"\b\w+(?:áis|éis|ís)\b", re.IGNORECASE)
ENDING_EXCEPTIONS = {"país", "dieciséis", "veintiséis", "laís", "aquís", "achís"}

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
                    self.assertIsNone(re.search(r"\brespondió y dijo\b", text, re.IGNORECASE), str(path))
                    self.assertIsNone(
                        re.search(r"\baconteció(?:\[[A-Za-z0-9]+\])* que\b", text, re.IGNORECASE),
                        str(path),
                    )
                    self.assertIsNone(PENINSULAR_FORMS.search(text), str(path))
                    ending_hits = {
                        token.lower()
                        for token in PENINSULAR_VERB_ENDING.findall(text)
                        if token.lower() not in ENDING_EXCEPTIONS
                    }
                    self.assertFalse(ending_hits, f"{path}: {sorted(ending_hits)}")
                    checked += 1
        self.assertEqual(checked, 13910)

    def test_additional_graphic_books_have_no_parentheses(self):
        checked = 0
        for testament, book in (("ot", "isaiah"), ("nt", "hebrews"), ("nt", "romans")):
            for path in (ROOT / "translation_es" / testament / book).rglob("*.yaml"):
                record = yaml.safe_load(path.read_text())
                text = str(record["translation"]["text"])
                self.assertNotIn("(", text, str(path))
                self.assertNotIn(")", text, str(path))
                checked += 1
        self.assertEqual(checked, 2027)

    def test_spot_checked_accuracy_and_naturalness_repairs(self):
        acts = yaml.safe_load((ROOT / "translation_es/nt/acts/009/003.yaml").read_text())
        john = yaml.safe_load((ROOT / "translation_es/nt/john/001/041.yaml").read_text())
        self.assertEqual(
            acts["translation"]["text"],
            "Mientras iba de camino y se acercaba a Damasco, de repente una luz del cielo[a] brilló a su alrededor.",
        )
        self.assertIn("que significa Cristo", john["translation"]["text"])
        self.assertNotIn("significa Mesías", john["translation"]["text"])

        acts_20 = yaml.safe_load((ROOT / "translation_es/nt/acts/020/025.yaml").read_text())
        genesis_31 = yaml.safe_load((ROOT / "translation_es/ot/genesis/031/010.yaml").read_text())
        genesis_39 = yaml.safe_load((ROOT / "translation_es/ot/genesis/039/011.yaml").read_text())
        matthew_1 = yaml.safe_load((ROOT / "translation_es/nt/matthew/001/006.yaml").read_text())
        self.assertIsNone(
            re.search(r"ninguno de ustedes.*\bno volverá", acts_20["translation"]["text"]),
        )
        self.assertNotIn("en la casa, en la casa", genesis_39["translation"]["text"])
        self.assertIn("cuando el rebaño estaba en celo", genesis_31["translation"]["text"])
        self.assertNotIn("Griego literalmente", matthew_1["translation"]["text"])

if __name__ == "__main__":
    unittest.main()
