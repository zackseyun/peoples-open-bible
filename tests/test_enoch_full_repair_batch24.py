"""Three complete33 units, a real bird-descriptor hold and no fake star count."""
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

P=t.APPLICATIONS/'enoch_full_repair_batch24_20261024'
VERSES=(2,3,4)
REFS=[f'1 Enoch 33:{v}'for v in VERSES]
MANIFEST='00593b37466d11106c8e51a2c4b72563ee944ab30afe9c36768525d3831dbcc1'


def record(v):return yaml.load((t.TRANSLATION/f'033/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)


class FullRepairBatch24Test(unittest.TestCase):
    def test_three_existing_exact_units_and_full964_postmap(self):
        self.assertEqual(t.sha((P/'manifest.json').read_bytes()),MANIFEST)
        m=t.load_manifest(P);r=json.loads((P/'application.json').read_text())
        self.assertEqual(verify_current(P)['references'],REFS)
        self.assertEqual(m['source_baseline_git_commit'],'2a97703af3931e95c09811cda6a9cfbe003b3916')
        prior=json.loads((t.APPLICATIONS/'enoch_full_repair_batch23_20261024/application.json').read_text())
        self.assertEqual(m['canonical_baseline_sha256'],prior['canonical_after_sha256'])
        expected=dict(m['canonical_baseline_sha256'])
        for v in VERSES:
            rel=f'033/{v:03d}.yaml';expected[rel]=t.sha((P/f'033-{v:03d}.candidate.yaml').read_bytes())
            self.assertEqual(t.sha((t.TRANSLATION/rel).read_bytes()),expected[rel])
        self.assertEqual(r['canonical_after_sha256'],expected);self.assertEqual(r['snapshot_file_count'],964)
        self.assertEqual(m['retirements'],[]);self.assertEqual(m['supersedes'],{})

    def test_original_fullfour_pair_accepts_three_and_holds_one(self):
        m=t.load_manifest(P);p=P/'final/ch33-full/review-input.json'
        self.assertEqual(t.sha(p.read_bytes()),'1ba33620057656726b20851d465edf6a29904033f8858d63b2708527e30448ec')
        self.assertEqual([r['reference']for r in json.loads(p.read_text())],[f'1 Enoch 33:{v}'for v in range(1,5)])
        for b in m['review_bindings'][REFS[0]]:
            for ref in REFS:t.review_row(P,b,ref,m['files'])
            rows=t.review_entries(json.loads((P/b['review']).read_text()))
            self.assertEqual([(r['reference'],r['verdict'])for r in rows],[(f'1 Enoch 33:{v}','hold'if v==1 else'accept')for v in range(1,5)])
            with self.assertRaises(ValueError):t.review_row(P,b,'1 Enoch 33:1',m['files'])

    def test_east_and_derived_intransitive_rest_have_exact_qualified_controls(self):
        d=record(2);s=d['source'];text=d['translation']['text'];note=d['translation']['footnotes'][0]['text']
        self.assertIn('To the east of these beasts',text);self.assertIn('where heaven comes to rest',text)
        self.assertIn('open gates of heaven',text);self.assertEqual(s['confidence'],'low')
        self.assertIn('970',note);self.assertIn('does not assert that every derived form is intransitive',note)
        self.assertEqual(s['transcription_uncertainties'][0]['status'],'intransitive_rest_range_selected_and_qualified')
        self.assertFalse(s.get('additional_translation_input'))

    def test_how_and_full_gate_count_clause_not_an_unprinted_mouth_opening(self):
        d=record(3);s=d['source'];text=d['translation']['text']
        self.assertIn('እፎ፡',s['text']);self.assertIn('ወኍልቁ፡',s['text'])
        self.assertIn('how the stars of heaven come out',text)
        self.assertIn('the number of the gates from which they come out',text)
        self.assertNotIn('mouth',text);self.assertNotIn('portal',text)
        self.assertIn('806–807',d['translation']['footnotes'][0]['text'])

    def test_real_doubled_one_star_and_no_apparatus_31_in_source(self):
        d=record(3);s=d['source']['text'];note=d['translation']['footnotes'][0]['text']
        self.assertIn('ለለ*፩፩፡',s);self.assertIn('በኍልቆሙ፡',s)
        self.assertNotIn('*በኍልቆሙ',s);self.assertNotIn('31',s)
        self.assertIn('raised apparatus number31',note)
        self.assertIn('one by one',d['translation']['text'])

    def test_every_list_member_and_selected_name_remain_without_new_catalogue(self):
        d=record(3);text=d['translation']['text']
        for phrase in('number and names','ranks, activity, times and months','Urel, the holy angel who was with me'):self.assertIn(phrase,text)
        self.assertIn('ኡርኤል',d['source']['text'])
        for extra in('year','season','constellation','catalogue'):self.assertNotIn(extra,text)

    def test_firstperson_writing_three_vs_thirdperson_four_and_both_clauses(self):
        a=record(3);b=record(4)
        self.assertIn('ወጸሐፍኩ፡',a['source']['text']);self.assertIn('I wrote down',a['translation']['text'])
        self.assertIn('ወጸሐፈ፡',b['source']['text']);self.assertIn('*ጸሐፈ፡',b['source']['text'])
        self.assertIn('He showed me everything and wrote it down for me',b['translation']['text'])
        self.assertIn('Again he wrote down for me',b['translation']['text'])
        self.assertIn('their names, their commands and their groupings',b['translation']['text'])

    def test_one_hold_and_four_structural_addresses_do_not_complete_chapter(self):
        m=t.load_manifest(P);r=json.loads((P/'application.json').read_text())
        self.assertEqual([x['reference']for x in m['not_applied']],['1 Enoch 33:1'])
        self.assertEqual(r['canonical_after_sha256']['033/001.yaml'],m['canonical_baseline_sha256']['033/001.yaml'])
        self.assertEqual(t.sha((t.TRANSLATION/'033/001.yaml').read_bytes()),m['canonical_baseline_sha256']['033/001.yaml'])
        self.assertFalse((P/'033-001.candidate.yaml').exists());self.assertEqual(m['chapter_inventories'],[])
        c=m['source_only_count_inventories'][0];self.assertEqual(c['units'],list(range(1,5)));self.assertTrue(c['independent_count_confirmation'])
        d=json.loads((P/c['artifact']).read_text());self.assertFalse(d['wording_approval']);self.assertFalse(d['reader_release_policy_changed'])

    def test_exact_explanations_source_controls_and_prompt_ingress(self):
        from tools.enoch.selected_edition_sources import registry_data,load_unit_overrides
        registry=registry_data();self.assertNotIn('33',registry['chapters'])
        self.assertEqual([r['verse']for r in load_unit_overrides(33)],[2,3,4])
        for v in VERSES:
            self.assertEqual(registry['units'][f'33:{v}'],P.name)
            d=record(v);out=reader._export_record_verse(v,d);prompt=build_enoch_prompt(33,v)
            self.assertEqual(out['footnotes'],d['translation']['footnotes']);self.assertEqual(out['text'],d['translation']['text']);self.assertEqual(out['footnote_review'],reader.PROTOCOL)
            for key in('text','pages','confidence','transcription_uncertainties','additional_translation_input'):
                if key in d['source']:self.assertEqual(out['source_critical'][key],d['source'][key]);self.assertEqual(prompt.source_payload[key],d['source'][key])
        self.assertNotIn('33:1',registry['units'])

    def test_rehashed_lost_count_or_changed_writer_does_not_get_approval(self):
        for v in(3,4):
            with self.subTest(verse=v),tempfile.TemporaryDirectory()as directory:
                q=Path(directory)/'package';shutil.copytree(P,q);p=q/f'033-{v:03d}.candidate.yaml';d=yaml.load(p.read_bytes(),Loader=t.LOADER)
                d['translation']['text']=d['translation']['text'].replace('and the number of the gates from which they come out.','')if v==3 else d['translation']['text'].replace('he wrote','I wrote')
                p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False));m=json.loads((q/'manifest.json').read_text());m['files'][p.name]=t.sha(p.read_bytes());(q/'manifest.json').write_text(json.dumps(m))
                with self.assertRaises(ValueError):t.verify(q,evidence_only=True)

    def test_no_reader_chapter_or_unrelated_export_change(self):
        m=t.load_manifest(P)
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory);before=root/'1_enoch';shutil.copytree(t.TRANSLATION,before)
            for v in VERSES:
                rel=f'033/{v:03d}.yaml';(before/rel).write_bytes(subprocess.check_output(['git','cat-file','blob',m['baseline_git_blobs'][rel]['blob']],cwd=t.ROOT))
            with patch.object(reader,'EXTRA_CANONICAL_ROOT',root):old=reader.export_extra_canonical_book('ENO')
            new=reader.export_extra_canonical_book('ENO')
        a={c['chapter']:c for c in old['chapters']};b={c['chapter']:c for c in new['chapters']};self.assertEqual(set(a),set(b))
        self.assertEqual({c:v for c,v in a.items()if c!=33},{c:v for c,v in b.items()if c!=33})

    def test_progress_and_provenance_scope_do_not_certify_the_book(self):
        from tools.enoch.full_repair_progress import build
        p=build();self.assertGreaterEqual(p['current_units_with_imported_review_evidence'],474)
        self.assertEqual(p['evidence_inventory_warnings'],[]);self.assertNotIn(33,p['chapters_with_complete_imported_selected_edition_review']);self.assertFalse(p['completion_proven'])
        for v in VERSES:
            d=record(v);self.assertEqual(d['ai_draft']['model_id'],'not_reported')
            for key in('selected_edition_chapter_reviewed','chapter_publication_approval','full_book_verified','human_specialist_certification','manuscript_witness_certification','graphic_publication_approved'):self.assertFalse(d['source_correction'][key])


if __name__=='__main__':unittest.main()
