"""The ending count is source-only;107context is not a new English pass."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from tools.enoch import bounded_application as t, count106_108_evidence as counts


class EndingCountEvidenceTest(unittest.TestCase):
    def test_registers_only_two_new_counts_with_three_exact_context_chapters(self):
        result=counts.load();self.assertEqual({c:len(r['units'])for c,r in result.items()},{106:19,108:15})
        self.assertNotIn(107,result)
        d,_=counts.evidence();self.assertEqual(d['counts'],{'106':19,'107':3,'108':15})
        self.assertEqual(len(d['unit_pages']),37)
        self.assertFalse(d['wording_approval']);self.assertEqual(d['canonical_English_votes_imported'],0)

    def test_crosspage_tails_and_book_end_are_source_observations(self):
        d,_=counts.evidence();spans=d['unit_pages']
        for key,pages in {'106:2':[257,258],'106:9':[258,259],'106:14':[259,260],'107:1':[260,261],'108:3':[261,262],'108:7':[262,263],'108:11':[263,264]}.items():self.assertEqual(spans[key],pages)
        self.assertEqual(spans['108:15'],[264]);self.assertNotIn('108:16',spans)
        result=json.loads((t.ROOT/d['artifact_prefix']/'raw-model-text.json').read_text())
        self.assertIn('book-ending colophon',result['excluded_material'])
        self.assertIn('parallel Latin column',result['excluded_material'])
        self.assertFalse(result['wording_approved']);self.assertFalse(result['publication_approved'])

    def test_two_windows_are_exact_successor_to_prior_three_window_map(self):
        d,after=counts.evidence();prefix=t.ROOT/d['artifact_prefix']
        proof=json.loads((prefix/'page-map-application-proof.json').read_text())
        self.assertEqual(proof['before_sha256'],'51235ca99c57e611b7c9ed9e653ea84390b2d87c724aab6d0b271a4600b33c76')
        self.assertEqual(proof['after_sha256'],'a51746556e1547198177d8c82ba4787bbf089aac0cb600d4f61e3992b2647880')
        self.assertEqual([r['json_path']for r in proof['changes']],[f'$.editions.charles_1906.chapters.{c}.pages'for c in('106','107')])
        self.assertEqual(after['editions']['charles_1906']['chapters']['106']['pages'],[257,258,259,260])
        self.assertEqual(after['editions']['charles_1906']['chapters']['107']['pages'],[260,261])
        self.assertEqual(counts.window_successor(proof['before_sha256']),proof['after_sha256'])
        with self.assertRaisesRegex(ValueError,'different predecessor'):counts.window_successor('0'*64)
        self.assertTrue(counts.verify_current_windows())
        from tools.enoch.count41_44_evidence import verify_current_windows
        self.assertTrue(verify_current_windows())

    def test_structural_progress_does_not_promote106_108_or_reapprove107(self):
        from tools.enoch.structural_counts import load_all_inventories
        inv=load_all_inventories()
        self.assertEqual(inv[106]['units'],list(range(1,20)));self.assertEqual(inv[108]['units'],list(range(1,16)))
        self.assertNotIn(107,inv)  # Original107language certificate is merged later, not recast as this profile.
        original=t.load_manifest(t.APPLICATIONS/'enoch_full_repair_batch04_20261020')
        self.assertEqual(next(c for c in original['chapter_inventories']if c['chapter']==107)['units'],[1,2,3])
        from tools.enoch.full_repair_progress import build
        report=build();self.assertEqual(report['evidence_inventory_warnings'],[])
        self.assertIn(107,report['chapters_with_complete_imported_selected_edition_review'])
        for c in(106,108):self.assertNotIn(c,report['chapters_with_complete_imported_selected_edition_review'])
        self.assertFalse(report['completion_proven']);self.assertFalse(report['artwork_publication_approval'])

    def test_actual_completed_provider_id_usage_and_request_images(self):
        d,_=counts.evidence();prefix=t.ROOT/d['artifact_prefix']
        response=json.loads((prefix/'provider-terminal-response.json').read_text())
        self.assertEqual(response['id'],'resp_0089cd11ad8cf9ad006adbff33ba0481959dad2fc1375e2297')
        self.assertEqual(response['status'],'completed');self.assertEqual(response['model'],'gpt-6-1-sol-review')
        self.assertEqual(response['usage']['total_tokens'],11746)
        request=json.loads((prefix/'request-with-image-hashes.json').read_text())
        self.assertTrue(request['no_expected_count_or_author_candidate_supplied'])
        self.assertNotIn('image_url',json.dumps(request))
        self.assertEqual(sum(r['type']=='input_image'for r in request['request_projection']['input'][0]['content']),10)

    def test_drifted_count_artifact_or_index_is_rejected(self):
        d,_=counts.evidence()
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory)
            for name in(counts.INDEX,*d['files']):
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(t.ROOT/name,p)
            target=root/d['artifact_prefix']/'raw-model-text.json';target.write_bytes(target.read_bytes()+b'\n')
            with patch.object(t,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'original count artifact differs'):counts.load()
            index=root/counts.INDEX;index.write_bytes(index.read_bytes()+b'\n')
            with patch.object(t,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'fixed structural count index differs'):counts.load()

    def test_other_unreviewed_map_changes_still_fail_closed(self):
        real=t.artifact
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory)/'map.json';d=json.loads((t.ROOT/counts.PATH).read_text());d['updated']='not-reviewed';p.write_text(json.dumps(d))
            with patch.object(t,'artifact',side_effect=lambda root,path:p if path==counts.PATH else real(root,path)):
                with self.assertRaisesRegex(ValueError,'explicit reviewed window successor'):counts.verify_current_windows()

    def test_workflow_fetches_actual_noncanonical_checkpoint_and_runs_test(self):
        workflow=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn('git fetch --no-tags --depth=1 origin '+counts.BASE,workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_enoch_count106_108_evidence.py'",workflow)
