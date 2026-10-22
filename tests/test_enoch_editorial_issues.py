"""Mechanical diagnostics must never silently certify Enoch translations."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml
from tools.enoch import audit_editorial_issues as editorial
from tools.enoch import audit_pob_source_coverage as coverage, verse_parser


def fixture(text='A complete English sentence.', notes=None):
    return {'id': '1EN.3.1', 'reference': '1 Enoch 3:1', 'book': '1 Enoch',
            'source': {'text': 'source።'},
            'translation': {'text': text, 'footnotes': notes or []}}


class EditorialIssuesTest(unittest.TestCase):
    def kinds(self, record):
        return {r['kind'] for r in editorial.record_issues(record, 3, 1)}

    def test_clean_record_is_not_linguistic_approval(self):
        self.assertEqual(self.kinds(fixture()), set())

    def test_duplicate_labels_and_misplaced_supplied_word_marker(self):
        notes = [{'marker': 'a', 'text': 'first'}, {'marker': 'a', 'text': 'second'},
                 {'marker': 'him', 'text': 'not a reader anchor'}]
        kinds = self.kinds(fixture('Some text[a] and more[a][him].', notes))
        self.assertTrue({'duplicate_note_marker', 'repeated_note_anchor',
                         'invalid_note_marker', 'unanchored_footnote'} <= kinds)

    def test_supplied_words_are_not_silently_treated_as_notes(self):
        self.assertEqual(self.kinds(fixture('He blessed [him].')), set())

    def test_oracle_origin_and_stale_selected_witness_are_not_ignored(self):
        record = fixture()
        record['source']['note'] = 'Source corrected to full Beta maṣāḥǝft oracle text.'
        record['enoch_witnesses'] = {'available_witnesses': [
            {'witness': 'charles_1906', 'text': 'different source'}]}
        self.assertTrue({'source_origin_policy_review', 'charles_witness_source_mismatch'} <= self.kinds(record))
        clean = fixture('A judgment oracle was spoken.')
        self.assertNotIn('source_origin_policy_review', self.kinds(clean))

    def test_missing_and_empty_note(self):
        kinds = self.kinds(fixture('A[b].', [{'marker': 'a', 'text': ''}]))
        self.assertTrue({'unanchored_footnote', 'missing_footnote', 'empty_footnote'} <= kinds)

    def test_repeated_span_is_a_lead_not_an_automatic_deletion(self):
        phrase = 'one two three four five six seven eight nine ten eleven twelve'
        self.assertIn('repeated_english_span_review', self.kinds(fixture(phrase + ' ' + phrase)))

    def test_empty_english_is_reported_even_without_a_primary_row(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / '003').mkdir()
            (root / '003/001.yaml').write_text(yaml.safe_dump(fixture(None)))
            with patch.object(coverage.verse_parser, 'parse_chapter', return_value=([], [])):
                result = coverage.audit([3], root)['chapters'][0]
            self.assertEqual(result['empty_translation_verse_numbers'], [1])
            self.assertFalse(result['translation_verified_by_this_audit'])

    def test_read_only_hash_bound_and_historical_status_not_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'translation'
            (root / '003').mkdir(parents=True)
            path = root / '003/001.yaml'
            path.write_text(yaml.safe_dump(fixture('A[a].')))
            before = path.read_bytes()
            apps = Path(directory) / 'applications'
            (apps / 'enoch_old').mkdir(parents=True)
            status = {'held_references': ['1 Enoch 3:1'], 'canonical_changed': False}
            (apps / 'enoch_old/status.json').write_text(json.dumps(status))
            primary = verse_parser.EnochVerseRow(3, 1, 'source።', '', 'fixture')
            with patch.object(coverage.verse_parser, 'parse_chapter', return_value=([primary], [])):
                report = editorial.build([3], root, apps)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(report['issues'][0]['canonical_sha256'], hashlib.sha256(before).hexdigest())
            self.assertFalse(report['full_book_verified'])
            self.assertFalse(report['publication_approved'])
            self.assertFalse(report['issues'][0]['translation_approved'])
            self.assertEqual(report['historical_review_status'][0]['record'], status)
            self.assertIn('missing_footnote', editorial.markdown(report))

    def test_chapter84_count_does_not_approve_held_text(self):
        # Preserve the exact original incomplete84 guard at its immutable tree.
        # Current complete critical-treatment controls are tested separately.
        from tools.enoch.replay_84_pre_critical_gate import replay
        historical=replay()
        self.assertTrue(historical['passed'])
        self.assertEqual(historical['tests_run'],1)
        self.assertEqual(historical['skipped'],0)
        self.assertFalse(historical['current_corpus_validated'])


if __name__ == '__main__':
    unittest.main()
