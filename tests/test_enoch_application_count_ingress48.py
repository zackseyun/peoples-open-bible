"""A fixed old ten-unit count is not a fresh one-row language certificate."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools.enoch import bounded_application as t,application_count_ingress48 as c
class ApplicationCountIngress48Test(unittest.TestCase):
 def manifest(self):return {'references':['1 Enoch 48:7'],c.KEY:[copy.deepcopy(c.DECLARATION)]}
 def test_exact_already_paired_count_only_and_no_reader_release_change(self):
  d=c.validate(self.manifest())[48];self.assertEqual(d['units'],list(range(1,11)));self.assertTrue(d['independent_count_confirmation']);self.assertFalse(d['wording_approval']);self.assertFalse(d['reader_release_policy_changed'])
  from tools.enoch.audit_pob_source_coverage import EXPECTED_VERSES
  self.assertNotIn(48,EXPECTED_VERSES)
 def test_historical_ten_unit_inputs_and_decisions_remain_bound_including_hold7(self):
  p=t.APPLICATIONS/c.NAME;m=t.load_manifest(p);self.assertEqual(t.sha((p/'manifest.json').read_bytes()),c.MANIFEST_SHA);self.assertEqual(m['files'][c.COUNT_ARTIFACT],c.COUNT_SHA)
  ref=next(r for r in m['references']if t.parse_ref(r)[0]==48)
  for b in m['review_bindings'][ref]:
   inputs=json.loads((p/b['input']).read_text());decisions=t.review_entries(json.loads((p/b['review']).read_text()))
   for rows in(inputs,decisions):self.assertEqual(sorted(t.parse_ref(r['reference'])[1]for r in rows if t.parse_ref(r['reference'])[0]==48),c.UNITS)
   self.assertEqual(next(r['verdict']for r in decisions if r['reference']=='1 Enoch 48:7'),'hold')
  self.assertNotIn('1 Enoch 48:7',m['references'])
 def test_wrong_scope_address_and_overlapping_declarations_fail(self):
  for mode in('missingref','excess','chapter','legacy','profile'):
   with self.subTest(mode=mode):
    m=self.manifest()
    if mode=='missingref':m['references']=['1 Enoch 18:8']
    elif mode=='excess':m['references']=['1 Enoch 48:11']
    elif mode=='chapter':m['chapter_inventories']=[{'chapter':48}]
    elif mode=='legacy':m['source_only_count_inventories']=[{'chapter':48}]
    else:m['existing_paired_count_ingress']=[{'chapter':48}]
    with self.assertRaises(ValueError):c.validate(m)
 def test_no_generic_profile_path_flags_or_count_substitution(self):
  changes=[{'chapter':49},{'chapter':'48'},{'package':'../other'},{'package_manifest_sha256':'0'*64},{'count_artifact':'../other.json'},{'count_artifact_sha256':'0'*64},{'units':list(range(1,10))},{'units':[True,*range(2,11)]},{'independent_count_confirmation':False},{'wording_approval':True},{'reader_release_policy_changed':True},{'wording_approval':0},{'full_chapter_language_approved':True}]
  for change in changes:
   with self.subTest(change=change):
    m=self.manifest();m[c.KEY][0].update(change)
    with self.assertRaises(ValueError):c.validate(m)
 def test_duplicate_or_nonlist_declaration_rejected_empty_is_no_certificate(self):
  self.assertEqual(c.validate({'references':['1 Enoch 48:7']}),{})
  for value in(None,{},[copy.deepcopy(c.DECLARATION)]*2):
   with self.subTest(value=value),self.assertRaises(ValueError):c.validate({'references':['1 Enoch 48:7'],c.KEY:value})
 def test_changed_historical_count_file_rejected_even_if_only_whitespace(self):
  actual=t.artifact;p=t.APPLICATIONS/c.NAME
  with tempfile.TemporaryDirectory()as directory:
   changed=Path(directory)/'count.json';changed.write_bytes((p/c.COUNT_ARTIFACT).read_bytes()+b'\n')
   with patch.object(t,'artifact',side_effect=lambda root,rel:changed if Path(root)==p and rel==c.COUNT_ARTIFACT else actual(root,rel)):
    with self.assertRaises(ValueError):c.validate(self.manifest())
 def test_missing_or_rebound_original_receipt_is_not_an_installed_count(self):
  receipt=t.APPLICATIONS/c.NAME/'application.json';read=Path.read_text
  for change in({'status':'not_applied'},{'manifest_sha256':'0'*64}):
   with self.subTest(change=change):
    data=json.loads(read(receipt));data.update(change)
    with patch.object(Path,'read_text',autospec=True,side_effect=lambda path,*args,**kwargs:json.dumps(data)if path==receipt else read(path,*args,**kwargs)):
     with self.assertRaises(ValueError):c.validate(self.manifest())
