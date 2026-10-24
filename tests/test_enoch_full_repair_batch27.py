"""Exact43:4 printed-title correction with the mandatory variant explanation."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import yaml
from tools.enoch import bounded_application as t
from tools.enoch.current_evidence import verify_current
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader
P=t.APPLICATIONS/'enoch_full_repair_batch27_20261024'
OLD=t.APPLICATIONS/'enoch_full_repair_batch05_20261020'
SHA='d385f8fd51e2b4b93c310c78e295a3d340f5f3117df73370885e95f9225cb611'
REF='1 Enoch 43:4'
def record(v):return yaml.load((t.TRANSLATION/f'043/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)
def assert_current4(test):
    test.assertEqual(t.sha((P/'manifest.json').read_bytes()),SHA);m=t.load_manifest(P);old=t.load_manifest(OLD)
    test.assertEqual(m['supersedes'],{REF:{'package':OLD.name,'manifest_sha256':t.sha((OLD/'manifest.json').read_bytes()),'candidate_sha256':old['files']['043-004.candidate.yaml']}})
    test.assertEqual(m['canonical_baseline_sha256']['043/004.yaml'],old['files']['043-004.candidate.yaml'])
    test.assertEqual(t.sha((t.TRANSLATION/'043/004.yaml').read_bytes()),m['files']['043-004.candidate.yaml']);test.assertEqual(verify_current(P)['references'],[REF])

class Batch27Test(unittest.TestCase):
    def test_exact_one_and_complete965_postmap_no_additions(self):
        assert_current4(self);m=t.load_manifest(P);r=json.loads((P/'application.json').read_text());self.assertEqual(m['source_baseline_git_commit'],'68ae1e77262afcdcf64640ce01832549af1ec69c')
        self.assertEqual(m['canonical_baseline_sha256'],json.loads((t.APPLICATIONS/'enoch_full_repair_batch26_20261024/application.json').read_text())['canonical_after_sha256'])
        expected=dict(m['canonical_baseline_sha256']);expected['043/004.yaml']=m['files']['043-004.candidate.yaml'];self.assertEqual(r['canonical_after_sha256'],expected);self.assertEqual(r['snapshot_file_count'],965);self.assertEqual(m['retirements'],[])

    def test_both_actual_body_forms_not_apparatus_or_familiar_plural(self):
        d=record(4);self.assertEqual(d['source']['text'].count('መንፈስት'),2)
        for other in('መንፈሳት','መናፍስት'):self.assertNotIn(other,d['source']['text'])
        old=yaml.load((OLD/'043-004.candidate.yaml').read_bytes(),Loader=t.LOADER);self.assertEqual(old['source']['text'].count('መንፈሳት'),2)
        self.assertEqual(d['source']['confidence'],'medium');self.assertEqual(d['source']['transcription_uncertainties'],[])

    def test_complete_possessors_names_belief_title_and_eternity(self):
        text=record(4)['translation']['text']
        for phrase in('has shown you their likeness','These are their names','the names of the holy ones','who dwell on dry land','believe in the name of the Lord of spirits','forever and ever'):self.assertIn(phrase,text)
        self.assertNotIn('sowing',text)

    def test_mandatory_note_preserves_printed_reported_variant_contrast(self):
        d=record(4);self.assertIn('spirits[a]',d['translation']['text']);note=d['translation']['footnotes'][0]
        self.assertEqual(note['reason'],'textual_variant');self.assertIn('መንፈስት',note['text']);self.assertIn('መንፈሳት',note['text']);self.assertIn('not silently replaced',note['text'])

    def test_new_single_input_pair_does_not_rewrite_original_hold(self):
        m=t.load_manifest(P);p=P/'final/ch43-4-jp2/review-input.json';self.assertEqual(t.sha(p.read_bytes()),'1b8bc065769823520d29ad3b34084257574a88a02ce4e52948869d63c12b6680')
        for b in m['review_bindings'][REF]:
            t.review_row(P,b,REF,m['files']);self.assertEqual([(r['reference'],r['verdict'])for r in t.review_entries(json.loads((P/b['review']).read_text()))],[(REF,'accept')])
        for name in('ch43-full-author/author-review.json','ch43-full-exact-peer/independent-review.json'):
            rows=t.review_entries(json.loads((P/'history'/name).read_text()));self.assertEqual(next(r['verdict']for r in rows if r['reference']==REF),'hold')
        self.assertEqual(m['chapter_inventories'],[]);self.assertEqual(m['source_only_count_inventories'],[])

    def test_unchanged_neighbors_real_two_hold_and_B26_three_owner(self):
        m=t.load_manifest(P)
        for v in(1,2,3):self.assertEqual(t.sha((t.TRANSLATION/f'043/{v:03d}.yaml').read_bytes()),m['canonical_baseline_sha256'][f'043/{v:03d}.yaml'])
        from tools.enoch.selected_edition_sources import registry_data
        reg=registry_data();self.assertEqual(reg['units']['43:3'],'enoch_full_repair_batch26_20261024');self.assertEqual(reg['units']['43:4'],P.name);self.assertNotIn('43',reg['chapters']);self.assertNotIn('43:2',reg['units'])

    def test_exact_source_prompt_and_existing_details_export(self):
        d=record(4);out=reader._export_record_verse(4,d);prompt=build_enoch_prompt(43,4)
        self.assertEqual(out['text'],d['translation']['text']);self.assertEqual(out['footnotes'],d['translation']['footnotes']);self.assertEqual(out['footnote_review'],reader.PROTOCOL)
        self.assertEqual(out['source_critical']['text'],d['source']['text']);self.assertEqual(prompt.source_payload['text'],d['source']['text'])

    def test_rehashed_silent_normalization_or_note_drop_rejected(self):
        for mode in('normalize','drop_note'):
            with self.subTest(mode=mode),tempfile.TemporaryDirectory()as directory:
                q=Path(directory)/'package';shutil.copytree(P,q);p=q/'043-004.candidate.yaml';d=yaml.load(p.read_bytes(),Loader=t.LOADER)
                if mode=='normalize':d['source']['text']=d['source']['text'].replace('መንፈስት','መናፍስት')
                else:d['translation']['footnotes']=[]
                p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False));m=json.loads((q/'manifest.json').read_text());m['files'][p.name]=t.sha(p.read_bytes());(q/'manifest.json').write_text(json.dumps(m))
                with self.assertRaises(ValueError):t.verify(q,evidence_only=True)

    def test_no_source_record_chapter_count_or_book_completion_inflation(self):
        from tools.enoch.full_repair_progress import build
        r=build();self.assertEqual(r['canonical_file_count'],965);self.assertEqual(r['current_units_with_imported_review_evidence'],475);self.assertEqual(len(r['chapters_with_complete_imported_selected_edition_review']),36);self.assertEqual(len(r['chapters_with_imported_paired_count_inventory']),108);self.assertFalse(r['completion_proven'])
        self.assertFalse(record(4)['source_correction']['selected_edition_chapter_reviewed']);self.assertFalse(record(4)['source_correction']['chapter_publication_approval'])

    def test_CI_fetches_actual_preimage_and_runs_gate(self):
        s=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text();self.assertIn('git fetch --no-tags --depth=1 origin 68ae1e77262afcdcf64640ce01832549af1ec69c',s);self.assertIn("python -m unittest discover -s tests -p 'test_enoch_full_repair_batch27.py'",s)
