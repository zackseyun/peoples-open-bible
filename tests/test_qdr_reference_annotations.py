"""Unindexed text cannot become negative passage or preservation evidence."""
import copy
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from tools.textual_restoration.extract_qdr_passages import (
    extract_passages, main, reference_annotation_audit,
)


def corpus(words):
    return [{'scroll': 'fixture', 'fragments': [{'id': 'f1', 'lines': [
        {'n': '1', 'words': words}]}]}]


class ReferenceAnnotationTests(unittest.TestCase):
    def test_unindexed_six_slot_words_are_not_passage_absence(self):
        data = corpus([['', 'visible', '', '', '', ''], ['', '[supplied]', '', '', '', '']])
        before = copy.deepcopy(data)
        audit = reference_annotation_audit(data)
        self.assertEqual((audit['status'], audit['words'], audit['empty_reference_slots']),
                         ('none', 2, 2))
        self.assertEqual(audit['annotated_words'], 0)
        with self.assertRaisesRegex(ValueError, 'cannot establish absence'):
            extract_passages(data, {'Hab 1:5'})
        self.assertEqual(data, before)

    def test_partial_annotations_keep_exact_matches_and_line_context(self):
        data = corpus([['', '[prior', '', '', '', ''],
                       ['', 'target]', '', '', '', 'Hab 1:5']])
        audit = reference_annotation_audit(data)
        self.assertEqual(audit['status'], 'partial')
        self.assertEqual((audit['annotated_words'], audit['empty_reference_slots'],
                          audit['records_with_references']), (1, 1, 1))
        result = extract_passages(data, {'Hab 1:5', 'Hab 1:6'}, include_line_context=True)
        self.assertEqual(result['Hab 1:6'], [])
        line = result['Hab 1:5'][0]['lines'][0]
        self.assertEqual(line['diplomatic_text'], 'target]')
        self.assertEqual(line['line_context']['diplomatic_text'], '[prior target]')
        self.assertFalse(line['line_context']['preservation_assessed'])
        self.assertIn('Only indexed words', audit['warning'])

    def test_empty_whitespace_and_unusable_slots_are_reported_not_normalized(self):
        data = corpus([[], ['short'], ['', 'word', '', '', '', None],
                       ['', 'word', '', '', '', []], ['', 'word', '', '', '', '  ']])
        audit = reference_annotation_audit(data)
        self.assertEqual((audit['unusable_reference_slots'], audit['empty_reference_slots']), (4, 1))
        self.assertEqual(audit['status'], 'none')
        self.assertEqual(reference_annotation_audit([])['status'], 'none')
        with self.assertRaises(ValueError):
            extract_passages(data, {'Hab 1:5'})
        annotated = corpus([['', 'word', '', '', '', ' Hab 1:5']])
        self.assertEqual(reference_annotation_audit(annotated)['status'], 'complete')
        self.assertEqual(extract_passages(annotated, {'Hab 1:5'}), {'Hab 1:5': []})

    def test_cli_rejects_unindexed_source_and_emits_audit_for_annotated_source(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'synthetic.json'
            # Synthetic test fixtures, not acquisition or modification of research inputs.
            path.write_text(json.dumps(corpus([['', 'word', '', '', '', '']])))
            error, out = io.StringIO(), io.StringIO()
            with redirect_stderr(error), redirect_stdout(out), self.assertRaises(SystemExit) as result:
                main([str(path), '--reference', 'Hab 1:5'])
            self.assertEqual(result.exception.code, 2)
            self.assertEqual(out.getvalue(), '')
            self.assertIn('cannot establish absence', error.getvalue())
            path.write_text(json.dumps(corpus([['', 'word', '', '', '', 'Hab 1:5']])))
            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(main([str(path), '--reference', 'Hab 1:5']), 0)
            result = json.loads(out.getvalue())
            self.assertEqual(result['reference_annotations']['status'], 'complete')
            self.assertEqual(result['results']['Hab 1:5'][0]['manuscript_id'], 'fixture')


if __name__ == '__main__':
    unittest.main()
