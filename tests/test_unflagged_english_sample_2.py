"""Check draw mechanics and recorded scope, not philological correctness."""
import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from tools.textual_restoration import build_unflagged_english_sample_2 as runner

ROOT = Path(__file__).resolve().parents[1]
SELECTION = ROOT / 'sources/textual_restoration/samples/unflagged_english_sample.selection.v2.json'
REVIEW = ROOT / 'sources/textual_restoration/samples/unflagged_english_sample.review.v2.json'


class SampleTwoTests(unittest.TestCase):
    def test_success_restores_seed_and_records_actual_inputs(self):
        previous = runner.first.SEED
        fake = {'strata': {'torah': {'selected': {'path': 'not-in-first'}}}, 'protocol_inputs': {}}
        def build(root):
            self.assertEqual(runner.first.SEED, runner.SEED)
            return copy.deepcopy(fake)
        with patch.object(runner.first, 'build', side_effect=build), patch.object(runner.subprocess, 'check_output', return_value='test-head\n'):
            result = runner.build(ROOT)
        self.assertEqual(runner.first.SEED, previous)
        self.assertEqual(result['baseline_revision'], 'test-head')
        self.assertFalse(result['strata']['torah']['selected']['selected_in_first_sample'])
        for path in (runner.DECLARATION, runner.RUNNER):
            self.assertEqual(result['protocol_inputs'][path], hashlib.sha256((ROOT / path).read_bytes()).hexdigest())

    def test_failure_restores_seed(self):
        previous = runner.first.SEED
        with patch.object(runner.first, 'build', side_effect=RuntimeError('intentional')):
            with self.assertRaises(RuntimeError):
                runner.build(ROOT)
        self.assertEqual(runner.first.SEED, previous)

    def test_frozen_draw_scope(self):
        draw = json.loads(SELECTION.read_text())
        self.assertEqual(draw['seed'], runner.SEED)
        self.assertEqual(draw['corpus_files'], 23264)
        self.assertEqual(sum(s['eligible'] for s in draw['strata'].values()), 16410)
        self.assertEqual({s['selected']['id'] for s in draw['strata'].values()}, {'EXO.6.18', 'EZK.48.28', '1CH.19.1'})
        self.assertTrue(all(not s['selected']['selected_in_first_sample'] for s in draw['strata'].values()))

    def test_assessment_is_bound_to_draw_not_future_corpus(self):
        draw = json.loads(SELECTION.read_text())
        review = json.loads(REVIEW.read_text())
        self.assertEqual(review['selection_sha256'], hashlib.sha256(SELECTION.read_bytes()).hexdigest())
        selected = {s['selected']['id']: s['selected'] for s in draw['strata'].values()}
        self.assertEqual(set(selected), {r['id'] for r in review['reviews']})
        self.assertEqual([len(r['context_hashes']) for r in review['reviews']], [30, 35, 19])
        for row in review['reviews']:
            pin = selected[row['id']]
            self.assertEqual(row['context_hashes'][row['path']], pin['yaml_sha256'])
            for field, pin_field in [('source', 'source_text_sha256'), ('pob', 'english_text_sha256')]:
                self.assertEqual(hashlib.sha256(row[field].encode()).hexdigest(), pin[pin_field])
            self.assertEqual(len(row['rubric']), 6)
            self.assertEqual(row['outcome'], 'retain/tie')
        self.assertEqual(review['summary']['established_main_english_semantic_improvements'], 0)
        self.assertFalse(review['limits']['application_approved'])
        evidence = {r['url']: r for r in review['reference_evidence']}
        self.assertEqual(set(evidence), {url for r in review['reviews'] for url in r['references']})
        for item in evidence.values():
            self.assertEqual(item['excerpt_sha256'], hashlib.sha256(item['excerpt'].encode()).hexdigest())
            self.assertTrue(item['verified_on'])
        self.assertEqual(review['critic']['status'], 'completed_with_record_repairs')


if __name__ == '__main__':
    unittest.main()
