"""Historical provenance is imported explicitly, not chapter-complete labels."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.enoch import historical_evidence as historical
from tools.enoch.full_repair_progress import build

class HistoricalEvidenceTest(unittest.TestCase):
    def test_exact29_older_units_are_imported_without_fresh_review_claim(self):
        from tools.enoch import bounded_application as current_transaction
        if (current_transaction.APPLICATIONS/'enoch_full_repair_batch11_20261022/application.json').is_file():
            # Exact original assertions remain below and run at pinned49ed;
            # separate batch11 assertions validate actual current replacements.
            from tools.enoch.replay_29_97_pre_successor import replay
            result = replay('historical29')
            self.assertEqual((result['tests_run'], result['skipped'], result['expected_failures']), (1, 0, 0))
            self.assertFalse(result['current_corpus_validated'])
            return
        result=historical.load_current()
        self.assertEqual(len(result),29)
        self.assertEqual({c for c,v in result},{15,16,29,83})
        for row in result.values():
            self.assertFalse(row['fresh_review'])
            self.assertFalse(row['full_chapter_count_certified_by_import'])
        report=build()
        self.assertGreaterEqual(report['current_units_with_imported_review_evidence'],113)
        self.assertEqual(report['evidence_inventory_warnings'],[])
        self.assertFalse(report['completion_proven'])
        # Separate fresh paired source counts, not old chapter_complete labels.
        for c in [15,16,29,83]:
            self.assertIn(c,report['chapters_with_complete_imported_selected_edition_review'])
        self.assertNotIn((13,1),result)
        self.assertNotIn((14,1),result)

    def test_separate_fresh_counts_are_bound_and_not_wording_reviews(self):
        result=historical.load_count_inventories()
        self.assertEqual({c:len(v['units']) for c,v in result.items()},{15:12,16:4,29:2,83:11})
        data=json.loads(historical.INDEX.read_text())
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory).resolve();index=root/'index.json'
            for name in data['paired_count_review']['files']:
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes((historical.transaction.ROOT/name).read_bytes())
            index.write_text(json.dumps(data))
            with patch.object(historical.transaction,'ROOT',root):
                self.assertEqual(len(historical.load_count_inventories(index)),4)
                (root/data['paired_count_review']['review']).write_text('{}')
                with self.assertRaisesRegex(ValueError,'Historical count artifact hash differs'):
                    historical.load_count_inventories(index)

    def fixture(self,directory):
        root=Path(directory).resolve();data=json.loads(historical.INDEX.read_text())
        for pack in data['packages']:
            for name in pack['files']:
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes((historical.transaction.ROOT/name).read_bytes())
            for unit in pack['units']:
                c,v=historical.transaction.parse_ref(unit['reference'])
                relative=f'translation/extra_canonical/1_enoch/{c:03d}/{v:03d}.yaml'
                target=root/relative;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes((historical.transaction.ROOT/relative).read_bytes())
        index=root/'index.json';index.write_text(json.dumps(data))
        return root,data,index

    def test_current_canonical_drift_is_not_approved_by_old_review(self):
        from tools.enoch import bounded_application as current_transaction
        if (current_transaction.APPLICATIONS/'enoch_full_repair_batch11_20261022/application.json').is_file():
            # Exact original assertions remain below and run at pinned49ed;
            # separate batch11 assertions validate actual current replacements.
            from tools.enoch.replay_29_97_pre_successor import replay
            result = replay('historical-drift')
            self.assertEqual((result['tests_run'], result['skipped'], result['expected_failures']), (1, 0, 0))
            self.assertFalse(result['current_corpus_validated'])
            return
        with tempfile.TemporaryDirectory() as directory:
            root,data,index=self.fixture(directory)
            target=root/'translation/extra_canonical/1_enoch/015/001.yaml'
            target.write_bytes(target.read_bytes()+b'\n# later metadata change\n')
            with patch.object(historical.transaction,'ROOT',root),patch.object(historical.transaction,'TRANSLATION',root/'translation/extra_canonical/1_enoch'):
                result=historical.load_current(index)
            self.assertEqual(len(result),28)
            self.assertNotIn((15,1),result)

    def test_changed_pinned_review_artifact_rejects_import(self):
        with tempfile.TemporaryDirectory() as directory:
            root,data,index=self.fixture(directory)
            (root/data['packages'][0]['units'][0]['review']).write_text('{}')
            with patch.object(historical.transaction,'ROOT',root),patch.object(historical.transaction,'TRANSLATION',root/'translation/extra_canonical/1_enoch'):
                with self.assertRaisesRegex(ValueError,'Historical artifact hash differs'):
                    historical.load_current(index)

    def test_laundering_wrong_input_path_cannot_replace_review_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            root,data,index=self.fixture(directory)
            unit=data['packages'][0]['units'][0];unit['input']=unit['review']
            index.write_text(json.dumps(data))
            with patch.object(historical.transaction,'ROOT',root),patch.object(historical.transaction,'TRANSLATION',root/'translation/extra_canonical/1_enoch'):
                with self.assertRaisesRegex(ValueError,'Historical exact input hash differs'):
                    historical.load_current(index)

    def test_duplicate_and_unknown_index_are_rejected(self):
        data=json.loads(historical.INDEX.read_text())
        with tempfile.TemporaryDirectory() as directory:
            index=Path(directory)/'index.json';data['packages'][0]['units'].append(copy.deepcopy(data['packages'][0]['units'][0]))
            index.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'Duplicate historical unit'):
                historical.load_current(index)
            data['kind']='claimed-complete';index.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'Historical index source/kind differs'):
                historical.load_current(index)

if __name__=='__main__':unittest.main()
