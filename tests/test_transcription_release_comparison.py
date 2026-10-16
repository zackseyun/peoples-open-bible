import json
import re
import unittest

from tests.test_published_parallel_index import fixture
from tools.textual_restoration.compare_transcription_releases import compare, primary_snapshot


class TranscriptionReleaseTests(unittest.TestCase):
    def test_new_date_and_parallel_text_are_not_primary_changes(self):
        old = fixture().replace(b'2026-10-06', b'2026-05-21')
        new = fixture().replace(b'parallel-only', b'different-parallel')
        result = compare(old, new)
        self.assertTrue(result['primary_layer_identical'])
        self.assertNotEqual(result['old']['html_sha256'], result['new']['html_sha256'])
        self.assertEqual(result['identical_primary_rows'], 1)
        self.assertNotIn('primary-only', json.dumps(result))
        self.assertNotIn('different-parallel', json.dumps(result))

    def test_letter_or_supplied_boundary_change_is_reported(self):
        old = fixture(primary='<span class="word" data-word-id="10">כ֯שמח[ת]</span>')
        for text in ['כ֯שמחת', 'כ֯שמח[ה]', 'כשמח[ת]']:
            new = fixture(primary=f'<span class="word" data-word-id="10">{text}</span>')
            with self.subTest(text=text):
                result = compare(old, new)
                self.assertEqual(result['changed_primary_row_ids'], ['c1-i10'])
                self.assertFalse(result['primary_layer_identical'])
                self.assertFalse(result['policy']['changed_markup_is_reading_change'])

    def test_presentation_change_remains_a_review_item(self):
        result = compare(fixture(), fixture().replace(b'class="word"', b'class="word no-details"', 1))
        self.assertEqual(result['changed_primary_row_ids'], ['c1-i10'])
        self.assertFalse(result['policy']['changed_markup_is_reading_change'])

    def test_alternative_reading_is_not_silently_excluded(self):
        old = fixture(primary='<span class="word" data-word-id="10">main</span>'
                      '<span class="alternative-reading level-1"><span class="word" data-word-id="10">alt</span></span>')
        new = old.replace(b'>alt<', b'>changed<')
        self.assertEqual(compare(old, new)['changed_primary_row_ids'], ['c1-i10'])

    def test_added_removed_and_reordered_rows(self):
        extra = b'<tr class="line-verse" id="c1-i20" data-name="2"><td class="line-text"><span class="word" data-word-id="20">second</span></td></tr>'
        one = fixture()
        two = one.replace(b'</tbody>', extra + b'</tbody>')
        reordered = one.replace(b'<tbody>', b'<tbody>' + extra)
        self.assertEqual(compare(one, two)['added_primary_row_ids'], ['c1-i20'])
        self.assertEqual(compare(two, one)['removed_primary_row_ids'], ['c1-i20'])
        result = compare(two, reordered)
        self.assertEqual(result['identical_primary_rows'], 2)
        self.assertEqual(result['changed_primary_row_ids'], [])
        self.assertFalse(result['common_row_order_unchanged'])
        self.assertFalse(result['primary_layer_identical'])

    def test_manuscript_identity_mismatch_fails(self):
        with self.assertRaisesRegex(ValueError, 'different manuscript'):
            compare(fixture(), fixture().replace(b'transcription_id_4', b'transcription_id_5'))

    def test_invalid_empty_duplicate_or_truncated_input_fails(self):
        duplicate = fixture().replace(b'</tbody>', re.search(rb'<tr class="line-verse".*?</tr>', fixture())[0] + b'</tbody>')
        empty = b'<html><body id="transcription_id_4"><time datetime="2026-10-06"></time></body></html>'
        for raw in [b'<html>access denied</html>', fixture()[:-7], duplicate, empty]:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    primary_snapshot(raw)

    def test_single_quoted_attributes_keep_exact_raw_bytes(self):
        raw = fixture().replace(b'id="c1-i10"', b"id='c1-i10'")
        self.assertTrue(compare(raw, raw)['primary_layer_identical'])
        self.assertEqual(compare(fixture(), raw)['changed_primary_row_ids'], ['c1-i10'])

    def test_tag_like_comments_and_attributes_cannot_hide_changes(self):
        for decoration in ['<!-- </tr> -->', '<!-- <tr id="bogus"> -->',
                           '<span title="</tr>"></span>']:
            old = fixture().replace(b'primary-only', (decoration + 'primary-only').encode())
            new = old.replace(b'primary-only', b'changed-primary')
            with self.subTest(decoration=decoration):
                self.assertEqual(compare(old, new)['changed_primary_row_ids'], ['c1-i10'])
                self.assertFalse(compare(old, new)['primary_layer_identical'])

    def test_repeated_word_id_across_distinct_rows_stays_held(self):
        extra = b'<tr class="line-verse" id="c1-i20" data-name="2"><td class="line-text"><span class="word" data-word-id="10">repeated-placement</span></td></tr>'
        raw = fixture().replace(b'</tbody>', extra + b'</tbody>')
        with self.assertRaisesRegex(ValueError, 'duplicate primary word ID'):
            compare(raw, raw)

    def test_unicode_and_newlines_preserve_raw_row_digest(self):
        from tools.textual_restoration.compare_transcription_releases import digest, sha
        raw = fixture(primary='<span class="word" data-word-id="10">כ֯שמח[ת]</span>')
        raw = raw.replace(b'<main>', 'ש\n<main>\n'.encode())
        row = raw[raw.index(b'<tr class="line-verse"'):raw.index(b'</tr>') + 5]
        self.assertEqual(primary_snapshot(raw)['ordered_primary_row_digest'],
                         digest([('c1-i10', sha(row))]))


if __name__ == '__main__':
    unittest.main()
