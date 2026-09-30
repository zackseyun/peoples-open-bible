"""Focused pre/post checks for the bounded 1 Enoch 12 source completion."""

import unittest

from tools.textual_restoration import enoch_12_transaction as release


class EnochTwelveTransactionTest(unittest.TestCase):
    def test_frozen_source_and_review_package(self):
        if (release.PACKAGE / 'application.json').exists():
            self.assertEqual(release.verify_applied()['refs'],
                             [f'12:{verse}' for verse in range(1, 7)])
        else:
            self.assertEqual(set(release.verify_structure()),
                             {f'012-{verse:03d}' for verse in range(1, 7)})

    def test_chapter_twelve_export_has_six_ordered_verses(self):
        if (release.PACKAGE / 'application.json').exists():
            book = release.exporter.export_extra_canonical_book('ENO')
            chapter = next(row for row in book['chapters'] if row['chapter'] == 12)
            self.assertEqual([verse['verse'] for verse in chapter['verses']],
                             list(range(1, 7)))
        else:
            delta = release.verify_export_delta()
            self.assertEqual(delta['changed_chapters'], [12])
            self.assertEqual(delta['chapter_12_verses'], 6)


if __name__ == '__main__':
    unittest.main()
