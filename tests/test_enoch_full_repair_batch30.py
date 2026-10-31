"""Exact missing53:6 restoration; prior wrong fidels never inherit approval."""
import json,shutil,subprocess,tempfile,unittest
from tools.enoch.batch34_evidence import assert_current_progress
from pathlib import Path
import yaml
from tools.enoch import bounded_application as t
from tools.enoch.current_evidence import verify_current
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader
P=t.APPLICATIONS/'enoch_full_repair_batch30_20261025';PREVIOUS=t.APPLICATIONS/'enoch_full_repair_batch29_20261024';REF='1 Enoch 53:6';SHA='c71ce5a3d18960cc6ac785bee2be9afd52247aa5faacf4c6539b5129e6fff978';INPUT='531b38d6de133c420acebfde36f63fcae07762a9ffeb3cad36ca276d2988f1a4'
def record():return yaml.load((t.TRANSLATION/'053/006.yaml').read_bytes(),Loader=t.LOADER)
class Batch30Test(unittest.TestCase):
    def test_one_real_addition_and_exact_all966_file_postmap(self):
        self.assertEqual(t.sha((P/'manifest.json').read_bytes()),SHA);m=t.load_manifest(P);r=json.loads((P/'application.json').read_text());old=json.loads((PREVIOUS/'application.json').read_text())
        self.assertEqual(m['references'],[REF]);self.assertEqual(m['canonical_baseline_sha256'],old['canonical_after_sha256']);self.assertEqual(len(m['canonical_baseline_sha256']),965)
        expected=dict(m['canonical_baseline_sha256']);self.assertNotIn('053/006.yaml',expected);expected['053/006.yaml']=m['files']['053-006.candidate.yaml']
        self.assertEqual(r['canonical_after_sha256'],expected);from test_enoch_full_repair_batch31 import assert_current_batch31;successor,_=assert_current_batch31(self);self.assertEqual(successor['canonical_baseline_sha256'],expected);self.assertEqual(r['snapshot_file_count'],966);self.assertTrue(r['unrelated_canonical_files_unchanged_at_application']);self.assertEqual(m['retirements'],[]);self.assertEqual(m['supersedes'],{})
        self.assertEqual(t.sha((P/'history/unapplied-stage-v1/manifest.json').read_bytes()),'436e7ebfe09c7a93c526563a956679b107190458f93e6a6544f486b4725c902e')
    def test_actual_published_main_git_path_was_absent(self):
        m=t.load_manifest(P);base='cc3ee94d1fb63bfadfd1f514477978f2537a02ad';self.assertEqual(m['source_baseline_git_commit'],base)
        result=subprocess.run(['git','cat-file','-e',base+':translation/extra_canonical/1_enoch/053/006.yaml'],cwd=t.ROOT,capture_output=True);self.assertNotEqual(result.returncode,0)
        proof=json.loads((P/'absent-baseline-proof.json').read_text());self.assertTrue(proof['actual_git_path_absent']);self.assertEqual(proof['new_canonical_file_count'],966)
        delivery=json.loads((P/'prior-public-delivery-verification.json').read_text());self.assertEqual(delivery['source_commit'],base);self.assertEqual(delivery['compiler_revision'],'enoch-notes-v2')
    def test_exact_pair_and_actual_raw_input_hashes(self):
        m=t.load_manifest(P);self.assertEqual(verify_current(P)['references'],[REF]);bindings=m['review_bindings'][REF];self.assertEqual(len({b['reviewer_id']for b in bindings}),2)
        rows=[t.review_row(P,b,REF,m['files'])for b in bindings];self.assertEqual(rows[0],rows[1]);self.assertEqual(rows[0]['translation'],record()['translation'])
        for b in bindings:self.assertEqual(m['files'][b['input']],INPUT)
        peer=json.loads((P/bindings[1]['review']).read_text());self.assertEqual(peer['review_kind'],'informed-same-source-exact-whole-unit-peer-review');self.assertEqual(peer['model'],'not_reported');self.assertEqual(peer['provider'],'not_reported')
        pv=json.loads((P/bindings[1]['provenance']).read_text());self.assertTrue(pv['prior_exposure']);self.assertEqual(pv['source_pdf_sha256'],t.PRIMARY_SHA)
    def test_actual_contracted_verb_assembly_noun_and_printed_title(self):
        d=record();s=d['source']['text'];self.assertIn('ያስተርኢ፡',s);self.assertIn('ቤተ፡ ምስትጉብኤ፡ ዚአሁ፡',s);self.assertTrue(s.endswith('መንፈስት።'))
        for wrong in('ማኅበሩ','ያስተርእይ','መንፈሳት'):self.assertNotIn(wrong,s)
        self.assertEqual(d['source']['pages'],[135]);self.assertEqual(d['source']['confidence'],'low');self.assertEqual(len(d['source']['transcription_uncertainties']),3)
    def test_complete_singular_causative_then_plural_negative_not_named_agent(self):
        self.assertEqual(record()['translation']['text'],'After this, the righteous and chosen one will make the house of his assembly visible. From now on they will not be hindered, in the name of the Lord of Spirits.[a]')
        self.assertIn('ኢይትከልኡ',record()['source']['text']);self.assertTrue(record()['translation']['footnotes']);self.assertFalse(record()['source_correction']['selected_edition_chapter_reviewed'])
    def test_original_and_first_corrective_whole_holds_not_erased(self):
        for name,digest in [('ch53-unit6-exact-peer','a5ceba827d8271a5f1b1c49ad7cddcbd4a66ab8948145319165eac698bce588b'),('ch53-unit6-corrective-exact-peer','1f98adf397c9fc6a6b202c33266889af1802470a31c63a28794bfc48e2e0bdfe')]:
            p=P/'history'/name/'independent-review.json';self.assertEqual(t.sha(p.read_bytes()),digest);self.assertEqual(next(r['verdict']for r in t.review_entries(json.loads(p.read_text()))if r['reference']==REF),'hold')
        self.assertEqual(t.sha((PREVIOUS/'manifest.json').read_bytes()),'bcdbfe3deba3095ef7b194220e844b4b7de775ebbe8e7c09af7feccf7a5f5ad9')
    def test_only_named_source_ingress_not_whole_chapter_or_neighbors(self):
        from tools.enoch import selected_edition_sources as sources,existing_count_ingress as ingress
        m=t.load_manifest(P);self.assertEqual(m['chapter_inventories'],[]);self.assertEqual(m['source_only_count_inventories'],[]);self.assertEqual(ingress.validate(m)[53]['units'],list(range(1,8)))
        registry=sources.registry_data();self.assertEqual(registry['units']['53:6'],P.name);self.assertNotIn('53',registry['chapters'])
        for v in(3,4,7):self.assertNotIn(f'53:{v}',registry['units'])
        for v in(4,7):self.assertFalse((t.TRANSLATION/f'053/{v:03d}.yaml').exists())
        self.assertEqual(t.sha((t.TRANSLATION/'053/003.yaml').read_bytes()),m['canonical_baseline_sha256']['053/003.yaml'])
        self.assertEqual(next(r['source']['text']for r in sources.load_unit_overrides(53)if r['verse']==6),record()['source']['text'])
    def test_exact_source_english_and_notes_reach_existing_export_and_prompt(self):
        d=record();out=reader._export_record_verse(6,d);prompt=build_enoch_prompt(53,6)
        self.assertEqual(out['text'],d['translation']['text']);self.assertEqual(out['footnotes'],d['translation']['footnotes']);self.assertEqual(out['footnote_review'],reader.PROTOCOL);self.assertEqual(out['source_critical']['text'],d['source']['text']);self.assertEqual(prompt.source_payload['text'],d['source']['text'])
    def tamper_candidate(self,field,change):
        with tempfile.TemporaryDirectory()as directory:
            q=Path(directory)/'package';shutil.copytree(P,q);p=q/'053-006.candidate.yaml';d=yaml.load(p.read_bytes(),Loader=t.LOADER);d[field]['text']=change(d[field]['text']);p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False));m=json.loads((q/'manifest.json').read_text());m['files'][p.name]=t.sha(p.read_bytes());(q/'manifest.json').write_text(json.dumps(m))
            with self.assertRaises(ValueError):t.verify(q,evidence_only=True)
    def test_rehashed_normalized_title_is_not_reviewed(self):
        self.tamper_candidate('source',lambda s:s.replace('መንፈስት','መንፈሳት'))
    def test_rehashed_removed_negative_is_not_reviewed(self):
        self.tamper_candidate('translation',lambda s:s.replace('they will not be hindered','they will be hindered'))
    def test_missing_peer_and_rehashed_false_primary_identity_fail_closed(self):
        for mode in('missing_peer','wrong_PDF'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory()as directory:
                q=Path(directory)/'package';shutil.copytree(P,q);m=json.loads((q/'manifest.json').read_text())
                if mode=='missing_peer':m['review_bindings'][REF]=m['review_bindings'][REF][:1]
                else:
                    name=m['review_bindings'][REF][1]['provenance'];p=q/name;pv=json.loads(p.read_text());pv['source_pdf_sha256']='0'*64;p.write_text(json.dumps(pv));m['files'][name]=t.sha(p.read_bytes())
                (q/'manifest.json').write_text(json.dumps(m))
                with self.assertRaises(ValueError):t.verify(q,evidence_only=True)
    def test_exact_progress_increment_no_new_complete_chapter_or_count_credit(self):
        from tools.enoch.full_repair_progress import build
        r=build();self.assertEqual(r['canonical_file_count'],966);assert_current_progress(self,r);self.assertEqual(len(r['chapters_with_imported_paired_count_inventory']),108);self.assertEqual(r['evidence_inventory_warnings'],[]);self.assertFalse(r['completion_proven'])
        old=json.loads((t.ROOT/'sources/enoch/coverage/full-repair-progress-batch29-20261024.json').read_text());self.assertEqual(old['canonical_file_count'],965);self.assertEqual(old['current_units_with_imported_review_evidence'],475)
