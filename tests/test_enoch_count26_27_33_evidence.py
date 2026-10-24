"""New counts never approve English; two windows retain an exact typed chain."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from tools.enoch import bounded_application as t,count26_27_33_evidence as counts


class SourceCount26_27_33Test(unittest.TestCase):
    def test_only_three_source_inventories_are_new(self):
        result=counts.load()
        self.assertEqual({c:len(r['units'])for c,r in result.items()},{26:6,27:5,33:4})
        self.assertNotIn(17,result)
        for row in result.values():self.assertFalse(row['wording_approval']);self.assertFalse(row['reader_release_policy_changed'])
        d,_=counts.evidence();self.assertEqual(d['canonical_English_votes_imported'],0)

    def test_actual_selected_body_continuation_excludes_Greek_and_adjacent_chapters(self):
        d,_=counts.evidence();spans=d['unit_pages']
        self.assertEqual(spans['26:4'],[102,104]);self.assertEqual(spans['26:5'],[104]);self.assertEqual(spans['26:6'],[104])
        for v in range(1,6):self.assertEqual(spans[f'27:{v}'],[104])
        for v in range(1,5):self.assertEqual(spans[f'33:{v}'],[112])
        p=t.ROOT/d['artifact_prefix'];raw=json.loads((p/'raw-model-text.json').read_text())
        self.assertIn('Greek comparison',raw['excluded_material']);self.assertIn('113',raw['excluded_material'])
        self.assertFalse(raw['wording_approved']);self.assertFalse(raw['publication_approved'])

    def test_real_provider_id_usage_and_ten_hash_projected_photographs(self):
        d,_=counts.evidence();p=t.ROOT/d['artifact_prefix'];r=json.loads((p/'provider-terminal-response.json').read_text())
        self.assertEqual(r['id'],'resp_0d45f9e90159d49d006adc3dad24c08194ba4028e4d7c3bb47')
        self.assertEqual(r['usage']['total_tokens'],10892)
        project=json.loads((p/'request-with-image-hashes.json').read_text());self.assertNotIn('image_url',json.dumps(project))
        self.assertEqual(sum(x['type']=='input_image'for x in project['request_projection']['input'][0]['content']),10)
        root=json.loads((p/'root-source-first-ledger.json').read_text())
        self.assertIn('previously integrated chapter26 provenance-only',root['prior_exposure'])
        self.assertFalse(root['English_or_publication_approval'])

    def test_separate_two_actor17_observations_are_not_an_Azure17_vote(self):
        d,_=counts.evidence();p=t.ROOT/d['artifact_prefix']
        a=json.loads((p/'ch17-full-author-source-first.json').read_text());b=json.loads((p/'ch17-full-exact-peer-source-first.json').read_text())
        self.assertNotEqual(a['reviewer_id'],b['reviewer_id']);self.assertEqual(a['actual_count'],8);self.assertEqual(b['count'],8)
        self.assertEqual(a['actual_spans']['7'],[84,86]);self.assertEqual(a['actual_spans']['8'],[86])
        result=json.loads((p/'raw-model-text.json').read_text());self.assertEqual([c['chapter']for c in result['chapters']],[26,27,33])

    def test_two_exact_window_arrays_from_actual_main_preimage(self):
        d,after=counts.evidence();p=t.ROOT/d['artifact_prefix'];before=json.loads((p/'page-map-before.json').read_text())
        proof=json.loads((p/'page-map-application-proof.json').read_text())
        self.assertEqual(proof['baseline_commit'],'d03dadea03d61bccea631399659c794532d619fd')
        self.assertEqual(proof['before_sha256'],'a51746556e1547198177d8c82ba4787bbf089aac0cb600d4f61e3992b2647880')
        self.assertEqual(proof['after_sha256'],'f539cd5ed8bf73a6ab65cf4e0030bf4e7692649a631cfcffacba5bf332fb7005')
        expected=copy.deepcopy(before)
        for c,pages in(('017',[84,86]),('026',[102,104])):expected['editions']['charles_1906']['chapters'][c]['pages']=pages
        self.assertEqual(after,expected)
        self.assertEqual(proof['canonical_YAML_changes'],0);self.assertEqual(proof['new_language_votes'],0)
        self.assertEqual(proof['model_scope_chapters'],[26,27,33])

    def test_typed_successor_keeps_earlier_owned_windows_and_full_map_guard(self):
        self.assertEqual(counts.window_successor('a51746556e1547198177d8c82ba4787bbf089aac0cb600d4f61e3992b2647880'),'f539cd5ed8bf73a6ab65cf4e0030bf4e7692649a631cfcffacba5bf332fb7005')
        with self.assertRaisesRegex(ValueError,'different predecessor'):counts.window_successor('0'*64)
        from tools.enoch.count41_44_evidence import verify_current_windows as first
        from tools.enoch.count106_108_evidence import verify_current_windows as second
        self.assertTrue(first());self.assertTrue(second());self.assertTrue(counts.verify_current_windows())

    def test_arbitrary_other_map_field_still_fails_closed(self):
        actual=t.artifact
        with tempfile.TemporaryDirectory()as directory:
            p=Path(directory)/'map.json';d=json.loads((t.ROOT/counts.PATH).read_text());d['updated']='unreviewed'
            p.write_text(json.dumps(d))
            with patch.object(t,'artifact',side_effect=lambda root,path:p if path==counts.PATH else actual(root,path)):
                with self.assertRaisesRegex(ValueError,'explicit reviewed window successor'):counts.verify_current_windows()

    def test_rewritten_original_result_or_index_is_rejected(self):
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
                with self.assertRaisesRegex(ValueError,'fixed structural index differs'):counts.load()

    def test_count_import_does_not_complete26_27_33_language(self):
        from tools.enoch.structural_counts import load_all_inventories
        inventories=load_all_inventories()
        for c,n in counts.COUNTS.items():self.assertEqual(inventories[c]['units'],list(range(1,n+1)))
        from tools.enoch.full_repair_progress import build
        report=build();self.assertEqual(report['evidence_inventory_warnings'],[])
        self.assertGreaterEqual(len(report['chapters_with_imported_paired_count_inventory']),102)
        for c in(26,27,33):self.assertNotIn(c,report['chapters_with_complete_imported_selected_edition_review'])
        self.assertFalse(report['completion_proven'])

    def test_CI_fetches_real_main_preimage_and_runs_new_test(self):
        workflow=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn('git fetch --no-tags --depth=1 origin '+counts.BASE,workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_enoch_count26_27_33_evidence.py'",workflow)


if __name__=='__main__':unittest.main()
