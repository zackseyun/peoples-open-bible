"""Primary source promotion cannot be a readback of installed English/YAML."""
from contextlib import contextmanager
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from tools.enoch import selected_edition_sources as sources, verse_parser as parser
from tools.enoch import bounded_application as transaction
from tools.enoch.audit_pob_source_coverage import EXPECTED_VERSES
from tools.enoch.build_translation_prompt import build_enoch_prompt


@contextmanager
def evidence_copy():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory).resolve()
        registry = root/'registry.json'
        registry.write_bytes(sources.REGISTRY.read_bytes())
        name = 'enoch_full_repair_batch02_20261020'
        package = root/'applications'/name
        shutil.copytree(transaction.APPLICATIONS/name, package)
        with patch.object(sources, 'REGISTRY', registry), \
                patch.object(transaction, 'APPLICATIONS', package.parent), \
                patch.object(transaction, 'ROOT', root):
            yield registry, package


class ReviewedSourcesTest(unittest.TestCase):
    def test_registered_chapters_have_complete_reviewed_sources(self):
        for c,count in {36:4,37:5,38:6,39:14,45:6}.items():
            rows,warnings=parser.parse_chapter(c)
            self.assertEqual([r.verse for r in rows], list(range(1,count+1)))
            self.assertTrue(all(r.pages and 'applications/' in r.chapter_file for r in rows))
            self.assertIn('Not independent manuscript certification', warnings[0])

    def test_registered_source_loader_never_reads_installed_canonical_yaml(self):
        original_bytes, original_text = Path.read_bytes, Path.read_text
        def deny_canonical(path):
            if path.is_relative_to(transaction.TRANSLATION):
                raise AssertionError('Source loader read canonical output')
        def read_bytes(path, *args, **kwargs):
            deny_canonical(path);return original_bytes(path, *args, **kwargs)
        def read_text(path, *args, **kwargs):
            deny_canonical(path);return original_text(path, *args, **kwargs)
        with patch.object(Path, 'read_bytes', read_bytes), patch.object(Path, 'read_text', read_text):
            rows=sources.load_chapter(39)
        self.assertIn('ይትለሐዩ', rows[6]['source']['text'])

    def test_raw_ocr_remains_separate_and_unchanged(self):
        path=parser.chapter_path(39);before=path.read_bytes()
        raw,_=parser.parse_ocr_chapter(39);reviewed,_=parser.parse_chapter(39)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse(raw[0].pages)
        self.assertNotEqual(raw[6].text, reviewed[6].text)

    def test_prompt_pages_and_source_label_follow_exact_reviewed_units(self):
        bundle=build_enoch_prompt(39,10)
        self.assertEqual(bundle.source_payload['pages'], [117,118])
        self.assertIn('paired-reviewed primary transcription', bundle.zone1_sources_at_draft[0])
        self.assertNotIn('Gemini OCR', bundle.zone1_sources_at_draft[0])

    def test_unregistered_chapters_keep_raw_parser(self):
        self.assertIsNone(sources.load_chapter(5))
        self.assertEqual(parser.parse_chapter(5), parser.parse_ocr_chapter(5))

    def test_corrupted_registered_evidence_does_not_fall_back_to_ocr(self):
        with evidence_copy() as (registry,package):
            p=package/'final/ch39-source-corrected-v3-input.json'
            p.write_text(p.read_text()+' ')
            with self.assertRaisesRegex(ValueError, 'artifact changed'):
                parser.parse_chapter(39)

    def test_repinning_a_held_review_does_not_promote_it_to_source(self):
        with evidence_copy() as (registry,package):
            p=package/'final/final-review-ch39-v3-independent.json'
            review=json.loads(p.read_text());review['reviews'][0]['verdict']='hold'
            p.write_text(json.dumps(review))
            m=package/'manifest.json';manifest=json.loads(m.read_text())
            manifest['files'][str(p.relative_to(package))]=transaction.sha(p.read_bytes())
            m.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'not accepted'):
                sources.load_chapter(39)

    def test_unconfirmed_chapter_count_cannot_be_promoted(self):
        with evidence_copy() as (registry,package):
            m=package/'manifest.json';manifest=json.loads(m.read_text())
            manifest['chapter_inventories'][0]['independent_count_confirmation']=False
            m.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'not independently bound'):
                sources.load_chapter(36)

    def test_individual_override_changes_only_its_exact_raw_unit(self):
        with evidence_copy() as (registry,package):
            data=json.loads(registry.read_text());data['chapters'].pop('39')
            data['units']={'39:7':package.name};registry.write_text(json.dumps(data))
            raw,_=parser.parse_ocr_chapter(39);rows,warnings=parser.parse_chapter(39)
            self.assertIn('ይትለሐዩ',rows[6].text)
            self.assertTrue(rows[6].pages)
            self.assertEqual([r for r in rows if r.verse!=7],[r for r in raw if r.verse!=7])
            self.assertIn('does not approve other OCR rows',warnings[-1])

    def test_individual_source_requires_declared_count_and_valid_address(self):
        for key in ('40:1','18:99'):
            with evidence_copy() as (registry,package):
                data=json.loads(registry.read_text());data['units']={key:package.name}
                registry.write_text(json.dumps(data))
                # This fixture tests missing-count rejection, not the evolving
                # production count inventory (40 now has a paired count).
                counts=dict(EXPECTED_VERSES);counts.pop(40,None)
                with patch.dict(EXPECTED_VERSES,counts,clear=True):
                    with self.assertRaisesRegex(ValueError,'requires a declared printed count'):
                        sources.load_unit_overrides(int(key.split(':')[0]))

    def test_individual_override_does_not_accept_an_ambiguous_raw_address(self):
        with evidence_copy() as (registry,package):
            data=json.loads(registry.read_text());data['chapters'].pop('39')
            data['units']={'39:7':package.name};registry.write_text(json.dumps(data))
            row=parser.EnochVerseRow(39,7,'raw','7.','fixture')
            with patch.object(parser,'parse_ocr_chapter',return_value=([row,row],[])):
                with self.assertRaisesRegex(ValueError,'ambiguous raw address'):
                    parser.parse_chapter(39)

    def test_individual_override_cannot_hide_an_unaccepted_exact_reference(self):
        with evidence_copy() as (registry,package):
            data=json.loads(registry.read_text());data['units']={'18:12':package.name}
            registry.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'lacks the exact unit'):
                sources.load_unit_overrides(18)

    def test_reviewed_source_controls_survive_into_the_drafting_prompt(self):
        # These are the source-reviewer's editorial notes, not the English
        # running translation being fed back as a source/oracle.
        row,_=parser.load_verse(4,1)
        self.assertTrue(row.source_note)
        prompt=build_enoch_prompt(4,1)
        self.assertIn('Source editorial control:',prompt.source_payload['note'])
        self.assertIn(row.source_note,prompt.source_payload['note'])


if __name__=='__main__':
    unittest.main()
