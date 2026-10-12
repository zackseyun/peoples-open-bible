"""Checks the opt-in edition projection, not historical Hebrew priority."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.textual_restoration import export_wlc_layers as m

RECEIPT = m.ROOT / "sources/textual_restoration/comparisons/wlc_ordered_layers.2026-10-12.v1.json"


class OrderedLayersTests(unittest.TestCase):
    def synthetic(self, body, extra=""):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "ot/wlc"
            folder.mkdir(parents=True)
            (folder / "Gen.xml").write_text(
                '<osis xmlns="urn:test"><verse osisID="Gen.1.1">'
                + body + '</verse>' + extra + '</osis>', encoding="utf-8")
            return m.build_book("GEN", root)["verses"][0]

    def test_actual_internal_samekh_is_not_moved(self):
        verse = next(v for v in m.build_book("1CH")["verses"]
                     if v["reference_id"] == "1CH.12.14")
        units = verse["ordered_units"]
        index = next(i for i, u in enumerate(units)
                     if u["attributes"].get("type") == "x-samekh")
        self.assertIn("עֲשִׂירִ", units[index - 1]["text"])
        self.assertIn("מַכְבַּנַּ", units[index + 1]["text"])
        self.assertNotIn("ס", verse["written_text"])
        self.assertEqual(verse["ordered_xml_text"].count("ס"), 1)

    def test_paragraphs_are_segments_not_removed_letters(self):
        verse = self.synthetic('<w id="a" lemma="l" morph="HC/R">פס/א</w>'
                               '<seg type="x-pe">פ</seg><w id="b">סב</w>'
                               '<seg type="x-samekh">ס</seg>')
        self.assertEqual(verse["ordered_xml_text"], "פס/אפסבס")
        self.assertEqual(verse["written_text"], "פס/אסב")
        self.assertEqual(verse["ordered_units"][0]["attributes"],
                         {"id": "a", "lemma": "l", "morph": "HC/R"})

    def test_punctuation_order_and_inline_offsets_no_normalization(self):
        text = 'בָ\u034fִ/א'
        verse = self.synthetic(f'<w id="a">{text}<seg type="x-large">ג</seg>ד</w>'
                               '<seg type="x-maqqef">־</seg><w id="b">ה</w>'
                               '<seg type="x-paseq">׀</seg><seg type="x-sof-pasuq">׃</seg>')
        self.assertEqual(verse["written_text"], text + "גד־ה׀׃")
        self.assertEqual(verse["ordered_units"][0]["inline_annotations"],
                         [{"type": "x-large", "text": "ג", "offset": len(text),
                           "attributes": {"type": "x-large"}}])
        self.assertEqual(verse["annotations"][0]["attributes"], {"type": "x-large"})

    def test_empty_multiword_and_insertion_qere_stay_separate(self):
        verse = self.synthetic('<w type="x-ketiv">אב</w>'
            '<note type="variant" n="empty"><catchWord>אב</catchWord><rdg type="x-qere"/></note>'
            '<note type="variant" n="multi"><catchWord>אב</catchWord><rdg type="x-qere" n="reading">'
            '<w id="a" lemma="1">ג</w><seg type="x-maqqef">־</seg><w id="b">ד</w></rdg></note>'
            '<note type="variant"><rdg type="x-qere"><w id="c">ה</w></rdg></note>')
        self.assertEqual(verse["written_text"], "אב")
        self.assertEqual([q["word_count"] for q in verse["qere"]], [0, 2, 1])
        self.assertEqual([q["catchwords"] for q in verse["qere"]], [["אב"], ["אב"], []])
        group = verse["qere"][1]
        self.assertEqual(group["note_attributes"]["n"], "multi")
        self.assertEqual(group["reading_attributes"]["n"], "reading")
        self.assertEqual([u["text"] for u in group["units"]], ["ג", "־", "ד"])
        self.assertEqual(verse["notes"][0]["content"]["children"][0]["text"], "אב")

    def test_non_qere_notes_and_qere_inline_content_retained(self):
        verse = self.synthetic('<w>א</w><note n="1">comment</note>'
            '<note type="alternative"><rdg type="x-accent"><w morph="HN">ב</w></rdg></note>'
            '<note type="variant"><rdg type="x-qere"><w>ג<seg type="x-small">ד</seg>ה</w></rdg></note>')
        self.assertEqual(verse["other_note_types"], {"unspecified": 1, "alternative": 1})
        self.assertEqual(verse["notes"][1]["content"]["children"][0]["children"][0]["attributes"], {"morph": "HN"})
        self.assertEqual(verse["qere"][0]["units"][0]["text"], "גדה")
        self.assertEqual(verse["qere"][0]["units"][0]["inline_annotations"][0]["offset"], 1)

    def test_unknown_book_foreign_missing_and_duplicate_verse_ids_fail(self):
        with self.assertRaises(ValueError):
            m.build_book("1Chr")
        for extra in ('<verse osisID="Exod.1.2"/>', '<verse/>',
                      '<verse osisID="Gen.1.1"/>', '<verse osisID="Gen.-1.1"/>'):
            with self.assertRaises(ValueError):
                self.synthetic('<w>א</w>', extra)

    def test_duplicate_word_ids_and_unknown_markup_fail_closed(self):
        for body in ('<w id="same">א</w><w id="same">ב</w>',
                     '<w>א<unknown>ב</unknown></w>', '<unknown/>',
                     '<seg type="x-pe"><w>פ</w></seg>',
                     '<note type="variant"><rdg type="x-qere"><unknown/></rdg></note>'):
            with self.assertRaises(ValueError):
                self.synthetic(body)

    def test_actual_qere_edge_contexts(self):
        sam = {(v["chapter"], v["verse"]): v for v in m.build_book("1SA")["verses"]}
        kings = {(v["chapter"], v["verse"]): v for v in m.build_book("2KI")["verses"]}
        self.assertEqual(sam[(20, 2)]["qere"][0]["word_count"], 2)
        self.assertEqual(kings[(5, 18)]["qere"][0]["word_count"], 0)
        self.assertEqual(kings[(19, 31)]["qere"][0]["catchwords"], [])

    def test_orphan_verse_and_qere_text_fail_without_losing_inline_tails(self):
        for body in ('ב<w>א</w>', '<w>א</w>ב',
                     '<w>א</w><seg type="x-pe">פ</seg>ב',
                     '<note type="variant"><rdg type="x-qere">ב<w>א</w></rdg></note>',
                     '<note type="variant"><rdg type="x-qere"><w>א</w>ב</rdg></note>',
                     '<note type="variant"><rdg type="x-qere"><seg type="x-maqqef">־</seg>ב</rdg></note>'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                self.synthetic(body)
        verse = self.synthetic('\n <w>א<seg type="x-large">ב</seg>ג</w> \n'
            '<note type="variant"><rdg type="x-qere">\n '
            '<w>ד<seg type="x-small">ה</seg>ו</w> \n</rdg></note> \n')
        self.assertEqual(verse["written_text"], "אבג")
        self.assertEqual(verse["qere"][0]["text"], "דהו")

    def test_cli_subset_scope_counts_and_read_only(self):
        paths = [m.ROOT / "sources/ot/wlc/1Chr.xml",
                 m.ROOT / "translation/ot/1_chronicles/012/014.yaml"]
        before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
        command = [sys.executable, "-m", "tools.textual_restoration.export_wlc_layers"]
        output = subprocess.check_output(command + ["--book", "1CH", "--verse", "12:14"], cwd=m.ROOT)
        result = json.loads(output)
        self.assertEqual(result["scope"], "selected-vendored-verse")
        self.assertEqual(result["counts"]["verse_contexts"], 1)
        self.assertEqual(result["source"]["attribution"], m.ATTRIBUTION)
        self.assertEqual(before, [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths])
        for args in (["--book", "1CH", "--verse", "999:999"], ["--all-summary", "--verse", "1:1"], ["--book", "1Chr"]):
            completed = subprocess.run(command + args, cwd=m.ROOT, capture_output=True)
            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(completed.stdout, b"")

    def test_all_39_current_exports_match_frozen_receipt(self):
        receipt = json.loads(RECEIPT.read_text())
        current = m.all_summary()
        self.assertEqual(current, receipt["result"])
        self.assertEqual(current["summary"]["books"], 39)
        self.assertEqual(current["summary"]["verse_contexts"], 23213)
        self.assertEqual(m.digest(m.json_bytes(current)), receipt["result_sha256"])
        screen = json.loads((m.ROOT / "sources/textual_restoration/comparisons/eleven_compound_screen.2026-10-12.v1.json").read_text())
        pins = screen["xml_input_pins"]
        for book in current["books"]:
            self.assertEqual(book["source_sha256"], pins[book["source_path"]])


if __name__ == "__main__":
    unittest.main()
