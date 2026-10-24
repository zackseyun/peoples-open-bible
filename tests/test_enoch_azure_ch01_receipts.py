"""Actual Azure output/usage receipts; neither call is an accepted repair."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'sources/enoch/coverage/azure61-sol-ch01-followup-20261023'
INDEX_SHA='4fef1f8dcb342f4896cf41f0f9223b573147c2fa5858a02c8ddaacc0328eeb8e'


def read_index():
    raw=(D/'index.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=INDEX_SHA:raise ValueError('Chapter1 Azure fixed receipt index differs')
    data=json.loads(raw)
    for path,digest in data['files'].items():
        if hashlib.sha256((D/path).read_bytes()).hexdigest()!=digest:raise ValueError('Chapter1 Azure original receipt differs')
    return data


class AzureChapter1ActualReceiptsTest(unittest.TestCase):
    def test_provider_ids_models_raw_outputs_and_tokens_match_actual_terminal(self):
        index=read_index();total=0
        for job in index['jobs']:
            directory=D/job['directory'];terminal=json.loads((directory/'provider-terminal-response.json').read_text())
            completed=json.loads((directory/'completed-receipt.json').read_text())
            self.assertEqual(terminal['status'],'completed')
            self.assertEqual(terminal['id'],completed['id']);self.assertEqual(terminal['id'],job['response_id'])
            self.assertEqual(terminal['model'],job['provider_reported_model'])
            self.assertEqual(terminal['model'],'gpt-6-1-sol-review')
            self.assertEqual(terminal['usage'],completed['usage'])
            self.assertEqual(terminal['usage']['total_tokens'],job['usage_total_tokens'])
            output=[c['text']for row in terminal['output']for c in row.get('content',[])if c.get('type')=='output_text']
            self.assertEqual(output,[(directory/'raw-model-text.json').read_text()])
            manifest=json.loads((directory/'request-manifest.json').read_text())
            start=json.loads((directory/'submission-started.json').read_text())
            self.assertEqual(manifest['request_sha256'],job['request_sha256']);self.assertEqual(start['request_sha256'],job['request_sha256'])
            total+=job['usage_total_tokens']
        self.assertEqual(total,24913)
        self.assertEqual(total+index['previous_known_usage_tokens'],index['cumulative_known_usage_tokens'])
        self.assertFalse(index['complete_billing_total']);self.assertEqual(index['older_unknown_upload_outcomes'],2)

    def test_nine_unit_source_only_output_is_incomplete_not_an_English_acceptance(self):
        read_index();data=json.loads((D/'source-only/raw-model-text.json').read_text())
        self.assertEqual(data['chapter'],1);self.assertEqual(data['observed_printed_unit_count'],9)
        self.assertEqual([r['verse']for r in data['printed_units']],list(range(1,10)))
        self.assertTrue(any('⟦?⟧'in r['source_text']for r in data['printed_units']))
        self.assertFalse(data['publication_approved'])
        self.assertIn('incomplete glyph-resolution',data['limits'])

    def test_exact_one_unit_adverse_and_image_count_are_not_rewritten(self):
        read_index();data=json.loads((D/'exact-1-7/raw-model-text.json').read_text())
        self.assertEqual((data['reference'],data['verdict']),('1 Enoch 1:7','hold'))
        self.assertFalse(data['publication_approved'])
        self.assertTrue(any('punctuation' in x for x in data['source_findings']))
        self.assertIn('five lexicon photographs',data['limits'])
        manifest=json.loads((D/'exact-1-7/request-manifest.json').read_text())
        names=[Path(p).suffix for p in manifest['scan_image_sha256']]
        self.assertEqual(names.count('.jpg'),4);self.assertEqual(names.count('.png'),2)
        self.assertTrue(manifest['candidate_English_supplied']);self.assertFalse(manifest['author_votes_supplied'])
        candidate=(D/'exact-1-7/review-input.json').read_bytes()
        self.assertEqual(hashlib.sha256(candidate).hexdigest(),manifest['exact_candidate_input_sha256'])

    def test_no_approval_retry_or_fabricated_control_plane_response_model(self):
        index=read_index();live=json.loads((D/'chapter1-live-deployment.json').read_text())
        self.assertEqual(live['model']['name'],'gpt-6.1-sol');self.assertEqual(live['model']['version'],'2026-09-29')
        self.assertEqual(live['state'],'Succeeded')
        self.assertEqual(index['canonical_votes_imported'],0);self.assertFalse(index['automatic_application'])
        self.assertFalse(index['older_unknown_requests_retried'])
        for row in index['jobs']:
            self.assertFalse(row['exact_English_acceptance']);self.assertFalse(row['publication_approved'])
        workflow=(ROOT/'.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn("python -m unittest discover -s tests -p 'test_enoch_azure_ch01_receipts.py'",workflow)
