import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

from tools import export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]


class ReaderFootnoteExportTests(unittest.TestCase):
    def record(self):
        return {'translation': {'text': 'A disputed reading[a] and a supplied [word].',
                'footnotes': [{'marker': 'a', 'text': 'A contrary witness.', 'reason': 'textual_variant'},
                             {'marker': 'b', 'text': 'An unreferenced archival note.'}]}}

    def test_referenced_note_and_reason_survive_without_mutation(self):
        record = self.record()
        before = copy.deepcopy(record)
        result = exporter._export_record_verse(8, record)
        self.assertEqual(result['text'], record['translation']['text'])
        self.assertEqual(result['footnotes'], [record['translation']['footnotes'][0]])
        self.assertEqual(record, before)
        result['footnotes'][0]['text'] = 'changed output only'
        self.assertEqual(record, before)

    def test_bracketed_marker_normalizes_like_publisher(self):
        record = self.record()
        record['translation']['footnotes'][0]['marker'] = ' [a] '
        self.assertEqual(exporter._export_record_verse(8, record)['footnotes'][0]['marker'], 'a')

    def test_empty_malformed_and_background_notes_are_not_exported(self):
        record = self.record()
        record['translation']['footnotes'] = [None, 3, {}, {'marker': 'a', 'text': None},
                                              {'marker': 'a', 'text': '  '},
                                              {'marker': 'z', 'text': 'old rationale'}]
        result = exporter._export_record_verse(8, record)
        self.assertNotIn('footnotes', result)
        self.assertEqual(result['text'], record['translation']['text'])

    def test_absent_notes_and_manuscript_brackets_do_not_invent_notes(self):
        record = {'translation': {'text': 'Text with [supplied words].'}}
        self.assertEqual(exporter._export_record_verse(1, record),
                         {'verse': 1, 'text': record['translation']['text']})

    def test_canonical_ot_and_nt_book_paths_use_note_export(self):
        for code in ('DEU', 'MAT'):
            with self.subTest(code=code), \
                 patch.object(exporter, 'expected_chapter_map', return_value={1: [1]}), \
                 patch.object(exporter, 'load_translation_record', return_value=self.record()):
                book = exporter.export_book(code)
                self.assertEqual(book['chapters'][0]['verses'][0]['footnotes'][0]['text'], 'A contrary witness.')

    def test_final_payload_normalization_and_json_keep_note_bodies(self):
        with patch.object(exporter, 'CANONICAL_BOOK_ORDER', ['DEU']), \
             patch.object(exporter, 'APOCRYPHA_BOOK_ORDER', []), \
             patch.object(exporter, 'EXTRA_CANONICAL_BOOK_ORDER', []), \
             patch.object(exporter, 'expected_chapter_map', return_value={1: [1]}), \
             patch.object(exporter, 'load_translation_record', return_value=self.record()):
            payload = json.loads(json.dumps(exporter.export_translation()))
        verse = payload['books'][0]['chapters'][0]['verses'][0]
        self.assertEqual(verse['text'], self.record()['translation']['text'])
        self.assertEqual(verse['footnotes'], [self.record()['translation']['footnotes'][0]])

    def test_psalm_superscription_and_body_notes_survive(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            chapter = root / 'ot/psalms/001'
            chapter.mkdir(parents=True)
            for number in (0, 1):
                (chapter / f'{number:03}.yaml').write_text(yaml.safe_dump(self.record()))
            with patch.object(exporter, 'TRANSLATION_ROOT', root):
                verses = exporter.export_psalms_book()['chapters'][0]['verses']
            self.assertTrue(verses[0]['is_superscription'])
            self.assertTrue(all(v['footnotes'] for v in verses))

    def write_apocrypha_fixture(self, root, chapter, verse, record):
        directory = root / exporter.APOCRYPHA_BOOK_SLUGS['SIR'] / f'{chapter:03}'
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f'{verse:03}.yaml'
        path.write_text(yaml.safe_dump(record), encoding='utf-8')
        return path

    def test_apocrypha_referenced_notes_normalize_and_background_notes_stay_hidden(self):
        record = self.record()
        record['translation']['text'] = '  A disputed reading[a] and a supplied [word].  '
        record['translation']['footnotes'][0] = {
            'marker': ' [a] ', 'text': '  A contrary witness.  ',
            'reason': ' textual_variant ', 'archival_detail': 'not a reader field',
        }
        record['translation']['footnotes'].extend([
            None, {'marker': 'word', 'text': '  '}, {'marker': 'a', 'text': None},
        ])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_apocrypha_fixture(root, 1, 1, record)
            with patch.object(exporter, 'APOCRYPHA_ROOT', root):
                book = exporter.export_apocrypha_book('SIR')
        self.assertEqual(book, {
            'name': exporter.APOCRYPHA_BOOK_TITLES['SIR'],
            'chapters': [{'chapter': 1, 'verses': [{
                'verse': 1, 'text': record['translation']['text'].strip(),
                'footnotes': [{'marker': 'a', 'text': 'A contrary witness.',
                              'reason': 'textual_variant'}],
            }]}],
        })

    def test_apocrypha_no_note_records_keep_original_shape_without_superscription(self):
        records = [
            {'translation': {'text': ' Text with [supplied words]. '}},
            {'translation': {'text': 'Another text.', 'footnotes': [
                {'marker': 'a', 'text': 'Not referenced.'}]}},
        ]
        records[0]['is_superscription'] = True
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for number, record in enumerate(records, 1):
                self.write_apocrypha_fixture(root, 1, number, record)
            with patch.object(exporter, 'APOCRYPHA_ROOT', root):
                book = exporter.export_apocrypha_book('SIR')
        self.assertEqual(book, {
            'name': exporter.APOCRYPHA_BOOK_TITLES['SIR'],
            'chapters': [{'chapter': 1, 'verses': [
                {'verse': number, 'text': record['translation']['text'].strip()}
                for number, record in enumerate(records, 1)
            ]}],
        })

    def test_apocrypha_incomplete_chapters_do_not_withhold_later_complete_chapter(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for number in (1, 3):
                self.write_apocrypha_fixture(root, 1, number, self.record())
            self.write_apocrypha_fixture(root, 2, 1, self.record())
            self.write_apocrypha_fixture(root, 2, 2, {'translation': {'text': '  '}})
            self.write_apocrypha_fixture(root, 2, 3, self.record())
            for number in (1, 2):
                self.write_apocrypha_fixture(root, 3, number, self.record())
            with patch.object(exporter, 'APOCRYPHA_ROOT', root):
                book = exporter.export_apocrypha_book('SIR')
        self.assertEqual([chapter['chapter'] for chapter in book['chapters']], [3])
        verses = book['chapters'][0]['verses']
        self.assertEqual([verse['verse'] for verse in verses], [1, 2])
        self.assertTrue(all(verse['footnotes'] for verse in verses))

    def test_apocrypha_export_does_not_mutate_record_or_fixture(self):
        record = self.record()
        before = copy.deepcopy(record)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_apocrypha_fixture(root, 1, 1, record)
            original_bytes = path.read_bytes()
            with patch.object(exporter, 'APOCRYPHA_ROOT', root), \
                 patch.object(exporter.yaml, 'safe_load', return_value=record):
                book = exporter.export_apocrypha_book('SIR')
            self.assertEqual(record, before)
            book['chapters'][0]['verses'][0]['footnotes'][0]['text'] = 'output-only change'
            self.assertEqual(record, before)
            self.assertEqual(path.read_bytes(), original_bytes)

    def test_thirteen_actual_comparison_baselines_preserve_reader_notes(self):
        comparisons = ROOT / 'sources/textual_restoration/comparisons'
        cases = []
        for name in ('pentateuch_controls.v1.json', 'samuel_controls.v1.json', 'psalms_controls.v1.json'):
            cases.extend(json.loads((comparisons / name).read_text())['cases'])
        self.assertEqual(len(cases), 13)
        for case in cases:
            record = yaml.safe_load((ROOT / case['baseline']['repo_path']).read_text())
            out = exporter._export_record_verse(int(record['id'].split('.')[-1]), record)
            expected = [
                {k: str(n[k]).strip() for k in ('marker', 'text', 'reason') if n.get(k) is not None}
                for n in record['translation']['footnotes']
                if f"[{n['marker']}]" in record['translation']['text']
            ]
            self.assertTrue(expected, case['id'])
            self.assertEqual(out['footnotes'], expected)
            self.assertEqual(out['text'], record['translation']['text'].strip())


if __name__ == '__main__':
    unittest.main()
