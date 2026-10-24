"""Actual independent Azure structural counts, not Geʽez/English approval."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from tools.enoch import bounded_application as t, count41_44_evidence as counts


class Chapter41To44CountEvidenceTest(unittest.TestCase):
    def test_actual_root_and_provider_have_same17_counted_spans(self):
        output=counts.load();self.assertEqual({c:len(r['units'])for c,r in output.items()},counts.COUNTS)
        self.assertEqual(sum(len(r['units'])for r in output.values()),17)
        self.assertTrue(all(r['wording_approval']is False and r['reader_release_policy_changed']is False for r in output.values()))
        d,_=counts.evidence();self.assertEqual(d['unit_pages']['41:1'],[119,120])
        self.assertEqual(d['unit_pages']['41:5'],[120,121]);self.assertEqual(d['unit_pages']['44:1'],[122,123])
        self.assertEqual(d['unit_pages']['42:1'],[121]);self.assertEqual(d['unit_pages']['42:2'],[122])

    def test_actual_git_before_and_only_three_source_windows_changed(self):
        d,after=counts.evidence();prefix=t.ROOT/d['artifact_prefix']
        proof=json.loads((prefix/'page-map-application-proof.json').read_text())
        self.assertEqual(proof['before_sha256'],'3767ebc1bb19abf174afe21aa7c992af551853cbefa358ee12f1cc18a4a19800')
        self.assertEqual(proof['after_sha256'],'51235ca99c57e611b7c9ed9e653ea84390b2d87c724aab6d0b271a4600b33c76')
        self.assertEqual([r['json_path']for r in proof['changes']],[f'$.editions.charles_1906.chapters.{c:03d}.pages'for c in(41,42,44)])
        self.assertEqual(after['editions']['charles_1906']['chapters']['041']['pages'],[119,120,121])
        self.assertEqual(after['editions']['charles_1906']['chapters']['042']['pages'],[121,122])
        self.assertEqual(after['editions']['charles_1906']['chapters']['044']['pages'],[122,123])
        self.assertTrue(counts.verify_current_windows())
        self.assertFalse(proof['wording_approval']);self.assertEqual(proof['new_language_votes'],0)
        self.assertEqual(proof['canonical_YAML_changes'],0)

    def test_progress_gains_counts_not_new_complete_translations(self):
        from tools.enoch.structural_counts import load_all_inventories
        self.assertTrue(set(counts.COUNTS)<=set(load_all_inventories()))
        from tools.enoch.full_repair_progress import build
        report=build();self.assertEqual(report['evidence_inventory_warnings'],[])
        # The count profile itself approved no English. Preserve its dated
        # partial state instead of blocking a later full-language chapter42.
        import subprocess
        baseline='6499ede72eea063ebc8574ff56e029bb66768f5f'
        path='sources/enoch/coverage/full-repair-progress-batch24-20261024.json'
        historical=json.loads(subprocess.check_output(['git','show',baseline+':'+path],cwd=t.ROOT))
        for c in counts.COUNTS:self.assertNotIn(c,historical['chapters_with_complete_imported_selected_edition_review'])
        successor=t.APPLICATIONS/'enoch_full_repair_batch25_20261024'
        from tools.enoch.current_evidence import verify_current
        manifest=t.load_manifest(successor)
        self.assertEqual(t.sha((successor/'manifest.json').read_bytes()),'a63aeb53e3aa258c49d57e24e1bad6fdc6ec3ceca917882ddfc2b94715f92661')
        self.assertEqual(verify_current(successor)['references'],[f'1 Enoch 42:{v}'for v in(1,2,3)])
        self.assertEqual(manifest['chapter_inventories'][0]['units'],[1,2,3])
        self.assertIn(42,report['chapters_with_complete_imported_selected_edition_review'])
        for c in set(counts.COUNTS)-{42}:self.assertNotIn(c,report['chapters_with_complete_imported_selected_edition_review'])
        self.assertFalse(report['completion_proven']);self.assertFalse(report['artwork_publication_approval'])
        from tools.enoch.selected_edition_sources import registry_data
        registry=registry_data()
        self.assertEqual(registry['chapters']['42'],successor.name)
        for c in set(counts.COUNTS)-{42}:self.assertNotIn(str(c),registry['chapters'])

    def test_provider_receipt_is_a_real_completed_structural_only_job(self):
        d,_=counts.evidence();prefix=t.ROOT/d['artifact_prefix']
        terminal=json.loads((prefix/'provider-terminal-response.json').read_text())
        self.assertEqual(terminal['id'],'resp_048a5444503cf6d9006adbf7a779bc8196ac7d180d02c7ddd0')
        self.assertEqual(terminal['model'],'gpt-6-1-sol-review')
        self.assertEqual(terminal['usage']['total_tokens'],7294)
        result=json.loads((prefix/'raw-model-text.json').read_text())
        self.assertFalse(result['wording_approved']);self.assertFalse(result['publication_approved'])
        self.assertEqual(d['canonical_English_votes_imported'],0)
        request=json.loads((prefix/'request-with-image-hashes.json').read_text())
        self.assertTrue(request['no_expected_count_or_author_candidate_supplied'])
        self.assertNotIn('image_url',json.dumps(request))

    def test_original_count_or_index_drift_is_rejected(self):
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

    def test_arbitrary_other_window_change_cannot_hide_behind_owned_arrays(self):
        real=t.artifact
        with tempfile.TemporaryDirectory()as directory:
            target=Path(directory)/'tampered-map.json';d=json.loads((t.ROOT/counts.PATH).read_text());d['updated']='unreviewed';target.write_text(json.dumps(d))
            with patch.object(t,'artifact',side_effect=lambda root,path:target if path==counts.PATH else real(root,path)):
                with self.assertRaisesRegex(ValueError,'explicit reviewed window successor'):counts.verify_current_windows()

    def test_workflow_fetches_actual_predecessor_and_runs_registered_test(self):
        workflow=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn('git fetch --no-tags --depth=1 origin '+counts.BASE,workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_enoch_count41_44_evidence.py'",workflow)
