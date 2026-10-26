"""Singular53:5 and actual selected54:9 voice, with adverse evidence preserved."""
import json,shutil,tempfile,unittest
from pathlib import Path
import yaml
from tools.enoch import bounded_application as t
from tools.enoch.current_evidence import verify_current
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader
P=t.APPLICATIONS/'enoch_full_repair_batch29_20261024';OLD=t.APPLICATIONS/'enoch_full_repair_batch08_20261022';SHA='bcdbfe3deba3095ef7b194220e844b4b7de775ebbe8e7c09af7feccf7a5f5ad9';REFS=['1 Enoch 53:5','1 Enoch 54:9']
def record(c,v):return yaml.load((t.TRANSLATION/f'{c:03d}/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)
class Batch29Test(unittest.TestCase):
    def test_exact_two_and_complete965_postmap(self):
        self.assertEqual(t.sha((P/'manifest.json').read_bytes()),SHA);m=t.load_manifest(P);r=json.loads((P/'application.json').read_text());self.assertEqual(verify_current(P)['references'],REFS)
        previous=json.loads((t.APPLICATIONS/'enoch_full_repair_batch27_20261024/application.json').read_text());self.assertEqual(m['canonical_baseline_sha256'],previous['canonical_after_sha256'])
        expected=dict(m['canonical_baseline_sha256'])
        for ref in REFS:
            c,v=t.parse_ref(ref);expected[f'{c:03d}/{v:03d}.yaml']=m['files'][f'{c:03d}-{v:03d}.candidate.yaml']
        self.assertEqual(r['canonical_after_sha256'],expected);self.assertEqual(r['snapshot_file_count'],965);self.assertTrue(r['unrelated_canonical_files_unchanged_at_application']);self.assertEqual(m['retirements'],[])
    def test_both_explicit_B08_owners_and_actual_preimages(self):
        m=t.load_manifest(P);old=t.load_manifest(OLD);self.assertEqual(m['source_baseline_git_commit'],'9e1a7a359d1aa9a2ef21104f1d7d697cf2cf2996')
        for ref in REFS:
            c,v=t.parse_ref(ref);fn=f'{c:03d}-{v:03d}.candidate.yaml';self.assertEqual(m['supersedes'][ref],{'package':OLD.name,'manifest_sha256':t.sha((OLD/'manifest.json').read_bytes()),'candidate_sha256':old['files'][fn]});self.assertEqual(m['canonical_baseline_sha256'][f'{c:03d}/{v:03d}.yaml'],old['files'][fn])
        result=verify_current(OLD)['reviewed_supersessions']
        for ref in REFS:self.assertIn({'reference':ref,'superseded_by':P.name},result)
    def test_535_singular_in_it_not_unjustified_plural(self):
        d=record(53,5);old=yaml.load((OLD/'053-005.candidate.yaml').read_bytes(),Loader=t.LOADER)
        self.assertEqual(d['source']['text'],old['source']['text']);self.assertIn('ቦቱ',d['source']['text']);self.assertIn('destroyed in it',d['translation']['text']);self.assertNotIn('by them',d['translation']['text']);self.assertIn('by them',old['translation']['text']);self.assertEqual(d['source']['confidence'],'low')
        note=d['translation']['footnotes'][0]['text'];self.assertIn('singular',note)
    def test_549_actual_selected_active_plural_and_accusative_object(self):
        d=record(54,9);old=yaml.load((OLD/'054-009.candidate.yaml').read_bytes(),Loader=t.LOADER)
        self.assertIn('ወይደመስሱ፡ ኵሎ፡',d['source']['text']);self.assertIn('ወይደመሰስ፡ ኵሉ፡',old['source']['text']);self.assertIn('they will wipe out all',d['translation']['text']);self.assertIn('will be wiped out',old['translation']['text'])
        for clause in('those who dwell on dry land','those who dwell beneath the ends of heaven'):self.assertIn(clause,d['translation']['text'])
        self.assertIn('*ዲበ',d['source']['text']);self.assertIn('active',d['translation']['footnotes'][0]['text'])
    def test_distinct_author_full_and_peer_projection_are_exact_same_row(self):
        m=t.load_manifest(P)
        for ref in REFS:
            rows=[t.review_row(P,b,ref,m['files'])for b in m['review_bindings'][ref]];self.assertEqual(rows[0],rows[1]);self.assertEqual(len({b['reviewer_id']for b in m['review_bindings'][ref]}),2)
        a,b=m['review_bindings']['1 Enoch 54:9'];self.assertNotEqual(m['files'][a['input']],m['files'][b['input']]);self.assertEqual(len(json.loads((P/a['input']).read_text())),10);self.assertEqual(len(json.loads((P/b['input']).read_text())),1)
    def test_new_material_grammar_phase_is_not_a_second_blind_reviewer(self):
        raw=json.loads((P/'history/ch54-9-exact-peer-final/independent-review.json').read_text());self.assertFalse(raw['independence']['new_blind_actor']);self.assertEqual(raw['independence']['additional_independent_reviewer_count'],0)
        self.assertFalse(raw['limits']['publication_approval']);self.assertFalse(raw['limits']['new_MSS_inspection']);self.assertEqual(len(raw['scan_image_sha256']),43)
        m=t.load_manifest(P);peer=m['review_bindings']['1 Enoch 54:9'][1];self.assertEqual(peer['reviewer_id'],'/root/enoch54_9_grammar_controls')
    def test_metadata_adapter_binds_whole_file_not_self_payload_and_adds_zero_passes(self):
        m=t.load_manifest(P);b=m['review_bindings']['1 Enoch 54:9'][1];pv=json.loads((P/b['provenance']).read_text());r=json.loads((P/b['review']).read_text());receipt=json.loads((P/'history/ch54-9-exact-peer-final/file-receipt.json').read_text())
        self.assertEqual(pv['review_sha256'],t.sha((P/b['review']).read_bytes()));self.assertEqual(pv['review_sha256'],receipt['independent_review_file_sha256']);self.assertNotEqual(pv['review_sha256'],r['review_sha256']);self.assertEqual(pv['raw_reviews_payload_sha256'],r['review_sha256']);self.assertEqual(pv['scan_image_sha256'],r['scan_image_sha256'])
        for key in('new_English_review_passes','new_provider_calls','new_personally_viewed_photos'):self.assertEqual(pv[key],0)
    def test_adverse_holds_and_withdrawn_unpublished_integration_not_erased(self):
        self.assertFalse((t.APPLICATIONS/'enoch_full_repair_batch28_20261024').exists());rollback=json.loads((P/'history/withdrawn-local-batch28-20261024/rollback-receipt.json').read_text());self.assertTrue(rollback['all965_file_preimage_restored']);self.assertFalse(rollback['published_or_pushed']);self.assertFalse(rollback['raw_review_or_vote_rewritten'])
        raw=json.loads((P/'history/ch54-full-exact-peer-followup1/independent-review.json').read_text());self.assertEqual(next(r['verdict']for r in raw['reviews']if r['reference']=='1 Enoch 54:9'),'hold')
        api=json.loads((P/'history/azure61-sol-pilot/accelerated54-unit09-v1/exact-review/raw-model-text.json').read_text());self.assertEqual(api['reviews'][0]['verdict'],'hold')
        m=t.load_manifest(P)
        from test_enoch_full_repair_batch31 import assert_current_batch31
        successor,_=assert_current_batch31(self);self.assertEqual(successor['canonical_baseline_sha256']['054/001.yaml'],m['canonical_baseline_sha256']['054/001.yaml'])
        self.assertEqual(t.sha((t.TRANSLATION/'054/002.yaml').read_bytes()),m['canonical_baseline_sha256']['054/002.yaml'])
    def test_existing_count_reuse_not_fake_full_submitted_language_scope(self):
        m=t.load_manifest(P);self.assertEqual(m['source_only_count_inventories'],[]);self.assertEqual(m['chapter_inventories'],[]);self.assertEqual([r['chapter']for r in m['existing_paired_count_ingress']],[53,54])
        data=json.loads((P/'source-only-counts.json').read_text());original=json.loads(t.artifact(t.ROOT,data['existing_paired_unit_spans']['path']).read_text())
        for row in data['chapters']:self.assertEqual(row['unit_pdf_pages'],{str(r['verse']):r['pdf_pages']for r in original if r['chapter']==row['chapter']})
        self.assertEqual(data['chapters'][1]['unit_pdf_pages']['7'],[136]);self.assertEqual(data['chapters'][1]['unit_pdf_pages']['8'],[136,137])
    def test_exact_source_notes_and_prompt_existing_details_export(self):
        for c,v in((53,5),(54,9)):
            d=record(c,v);out=reader._export_record_verse(v,d);prompt=build_enoch_prompt(c,v);self.assertEqual(out['text'],d['translation']['text']);self.assertEqual(out['footnotes'],d['translation']['footnotes']);self.assertEqual(out['footnote_review'],reader.PROTOCOL);self.assertEqual(out['source_critical']['text'],d['source']['text']);self.assertEqual(prompt.source_payload['text'],d['source']['text'])
    def test_rehashed_old_plural_or_reported_verb_cannot_get_approval(self):
        for c,v in((53,5),(54,9)):
            with self.subTest(reference=f'{c}:{v}'),tempfile.TemporaryDirectory()as directory:
                q=Path(directory)/'package';shutil.copytree(P,q);p=q/f'{c:03d}-{v:03d}.candidate.yaml';d=yaml.load(p.read_bytes(),Loader=t.LOADER)
                if c==53:d['translation']['text']=d['translation']['text'].replace('in it','by them')
                else:d['source']['text']=d['source']['text'].replace('ወይደመስሱ','ወይደመሰሱ')
                p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False));m=json.loads((q/'manifest.json').read_text());m['files'][p.name]=t.sha(p.read_bytes());(q/'manifest.json').write_text(json.dumps(m))
                with self.assertRaises(ValueError):t.verify(q,evidence_only=True)
    def test_counts_record_coverage_and_language_certificates_not_inflated(self):
        from tools.enoch.full_repair_progress import build
        r=build();self.assertEqual(r['canonical_file_count'],966);self.assertEqual(r['current_units_with_imported_review_evidence'],477);self.assertEqual(len(r['chapters_with_complete_imported_selected_edition_review']),36);self.assertEqual(len(r['chapters_with_imported_paired_count_inventory']),108);self.assertFalse(r['completion_proven']);self.assertEqual(r['evidence_inventory_warnings'],[])
        for c,v in((53,5),(54,9)):self.assertFalse(record(c,v)['source_correction']['selected_edition_chapter_reviewed'])
