"""Whole35 selected-print critical treatment;30/31 count-only holds remain."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import yaml
from tools.enoch import bounded_application as t, short_watchers_counts as counts
from tools.enoch.current_evidence import verify_current
from tools.enoch.build_translation_prompt import build_enoch_prompt
from tools import export_reader_bible as reader

P=t.APPLICATIONS/'enoch_full_repair_batch16_20261023'


class FullRepairBatch16Test(unittest.TestCase):
    def test_exact_whole35_one_unit_and_full_historical_application_map(self):
        result=verify_current(P);m=t.load_manifest(P);r=json.loads((P/'application.json').read_text())
        self.assertEqual(result['references'],['1 Enoch 35:1']);self.assertEqual(result['candidate_files'],1)
        self.assertEqual(m['retirements'],[]);self.assertEqual(r['snapshot_file_count'],962)
        expected=dict(m['canonical_baseline_sha256']);expected['035/001.yaml']=t.sha((P/'035-001.candidate.yaml').read_bytes())
        self.assertEqual(r['canonical_after_sha256'],expected)
        self.assertEqual(t.sha((t.TRANSLATION/'035/001.yaml').read_bytes()),expected['035/001.yaml'])
        self.assertTrue(r['unrelated_canonical_files_unchanged_at_application'])
        self.assertEqual([(c['chapter'],c['units'])for c in m['chapter_inventories']],[(35,[1])])
        self.assertEqual(m['source_only_count_inventories'],[])
        holds={f'1 Enoch {c}:{v}'for c in(30,31)for v in(1,2,3)}
        self.assertEqual({r['reference']for r in m['not_applied']},holds)
        for ref in holds:
            c,v=t.parse_ref(ref);rel=f'{c:03d}/{v:03d}.yaml'
            self.assertEqual(r['canonical_after_sha256'][rel],m['canonical_baseline_sha256'][rel])
            self.assertEqual(t.sha((t.TRANSLATION/rel).read_bytes()),m['canonical_baseline_sha256'][rel])

    def test_selected_east_not_silent_north_and_correct_gate_outlet_forms(self):
        d=yaml.load((t.TRANSLATION/'035/001.yaml').read_bytes(),Loader=t.LOADER)
        self.assertIn('በምሥራቅ',d['source']['text']);self.assertIn('ኆኃተ፡ ሰማይ',d['source']['text'])
        self.assertIn('በእመጠነ፡ ኆኃት',d['source']['text']);self.assertTrue(d['source']['text'].endswith('ሞፅአት።'))
        self.assertNotIn('*',d['source']['text']);self.assertEqual(d['source']['confidence'],'low')
        self.assertEqual(d['source']['pages'],[113]);self.assertEqual(d['source']['additional_translation_input'],[])
        self.assertIn('as I had seen in the east',d['translation']['text']);self.assertNotIn('north',d['translation']['text'])
        self.assertIn('three open gates',d['translation']['text']);self.assertIn('as many gates and as many outlets',d['translation']['text'])
        self.assertNotIn('springs',d['translation']['text']);self.assertNotIn('winds',d['translation']['text'])
        self.assertTrue(d['source']['transcription_uncertainties'])
        self.assertIn('corrupt',d['translation']['footnotes'][0]['text'])
        self.assertIn('not silently harmonized',d['translation']['footnotes'][0]['text'])
        self.assertTrue(d['source_correction']['selected_edition_chapter_reviewed'])
        self.assertFalse(d['source_correction']['chapter_publication_approval'])
        self.assertFalse(d['source_correction']['graphic_publication_approved'])

    def test_count_only30_31_35_never_promotes_held_english_or_release_policy(self):
        inventories=counts.load();self.assertEqual({c:len(r['units'])for c,r in inventories.items()},{30:3,31:3,35:1})
        self.assertTrue(all(r['wording_approval']is False and r['reader_release_policy_changed']is False for r in inventories.values()))
        from tools.enoch.full_repair_progress import build
        report=build();self.assertEqual(report['evidence_inventory_warnings'],[])
        self.assertIn(35,report['chapters_with_complete_imported_selected_edition_review'])
        for c in(30,31):self.assertNotIn(c,report['chapters_with_complete_imported_selected_edition_review'])
        self.assertFalse(report['completion_proven']);self.assertFalse(report['artwork_publication_approval'])
        from tools.enoch.selected_edition_sources import registry_data,load_chapter
        registry=registry_data();self.assertEqual(registry['chapters']['35'],P.name)
        self.assertEqual([r['verse']for r in load_chapter(35)],[1])
        self.assertNotIn('30',registry['chapters']);self.assertNotIn('31',registry['chapters'])

    def test_count_artifact_or_scope_drift_fails_closed(self):
        index=t.ROOT/counts.INDEX;data=json.loads(index.read_text())
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory)
            for name in(counts.INDEX,*data['files']):
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(t.ROOT/name,p)
            target=root/data['source_input'];target.write_bytes(target.read_bytes()+b'\n')
            with patch.object(t,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'count artifact differs'):counts.load()
            p=root/counts.INDEX;p.write_bytes(p.read_bytes()+b'\n')
            with patch.object(t,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'fixed count index differs'):counts.load()

    def test_exact_explanations_and_controls_survive_export_and_prompt(self):
        d=yaml.load((t.TRANSLATION/'035/001.yaml').read_bytes(),Loader=t.LOADER)
        book=reader.export_extra_canonical_book('ENO');c=next(c for c in book['chapters']if c['chapter']==35)
        self.assertEqual([v['verse']for v in c['verses']],[1]);v=c['verses'][0]
        self.assertEqual(v['footnotes'],d['translation']['footnotes']);self.assertEqual(v['footnote_review'],'pob-enoch-paired-source-review-v1')
        for key in('text','pages','note','confidence','additional_translation_input','transcription_uncertainties'):
            self.assertEqual(v['source_critical'][key],d['source'][key])
        self.assertEqual(build_enoch_prompt(35,1).source_payload['transcription_uncertainties'],d['source']['transcription_uncertainties'])

    def test_six_held_inputs_are_not_partial_source_approvals(self):
        m=t.load_manifest(P);bindings=m['review_bindings']['1 Enoch 35:1']
        for c in(30,31):
            for v in(1,2,3):
                for binding in bindings:
                    with self.assertRaisesRegex(ValueError,'not accepted'):t.review_row(P,binding,f'1 Enoch {c}:{v}',m['files'])
        peer=json.loads((P/'final/ch30-31-35/independent-provenance.json').read_text())
        self.assertEqual(peer['reviewer_id'],'/root');self.assertEqual(len(peer['scan_image_sha256']),50)
        self.assertFalse(peer['fresh_full30_31_language_approval'])
        self.assertEqual(peer['whole_unit_accepts'],['1 Enoch 35:1'])
        self.assertFalse(json.loads((P/'explanation-delivery-gate.json').read_text())['candidate_public_delivery_verified'])
