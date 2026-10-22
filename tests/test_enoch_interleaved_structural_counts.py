"""Printed-unit counts do not silently redefine POBverse addresses."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.enoch import bounded_application as t,interleaved_structural_counts as counts
from tools.enoch import structural_counts,audit_pob_source_coverage as coverage
from tools.enoch.full_repair_progress import build
from tools.enoch.audit_editorial_issues import build as issues

class InterleavedCountTest(unittest.TestCase):
    def index(self,scope):return t.ROOT/f'sources/enoch/coverage/count{scope}-20261022/paired-count-index-v3.json'
    def fixture(self,root,scope):
        d=json.loads(self.index(scope).read_text())
        for name in d['files']:
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((t.ROOT/name).read_bytes())
        return d
    def write(self,root,d):
        def read(k):return json.loads((root/d[k]).read_text())
        def put(k,value):(root/d[k]).write_text(json.dumps(value))
        sha=lambda k:t.sha((root/d[k]).read_bytes())
        review,pv=read('review'),read('provenance');review['input_sha256']=sha('input')
        ownsha=sha('own_observation');review['own_observation_sha256']=ownsha
        put('review',review);pv['input_sha256']=sha('input');pv['review_sha256']=sha('review')
        pv['own_span_ledger_sha256' if 'own_span_ledger_sha256' in pv else 'own_photo_observation_sha256']=ownsha
        put('provenance',pv);d['files']={n:t.sha((root/n).read_bytes()) for n in d['files']}
        p=root/'index.json';p.write_text(json.dumps(d));return p
    def reject(self,scope,key,change,error):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);d=self.fixture(root,scope);p=root/d[key];value=json.loads(p.read_text());change(value);p.write_text(json.dumps(value));index=self.write(root,d)
            with self.assertRaisesRegex(ValueError,error):counts.load(index,root)

    def test_exact116units_keep_interleaved_spans_and_canonical6_mapping_hold(self):
        before=dict(coverage.EXPECTED_VERSES)
        result={**counts.load(self.index('1-8')),**counts.load(self.index('9-14'))}
        self.assertEqual(len(result),14);self.assertEqual(sum(len(v['units']) for v in result.values()),116)
        self.assertEqual(len(result[6]['units']),7);self.assertTrue(result[6]['canonical_mapping_pending'])
        self.assertTrue(all(not v['canonical_mapping_pending'] for c,v in result.items() if c!=6))
        self.assertEqual(coverage.EXPECTED_VERSES,before);self.assertEqual(before[6],8)
        first=json.loads((t.ROOT/json.loads(self.index('1-8').read_text())['input']).read_text())
        row=next(r for r in first['units'] if r['reference']=='1 Enoch 4:1');self.assertEqual(row['pdf_pages'],[44,46])

    def test_current_progress_distinguishes_printed7_from_canonical8_and_never_completes6(self):
        data=build();row=data['chapters'][5]
        self.assertEqual(row['selected_printed_source_units'],list(range(1,8)))
        self.assertEqual(row['expected_units'],list(range(1,9)))
        self.assertTrue(row['canonical_source_unit_mapping_pending'])
        self.assertFalse(row['selected_edition_chapter_review_complete'])
        self.assertIn(6,data['chapters_with_imported_paired_count_inventory'])
        self.assertFalse(data['completion_proven']);self.assertEqual(data['evidence_inventory_warnings'],[])

    def test_diagnostic_count_difference_does_not_declare_canonical8_spurious(self):
        result=issues([6]);row=result['inventory']['chapters'][0]
        self.assertEqual(row['expected_verses'],8)
        self.assertEqual(result['printed_source_mapping_reviews'],[6])
        findings=[f for r in result['issues'] for f in r['findings']]
        self.assertTrue(any(f['kind']=='printed_source_to_canonical_mapping_review' for f in findings))
        self.assertFalse(any(f['kind']=='unexpected_verse_file' for f in findings))
        self.assertFalse(result['publication_approved'])

    def test_changed_raw_photo_input_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);d=self.fixture(root,'1-8');p=root/d['input'];p.write_text(p.read_text()+' ')
            index=root/'index.json';index.write_text(json.dumps(d))
            with self.assertRaisesRegex(ValueError,'artifact hash'):counts.load(index,root)

    def test_rebound_different_independent_span_rejected(self):
        self.reject('1-8','review',lambda x:x['unit_reviews'][0].update(pdf_pages=[42]),'complete spans')

    def test_boolean_count_rejected(self):
        self.reject('1-8','input',lambda x:x['chapters'][0].update(observed_unit_count=True),'types differ')

    def test_direct_mapping_promotion_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);d=self.fixture(root,'1-8');d['canonical_mapping_pending_chapters']=[]
            with self.assertRaisesRegex(ValueError,'mapping limit'):counts.load(self.write(root,d),root)

    def test_source_to_reader_policy_promotion_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);d=self.fixture(root,'1-8');d['canonical_versification_changed']=True
            with self.assertRaisesRegex(ValueError,'approval scope'):counts.load(self.write(root,d),root)

    def test_own_observation_must_precede_comparison(self):
        self.reject('9-14','own_observation',lambda x:x.update(comparison_inventory_opened=True),'independent observation')

    def test_rebound_own_span_disagreement_rejected(self):
        self.reject('9-14','own_observation',lambda x:x['unit_spans'][0].update(pdf_pages=[58]),'unit/page span|complete spans')

    def test_wrong_photo_digest_even_if_outer_receipt_rebound_rejected(self):
        self.reject('9-14','own_observation',lambda x:x['scan_image_sha256'].update({next(iter(x['scan_image_sha256'])):'0'*64}),'independent observation')

    def test_two_counters_not_same_identity(self):
        self.reject('1-8','input',lambda x:x.update(reviewer_id='/root/enoch52_54_independent'),'identity/receipt')

    def test_no_canonical_bodies_needed_for_raw_count_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);d=self.fixture(root,'9-14');self.assertEqual(len(counts.load(self.write(root,d),root)),6)
            self.assertFalse((root/'translation').exists())

if __name__=='__main__':unittest.main()
