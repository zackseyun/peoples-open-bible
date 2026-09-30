"""Focused pre/post checks for the bounded 1 Enoch 6 source completion."""

import unittest

from tools.textual_restoration import enoch_6_transaction as release


class EnochSixTransactionTest(unittest.TestCase):
    def test_frozen_source_and_review_package(self):
        if (release.PACKAGE / 'application.json').exists():
            applied = release.verify_applied()
            self.assertEqual(applied['refs'], ['6:6', '6:7', '6:8'])
        else:
            candidates = release.verify_structure()
            self.assertEqual(set(candidates), {'006-006', '006-007', '006-008'})

    def test_chapter_six_export_has_eight_ordered_verses(self):
        if (release.PACKAGE / 'application.json').exists():
            book = release.exporter.export_extra_canonical_book('ENO')
            chapter = next(row for row in book['chapters'] if row['chapter'] == 6)
            self.assertEqual([verse['verse'] for verse in chapter['verses']], list(range(1, 9)))
        else:
            delta = release.verify_export_delta()
            self.assertEqual(delta['changed_chapters'], [6])
            self.assertEqual(delta['chapter_6_verses'], 8)


if __name__ == '__main__':
    unittest.main()
