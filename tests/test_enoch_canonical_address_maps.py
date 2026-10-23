"""Seven actual printed units, eight reviewed POB addresses, no wording grant."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from tools.enoch import bounded_application as t,canonical_address_maps as maps
from tools.enoch import structural_counts,interleaved_structural_counts as raw,verse_parser, audit_pob_source_coverage as coverage
from tools.enoch.full_repair_progress import build as progress
from tools.enoch.audit_editorial_issues import build as audit


class Canonical6MappingTest(unittest.TestCase):
    def test_exact_mapping_preserves_print7_and_existing_addresses8(self):
        before=dict(coverage.EXPECTED_VERSES);proof=maps.load_chapter6()
        self.assertEqual(proof['selected_printed_units'],list(range(1,8)))
        self.assertEqual(proof['canonical_address_units'],list(range(1,9)))
        self.assertFalse(proof['wording_approval']);self.assertFalse(proof['reader_release_policy_changed'])
        self.assertEqual(coverage.EXPECTED_VERSES,before)
        self.assertEqual(before[6],8)

    def test_raw_count_only_hold_is_immutable_but_separate_map_resolves_addressing(self):
        count=raw.load(t.ROOT/'sources/enoch/coverage/count1-8-20261022/paired-count-index-v3.json')[6]
        current=structural_counts.load_all_inventories()[6]
        self.assertEqual(count['units'],current['units'])
        self.assertTrue(count['canonical_mapping_pending'])
        self.assertTrue(current['raw_canonical_mapping_pending'])
        self.assertFalse(current['canonical_mapping_pending'])
        self.assertEqual(current['canonical_address_units'],list(range(1,9)))
        self.assertFalse(current['canonical_mapping_resolution']['wording_approval'])

    def test_progress_keeps_print_count_distinct_and_requires_all_wording_evidence(self):
        d=progress();row=d['chapters'][5]
        self.assertEqual(row['expected_units'],list(range(1,9)))
        self.assertEqual(row['selected_printed_source_units'],list(range(1,8)))
        self.assertFalse(row['canonical_source_unit_mapping_pending'])
        self.assertEqual(row['count_basis'],'paired_printed_units_with_reviewed_canonical_segmentation')
        self.assertEqual(row['selected_edition_chapter_review_complete'],row['current_records']==row['expected_units']and row['current_units_with_imported_review_evidence']==row['expected_units'])
        self.assertEqual(d['evidence_inventory_warnings'],[])
        self.assertFalse(d['completion_proven'])

    def test_diagnostic_does_not_declare_eighth_address_spurious_or_approve_words(self):
        d=audit([6]);row=d['inventory']['chapters'][0]
        self.assertEqual(row['expected_verses'],8)
        self.assertEqual(d['printed_source_mapping_reviews'],[])
        self.assertFalse(any(f['kind']=='unexpected_verse_file'for r in d['issues']for f in r['findings']))
        self.assertFalse(d['publication_approved'])

    def test_no_current_canonical_body_read_or_echo_needed_for_mapping(self):
        before_bytes,before_text=Path.read_bytes,Path.read_text
        def deny(path):
            if path.is_relative_to(t.TRANSLATION):raise AssertionError('Current canonical read by mapping source')
        def rb(path,*a,**kw):deny(path);return before_bytes(path,*a,**kw)
        def rt(path,*a,**kw):deny(path);return before_text(path,*a,**kw)
        with patch.object(Path,'read_bytes',rb),patch.object(Path,'read_text',rt):
            self.assertEqual(maps.load_chapter6()['canonical_address_units'],list(range(1,9)))

    def test_raw_artifact_drift_rejected(self):
        d=json.loads((t.ROOT/maps.INDEX).read_text())
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory)
            for name in [maps.INDEX,*d['files']]:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(t.ROOT/name,p)
            p=root/d['review'];p.write_bytes(p.read_bytes()+b'\n')
            with patch.object(t,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'raw mapping artifact differs'):maps.load_chapter6()

    def test_count_promotion_or_count8_print_laundering_rejected(self):
        original=structural_counts.load_all_inventories();original[6]['canonical_mapping_pending']=True
        original[6]['units']=list(range(1,9))
        with self.assertRaisesRegex(ValueError,'unchanged printed-count certificate'):
            maps.apply_reviewed_maps(original)
        d=json.loads((t.ROOT/maps.INDEX).read_text())
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory);p=root/maps.INDEX;p.parent.mkdir(parents=True);d['wording_approval']=True;p.write_text(json.dumps(d))
            with patch.object(t,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'mapping index differs'):maps.load_chapter6()

    def test_parser_preserves_source_words_and_labels_editorial_not_missing_print(self):
        rows,warnings=verse_parser.parse_ocr_chapter(6)
        self.assertEqual([r.verse for r in rows],list(range(1,9)))
        self.assertEqual(rows[-1].marker_raw,'editorial boundary')
        self.assertTrue(any('POB editorial'in w and 'no printed numeral8'in w for w in warnings))
        self.assertFalse(any('Restored chapter 6'in w for w in warnings))
        label=maps.reviewed_boundary_label(6,8)
        self.assertIn('editorial',label);self.assertIn('unit7',label)
        self.assertNotEqual(label,'reviewed printed unit boundary')
        self.assertEqual(maps.reviewed_boundary_label(39,1),'reviewed printed unit boundary')
