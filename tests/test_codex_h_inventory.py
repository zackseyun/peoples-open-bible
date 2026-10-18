"""Published completion markup must remain distinguishable from visible text."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / "tools/textual_restoration/inspect_codex_h_tei.py"
XML = b'''<teiCorpus xmlns="http://www.tei-c.org/ns/1.0">
<TEI><text><body><pb n="1v"/><lb/><ab n="1Cor.10.21">
<w><unclear reason="faded ink">ab</unclear></w><lb/>
<w><supplied source="na28" reason="illegible">cd</supplied></w>
<gap reason="illegible" unit="line" extent="2"/></ab></body></text></TEI>
<TEI><text><body><pb n="3r"/><ab n="1Cor.10.32">
<gap reason="lacuna" unit="char" extent="1"/></ab></body></text></TEI>
</teiCorpus>'''


class CodexHInventoryTests(unittest.TestCase):
    def run_inventory(self, extra_member=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "codex-h-2105_data.zip"
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("combined-xml.xml", XML)
                if extra_member:
                    bundle.writestr("unexpected.xml", XML)
            run = subprocess.run([sys.executable, str(SCRIPT), "--work-dir", str(root)],
                                 capture_output=True, text=True)
            if extra_member:
                return run.returncode
            self.assertEqual(run.returncode, 0, run.stderr)
            return json.loads((root / "codex-h-uncertainty-inventory.json").read_text())

    def test_supplied_is_not_unclear(self):
        report = self.run_inventory()
        unclear, supplied = report["events"][:2]
        self.assertEqual(unclear["tag"], "unclear")
        self.assertEqual(supplied["tag"], "supplied")
        self.assertEqual(supplied["attributes"]["source"], "na28")
        self.assertEqual(supplied["edition_text"], "cd")

    def test_gap_extent_and_milestones_are_preserved(self):
        report = self.run_inventory()
        first, second = report["events"][-2:]
        self.assertEqual(first["attributes"], {"reason": "illegible", "unit": "line", "extent": "2"})
        self.assertEqual((first["folio"], first["line"]), ("1v", 2))
        self.assertEqual((second["folio"], second["line"]), ("3r", 0))
        self.assertEqual(second["verse"], "1Cor.10.32")

    def test_counts_are_elements_and_xml_is_pinned(self):
        report = self.run_inventory()
        self.assertEqual(report["tag_counts"]["TEI"], 2)
        self.assertEqual(report["tag_counts"]["gap"], 2)
        self.assertEqual(report["xml_sha256"], hashlib.sha256(XML).hexdigest())

    def test_unexpected_archive_members_are_rejected(self):
        self.assertNotEqual(self.run_inventory(extra_member=True), 0)


if __name__ == "__main__":
    unittest.main()
