"""Joel 2:23 checks after the November 2026 meaning-first pass.

The reviewed test froze every other Joel verse to prove its change was narrow. The
meaning-first pass later revised those verses on purpose, so this successor
reruns the frozen checks against the text from just before the pass
(tests/meaning_pass_baseline.py). The reviewed test file is unchanged; every
other check is inherited as is.
"""
from tests import test_joel2_23_reader_application as original
from tests.meaning_pass_baseline import pre_meaning_pass_view


class JoelReaderApplicationTestsMeaningPassSuccessor(original.JoelReaderApplicationTests):
    def test_current_application_state_and_other_files(self):
        with pre_meaning_pass_view():
            super().test_current_application_state_and_other_files()


if __name__ == '__main__':
    import unittest
    unittest.main()
