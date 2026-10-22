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

if __name__=='__main__':unittest.main()
