"""Reviewed Enoch notes and critical source metadata remain exact in exports."""
import copy
import unittest
from tools import export_mobile_bible as exporter

class ReviewedEnochNotesExportTest(unittest.TestCase):
    def fixture(self):
        return {'book':'1 Enoch','source':{'edition':'charles-1906-enoch','language':'Geez',
            'text':'መ⟦?⟧ትከ','pages':[200],'transcription_uncertainties':[{'marker':'⟦?⟧','status':'unresolved'}],
            'additional_translation_input':[{'language':'Greek','text':'reported reading','scope':'printed edited comparison only'}]},
            'source_correction':{'individual_unit_application_approved':True},
            'translation':{'text':'Provisional rendering[a] [critical words].',
                'footnotes':[{'marker':'a','text':'A source glyph ⟦?⟧ is unresolved.','reason':'textual_variant'}]}}

    def test_exact_notes_literal_marker_and_uncertainties_survive_without_canonical_mutation(self):
        record=self.fixture();before=copy.deepcopy(record);out=exporter._export_record_verse(2,record)
        self.assertEqual(out['footnote_review'],'pob-enoch-paired-source-review-v1')
        self.assertEqual(out['source_critical'],record['source'])
        self.assertEqual(out['footnotes'],record['translation']['footnotes'])
        self.assertEqual(out['text'],record['translation']['text']);self.assertEqual(record,before)

    def test_other_books_and_unapproved_sources_do_not_inherit_note_approval(self):
        for change in ('book','approval','edition'):
            record=self.fixture()
            if change=='book':record['book']='Genesis'
            if change=='approval':record['source_correction']['individual_unit_application_approved']=False
            if change=='edition':record['source']['edition']='unreviewed'
            out=exporter._export_record_verse(2,record)
            self.assertNotIn('footnote_review',out);self.assertNotIn('source_critical',out)


class EnochReleaseCountIsolationTest(unittest.TestCase):
    def test_source_only_override_cannot_change_fallback_release_count(self):
        from unittest.mock import patch
        from tools.enoch import verse_parser, selected_edition_sources
        from tools.enoch.audit_pob_source_coverage import EXPECTED_VERSES
        raw=[verse_parser.EnochVerseRow(48,1,'raw','','fixture')]
        reviewed=raw+[verse_parser.EnochVerseRow(48,2,'reviewed','','fixture')]
        with patch.dict(EXPECTED_VERSES,{},clear=True), \
             patch.object(selected_edition_sources,'registry_data',return_value={'chapters':{}}), \
             patch.object(verse_parser,'parse_chapter',return_value=(reviewed,[])), \
             patch.object(verse_parser,'parse_ocr_chapter',return_value=(raw,[])):
            self.assertEqual(exporter._enoch_expected_verse_map()[48],[1])

    def test_declared_release_count_is_not_replaced_by_a_partial_recovery(self):
        from unittest.mock import patch
        from tools.enoch import verse_parser, selected_edition_sources
        from tools.enoch.audit_pob_source_coverage import EXPECTED_VERSES
        partial=[verse_parser.EnochVerseRow(48,1,'raw','','fixture')]
        with patch.dict(EXPECTED_VERSES,{48:3},clear=True), \
             patch.object(selected_edition_sources,'registry_data',return_value={'chapters':{}}), \
             patch.object(verse_parser,'parse_chapter',return_value=(partial,[])), \
             patch.object(verse_parser,'parse_ocr_chapter',return_value=(partial,[])):
            self.assertEqual(exporter._enoch_expected_verse_map()[48],[1,2,3])

if __name__=='__main__':unittest.main()
