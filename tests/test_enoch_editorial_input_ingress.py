"""Accepted critical inputs survive drafting without claiming new manuscripts."""
import copy
import unittest
from unittest.mock import patch
from tools.enoch import verse_parser as parser, selected_edition_sources as sources
from tools.enoch import multi_witness
from tools.enoch.build_translation_prompt import build_enoch_prompt


class EditorialInputIngressTest(unittest.TestCase):
    def test_reviewed_row_prompt_and_witness_bundle_preserve_exact_controls(self):
        # Synthetic control: this tests transport, not approval of any reading.
        extra = [{'edition':'reported edited apparatus (test fixture)',
                  'text':'ἐνιαυτῶν μυρίων', 'pages':[49],
                  'scope':'Reported edition reading, not fresh manuscript inspection'}]
        uncertainty = [{'text':'መ⟦?⟧ትከ', 'scope':'POB unknown-glyph span (test fixture)'}]
        source = {'text':'መ⟦?⟧ትከ', 'pages':[49], 'note':'literal unknown span',
                  'additional_translation_input':extra,
                  'transcription_uncertainties':uncertainty}
        frozen = copy.deepcopy(source)
        rows = [{'verse':1, 'source':source, 'evidence':'test-only-reviewed-input.json'}]
        with patch.object(sources,'load_chapter',return_value=rows), \
             patch.object(sources,'load_unit_overrides',return_value=[]), \
             patch.object(multi_witness,'is_available',return_value=True), \
             patch.object(multi_witness,'dillmann_is_available',return_value=False):
            row,_ = parser.load_verse(1,1)
            bundle = build_enoch_prompt(1,1)
            witnesses = multi_witness.load_verse(1,1)
        for key, expected in [('additional_translation_input',extra),
                              ('transcription_uncertainties',uncertainty)]:
            self.assertEqual(getattr(row,key),expected)
            self.assertEqual(bundle.source_payload[key],expected)
            self.assertEqual(bundle.witness_set['accepted_source_editorial_controls'][key],expected)
            self.assertEqual(witnesses.accepted_source_editorial_controls[key],expected)
        self.assertIn('not newly inspected manuscripts',bundle.prompt)
        self.assertIn('መ⟦?⟧ትከ',bundle.prompt)
        self.assertIn('ἐνιαυτῶν μυρίων',bundle.prompt)
        self.assertIsNone(witnesses.greek_panopolitanus)
        self.assertIsNone(witnesses.greek_syncellus)
        self.assertIsNone(witnesses.greek_chester_beatty)
        row.additional_translation_input[0]['text']='mutated copy'
        self.assertEqual(source,frozen)
        self.assertEqual(bundle.source_payload['additional_translation_input'],extra)

    def test_unreviewed_ocr_has_no_invented_editorial_controls(self):
        row = parser.EnochVerseRow(5,1,'test','', 'test-only')
        self.assertIsNone(row.additional_translation_input)
        self.assertIsNone(row.transcription_uncertainties)

if __name__=='__main__': unittest.main()
