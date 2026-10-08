"""Source, exact review content and complete chapter-14 export contract."""
import json
import unittest
from tools.textual_restoration import enoch_14_transaction as release

class EnochFourteenTransactionTest(unittest.TestCase):
    def test_scoped_source_and_review_binding(self):
        if (release.PACKAGE / 'application.json').exists():
            self.assertEqual(release.verify_applied()['refs'], [f'14:{n}' for n in range(19,26)])
        else:
            self.assertEqual(set(release.verify_structure()), {f'014-{n:03d}' for n in range(19,26)})
        review=json.loads((release.PACKAGE/'final-source-review.json').read_text())
        self.assertEqual(len(review['reviewed_content_sha256']),7)
        self.assertTrue(all(r['verdict']=='accept' for r in review['reviews'].values()))

    def test_full_chapter_fourteen_has_twenty_five_ordered_verses(self):
        if (release.PACKAGE / 'application.json').exists():
            book=release.exporter.export_extra_canonical_book('ENO')
            chapter=next(c for c in book['chapters'] if c['chapter']==14)
            self.assertEqual([v['verse'] for v in chapter['verses']],list(range(1,26)))
        else:
            delta=release.verify_export_delta()
            self.assertEqual(delta['changed_chapters'],[14])
            self.assertEqual(delta['chapter_14_verses'],25)

if __name__=='__main__':unittest.main()
