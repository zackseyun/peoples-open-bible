import unittest
from pathlib import Path
from tools.enoch import review_source_candidates as review

class CodexSourceReviewTest(unittest.TestCase):
    def test_supported_login_route_uses_read_only_ephemeral_cli(self):
        args=review.command(Path('/package'),[Path('/scan.png')],Path('/output.json'))
        self.assertEqual(args[:2],['codex','exec'])
        self.assertIn('--ephemeral',args)
        self.assertEqual(args[args.index('--sandbox')+1],'read-only')
        self.assertNotIn('--model',args)
        self.assertEqual(args[-1],'-')

    def test_bounded_result_rejects_omitted_extra_or_duplicate_references(self):
        for rows in [[],[{'reference':'wrong','verdict':'accept'}],
                     [{'reference':'1 Enoch 13:4','verdict':'accept'}]*2]:
            with self.assertRaises(ValueError):
                review.validate_result({'reviews':rows,'chapter_complete':True},['1 Enoch 13:4'])

    def test_no_completion_claim_on_held_review(self):
        row={'reference':'1 Enoch 13:4','verdict':'hold'}
        result={'reviews':[row],'chapter_complete':True}
        review.validate_result(result,[row['reference']])
        self.assertFalse(review.editorially_accepted(result))
        review.validate_result({'reviews':[row],'chapter_complete':False},[row['reference']])

if __name__=='__main__':unittest.main()
