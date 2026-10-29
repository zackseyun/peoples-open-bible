"""Serialization-only checks prevent re-review churn; never approve language."""
import copy,hashlib,json,tempfile,unittest
from pathlib import Path
from tools.enoch import review_input_preflight as p
BASE=[{'id':'1EN.54.1','reference':'1 Enoch 54:1','book':'1 Enoch','source':{'edition':'charles-1906-enoch','language':'Geez','text':'ወነጸርኩ።','pages':[135],'confidence':'low','note':'Test-only selected-scope serialization, not source evidence.','transcription_uncertainties':[{'type':'test_selected_scope','status':'test_not_language_approval'}]},'translation':{'text':'Test serialization.[a]','philosophy':'optimal-equivalence','footnotes':[{'marker':'a','text':'Test only.','reason':'lexical_alternative'}]}}]
class ReviewInputPreflightTest(unittest.TestCase):
 def test_valid_shape_is_only_serialization_not_language_acceptance(self):self.assertEqual(p.findings(BASE),[])
 def test_empty_and_map_inputs_fail(self):
  self.assertTrue(p.findings([]));self.assertTrue(p.findings({}))
 def test_empty_or_blank_source_cannot_be_integration_ready(self):
  for text in('', ' \n\t'):
   rows=copy.deepcopy(BASE);rows[0]['source']['text']=text
   self.assertTrue(any('source.text_empty_or_blank'in e for e in p.findings(rows)))
 def test_empty_or_blank_english_without_anchors_cannot_be_integration_ready(self):
  for text in('', ' \n\t'):
   rows=copy.deepcopy(BASE);rows[0]['source']['confidence']='medium';rows[0]['translation'].update(text=text,footnotes=[])
   self.assertTrue(any('translation.text_empty_or_blank'in e for e in p.findings(rows)))
 def test_new_hold_receipt_can_be_serialized_but_is_not_an_acceptance(self):
  with tempfile.TemporaryDirectory()as directory:
   i,r,v=self.receipt(Path(directory),'hold');self.assertEqual(p.receipt_findings(i,r,v),[])
 def receipt(self,d,decision='accept'):
  i,r,v=[d/n for n in('input.json','review.json','pv.json')];i.write_text(json.dumps(BASE));r.write_text(json.dumps({'reviewer_id':'test-only','role':'author','reviews':[{'reference':'1 Enoch 54:1','verdict':decision}]}));sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();v.write_text(json.dumps({'reviewer_id':'test-only','role':'author','input_sha256':sha(i),'review_sha256':sha(r),'source_pdf_sha256':'505f248c667cebd5136991d7c570841a0a3ed9396d5b28b85bf07f4a3957053e','scan_image_sha256':{'test-only-not-real-photo':'0'*64}}));return i,r,v
 def test_receipt_byte_drift_fails(self):
  with tempfile.TemporaryDirectory()as directory:
   i,r,v=self.receipt(Path(directory));r.write_text(r.read_text()+'\n');self.assertTrue(p.receipt_findings(i,r,v))
 def test_direct_decision_is_not_silently_reinterpreted(self):
  with tempfile.TemporaryDirectory()as directory:
   i,r,v=self.receipt(Path(directory));d=json.loads(r.read_text());d.pop('reviews');d.update(decision='APPROVE',approved=True);r.write_text(json.dumps(d));self.assertTrue(p.receipt_findings(i,r,v))
 def test_nonflat_image_alias_and_identity_drift_fail(self):
  for mode in('alias','identity','pdf'):
   with self.subTest(mode=mode),tempfile.TemporaryDirectory()as directory:
    i,r,v=self.receipt(Path(directory));d=json.loads(v.read_text())
    if mode=='alias':d['actualscan_image_sha256']=d.pop('scan_image_sha256')
    elif mode=='identity':d['reviewer_id']='other'
    else:d['source_pdf_sha256']='0'*64
    v.write_text(json.dumps(d));self.assertTrue(p.receipt_findings(i,r,v))
def mutation_case(change):
 def run(self):
  rows=copy.deepcopy(BASE);change(rows);self.assertTrue(p.findings(rows))
 return run
CASES={'malformed_source':lambda x:x[0].update(source=None),'malformed_translation':lambda x:x[0].update(translation=[]),'nonscalar_source_text':lambda x:x[0]['source'].update(text=55),'nonscalar_note_marker':lambda x:x[0]['translation']['footnotes'][0].update(marker={}), 'missing_philosophy':lambda x:x[0]['translation'].pop('philosophy'),'missing_marker':lambda x:x[0]['translation']['footnotes'][0].pop('marker'),'invalid_note_reason':lambda x:x[0]['translation']['footnotes'][0].update(reason='literal_meaning'),'wrong_edition':lambda x:x[0]['source'].update(edition='other'),'unsupported_high_confidence_label':lambda x:x[0]['source'].update(confidence='high'),'missing_low_scope':lambda x:x[0]['source'].update(transcription_uncertainties=[]),'missing_low_source_note':lambda x:x[0]['source'].pop('note'),'wrong_identity':lambda x:x[0].update(id='1EN.54.2'),'unbound_note':lambda x:x[0]['translation']['footnotes'][0].update(marker='z'),'replacement_fidel':lambda x:x[0]['source'].update(text='\ufffd'),'unknown_fidel_square':lambda x:x[0]['source'].update(text='□'),'duplicate_unit':lambda x:x.append(copy.deepcopy(x[0])),'duplicate_marker':lambda x:x[0]['translation']['footnotes'].append(copy.deepcopy(x[0]['translation']['footnotes'][0]))}
for name,change in CASES.items():setattr(ReviewInputPreflightTest,'test_'+name,mutation_case(change))
