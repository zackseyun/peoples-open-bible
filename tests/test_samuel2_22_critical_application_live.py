"""1 Samuel 2:22 checks after the November 2026 meaning-first pass.

The reviewed test froze every other 1 Samuel verse to prove its change was narrow. The
meaning-first pass later revised those verses on purpose, so this successor
reruns the frozen checks against the text from just before the pass
(tests/meaning_pass_baseline.py). The reviewed test file is unchanged; every
other check is inherited as is.
"""
from tests import test_samuel2_22_critical_application as original
from tests.meaning_pass_baseline import pre_meaning_pass_view


class Samuel222CriticalApplicationTestsMeaningPassSuccessor(original.Samuel222CriticalApplicationTests):
    def test_all_811_raw_book_paths_match_baseline_except_exact_target(self):
        with pre_meaning_pass_view():
            super().test_all_811_raw_book_paths_match_baseline_except_exact_target()

    def test_actual_full_export_only_changes_2_22_and_preserves_notes_not_deployment_proof(self):
        with pre_meaning_pass_view():
            super().test_actual_full_export_only_changes_2_22_and_preserves_notes_not_deployment_proof()


if __name__ == '__main__':
    import unittest
    unittest.main()
