"""Nahum 1:5 checks after the November 2026 meaning-first pass.

The reviewed test froze every other Nahum verse to prove its change was narrow. The
meaning-first pass later revised those verses on purpose, so this successor
reruns the frozen checks against the text from just before the pass
(tests/meaning_pass_baseline.py). The reviewed test file is unchanged; every
other check is inherited as is.
"""
from tests import test_nahum1_5_earth_reader_application as original
from tests.meaning_pass_baseline import pre_meaning_pass_view


class NahumEarthApplicationTestsMeaningPassSuccessor(original.NahumEarthApplicationTests):
    def test_exact_applied_bytes_complete_current_export_and_non_targets(self):
        with pre_meaning_pass_view():
            super().test_exact_applied_bytes_complete_current_export_and_non_targets()


if __name__ == '__main__':
    import unittest
    unittest.main()
