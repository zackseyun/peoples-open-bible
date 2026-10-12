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

    def test_refuses_truncated_response(self):
        with self.assertRaises(ValueError):
            pages.parse_response({"choices": [{"finish_reason": "length", "message": {"content": "{}"}}]})

    def test_checked_artifact_binds_text_image_review_and_model(self):
        with tempfile.TemporaryDirectory() as tmp:
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
