"""Complete42, real missing3 and exact negative-relative subject preservation."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t
from tools.enoch.current_evidence import verify_current
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader

P=t.APPLICATIONS/'enoch_full_repair_batch25_20261024'
OLD=t.APPLICATIONS/'enoch_full_repair_batch05_20261020'
REFS=[f'1 Enoch 42:{v}'for v in(1,2,3)]
MANIFEST='a63aeb53e3aa258c49d57e24e1bad6fdc6ec3ceca917882ddfc2b94715f92661'


def record(v):return yaml.load((t.TRANSLATION/f'042/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)


class FullRepairBatch25Test(unittest.TestCase):
    def test_exact_three_and_complete965_postmap_with_one_addition(self):
        self.assertEqual(t.sha((P/'manifest.json').read_bytes()),MANIFEST)
        m=t.load_manifest(P);r=json.loads((P/'application.json').read_text())
        self.assertEqual(verify_current(P)['references'],REFS)
        previous=json.loads((t.APPLICATIONS/'enoch_full_repair_batch24_20261024/application.json').read_text())
        self.assertEqual(m['canonical_baseline_sha256'],previous['canonical_after_sha256'])
        self.assertEqual(len(m['canonical_baseline_sha256']),964);self.assertNotIn('042/003.yaml',m['canonical_baseline_sha256'])
        expected=dict(m['canonical_baseline_sha256'])
        for v in(1,2,3):
            expected[f'042/{v:03d}.yaml']=t.sha((P/f'042-{v:03d}.candidate.yaml').read_bytes())
            self.assertEqual(t.sha((t.TRANSLATION/f'042/{v:03d}.yaml').read_bytes()),expected[f'042/{v:03d}.yaml'])
        self.assertEqual(r['canonical_after_sha256'],expected);self.assertEqual(r['snapshot_file_count'],965)
        self.assertTrue(r['unrelated_canonical_files_unchanged_at_application']);self.assertEqual(m['retirements'],[])

    def test_actual_Git_absence_and_two_explicit_prior_owners(self):
        m=t.load_manifest(P);old=t.load_manifest(OLD)
        self.assertEqual(m['source_baseline_git_commit'],'6499ede72eea063ebc8574ff56e029bb66768f5f')
        path='translation/extra_canonical/1_enoch/042/003.yaml'
        self.assertNotEqual(subprocess.run(['git','cat-file','-e',m['source_baseline_git_commit']+':'+path],cwd=t.ROOT,capture_output=True).returncode,0)
        self.assertNotIn('review_history',record(3));self.assertIsNone(record(3)['source_correction']['baseline_sha256'])
        self.assertEqual(set(m['supersedes']),set(REFS[:2]))
        for v in(1,2):
            ref=f'1 Enoch 42:{v}';digest=old['files'][f'042-{v:03d}.candidate.yaml']
            self.assertEqual(m['supersedes'][ref],{'package':OLD.name,'manifest_sha256':t.sha((OLD/'manifest.json').read_bytes()),'candidate_sha256':digest})
            self.assertEqual(m['canonical_baseline_sha256'][f'042/{v:03d}.yaml'],digest)
        self.assertTrue(set(REFS[:2])<={r['reference']for r in verify_current(OLD)['reviewed_supersessions']})

    def test_original_fullthree_inputs_decisions_and_actual_spans(self):
        m=t.load_manifest(P);p=P/'final/ch42-full/review-input.json'
        self.assertEqual(t.sha(p.read_bytes()),'ef72b6769cb9fa596b39c9f63f809b5cdc204bce089fdd9e2e98b0285e1975a2')
        self.assertEqual([r['reference']for r in json.loads(p.read_text())],REFS)
        for b in m['review_bindings'][REFS[0]]:
            for ref in REFS:t.review_row(P,b,ref,m['files'])
            self.assertEqual([(r['reference'],r['verdict'])for r in t.review_entries(json.loads((P/b['review']).read_text()))],[(r,'accept')for r in REFS])
        c=m['chapter_inventories'][0];self.assertEqual(c['chapter'],42);self.assertEqual(c['units'],[1,2,3]);self.assertTrue(c['independent_count_confirmation'])
        data=json.loads((P/c['artifact']).read_text());self.assertEqual(data['chapters'][0]['unit_pdf_pages'],{'1':[121],'2':[122],'3':[122]})
        self.assertFalse(data['wording_approval']);self.assertFalse(data['reader_release_policy_changed'])

    def test_found_no_place_and_existence_do_not_add_a_giver(self):
        d=record(1);text=d['translation']['text']
        self.assertIn('Wisdom found no place',text);self.assertIn('her dwelling was in the heavens',text)
        self.assertIn('ወ*ሀለወ፡',d['source']['text'])
        for extra in('God','assigned','given','granted'):self.assertNotIn(extra,text)
        self.assertEqual(d['source']['transcription_uncertainties'][0]['status'],'literal_selected_relation_retained')

    def test_return_and_starred_seating_range_do_not_invent_throne_or_vehicle(self):
        d=record(2);text=d['translation']['text'];note=d['translation']['footnotes'][0]['text']
        self.assertIn('መካና፡ ገብአት',d['source']['text']);self.assertIn('ወ*ተጸዐነት',d['source']['text'])
        self.assertIn('returned to her place',text);self.assertIn('took her seat among the angels',text)
        self.assertNotIn('ተቀመጠት',d['source']['text'])
        for extra in('throne','vehicle'):self.assertNotIn(extra,text)
        self.assertIn('mounting',note)

    def test_missing_three_keeps_Injustice_feminine_subject_not_reversed_object(self):
        d=record(3);s=d['source'];text=d['translation']['text'];note=d['translation']['footnotes'][0]['text']
        self.assertIn('ዘኢፈቀደት፡ ረከበት',s['text']);self.assertNotIn('ፈቀዱት',s['text'])
        self.assertIn('She found those she had not wanted and dwelt among them',text)
        self.assertNotIn('those who did not want her',text);self.assertNotIn('seek',text)
        self.assertIn('Injustice is the subject',note);self.assertIn('later plural',note)

    def test_both_full_similes_and_source_storehouses_are_retained(self):
        d=record(3);text=d['translation']['text'];source=d['source']['text']
        for phrase in('from her storehouses','like rain in a wilderness','like dew on thirsty earth'):self.assertIn(phrase,text)
        for phrase in('እምመዛግብቲሃ','ከመ፡ ዝናም፡ በበዳው','ወከመ፡ ጠል፡ በምድር፡ ጽምእት'):self.assertIn(phrase,source)
        self.assertEqual(text.count('like '),2)

    def test_full_source_registration_and_exact_prompt_notes_export(self):
        from tools.enoch.selected_edition_sources import registry_data,load_chapter
        r=registry_data();self.assertEqual(r['chapters']['42'],P.name)
        self.assertFalse(any(k.startswith('42:')for k in r['units']))
        self.assertEqual([row['verse']for row in load_chapter(42)],[1,2,3])
        for v in(1,2,3):
            d=record(v);out=reader._export_record_verse(v,d);bundle=build_enoch_prompt(42,v)
            self.assertEqual(out['text'],d['translation']['text']);self.assertEqual(out['footnotes'],d['translation']['footnotes']);self.assertEqual(out['footnote_review'],reader.PROTOCOL)
            for key in('text','pages','confidence','transcription_uncertainties','additional_translation_input'):
                if key in d['source']:self.assertEqual(out['source_critical'][key],d['source'][key]);self.assertEqual(bundle.source_payload[key],d['source'][key])

    def test_isolated_reader_adds_only_complete42_under_existing_policy(self):
        m=t.load_manifest(P)
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory);before=root/'1_enoch';shutil.copytree(t.TRANSLATION,before)
            for v in(1,2):
                rel=f'042/{v:03d}.yaml';(before/rel).write_bytes(subprocess.check_output(['git','cat-file','blob',m['baseline_git_blobs'][rel]['blob']],cwd=t.ROOT))
            (before/'042/003.yaml').unlink()
            with patch.object(reader,'EXTRA_CANONICAL_ROOT',root):old=reader.export_extra_canonical_book('ENO')
            new=reader.export_extra_canonical_book('ENO')
        a={c['chapter']:c for c in old['chapters']};b={c['chapter']:c for c in new['chapters']}
        self.assertEqual(sorted(set(b)-set(a)),[42]);self.assertFalse(set(a)-set(b))
        self.assertEqual(a,{c:v for c,v in b.items()if c!=42})
        self.assertEqual([v['verse']for v in b[42]['verses']],[1,2,3])

    def test_rehashed_subject_reversal_and_giver_invention_are_rejected(self):
        for v in(1,3):
            with self.subTest(verse=v),tempfile.TemporaryDirectory()as directory:
                q=Path(directory)/'package';shutil.copytree(P,q);p=q/f'042-{v:03d}.candidate.yaml';d=yaml.load(p.read_bytes(),Loader=t.LOADER)
                d['translation']['text']=d['translation']['text'].replace('her dwelling was','God assigned her dwelling')if v==1 else d['translation']['text'].replace('those she had not wanted','those who did not want her')
                p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False));m=json.loads((q/'manifest.json').read_text());m['files'][p.name]=t.sha(p.read_bytes());(q/'manifest.json').write_text(json.dumps(m))
                with self.assertRaises(ValueError):t.verify(q,evidence_only=True)

    def test_composite_progress_not_autograph_or_whole_book_certification(self):
        from tools.enoch.full_repair_progress import build
        p=build();self.assertGreaterEqual(p['canonical_file_count'],965);self.assertGreaterEqual(p['current_units_with_imported_review_evidence'],475)
        self.assertEqual(p['evidence_inventory_warnings'],[]);self.assertIn(42,p['chapters_with_complete_imported_selected_edition_review']);self.assertFalse(p['completion_proven'])
        for v in(1,2,3):
            d=record(v);flags=d['source_correction'];self.assertTrue(flags['selected_edition_chapter_reviewed'])
            for key in('chapter_publication_approval','full_book_verified','human_specialist_certification','manuscript_witness_certification','graphic_publication_approved'):self.assertFalse(flags[key])
            self.assertEqual(d['ai_draft']['model_id'],'not_reported')

    def test_workflow_fetches_actual_current_main_and_runs_gate(self):
        text=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn('git fetch --no-tags --depth=1 origin 6499ede72eea063ebc8574ff56e029bb66768f5f',text)
        self.assertIn("python -m unittest discover -s tests -p 'test_enoch_full_repair_batch25.py'",text)


if __name__=='__main__':unittest.main()
