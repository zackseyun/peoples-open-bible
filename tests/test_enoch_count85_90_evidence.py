"""All108 structural inventories, without treating any count as a translation."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.enoch import bounded_application as t
from tools.enoch import count85_90_evidence as evidence

class Count85To90EvidenceTest(unittest.TestCase):
    def test_exact_six_counts_all142_body_spans_and_actual_provider_receipts(self):
        d,_=evidence.evidence();self.assertEqual(evidence.COUNTS,{85:10,86:6,87:4,88:3,89:77,90:42});self.assertEqual(len(d['unit_pages']),142)
        self.assertEqual(d['registered_new_count_chapters'],list(range(85,91)));self.assertEqual(d['independent_count_actor_count'],2)
        self.assertEqual(sum(v[1]for v in evidence.JOBS.values()),40191)
        for r in evidence.load().values():self.assertFalse(r['wording_approval']);self.assertFalse(r['reader_release_policy_changed'])

    def test_Physical_Greek_interleaves_are_not_Ethiopic_body_pages(self):
        d,_=evidence.evidence();self.assertEqual(d['unit_pages']['89:48'],[212,214]);self.assertEqual(d['unit_pages']['89:57'],[214,216])
        self.assertFalse(any(p in(213,215)for pages in d['unit_pages'].values()for p in pages))
        prefix=d['artifact_prefix'];raw=json.loads(t.artifact(t.ROOT,prefix+'/author/author-inventory.json').read_text())
        c=next(c for c in raw['chapters']if c['chapter']==89)
        self.assertEqual(c['units'][47]['physical_pdf_pages_inclusive'],[212,213,214]);self.assertEqual(c['units'][56]['intervening_non_main_text_pdf_pages'],[215])

    def test_all_five_exact_window_repairs_and_no_unrelated_map_edits(self):
        d,after=evidence.evidence();before=json.loads(t.artifact(t.ROOT,d['artifact_prefix']+'/page-map-before.json').read_text());expected=copy.deepcopy(before)
        for c,pages in{53:[134,135],85:[201,202],88:[204,205],89:[205,206,207,208,209,210,211,212,214,216,217,218,219],90:list(range(219,228))}.items():
            expected['editions']['charles_1906']['chapters'][f'{c:03d}']['pages']=pages
        self.assertEqual(after,expected);self.assertTrue(evidence.verify_current_windows())
        self.assertEqual(t.sha(t.artifact(t.ROOT,evidence.PATH).read_bytes()),'dc672a5dacef5ddca28c354aef1c12dc57d779e88abcb3fbb8887e0ab98c1bd4')

    def test_entire_current_map_chain_remains_strict(self):
        from tools.enoch import count41_44_evidence,count106_108_evidence,count26_27_33_evidence
        for module in(count41_44_evidence,count106_108_evidence,count26_27_33_evidence):self.assertTrue(module.verify_current_windows())
        original=t.artifact
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory)/'map.json';m=json.loads(original(t.ROOT,evidence.PATH).read_text());m['editions']['charles_1906']['chapters']['001']['opening_hint']='unreviewed unrelated drift';p.write_text(json.dumps(m))
            def redirected(root,name):return p if str(name)==evidence.PATH else original(root,name)
            with patch.object(t,'artifact',side_effect=redirected):
                for module in(evidence,count41_44_evidence,count106_108_evidence,count26_27_33_evidence):
                    with self.assertRaisesRegex(ValueError,'explicit reviewed window successor'):module.verify_current_windows()

    def test_existing53_inventory_not_a_seventh_new_count_or_language_vote(self):
        d,_=evidence.evidence();self.assertEqual(d['context_only_window_chapter'],53);self.assertNotIn(53,evidence.load())
        p=json.loads(t.artifact(t.ROOT,d['artifact_prefix']+'/page-map-application-proof.json').read_text())
        self.assertEqual(p['new_count_inventories'],6);self.assertEqual(p['new_language_votes'],0);self.assertEqual(p['canonical_YAML_changes'],0)
        self.assertFalse(p['wording_approval']);self.assertFalse(p['reader_release_policy_changed'])

    def test_fixed_successor_rejects_wrong_predecessor(self):
        with self.assertRaisesRegex(ValueError,'different predecessor'):evidence.window_successor('0'*64)

    def test_progress_has108_counts_not108_complete_translation_chapters(self):
        from tools.enoch.full_repair_progress import build
        from tools.enoch.selected_edition_sources import registry_data
        r=build();self.assertEqual(r['chapters_with_imported_paired_count_inventory'],list(range(1,109)));self.assertEqual(r['canonical_file_count'],965)
        self.assertEqual(len(r['chapters_with_complete_imported_selected_edition_review']),36)
        registry=registry_data()
        for c in range(85,91):self.assertNotIn(str(c),registry['chapters'])
        self.assertEqual(r['evidence_inventory_warnings'],[])

    def test_rehashed_scope_does_not_turn_count_into_language_approval(self):
        self.assert_forged_rejected('index.json',lambda d:d.update(wording_approval=True),'source-only scope')

    def test_rehashed_body_projection_does_not_admit_Greek_page(self):
        self.assert_forged_rejected('index.json',lambda d:d['unit_pages']['89:48'].append(213),'main-body projection')

    def assert_forged_rejected(self,name,change,reason):
        d,_=evidence.evidence();prefix=d['artifact_prefix']+'/';original=t.artifact
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory)/name;v=json.loads(original(t.ROOT,prefix+name).read_text());change(v);p.write_text(json.dumps(v,indent=2)+'\n')
            def redirected(root,path):return p if str(path)==prefix+name else original(root,path)
            with patch.object(t,'artifact',side_effect=redirected),patch.object(evidence,'INDEX_SHA',t.sha(p.read_bytes())):
                with self.assertRaisesRegex(ValueError,reason):evidence.evidence()
