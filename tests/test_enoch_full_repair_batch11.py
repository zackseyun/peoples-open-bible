"""Current29/97 repairs, explicit uncertainties, and partial17/71 limits."""
import copy,json,shutil,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t,legacy97_evidence as legacy,structural_counts
from tools.enoch.current_evidence import verify_current
from tools.enoch.full_repair_progress import build
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader

P=t.APPLICATIONS/'enoch_full_repair_batch11_20261022'
def record(c,v):return yaml.load((t.TRANSLATION/f'{c:03d}/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)

class FullRepairBatch11Test(unittest.TestCase):
 def test_exact29_units_four_restored_records_and_eight_held_preimages(self):
  result=verify_current(P);m=t.load_manifest(P);receipt=json.loads((P/'application.json').read_text())
  self.assertEqual(result['candidate_files'],29);self.assertFalse(result['full_book_verified'])
  self.assertEqual(receipt['snapshot_file_count'],962);self.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
  additions=[r for r in m['references']if '%03d/%03d.yaml'%t.parse_ref(r)not in m['canonical_baseline_sha256']]
  self.assertEqual(additions,['1 Enoch 71:14','1 Enoch 71:16','1 Enoch 71:17','1 Enoch 97:10'])
  self.assertEqual(len(m['not_applied']),8)
  for row in m['not_applied']:
   rel='%03d/%03d.yaml'%t.parse_ref(row['reference']);self.assertEqual(receipt['canonical_after_sha256'].get(rel),m['canonical_baseline_sha256'].get(rel))
  self.assertNotIn('071/015.yaml',receipt['canonical_after_sha256'])

 def test_29_keeps_source_signs_corrects_greek_note_and_source_led_suffix(self):
  a=record(29,1);b=record(29,2);m=t.load_manifest(P)
  self.assertEqual(set(m['supersedes']),{'1 Enoch 29:1','1 Enoch 29:2'})
  for v,d in[(1,a),(2,b)]:
   old=yaml.load((t.APPLICATIONS/'enoch_29_20261016'/f'029-{v:03d}.candidate.yaml').read_bytes(),Loader=t.LOADER)
   self.assertEqual(d['source']['text'],old['source']['text'])
   if v==1:self.assertEqual(d['translation']['text'],old['translation']['text'])
  self.assertIn('and the trees also resembled',b['translation']['text']);self.assertNotIn('their trees',b['translation']['text'])
  self.assertIn('†ኵነኔ፡ †ፈድፋደ፡',b['source']['text']);self.assertTrue(b['source']['text'].endswith('(ከርካዕ።)'))
  note=b['translation']['footnotes'][1]['text'];self.assertIn('πιέοντα',note);self.assertIn('πνέοντα',note)
  self.assertTrue(b['source']['additional_translation_input'])

 def test_97_10_retains_negative_wealth_clause_and_both_causes(self):
  d=record(97,10);text=d['translation']['text']
  self.assertIn('ኢይነብር',d['source']['text']);self.assertEqual(d['source']['text'].count('እስመ'),2)
  self.assertIn('for wealth will not remain with you',text);self.assertIn('For you acquired all of it through injustice',text)
  from tools.enoch import audit_pob_source_coverage as coverage
  inventory=coverage.audit([97])['chapters'][0];self.assertTrue(inventory['inventory_complete']);self.assertEqual(inventory['missing_verse_numbers'],[]);self.assertEqual(inventory['primary_source_verses'],10);self.assertFalse(inventory['translation_verified_by_this_audit'])
  self.assertIn('but will quickly leave you',text);self.assertNotIn('burn',text)
  self.assertEqual(len(d['translation']['footnotes']),2)
  # The91–103 count-only profile explicitly excludes separately declared97.
  self.assertNotIn(97,structural_counts.load_all_inventories())
  m=t.load_manifest(P);self.assertEqual(next(c['units']for c in m['chapter_inventories']if c['chapter']==97),list(range(1,11)))
  for n in(1,2):
   raw=json.loads((P/f'history/declared97-boundary/original-pass{n}-review.json').read_text())
   self.assertEqual([r['reference']for r in raw['reviews']],[f'1 Enoch 97:{v}'for v in range(1,11)])
   self.assertEqual(raw['reviews'][-1]['verdict'],'hold') # Historical adversity is never approval.

 def test_97_5_secondary_edition_not_silent_short_form_normalization(self):
  d=record(97,5);s=d['source'];self.assertTrue(s['text'].endswith('ኵነ*ክሙ።'));self.assertEqual(s['confidence'],'low')
  self.assertEqual(s['transcription_uncertainties'][0]['type'],'printed_internal_critical_mark_meaning_unresolved')
  extra=s['additional_translation_input'];self.assertEqual(len(extra),1);self.assertEqual(extra[0]['reading'],'ኵነኔክሙ')
  self.assertEqual(extra[0]['pdf_pages'],[99]);self.assertIn('your judgment',d['translation']['text'])
  self.assertIn('holy ones',d['translation']['text']);self.assertIn('different edited edition',d['translation']['footnotes'][1]['text'])

 def test_97_6_passive_requires_exact_reported_and_edited_additional_readings(self):
  d=record(97,6);s=d['source'];self.assertIn('ወ*ይገደፍ',s['text']);self.assertNotIn('ወይትገደፍ',s['text'])
  self.assertEqual(s['confidence'],'low');self.assertEqual(s['transcription_uncertainties'][0]['type'],'unresolved_selected_verb_voice')
  extra=s['additional_translation_input'];self.assertEqual(len(extra),2)
  self.assertEqual(extra[0]['reported_reading'],'ይትገደፍ');self.assertEqual(extra[0]['reported_witness_labels_exact'],'m u, β')
  self.assertEqual(extra[1]['exact_reading_with_conjunction'],'ወይትገደፍ');self.assertEqual(extra[1]['pdf_pages'],[99])
  self.assertIn('will be rejected',d['translation']['text']);self.assertNotIn('He will reject',d['translation']['text'])
  self.assertEqual(record(97,4)['source']['transcription_uncertainties'],[])

 def test_exact_current_source_controls_and_all_explanations_survive_export_and_prompt(self):
  for ref in t.load_manifest(P)['references']:
   c,v=t.parse_ref(ref);d=record(c,v);out=reader._export_record_verse(v,d)
   self.assertEqual(out.get('footnotes',[]),d['translation'].get('footnotes',[]))
   if d['translation'].get('footnotes'):
    self.assertEqual(out['footnote_review'],reader.PROTOCOL)
    for k in('edition','language','text','pages','note','confidence','transcription_uncertainties','additional_translation_input'):
     if k in d['source']:self.assertEqual(out['source_critical'][k],d['source'][k])
  for c,v in[(29,2),(97,5),(97,6),(97,10)]:
   s=record(c,v)['source'];bundle=build_enoch_prompt(c,v)
   for k in('text','confidence','transcription_uncertainties','additional_translation_input'):
    if k in s:self.assertEqual(bundle.source_payload[k],s[k])

 def test_legacy_four_current_successors_do_not_invent_two_old_acceptances(self):
  result=verify_current(t.APPLICATIONS/legacy.NAME)
  self.assertEqual(len(result['reviewed_supersessions']),4)
  self.assertEqual(result['historical_accepted_individual_review_passes'],1)
  self.assertEqual(result['diagnostic_whole_chapter_reviews'],2)
  self.assertFalse(result['chapter_publication_approval'])
  self.assertNotIn('canonical_sha256',result)
  for ref in legacy.REFS:
   c,v=t.parse_ref(ref);self.assertEqual(result['current_canonical_sha256'][ref],t.sha((t.TRANSLATION/f'{c:03d}/{v:03d}.yaml').read_bytes()))
   self.assertNotEqual(result['current_canonical_sha256'][ref],result['historical_canonical_sha256'][ref])
  from tools.textual_restoration import enoch_97_partial_transaction as old
  with self.assertRaises(ValueError):old.verify_applied() # Strict old target check unchanged.

 def test_only97_newly_released_no_unrelated_export_change(self):
  m=t.load_manifest(P)
  with tempfile.TemporaryDirectory()as directory:
   root=Path(directory);before_root=root/'1_enoch';shutil.copytree(t.TRANSLATION,before_root)
   for ref in m['references']:
    c,v=t.parse_ref(ref);rel=f'{c:03d}/{v:03d}.yaml';target=before_root/rel
    if rel in m['baseline_git_blobs']:target.write_bytes(subprocess.check_output(['git','cat-file','blob',m['baseline_git_blobs'][rel]['blob']],cwd=t.ROOT))
    else:target.unlink()
   with patch.object(reader,'EXTRA_CANONICAL_ROOT',root):before=reader.export_extra_canonical_book('ENO')
   after=reader.export_extra_canonical_book('ENO')
  a={c['chapter']:c for c in before['chapters']};b={c['chapter']:c for c in after['chapters']}
  self.assertEqual(sorted(set(b)-set(a)),[97]);self.assertFalse(set(a)-set(b))
  self.assertEqual({c:d for c,d in a.items()if c not in(17,29,71,97)},{c:d for c,d in b.items()if c not in(17,29,71,97)})
  self.assertEqual([v['verse']for v in b[97]['verses']],list(range(1,11)));self.assertNotIn(71,b)

 def test_partial17_71_counts_and_pronouns_not_full_chapter_or_harmonization(self):
  m=t.load_manifest(P);self.assertEqual({c['chapter']:len(c['units'])for c in m['source_only_count_inventories']},{17:8,71:17})
  for ref in m['references']:
   c,v=t.parse_ref(ref)
   if c in(17,71):self.assertFalse(record(c,v)['source_correction']['selected_edition_chapter_reviewed'])
  self.assertIn('You are the Son of Man',record(71,14)['translation']['text']);self.assertIn('will not leave you',record(71,14)['translation']['text'])
  self.assertIn('Their dwelling will be with you',record(71,16)['translation']['text']);self.assertIn('that Son of Man',record(71,17)['translation']['text'])

 def test_language_id_normalization_changes_no_source_glyph_or_english(self):
  m=t.load_manifest(P)
  for v in(7,8):
   current=record(17,v);old=yaml.load((P/f'history/unpublished-local-language-defect/017-{v:03d}.candidate.yaml').read_bytes(),Loader=t.LOADER)
   self.assertEqual(old['source']['language'],'Geʿez');self.assertEqual(current['source']['language'],'Geez')
   a=copy.deepcopy(current['source']);b=copy.deepcopy(old['source']);a.pop('language');b.pop('language');self.assertEqual(a,b)
   self.assertEqual(current['translation'],old['translation']);self.assertTrue(all('ch17-language-id'in b['input']for b in m['review_bindings'][f'1 Enoch 17:{v}']))
  with tempfile.TemporaryDirectory()as directory:
   target=Path(directory)/'package';shutil.copytree(P,target);path=target/'017-007.candidate.yaml';d=yaml.load(path.read_bytes(),Loader=t.LOADER);d['source']['language']='Geʿez';path.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False))
   manifest=json.loads((target/'manifest.json').read_text());manifest['files'][path.name]=t.sha(path.read_bytes());(target/'manifest.json').write_text(json.dumps(manifest))
   with self.assertRaisesRegex(ValueError,'identity/lifecycle'):t.verify(target,evidence_only=True)

 def test_old29_imports_skip_repaired_units_and_old17_receipt_is_not_reused(self):
  from tools.enoch import historical_evidence as h
  old=h.load_current();self.assertEqual(len(old),27);self.assertNotIn((29,1),old);self.assertNotIn((29,2),old)
  self.assertEqual(len(h.load_all_current()),35)
  m=t.load_manifest(P);prior=t.APPLICATIONS/'enoch_5_9_17_7_8_20260929';old_manifest=json.loads((prior/'manifest.json').read_text())
  for v in(7,8):
   raw=(prior/f'017-{v:03d}.candidate.yaml').read_bytes();digest=t.sha(raw)
   self.assertEqual(digest,old_manifest['files'][f'017-{v:03d}.candidate.yaml'])
   self.assertEqual(m['canonical_baseline_sha256'][f'017/{v:03d}.yaml'],digest)
   self.assertEqual(record(17,v)['review_history'][0]['sha256'],digest)
   self.assertNotEqual(t.sha((t.TRANSLATION/f'017/{v:03d}.yaml').read_bytes()),digest)
  # Raw continuation evidence remains available independently of accepted source ingress.
  from tools.enoch import verse_parser
  raw17=next(r for r in verse_parser.parse_ocr_chapter(17)[0]if r.verse==7)
  self.assertIn('ch18.txt',raw17.chapter_file)
  accepted=verse_parser.load_verse(17,7)[0];self.assertIn('enoch_full_repair_batch11',accepted.chapter_file)
  self.assertEqual(record(17,7)['source']['pages'],[84,86])

 def test_current_progress_and_delivery_limits_not_whole_book_certificate(self):
  report=build();self.assertGreaterEqual(report['current_units_with_imported_review_evidence'],366)
  self.assertIn(97,report['chapters_with_complete_imported_selected_edition_review']);self.assertIn(29,report['chapters_with_complete_imported_selected_edition_review'])
  self.assertEqual(report['evidence_inventory_warnings'],[]);self.assertFalse(report['completion_proven'])
  gate=json.loads((P/'explanation-delivery-gate.json').read_text())
  for k in('candidate_public_delivery_verified','candidate_live_browser_verified','physical_device_verified','all108_verified'):self.assertFalse(gate[k])

if __name__=='__main__':unittest.main()
