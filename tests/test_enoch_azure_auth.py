import json,sys,unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/enoch'))
import draft_enoch as d
class AzureAuth(unittest.TestCase):
 def env(self):return {'AZURE_OPENAI_ENDPOINT':'https://example.openai.azure.com','AZURE_OPENAI_DEPLOYMENT_ID':'test','AZURE_OPENAI_AUTH_MODE':'azure-cli','AZURE_OPENAI_OMIT_TEMPERATURE':'1'}
 def test_aad_no_key_no_temperature_no_token_logging(self):
  captured=[]
  def stop(req,**kw):captured.append(req);raise d.urllib.error.URLError('test stop')
  with patch.dict(d.os.environ,self.env(),clear=True),patch.object(d.subprocess,'run',return_value=SimpleNamespace(returncode=0,stdout='test-token')),patch.object(d.urllib.request,'urlopen',side_effect=stop):
   with self.assertRaisesRegex(RuntimeError,'test stop'):d.call_azure_openai(system='s',user='u',model='m',temperature=0.2)
  request=captured[0];self.assertEqual(request.get_header('Authorization'),'Bearer test-token');self.assertIsNone(request.get_header('Api-key'))
  self.assertNotIn('temperature',json.loads(request.data))
 def test_untrusted_destination_rejected_before_token_acquisition(self):
  for endpoint in ['http://example.openai.azure.com','https://example.com','https://example.openai.azure.com/evil','https://user@example.openai.azure.com','https://example.openai.azure.com?x=1']:
   env=self.env();env['AZURE_OPENAI_ENDPOINT']=endpoint
   with patch.dict(d.os.environ,env,clear=True),patch.object(d.subprocess,'run') as run:
    with self.assertRaises(RuntimeError):d.call_azure_openai(system='s',user='u',model='m',temperature=0.2)
    run.assert_not_called()
 def test_failed_cli_does_not_expose_output(self):
  with patch.dict(d.os.environ,self.env(),clear=True),patch.object(d.subprocess,'run',return_value=SimpleNamespace(returncode=1,stdout='SECRET',stderr='SECRET')):
   with self.assertRaisesRegex(RuntimeError,'token acquisition failed') as cm:d.call_azure_openai(system='s',user='u',model='m',temperature=0.2)
   self.assertNotIn('SECRET',str(cm.exception))
if __name__=='__main__':unittest.main()
