import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.extra_texts import pseudo_clementine_pages as pages
from tools.extra_texts import pseudo_clementine_recover as recovery


class RecoveryTests(unittest.TestCase):
    def test_only_unknown_terminal_failures_get_exact_diagnostic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / "pages-blind/068"
            directory.mkdir(parents=True)
            cache = root / "cache"
            cache.mkdir()
            body = {"model": "approved-model", "messages": [{"content": "unchanged"}]}
            digest = pages.sha(pages.canonical(body))
            pages.save(cache / (digest + ".request.json"), body)
            file = directory / "review-1.response.attempt1.json"
            for kind, expected in (("authorization", 0), ("content_filter", 0), ("terminal_cli_error", 1)):
                failure = {"status": "error", "error_kind": kind, "request_sha256": digest}
                pages.save(file, failure)
                with patch.object(pages, "SOURCE", root), patch.object(pages, "invoke", return_value={"choices": [{"finish_reason": "stop"}]}) as invoke:
                    recovery.recover(68, cache)
                    self.assertEqual(invoke.call_count, expected)
                    if expected:
                        self.assertEqual(invoke.call_args.args[0], body)
                self.assertEqual(json.loads(file.read_text()), failure)

    def test_missing_exact_request_blocks_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            directory = root / "pages-blind/068"
            directory.mkdir(parents=True)
            pages.save(directory / "review-1.response.attempt1.json",
                       {"status": "error", "error_kind": "terminal_cli_error", "request_sha256": "missing"})
            with patch.object(pages, "SOURCE", root), patch.object(pages, "invoke") as invoke:
                with self.assertRaisesRegex(ValueError, "missing"):
                    recovery.recover(68, root)
                invoke.assert_not_called()
