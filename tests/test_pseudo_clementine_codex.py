import copy
import unittest

from tools.extra_texts import pseudo_clementine_translation as tr
from tools.extra_texts.pseudo_clementine_codex import validate_output


class CodexGenerationTests(unittest.TestCase):
    def setUp(self):
        self.rows = [{"reference":"6.1", "source_text":"λόγος.... ἀλήθεια"}]
        self.packet = {"kind":"codex_subagent_translation_request", "publication_status":"candidate_only_not_reviewed",
            "references":["6.1"], "passages":self.rows, "source_hash":tr.digest(self.rows)}
        self.output = {"passages":[{"reference":"6.1", "text":"Word.... truth", "lexical_decisions":[],
            "source_issues":[{"source_quote":"λόγος....", "issue":"A printed gap, not reconstructed.", "blocks_publication":False}]}]}

    def test_honest_generation_is_validated_without_an_invented_provider_response(self):
        validate_output(self.packet,self.output,self.rows)
        self.assertNotIn('choices',self.output)
        self.assertNotIn('review',self.output)

    def test_source_change_and_invented_quote_fail(self):
        rows = copy.deepcopy(self.rows);rows[0]['source_text'] += ' changed'
        with self.assertRaisesRegex(ValueError,'source changed'):
            validate_output(self.packet,self.output,rows)
        out = copy.deepcopy(self.output);out['passages'][0]['source_issues'][0]['source_quote']='invented'
        with self.assertRaisesRegex(ValueError,'quotation'):
            validate_output(self.packet,out,self.rows)

    def test_missing_section_hidden_gap_and_self_approval_fail(self):
        for out in [{'passages':[]},dict(self.output,review='approved')]:
            with self.assertRaises(ValueError):validate_output(self.packet,out,self.rows)
        out = copy.deepcopy(self.output);out['passages'][0]['text']='Word restored truth'
        with self.assertRaisesRegex(ValueError,'explicit and unfilled'):
            validate_output(self.packet,out,self.rows)
