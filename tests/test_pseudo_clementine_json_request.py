import unittest
from pathlib import Path
from unittest.mock import patch
from tools.extra_texts import pseudo_clementine_pages as p
class JsonRequestTests(unittest.TestCase):
 def test_missing_json_instruction_is_rejected_without_provider_call(self):
  body={'response_format':{'type':'json_object'},'messages':[{'content':[{'type':'text','text':'Return {text}.'},{'type':'image_url','image_url':{'url':'data:image/png;base64,json'}}]}]}
  with patch.object(p,'_invoke_attempts') as call:
   with self.assertRaisesRegex(ValueError,'explicit JSON instruction'):p.invoke(body,Path('/tmp/cache'),Path('/tmp/evidence'))
   call.assert_not_called()
 def test_json_instruction_in_actual_text_passes(self):
  response={'choices':[{'finish_reason':'stop'}]};body={'response_format':{'type':'json_object'},'messages':[{'content':[{'type':'text','text':'Return valid JSON.'}]}]}
  with patch.object(p,'_invoke_attempts',return_value=response) as call:self.assertEqual(p.invoke(body,Path('/tmp/cache'),Path('/tmp/evidence')),response)
  call.assert_called_once()
