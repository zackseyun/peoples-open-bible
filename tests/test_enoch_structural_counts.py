"""Paired counts must not become translation approval or reader-release policy."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.enoch import structural_counts as counts
from tools.enoch import audit_pob_source_coverage as coverage
from tools.enoch.full_repair_progress import build

class StructuralCountsTest(unittest.TestCase):
    def test_actual154_spans_include_eight_not_nine_in77(self):
        before=dict(coverage.EXPECTED_VERSES)
        data=counts.load_inventories()
        self.assertEqual({c:len(v['units']) for c,v in data.items()},
                         {72:37,73:8,74:17,75:9,76:14,77:8,78:17,79:6,80:8,81:10,82:20})
        self.assertEqual(sum(len(x['units']) for x in data.values()),154)
        self.assertEqual(coverage.EXPECTED_VERSES,before)
        index=json.loads(counts.INDEX.read_text())
        self.assertFalse(index['wording_approval'])
        self.assertFalse(index['reader_release_policy_changed'])
        report=build()
        self.assertEqual(report['chapters'][76]['expected_units'],list(range(1,9)))
        self.assertTrue(set(range(72,83))<=set(report['chapters_with_imported_paired_count_inventory']))
        self.assertFalse(report['completion_proven'])

    def test_diagnostic_audit_uses_actual_counts_without_mutating_release_counts(self):
        before=dict(coverage.EXPECTED_VERSES)
        result=coverage.audit([77],diagnostic_counts={77:8})
        row=result['chapters'][0]
        self.assertEqual(row['expected_verses'],8)
        self.assertEqual(row['missing_verse_numbers'],[8])
        self.assertEqual(row['expected_count_basis'],'separately_paired_structural_count')
        self.assertEqual(coverage.EXPECTED_VERSES,before)
        self.assertFalse(row['translation_verified_by_this_audit'])

    def fixture(self,directory):
        root=Path(directory).resolve();data=json.loads(counts.INDEX.read_text())
        for name in data['files']:
            target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((counts.transaction.ROOT/name).read_bytes())
        index=root/'index.json';index.write_text(json.dumps(data))
        return root,data,index

    def test_changed_count_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root,data,index=self.fixture(directory)
            (root/data['input']).write_text('{}')
            with patch.object(counts.transaction,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'Structural count artifact hash differs'):
                    counts.load_inventories(index)

    def test_unknown_scope_or_wording_promotion_is_rejected(self):
        data=json.loads(counts.INDEX.read_text())
        with tempfile.TemporaryDirectory() as directory:
            index=Path(directory)/'index.json';data['wording_approval']=True;index.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'Structural count index scope differs'):
                counts.load_inventories(index)

    def test_current_wording_changes_do_not_rewrite_or_revoke_actual_page_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            root,data,index=self.fixture(directory)
            # No canonical source/English bodies are needed by this adapter.
            with patch.object(counts.transaction,'ROOT',root):
                self.assertEqual(len(counts.load_inventories(index)),11)

if __name__=='__main__':unittest.main()
