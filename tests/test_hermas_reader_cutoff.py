"""The restored cutoff must reach both written readers without stale bases."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import yaml

from tools import export_mobile_bible as exporter
from tools import shepherd_of_hermas as hermas

ROOT = Path(__file__).resolve().parents[1]
SLUG = Path("extra_canonical/shepherd_of_hermas")


class HermasReaderCutoffTests(unittest.TestCase):
    def test_both_exports_have_six_complete_paragraphs(self):
        for edition in ("translation", "translation_simplified"):
            with self.subTest(edition=edition), patch.object(
                exporter, "EXTRA_CANONICAL_ROOT", ROOT / edition / "extra_canonical"
            ):
                book = exporter.export_extra_canonical_book("HERM")
                chapter = next(c for c in book["chapters"] if c["chapter"] == 63)
                assert [v["verse"] for v in chapter["verses"]] == list(range(1, 7))
                assert chapter["verses"][4]["text"].endswith("with the first group.")
                assert "half dry and cracked" in chapter["verses"][5]["text"]
                assert "others apart." in chapter["verses"][5]["text"]

    def test_standard_reader_parent_source_and_simplified_bases_are_current(self):
        source = hermas.load_unit("S.8.iv").text
        flat = yaml.safe_load((ROOT / "translation" / SLUG / "063.yaml").read_text())
        assert len(flat["translation"]["text"].split("\n\n")) == 6
        for verse in range(1, 7):
            tail = SLUG / "063" / f"{verse:03d}.yaml"
            full = yaml.safe_load((ROOT / "translation" / tail).read_text())
            simple = yaml.safe_load((ROOT / "translation_simplified" / tail).read_text())
            assert full["source"]["text"] == source
            assert full["source"]["reader_segment"] == verse
            assert simple["base_translation"]["text"] == full["translation"]["text"]
        assert "without cracks" in full["translation"]["text"]
        assert "had not been eaten" in full["translation"]["text"]

    def test_new_paragraph_is_identified_and_does_not_claim_independent_review(self):
        for edition in ("translation", "translation_simplified"):
            doc = yaml.safe_load((ROOT / edition / SLUG / "063/006.yaml").read_text())
            assert doc["id"] == "HERM.S.8.iv.6"
            assert doc["source"]["reader_segment"] == 6
            assert doc["status"] == "draft"
            assert doc["translation"]["philosophy"] == "optimal-equivalence"
            provenance = doc.get("ai_draft_provenance") or doc["ai_draft"]
            assert provenance["independent_review"] is False
        record = json.loads((ROOT / "sources/shepherd_of_hermas/repair/reader-cutoff-20261103.v1.json").read_text())
        assert record["reader_crosswalk"][-1]["after"] == "63:6"
        repaired = yaml.safe_load((ROOT / "translation" / SLUG / "063/005.yaml").read_text())
        archive = next(x for x in repaired["review_history"] if x.get("field") == "cross_check")
        assert archive["certifies_repaired_text"] is False
        assert archive["value"]["status"] == "high_agreement"
        assert repaired["cross_check"]["status"] == "needs_review"
