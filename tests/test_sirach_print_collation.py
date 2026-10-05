"""Scoped source repairs must reach prompts without inventing validation."""
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import hebrew_parallels
import build_translation_prompt
import lxx_swete


class SirachPrintCollationTests(unittest.TestCase):
    def tearDown(self):
        hebrew_parallels._SIR_COLLATION_CACHE = None

    def test_only_two_source_units_change_from_pinned_base(self):
        changed = []
        base = hebrew_parallels._load_sir()
        for chapter, data in base["chapters"].items():
            for verse in data["verses"]:
                if verse.get("hebrew"):
                    hit = hebrew_parallels.lookup("SIR", int(chapter), verse["verse"])
                    if hit["hebrew"] != verse["hebrew"]:
                        changed.append(f"SIR.{chapter}.{verse['verse']}")
        self.assertEqual(sorted(changed), ["SIR.51.19", "SIR.51.29"])

    def test_print_corrections_keep_their_limited_claim(self):
        hand = hebrew_parallels.lookup("SIR", 51, 19)
        self.assertIn("יָדִי פָתְחָה שְׁעָרֶיהָ", hand["hebrew"])
        self.assertIn("וְלָהּ אֶחֱדַר", hand["hebrew"])
        age = hebrew_parallels.lookup("SIR", 51, 29)
        self.assertIn("בְּישֵׂיבָתִי", age["hebrew"])
        self.assertFalse(hand["collation"]["earliest_hebrew_adjudicated"])
        self.assertEqual(hand["english_witness"], "")
        self.assertIn("not a diplomatic transcription", hand["note"])
        raw = hebrew_parallels.KAHANA_PRINT_COLLATION.read_bytes()
        self.assertEqual(hand["collation"]["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(json.loads(raw)["records"]["SIR.51.29"]["print_footnote_fact"].count("old age"), 1)

    def test_corpus_records_match_the_retrieved_corrected_source(self):
        for n in (19, 29):
            record = yaml.safe_load((hebrew_parallels.REPO_ROOT /
                f"translation/deuterocanon/sirach/051/{n:03}.yaml").read_text())
            hit = hebrew_parallels.lookup("SIR", 51, n)
            for key in ("edition", "pages", "collation", "note"):
                self.assertEqual(record["source"][key], hit[key])
            self.assertEqual(record["source"]["text"], hit["hebrew"])

    def test_prompt_source_identity_and_greek_parallel(self):
        verse = lxx_swete.SwtVerse("SIR", 51, 19, greek_text="fixture Greek",
                                 source_pages=[771], source_confidence="high",
                                 source_validation="agree")
        hit = hebrew_parallels.lookup("SIR", 51, 19)
        payload, labels = build_translation_prompt._build_source_payload(
            verse, {"zone_1_parallel": hit})
        self.assertEqual(payload["edition"], "pob-kahana-1912-collated")
        self.assertEqual(payload["text"], hit["hebrew"])
        self.assertEqual(payload["pages"], [118])
        self.assertNotIn("confidence", payload)
        self.assertNotIn("validation", payload)
        self.assertEqual(payload["parallel_sources"][0]["edition"], "lxx-swete-1909")
        self.assertEqual(payload["parallel_sources"][0]["text"], "fixture Greek")
        self.assertTrue(any("scoped Kahana 1912" in label for label in labels))
        self.assertFalse(any("Sefaria Ben Sira Kahana" in label for label in labels))

    def test_ordinary_source_payload_keeps_legacy_identity(self):
        verse = lxx_swete.SwtVerse("SIR", 51, 28, greek_text="fixture Greek")
        hit = hebrew_parallels.lookup("SIR", 51, 28)
        payload, labels = build_translation_prompt._build_source_payload(
            verse, {"zone_1_parallel": hit})
        self.assertEqual(payload["edition"], "sefaria-ben-sira-kahana")
        self.assertEqual(payload["text"], hit["hebrew"])
        self.assertNotIn("collation", payload)
        self.assertTrue(any("Sefaria Ben Sira Kahana" in label for label in labels))

    def test_changed_base_fails_closed(self):
        hebrew_parallels._load_sir()
        hebrew_parallels._SIR_COLLATION_CACHE = None
        with patch.object(hebrew_parallels, "SEFARIA_BEN_SIRA") as source:
            source.read_bytes.return_value = b"changed base"
            with self.assertRaisesRegex(ValueError, "base hash mismatch"):
                hebrew_parallels.lookup("SIR", 51, 19)
            # A failed scoped correction does not replace unrelated base units.
            ordinary = hebrew_parallels.lookup("SIR", 51, 28)
            self.assertNotIn("collation", ordinary)


if __name__ == "__main__":
    unittest.main()
