"""Selected seven-unit count, not a familiar eight-name roster or fresh wording."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from tools.enoch import bounded_application as t,count20_evidence as counts


class Chapter20CountEvidenceTest(unittest.TestCase):
    def test_selected_actual_count7_does_not_add_a_roster_unit(self):
        d=counts.load();self.assertEqual(d[20]['units'],list(range(1,8)))
        self.assertFalse(d[20]['wording_approval']);self.assertFalse(d[20]['reader_release_policy_changed'])
        self.assertNotIn(8,d[20]['units'])

    def test_real_independent_API_response_matches_author_count_photos(self):
        counts.load();index=json.loads((t.ROOT/counts.INDEX).read_text());prefix=t.ROOT/index['artifact_prefix']
        response=json.loads((prefix/'provider-terminal-response.json').read_text())
        self.assertEqual(response['id'],'resp_080cc63578dfd429006adc071713ec8194a946b4a5a3457a03')
        self.assertEqual(response['usage']['total_tokens'],3959)
        request=json.loads((prefix/'request-with-image-hashes.json').read_text())
        self.assertTrue(request['no_expected_count_or_author_candidate_supplied']);self.assertNotIn('image_url',json.dumps(request))
        review=json.loads((prefix/'author-author-review.json').read_text())
        self.assertEqual([r['reference']for r in review['reviews']if r['verdict']=='hold'],['1 Enoch 20:6'])
        self.assertEqual(index['canonical_English_votes_imported'],0)

    def test_count_does_not_complete_whole20_or_change_canonical_records(self):
        before=t.corpus_hashes();counts.load();self.assertEqual(before,t.corpus_hashes())
        from tools.enoch.full_repair_progress import build
        report=build();self.assertEqual(report['evidence_inventory_warnings'],[])
        self.assertIn(20,report['chapters_with_imported_paired_count_inventory'])
        self.assertNotIn(20,report['chapters_with_complete_imported_selected_edition_review'])
        self.assertFalse(report['completion_proven']);self.assertFalse(report['artwork_publication_approval'])
        from tools.enoch.selected_edition_sources import registry_data
        self.assertNotIn('20',registry_data()['chapters'])

    def test_raw_or_index_drift_rejected(self):
        index=json.loads((t.ROOT/counts.INDEX).read_text())
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory)
            for name in(counts.INDEX,*index['files']):
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(t.ROOT/name,p)
            p=root/index['artifact_prefix']/'raw-model-text.json';p.write_bytes(p.read_bytes()+b'\n')
            with patch.object(t,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'original count artifact differs'):counts.load()
            p=root/counts.INDEX;p.write_bytes(p.read_bytes()+b'\n')
            with patch.object(t,'ROOT',root):
                with self.assertRaisesRegex(ValueError,'fixed structural count index differs'):counts.load()

    def test_workflow_keeps_count_gate_separate(self):
        workflow=(t.ROOT/'.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn("python -m unittest discover -s tests -p 'test_enoch_count20_evidence.py'",workflow)
