"""Reuse validation only inside one source read, never across calls."""
import unittest
from unittest.mock import patch
from pathlib import Path
from tools.enoch import selected_edition_sources as source

class SourceReadScopeTest(unittest.TestCase):
 def test_same_package_is_verified_once_per_read_not_per_unit(self):
  registry={'units':{'17:1':'same','17:2':'same','17:4':'other'}}
  def row(p,m,c,v):return {'verse':v}
  with patch.object(source,'registry_data',return_value=registry),patch.object(source,'package_evidence',side_effect=lambda n:(Path(n),{}))as verify,patch.object(source,'source_row',side_effect=row):
   self.assertEqual([r['verse']for r in source.load_unit_overrides(17)],[1,2,4])
   self.assertEqual([x.args[0]for x in verify.call_args_list],['same','other'])
   source.load_unit_overrides(17)
   self.assertEqual([x.args[0]for x in verify.call_args_list],['same','other','same','other'])

 def test_next_read_revalidates_and_rejects_drift(self):
  with patch.object(source,'registry_data',return_value={'units':{'17:1':'same','17:2':'same'}}),patch.object(source,'package_evidence',side_effect=[(Path('same'),{}),ValueError('artifact drift')])as verify,patch.object(source,'source_row',side_effect=lambda p,m,c,v:{'verse':v}):
   self.assertEqual(len(source.load_unit_overrides(17)),2)
   with self.assertRaisesRegex(ValueError,'artifact drift'):source.load_unit_overrides(17)
   self.assertEqual(verify.call_count,2)

if __name__=='__main__':unittest.main()
