"""Enoch inventory and secondary-witness fail-closed regression checks."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from tools.enoch import audit_pob_source_coverage as coverage
from tools.enoch import dillmann_verse_parser as dillmann
from tools.enoch import multi_witness, verse_parser
from tools.enoch import build_restoration_queue as queue


class EnochCompletenessTest(unittest.TestCase):
    def test_declared_primary_inventories(self):
        for chapter, expected in coverage.EXPECTED_VERSES.items():
            rows, _ = verse_parser.parse_chapter(chapter)
            self.assertEqual([row.verse for row in rows], list(range(1, expected + 1)), chapter)
        self.assertEqual(coverage.EXPECTED_VERSES[20], 7)
        self.assertEqual(coverage.EXPECTED_VERSES[45], 6)
        self.assertEqual(coverage.EXPECTED_VERSES[97], 10)

    def test_chapter_45_sixth_unit_is_now_present_after_bounded_review(self):
        row = coverage.audit([45])["chapters"][0]
        self.assertEqual(row["expected_count_basis"], "declared_primary_inventory")
        self.assertEqual(row["primary_source_verses"], 6)
        self.assertEqual(row["missing_verse_numbers"], [])
        # Raw OCR alignment is only a diagnostic; exact accepted payloads
        # and the full printed count are tested by the batch02 application.
        self.assertFalse(row["translation_verified_by_this_audit"])

    def test_chapter_97_tenth_unit_is_declared_but_not_complete(self):
        row = coverage.audit([97])["chapters"][0]
        self.assertEqual(row["expected_count_basis"], "declared_primary_inventory")
        self.assertEqual(row["primary_source_verses"], 10)
        self.assertEqual(row["missing_verse_numbers"], [10])
        self.assertFalse(row["inventory_complete"])

    def test_missing_empty_and_primary_gaps_fail_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / '003').mkdir()
            row = verse_parser.EnochVerseRow(3, 1, 'source።', '', 'fixture')
            with patch.object(coverage.verse_parser, 'parse_chapter', return_value=([row], [])):
                self.assertEqual(coverage.audit([3], root)['missing_verse_total'], 1)
                (root / '003/001.yaml').write_text(yaml.safe_dump({'source': {'text': 'source።'}, 'translation': {'text': ''}}))
                report = coverage.audit([3], root)
                self.assertEqual(report['chapters'][0]['empty_translation_verse_numbers'], [1])
                self.assertEqual(report['incomplete_chapters'], [3])
            with patch.object(coverage.verse_parser, 'parse_chapter', return_value=([], [])):
                report = coverage.audit([3], root)
                self.assertEqual(report['chapters'][0]['primary_missing_verse_numbers'], [1])
                self.assertFalse(report['chapters'][0]['inventory_complete'])

    def test_broken_dillmann_rows_are_not_verse_witnesses(self):
        rows, warnings = dillmann.parse_chapter(7)
        self.assertEqual(rows, [])
        self.assertTrue(any('Unverified Dillmann verse alignment' in warning for warning in warnings))
        self.assertIsNone(multi_witness.load_verse(7, 2).geez_dillmann)

    def test_chapter_thirteen_scan_cleanup_is_bounded_and_raw_ocr_preserved(self):
        raw = verse_parser.chapter_path(13).read_bytes()
        rows, warnings = verse_parser.parse_chapter(13)
        texts = {row.verse: row.text for row in rows}
        self.assertIn('*ትዝካረ፡', texts[4])
        self.assertTrue(texts[6].endswith('ወአስተ።'))
        self.assertIn('ዐረብ፡ አርሞን፡', texts[7])
        self.assertIn('በ*አበልስያኤል፡', texts[9])
        self.assertEqual(raw, verse_parser.chapter_path(13).read_bytes())
        self.assertTrue(any('scan OCR cleanup' in warning for warning in warnings))
        with patch.dict(verse_parser.SCAN_OCR_CLEANUPS, {(13,4): (('missing baseline','bad'),)}):
            with self.assertRaises(ValueError):
                verse_parser.parse_chapter(13)

    def test_missing_dillmann_header_is_not_full_file_witness(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'ch07.txt').write_text('ክፍል ፡ ፰ ፡፡ ሀ፡፡ ፪ ለ፡፡')
            with patch.object(dillmann, 'DILLMANN_ROOT', root):
                rows, warnings = dillmann.parse_chapter(7)
            self.assertEqual(rows, [])
            self.assertTrue(any('Unverified' in warning for warning in warnings))

    def test_source_queue_is_read_only_and_hash_bound(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / '003').mkdir()
            row = verse_parser.EnochVerseRow(3, 1, 'source።', '', 'fixture')
            with patch.object(coverage.verse_parser, 'parse_chapter', return_value=([row], [])):
                result = queue.build([3], root)
            self.assertEqual(list((root / '003').iterdir()), [])
            self.assertEqual(result['tasks'][0]['kind'], 'absent_verse')
            self.assertTrue(result['tasks'][0]['source_text_sha256'])


if __name__ == '__main__':
    unittest.main()
