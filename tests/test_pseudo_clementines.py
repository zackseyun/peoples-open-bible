"""Pinned Greek acquisition is not permission to publish unchecked English."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from tools.extra_texts import catalog
from tools.extra_texts import pseudo_clementines as pc
from tools.extra_texts.validate_catalog import validate_catalog


class PseudoClementineTests(unittest.TestCase):
    def test_all_four_sources_validate_offline(self):
        for text_id in pc.WORKS:
            with self.subTest(work=text_id):
                self.assertEqual(pc.validate_source(text_id), [])

    def test_section_counts_and_homilies_gap_are_explicit(self):
        counts = []
        for text_id in pc.WORKS:
            manifest = json.loads((pc.SOURCE_ROOT / text_id / "manifest.json").read_text())
            counts.append(manifest["expected_units"])
            self.assertEqual(manifest["translation_policy"]["status"], "not_generated")
            self.assertEqual(manifest["review"]["philological"], "not_started")
        self.assertEqual(counts, [3, 5, 20, 505])
        gap = manifest["coverage"]
        self.assertEqual(gap["status"], "incomplete_work")
        self.assertEqual(gap["last_supplied_reference"], "19.14")
        self.assertEqual(gap["expected_homilies"], 20)
        self.assertTrue(gap["missing"])

    def test_sources_do_not_enter_reader_or_english_witness_bridge(self):
        from tools.extra_texts.draft_public_domain_witness import TEXTS
        entries = {e["id"]: e for e in catalog.load_entries()}
        published = {e["id"] for e in catalog.published_entries()}
        for text_id in pc.WORKS:
            self.assertIs(entries[text_id]["publish"], False)
            self.assertNotIn(text_id, published)
            self.assertNotIn(text_id, TEXTS)
            self.assertFalse((pc.ROOT / "translation/extra_canonical" / text_id).exists())
        self.assertEqual(len(published), 29)

    def test_publication_flag_cannot_bypass_source_only_gate(self):
        entries = catalog.load_entries()
        next(e for e in entries if e["id"] in pc.WORKS)["publish"] = True
        with patch.object(catalog, "load_entries", return_value=entries):
            with self.assertRaisesRegex(catalog.CatalogError, "source-only"):
                catalog.published_entries()

    def test_catalog_validator_rejects_changed_strategy_or_publication(self):
        payload = catalog.load_catalog()
        for row in payload["early_christian_apocrypha_order"]:
            if row["id"] in pc.WORKS:
                row["source"]["strategy"] = "pretend_approved"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "catalog.json"
            path.write_text(json.dumps(payload))
            errors = validate_catalog(path)
        self.assertEqual(sum("source-only work" in e for e in errors), 4)

    def test_prompt_is_greek_hash_bound_and_requires_separate_check(self):
        prompt = pc.draft_prompt("pseudo_clementine_peter_to_james", "1")
        self.assertIn("Πέτρος", prompt["source"]["source_text"])
        self.assertEqual(prompt["source"]["source_text_sha256"], pc.sha256(prompt["source"]["source_text"].encode()))
        self.assertEqual(prompt["required_followup"]["review_status"], "not_started")
        self.assertIn("Greek", prompt["instructions"])
        self.assertIn("CC BY-SA", prompt["rights_notice"])
        self.assertEqual(prompt["source_snapshot"]["commit"], pc.UPSTREAM_COMMIT)
        with self.assertRaisesRegex(ValueError, "not present"):
            pc.draft_prompt("pseudo_clementine_homilies", "20.1")

    def test_retains_salutation_and_internal_heading(self):
        peter = pc.draft_prompt("pseudo_clementine_peter_to_james", "1")["source"]
        self.assertTrue(peter["source_text"].startswith("Πέτρος Ἰακώβῳ"))
        homily = pc.draft_prompt("pseudo_clementine_homilies", "5.10")["source"]
        self.assertIn("Ο ΕΡΩΝ ΤΗ ΕΡΩΜΕΝΗ", homily["source_text"])

    def test_parser_preserves_text_on_both_sides_of_page_break(self):
        text_id = "pseudo_clementine_peter_to_james"
        raw = (pc.SOURCE_ROOT / text_id / "source.xml").read_bytes()
        raw = raw.replace(b'<p rend="indent">', b'<p rend="indent">BEFORE<pb facs="test"/>AFTER ', 1)
        row = pc.parse_source(raw, text_id)[0]
        self.assertIn("BEFOREAFTER", row["source_text"])
        self.assertIn({"facs": "test"}, row["page_breaks_within_section"])

    def test_parser_rejects_unreviewed_markup_license_and_numbering_changes(self):
        text_id = "pseudo_clementine_peter_to_james"
        raw = (pc.SOURCE_ROOT / text_id / "source.xml").read_bytes()
        variants = [
            raw.replace(b'<p rend="indent">', b'<p rend="indent"><gap/>', 1),
            raw.replace(pc.LICENSE_URL.encode(), b"https://example.org/unknown"),
            raw.replace(b'n="2"', b'n="7"'),
            raw.replace(b'<pb facs=', b'<p>UNMAPPED PREFACE</p><pb facs=', 1),
        ]
        for value in variants:
            with self.assertRaises(ValueError):
                pc.parse_source(value, text_id)

    def test_source_hash_normalization_and_review_claims_fail_closed(self):
        text_id = "pseudo_clementine_peter_to_james"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / text_id
            shutil.copytree(pc.SOURCE_ROOT / text_id, directory)
            manifest_path = directory / "manifest.json"
            original = json.loads(manifest_path.read_text())
            for field, value in [("translation_policy", {"status": "approved"}), ("coverage", {"status": "complete"}), ("review", {"philological": "approved"})]:
                altered = copy.deepcopy(original)
                altered[field] = value
                manifest_path.write_text(json.dumps(altered))
                self.assertTrue(pc.validate_source(text_id, root))
            manifest_path.write_text(json.dumps(original))
            source = directory / "source.xml"
            raw = source.read_bytes()
            source.write_bytes(raw + b"\n")
            self.assertTrue(any("source hash" in e for e in pc.validate_source(text_id, root)))
            source.write_bytes(raw)
            sections = directory / "sections.json"
            rows = json.loads(sections.read_text())
            rows[0]["source_text"] = "tampered"
            sections.write_text(json.dumps(rows))
            self.assertTrue(any("normalized source" in e for e in pc.validate_source(text_id, root)))

    def test_acquire_never_overwrites_existing_source(self):
        with self.assertRaisesRegex(ValueError, "overwrite"):
            pc.acquire("pseudo_clementine_peter_to_james")


if __name__ == "__main__":
    unittest.main()
