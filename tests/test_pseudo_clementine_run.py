import copy
import json
import unittest
from tools.extra_texts import pseudo_clementine_run as runner
from tools.extra_texts import pseudo_clementine_translation as translation


class BatchReviewTests(unittest.TestCase):
    def setUp(self):
        root = translation.source.SOURCE_ROOT / "pseudo_clementine_peter_to_james" / "translation_workflow"
        self.draft = json.loads((root / "lagarde-v3.draft.record.json").read_text())
        self.review = json.loads((root / "lagarde-v3.review.record.json").read_text())

    def test_source_and_evidence_failures_are_not_model_format_repairs(self):
        for message in ("Source changed after request preparation", "Request context changed",
                        "Unresolved blocking source issue requires separate source evidence"):
            self.assertFalse(runner.format_repairable(ValueError(message)))
        self.assertTrue(runner.format_repairable(ValueError("Audit quotation is not present in the supplied Greek")))

    def test_actual_review_is_accepted(self):
        self.assertTrue(runner.accepted(self.draft, self.review))

    def test_missing_changed_or_wrong_model_review_fails(self):
        for key, value in (("references", []), ("model", "different-model"), ("source_hash", "stale"), ("draft_output_hash", "stale")):
            bad = copy.deepcopy(self.review)
            bad[key] = value
            self.assertFalse(runner.accepted(self.draft, bad))
        bad = copy.deepcopy(self.review)
        bad["output"]["passages"].pop()
        bad["output_hash"] = translation.digest(bad["output"])
        self.assertFalse(runner.accepted(self.draft, bad))

    def test_substantive_finding_cannot_be_hidden_by_accept_label(self):
        bad = copy.deepcopy(self.review)
        bad["output"]["passages"][0]["findings"].append({"severity": "major"})
        bad["output_hash"] = translation.digest(bad["output"])
        self.assertFalse(runner.accepted(self.draft, bad))

    def test_unresolved_source_problem_still_blocks(self):
        draft, review = copy.deepcopy(self.draft), copy.deepcopy(self.review)
        draft["output"]["passages"][0]["source_issues"].append({"blocks_publication": True})
        draft["output_hash"] = translation.digest(draft["output"])
        review["draft_output_hash"] = draft["output_hash"]
        self.assertFalse(runner.accepted(draft, review))
