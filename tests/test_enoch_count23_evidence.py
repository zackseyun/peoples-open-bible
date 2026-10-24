"""Count all four actual printed units without approving corrupt23:4."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from tools.enoch import bounded_application as t, count23_evidence as counts


class Chapter23CountEvidenceTest(unittest.TestCase):
    def test_two_distinct_actual_observations_not_four_language_votes(self):
        result=counts.load();self.assertEqual(set(result),{23})
        self.assertEqual(result[23]['units'],[1,2,3,4])
        self.assertTrue(result[23]['independent_count_confirmation'])
        self.assertFalse(result[23]['wording_approval'])
        self.assertFalse(result[23]['reader_release_policy_changed'])
        d=json.loads((t.ROOT/counts.INDEX).read_text());prefix=t.ROOT/d['artifact_prefix']
        a=json.loads((prefix/'root-source-first-ledger.json').read_text())
        b=json.loads((prefix/'other-source-first-ledger.json').read_text())
        self.assertNotEqual(a['reviewer_id'],b['reviewer_id'])
        self.assertEqual([r['pages']for r in a['observed_units']],[[98]]*4)
        self.assertEqual(b['observations']['all_chapter_pages'],[98])
        old=json.loads((prefix/'other-author-review.json').read_text())
        self.assertEqual([(r['reference'],r['verdict'])for r in old['reviews']],[('1 Enoch 23:4','hold')])

    def test_structural_progress_does_not_complete_chapter23_or_book(self):
        from tools.enoch.structural_counts import load_all_inventories
        self.assertEqual(load_all_inventories()[23]['units'],[1,2,3,4])
        from tools.enoch.full_repair_progress import build
        report=build();self.assertEqual(report['evidence_inventory_warnings'],[])
        self.assertNotIn(23,report['chapters_with_complete_imported_selected_edition_review'])
        self.assertFalse(report['completion_proven'])
        self.assertFalse(report['artwork_publication_approval'])
        from tools.enoch.selected_edition_sources import registry_data
        self.assertNotIn('23',registry_data()['chapters'])

    def test_loading_count_observations_does_not_change_any_canonical_bytes(self):
        before=t.corpus_hashes();counts.load();after=t.corpus_hashes()
        self.assertEqual(before,after);self.assertEqual(len(after),962)

    def test_index_or_original_hold_receipt_drift_is_rejected(self):
        d=json.loads((t.ROOT/counts.INDEX).read_text())
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory)
            for name in(counts.INDEX,*d['files']):
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(t.ROOT/name,p)
            target=root/d['artifact_prefix']/'other-author-review.json';target.write_bytes(target.read_bytes()+b'\n')
            with patch.object(t,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'original count artifact differs'):counts.load()
            index=root/counts.INDEX;index.write_bytes(index.read_bytes()+b'\n')
            with patch.object(t,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'fixed count index differs'):counts.load()

    def test_source_and_exposure_boundaries_are_explicit(self):
        d=json.loads((t.ROOT/counts.INDEX).read_text());prefix=t.ROOT/d['artifact_prefix']
        comparison=json.loads((prefix/'paired-count-comparison.json').read_text())
        self.assertTrue(comparison['all_photograph_bytes_rechecked'])
        self.assertFalse(comparison['source_English_semantic_acceptance'])
        self.assertTrue(comparison['whole23_4_hold_unchanged'])
        self.assertIn('not before its count freeze',comparison['source_first_exposure'])
        self.assertIn('not a fresh shared-input language review',d['scope'])
        workflow=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn("python -m unittest discover -s tests -p 'test_enoch_count23_evidence.py'",workflow)
