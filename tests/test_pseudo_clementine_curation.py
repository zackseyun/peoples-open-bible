import copy,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools.extra_texts import pseudo_clementine_curation as c,pseudo_clementine_pages as p

class CurationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.source=self.root/'source';self.source.mkdir()
  self.rows=[{'reference':'3.12','source_text':'ἀρχὴ καὶ προφητειῶν τέλος','source_text_sha256':p.sha('ἀρχὴ καὶ προφητειῶν τέλος'.encode())}]
  self.item={'reference':'3.12','kind':'primary_print_variant','authorization':'Explicit user permission','source_license':'public_domain_print','before':'καὶ προφητειῶν','after':'μὴ προφητεύων','translation_requirement':'Disclose former print and editorial variant','evidence':[{'verified_excerpt':'μὴ προφητεύων'}]}
  self.rootpatch=patch.object(p,'ROOT',self.root);self.sourcepatch=patch.object(p,'SOURCE',self.source);self.rootpatch.start();self.sourcepatch.start()
 def tearDown(self):self.sourcepatch.stop();self.rootpatch.stop();self.tmp.cleanup()
 def apply(self,item=None):
  (self.source/'source-curations.json').write_text(json.dumps([self.item if item is None else item]));return c.apply_curations(self.rows)
 def test_corrected_source_retains_original_and_requires_fresh_hash(self):
  with patch.object(c,'verified_reading',return_value='μὴ προφητεύων'):result=self.apply()
  self.assertEqual(result[0]['source_text'],'ἀρχὴ μὴ προφητεύων τέλος');self.assertEqual(result[0]['source_curations'][0]['before'],'καὶ προφητειῶν');self.assertNotEqual(result[0]['source_text_sha256'],self.rows[0]['source_text_sha256']);self.assertNotIn('source_curations',self.rows[0])
 def test_no_curation_does_not_change_source(self):self.assertEqual(c.apply_curations(self.rows),self.rows)
 def test_licensed_xml_and_missing_authorization_are_not_imported(self):
  for key,value in [('source_license','CC-BY-SA-4.0'),('authorization',''),('kind','force_accept')]:
   item=copy.deepcopy(self.item);item[key]=value
   with self.assertRaises(ValueError):self.apply(item)
 def test_unverified_replacement_and_stale_target_fail(self):
  with patch.object(c,'verified_reading',return_value='different'):
   with self.assertRaisesRegex(ValueError,'not the verified'):self.apply()
  item=copy.deepcopy(self.item);item['before']='not in Greek'
  with patch.object(c,'verified_reading',return_value=item['after']):
   with self.assertRaisesRegex(ValueError,'exact former'):self.apply(item)
 def test_raw_model_receipt_and_readback_are_required(self):
  response={'model':'gpt-6.1-sol-test','choices':[{'finish_reason':'stop','message':{'content':json.dumps({'text':'μὴ προφητεύων'})}}]};request={'initial_transcription_was_not_supplied':True,'request_sha256':'hash'};receipt={'status':'success','request_sha256':'hash','response':response};e={'fields':['text'],'verified_excerpt':'μὴ προφητεύων'}
  for key,data in [('request',request),('response',response),('receipt',receipt)]:
   path=self.root/(key+'.json');p.save(path,data);e[key]=path.name;e[key+'_sha256']=p.sha(path.read_bytes())
  self.assertEqual(c.verified_reading(e),'μὴ προφητεύων')
  e['verified_excerpt']='fabricated'
  with self.assertRaisesRegex(ValueError,'absent'):c.verified_reading(e)
  e['verified_excerpt']='μὴ προφητεύων';(self.root/'response.json').write_text('{}')
  with self.assertRaisesRegex(ValueError,'evidence changed'):c.verified_reading(e)
