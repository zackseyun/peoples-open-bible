"""Extra-text notes must remain attached to their own emitted reader units."""

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

from tools import export_mobile_bible as exporter


class ExtraTextReaderNotesTests(unittest.TestCase):
    def write_record(self, root, code, chapter, record, verse=None):
        directory = root / exporter.EXTRA_CANONICAL_BOOK_SLUGS[code]
        if verse is not None:
            directory /= f'{chapter:03}'
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f'{chapter if verse is None else verse:03}.yaml'
        path.write_text(yaml.safe_dump(record), encoding='utf-8')
        return path

    def export_records(self, code, records):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for chapter, verse, record in records:
                self.write_record(root, code, chapter, record, verse)
            with patch.object(exporter, 'EXTRA_CANONICAL_ROOT', root):
                return exporter.export_extra_canonical_book(code)

    def record(self, text):
        return {'translation': {'text': text, 'footnotes': [
            {'marker': ' [1] ', 'text': '  First note.  ',
             'reason': ' textual_variant ', 'archival_detail': 'not exported'},
            {'marker': 'a2', 'text': 'Second note.', 'reason': ''},
            {'marker': 'unused', 'text': 'Unreferenced archival note.'},
            None, 3, {}, {'marker': '1', 'text': None},
            {'marker': '1', 'text': '  '}, {'text': 'Missing marker.'},
        ]}}

    def test_nested_notes_normalize_only_anchored_markers_and_preserve_gaps(self):
        first = self.record('  First[1], with [supplied words].  ')
        first['is_superscription'] = True
        second = self.record('Second[a2].')
        book = self.export_records('JUB', [(1, 1, first), (1, 3, second)])
        self.assertEqual(book, {
            'name': 'Jubilees', 'chapters': [{'chapter': 1, 'verses': [
                {'verse': 1, 'text': first['translation']['text'].strip(),
                 'footnotes': [{'marker': '1', 'text': 'First note.',
                               'reason': 'textual_variant'}]},
                {'verse': 3, 'text': second['translation']['text'],
                 'footnotes': [{'marker': 'a2', 'text': 'Second note.'}]},
            ]}],
        })

    def test_chapter_paragraph_notes_are_filtered_per_unit(self):
        record = self.record('First[1].\n\nSecond[a2].\n\nText with [supplied words].')
        verses = self.export_records('GOSTR', [(1, None, record)])['chapters'][0]['verses']
        self.assertEqual([v['verse'] for v in verses], [1, 2, 3])
        self.assertEqual([v['text'] for v in verses], record['translation']['text'].split('\n\n'))
        self.assertEqual(verses[0]['footnotes'], [
            {'marker': '1', 'text': 'First note.', 'reason': 'textual_variant'}])
        self.assertEqual(verses[1]['footnotes'], [{'marker': 'a2', 'text': 'Second note.'}])
        self.assertNotIn('footnotes', verses[2])
        self.assertTrue(all(v['is_editorial_section'] for v in verses))

    def test_explicit_numbers_and_repeated_markers_retain_unit_boundaries(self):
        record = self.record('1:1 First[1].\n\n1:3 Second[1][a2].')
        verses = self.export_records('GOSTR', [(1, None, record)])['chapters'][0]['verses']
        self.assertEqual([v['verse'] for v in verses], [1, 3])
        self.assertEqual([v['text'] for v in verses], ['First[1].', 'Second[1][a2].'])
        self.assertEqual([len(v['footnotes']) for v in verses], [1, 2])
        self.assertNotIn('is_editorial_section', verses[0])
        verses[0]['footnotes'][0]['text'] = 'Changed output.'
        self.assertEqual(verses[1]['footnotes'][0]['text'], 'First note.')

    def test_parenthetical_numbers_attach_only_local_notes(self):
        record = self.record('(6) First[1]. (7) Second[a2].')
        verses = self.export_records('IGTH', [(1, None, record)])['chapters'][0]['verses']
        self.assertEqual([v['verse'] for v in verses], [6, 7])
        self.assertEqual([v['text'] for v in verses], ['First[1].', 'Second[a2].'])
        self.assertEqual([v['footnotes'][0]['marker'] for v in verses], ['1', 'a2'])

    def test_editorial_sections_and_navigation_keep_their_shape(self):
        record = self.record('First[1].\n\nSecond[a2].\n\nThird.')
        record.update({
            'unit': 'editorial_section', 'reference': 'Synthetic 1',
            'reader_navigation': {'heading': 'Chapter heading'},
            'reader_sections': [
                {'section': 2, 'paragraph_start': 1, 'paragraph_end': 2, 'title': 'First section'},
                {'section': 5, 'paragraph_start': 3, 'title': 'Last section'},
            ],
        })
        chapter = self.export_records('GOSTR', [(1, None, record)])['chapters'][0]
        self.assertEqual({k: v for k, v in chapter.items() if k != 'verses'}, {
            'chapter': 1, 'unit': 'editorial_section', 'reference': 'Synthetic 1',
            'heading': 'Chapter heading', 'reader_navigation': record['reader_navigation'],
        })
        verses = chapter['verses']
        self.assertEqual([v['verse'] for v in verses], [2, 5])
        self.assertEqual(verses[0]['text'], 'First[1].\nSecond[a2].')
        self.assertEqual([n['marker'] for n in verses[0]['footnotes']], ['1', 'a2'])
        self.assertEqual(verses[0]['section_label'], '§2')
        self.assertEqual(verses[0]['section_heading'], 'First section')
        self.assertNotIn('footnotes', verses[1])

    def test_no_notes_plain_brackets_and_malformed_note_lists_keep_exact_shape(self):
        for code in ('JUB', 'GOSTR'):
            for notes in (None, {}, 'malformed', [None, {'marker': 'x', 'text': 'Not anchored.'}]):
                with self.subTest(code=code, notes=notes):
                    record = {'translation': {'text': '  Supplied [words] and [1].  ', 'footnotes': notes},
                              'is_superscription': True}
                    verse = None if code == 'GOSTR' else 0
                    book = self.export_records(code, [(1, verse, record)])
                    unit = {'verse': 1 if verse is None else 0, 'text': 'Supplied [words] and [1].'}
                    if code == 'GOSTR':
                        unit['is_editorial_section'] = True
                    self.assertEqual(book, {'name': exporter.EXTRA_CANONICAL_BOOK_TITLES[code],
                                            'chapters': [{'chapter': 1, 'verses': [unit]}]})

    def test_metadata_and_jesus_annotations_are_unchanged(self):
        for code, verse in (('JUB', 1), ('GOSTR', None)):
            with self.subTest(code=code):
                record = self.record('Jesus said, “Peace[1].”')
                record['source'] = {'manuscript': 'Synthetic witness', 'ancient_language': 'Greek',
                                    'witness_url': 'https://example.invalid/witness'}
                with_notes = self.export_records(code, [(1, verse, record)])
                no_notes_record = copy.deepcopy(record)
                no_notes_record['translation'].pop('footnotes')
                without_notes = self.export_records(code, [(1, verse, no_notes_record)])
                unit = with_notes['chapters'][0]['verses'][0]
                self.assertEqual(unit['text'][unit['jesus_words'][0]['start']:unit['jesus_words'][0]['end']],
                                 'Peace[1].')
                self.assertIn('footnotes', unit)
                unit.pop('footnotes')
                self.assertEqual(with_notes, without_notes)
                self.assertEqual(with_notes['metadata']['manuscript'], 'Synthetic witness')

    def test_exports_do_not_mutate_records_or_yaml_bytes(self):
        for code, verse in (('JUB', 1), ('GOSTR', None)):
            with self.subTest(code=code), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                record = self.record('First[1].')
                original = copy.deepcopy(record)
                path = self.write_record(root, code, 1, record, verse)
                original_bytes = path.read_bytes()
                with patch.object(exporter, 'EXTRA_CANONICAL_ROOT', root), \
                     patch.object(exporter.yaml, 'safe_load', return_value=record):
                    book = exporter.export_extra_canonical_book(code)
                self.assertEqual(record, original)
                book['chapters'][0]['verses'][0]['footnotes'][0]['text'] = 'Output-only change.'
                self.assertEqual(record, original)
                self.assertEqual(path.read_bytes(), original_bytes)

    def test_final_json_payload_keeps_both_extra_text_layouts_notes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for code, verse in (('JUB', 1), ('GOSTR', None)):
                self.write_record(root, code, 1, self.record('First[1].'), verse)
            with patch.object(exporter, 'EXTRA_CANONICAL_ROOT', root), \
                 patch.object(exporter, 'CANONICAL_BOOK_ORDER', []), \
                 patch.object(exporter, 'APOCRYPHA_BOOK_ORDER', []), \
                 patch.object(exporter, 'EXTRA_CANONICAL_BOOK_ORDER', ['JUB', 'GOSTR']):
                payload = json.loads(json.dumps(exporter.export_translation()))
        self.assertEqual([b['name'] for b in payload['books']], ['Jubilees', 'Gospel of Truth'])
        for book in payload['books']:
            unit = book['chapters'][0]['verses'][0]
            self.assertEqual(unit['text'], 'First[1].')
            self.assertEqual(unit['footnotes'], [{'marker': '1', 'text': 'First note.',
                                                'reason': 'textual_variant'}])


if __name__ == '__main__':
    unittest.main()
