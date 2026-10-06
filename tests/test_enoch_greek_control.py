"""Checked edited Greek can inform a prompt without becoming its primary source."""

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.enoch import multi_witness
from tools.enoch import build_translation_prompt as prompts


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "sources/enoch/greek/verified/flemming_1901/001/009.json"


class EnochGreekControlTest(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(RECORD.read_text(encoding="utf-8"))

    def test_real_control_keeps_complete_edition_ending_and_raw_ocr(self):
        control = multi_witness.load_greek_edition_control(1, 9)
        self.assertEqual(control.text, self.record["text"])
        self.assertTrue(control.text.endswith("κατ' αὐτοῦ ἁμαρτωλοὶ ἀσεβεῖς."))
        self.assertEqual(hashlib.sha256(control.text.encode()).hexdigest(), self.record["text_sha256"])
        raw = (ROOT / self.record["raw_ocr"]["repo_path"]).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), self.record["raw_ocr"]["sha256"])
        self.assertNotIn("αὐτοῦ ἁμαρτωλοὶ ἀσεβεῖς.", raw.decode())
        self.assertIn("not a diplomatic manuscript reading", control.note)
        self.assertIn("primary Ge'ez/source promotion", control.note)

    def test_aggregator_exposes_control_without_assigning_a_manuscript(self):
        witnesses = multi_witness.load_verse(1, 9)
        self.assertTrue(witnesses.has_greek())
        self.assertIn(witnesses.greek_edition_control, witnesses.available_witnesses())
        self.assertIsNone(witnesses.greek_panopolitanus)
        self.assertIsNone(witnesses.greek_syncellus)
        self.assertIsNone(witnesses.greek_chester_beatty)

    def test_absent_control_does_not_reconstruct_from_raw_ocr(self):
        self.assertIsNone(multi_witness.load_greek_edition_control(1, 8))
        witnesses = multi_witness.load_verse(1, 8)
        self.assertFalse(witnesses.has_greek())
        bundle = prompts.build_enoch_prompt(1, 8)
        self.assertIsNone(bundle.witness_set["greek_edition_control"])
        self.assertIn("no checked local record for this verse", bundle.prompt)

    def test_prompt_exposes_complete_control_but_primary_payload_is_unchanged(self):
        with patch.object(prompts, "load_greek_edition_control", return_value=None):
            without_control = prompts.build_enoch_prompt(1, 9)
        with_control = prompts.build_enoch_prompt(1, 9)
        self.assertEqual(with_control.source_payload, without_control.source_payload)
        self.assertEqual(with_control.source_payload["edition"], "charles-1906-enoch")
        self.assertEqual(with_control.source_payload["language"], "Geez")
        self.assertIn(self.record["text"], with_control.prompt)
        self.assertIn("Edited comparative control", with_control.prompt)
        self.assertIn("do not silently substitute or harmonize", with_control.prompt)
        self.assertEqual(with_control.witness_set["greek_edition_control"]["text"], self.record["text"])
        self.assertEqual(len(with_control.witness_set["available_witnesses"]), 2)
        self.assertTrue(any("comparative control only" in label for label in with_control.zone1_sources_at_draft))

    def _load_temporary(self, record, *, malformed=False, changed_raw=False):
        with tempfile.TemporaryDirectory(prefix="pob-enoch-control-") as temporary:
            root = Path(temporary)
            target = root / "sources/enoch/greek/verified/flemming_1901/001/009.json"
            target.parent.mkdir(parents=True)
            target.write_text("{invalid" if malformed else json.dumps(record), encoding="utf-8")
            raw = root / self.record["raw_ocr"]["repo_path"]
            raw.parent.mkdir(parents=True)
            original = (ROOT / self.record["raw_ocr"]["repo_path"]).read_bytes()
            raw.write_bytes(original + (b"mutation" if changed_raw else b""))
            with patch.object(multi_witness, "REPO_ROOT", root), patch.object(multi_witness, "SOURCES_ROOT", root / "sources/enoch"):
                return multi_witness.load_greek_edition_control(1, 9)

    def test_valid_temporary_record_loads(self):
        self.assertEqual(self._load_temporary(self.record).text, self.record["text"])

    def test_malformed_present_record_fails_closed(self):
        with self.assertRaises(ValueError):
            self._load_temporary(self.record, malformed=True)

    def test_reference_basis_text_and_pins_cannot_be_silently_repaired(self):
        mutations = [
            ("schema_version", True),
            ("chapter", 2),
            ("verse", 8),
            ("reference", "1 Enoch 1:8"),
            ("edition", "Chester Beatty 1901"),
            ("reading_basis", "diplomatic-papyrus"),
            ("text", self.record["text"] + " καί"),
            ("text_sha256", "0" * 64),
            ("limits", []),
        ]
        for key, value in mutations:
            with self.subTest(key=key):
                candidate = copy.deepcopy(self.record)
                candidate[key] = value
                with self.assertRaises(ValueError):
                    self._load_temporary(candidate)
        for field in ("sha256", "repo_path"):
            with self.subTest(missing_raw_field=field):
                candidate = copy.deepcopy(self.record)
                del candidate["raw_ocr"][field]
                with self.assertRaises(ValueError):
                    self._load_temporary(candidate)

    def test_changed_raw_input_or_escaping_path_is_rejected(self):
        with self.assertRaises(ValueError):
            self._load_temporary(self.record, changed_raw=True)
        candidate = copy.deepcopy(self.record)
        candidate["raw_ocr"]["repo_path"] = "sources/enoch/greek/transcribed/../../../../../outside.txt"
        with self.assertRaises(ValueError):
            self._load_temporary(candidate)

    def test_invalid_present_control_aborts_prompt_instead_of_dropping_it(self):
        with patch.object(prompts, "load_greek_edition_control", side_effect=ValueError("pin mismatch")):
            with self.assertRaisesRegex(ValueError, "pin mismatch"):
                prompts.build_enoch_prompt(1, 9)

    def test_summary_separates_presence_from_unverified_completeness(self):
        state = multi_witness.summary()
        self.assertTrue(state["greek_ocr_present"])
        self.assertIsNone(state["greek_ocr_complete"])
        self.assertTrue(state["greek_edition_controls_present"])


if __name__ == "__main__":
    unittest.main()
