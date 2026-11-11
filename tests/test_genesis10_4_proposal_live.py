"""Genesis 10:4 checks after the November 2026 meaning-first pass.

The reviewed test froze the proposal's context verses to prove its change was narrow. The
meaning-first pass later revised those verses on purpose, so this successor
reruns the frozen checks against the text from just before the pass
(tests/meaning_pass_baseline.py). The reviewed test file is unchanged; every
other check is inherited as is.
"""
from tests import test_genesis10_4_proposal as original
from tests.meaning_pass_baseline import pre_meaning_pass_view


class Genesis104ProposalTestsMeaningPassSuccessor(original.Genesis104ProposalTests):
    def test_frozen_inputs_and_context(self):
        with pre_meaning_pass_view():
            super().test_frozen_inputs_and_context()


if __name__ == '__main__':
    import unittest
    unittest.main()
