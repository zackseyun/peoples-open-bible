"""Focused pre-publication checks for the bounded Enoch correction."""

import unittest
import yaml

from tools.textual_restoration import enoch_low_risk_transaction as release


class EnochLowRiskTransactionTest(unittest.TestCase):
    def test_frozen_source_and_review_package(self):
        if (release.PACKAGE / 'application.json').exists():
            applied = release.verify_applied()
            self.assertEqual(applied['refs'], ['5:9', '17:7', '17:8'])
        else:
            candidates = release.verify_structure()
            self.assertEqual(set(candidates), {'005-009', '017-007', '017-008'})

    def test_only_chapters_five_and_seventeen_change_in_local_export(self):
        if (release.PACKAGE / 'application.json').exists():
            book = release.exporter.export_extra_canonical_book('ENO')
            chapter_17 = next(ch for ch in book['chapters'] if ch['chapter'] == 17)
            self.assertEqual([v['verse'] for v in chapter_17['verses']], list(range(1, 9)))
            chapter_5 = next(ch for ch in book['chapters'] if ch['chapter'] == 5)
            expected = yaml.safe_load((release.PACKAGE / '005-009.candidate.yaml').read_text())
            self.assertEqual(chapter_5['verses'][8]['text'], expected['translation']['text'])
        else:
            delta = release.verify_export_delta()
            self.assertEqual(delta['changed_chapters'], [5, 17])
            self.assertEqual(delta['chapter_17_verses'], 8)


if __name__ == '__main__':
    unittest.main()
