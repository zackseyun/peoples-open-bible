import contextlib
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

os.environ.setdefault('CARTHA_DRAFTER_BACKEND', 'openai-sdk')
from tools import draft


class OTSelectedSourceRedraftGuardTests(unittest.TestCase):
    def setUp(self):
        self.verse = draft.load_source_verse('ISA', 9, 2)
        self.base = {'id': self.verse.canonical_id, 'source': {
            'edition': 'WLC', 'text': draft.source_text_for_verse(self.verse)}}

    def save(self, record):
        path = draft.translation_path_for_verse(self.verse)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(record, allow_unicode=True), encoding='utf-8')
        return path

    def test_actual_qere_and_critical_source_are_stopped_before_model(self):
        for chapter, number in ((9, 2), (53, 11)):
            verse = draft.load_source_verse('ISA', chapter, number)
            path = draft.translation_path_for_verse(verse)
            before = path.read_bytes()
            with self.subTest(id=verse.canonical_id), patch.object(draft, 'call_model') as model:
                with self.assertRaisesRegex(ValueError, 'Selected-source regeneration required'):
                    draft.draft_verse(verse, write=True)
                model.assert_not_called()
                self.assertEqual(path.read_bytes(), before)
        self.assertIn(' לא ', draft.source_text_for_verse(self.verse))

    def test_cli_dry_run_refuses_to_present_raw_base_as_selected_source(self):
        with patch('sys.argv', ['draft.py', '--book', 'ISA', '--chapter', '9', '--verse', '2', '--dry-run']), \
                patch.object(draft, 'call_model') as model, \
                contextlib.redirect_stderr(io.StringIO()) as errors, \
                contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(draft.main(), 5)
        self.assertIn('Selected-source regeneration required', errors.getvalue())
        self.assertEqual(output.getvalue(), '')
        model.assert_not_called()

    def test_missing_first_draft_and_exact_base_record_keep_prompt_behavior(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(draft, 'TRANSLATION_ROOT', Path(directory)):
            first = draft.build_user_prompt(self.verse)
            path = self.save(self.base)
            before = path.read_bytes()
            self.assertEqual(draft.build_user_prompt(self.verse), first)
            self.assertIn(self.base['source']['text'], first)
            self.assertEqual(path.read_bytes(), before)

    def test_text_edition_and_integrated_source_divergence_fail_closed(self):
        for field in ('text', 'edition', 'integration'):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory, \
                    patch.object(draft, 'TRANSLATION_ROOT', Path(directory)):
                record = {'id': self.base['id'], 'source': dict(self.base['source'])}
                if field == 'text':
                    record['source']['text'] += ' '
                elif field == 'edition':
                    record['source']['edition'] = 'POB-critical'
                else:
                    record['critical_source_integration'] = {'record': 'unverified'}
                self.save(record)
                with self.assertRaisesRegex(ValueError, 'Selected-source regeneration required'):
                    draft.assert_raw_ot_draft_source_safe(self.verse)

    def test_missing_malformed_and_wrong_identity_records_do_not_authorize_raw_redraft(self):
        for record in (None, [], {'id': 'ISA.9.3', 'source': self.base['source']},
                       {'id': self.base['id']}, {'id': self.base['id'], 'source': {'edition': 'WLC', 'text': ''}},
                       {'id': self.base['id'], 'source': {'edition': '', 'text': 'text'}}):
            with self.subTest(record=record), tempfile.TemporaryDirectory() as directory, \
                    patch.object(draft, 'TRANSLATION_ROOT', Path(directory)):
                self.save(record)
                with self.assertRaises(ValueError):
                    draft.assert_raw_ot_draft_source_safe(self.verse)

    def test_yaml_parse_and_read_errors_are_nonretryable_validation_errors(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(draft, 'TRANSLATION_ROOT', Path(directory)):
            path = self.save(self.base)
            path.write_text('source: [', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Cannot parse'):
                draft.assert_raw_ot_draft_source_safe(self.verse)
            with patch.object(Path, 'read_text', side_effect=PermissionError('fixture denied')):
                with self.assertRaisesRegex(ValueError, 'Cannot verify'):
                    draft.assert_raw_ot_draft_source_safe(self.verse)

    def test_direct_and_retry_callers_cannot_bypass_gate_with_alternative_prompt(self):
        with patch.object(draft, 'build_user_prompt', return_value='fixture bypass'), \
                patch.object(draft, 'call_model') as model, patch.object(draft.time, 'sleep') as sleep:
            for write in (False, True):
                with self.assertRaisesRegex(ValueError, 'Selected-source regeneration required'):
                    draft.draft_verse(self.verse, write=write)
            with self.assertRaisesRegex(ValueError, 'Selected-source regeneration required'):
                draft.retry_draft_verse(self.verse, max_attempts=3)
            model.assert_not_called()
            sleep.assert_not_called()

    def test_source_change_during_model_call_stops_before_write(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(draft, 'TRANSLATION_ROOT', Path(directory)):
            path = self.save(self.base)
            changed = {'id': self.base['id'], 'source': {'edition': 'WLC', 'text': 'selected source'}}

            def model_call(**kwargs):
                self.save(changed)
                return ({'english_text': 'fixture text', 'source_distinction_checks': []}, 'fixture', '{}', 0.2)

            with patch.object(draft, 'build_user_prompt', return_value='fixture prompt'), \
                    patch.object(draft, 'source_distinction_prompt', return_value='fixture context'), \
                    patch.object(draft, 'call_model', side_effect=model_call), \
                    patch.object(draft, 'validate_tool_input'), patch.object(draft, 'validate_record'), \
                    patch.object(draft, 'build_verse_record', return_value={}), \
                    patch.object(draft.distinctions, 'bind_draft_checks', return_value=([], {})), \
                    patch.object(draft.distinctions, 'validate_checks', return_value={'requires_maintainer_review': False}), \
                    patch.object(draft.distinctions, 'assert_approved'), \
                    patch.object(draft, 'write_verse_yaml') as write:
                with self.assertRaisesRegex(ValueError, 'Selected-source regeneration required'):
                    draft.draft_verse(self.verse, write=True)
                write.assert_not_called()
            self.assertEqual(yaml.safe_load(path.read_text()), changed)

    def test_nt_behavior_is_outside_this_ot_guard(self):
        verse = draft.load_source_verse('JHN', 21, 15)
        with patch.object(Path, 'read_text', side_effect=AssertionError('OT guard should not read NT')):
            draft.assert_raw_ot_draft_source_safe(verse)


if __name__ == '__main__':
    unittest.main()
