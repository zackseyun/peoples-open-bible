from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.extra_texts import azure_cli_bounded_http as bounded
from tools.extra_texts import pseudo_clementine_pages as pages


class HttpDeadlineTests(unittest.TestCase):
    def test_only_missing_deadlines_are_bounded_without_changing_request(self):
        calls = []
        class Session:
            def send(self, request, **kwargs):
                calls.append((request,kwargs)); return 'response'
        bounded.install_deadlines(Session)
        self.assertEqual(Session().send('unchanged-request'), 'response')
        self.assertEqual(calls[-1],('unchanged-request',{'timeout':(30,600)}))
        Session().send('unchanged-request',timeout=45)
        self.assertEqual(calls[-1][1]['timeout'],45)

    def test_identified_cli_runtime_keeps_normal_cli_arguments(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp);runtime = root/'bin/python';runtime.parent.mkdir();runtime.write_text('')
            launcher = root/'az';launcher.write_text(f'#!/bin/bash\n{runtime} -Im azure.cli "$@"\n')
            args = ['rest','--method','post','--body','@request.json']
            with patch.object(pages.shutil,'which',return_value=str(launcher)):
                command,metadata = pages.cli_http_command(args)
                self.assertEqual(command[0],str(runtime));self.assertEqual(command[2:],args)
                self.assertEqual(metadata['http_read_timeout_seconds'],600)

    def test_unknown_launcher_does_not_claim_deadline_or_change_identity(self):
        with patch.object(pages.shutil,'which',return_value=None):
            command,metadata = pages.cli_http_command(['rest'])
        self.assertEqual(command,['az','rest'])
        self.assertFalse(metadata['http_deadline_installed'])


if __name__ == '__main__':
    unittest.main()
