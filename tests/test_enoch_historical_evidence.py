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
        # A count certificate has NOT been imported by this provenance adapter.
        for c in [15,16,29,83]:
            self.assertNotIn(c,report['chapters_with_complete_imported_selected_edition_review'])
        self.assertNotIn((13,1),result)
        self.assertNotIn((14,1),result)

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
