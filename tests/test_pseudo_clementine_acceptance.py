import copy
import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from tools.extra_texts import pseudo_clementine_acceptance as acceptance
from tools.extra_texts import pseudo_clementine_translation as translation
from tools.extra_texts.pseudo_clementine_selected import load_selected

WORK = "pseudo_clementine_clement_to_james"
BASE = "sources/early_christian_texts/" + WORK + "/translation_workflow/lagarde-batch-v1/batch-001/"


class AcceptanceTests(unittest.TestCase):
    def selection(self, refs):
        return {"references": refs, "draft": BASE + "v4.draft.record.json",
                "review": BASE + "v4.review.record.json"}

    def test_partial_positive_verdicts_are_not_whole_work_acceptance(self):
        result = acceptance.collect(WORK, [self.selection(["1", "2", "3", "5"])], complete=False)
        self.assertEqual(result["status"], "partial_model_checked_candidate")
        self.assertEqual(result["publication_status"], "not_published")
        self.assertIn("4", result["missing_references"])
        self.assertIn("20", result["missing_references"])
        self.assertEqual([r["reference"] for r in result["passages"]], ["1", "2", "3", "5"])
        with self.assertRaisesRegex(ValueError, "Complete work"):
            acceptance.collect(WORK, [self.selection(["1", "2", "3", "5"])])

    def test_rejected_section_and_duplicates_fail(self):
        with self.assertRaisesRegex(ValueError, "not passed"):
            acceptance.collect(WORK, [self.selection(["4"])], complete=False)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            acceptance.collect(WORK, [self.selection(["1"]), self.selection(["1"])], complete=False)

    def test_stale_greek_cannot_inherit_acceptance(self):
        rows = copy.deepcopy(load_selected(WORK)["passages"])
        rows[0]["source_text"] += " changed"
        with self.assertRaisesRegex(ValueError, "source is stale"):
            acceptance.validate_bundle(WORK, rows, BASE + "v4.draft.record.json", BASE + "v4.review.record.json")

    def test_minor_findings_do_not_override_failed_check(self):
        row = {"verdict": "accept", "checks": {k: True for k in translation.CHECKS},
               "findings": [{"severity": "minor"}]}
        self.assertTrue(acceptance.accepted_passage(row))
        row["checks"]["complete_coverage"] = False
        self.assertFalse(acceptance.accepted_passage(row))

    def test_later_adverse_finding_is_not_cherry_picked_away(self):
        original_path = acceptance.safe_path
        draft = json.loads(original_path(BASE + "v4.draft.record.json").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            later = Path(tmp) / "later.review.record.json"
            packet = Path(tmp) / "later.request.json"
            later.write_text(json.dumps({"recorded_at": "2099-01-01T00:00:00Z",
                "output": {"passages": [{"reference": "1", "verdict": "revise"}]},
                "evidence_files": {"request": "test-later-request"}}))
            packet.write_text(json.dumps({"context": {"draft": draft["output"]}}))
            def resolve(value):
                return packet if value == "test-later-request" else original_path(value)
            with patch.object(Path, "rglob", return_value=[later]), patch.object(acceptance, "safe_path", side_effect=resolve):
                with self.assertRaisesRegex(ValueError, "Later unresolved"):
                    acceptance.collect(WORK, [self.selection(["1"])], complete=False)

    def test_paths_cannot_escape_repository(self):
        with self.assertRaises(ValueError):
            acceptance.safe_path("../../outside.json")

    def test_current_policy_requirement_rejects_old_review_and_invented_ref(self):
        rule = {"references": ["1"], "policy_sha256": translation.digest_policy()}
        with patch.object(acceptance, "publication_requirements", return_value=rule):
            with self.assertRaisesRegex(ValueError, "current-policy"):
                acceptance.collect(WORK, [self.selection(["1"])], complete=False)
        rule["references"] = ["999"]
        with patch.object(acceptance, "publication_requirements", return_value=rule):
            with self.assertRaisesRegex(ValueError, "invented section"):
                acceptance.collect(WORK, [], complete=False)

    def test_policy_requirement_itself_is_validated_against_current_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            workflow = Path(tmp)
            path = workflow / "publication-requirements.json"
            self.assertEqual(acceptance.publication_requirements(workflow), {})
            rule = {"kind": "required_current_policy_review", "references": ["1"],
                    "policy_sha256": translation.digest_policy()}
            path.write_text(json.dumps(rule))
            self.assertEqual(acceptance.publication_requirements(workflow), rule)
            for invalid in [dict(rule, policy_sha256="stale"), dict(rule, references=["1", "1"]),
                            dict(rule, references=[]), dict(rule, kind="invented")]:
                path.write_text(json.dumps(invalid))
                with self.assertRaises(ValueError):
                    acceptance.publication_requirements(workflow)
