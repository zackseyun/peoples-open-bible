"""Live chapter5 successor checks; chapter8's original proof replays unchanged.

This checks a bounded printed-edition import repair, not ancient priority,
Hebrew reconstruction, a full lexical collation, or canonical authority.
"""
import copy
from contextlib import redirect_stdout
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import yaml
from jsonschema import Draft202012Validator
from tools import export_mobile_bible as exporter, lxx_swete

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from tools import build_normalized_deuterocanon_corpus as normalizer

BASE = '756074bd3e0bd97c5d849c5ff47125972f4684b2'
BOOK = 'translation/deuterocanon/1_esdras'
CORPUS = 'sources/lxx/swete/final_corpus_adjudicated/1ES.jsonl'
NORMALIZED = 'sources/lxx/swete/final_corpus_normalized/1ES.jsonl'
PREFIX = 'sources/textual_restoration/'
SOURCE = PREFIX + 'candidates/1esdras5_source_partition.2026-10-19.v1.json'
ENGLISH = PREFIX + 'candidates/1esdras5_english_partition.2026-10-19.v1.json'
CANDIDATE = PREFIX + 'candidates/1esdras5_application.2026-10-19.v1.json'
EVIDENCE = PREFIX + 'comparisons/1esdras5_application.2026-10-19.v1.json'
AFFECTED = {25, 28, 29, 31, 38, 39}
DUPLICATE = f'{BOOK}/005/145.yaml'
QUARANTINE = PREFIX + 'quarantine/1esdras5_duplicate145.2026-10-19.v1.yaml'
DUPLICATE_SHA = 'df89390df4567d111ff938bd53dee403b5a56b02fd8c2f3a1a31061f106d8d97'
ARCHIVES = ('source', 'translation', 'lexical_decisions', 'theological_decisions',
            'status', 'revision_pass', 'cross_check')


def historical(path):
    return subprocess.check_output(['git', '--no-replace-objects', 'show', f'{BASE}:{path}'], cwd=ROOT)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verse_path(verse):
    return f'{BOOK}/005/{verse:03}.yaml'


class EsdrasFivePartitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads((ROOT / CANDIDATE).read_text())
        cls.s = json.loads((ROOT / SOURCE).read_text())
        cls.e = json.loads((ROOT / ENGLISH).read_text())
        archive = subprocess.check_output(['git', '--no-replace-objects', 'archive', BASE, BOOK], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            cls.book = {m.name: tar.extractfile(m).read() for m in tar.getmembers()
                        if m.isfile() and m.name.endswith('.yaml')}
        cls.raw = historical(CORPUS)
        cls.rows = [json.loads(x) for x in cls.raw.splitlines()]
        cls.previous_normalized = [json.loads(x) for x in historical(NORMALIZED).splitlines()]
        cls.normalized, cls.dropped = normalizer.normalize_1es(copy.deepcopy(cls.rows))

    def test_exact_full_records_schema_history_and_note_anchors(self):
        self.assertEqual(self.c['baseline_commit'], BASE)
        self.assertEqual(self.s['read_commit'], BASE)
        self.assertEqual(self.e['baseline_commit'], BASE)
        self.assertEqual(set(self.s['records']), {str(v) for v in range(1, 71)})
        self.assertEqual(set(self.c['records']), {verse_path(v) for v in AFFECTED})
        self.assertEqual(set(self.e['records']), {str(v) for v in AFFECTED})
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        for v in AFFECTED:
            path = verse_path(v)
            old, new = yaml.safe_load(self.book[path]), self.c['records'][path]
            errors = [f'{list(error.path)}: {error.message}' for error in validator.iter_errors(new)]
            self.assertEqual(errors, [], path)
            for key in ('id', 'reference', 'ai_draft'):
                self.assertEqual(new[key], old[key], (path, key))
            self.assertNotIn('draft_receipt_provenance', new)
            self.assertEqual(new['source']['edition'], old['source']['edition'])
            self.assertEqual(new['source']['text'], self.s['records'][str(v)]['greek'])
            self.assertEqual(new['source']['pages'], self.s['records'][str(v)]['source_pages'])
            self.assertEqual(new['source']['confidence'], 'medium')
            self.assertNotIn('parallel_sources', new['source'])
            self.assertEqual(new['status'], 'draft')
            self.assertEqual(new['cross_check'], {'status': 'needs_review'})
            self.assertNotIn('revision_pass', new)
            for key in ('translation', 'lexical_decisions', 'theological_decisions'):
                self.assertEqual(new[key], self.e['records'][str(v)][key])
            history = new['review_history'][-1]
            self.assertEqual(history['baseline_commit'], BASE)
            self.assertEqual(history['baseline_sha256'], sha(self.book[path]))
            self.assertEqual(history['fields'], {k: old[k] for k in ARCHIVES if k in old})
            self.assertFalse(history['certifies_this_candidate'])
            self.assertEqual(new['review_history'][:-1], old.get('review_history', []))
            self.assertEqual(new['revisions'][:-1], old.get('revisions', []))
            self.assertEqual(new['revisions'][-1]['from'], old['translation']['text'])
            self.assertEqual(new['revisions'][-1]['to'], new['translation']['text'])
            marks = re.findall(r'\[([a-z])\]', new['translation']['text'])
            notes = new['translation'].get('footnotes', [])
            self.assertEqual(marks, [n['marker'] for n in notes], path)
            self.assertEqual(marks, [chr(97+i) for i in range(len(marks))], path)
            changed = {*ARCHIVES, 'review_history', 'revisions'}
            self.assertEqual({k: val for k, val in new.items() if k not in changed},
                             {k: val for k, val in old.items() if k not in changed}, path)

    def test_exact_existing_codepoint_consumption_and_only_two_printed_additions(self):
        old = {v: yaml.safe_load(self.book[verse_path(v)])['source']['text'] for v in range(1, 71)}
        consumed, restored = [], []
        for v in range(1, 71):
            unit = self.s['records'][str(v)]
            parts = []
            for part in unit['source_parts']:
                if part['kind'] == 'existing_source_slice':
                    ov = part['old_verse']
                    self.assertIn(ov, old)
                    start, end = part['start_codepoint_inclusive'], part['end_codepoint_exclusive']
                    self.assertTrue(0 <= start < end <= len(old[ov]))
                    parts.append(old[ov][start:end].strip())
                    consumed.extend((ov, i) for i in range(start, end) if not old[ov][i].isspace())
                else:
                    self.assertEqual(part['kind'], 'printed_source_addition')
                    restored.append((v, part['addition_key'], part['greek']))
                    definitions = {item['addition_key']: item for item in self.s['addition_definitions']}
                    self.assertEqual(part, definitions[part['addition_key']])
                    parts.append(part['greek'])
            self.assertEqual(' '.join(parts), unit['greek'])
        self.assertEqual(consumed, [(v, i) for v in range(1, 71)
                                    for i, char in enumerate(old[v]) if not char.isspace()])
        self.assertEqual([v for v, _, _ in restored], [25, 31])
        self.assertEqual(len(self.s['addition_definitions']), 2)
        self.assertEqual({item['addition_key'] for item in self.s['addition_definitions']},
                         {key for _, key, _ in restored})
        self.assertEqual(restored, [(25, 'charme_217', 'υἱοὶ Χαρμή, διακόσιοι δέκα ἑπτά·'),
                                    (31, 'basalem', 'υἱοὶ Βασαλέμ,')])
        self.assertIn('Τωβείς', self.s['records']['28']['greek'])
        self.assertTrue(self.s['records']['29']['greek'].startswith('οἱ ἱερόδουλοι'))
        self.assertTrue(self.s['records']['38']['greek'].endswith('καὶ ἐκλήθη ἐπὶ τῷ ὀνόματι αὐτοῦ.'))
        self.assertTrue(self.s['records']['39']['greek'].startswith('καὶ τούτων'))
        self.assertIn('217', self.c['records'][verse_path(25)]['translation']['text'])
        self.assertNotIn('1,017', self.c['records'][verse_path(25)]['translation']['text'])

    def test_historical_inputs_reviewed_pins_and_unchanged_chapter8_evidence(self):
        evidence = json.loads((ROOT / EVIDENCE).read_text())
        self.assertEqual(evidence['baseline_commit'], BASE)
        self.assertTrue({SOURCE, ENGLISH, CANDIDATE, NORMALIZED,
                         'docs/1ESDRAS_5_PARTITION_REPAIR_2026-10-19.md',
                         'tools/build_normalized_deuterocanon_corpus.py',
                         'tests/test_1esdras5_partition_application.py',
                         '.github/workflows/corpus-integrity.yml',
                         'tools/textual_restoration/replay_historical_tests.py'}
                        <= set(evidence['reviewed_file_pins']))
        self.assertIn(CORPUS, evidence['historical_input_pins'])
        manifest = ''.join(path + '\t' + sha(raw) + '\n'
                           for path, raw in sorted(self.book.items()) if '/005/' in path)
        self.assertEqual(sha(manifest.encode()), evidence['canonical_baseline_manifest_sha256'])
        for path, pin in evidence['historical_input_pins'].items():
            self.assertEqual(sha(historical(path)), pin, path)
        for path in evidence['unchanged_live_inputs']:
            self.assertEqual((ROOT / path).read_bytes(), historical(path), path)
        for path, pin in evidence['reviewed_file_pins'].items():
            self.assertEqual(sha((ROOT / path).read_bytes()), pin, path)
        old_evidence_path = PREFIX + 'comparisons/1esdras8_application.2026-10-19.v1.json'
        self.assertEqual((ROOT / old_evidence_path).read_bytes(), historical(old_evidence_path))
        old_evidence = json.loads(historical(old_evidence_path))
        for path in set(old_evidence['reviewed_file_pins']) - {NORMALIZED, 'tools/build_normalized_deuterocanon_corpus.py'}:
            self.assertEqual((ROOT / path).read_bytes(), historical(path), path)
        workflow = (ROOT / '.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn(f'git fetch --no-tags --depth=1 origin {BASE}', workflow)
        self.assertIn('git fetch --no-tags --depth=1 origin 97194d2b4c691514373896490110246b0b024219', workflow)
        self.assertIn('python -m tools.textual_restoration.replay_historical_tests esdras8_partition', workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_1esdras5_partition_application.py'", workflow)

    def test_normalized_source_reproduces_complete495_preserves_chapter8_and_guards_drift(self):
        self.assertEqual(len(self.rows), 496)
        self.assertEqual(len(self.normalized), 495)
        self.assertEqual(len(self.dropped), 1)
        self.assertIn('145', self.dropped[0])
        before = {(int(r['chapter']), int(r['verse'])): r for r in self.previous_normalized}
        after = {(int(r['chapter']), int(r['verse'])): r for r in self.normalized}
        self.assertEqual(set(before) - set(after), {(5, 145)})
        self.assertEqual(set(after) - set(before), set())
        self.assertEqual({key for key in after if after[key] != before[key]}, {(5, v) for v in AFFECTED})
        self.assertEqual([int(r['verse']) for r in self.normalized if int(r['chapter']) == 5], list(range(1, 71)))
        for v in AFFECTED:
            row = after[(5, v)]
            self.assertEqual(row['greek'], self.s['records'][str(v)]['greek'])
            self.assertEqual(row['confidence'], 'medium')
            self.assertEqual(row['adjudication']['confidence'], 'medium')
            self.assertNotIn('similarity', row)
            self.assertFalse(any(k.startswith('pre_adjudication') for k in row))
            self.assertEqual(row['source_correction_history'][-1]['record'], before[(5, v)])
            self.assertFalse(row['source_correction_history'][-1]['certifies_corrected_record'])
        with tempfile.TemporaryDirectory(prefix='pob-1es5-source-') as tmp:
            folder = Path(tmp)
            (folder / 'SUMMARY.md').write_text('unchanged summary\n')
            (folder / 'WIS.jsonl').write_text('unrelated override\n')
            with patch.object(normalizer, 'OUT_DIR', folder), redirect_stdout(io.StringIO()):
                self.assertEqual(normalizer.main(['--book', '1ES']), 0)
            self.assertEqual((folder / '1ES.jsonl').read_bytes(), (ROOT / NORMALIZED).read_bytes())
            self.assertEqual({p.name for p in folder.iterdir()}, {'1ES.jsonl', 'WIS.jsonl', 'SUMMARY.md'})
            self.assertEqual((folder / 'SUMMARY.md').read_text(), 'unchanged summary\n')
            self.assertEqual((folder / 'WIS.jsonl').read_text(), 'unrelated override\n')
            with patch.object(lxx_swete, 'NORMALIZED_CORPUS_DIR', folder):
                loaded = list(lxx_swete.iter_source_verses('1ES'))
            self.assertEqual(len(loaded), 495)
            units = {r.verse: r for r in loaded if r.chapter == 5}
            self.assertEqual(set(units), set(range(1, 71)))
            for v in AFFECTED:
                self.assertEqual(units[v].greek_text, self.s['records'][str(v)]['greek'])
                self.assertEqual(units[v].source_confidence, 'medium')
            (folder / '1ES.jsonl').write_text('{}\n')
            with patch.object(normalizer, 'SRC_DIR', folder), self.assertRaises(ValueError):
                normalizer.normalize_1es(self.rows)
        mutated = copy.deepcopy(self.rows)
        mutated[0]['greek'] += ' drift'
        with self.assertRaises(ValueError):
            normalizer.normalize_1es(mutated)

    def test_recoverable_quarantine_and_exact_live_canonical_scope(self):
        self.assertEqual(len(self.book), 496)
        self.assertEqual(self.c['quarantine'], {
            'original_path': DUPLICATE, 'archive_path': QUARANTINE,
            'sha256': DUPLICATE_SHA, 'duplicate_of': '1ES.5.47',
        })
        self.assertEqual(sha(self.book[DUPLICATE]), DUPLICATE_SHA)
        self.assertEqual((ROOT / QUARANTINE).read_bytes(), self.book[DUPLICATE])
        self.assertEqual(yaml.safe_load(self.book[DUPLICATE])['source']['text'],
                         yaml.safe_load(self.book[verse_path(47)])['source']['text'])
        live = {str(p.relative_to(ROOT)): p.read_bytes() for p in (ROOT / BOOK).rglob('*.yaml')}
        # Permit exactly the untouched preflight or the complete applied state,
        # never an arbitrary mixed application or loss of an unrelated record.
        preflight = DUPLICATE in live
        self.assertEqual(set(live), set(self.book) if preflight else set(self.book) - {DUPLICATE})
        for path, raw in live.items():
            if not preflight and path in self.c['records']:
                self.assertEqual(yaml.safe_load(raw), self.c['records'][path], path)
            else:
                self.assertEqual(raw, self.book[path], path)
        self.assertEqual(len(live), 496 if preflight else 495)
        self.assertEqual(sum('/008/' in path for path in live), 92)

    def test_real_whole_book_export_restores70_units_without_changing_other_chapters(self):
        with tempfile.TemporaryDirectory(prefix='pob-1es5-export-') as tmp:
            folder = Path(tmp)
            for path, raw in self.book.items():
                dest = folder / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)
            with patch.object(exporter, 'APOCRYPHA_ROOT', folder / 'translation/deuterocanon'):
                before = exporter.export_apocrypha_book('1ES')
                for path, record in self.c['records'].items():
                    (folder / path).write_text(yaml.safe_dump(record, allow_unicode=True, sort_keys=False))
                (folder / DUPLICATE).unlink()  # Isolated temporary tree only.
                after = exporter.export_apocrypha_book('1ES')
        self.assertEqual([ch['chapter'] for ch in before['chapters']], [1, 2, 3, 4, 6, 7, 8, 9])
        self.assertEqual(sum(len(ch['verses']) for ch in before['chapters']), 425)
        self.assertEqual([ch['chapter'] for ch in after['chapters']], list(range(1, 10)))
        self.assertEqual(sum(len(ch['verses']) for ch in after['chapters']), 495)
        chapter = next(ch for ch in after['chapters'] if ch['chapter'] == 5)
        self.assertEqual([v['verse'] for v in chapter['verses']], list(range(1, 71)))
        for v in range(1, 71):
            record = self.c['records'].get(verse_path(v), yaml.safe_load(self.book[verse_path(v)]))
            translation = record['translation']
            expected = {'verse': v, 'text': translation['text']}
            if translation.get('footnotes'):
                expected['footnotes'] = translation['footnotes']
            self.assertEqual(chapter['verses'][v-1], expected)
        without5 = copy.deepcopy(after)
        without5['chapters'] = [ch for ch in without5['chapters'] if ch['chapter'] != 5]
        self.assertEqual(without5, before)
        if not (ROOT / DUPLICATE).exists():
            self.assertEqual(exporter.export_apocrypha_book('1ES'), after)


if __name__ == '__main__':
    unittest.main()
