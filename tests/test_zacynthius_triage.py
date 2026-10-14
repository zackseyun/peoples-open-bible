import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "tools/textual_restoration/triage_zacynthius.py"
SPEC = importlib.util.spec_from_file_location("zacynthius", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TriageTests(unittest.TestCase):
    def parse(self, content):
        return MODULE.inventory(('<TEI xmlns="http://www.tei-c.org/ns/1.0"><text>' + content + '</text></TEI>').encode())

    def test_html_is_not_xml_evidence(self):
        with self.assertRaises(ValueError):
            MODULE.inventory(b"<html><body>System status</body></html>")

    def test_marginal_unclear_is_not_counted_as_body_word(self):
        result = self.parse('<pb n="12r"/><ab n="B03K1V46"><seg type="margin"><unclear reason="faded ink">x</unclear></seg></ab>')
        self.assertTrue(result["candidates"][0]["marginal"])
        self.assertEqual(result["candidates"][0]["verse_label"], "B03K1V46")
        self.assertEqual(result["accepted_new_characters"], 0)

    def test_alternative_readings_remain_separate(self):
        result = self.parse('<pb n="61r"/><ab n="B03K9V7"><app><rdg hand="firsthand" type="orig"><w>t<unclear reason="faded ink">aa</unclear>r</w></rdg><rdg hand="corrector"><w>t<supplied source="Tregelles" reason="illegible">a</supplied>r</w></rdg></app></ab>')
        self.assertEqual(len(result["candidates"]), 1)
        self.assertEqual(result["candidates"][0]["word_context"], "taar")
        self.assertEqual(result["candidates"][0]["hand"], "firsthand")
        self.assertEqual(sum(row["count"] for row in result["counts"]), 2)

    def test_above_line_number_is_still_paratext(self):
        result = self.parse('<seg type="line" n="@P16v"><fw type="SectionNumber"><w><unclear>x</unclear></w></fw></seg>')
        item = result["candidates"][0]
        self.assertFalse(item["marginal"])
        self.assertTrue(item["paratext"])
        self.assertEqual(item["placement_target"], "@P16v")

    def test_gap_units_are_not_letter_counts_and_page_resets_line(self):
        result = self.parse('<pb n="1r"/><lb n="old"/><gap reason="lacuna" extent="99" unit="char"/><pb n="1v"/><w><supplied source="transcriber">x</supplied></w>')
        self.assertEqual(result["counts"][0]["count"], 1)
        self.assertIsNone(result["candidates"][0]["line_label"])
        self.assertEqual(result["candidates"][0]["folio"], "1v")


if __name__ == "__main__":
    unittest.main()
