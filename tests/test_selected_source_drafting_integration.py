import contextlib
import copy
import io
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

import yaml

os.environ.setdefault('CARTHA_DRAFTER_BACKEND', 'openai-sdk')
from tools import draft
from tools.textual_restoration import selected_draft_source as resolver


ROOT = Path(__file__).resolve().parents[1]


class SelectedSourceDraftingIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.verse = draft.load_source_verse('ISA', 9, 2)
        self.path = draft.translation_path_for_verse(self.verse)
        self.before = self.path.read_bytes()
        self.selected = resolver.resolve_selected_ot_source(self.verse)
        candidate = json.loads((ROOT / 'sources/textual_restoration/candidates/isaiah9_2_joy.2026-10-10.v1.json').read_text())
        self.tool = {
            'english_text': candidate['translation']['text'],
            'translation_philosophy': 'optimal-equivalence',
            'lexical_decisions': [copy.deepcopy(candidate['lexical_decisions'][2])],
            'footnotes': copy.deepcopy(candidate['translation']['footnotes']),
            'source_distinction_checks': [],
        }

    def tearDown(self):
        self.assertEqual(self.path.read_bytes(), self.before)

    def model_response(self):
        return (copy.deepcopy(self.tool), 'fixture-model-version', '{}', 0.2)

    def test_selected_prompt_uses_actual_qere_and_its_morphology(self):
        prompt = draft.build_selected_source_prompt(self.verse)
        source_section, tail = prompt.split('# Morphology table', 1)
        morphology = tail.split('# DOCTRINE.md excerpt', 1)[0]
        self.assertIn(self.selected.source_payload['text'], source_section)
        self.assertIn('selected Masoretic reading form', source_section)
        self.assertIn('written_text', source_section)
        self.assertIn('ל֖/וֹ', morphology)
        self.assertIn('morph=HR/Sp3ms', morphology)
        self.assertNotIn('morph=HTn', morphology)
        self.assertIn('base-edition context only, not selected readings', prompt)
        self.assertIn('unapproved candidate', prompt)
        self.assertIn(' לא ', draft.source_text_for_verse(self.verse))

    def test_generation_validation_binding_and_emitted_record_share_selected_source(self):
        with patch.object(draft, 'call_model', return_value=self.model_response()) as model, \
                patch.object(draft, 'validate_tool_input', wraps=draft.validate_tool_input) as validation, \
                patch.object(draft.distinctions, 'bind_draft_checks', wraps=draft.distinctions.bind_draft_checks) as binding, \
                patch.object(draft, 'write_verse_yaml') as write:
            result = draft.draft_selected_source_candidate(self.verse, model='fixture-model')
        self.assertEqual(result.verse.hebrew_text, self.selected.source_payload['text'])
        self.assertEqual(validation.call_args.args[0].hebrew_text, self.selected.source_payload['text'])
        self.assertEqual(binding.call_args.args[0]['source'], self.selected.source_payload)
        self.assertEqual(result.record['source'], self.selected.source_payload)
        self.assertEqual(result.record['ai_draft']['selected_source_at_draft'], self.selected.provenance)
        self.assertEqual(result.record['ai_draft']['model_id'], 'fixture-model')
        self.assertIn('verified-selected-source-v1', result.record['ai_draft']['prompt_id'])
        self.assertNotEqual(result.record['ai_draft'], yaml.safe_load(self.before)['ai_draft'])
        self.assertEqual(result.record['status'], 'draft')
        self.assertNotIn('review_history', result.record)
        self.assertNotIn('revision_pass', result.record)
        self.assertIn(self.selected.source_payload['text'], model.call_args.kwargs['user'])
        self.assertTrue(draft.distinctions.receipt_is_current(result.record))
        draft.validate_record(result.record)
        write.assert_not_called()

    def test_raw_route_still_refuses_selected_sources_even_in_memory(self):
        with patch.object(draft, 'call_model') as model:
            with self.assertRaisesRegex(ValueError, 'Selected-source regeneration required'):
                draft.draft_verse(self.verse, write=False)
            model.assert_not_called()

    def test_unregistered_critical_or_nt_source_stops_before_model(self):
        with patch.object(draft, 'call_model') as model:
            for code, chapter, verse in [('ISA', 53, 11), ('JHN', 21, 15)]:
                with self.subTest(code=code), self.assertRaisesRegex(ValueError, 'No verified selected-source drafting entry'):
                    draft.draft_selected_source_candidate(draft.load_source_verse(code, chapter, verse))
            model.assert_not_called()

    def test_private_engine_refuses_selected_canonical_write(self):
        with patch.object(draft, 'call_model') as model, patch.object(draft, 'write_verse_yaml') as write:
            with self.assertRaisesRegex(ValueError, 'candidate-only'):
                draft._generate_draft(self.selected.verse, selected_source=self.selected, write=True)
            model.assert_not_called()
            write.assert_not_called()

    def test_input_drift_after_model_discards_candidate_without_write(self):
        with patch.object(draft, '_selected_ot_source', side_effect=[self.selected, resolver.SelectedSourceError('fixture drift')]), \
                patch.object(draft, 'call_model', return_value=self.model_response()) as model, \
                patch.object(draft, 'write_verse_yaml') as write:
            with self.assertRaisesRegex(ValueError, 'fixture drift'):
                draft.draft_selected_source_candidate(self.verse)
            model.assert_called_once()
            write.assert_not_called()

    def test_selected_cli_dry_run_is_verified_and_does_not_call_model(self):
        argv = ['draft.py', '--ref', 'Isaiah 9:2', '--selected-source-candidate', '--dry-run']
        with patch('sys.argv', argv), patch.object(draft, 'call_model') as model, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(draft.main(), 0)
        self.assertIn(self.selected.source_payload['text'], output.getvalue())
        self.assertIn('morph=HR/Sp3ms', output.getvalue())
        model.assert_not_called()

    def test_selected_cli_emits_only_unapproved_candidate_yaml(self):
        argv = ['draft.py', '--ref', 'Isaiah 9:2', '--selected-source-candidate', '--backend', 'openai-sdk']
        with patch('sys.argv', argv), patch.dict(os.environ, {'OPENAI_API_KEY': 'fixture-key'}), \
                patch.object(draft, 'call_model', return_value=self.model_response()), \
                patch.object(draft, 'write_verse_yaml') as write, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(draft.main(), 0)
        record = yaml.safe_load(output.getvalue())
        self.assertEqual(record['source'], self.selected.source_payload)
        self.assertTrue(record['ai_draft']['selected_source_at_draft']['candidate_only'])
        self.assertFalse(record['ai_draft']['selected_source_at_draft']['publication_approved'])
        self.assertNotIn('Wrote ', output.getvalue())
        write.assert_not_called()

    def test_pre_model_resolver_failure_is_not_downgraded_to_raw_fallback(self):
        with patch.object(draft, '_selected_ot_source', side_effect=resolver.SelectedSourceError('fixture bad pin')), \
                patch.object(draft, 'call_model') as model:
            with self.assertRaisesRegex(ValueError, 'fixture bad pin'):
                draft.draft_selected_source_candidate(self.verse)
            model.assert_not_called()


if __name__ == '__main__':
    unittest.main()
