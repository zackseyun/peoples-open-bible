import copy
import json
import unittest

from tools.extra_texts import pseudo_clementine_translation as pipeline


class TranslationWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.request = pipeline.prepare("pseudo_clementine_peter_to_james", ["1"], "gpt-5-6-sol-atlas")
        self.output = {"passages": [{"reference": "1", "text": "TEST FIXTURE ONLY", "lexical_decisions": [{"source_quote": "Πέτρος", "chosen": "Peter", "rationale": "Personal name"}], "source_issues": []}]}

    def response(self, output=None, finish="stop"):
        return {"model": "test-only-model", "choices": [{"finish_reason": finish, "message": {"content": json.dumps(output or self.output)}}]}

    def test_draft_is_only_a_hash_bound_candidate(self):
        record = pipeline.validate_response(self.request, self.response())
        self.assertEqual(record["publication_status"], "candidate_only")
        self.assertEqual(record["model"], "test-only-model")
        self.assertEqual(record["output_hash"], pipeline.digest(self.output))

    def test_elided_quotations_require_literal_spans_in_order(self):
        self.assertTrue(pipeline.quotation_matches("α ... γ", "α β γ"))
        self.assertFalse(pipeline.quotation_matches("γ ... α", "α β γ"))
        self.assertFalse(pipeline.quotation_matches("α ... δ", "α β γ"))
        self.assertFalse(pipeline.quotation_matches("α ... ", "α β γ"))

    def test_rejects_truncation_wrong_references_and_fabricated_quotes(self):
        with self.assertRaisesRegex(ValueError, "finish normally"):
            pipeline.validate_response(self.request, self.response(finish="length"))
        wrong = copy.deepcopy(self.output)
        wrong["passages"][0]["reference"] = "2"
        with self.assertRaisesRegex(ValueError, "coverage"):
            pipeline.validate_response(self.request, self.response(wrong))
        wrong = copy.deepcopy(self.output)
        wrong["passages"][0]["lexical_decisions"][0]["source_quote"] = "invented Greek"
        with self.assertRaisesRegex(ValueError, "quotation"):
            pipeline.validate_response(self.request, self.response(wrong))

    def test_rejects_tampered_request_and_nonexistent_source(self):
        wrong = copy.deepcopy(self.request)
        wrong["references"] = ["2"]
        with self.assertRaisesRegex(ValueError, "context changed"):
            pipeline.validate_response(wrong, self.response())
        with self.assertRaisesRegex(ValueError, "Missing"):
            pipeline.prepare("pseudo_clementine_homilies", ["20.1"], "model")

    def test_separate_review_binds_current_english_and_source(self):
        draft = pipeline.validate_response(self.request, self.response())
        request = pipeline.prepare(draft["work"], ["1"], "gpt-6-1-sol-review", draft)
        review = {"passages": [{"reference": "1", "verdict": "accept", "checks": {k: True for k in pipeline.CHECKS}, "findings": []}]}
        result = pipeline.validate_response(request, self.response(review))
        self.assertEqual(result["draft_output_hash"], draft["output_hash"])
        review["passages"][0]["checks"]["complete_coverage"] = False
        with self.assertRaisesRegex(ValueError, "contradicts"):
            pipeline.validate_response(request, self.response(review))
        draft["output"]["passages"][0]["text"] = "Changed after generation"
        with self.assertRaisesRegex(ValueError, "Draft text changed"):
            pipeline.prepare(draft["work"], ["1"], "review-model", draft)

    def test_review_standard_preserves_disclosed_ambiguity_without_waiving_actual_defects(self):
        request = pipeline.prepare("pseudo_clementine_peter_to_james", ["1"], "test")
        standard = request["context"]["ambiguity_review_standard"]
        self.assertIn("DOCTRINE.md", standard)
        self.assertIn("unique or uncontested interpretation is not required", standard)
        self.assertIn("main rendering must itself be defensible", standard)
        self.assertIn("unreadable", standard)
        self.assertIn("invented restoration", standard)

    def test_unresolved_source_issue_cannot_be_certified_away(self):
        output = copy.deepcopy(self.output)
        output["passages"][0]["source_issues"] = [{"source_quote": "Πέτρος", "issue": "TEST SOURCE ISSUE", "blocks_publication": True}]
        draft = pipeline.validate_response(self.request, self.response(output))
        request = pipeline.prepare(draft["work"], ["1"], "review-model", draft)
        review = {"passages": [{"reference": "1", "verdict": "accept", "checks": {k: True for k in pipeline.CHECKS}, "findings": []}]}
        with self.assertRaisesRegex(ValueError, "separate source evidence"):
            pipeline.validate_response(request, self.response(review))

    def test_citation_fix_is_disclosed_and_cannot_change_english(self):
        output = copy.deepcopy(self.output)
        output["passages"][0]["lexical_decisions"][0]["source_quote"] = "Πετρος"
        fix = [{"reference": "1", "index": 0, "field": "source_quote", "before": "Πετρος", "after": "Πέτρος", "reason": "Use exact supplied source spelling"}]
        record = pipeline.validate_response(self.request, self.response(output), fix)
        self.assertEqual(record["output"]["passages"][0]["text"], output["passages"][0]["text"])
        self.assertNotEqual(record["raw_model_output_hash"], record["output_hash"])
        fix[0]["field"] = "text"
        with self.assertRaisesRegex(ValueError, "Only documented"):
            pipeline.validate_response(self.request, self.response(output), fix)


if __name__ == "__main__":
    unittest.main()
