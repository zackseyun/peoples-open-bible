"""The live comparator must not hide fresh26 language notes behind old metadata."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from tools.enoch import bounded_application as t
from tools.enoch.delivery_candidates import ordered_packages


class DeliveryCandidateOrderTest(unittest.TestCase):
    def test_actual_metadata_boundary_and_latest26_language_successor(self):
        packages=ordered_packages();names=[p.name for p in packages]
        self.assertEqual(len(names),len(set(names)))
        metadata=names.index('enoch_26_metadata_v3_20261023')
        self.assertLess(names.index('enoch_full_repair_batch14_20261023'),metadata)
        self.assertLess(metadata,names.index('enoch_full_repair_batch15_20261023'))
        latest={}
        for p in packages:
            m=json.loads((p/'manifest.json').read_text())
            latest.update({ref:p for ref in m['references']})
        for v in(5,6):self.assertEqual(latest[f'1 Enoch 26:{v}'].name,'enoch_full_repair_batch22_20261024')

    def test_unapplied_late_proposal_is_excluded_and_corrupt_applied_receipt_rejected(self):
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory)/'applications';root.mkdir()
            for p in ordered_packages():shutil.copytree(p,root/p.name)
            late=root/'enoch_full_repair_batch999_20990101';late.mkdir();(late/'manifest.json').write_text('{}')
            with patch.object(t,'APPLICATIONS',root):self.assertNotIn(late,ordered_packages())
            p=root/'enoch_full_repair_batch22_20261024';r=json.loads((p/'application.json').read_text());r['manifest_sha256']='0'*64;(p/'application.json').write_text(json.dumps(r))
            with patch.object(t,'APPLICATIONS',root):
                with self.assertRaisesRegex(ValueError,'exact applied receipt'):ordered_packages()


if __name__=='__main__':unittest.main()
