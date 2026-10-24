"""Five exact chapter26 treatments and two explicit metadata-to-language successors."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t,metadata26_evidence as metadata
from tools.enoch.current_evidence import verify_current
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader

P=t.APPLICATIONS/'enoch_full_repair_batch22_20261024'
VERSES=(1,2,3,5,6)
REFS=[f'1 Enoch 26:{v}'for v in VERSES]
MANIFEST='74d1340efb155ac8a266f751c49f212f1ecae8d915fd107dc03b933b4f08470b'


def record(v):return yaml.load((t.TRANSLATION/f'026/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)


class FullRepairBatch22Test(unittest.TestCase):
    def test_five_existing_units_and_complete964_historical_postmap(self):
        self.assertEqual(t.sha((P/'manifest.json').read_bytes()),MANIFEST)
        m=t.load_manifest(P);r=json.loads((P/'application.json').read_text())
        self.assertEqual(verify_current(P)['references'],REFS)
        self.assertEqual(m['source_baseline_git_commit'],'ee2a89b5e46db917b59bfa891e127d6bf98f5cfc')
        previous=json.loads((t.APPLICATIONS/'enoch_full_repair_batch21_20261024/application.json').read_text())
        self.assertEqual(m['canonical_baseline_sha256'],previous['canonical_after_sha256'])
        expected=dict(m['canonical_baseline_sha256'])
        for v in VERSES:
            rel=f'026/{v:03d}.yaml';self.assertIn(rel,expected)
            expected[rel]=t.sha((P/f'026-{v:03d}.candidate.yaml').read_bytes())
            self.assertEqual(t.sha((t.TRANSLATION/rel).read_bytes()),expected[rel])
        self.assertEqual(r['canonical_after_sha256'],expected);self.assertEqual(r['snapshot_file_count'],964)
        self.assertTrue(r['unrelated_canonical_files_unchanged_at_application'])
        self.assertEqual(m['retirements'],[]);self.assertEqual(m['chapter_inventories'],[])

    def test_exact_fullsix_input_accepts_five_and_holds_four(self):
        m=t.load_manifest(P);inp=P/'final/ch26-full/review-input.json'
        self.assertEqual(t.sha(inp.read_bytes()),'40383003926a137a74e955d7af4b5b84dbcf524edb8192371bd9c7b88f35a645')
        self.assertEqual([r['reference']for r in json.loads(inp.read_text())],[f'1 Enoch 26:{v}'for v in range(1,7)])
        for b in m['review_bindings'][REFS[0]]:
            for ref in REFS:t.review_row(P,b,ref,m['files'])
            rows=t.review_entries(json.loads((P/b['review']).read_text()))
            self.assertEqual([(r['reference'],r['verdict'])for r in rows],[(f'1 Enoch 26:{v}','hold'if v==4 else'accept')for v in range(1,7)])
            with self.assertRaises(ValueError):t.review_row(P,b,'1 Enoch 26:4',m['files'])

    def test_moist_not_shaded_and_every_botanical_editorial_boundary_remains(self):
        d=record(1);text=d['translation']['text'];source=d['source']['text'];note=d['translation']['footnotes'][0]['text']
        for word in('[moist]','(where there were trees)','branches that remain and sprout','[from a tree that has been cut]'):self.assertIn(word,text)
        self.assertNotIn('shaded',text);self.assertIn('[ጥሉለ፡]',source)
        self.assertIn('(ዘቦቱ፡ ዕፀወ፡)',source);self.assertIn('[እምዕፅ፡ ዘ*ተመተረ።]',source)
        for col in('1214','1019','651','246','184'):self.assertIn(col,note)
        for name in('Jerusalem','temple','fig tree','tree of life'):self.assertNotIn(name,text)

    def test_directions_higher_comparison_and_literal_flow_are_not_reconstructed(self):
        self.assertIn('water from the east',record(2)['translation']['text'])
        self.assertIn('its flow toward the north',record(2)['translation']['text'])
        d=record(3);text=d['translation']['text']
        for words in('higher than this one','[was] a deep ravine without breadth','flowed toward the mountain'):self.assertIn(words,text)
        self.assertNotIn('lower',text)
        self.assertTrue(d['source']['transcription_uncertainties'])

    def test_selected_negative_discloses_intrinsic_dependency_not_new_Greek_adoption(self):
        d=record(5);text=d['translation']['text'];note=d['translation']['footnotes'][0]['text']
        self.assertIn('ኢይትከል',d['source']['text']);self.assertIn('no tree was planted',text)
        self.assertIn('editorial addition in accordance with Greek',note)
        self.assertIn('does not mean that every kind of vegetation was absent',note)
        self.assertFalse(d['source'].get('additional_translation_input'))
        self.assertEqual(d['source']['transcription_uncertainties'][0]['status'],'retained_with_dependency_disclosed')
        self.assertNotIn('impossible',text)

    def test_three_wonders_are_retained_not_collapsed_to_one(self):
        text=record(6)['translation']['text']
        self.assertEqual(text.count('marveled'),3);self.assertIn('marveled greatly',text)
        self.assertIn('at the rocks',text);self.assertIn('at the valley',text)

    def test_only_two_metadata_candidates_are_explicitly_superseded(self):
        m=t.load_manifest(P);old=t.APPLICATIONS/metadata.NAME;index=metadata.read_index()
        self.assertEqual(set(m['supersedes']),set(metadata.REFS))
        for ref,case in index['cases'].items():
            expected={'package':metadata.NAME,'manifest_sha256':t.sha((old/'manifest.json').read_bytes()),'candidate_sha256':index['files'][case['candidate']]}
            self.assertEqual(m['supersedes'][ref],expected)
            c,v=t.parse_ref(ref);self.assertEqual(m['canonical_baseline_sha256'][f'{c:03d}/{v:03d}.yaml'],expected['candidate_sha256'])
        result=metadata.verify_current(old)
        self.assertEqual(result['reviewed_supersessions'],[{'reference':r,'superseded_by':P.name}for r in metadata.REFS])
        self.assertEqual(result['new_full_source_English_reviews'],0)
        self.assertEqual(result['historical_payloads']['1 Enoch 26:5']['historical_full_final_payload_accepting_passes'],[1,2])
        self.assertEqual(result['historical_payloads']['1 Enoch 26:6']['historical_full_final_payload_accepting_passes'],[2])
        with self.assertRaisesRegex(ValueError,'current canonical target differs'):metadata.verify(applied=True)

    def test_unapproved_four_is_unchanged_and_fullsix_count_is_only_structural(self):
        m=t.load_manifest(P);r=json.loads((P/'application.json').read_text())
        self.assertEqual([x['reference']for x in m['not_applied']],['1 Enoch 26:4'])
        self.assertEqual(r['canonical_after_sha256']['026/004.yaml'],m['canonical_baseline_sha256']['026/004.yaml'])
        self.assertEqual(t.sha((t.TRANSLATION/'026/004.yaml').read_bytes()),m['canonical_baseline_sha256']['026/004.yaml'])
        self.assertFalse((P/'026-004.candidate.yaml').exists())
        certificate=m['source_only_count_inventories'][0]
        self.assertEqual(certificate['chapter'],26);self.assertEqual(certificate['units'],list(range(1,7)))
        self.assertTrue(certificate['independent_count_confirmation'])
        data=json.loads((P/certificate['artifact']).read_text())
        self.assertFalse(data['wording_approval']);self.assertFalse(data['reader_release_policy_changed'])
        self.assertEqual(data['chapters'][0]['unit_pdf_pages']['4'],[102,104])

    def test_partial_source_registration_retires_old_metadata_overlay_without_echo(self):
        from tools.enoch.selected_edition_sources import registry_data,load_unit_overrides
        registry=registry_data();self.assertNotIn('26',registry['chapters']);self.assertEqual(registry['metadata_units'],{})
        rows={r['verse']:r for r in load_unit_overrides(26)}
        self.assertEqual(set(rows),set(VERSES))
        original={t.parse_ref(r['reference'])[1]:r['source']for r in json.loads((P/'final/ch26-full/review-input.json').read_text())}
        for v in VERSES:
            self.assertEqual(registry['units'][f'26:{v}'],P.name)
            self.assertEqual(rows[v]['source'],original[v]);self.assertIn(P.name+'/final/',rows[v]['evidence'])
        self.assertFalse(metadata.current_units())

    def test_exact_notes_source_controls_and_critical_brackets_survive_export(self):
        for v in VERSES:
            d=record(v);out=reader._export_record_verse(v,d)
            self.assertEqual(out['text'],d['translation']['text']);self.assertEqual(out['footnotes'],d['translation']['footnotes'])
            self.assertEqual(out['footnote_review'],reader.PROTOCOL)
            for key in('edition','language','text','pages','note','confidence','transcription_uncertainties','additional_translation_input'):
                if key in d['source']:self.assertEqual(out['source_critical'][key],d['source'][key])
            bundle=build_enoch_prompt(26,v)
            for key in('text','confidence','transcription_uncertainties','additional_translation_input'):
                if key in d['source']:self.assertEqual(bundle.source_payload[key],d['source'][key])
        self.assertIn('[moist]',reader._export_record_verse(1,record(1))['text'])
        self.assertIn('[was]',reader._export_record_verse(3,record(3))['text'])

    def test_no_reader_chapter_or_unrelated_export_change_and_legacy_exporter_unchanged(self):
        m=t.load_manifest(P)
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory);before=root/'1_enoch';shutil.copytree(t.TRANSLATION,before)
            for v in VERSES:
                rel=f'026/{v:03d}.yaml';blob=m['baseline_git_blobs'][rel]['blob'];(before/rel).write_bytes(subprocess.check_output(['git','cat-file','blob',blob],cwd=t.ROOT))
            with patch.object(reader,'EXTRA_CANONICAL_ROOT',root):old=reader.export_extra_canonical_book('ENO')
            new=reader.export_extra_canonical_book('ENO')
        a={c['chapter']:c for c in old['chapters']};b={c['chapter']:c for c in new['chapters']}
        self.assertEqual(set(a),set(b));self.assertEqual({c:x for c,x in a.items()if c!=26},{c:x for c,x in b.items()if c!=26})
        self.assertEqual([v['verse']for v in a[26]['verses']],[v['verse']for v in b[26]['verses']])
        self.assertEqual(hashlib.sha256((t.ROOT/'tools/export_mobile_bible.py').read_bytes()).hexdigest(),'2258f72485099fe1014152eeb29394324415940467c2edd9d9da0d48a4a113c3')

    def test_rehashed_shade_or_positive_negative_clause_is_rejected(self):
        for v in(1,5):
            with self.subTest(verse=v),tempfile.TemporaryDirectory()as directory:
                target=Path(directory)/'package';shutil.copytree(P,target);p=target/f'026-{v:03d}.candidate.yaml';d=yaml.load(p.read_bytes(),Loader=t.LOADER)
                d['translation']['text']=d['translation']['text'].replace('[moist]','[shaded]')if v==1 else d['translation']['text'].replace('no tree was planted','a tree was planted')
                p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False));m=json.loads((target/'manifest.json').read_text());m['files'][p.name]=t.sha(p.read_bytes());(target/'manifest.json').write_text(json.dumps(m))
                with self.assertRaises(ValueError):t.verify(target,evidence_only=True)

    def test_progress_and_review_scope_do_not_certify_held_chapter_or_ancient_original(self):
        from tools.enoch.full_repair_progress import build
        p=build();self.assertEqual(p['evidence_inventory_warnings'],[])
        self.assertGreaterEqual(p['current_units_with_imported_review_evidence'],470)
        self.assertNotIn(26,p['chapters_with_complete_imported_selected_edition_review']);self.assertFalse(p['completion_proven'])
        for v in VERSES:
            flags=record(v)['source_correction'];self.assertTrue(flags['individual_unit_application_approved'])
            for key in('selected_edition_chapter_reviewed','chapter_publication_approval','full_book_verified','human_specialist_certification','manuscript_witness_certification','graphic_publication_approved'):self.assertFalse(flags[key])
            self.assertEqual(record(v)['ai_draft']['model_id'],'not_reported')

    def test_workflow_fetches_actual_latest_main_baseline_and_runs_new_gate(self):
        text=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn('git fetch --no-tags --depth=1 origin ee2a89b5e46db917b59bfa891e127d6bf98f5cfc',text)
        self.assertIn("python -m unittest discover -s tests -p 'test_enoch_full_repair_batch22.py'",text)


if __name__=='__main__':unittest.main()
