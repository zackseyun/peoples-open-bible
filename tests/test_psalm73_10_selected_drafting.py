"""Exact Psalm 73:10 drafting selection; mocked generation, no canonical writes.

These checks establish operational integrity, not historical source priority or
publication approval. The actual reviewed v2 index and receipt are required.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import yaml

os.environ.setdefault("CARTHA_DRAFTER_BACKEND", "openai-sdk")
from tools import draft, wlc
from tools.textual_restoration import selected_draft_source as selected


class PsalmSelectedResolverTests(unittest.TestCase):
    def setUp(self):
        self.root = selected.ROOT
        self.raw = wlc.load_verse("PSA", 73, 10, self.root / "sources")
        self.index = json.loads((self.root / selected.INDEX).read_bytes())
        self.entry = self.index["entries"]["PSA.73.10"]
        self.paths = [selected.INDEX, self.entry["target"]]
        self.paths += [self.entry[name] for name in ("candidate", "receipt", "wlc", "schema")]

    def fixture(self, root):
        for relative in self.paths:
            output = root / relative
            output.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.root / relative, output)

    def test_actual_qal_replaces_one_written_word_and_preserves_immutable_base(self):
        before = copy.deepcopy(self.raw)
        inputs = {path: (self.root / path).read_bytes() for path in self.paths}
        result = selected.resolve_selected_ot_source(self.raw)
        self.assertEqual(self.raw, before)
        self.assertIsNot(result.verse, self.raw)
        self.assertIsNot(result.verse.words, self.raw.words)
        self.assertEqual(len(result.verse.words), len(self.raw.words))
        self.assertEqual((self.raw.words[1].text, self.raw.words[1].morph),
                         ("ישיב", "HVhi3ms"))
        qere = result.verse.words[1]
        self.assertEqual((qere.text, qere.lemma, qere.morph, qere.word_id),
                         ("יָשׁ֣וּב", "7725", "HVqi3ms", "19h5B"))
        self.assertEqual(result.verse.hebrew_text,
                         self.raw.hebrew_text.replace(" ישיב ", " יָשׁ֣וּב ", 1))
        self.assertEqual(result.verse.punctuation, self.raw.punctuation)
        self.assertEqual([w for i, w in enumerate(result.verse.words) if i != 1],
                         [w for i, w in enumerate(self.raw.words) if i != 1])
        candidate = json.loads(inputs[self.entry["candidate"]])
        self.assertEqual(result.source_payload, candidate["source"])
        self.assertEqual(result.verse.hebrew_text, candidate["source"]["text"])
        for relative, raw in inputs.items():
            self.assertEqual((self.root / relative).read_bytes(), raw)
            self.assertEqual(result.provenance["pinned_inputs"][relative],
                             hashlib.sha256(raw).hexdigest())
        self.assertTrue(result.provenance["candidate_only"])
        self.assertFalse(result.provenance["publication_approved"])
        self.assertFalse(result.provenance["source_interpretation_settled"])
        self.assertFalse(result.provenance["upstream_wlc_changed"])
        result.verse.words[1].text = "tampered"
        result.source_payload["apparatus"][0]["reading"] = "tampered"
        self.assertEqual(selected.resolve_selected_ot_source(self.raw).source_payload,
                         candidate["source"])
        self.assertEqual(self.raw, before)

    def test_all_pinned_input_byte_drift_fails_closed(self):
        for relative in self.paths:
            if relative == self.entry["target"]:
                continue
            with self.subTest(path=relative), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root)
                path = root / relative
                path.write_bytes(path.read_bytes() + b"\n")
                with self.assertRaisesRegex(selected.SelectedSourceError, "SHA256 drift"):
                    selected.resolve_selected_ot_source(self.raw, root=root)

    def test_full_canonical_disclosure_equality_is_required(self):
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

    def test_incoming_raw_morphology_and_identity_drift_fail_closed(self):
        for kind in ("text", "morph", "lemma", "word_id", "annotations", "punctuation"):
            with self.subTest(kind=kind):
                raw = copy.deepcopy(self.raw)
                if kind == "annotations":
                    raw.words[1].annotations.append({"type": "x-large", "text": "א", "offset": 0})
                elif kind == "punctuation":
                    raw.punctuation.append(" ")
                else:
                    setattr(raw.words[1], kind, getattr(raw.words[1], kind) + " ")
                with self.assertRaisesRegex(selected.SelectedSourceError, "Incoming raw WLC Verse"):
                    selected.resolve_selected_ot_source(raw)

    def test_code_trusted_registration_has_distinct_psalm_and_isaiah_analyses(self):
        self.assertEqual(selected.REGISTERED_IDS, frozenset({"ISA.9.2", "PSA.73.10"}))
        self.assertEqual(selected.REGISTERED_SOURCES["PSA.73.10"], {
            "target": "translation/ot/psalms/073/010.yaml",
            "wlc": "sources/ot/wlc/Ps.xml", "osis_id": "Ps.73.10",
            "qere_lemma": "7725", "qere_morph": "HVqi3ms"})
        self.assertEqual(selected.REGISTERED_SOURCES["ISA.9.2"]["qere_lemma"], "l")
        self.assertEqual(selected.REGISTERED_SOURCES["ISA.9.2"]["qere_morph"], "HR/Sp3ms")


class PsalmSelectedDraftingIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.verse = draft.load_source_verse("PSA", 73, 10)
        self.path = draft.translation_path_for_verse(self.verse)
        self.before = self.path.read_bytes()
        self.resolved = selected.resolve_selected_ot_source(self.verse)
        index = json.loads((selected.ROOT / selected.INDEX).read_bytes())
        entry = index["entries"]["PSA.73.10"]
        candidate = json.loads((selected.ROOT / entry["candidate"]).read_bytes())
        self.tool = {
            "english_text": candidate["translation"]["text"],
            "translation_philosophy": "optimal-equivalence",
            "lexical_decisions": [copy.deepcopy(candidate["lexical_decisions"][1])],
            "footnotes": copy.deepcopy(candidate["translation"]["footnotes"]),
            "source_distinction_checks": [],
        }

    def tearDown(self):
        self.assertEqual(self.path.read_bytes(), self.before)

    def model_response(self):
        return (copy.deepcopy(self.tool), "fixture-model-version", "{}", 0.2)

    def test_prompt_uses_qal_qere_not_hiphil_written_analysis(self):
        prompt = draft.build_selected_source_prompt(self.verse)
        source_section, tail = prompt.split("# Morphology table", 1)
        morphology = tail.split("# DOCTRINE.md excerpt", 1)[0]
        self.assertIn(self.resolved.source_payload["text"], source_section)
        self.assertIn("selected Masoretic reading form", source_section)
        self.assertIn("written_text", source_section)
        self.assertIn("יָשׁ֣וּב", morphology)
        self.assertIn("morph=HVqi3ms", morphology)
        self.assertNotIn("morph=HVhi3ms", morphology)
        self.assertIn("base-edition context only, not selected readings", prompt)
        self.assertIn("unapproved candidate", prompt)
        self.assertIn(" ישיב ", draft.source_text_for_verse(self.verse))

    def test_candidate_generation_preserves_full_source_and_provenance_without_write(self):
        with patch.object(draft, "call_model", return_value=self.model_response()) as model, \
                patch.object(draft, "validate_tool_input", wraps=draft.validate_tool_input) as validation, \
                patch.object(draft.distinctions, "bind_draft_checks", wraps=draft.distinctions.bind_draft_checks) as binding, \
                patch.object(draft, "write_verse_yaml") as write:
            result = draft.draft_selected_source_candidate(self.verse, model="fixture-model")
        self.assertEqual(result.verse.hebrew_text, self.resolved.source_payload["text"])
        self.assertEqual(validation.call_args.args[0].hebrew_text, self.resolved.source_payload["text"])
        self.assertEqual(binding.call_args.args[0]["source"], self.resolved.source_payload)
        self.assertEqual(result.record["source"], self.resolved.source_payload)
        self.assertEqual(result.record["ai_draft"]["selected_source_at_draft"], self.resolved.provenance)
        self.assertEqual(result.record["status"], "draft")
        self.assertNotIn("review_history", result.record)
        self.assertNotIn("revision_pass", result.record)
        self.assertIn(self.resolved.source_payload["text"], model.call_args.kwargs["user"])
        self.assertTrue(draft.distinctions.receipt_is_current(result.record))
        draft.validate_record(result.record)
        write.assert_not_called()

    def test_raw_route_refuses_before_model_even_without_write(self):
        with patch.object(draft, "call_model") as model:
            for write in (False, True):
                with self.subTest(write=write), self.assertRaisesRegex(
                        ValueError, "Selected-source regeneration required"):
                    draft.draft_verse(self.verse, write=write)
            model.assert_not_called()

    def test_pre_model_resolver_drift_cannot_fall_back_to_raw_source(self):
        with patch.object(draft, "_selected_ot_source", side_effect=selected.SelectedSourceError("fixture drift")), \
                patch.object(draft, "call_model") as model:
            with self.assertRaisesRegex(ValueError, "fixture drift"):
                draft.draft_selected_source_candidate(self.verse)
            model.assert_not_called()

    def test_post_model_drift_discards_candidate_without_canonical_write(self):
        with patch.object(draft, "_selected_ot_source", side_effect=[
                self.resolved, selected.SelectedSourceError("fixture drift")]), \
                patch.object(draft, "call_model", return_value=self.model_response()) as model, \
                patch.object(draft, "write_verse_yaml") as write:
            with self.assertRaisesRegex(ValueError, "fixture drift"):
                draft.draft_selected_source_candidate(self.verse)
            model.assert_called_once()
            write.assert_not_called()


if __name__ == "__main__":
    unittest.main()
