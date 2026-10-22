"""Reviewed Enoch notes and critical source metadata remain exact in exports."""
import copy
from pathlib import Path
import unittest
from tools import export_reader_bible as exporter

class ReviewedEnochNotesExportTest(unittest.TestCase):
    def fixture(self):
        return {'book':'1 Enoch','source':{'edition':'charles-1906-enoch','language':'Geez',
            'text':'መ⟦?⟧ትከ','pages':[200], 'note':'POB-added unknown span; not a Charles mark or ancient lacuna.', 'confidence':'low','transcription_uncertainties':[{'marker':'⟦?⟧','status':'unresolved'}],
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



class ReaderExporterIsolationTest(unittest.TestCase):
    def test_historical_shared_exporter_bytes_and_non_enoch_function_identity(self):
        import hashlib
        from tools import export_mobile_bible as legacy
        self.assertEqual(hashlib.sha256(Path(legacy.__file__).read_bytes()).hexdigest(),
            '2258f72485099fe1014152eeb29394324415940467c2edd9d9da0d48a4a113c3')
        self.assertIs(exporter.export_book,legacy.export_book)
        self.assertIs(exporter.export_apocrypha_book,legacy.export_apocrypha_book)
        self.assertIs(exporter.export_psalms_book,legacy.export_psalms_book)
        sentinel={'name':'unchanged non-Enoch output'}
        from unittest.mock import patch
        with patch.object(legacy,'export_extra_canonical_book',return_value=sentinel) as original:
            self.assertIs(exporter.export_extra_canonical_book('DID'),sentinel)
            original.assert_called_once_with('DID')

    def test_explicit_current_cli_serializes_approved_details_without_a_legacy_hook(self):
        import json,tempfile
        from unittest.mock import patch
        record=ReviewedEnochNotesExportTest().fixture()
        verse=exporter._export_record_verse(2,record)
        payload={'translation':'POB preview','books':[{'name':'1 Enoch',
            'chapters':[{'chapter':84,'verses':[verse]}]}]}
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'reader.json'
            with patch.object(exporter,'export_translation',return_value=payload) as build:
                self.assertEqual(exporter.main(['--output',str(path)]),0)
                build.assert_called_once_with()
            self.assertEqual(json.loads(path.read_text()),payload)



class CurrentPayloadAssemblyTest(unittest.TestCase):
    def test_real_payload_normalizer_preserves_exact_reviewed_critical_details(self):
        from unittest.mock import patch
        from tools import export_mobile_bible as legacy
        record=ReviewedEnochNotesExportTest().fixture()
        verse=exporter._export_record_verse(2,record)
        book={'name':'1 Enoch','chapters':[{'chapter':84,'verses':[verse]}]}
        with patch.object(legacy,'CANONICAL_BOOK_ORDER',[]), \
             patch.object(legacy,'APOCRYPHA_BOOK_ORDER',[]), \
             patch.object(legacy,'EXTRA_CANONICAL_BOOK_ORDER',['ENO']), \
             patch.object(exporter,'export_extra_canonical_book',return_value=copy.deepcopy(book)):
            payload=exporter.export_translation()
        self.assertEqual(payload['books'],[book])
        verse['source_critical']['pages'].append(999)
        self.assertEqual(record['source']['pages'],[200])

if __name__=='__main__':unittest.main()
