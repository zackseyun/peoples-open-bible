"""Habakkuk 1:17 checks after the November 2026 meaning-first pass.

The reviewed test froze every other Habakkuk verse to prove its change was narrow. The
meaning-first pass later revised those verses on purpose, so this successor
reruns the frozen checks against the text from just before the pass
(tests/meaning_pass_baseline.py). The reviewed test file is unchanged; every
other check is inherited as is.
"""
from tests import test_habakkuk1_17_reader_disclosure as original
from tests.meaning_pass_baseline import pre_meaning_pass_view


class Habakkuk117ReaderDisclosureTestsMeaningPassSuccessor(original.Habakkuk117ReaderDisclosureTests):
    def test_applied_current_complete_export_and_receipt(self):
        with pre_meaning_pass_view():
            super().test_applied_current_complete_export_and_receipt()


if __name__ == '__main__':
    import unittest
    unittest.main()
