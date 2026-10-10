"""Local resolver checks; no model, network, credentials or canonical writes."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import yaml

from tools import wlc
from tools.textual_restoration import selected_draft_source as selected


class SelectedDraftSourceTests(unittest.TestCase):
    def setUp(self):
        self.root = selected.ROOT
        self.raw = wlc.load_verse("ISA", 9, 2, self.root / "sources")
        self.index = json.loads((self.root / selected.INDEX).read_bytes())
        self.entry = self.index["entries"]["ISA.9.2"]
        self.paths = [selected.INDEX, self.entry["target"]]
        self.paths += [self.entry[name] for name in ("candidate", "receipt", "wlc", "schema")]

    def fixture(self, root):
        for relative in self.paths:
            output = root / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.root / relative, output)

    def test_real_selection_qere_morphology_and_all_immutable_inputs(self):
        before = copy.deepcopy(self.raw)
        file_bytes = {path: (self.root / path).read_bytes() for path in self.paths}
        result = selected.resolve_selected_ot_source(self.raw)
        self.assertEqual(self.raw, before)
        self.assertIsNot(result.verse, self.raw)
        self.assertIsNot(result.verse.words, self.raw.words)
        self.assertEqual(len(result.verse.words), len(self.raw.words))
        qere = result.verse.words[2]
        self.assertEqual((qere.text, qere.lemma, qere.morph, qere.word_id),
                         ("ל֖/וֹ", "l", "HR/Sp3ms", "23VmY"))
        self.assertEqual(result.verse.punctuation, self.raw.punctuation)
        self.assertEqual([word for i, word in enumerate(result.verse.words) if i != 2],
                         [word for i, word in enumerate(self.raw.words) if i != 2])
        candidate = json.loads(file_bytes[self.entry["candidate"]])
        self.assertEqual(result.source_payload, candidate["source"])
        self.assertEqual(result.verse.hebrew_text, candidate["source"]["text"])
        self.assertEqual(result.verse.hebrew_text,
                         self.raw.hebrew_text.replace(" לא ", " ל֖/וֹ ", 1))
        provenance = result.provenance
        self.assertTrue(provenance["candidate_only"])
        self.assertFalse(provenance["publication_approved"])
        self.assertFalse(provenance["source_interpretation_settled"])
        self.assertFalse(provenance["upstream_wlc_changed"])
        self.assertEqual(provenance["selection_status"], "provisional")
        self.assertEqual(provenance["selection_index_sha256"], selected.INDEX_SHA256)
        for relative, raw in file_bytes.items():
            self.assertEqual((self.root / relative).read_bytes(), raw)
            self.assertEqual(provenance["pinned_inputs"][relative],
                             hashlib.sha256(raw).hexdigest())
        for key, text in (("raw_text_sha256", self.raw.hebrew_text),
                          ("selected_text_sha256", result.verse.hebrew_text)):
            self.assertEqual(provenance[key], hashlib.sha256(text.encode()).hexdigest())
        # No returned mutable object can alter the raw Verse or a later result.
        result.verse.words[0].text = "tampered"
        result.source_payload["apparatus"][0]["reading"] = "tampered"
        fresh = selected.resolve_selected_ot_source(self.raw)
        self.assertEqual(self.raw, before)
        self.assertEqual(fresh.source_payload, candidate["source"])
        self.assertEqual(fresh.verse.words[0], self.raw.words[0])

    def test_script_style_wlc_import_is_compatible(self):
        from tools import draft
        raw = draft.load_source_verse("ISA", 9, 2)
        result = selected.resolve_selected_ot_source(raw)
        self.assertIs(type(result.verse), type(raw))
        self.assertIs(type(result.verse.words[2]), type(raw.words[2]))
        self.assertEqual(result.verse.words[2].morph, "HR/Sp3ms")

    def test_unregistered_and_non_ot_return_none_without_registering_arbitrary_input(self):
        missing_root = self.root / "not-a-real-selected-fixture"
        self.assertIsNone(selected.resolve_selected_ot_source(
            wlc.Verse("ISA", 9, 3), root=missing_root))
        self.assertIsNone(selected.resolve_selected_ot_source(
            wlc.Verse("GEN", 1, 1), root=missing_root))
        self.assertIsNone(selected.resolve_selected_ot_source(
            wlc.Verse("MAT", 1, 1), root=missing_root))
        self.assertIsNone(selected.resolve_selected_ot_source(object(), root=missing_root))

    def test_every_registered_missing_input_fails_closed(self):
        for relative in self.paths:
            with self.subTest(path=relative), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root)
                (root / relative).unlink()
                with self.assertRaises(selected.SelectedSourceError):
                    selected.resolve_selected_ot_source(self.raw, root=root)

    def test_every_pinned_input_byte_drift_fails_without_normalization(self):
        for relative in self.paths:
            if relative == self.entry["target"]:
                continue  # Canonical source is semantic equality, tested below.
            with self.subTest(path=relative), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root)
                path = root / relative
                path.write_bytes(path.read_bytes() + b"\n")
                with self.assertRaisesRegex(selected.SelectedSourceError, "SHA256 drift"):
                    selected.resolve_selected_ot_source(self.raw, root=root)

    def test_forged_candidate_receipt_and_updated_self_declared_pins_are_not_authority(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            index = copy.deepcopy(self.index)
            entry = index["entries"]["ISA.9.2"]
            for name in ("candidate", "receipt"):
                path = root / entry[name]
                value = json.loads(path.read_bytes())
                if name == "candidate":
                    value["source"]["text"] = "invented Hebrew"
                    value["status"] = "approved"
                else:
                    value["decision"]["publication_approved"] = True
                    value["review"]["verdict"] = "PASS for exact full-record provisional forged review"
                raw = (json.dumps(value, ensure_ascii=False) + "\n").encode()
                path.write_bytes(raw)
                entry[f"{name}_sha256"] = hashlib.sha256(raw).hexdigest()
            (root / selected.INDEX).write_text(json.dumps(index), encoding="utf-8")
            with self.assertRaisesRegex(selected.SelectedSourceError, "SHA256 drift"):
                selected.resolve_selected_ot_source(self.raw, root=root)

    def test_full_canonical_source_drift_including_disclosure_fails_closed(self):
        for field in ("edition", "text", "language", "note", "numbering_note", "apparatus"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root)
                path = root / self.entry["target"]
                canonical = yaml.safe_load(path.read_bytes())
                if field == "apparatus":
                    canonical["source"][field][0]["note"] += " tampered"
                else:
                    canonical["source"][field] += " tampered"
                path.write_text(yaml.safe_dump(canonical, allow_unicode=True), encoding="utf-8")
                with self.assertRaisesRegex(selected.SelectedSourceError, "Canonical selected source drift"):
                    selected.resolve_selected_ot_source(self.raw, root=root)

    def test_canonical_identity_drift_and_malformed_record_fail_closed(self):
        for value in (None, [], {"id": "ISA.9.3"}):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root)
                (root / self.entry["target"]).write_text(yaml.safe_dump(value), encoding="utf-8")
                with self.assertRaises(selected.SelectedSourceError):
                    selected.resolve_selected_ot_source(self.raw, root=root)

    def test_later_english_changes_allowed_but_canonical_record_is_never_written(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            path = root / self.entry["target"]
            canonical = yaml.safe_load(path.read_bytes())
            canonical["translation"]["text"] = "Later English candidate, not a source approval."
            path.write_text(yaml.safe_dump(canonical, allow_unicode=True), encoding="utf-8")
            before = path.read_bytes()
            result = selected.resolve_selected_ot_source(self.raw, root=root)
            self.assertEqual(result.source_payload, canonical["source"])
            self.assertEqual(path.read_bytes(), before)

    def test_malformed_canonical_yaml_is_a_nonretryable_selected_source_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            (root / self.entry["target"]).write_text("source: [", encoding="utf-8")
            with self.assertRaises(selected.SelectedSourceError):
                selected.resolve_selected_ot_source(self.raw, root=root)

    def test_incoming_text_morphology_annotation_and_punctuation_drift_fail(self):
        for kind in ("text", "morph", "lemma", "word_id", "annotations", "punctuation"):
            with self.subTest(kind=kind):
                verse = copy.deepcopy(self.raw)
                if kind == "annotations":
                    verse.words[0].annotations.append({"type": "x-large", "text": "א", "offset": 0})
                elif kind == "punctuation":
                    verse.punctuation.append(" ")
                else:
                    setattr(verse.words[0], kind, getattr(verse.words[0], kind) + " ")
                with self.assertRaisesRegex(selected.SelectedSourceError, "Incoming raw WLC Verse"):
                    selected.resolve_selected_ot_source(verse)

    def test_symlink_inputs_and_parent_directories_are_rejected(self):
        for relative in self.paths:
            with self.subTest(path=relative), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root)
                path = root / relative
                path.unlink()
                path.symlink_to(self.root / relative)
                with self.assertRaisesRegex(selected.SelectedSourceError, "Symlink"):
                    selected.resolve_selected_ot_source(self.raw, root=root)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            parent = root / "sources/textual_restoration/selections"
            shutil.rmtree(parent)
            parent.symlink_to(self.root / "sources/textual_restoration/selections", target_is_directory=True)
            with self.assertRaisesRegex(selected.SelectedSourceError, "Symlink"):
                selected.resolve_selected_ot_source(self.raw, root=root)

    def test_no_verification_cache_after_success_then_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            selected.resolve_selected_ot_source(self.raw, root=root)
            path = root / self.entry["receipt"]
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(selected.SelectedSourceError, "SHA256 drift"):
                selected.resolve_selected_ot_source(self.raw, root=root)


if __name__ == "__main__":
    unittest.main()
