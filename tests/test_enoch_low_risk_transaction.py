"""Focused pre-publication checks for the bounded Enoch correction."""

import unittest

from tools.textual_restoration import enoch_low_risk_transaction as release


class EnochLowRiskTransactionTest(unittest.TestCase):
    def test_frozen_source_and_review_package(self):
        candidates = release.verify_structure()
        self.assertEqual(set(candidates), {'005-009', '017-007', '017-008'})

    def test_only_chapters_five_and_seventeen_change_in_local_export(self):
        delta = release.verify_export_delta()
        self.assertEqual(delta['changed_chapters'], [5, 17])
        self.assertEqual(delta['chapter_17_verses'], 8)


if __name__ == '__main__':
    unittest.main()
