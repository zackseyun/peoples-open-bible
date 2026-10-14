import copy
import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
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

    def test_cached_execution_preserves_original_review_chronology_without_new_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request = {"params": {"model":"test"}, "packet_hash":"initial"}
            record = {"output_hash":"checked", "recorded_at":"2020-01-01T00:00:00Z",
                      "evidence_files":{"request":"saved.request.json", "response":"saved.response.json"}}
            for name, value in [("v0.review.record.json",record), ("v0.review.request.initial.json",request),
                                ("saved.request.json",request), ("saved.response.json",{})]:
                (root/name).write_text(json.dumps(value))
            before = (root/'v0.review.record.json').read_bytes()
            with patch.object(runner.transport,"ROOT",root), patch.object(runner.transport,"invoke") as invoke, \
                 patch.object(translation,"validate_response",return_value={"output_hash":"checked","recorded_at":"2099-01-01T00:00:00Z"}):
                self.assertEqual(runner.execute(request,root,'v0.review',root),record)
                invoke.assert_not_called()
                self.assertEqual((root/'v0.review.record.json').read_bytes(),before)
                with self.assertRaisesRegex(ValueError,"different request plan"):
                    runner.execute(dict(request,packet_hash='changed'),root,'v0.review',root)

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
