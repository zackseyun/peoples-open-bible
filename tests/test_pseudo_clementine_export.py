import json
from pathlib import Path
import tempfile
import unittest
from tools.extra_texts import pseudo_clementine_export as export
from tools.extra_texts import pseudo_clementine_translation as tr


class ExportTests(unittest.TestCase):
    def test_incomplete_real_work_writes_nothing(self):
        selections = tr.source.SOURCE_ROOT / "pseudo_clementine_clement_to_james/translation_workflow/lagarde-batch-v1/accepted-sections-1-10.selections.json"
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp) / "reader"
            with self.assertRaisesRegex(ValueError, "Complete work"):
                export.export("pseudo_clementine_clement_to_james", selections, "0"*40, destination)
            self.assertFalse(destination.exists())

    def test_text_keeps_sections_english_and_all_disclosures(self):
        rows = [{"reference": "1.1", "text": "Exact reviewed words.",
                 "source_issues": [{"source_quote": "λόγος", "issue": "An explicit uncertainty.", "blocks_publication": False}],
                 "lexical_decisions": [{"source_quote": "λέγει", "chosen": "says", "rationale": "An alternate interpretation remains possible."}]},
                {"reference": "2.1", "text": "More exact words.", "source_issues": [], "lexical_decisions": []}]
        source = {"edition": "Test edition", "source_snapshot": {"url": "https://example.test/source"},
                  "passages": [{"reference":"1.1", "source_text":"λόγος λέγει"}, {"reference":"2.1", "source_text":"ἄλλα"}]}
        accepted = {"status": "complete_model_checked_candidate", "missing_references": [], "passages": rows}
        text = export.render_text("Test work",source,accepted)
        for value in ("HOMILY 1", "SECTION 1.1", "HOMILY 2", "SECTION 2.1",
                      "Exact reviewed words.", "An explicit uncertainty.", "An alternate interpretation remains possible.",
                      "not human scholarly sign-off", "not additional canonical Scripture"):
            self.assertIn(value,text)
        self.assertEqual(text.count("Exact reviewed words."),1)
        rows[0]["source_issues"][0]["blocks_publication"] = True
        with self.assertRaisesRegex(ValueError, "Unresolved"):
            export.render_text("Test work",source,accepted)

    def test_printed_lacuna_receives_explicit_edition_coverage_framing(self):
        source = {"edition":"Test edition", "source_snapshot":{"url":"https://example.test/source"},
                  "passages":[{"reference":"1.1", "source_text":"λόγος......."}]}
        row = {"reference":"1.1", "text":"Word.......", "lexical_decisions":[],
               "source_issues":[{"source_quote":"λόγος.......", "issue":"The checked print has a gap; no missing wording is reconstructed.", "blocks_publication":False}]}
        accepted = {"status":"complete_model_checked_candidate", "missing_references":[], "passages":[row]}
        text = export.render_text("Test",source,accepted)
        self.assertIn("Lost wording has not been reconstructed",text)
        self.assertIn("Word.......",text)
        row["text"] = "Word supplied by invention."
        with self.assertRaisesRegex(ValueError,"explicit and unfilled"):
            export.render_text("Test",source,accepted)

    def test_partial_status_cannot_be_hidden_by_an_empty_missing_list(self):
        with self.assertRaisesRegex(ValueError, "Partial"):
            export.render_text("Test",{},{"status":"partial_model_checked_candidate","missing_references":[]})

    def test_pin_requires_full_commit_and_matching_committed_bytes(self):
        with self.assertRaisesRegex(ValueError, "full pinned"):
            export.pinned_bytes("DOCTRINE.md","HEAD")
        with self.assertRaisesRegex(ValueError, "absent or changed"):
            export.pinned_bytes("DOCTRINE.md","0"*40)
