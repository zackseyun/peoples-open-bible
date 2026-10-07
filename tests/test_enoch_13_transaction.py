"""Source, exact review content and complete chapter-13 export contract."""
import json
import unittest
from tools.textual_restoration import enoch_13_transaction as release

class EnochThirteenTransactionTest(unittest.TestCase):
    def test_scoped_source_and_review_binding(self):
        if (release.PACKAGE / 'application.json').exists():
            self.assertEqual(release.verify_applied()['refs'], [f'13:{n}' for n in range(4,11)])
        else:
            self.assertEqual(set(release.verify_structure()), {f'013-{n:03d}' for n in range(4,11)})
        review=json.loads((release.PACKAGE/'final-source-review.json').read_text())
        self.assertEqual(len(review['reviewed_content_sha256']),7)
        self.assertTrue(all(r['verdict']=='accept' for r in review['reviews'].values()))

    def test_full_chapter_thirteen_has_ten_ordered_verses(self):
        if (release.PACKAGE / 'application.json').exists():
            book=release.exporter.export_extra_canonical_book('ENO')
            chapter=next(c for c in book['chapters'] if c['chapter']==13)
            self.assertEqual([v['verse'] for v in chapter['verses']],list(range(1,11)))
        else:
            delta=release.verify_export_delta()
            self.assertEqual(delta['changed_chapters'],[13])
            self.assertEqual(delta['chapter_13_verses'],10)

if __name__=='__main__':unittest.main()
