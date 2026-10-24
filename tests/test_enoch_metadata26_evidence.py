"""Inherited26 full payloads and a narrow, truthful schema/control successor."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t, metadata26_evidence as m
from tools import export_reader_bible as reader
from tools.enoch.build_translation_prompt import build_enoch_prompt


class Metadata26Test(unittest.TestCase):
    def assert_exact_language_successor(self,ref):
        successor=t.APPLICATIONS/'enoch_full_repair_batch22_20261024'
        self.assertEqual(t.sha((successor/'manifest.json').read_bytes()),'74d1340efb155ac8a266f751c49f212f1ecae8d915fd107dc03b933b4f08470b')
        manifest=t.load_manifest(successor);case=m.read_index()['cases'][ref]
        self.assertEqual(manifest['supersedes'][ref],{'package':m.NAME,'manifest_sha256':t.sha((t.APPLICATIONS/m.NAME/'manifest.json').read_bytes()),'candidate_sha256':m.read_index()['files'][case['candidate']]})
        c,v=t.parse_ref(ref);rel=f'{c:03d}/{v:03d}.yaml'
        self.assertEqual(manifest['canonical_baseline_sha256'][rel],m.read_index()['files'][case['candidate']])
        self.assertEqual(t.sha((t.TRANSLATION/rel).read_bytes()),manifest['files'][f'{c:03d}-{v:03d}.candidate.yaml'])
        self.assertIn(ref,m.verify_current(t.APPLICATIONS/m.NAME)['references'])

    def test_actual_historical_full_payload_counts_not_new_metadata_language_votes(self):
        d=m.read_index();_,proofs=m._originals(d)
        self.assertEqual(proofs[m.REFS[0]]['historical_full_final_payload_accepting_passes'],[1,2])
        self.assertEqual(proofs[m.REFS[1]]['historical_full_final_payload_accepting_passes'],[2])
        for proof in proofs.values():
            self.assertEqual(proof['historical_execution_count'],2)
            self.assertEqual(proof['new_full_source_or_English_review_count'],0)
            self.assertTrue(proof['actual_parent_absence_verified'])
        for name in (*m.LEGACY,m.NAME):
            current=m.verify_current(t.APPLICATIONS/name)
            self.assertTrue(current['canonical_targets_checked'])
            self.assertEqual(current['new_full_source_English_reviews'],0)
            self.assertFalse(current['whole_chapter_approved'])
            self.assertFalse(current['graphic_publication_approved'])

    def test_every_source_semantic_field_and_entire_translation_remain_exact(self):
        d=m.read_index();old,_=m._originals(d);result=m.verify(check_targets=False,applied=True)
        for ref,case in d['cases'].items():
            # Exact metadata-only claims belong to the historical applied
            # candidate; current language changes need their own paired proof.
            c,v=t.parse_ref(ref);current=yaml.load(t.artifact(t.ROOT,case['candidate']).read_bytes(),Loader=t.LOADER)
            self.assert_exact_language_successor(ref)
            self.assertEqual(current['translation'],old[ref]['translation'])
            for key in ('text','edition','language','pages','confidence','validation'):
                self.assertEqual(current['source'][key],old[ref]['source'][key])
            self.assertNotIn('additional_translation_input',current['source'])
            self.assertNotIn('additional_translation_input',old[ref]['source'])
            self.assertEqual(old[ref]['status'],'revised')
            self.assertEqual(current['status'],'draft')
            self.assertEqual(current['cross_check']['status'],'needs_review')
            self.assertEqual(current['ai_draft']['model_id'],'not_reported')
            self.assertEqual(current['ai_draft']['model_version'],'not_reported')
            self.assertEqual(current['source'],result['metadata_candidate_source'][ref])
            if v==5:
                self.assertEqual(old[ref]['cross_check']['reviewer_model'],'gpt-6-astra')
                self.assertEqual(current['cross_check']['reviewer_model'],'gpt-6.1-sol')
                self.assertEqual(current['cross_check']['final_full_payload_accept_count'],2)
                self.assertEqual(len(current['source']['transcription_uncertainties']),1)
                self.assertIn('intrinsic_textual_difficulty',current['source']['transcription_uncertainties'][0]['kind'])
                self.assertIn('does not newly adopt',current['source']['note'])
            else:
                self.assertEqual(current['cross_check']['pass_count'],2)
                self.assertEqual(current['cross_check']['final_full_payload_accept_count'],1)
                self.assertEqual(current['cross_check']['final_full_payload_accepted_passes'],[2])
                self.assertNotIn('transcription_uncertainties',current['source'])
            self.assertEqual(current['cross_check']['fresh_full_source_accept_count_from_metadata_successor'],0)

    def test_historical_postmap_retains_all962_bounded_preimages(self):
        p=t.APPLICATIONS/m.NAME;manifest=json.loads((p/'manifest.json').read_text());receipt=json.loads((p/'application.json').read_text())
        expected=dict(manifest['canonical_baseline_sha256']);self.assertEqual(len(expected),962)
        for ref,case in m.read_index()['cases'].items():expected['%03d/%03d.yaml'%t.parse_ref(ref)]=m.read_index()['files'][case['candidate']]
        self.assertEqual(expected,receipt['canonical_after_sha256'])
        self.assertTrue(receipt['unrelated_canonical_files_unchanged_at_application'])
        self.assertEqual(receipt['new_full_source_English_reviews'],0)

    def test_exact_source_controls_notes_and_provenance_survive_ingress_and_export(self):
        from tools.enoch.selected_edition_sources import load_unit_overrides
        override={r['verse']:r for r in load_unit_overrides(26)}
        book=reader.export_extra_canonical_book('ENO');public={v['verse']:v for c in book['chapters']if c['chapter']==26 for v in c['verses']}
        for v in(5,6):
            d=yaml.load((t.TRANSLATION/f'026/{v:03d}.yaml').read_bytes(),Loader=t.LOADER)
            self.assert_exact_language_successor(f'1 Enoch 26:{v}')
            self.assertIn('enoch_full_repair_batch22_20261024/final/',override[v]['evidence'])
            for key in('text','language','pages','confidence','transcription_uncertainties','additional_translation_input'):
                if key in d['source']:self.assertEqual(override[v]['source'].get(key),d['source'][key])
            historical={r['verse']:r for r in m.source_overrides(26)}
            self.assertIn('metadata-delta-on-exact-historical-payload',historical[v]['evidence'])
            self.assertEqual(historical[v]['source'],m.verify(check_targets=False,applied=True)['metadata_candidate_source'][f'1 Enoch 26:{v}'])
            self.assertEqual(public[v]['footnotes'],d['translation']['footnotes'])
            self.assertEqual(public[v]['source_critical']['note'],d['source']['note'])
            if v==5:
                self.assertEqual(public[v]['source_critical']['transcription_uncertainties'],d['source']['transcription_uncertainties'])
                self.assertEqual(build_enoch_prompt(26,v).source_payload['transcription_uncertainties'],d['source']['transcription_uncertainties'])

    def test_raw_dependency_drift_and_index_scope_change_fail_closed(self):
        d=m.read_index()
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory)
            for name in (m.INDEX,*d['files']):
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(t.ROOT/name,p)
            name=next(x for x in d['files']if x.endswith('review-pass1/review.json'))
            p=root/name;p.write_bytes(p.read_bytes()+b'\n')
            with patch.object(t,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'immutable artifact differs'):m.read_index()
            index=root/m.INDEX;index.write_bytes(index.read_bytes()+b'\n')
            with patch.object(t,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'frozen evidence index differs'):m.read_index()

    def test_arbitrary_current_edit_is_not_approved_and_source_ingress_is_not_echo(self):
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory);shutil.copytree(t.TRANSLATION,root/'1_enoch');path=root/'1_enoch/026/005.yaml'
            raw=path.read_bytes();path.write_bytes(raw+b'\n# arbitrary unreviewed edit\n')
            with patch.object(t,'TRANSLATION',root/'1_enoch'):
                with self.assertRaisesRegex(ValueError,'current canonical target differs'):m.verify(applied=True)
                with self.assertRaises(ValueError):m.verify_current(t.APPLICATIONS/m.NAME)
                self.assertNotIn((26,5),m.current_units())
                rows=m.source_overrides(26);self.assertEqual(len(rows),2)
                self.assertNotIn('arbitrary unreviewed edit',str(rows))

    def test_repeat_apply_refuses_without_writing_anything(self):
        before=t.corpus_hashes()
        with self.assertRaisesRegex(ValueError,'already has an application receipt'):m.apply()
        self.assertEqual(before,t.corpus_hashes())
