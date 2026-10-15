"""Verify the reviewed Deut32:8 application, not its historical priority."""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest
from unittest.mock import patch

import yaml

from tools import export_mobile_bible as exporter
from tools.textual_restoration import critical_verse
from tools.textual_restoration.verify_source_composition import normalized

ROOT = Path(__file__).resolve().parents[1]
BASE = '3d0cab4d35b356e052417df5cb009a3137f614c4'
TARGET = 'translation/ot/deuteronomy/032/008.yaml'
PREFIX = 'sources/textual_restoration/'
SOURCE_PIN = {
    'path': 'sources/ot/pob_critical/deuteronomy/032/008.json',
    'sha256': '64da99eaebe065548730f137dc79912a6bf3e854be1cc46d8a0a830c518b9f1a',
}
TRUST = {
    'trusted_source_sha256': SOURCE_PIN['sha256'],
    'trusted_review_sha256': '5ba2c4a23b236b968bc65dbc7d1bbab56bcb5de3ef229ee429efa77a7f9d47f7',
    'trusted_composition_sha256': '159465475fd4a7618dede0ef2013fa9ee308c9f15e42337cdf6988b66c57c2b0',
}


class Deut32CriticalApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        raw = subprocess.check_output(['git', '-C', str(ROOT), 'show', f'{BASE}:{TARGET}'])
        cls.baseline = yaml.safe_load(raw)
        cls.baseline_sha = hashlib.sha256(raw).hexdigest()
        cls.current = yaml.safe_load((ROOT / TARGET).read_text())

    def test_exact_current_full_record_has_external_review_binding(self):
        result = critical_verse.validate(self.current, **TRUST)
        self.assertTrue(result['full_critical_verse_verified'])
        self.assertFalse(result['canonical_application_approved'])
        self.assertFalse(result['publication_approved'])
        self.assertEqual(self.current['source']['edition'], 'POB-critical')

    def test_only_the_declared_source_unit_changes(self):
        expected = normalized(self.baseline['source']['text']).replace('בני ישראל', 'בני אלוהים')
        self.assertEqual(self.current['source']['text'], expected)
        self.assertTrue(expected.startswith('בהנחל '))
        self.assertFalse(self.current['restoration_draft']['entire_verse_attested_in_selected_fragment'])

    def test_old_generation_and_all_changed_fields_are_preserved(self):
        self.assertEqual(self.current['ai_draft'], self.baseline['ai_draft'])
        for field in ('source', 'translation', 'lexical_decisions', 'theological_decisions',
                      'status', 'cross_check', 'revision_pass'):
            archive = next(a for a in self.current['review_history']
                           if a['field'] == field and a.get('archive_scope') == 'deut32-8-full-record-2026-10-15')
            self.assertEqual(archive['value'], self.baseline[field])
            self.assertEqual(archive['archived_from_baseline_sha256'], self.baseline_sha)
            self.assertFalse(archive['certifies_this_candidate'])
        self.assertEqual(self.current['cross_check'], {'status': 'needs_review'})
        self.assertEqual(self.current['status'], 'draft')
        self.assertNotIn('revision_pass', self.current)

    def test_english_matches_reviewed_synthesis_and_notes_are_anchored(self):
        result = json.loads((ROOT / PREFIX / 'comparisons/deut32_8_english_result.2026-10-15.v1.json').read_text())
        translation = self.current['translation']
        self.assertEqual(re.sub(r'\[[a-z]+\]', '', translation['text']), result['preferred_text'])
        self.assertIn('humankind[b]', translation['text'])
        self.assertIn('sons of God[a]', translation['text'])
        notes = {n['marker']: n['text'] for n in translation['footnotes']}
        for disclosure in ('provisionally', '4Q37', 'sons of Israel', 'angels of God',
                           'earliest Hebrew remains debated', 'not a complete surviving 4Q37'):
            self.assertIn(disclosure, notes['a'])
        self.assertIn('paralleling', notes['b'])
        self.assertIn('not only males', notes['b'])

    def test_active_metadata_does_not_reuse_obsolete_policy_or_root(self):
        entries = {e['source_word']: e for e in self.current['lexical_decisions']}
        self.assertEqual(entries['בני אדם']['chosen'], 'humankind')
        self.assertEqual(entries['בני אלוהים']['chosen'], 'the sons of God')
        self.assertIn('5324 (נצב)', entries['יצב']['rationale'])
        self.assertNotIn('gender-accurate over gender-neutral', json.dumps(self.current['theological_decisions']))

    def test_unreviewed_source_english_notes_or_score_cannot_reuse_review(self):
        for field in ('source', 'english', 'note', 'score'):
            record = copy.deepcopy(self.current)
            if field == 'source': record['source']['text'] = record['source']['text'].replace('אלוהים', 'אל')
            elif field == 'english': record['translation']['text'] += ' Added theology.'
            elif field == 'note': record['translation']['footnotes'][0]['text'] = 'Certain original.'
            else: record['cross_check']['agreement'] = 1
            with self.subTest(field=field), self.assertRaises(ValueError):
                critical_verse.validate(record, **TRUST)

    def test_current_full_book_export_changes_only_target_against_base_overlay(self):
        current_book = exporter.export_book('DEU')
        original = exporter.load_translation_record

        def overlay(book, chapter, verse):
            if (book, chapter, verse) == ('DEU', 32, 8):
                return copy.deepcopy(self.baseline)
            return original(book, chapter, verse)

        with patch.object(exporter, 'load_translation_record', side_effect=overlay):
            base_book = exporter.export_book('DEU')
        self.assertIsNotNone(current_book)

        def locate(book):
            return next(v for c in book['chapters'] if c['chapter'] == 32
                        for v in c['verses'] if v['verse'] == 8)

        exported = locate(current_book)
        self.assertEqual(exported['text'], self.current['translation']['text'])
        self.assertEqual(exported['footnotes'], self.current['translation']['footnotes'])
        self.assertNotIn('source', exported)  # Reader notes, not hidden source JSON, carry disclosure.
        restored = copy.deepcopy(current_book)
        old = locate(restored)
        old.clear()
        old.update(locate(base_book))
        self.assertEqual(restored, base_book)


if __name__ == '__main__':
    unittest.main()
