"""Restore two missing exact units; no harmonization or approval of three holds."""
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

P=t.APPLICATIONS/'enoch_full_repair_batch21_20261024'
REFS=['1 Enoch 106:15','1 Enoch 106:16']
MANIFEST='17e614171b4c0cfaf8300f24852fc240dff7e327bd5a2a5a43eef7edbc2dc4aa'


def record(v):return yaml.load((t.TRANSLATION/f'106/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)


class FullRepairBatch21Test(unittest.TestCase):
    def test_two_real_additions_and_complete_preimage_postmap(self):
        self.assertEqual(t.sha((P/'manifest.json').read_bytes()),MANIFEST)
        m=t.load_manifest(P);r=json.loads((P/'application.json').read_text())
        self.assertEqual(verify_current(P)['references'],REFS)
        before=json.loads((t.APPLICATIONS/'enoch_full_repair_batch20_20261024/application.json').read_text())['canonical_after_sha256']
        self.assertEqual(m['canonical_baseline_sha256'],before);self.assertEqual(len(before),962)
        expected=dict(before)
        for v in(15,16):
            rel=f'106/{v:03d}.yaml';self.assertNotIn(rel,before)
            expected[rel]=t.sha((P/f'106-{v:03d}.candidate.yaml').read_bytes())
            self.assertEqual(t.sha((t.TRANSLATION/rel).read_bytes()),expected[rel])
        self.assertEqual(r['canonical_after_sha256'],expected);self.assertEqual(r['snapshot_file_count'],964)
        self.assertEqual(m['baseline_git_blobs'],{});self.assertEqual(m['supersedes'],{});self.assertEqual(m['retirements'],[])

    def test_actual_Git_absence_not_a_fictitious_previous_candidate(self):
        m=t.load_manifest(P)
        self.assertEqual(m['source_baseline_git_commit'],'b0f748df7a1809b81c7a213ee47dc3ed66cbff10')
        for v in(15,16):
            path=f'translation/extra_canonical/1_enoch/106/{v:03d}.yaml'
            self.assertNotEqual(subprocess.run(['git','cat-file','-e',m['source_baseline_git_commit']+':'+path],cwd=t.ROOT,capture_output=True).returncode,0)
            d=record(v);self.assertIsNone(d['source_correction']['baseline_sha256']);self.assertNotIn('review_history',d)

    def test_full5_exact_inputs_and_original_two_accepts_three_holds(self):
        m=t.load_manifest(P);p=P/'final/ch106-tail/review-input.json'
        self.assertEqual(t.sha(p.read_bytes()),'d8673210608363a7aff55b8a3b59731a073069c37e2b05a94d56d6e78b193da1')
        self.assertEqual([r['reference']for r in json.loads(p.read_text())],[f'1 Enoch 106:{v}'for v in range(15,20)])
        for binding in m['review_bindings'][REFS[0]]:
            for ref in REFS:t.review_row(P,binding,ref,m['files'])
            reviews=t.review_entries(json.loads((P/binding['review']).read_text()))
            self.assertEqual([(r['reference'],r['verdict'])for r in reviews],[(f'1 Enoch 106:{v}','accept'if v<17 else'hold')for v in range(15,20)])
            with self.assertRaises(ValueError):t.review_row(P,binding,'1 Enoch 106:17',m['files'])

    def test_one_year_repeated_destruction_and_visible_copula_not_Latin_duration(self):
        d=record(15);s=d['source'];text=d['translation']['text'];note=d['translation']['footnotes'][0]['text']
        self.assertIn('በ*አሐዱ፡ ዓመት',s['text']);self.assertEqual(s['text'].count('ሐጕለ'),2)
        self.assertEqual(text.count('great destruction'),1)  # First occurrence is sentence-initial Great.
        self.assertIn('Great destruction will come upon all the earth',text)
        self.assertIn('[there will be] great destruction in one year',text)
        for forbidden in('forty','40','Noah','God','sent'):self.assertNotIn(forbidden,text)
        self.assertIn('no Latin parallel',note);self.assertFalse(s.get('additional_translation_input'))

    def test_three_children_plural_you_and_repeated_survival_no_unprinted_names(self):
        d=record(16);text=d['translation']['text'];note=d['translation']['footnotes'][0]['text']
        self.assertIn('ሠለስቱ፡ ደቂቅ',d['source']['text'])
        self.assertIn('three children',text);self.assertEqual(text.count('will be saved'),2)
        self.assertIn('he and his children will be saved',text);self.assertIn('selected plural addressee',note)
        for name in('Noah','Shem','Ham','Japheth'):self.assertNotIn(name,text)
        self.assertFalse(d['source'].get('additional_translation_input'))

    def test_three_held_units_remain_absent_not_partially_installed(self):
        m=t.load_manifest(P);receipt=json.loads((P/'application.json').read_text())
        self.assertEqual([r['reference']for r in m['not_applied']],[f'1 Enoch 106:{v}'for v in(17,18,19)])
        for v in(17,18,19):
            rel=f'106/{v:03d}.yaml';self.assertNotIn(rel,receipt['canonical_after_sha256'])
            self.assertFalse((t.TRANSLATION/rel).exists())
            self.assertFalse((P/f'106-{v:03d}.candidate.yaml').exists())
        self.assertEqual(m['chapter_inventories'],[]);self.assertEqual(m['source_only_count_inventories'],[])
        self.assertFalse(json.loads((P/'scoped-tail-controls.json').read_text())['full19_language_certificate'])

    def test_source_controls_notes_and_critical_brackets_export_exactly(self):
        for v in(15,16):
            d=record(v);out=reader._export_record_verse(v,d)
            self.assertEqual(out['footnotes'],d['translation']['footnotes']);self.assertEqual(out['text'],d['translation']['text'])
            self.assertEqual(out['footnote_review'],reader.PROTOCOL)
            for k in('edition','language','text','pages','note','confidence','transcription_uncertainties','additional_translation_input'):
                if k in d['source']:self.assertEqual(out['source_critical'][k],d['source'][k])
            bundle=build_enoch_prompt(106,v)
            for k in('text','confidence','transcription_uncertainties','additional_translation_input'):
                if k in d['source']:self.assertEqual(bundle.source_payload[k],d['source'][k])
        self.assertIn('[there will be]',reader._export_record_verse(15,record(15))['text'])

    def test_partial_source_ingress_not_full106_or_new_reader_release_policy(self):
        registry=json.loads((t.ROOT/'sources/enoch/ethiopic/reviewed_source_registry.json').read_text())
        self.assertNotIn('106',registry['chapters'])
        for v in(15,16):self.assertEqual(registry['units'][f'106:{v}'],P.name)
        from tools.enoch.verse_parser import load_verse
        for v in(15,16):self.assertIn(P.name,load_verse(106,v)[0].chapter_file)
        self.assertEqual(reader._enoch_expected_verse_map()[106],list(range(1,20)))
        # This isolated reader exporter remains complete-chapter gated. The
        # separately published web compiler is verified by its own live receipt.
        self.assertNotIn(106,[c['chapter']for c in reader.export_extra_canonical_book('ENO')['chapters']])

    def test_separate_paired_count_is_required_not_inferred_from_five_targets(self):
        from tools.enoch.selected_edition_sources import load_unit_overrides
        from tools.enoch import count106_108_evidence
        self.assertEqual([r['verse']for r in load_unit_overrides(106)],[15,16])
        with patch.object(count106_108_evidence,'load',return_value={}):
            with self.assertRaisesRegex(ValueError,'declared printed count/address'):load_unit_overrides(106)

    def test_progress_adds_two_units_but_not_a_full106_chapter_certificate(self):
        from tools.enoch.full_repair_progress import build
        d=build();self.assertEqual(d['evidence_inventory_warnings'],[])
        self.assertGreaterEqual(d['current_units_with_imported_review_evidence'],467)
        self.assertGreaterEqual(d['canonical_file_count'],964)
        self.assertNotIn(106,d['chapters_with_complete_imported_selected_edition_review']);self.assertFalse(d['completion_proven'])
        self.assertEqual(next(c for c in d['chapters']if c['chapter']==106)['expected_units'],list(range(1,20)))

    def test_rehashed_wrong_quantity_or_extra_name_is_rejected(self):
        for v in(15,16):
            with self.subTest(verse=v),tempfile.TemporaryDirectory()as directory:
                target=Path(directory)/'package';shutil.copytree(P,target);p=target/f'106-{v:03d}.candidate.yaml'
                d=yaml.load(p.read_bytes(),Loader=t.LOADER)
                d['translation']['text']=d['translation']['text'].replace('one year','forty days') if v==15 else d['translation']['text']+' Noah'
                p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False));m=json.loads((target/'manifest.json').read_text());m['files'][p.name]=t.sha(p.read_bytes());(target/'manifest.json').write_text(json.dumps(m))
                with self.assertRaises(ValueError):t.verify(target,evidence_only=True)

    def test_no_provider_identity_or_whole_book_approval_invented(self):
        for v in(15,16):
            d=record(v);self.assertEqual(d['ai_draft']['model_id'],'not_reported')
            flags=d['source_correction'];self.assertTrue(flags['individual_unit_application_approved'])
            for k in('selected_edition_chapter_reviewed','chapter_publication_approval','full_book_verified','human_specialist_certification','manuscript_witness_certification','graphic_publication_approved'):self.assertFalse(flags[k])
        workflow=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn('git fetch --no-tags --depth=1 origin b0f748df7a1809b81c7a213ee47dc3ed66cbff10',workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_enoch_full_repair_batch21.py'",workflow)


if __name__=='__main__':unittest.main()
