"""Historical97 authenticity never implies new whole97 approval."""
import copy,json,shutil,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from tools.enoch import legacy97_evidence as l
from tools.enoch import replay_29_97_pre_successor as gate

class Legacy97EvidenceTest(unittest.TestCase):
 def test_original_four_units_one_accepted_pass_not_two_diagnostics(self):
  result=l.verify_historical(l.t.APPLICATIONS/l.NAME)
  self.assertEqual(result['references'],l.REFS)
  self.assertEqual(result['historical_accepted_individual_review_passes'],1)
  self.assertEqual(result['diagnostic_whole_chapter_reviews'],2)
  self.assertFalse(result['chapter_publication_approval'])
  self.assertFalse(result['full_book_verified'])

 def test_original_raw_review_receipt_or_module_drift_rejected(self):
  index=json.loads((l.t.ROOT/l.INDEX_REL).read_text())
  for suffix in ('application.json','individual_1_3_5_8/review/review.json',l.VERIFIER):
   with self.subTest(suffix=suffix),tempfile.TemporaryDirectory()as directory:
    root=Path(directory);paths=[l.INDEX_REL,l.VERIFIER,*index['files']]
    for name in paths:
     p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((l.t.ROOT/name).read_bytes())
    name=l.VERIFIER if suffix==l.VERIFIER else next(n for n in index['files']if n.endswith(suffix))
    (root/name).write_bytes((root/name).read_bytes()+b'\n ')
    with patch.multiple(l.t,ROOT=root,APPLICATIONS=root/'sources/textual_restoration/applications'):
     with self.assertRaisesRegex(ValueError,'historical artifact differs|verifier differs'):
      l.verify_historical(l.t.APPLICATIONS/l.NAME)

 def test_unreviewed_current_drift_cannot_inherit_historical_acceptance(self):
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);(root/'097').mkdir()
   for v in l.VERSES:(root/f'097/{v:03d}.yaml').write_bytes((l.t.APPLICATIONS/l.NAME/f'097-{v:03d}.candidate.yaml').read_bytes())
   (root/'097/005.yaml').write_bytes(b'unreviewed drift')
   with patch.object(l.t,'TRANSLATION',root),patch.object(l.Path,'glob',return_value=[]):
    with self.assertRaisesRegex(ValueError,'No unique installed paired legacy97 successor'):
     l.verify_current(l.t.APPLICATIONS/l.NAME)

 def test_partial_or_incomplete_successor_is_rejected_before_history(self):
  for data in [ {'supersedes_legacy97':{}}, {'supersedes_legacy97':dict.fromkeys(l.REFS,{}),'references':l.REFS,'chapter_inventories':[]} ]:
   with self.subTest(data=data),self.assertRaisesRegex(ValueError,'all four|complete ten'):
    l.validate_declared_successor(Path('/not-a-package'),data)

 def test_complete_successor_cannot_rebind_a_different_receipt(self):
  p=l.t.APPLICATIONS/'enoch_full_repair_batch11_20261022'
  if not (p/'manifest.json').exists():
   # Construct the same full scope from the fixed original descriptors.
   m={'references':[f'1 Enoch 97:{v}'for v in range(1,11)],'chapter_inventories':[{'chapter':97,'units':list(range(1,11))}],'supersedes_legacy97':{r:l.descriptor(l.t.APPLICATIONS/l.NAME,r)for r in l.REFS}}
  else:m=json.loads((p/'manifest.json').read_text())
  m['supersedes_legacy97'][l.REFS[0]]['receipt_sha256']='0'*64
  with self.assertRaisesRegex(ValueError,'receipt/scope/preimage differs'):
   l.validate_declared_successor(p,m)

 def test_present_corrupt_primary_is_not_ignored_by_historical_verifier(self):
  from tools.textual_restoration import enoch_97_partial_transaction as old
  with tempfile.TemporaryDirectory()as directory:
   bad=Path(directory)/'bad.pdf';bad.write_bytes(b'wrong edition')
   with patch.object(old,'PRIMARY_PDF',bad),self.assertRaisesRegex(ValueError,'Primary PDF changed'):
    l.verify_historical(l.t.APPLICATIONS/l.NAME)

 def test_frozen_replay_rejects_unregistered_case_and_descriptor_reduction(self):
  with self.assertRaisesRegex(ValueError,'registered case'):gate.replay('97:any-other-test')
  data=json.loads(gate.DESCRIPTOR.read_text());data['cases'].pop(next(iter(data['cases'])))
  with patch.object(gate.Path,'read_text',return_value=json.dumps(data)),self.assertRaisesRegex(ValueError,'descriptor differs'):
   gate.replay(next(iter(gate.CASES)))

if __name__=='__main__':unittest.main()
