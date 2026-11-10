"""Isaiah 19:18 checks after the November 2026 meaning-first pass.

The reviewed test froze every other Isaiah verse to prove its change was narrow. The
meaning-first pass later revised those verses on purpose, so this successor
reruns the frozen checks against the text from just before the pass
(tests/meaning_pass_baseline.py). The reviewed test file is unchanged; every
other check is inherited as is.
"""
from tests import test_isaiah19_18_reader_note as original
from tests.meaning_pass_baseline import pre_meaning_pass_view


class Isaiah19ReaderNoteTestsMeaningPassSuccessor(original.Isaiah19ReaderNoteTests):
    def test_live_target_and_full_export_are_baseline_or_candidate(self):
        with pre_meaning_pass_view():
            super().test_live_target_and_full_export_are_baseline_or_candidate()


if __name__ == '__main__':
    import unittest
    unittest.main()
