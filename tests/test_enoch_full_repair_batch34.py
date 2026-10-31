"""Exact fresh44 pair and bounded successor chain; no old vote promotion."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t, batch34_evidence as b
from tools.enoch import legacy44_evidence as legacy, count41_44_evidence as counts
from tools.enoch import selected_edition_sources as sources, verse_parser
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader

P=t.APPLICATIONS/b.NAME
SHA='53d842f144cef8646a66ad64ac7b94d1b0f053773d66c79c12e841cfd99b83f9'
INPUT='a1149d13d2397c6f3d56e7a2c365d69c0bdd8457eb61e46104dc9b1d0f6d7e0c'
SOURCE='ወ*ካልእት፡ ርኢኩ፡ በእንተ፡ መብረቅ፡ እፎ፡ ይቀውሙ፡ እምከዋክብት፡ ወይከውን፡ መብረቅ፡ ወኢይክል፡ ኀዲገ፡ ምስሎሙ።'
ENGLISH='And I saw something else concerning lightning:[a] how they arise from the stars, and it becomes lightning and cannot leave their form.[b]'
def record():return yaml.load((t.TRANSLATION/'044/001.yaml').read_bytes(),Loader=t.LOADER)
def write_json(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

class Batch34Test(unittest.TestCase):
 def package_fixture(self,root):
  p=Path(root)/b.NAME;shutil.copytree(P,p);return p,json.loads((p/'manifest.json').read_text())
 def test_exact_one_change_full966_receipt_and_actual_git_preimage(self):
  self.assertEqual(t.sha((P/'manifest.json').read_bytes()),SHA)
  proof=b.verify_current();m=t.load_manifest(P);_,before=b.prior_postmap()
  self.assertEqual(m['canonical_baseline_sha256'],before);self.assertEqual(len(before),966)
  self.assertEqual({k for k,v in proof['current_postmap'].items()if before[k]!=v},{'044/001.yaml'})
  self.assertEqual(m['references'],[b.REF]);self.assertEqual(m['retirements'],[])
  self.assertEqual(m['source_baseline_git_commit'],'5a6633695bfcc3264f508974c104ad556892c036')
  self.assertEqual(before['044/001.yaml'],legacy.AFTER_SHA)
  t.verify_git_preimage(m,'044/001.yaml',legacy.AFTER_SHA)
  receipt=json.loads((P/'application.json').read_text())
  self.assertEqual(receipt['canonical_after_sha256'],t.corpus_hashes())
  self.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
  self.assertFalse(receipt['deployed_by_transaction'])
 def test_legacy_descriptor_preserves_parent_only_history(self):
  m=t.load_manifest(P);self.assertEqual(m['supersedes_legacy44'],legacy.declaration())
  self.assertEqual(m['supersedes'],{})
  proof=legacy.verify_historical();self.assertEqual(proof['historical_independent_review_passes_proven'],0)
  self.assertFalse(proof['graphic_publication_approved'])
  self.assertEqual(record()['review_history'][0]['sha256'],legacy.AFTER_SHA)
  self.assertFalse(record()['review_history'][0]['certifies_this_candidate'])
 def test_fresh_exact_pair_distinct_roles_hashes_and_actual_views(self):
  m=t.load_manifest(P);bindings=m['review_bindings'][b.REF]
  self.assertEqual(len(bindings),2);self.assertEqual(len({v['reviewer_id']for v in bindings}),2)
  rows=t.reviewed_rows(P,bindings,b.REF,m['files']);self.assertEqual(rows[0],rows[1])
  roles=[]
  review_hashes=[]
  for binding in bindings:
   self.assertEqual(t.sha((P/binding['input']).read_bytes()),INPUT)
   pv=json.loads((P/binding['provenance']).read_text());review=json.loads((P/binding['review']).read_text())
   self.assertEqual(pv['input_sha256'],INPUT);self.assertEqual(pv['review_sha256'],t.sha((P/binding['review']).read_bytes()))
   self.assertEqual(review['reviewer_id'],binding['reviewer_id']);self.assertEqual(pv['source_pdf_sha256'],t.PRIMARY_SHA)
   self.assertEqual(len(pv['scan_image_sha256']),28);roles.append(pv['role']);review_hashes.append(pv['review_sha256'])
   self.assertEqual(t.review_entries(review)[0]['verdict'],'accept')
  self.assertEqual(set(roles),{'corrective_author','independent_reviewer'})
  self.assertEqual(set(review_hashes),{'6e9e6f9b2d0abafe92a696eee007e4a572aa06b6074031d8ef8c11170d3131fb','33e700c82f6f8235bff9a9d35dd990a548a207426be7743080fab9b480a899c8'})
  self.assertEqual(record()['translation'],rows[0]['translation'])
 def test_source_english_two_explanations_and_low_critical_scope(self):
  d=record();self.assertEqual(d['source']['text'],SOURCE);self.assertEqual(d['translation']['text'],ENGLISH)
  self.assertEqual(d['source']['confidence'],'low');self.assertEqual(d['source']['pages'],[122,123])
  self.assertTrue(d['source']['transcription_uncertainties']);notes=d['translation']['footnotes']
  self.assertEqual([n['marker']for n in notes],['a','b'])
  self.assertIn('editorial star',notes[0]['text']);self.assertIn('plural',notes[1]['text'])
  self.assertIn('predicates are singular',notes[1]['text']);self.assertIn('not the preposition with',notes[1]['text'])
  self.assertIn('leave-infinitive',notes[1]['text']);self.assertIn('interpretively uncertain',notes[1]['text'])
  self.assertEqual(d['enoch_witnesses']['available_witnesses'][0]['text'],SOURCE)
  self.assertEqual(d['enoch_witnesses']['available_witnesses'][0]['confidence'],'low')
 def test_clean_metadata_and_no_inherited_publication_scope(self):
  d=record();self.assertEqual(d['status'],'draft')
  for key in ['lexical_decisions','theological_decisions','textual_comparison','previous_reviews']:self.assertNotIn(key,d)
  c=d['source_correction'];self.assertTrue(c['individual_unit_application_approved'])
  for key in ['selected_edition_chapter_reviewed','chapter_publication_approval','full_book_verified','human_specialist_certification','manuscript_witness_certification','graphic_publication_approved']:self.assertFalse(c[key])
 def test_source_ingress_accepted_input_not_canonical_echo_and_raw_retained(self):
  reg=sources.registry_data();self.assertEqual(reg['units']['44:1'],b.NAME);self.assertNotIn('44',reg['chapters'])
  row,_=verse_parser.load_verse(44,1);self.assertEqual(row.text,SOURCE);self.assertEqual(row.source_confidence,'low')
  self.assertIn(b.NAME,row.chapter_file);raw,_=verse_parser.parse_ocr_chapter(44)
  self.assertNotEqual(raw[0].text,SOURCE);self.assertIn('ምስሌሆሙ',raw[0].text)
  with patch.object(t,'TRANSLATION',Path('/nonexistent-canonical-reader-proof')):
   self.assertEqual(sources.load_unit_overrides(44)[0]['source']['text'],SOURCE)
  self.assertEqual(build_enoch_prompt(44,1).source_payload['text'],SOURCE)
 def test_fixed_structural_index_only_no_new_count_votes(self):
  m=t.load_manifest(P);self.assertEqual(m['chapter_inventories'],[])
  self.assertEqual(m['source_only_count_inventories'],[{'chapter':44,'units':[1],'artifact':'source-only-count-inventory.json','independent_count_confirmation':True}])
  inv=json.loads((P/'source-only-count-inventory.json').read_text());self.assertEqual(inv['new_count_votes'],0)
  self.assertFalse(inv['wording_approval']);self.assertFalse(inv['reader_release_policy_changed'])
  self.assertEqual(t.sha((P/'original-count41-44-index.json').read_bytes()),counts.INDEX_SHA)
  row=inv['chapters'][0];self.assertEqual(row['count_evidence_index'],counts.INDEX)
  self.assertEqual(row['count_evidence_index_sha256'],counts.INDEX_SHA);self.assertEqual(row['units'],[1]);self.assertEqual(row['pdf_pages'],[122,123])
 def test_reader_exact_notes_protocol_and_release44_unchanged(self):
  d=record();out=reader._export_record_verse(1,d)
  self.assertEqual(out['footnote_review'],reader.PROTOCOL);self.assertEqual(out['footnotes'],d['translation']['footnotes'])
  self.assertEqual(out['source_critical']['text'],SOURCE);self.assertEqual(out['source_critical']['confidence'],'low')
  self.assertEqual(reader._enoch_expected_verse_map()[44],[1])
  self.assertEqual(t.sha((t.ROOT/'tools/export_mobile_bible.py').read_bytes()),'2258f72485099fe1014152eeb29394324415940467c2edd9d9da0d48a4a113c3')
 def test_progress479_37_with_no_full_book_claim(self):
  from tools.enoch.full_repair_progress import build
  report=build();self.assertEqual(report['canonical_file_count'],966)
  self.assertEqual(report['current_units_with_imported_review_evidence'],479)
  self.assertEqual(len(report['chapters_with_complete_imported_selected_edition_review']),37)
  self.assertIn(44,report['chapters_with_complete_imported_selected_edition_review'])
  self.assertEqual(report['evidence_inventory_warnings'],[]);self.assertFalse(report['completion_proven'])
 def test_rehashed_source_english_and_each_explanation_rejected(self):
  for mode in ['source','English','notea','noteb']:
   with self.subTest(mode=mode),tempfile.TemporaryDirectory()as directory:
    p,m=self.package_fixture(directory);path=p/'044-001.candidate.yaml';d=yaml.load(path.read_bytes(),Loader=t.LOADER)
    if mode=='source':d['source']['text']=d['source']['text'].replace('ኀዲገ','ኃዲገ')
    elif mode=='English':d['translation']['text']=d['translation']['text'].replace('their form','with them')
    else:d['translation']['footnotes'][0 if mode=='notea'else 1]['text']='Unreviewed replacement.'
    path.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False));m['files'][path.name]=t.sha(path.read_bytes());write_json(p/'manifest.json',m)
    with self.assertRaises(ValueError):t.verify(p,evidence_only=True)
 def test_missing_peer_and_rebound_input_not_accepted(self):
  for mode in ['missing_peer','rebound_old_input']:
   with self.subTest(mode=mode),tempfile.TemporaryDirectory()as directory:
    p,m=self.package_fixture(directory)
    if mode=='missing_peer':m['review_bindings'][b.REF]=m['review_bindings'][b.REF][:1]
    else:
     peer=m['review_bindings'][b.REF][1];pvpath=p/peer['provenance'];pv=json.loads(pvpath.read_text())
     peer['input']='history/ch44-full-author/review-input.json'
     self.assertEqual(t.sha((p/peer['input']).read_bytes()),'0394f4ca6e72563f644bcf6f8f976934ab6733d91d5b885c2791181c9458f324')
     pv['input_sha256']=t.sha((p/peer['input']).read_bytes());write_json(pvpath,pv);m['files'][peer['provenance']]=t.sha(pvpath.read_bytes())
    write_json(p/'manifest.json',m)
    with self.assertRaises(ValueError):t.verify(p,evidence_only=True)
 def test_full_corpus_unrelated_drift_rejected_without_writes(self):
  actual=t.corpus_hashes()
  for key in ['044/001.yaml','001/001.yaml']:
   changed=dict(actual);changed[key]='0'*64
   with self.subTest(key=key),patch.object(t,'corpus_hashes',return_value=changed):
    with self.assertRaisesRegex(ValueError,'Canonical changes exceed'):b.verify_current()
 def test_fixed_chain_rejects_missing_receipt_stale_manifest_and_wrong_baseline(self):
  # Copy only B34. Other fixed evidence remains read-only in its real tree.
  original=t.APPLICATIONS
  for mode in ['missing_receipt','stale_manifest','wrong_baseline','wrong_receipt_postmap']:
   with self.subTest(mode=mode),tempfile.TemporaryDirectory()as directory:
    p,m=self.package_fixture(directory)
    if mode=='missing_receipt':(p/'application.json').unlink()
    elif mode=='stale_manifest':
     r=json.loads((p/'application.json').read_text());r['manifest_sha256']='0'*64;write_json(p/'application.json',r)
    elif mode=='wrong_receipt_postmap':
     r=json.loads((p/'application.json').read_text());r['canonical_after_sha256']['001/001.yaml']='0'*64;write_json(p/'application.json',r)
    else:m['canonical_baseline_sha256']['001/001.yaml']='0'*64;write_json(p/'manifest.json',m)
    # Route only this exact package; do not copy/change any canonical files.
    from unittest.mock import MagicMock
    routed=MagicMock();routed.resolve.return_value=original.resolve();routed.__truediv__.side_effect=lambda name:p if name==b.NAME else original/name
    with patch.object(t,'APPLICATIONS',routed):
     expected_error={'missing_receipt':'Canonical changes exceed','stale_manifest':'B34 exact applied receipt','wrong_baseline':'Fixed B34 manifest','wrong_receipt_postmap':'B34 exact applied receipt'}[mode]
     with self.assertRaisesRegex(ValueError,expected_error):b.verify_batch33_postmap_or_fixed_successor()
 def test_wrong_fixed_baseline_rejected_even_if_outer_digest_is_rebound(self):
  # Reach the semantic baseline guard rather than relying only on fixed SHA.
  with tempfile.TemporaryDirectory()as directory:
   p,m=self.package_fixture(directory);m['canonical_baseline_sha256']['001/001.yaml']='0'*64;write_json(p/'manifest.json',m)
   original=t.APPLICATIONS
   from unittest.mock import MagicMock
   routed=MagicMock();routed.resolve.return_value=original.resolve();routed.__truediv__.side_effect=lambda name:p if name==b.NAME else original/name
   with patch.object(t,'APPLICATIONS',routed),patch.object(b,'MANIFEST_SHA',t.sha((p/'manifest.json').read_bytes())):
    with self.assertRaisesRegex(ValueError,'exact B33'):b.verify_current()

if __name__=='__main__':unittest.main()
