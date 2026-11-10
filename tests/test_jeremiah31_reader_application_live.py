"""Jeremiah 31 checks after the November 2026 meaning-first pass.

The reviewed test froze its evidence verses, such as Hebrews 8:9 to prove its change was narrow. The
meaning-first pass later revised those verses on purpose, so this successor
reruns the frozen checks against the text from just before the pass
(tests/meaning_pass_baseline.py). The reviewed test file is unchanged; every
other check is inherited as is.
"""
from tests import test_jeremiah31_reader_application as original
from tests.meaning_pass_baseline import pre_meaning_pass_view


class Jeremiah31ReaderTestsMeaningPassSuccessor(original.Jeremiah31ReaderTests):
    def test_evidence_and_implementation_pins(self):
        with pre_meaning_pass_view():
            super().test_evidence_and_implementation_pins()


if __name__ == '__main__':
    import unittest
    unittest.main()
