import unittest
import json
import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch
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

    def test_relative_output_directory_is_resolved_before_changing_cwd(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            package = root / 'package'
            package.mkdir()
            (package / 'review-input.json').write_text('[{"reference":"1 Enoch 29:2"}]')
            (package / 'review-prompt.txt').write_text('Bounded review')
            (package / 'review.schema.json').write_text('{}')
            scan = root / 'scan.png'
            scan.write_bytes(b'scan bytes')
            output = Path('results')

            def fake_run(args, **kwargs):
                if args[:3] == ['codex', 'login', 'status']:
                    return subprocess.CompletedProcess(args, 0, 'Logged in using ChatGPT', '')
                result_file = Path(args[args.index('-o') + 1])
                self.assertTrue(result_file.is_absolute())
                result_file.write_text(json.dumps({'chapter_complete': True, 'reviews': [
                    {'reference': '1 Enoch 29:2', 'verdict': 'accept'}]}))
                return subprocess.CompletedProcess(args, 0, 'model: test-model', '')

            old_cwd = Path.cwd()
            try:
                os.chdir(root)
                with patch.object(review.subprocess, 'run', side_effect=fake_run):
                    self.assertTrue(review.run(package, [scan], output)['chapter_complete'])
            finally:
                os.chdir(old_cwd)
            self.assertTrue((root / output / 'review.json').exists())
            self.assertTrue((root / output / 'provenance.json').exists())

if __name__=='__main__':unittest.main()
