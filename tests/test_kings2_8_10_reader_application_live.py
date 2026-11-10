"""2 Kings 8:10 checks after the November 2026 meaning-first pass.

The reviewed test froze every other 2 Kings verse to prove its change was narrow. The
meaning-first pass later revised those verses on purpose, so this successor
reruns the frozen checks against the text from just before the pass
(tests/meaning_pass_baseline.py). The reviewed test file is unchanged; every
other check is inherited as is.
"""
from tests import test_kings2_8_10_reader_application as original
from tests.meaning_pass_baseline import pre_meaning_pass_view


class Kings2EightTenReaderApplicationTestsMeaningPassSuccessor(original.Kings2EightTenReaderApplicationTests):
    def test_live_book_is_exact_baseline_or_candidate(self):
        with pre_meaning_pass_view():
            super().test_live_book_is_exact_baseline_or_candidate()


if __name__ == '__main__':
    import unittest
    unittest.main()
