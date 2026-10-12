import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.extra_texts import pseudo_clementine_pages as pages


class PageReviewTests(unittest.TestCase):
    def setUp(self):
        self.lines = ["Πέτρος Ἰακώβῳ " * 12]
        self.accept = {"verdict": "accept", "checks": {k: True for k in pages.CHECKS}, "findings": [], "corrected_lines": []}

    def test_accept_requires_all_checks_no_changes_or_findings(self):
        pages.validate_review(self.accept, self.lines)
        for key in pages.CHECKS:
            bad = copy.deepcopy(self.accept)
            bad["checks"][key] = False
            with self.assertRaises(ValueError):
                pages.validate_review(bad, self.lines)
        bad = copy.deepcopy(self.accept)
        bad["findings"] = [{"issue": "Missing line"}]
        with self.assertRaises(ValueError):
            pages.validate_review(bad, self.lines)

    def test_revision_is_not_acceptance_and_must_change_text(self):
        result = dict(self.accept, verdict="revise", corrected_lines=self.lines)
        with self.assertRaises(ValueError):
            pages.validate_review(result, self.lines)
        result["corrected_lines"] = [self.lines[0] + "καὶ"]
        pages.validate_review(result, self.lines)

    def test_cli_error_classification_does_not_retry_denials(self):
        self.assertEqual(pages.classify_cli_failure("ConnectionError: request terminated"), "connection_error")
        self.assertEqual(pages.classify_cli_failure("403 Forbidden"), "authorization")
        self.assertEqual(pages.classify_cli_failure("content_filter"), "content_filter")
        self.assertEqual(pages.classify_cli_failure("unknown error"), "terminal_cli_error")

    def test_refuses_truncated_response(self):
        with self.assertRaises(ValueError):
            pages.parse_response({"choices": [{"finish_reason": "length", "message": {"content": "{}"}}]})

    def test_terminal_truncation_gets_bounded_distinct_requests(self):
        short = {"choices": [{"finish_reason": "length"}]}
        complete = {"choices": [{"finish_reason": "stop"}]}
        body = {"max_completion_tokens": 16000}
        with patch.object(pages, "_invoke_attempts", side_effect=[short, short, complete]) as call:
            self.assertEqual(pages.invoke(body, Path('/tmp'), Path('review-1.response')), complete)
            self.assertEqual(call.call_count, 3)
            self.assertEqual([str(x.args[2]) for x in call.call_args_list], ['review-1.response', 'review-1.response.tokens24000', 'review-1.response.tokens32000'])
            self.assertEqual(body['max_completion_tokens'], 32000)
        with patch.object(pages, "_invoke_attempts", return_value={"choices": [{"finish_reason": "content_filter"}]}) as call:
            pages.invoke({"max_completion_tokens":16000}, Path('/tmp'), Path('filtered'))
            self.assertEqual(call.call_count, 1)

    def test_checked_artifact_binds_text_image_review_and_model(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(pages, "SOURCE", Path(tmp)):
            root = Path(tmp)
            image = root / "page.png"
            image.write_bytes(b"test pixels")
            record = {"pdf_page": 47, "input_lines": self.lines, "image_sha256": pages.sha(image.read_bytes()), "model": "gpt-6.1-sol-2026-09-29", "review": self.accept, "request_sha256": "test-request"}
            pages.save(root / "review-1.response.attempt1.json", {"status": "success", "request_sha256": "test-request", "response": {"model": record["model"], "choices": [{"finish_reason": "stop", "message": {"content": json.dumps(self.accept)}}]}})
            pages.save(root / "review-1.json", record)
            checked = {"pdf_page": 47, "body_lines": self.lines, "body_lines_sha256": pages.sha(pages.canonical(self.lines)), "image_sha256": record["image_sha256"], "review_record": "review-1.json", "review_record_sha256": pages.sha(pages.canonical(record))}
            pages.save(root / "checked.json", checked)
            self.assertEqual(pages.verify_checked(root, image), checked)
            pages.save(root / "visual_controls.json", {"47": {"required_readings": ["νευουσῶν"]}})
            with patch.object(pages, "SOURCE", root):
                with self.assertRaisesRegex(ValueError, "visually verified"):
                    pages.verify_checked(root, image)
            receipt = root / "review-1.response.attempt1.json"
            original = receipt.read_text()
            receipt.write_text(json.dumps({"status": "error"}))
            with self.assertRaisesRegex(ValueError, "actual model response"):
                pages.verify_checked(root, image)
            receipt.write_text(original)
            image.write_bytes(b"different pixels")
            with self.assertRaises(ValueError):
                pages.verify_checked(root, image)


if __name__ == "__main__":
    unittest.main()
