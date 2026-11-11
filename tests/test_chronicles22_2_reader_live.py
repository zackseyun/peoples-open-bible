"""2 Chronicles 22:2 checks after the November 2026 meaning-first pass.

The reviewed test froze every other 2 Chronicles verse to prove its change was narrow. The
meaning-first pass later revised those verses on purpose, so this successor
reruns the frozen checks against the text from just before the pass
(tests/meaning_pass_baseline.py). The reviewed test file is unchanged; every
other check is inherited as is.
"""
from tests import test_chronicles22_2_reader as original
from tests.meaning_pass_baseline import pre_meaning_pass_view


class ChroniclesAgeReaderTestsMeaningPassSuccessor(original.ChroniclesAgeReaderTests):
    def test_all_live_files_exact_baseline_or_candidate(self):
        with pre_meaning_pass_view():
            super().test_all_live_files_exact_baseline_or_candidate()


if __name__ == '__main__':
    import unittest
    unittest.main()
