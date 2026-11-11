"""Exodus 4:24-26 checks after the November 2026 meaning-first pass.

The reviewed test froze every other Exodus verse to prove its change was narrow. The
meaning-first pass later revised those verses on purpose, so this successor
reruns the frozen checks against the text from just before the pass
(tests/meaning_pass_baseline.py). The reviewed test file is unchanged; every
other check is inherited as is.
"""
from tests import test_exodus4_24_26_application as original
from tests.meaning_pass_baseline import pre_meaning_pass_view


class Exodus42426ApplicationTestsMeaningPassSuccessor(original.Exodus42426ApplicationTests):
    def test_actual_full_exodus_export_isolates_three_units_and_keeps_all_notes(self):
        with pre_meaning_pass_view():
            super().test_actual_full_exodus_export_isolates_three_units_and_keeps_all_notes()


if __name__ == '__main__':
    import unittest
    unittest.main()
