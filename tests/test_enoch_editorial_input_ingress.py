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
        source = {'text':'መ⟦?⟧ትከ', 'pages':[49], 'note':'literal unknown span', 'confidence':'low',
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
            api = parser.build_jsonable(1)
        for key, expected in [('additional_translation_input',extra),
                              ('transcription_uncertainties',uncertainty)]:
            self.assertEqual(getattr(row,key),expected)
            self.assertEqual(bundle.source_payload[key],expected)
            self.assertEqual(bundle.witness_set['accepted_source_editorial_controls'][key],expected)
            self.assertEqual(witnesses.accepted_source_editorial_controls[key],expected)
        from tools.enoch.draft import build_record
        drafted=build_record(bundle,{'english_text':'Fixture only.','translation_philosophy':'optimal-equivalence'},model_id='fixture',model_version='fixture',prompt_id='fixture',prompt_sha256='0'*64,temperature=0,output_hash='0'*64)
        for key in ('additional_translation_input','transcription_uncertainties'):
            self.assertEqual(drafted['source'][key],source[key])
            self.assertEqual(drafted['enoch_witnesses']['accepted_source_editorial_controls'][key],source[key])
            self.assertEqual(api['verses'][0][key],source[key])
        self.assertEqual(drafted['source']['confidence'],'low')
        self.assertEqual(api['verses'][0]['source_confidence'],'low')
        self.assertEqual(row.source_confidence,'low')
        self.assertEqual(bundle.source_payload['confidence'],'low')
        self.assertEqual(witnesses.geez_charles.confidence,'low')
        self.assertIn(source['note'],witnesses.geez_charles.note)
        self.assertIn('exact independently accepted source input',bundle.prompt)
        self.assertNotIn('Source witness (Zone 1 primary — Charles 1906 Ge\'ez OCR)',bundle.prompt)
        self.assertTrue(any('additional_translation_input' in x for x in bundle.zone1_sources_at_draft))
        self.assertTrue(any('transcription_uncertainties' in x for x in bundle.zone1_sources_at_draft))
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
        self.assertIsNone(row.source_confidence)

if __name__=='__main__': unittest.main()
