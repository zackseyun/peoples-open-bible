"""Two printed-word import repairs, not a numbering or ancient-priority claim."""
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

BASE = '8ad14030bcedcdc533a74724afcdd672bdbf89ed'
BOOK = 'translation/deuterocanon/1_esdras'
CORPUS = 'sources/lxx/swete/final_corpus_adjudicated/1ES.jsonl'
NORMALIZED = 'sources/lxx/swete/final_corpus_normalized/1ES.jsonl'
PREFIX = 'sources/textual_restoration/'
SOURCE = PREFIX + 'candidates/1esdras7_source_import.2026-10-19.v1.json'
ENGLISH = PREFIX + 'candidates/1esdras7_english_import.2026-10-19.v1.json'
CANDIDATE = PREFIX + 'candidates/1esdras7_application.2026-10-19.v1.json'
EVIDENCE = PREFIX + 'comparisons/1esdras7_application.2026-10-19.v1.json'
WORDS = {4: ('προτάγματος', 'προστάγματος'), 6: ('προσενεχθέντες', 'προστεθέντες')}
ARCHIVES = ('source', 'translation', 'lexical_decisions', 'theological_decisions',
            'status', 'revision_pass', 'cross_check')


def historical(path):
    return subprocess.check_output(['git', '--no-replace-objects', 'show', f'{BASE}:{path}'], cwd=ROOT)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verse_path(verse):
    return f'{BOOK}/007/{verse:03}.yaml'


class EsdrasSevenWordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads((ROOT / CANDIDATE).read_text())
        cls.s = json.loads((ROOT / SOURCE).read_text())
        cls.e = json.loads((ROOT / ENGLISH).read_text())
        archive = subprocess.check_output(['git', '--no-replace-objects', 'archive', BASE, BOOK], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            cls.book = {m.name: tar.extractfile(m).read() for m in tar.getmembers()
                        if m.isfile() and m.name.endswith('.yaml')}
        cls.rows = [json.loads(x) for x in historical(CORPUS).splitlines()]
        cls.previous_normalized = [json.loads(x) for x in historical(NORMALIZED).splitlines()]
        cls.normalized, cls.dropped = normalizer.normalize_1es(copy.deepcopy(cls.rows))

    def test_exact_two_records_schema_active_metadata_history_and_notes(self):
        self.assertEqual(self.c['baseline_commit'], BASE)
        self.assertEqual(self.s['read_commit'], BASE)
        self.assertEqual(self.s['baseline_commit'], BASE)
        self.assertEqual(self.e['baseline_commit'], BASE)
        self.assertNotIn('quarantine', self.c)
        self.assertEqual(set(self.c['records']), {verse_path(v) for v in WORDS})
        self.assertEqual(set(self.e['records']), {'4', '6'})
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        for v in WORDS:
            path = verse_path(v)
            old, new = yaml.safe_load(self.book[path]), self.c['records'][path]
            self.assertEqual([f'{list(e.path)}: {e.message}' for e in validator.iter_errors(new)], [], path)
            for key in ('id', 'reference', 'ai_draft'):
                self.assertEqual(new[key], old[key], (path, key))
            self.assertNotIn('draft_receipt_provenance', new)
            self.assertEqual(new['source']['edition'], old['source']['edition'])
            self.assertEqual(new['source']['text'], self.s['records'][str(v)]['greek'])
            self.assertEqual(new['source']['pages'], [167])
            self.assertEqual(new['source']['confidence'], 'medium')
            self.assertEqual(new['source']['validation'], 'scan_word_correction_pending_full_review')
            self.assertNotIn('parallel_sources', new['source'])
            for locator in ('150', '168', '167'):
                self.assertIn(locator, new['source']['note'])
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
            self.assertEqual(marks, [n['marker'] for n in new['translation'].get('footnotes', [])])
            self.assertEqual(marks, [chr(97+i) for i in range(len(marks))])
            changed = {*ARCHIVES, 'review_history', 'revisions'}
            self.assertEqual({k: val for k, val in new.items() if k not in changed},
                             {k: val for k, val in old.items() if k not in changed}, path)
        six = self.c['records'][verse_path(6)]
        self.assertNotIn('who had been brought back', six['translation']['text'])
        self.assertNotIn('who had returned', six['translation']['text'])
        self.assertTrue(any('προστεθέντες' in d.get('source_word', '') for d in six['lexical_decisions']))
        self.assertFalse(any('προσενεχθέντες' in d.get('source_word', '') for d in six['lexical_decisions']))

    def test_all15_control_units_and_all_old_points_allow_only_two_word_replacements(self):
        self.assertEqual(set(self.s['records']), {str(v) for v in range(1, 16)})
        corrections, consumed = [], []
        for v in range(1, 16):
            old = yaml.safe_load(self.book[verse_path(v)])['source']['text']
            unit = self.s['records'][str(v)]
            self.assertEqual(unit['old_greek'], old)
            self.assertEqual(unit['old_greek_sha256'], sha(old.encode()))
            self.assertEqual(unit['contributors'], [v])
            self.assertEqual(unit['source_pages'], [167])
            self.assertEqual(unit['printed_pages'], [150])
            self.assertEqual(unit['pdf_pages'], [168])
            expected = old
            if v in WORDS:
                before, after = WORDS[v]
                self.assertEqual(old.count(before), 1)
                expected = old.replace(before, after, 1)
            self.assertEqual(unit['greek'], expected)
            parts = []
            for part in unit['source_parts']:
                self.assertIn(part['kind'], ('existing_source_slice', 'printed_word_correction'))
                self.assertEqual(part['old_verse'], v)
                self.assertEqual(part['old_source_id'], f'1ES.7.{v}')
                start, end = part['start_codepoint_inclusive'], part['end_codepoint_exclusive']
                self.assertTrue(0 <= start < end <= len(old))
                text = old[start:end]
                self.assertEqual(part['old_text'], text)
                self.assertEqual(part['old_slice_sha256'], sha(text.encode()))
                consumed.extend((v, i) for i in range(start, end))
                if part['kind'] == 'printed_word_correction':
                    self.assertIn(v, WORDS)
                    self.assertEqual((text, part['replacement_text']), WORDS[v])
                    self.assertEqual(part['replacement_sha256'], sha(part['replacement_text'].encode()))
                    corrections.append(part)
                    parts.append(part['replacement_text'])
                else:
                    parts.append(text)
            self.assertEqual(''.join(parts), unit['greek'])
        self.assertEqual(consumed, [(v, i) for v in range(1, 16)
                                    for i in range(len(yaml.safe_load(self.book[verse_path(v)])['source']['text']))])
        self.assertEqual(corrections, self.s['word_correction_definitions'])
        self.assertEqual([part['old_verse'] for part in corrections], [4, 6])
        self.assertIn('κοίλης Συρίας', self.s['records']['1']['greek'])
        self.assertTrue(self.s['records']['8']['greek'].startswith('χιμάρους'))
        self.assertTrue(self.s['records']['11']['greek'].startswith('καὶ πάντες'))

    def test_historical_reviewed_pins_and_original5_6_8_evidence_remain_immutable(self):
        evidence = json.loads((ROOT / EVIDENCE).read_text())
        self.assertEqual(evidence['baseline_commit'], BASE)
        self.assertTrue({SOURCE, ENGLISH, CANDIDATE, NORMALIZED,
                         'docs/1ESDRAS_7_WORD_REPAIR_2026-10-19.md',
                         'tools/build_normalized_deuterocanon_corpus.py',
                         'tests/test_1esdras7_word_application.py',
                         '.github/workflows/corpus-integrity.yml',
                         'tools/textual_restoration/replay_historical_tests.py'}
                        <= set(evidence['reviewed_file_pins']))
        self.assertIn(CORPUS, evidence['historical_input_pins'])
        manifest = ''.join(path + '\t' + sha(raw) + '\n'
                           for path, raw in sorted(self.book.items()) if '/007/' in path)
        self.assertEqual(sha(manifest.encode()), evidence['canonical_baseline_manifest_sha256'])
        for path, pin in evidence['historical_input_pins'].items():
            self.assertEqual(sha(historical(path)), pin, path)
        for path in evidence['unchanged_live_inputs']:
            self.assertEqual((ROOT / path).read_bytes(), historical(path), path)
        for path, pin in evidence['reviewed_file_pins'].items():
            self.assertEqual(sha((ROOT / path).read_bytes()), pin, path)
        mutable_implementations = {NORMALIZED, 'tools/build_normalized_deuterocanon_corpus.py',
                                  '.github/workflows/corpus-integrity.yml',
                                  'tools/textual_restoration/replay_historical_tests.py',
                                  'tests/test_replay_historical_tests.py'}
        for chapter in (5, 6, 8):
            path = PREFIX + f'comparisons/1esdras{chapter}_application.2026-10-19.v1.json'
            self.assertEqual((ROOT / path).read_bytes(), historical(path))
            previous = json.loads(historical(path))
            for frozen_path in set(previous['reviewed_file_pins']) - mutable_implementations:
                self.assertEqual((ROOT / frozen_path).read_bytes(), historical(frozen_path), frozen_path)
        workflow = (ROOT / '.github/workflows/corpus-integrity.yml').read_text()
        for commit in (BASE, 'c083d5b872d1bb70c79f065cf0007cb97ffceb97', '08a8a4cc05fcb8eb91580e01fb506a90de9799a9'):
            self.assertIn(f'git fetch --no-tags --depth=1 origin {commit}', workflow)
        for chapter in (5, 6, 8):
            self.assertIn(f'python -m tools.textual_restoration.replay_historical_tests esdras{chapter}_partition', workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_1esdras7_word_application.py'", workflow)

    def test_normalized495_exact_two_row_scope_loader_scoped_generation_and_drift_guards(self):
        self.assertEqual(len(self.rows), 496)
        self.assertEqual(len(self.normalized), 495)
        self.assertEqual(len(self.dropped), 1)
        self.assertIn('145', self.dropped[0])
        before = {(int(r['chapter']), int(r['verse'])): r for r in self.previous_normalized}
        after = {(int(r['chapter']), int(r['verse'])): r for r in self.normalized}
        self.assertEqual(set(after), set(before))
        self.assertEqual({key for key in after if after[key] != before[key]}, {(7, 4), (7, 6)})
        self.assertEqual([int(r['verse']) for r in self.normalized if int(r['chapter']) == 7], list(range(1, 16)))
        for v in WORDS:
            row = after[(7, v)]
            self.assertEqual(row['greek'], self.s['records'][str(v)]['greek'])
            self.assertEqual(row['confidence'], 'medium')
            self.assertEqual(row['adjudication']['confidence'], 'medium')
            self.assertNotIn('similarity', row)
            self.assertFalse(any(k.startswith('pre_adjudication') for k in row))
            self.assertEqual(row['source_correction_history'][-1]['record'], before[(7, v)])
            self.assertFalse(row['source_correction_history'][-1]['certifies_corrected_record'])
        with tempfile.TemporaryDirectory(prefix='pob-1es7-source-') as tmp:
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
            units = {r.verse: r for r in loaded if r.chapter == 7}
            self.assertEqual(set(units), set(range(1, 16)))
            for v in WORDS:
                self.assertEqual(units[v].greek_text, self.s['records'][str(v)]['greek'])
                self.assertEqual(units[v].source_confidence, 'medium')
            (folder / '1ES.jsonl').write_text('{}\n')
            with patch.object(normalizer, 'SRC_DIR', folder), self.assertRaises(ValueError):
                normalizer.normalize_1es(self.rows)
            for verse, field in (('4', 'greek'), ('6', 'old_greek'), ('7', 'greek')):
                mutated = copy.deepcopy(self.s)
                mutated['records'][verse][field] += ' drift'
                candidate_path = folder / 'mutated-source.json'
                candidate_path.write_text(json.dumps(mutated, ensure_ascii=False))
                with self.subTest(verse=verse, field=field), patch.object(normalizer, 'ESDRAS7_IMPORT', candidate_path):
                    with self.assertRaises(ValueError):
                        normalizer.normalize_1es(copy.deepcopy(self.rows))
        mutated = copy.deepcopy(self.rows)
        mutated[0]['greek'] += ' drift'
        with self.assertRaises(ValueError):
            normalizer.normalize_1es(mutated)

    def test_exact_live_scope_preserves493_other_yaml_records_including5_6_8(self):
        self.assertEqual(len(self.book), 495)
        live = {str(p.relative_to(ROOT)): p.read_bytes() for p in (ROOT / BOOK).rglob('*.yaml')}
        self.assertEqual(set(live), set(self.book))
        all_baseline = all(live[path] == self.book[path] for path in self.c['records'])
        for path, raw in live.items():
            if path in self.c['records'] and not all_baseline:
                self.assertEqual(yaml.safe_load(raw), self.c['records'][path], path)
            else:
                self.assertEqual(raw, self.book[path], path)
        self.assertEqual(len(set(live) - set(self.c['records'])), 493)
        for chapter, count in ((5, 70), (6, 33), (7, 15), (8, 92)):
            self.assertEqual(sum(f'/{chapter:03}/' in path for path in live), count)

    def test_real_complete495_export_changes_only_target_notes_and_meaning(self):
        with tempfile.TemporaryDirectory(prefix='pob-1es7-export-') as tmp:
            folder = Path(tmp)
            for path, raw in self.book.items():
                dest = folder / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)
            with patch.object(exporter, 'APOCRYPHA_ROOT', folder / 'translation/deuterocanon'):
                before = exporter.export_apocrypha_book('1ES')
                for path, record in self.c['records'].items():
                    (folder / path).write_text(yaml.safe_dump(record, allow_unicode=True, sort_keys=False))
                after = exporter.export_apocrypha_book('1ES')
        for exported in (before, after):
            self.assertEqual([ch['chapter'] for ch in exported['chapters']], list(range(1, 10)))
            self.assertEqual(sum(len(ch['verses']) for ch in exported['chapters']), 495)
        chapter = after['chapters'][6]
        self.assertEqual([v['verse'] for v in chapter['verses']], list(range(1, 16)))
        for v in range(1, 16):
            record = self.c['records'].get(verse_path(v), yaml.safe_load(self.book[verse_path(v)]))
            translation = record['translation']
            expected = {'verse': v, 'text': translation['text']}
            if translation.get('footnotes'):
                expected['footnotes'] = translation['footnotes']
            self.assertEqual(chapter['verses'][v-1], expected)
        changed = {b['verse'] for a, b in zip(before['chapters'][6]['verses'], chapter['verses']) if a != b}
        self.assertEqual(changed, set(WORDS))
        restored = copy.deepcopy(after)
        restored['chapters'][6] = before['chapters'][6]
        self.assertEqual(restored, before)
        if all(yaml.safe_load((ROOT / path).read_bytes()) == record for path, record in self.c['records'].items()):
            self.assertEqual(exporter.export_apocrypha_book('1ES'), after)


if __name__ == '__main__':
    unittest.main()
