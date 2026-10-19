"""Live chapter6 printed-import successor; earlier proofs replay immutably."""
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

BASE = '08a8a4cc05fcb8eb91580e01fb506a90de9799a9'
RECEIPT_COMMIT = '41ee5f853caacef940590c4136a4947901ed39e8'
RECEIPT_SHA = '9d04bce5f7b00e2b71b1db86e4e1ac66157d595067d89c738fad79deca4ad604'
BOOK = 'translation/deuterocanon/1_esdras'
CORPUS = 'sources/lxx/swete/final_corpus_adjudicated/1ES.jsonl'
NORMALIZED = 'sources/lxx/swete/final_corpus_normalized/1ES.jsonl'
PREFIX = 'sources/textual_restoration/'
SOURCE = PREFIX + 'candidates/1esdras6_source_partition.2026-10-19.v1.json'
ENGLISH = PREFIX + 'candidates/1esdras6_english_partition.2026-10-19.v1.json'
CANDIDATE = PREFIX + 'candidates/1esdras6_application.2026-10-19.v1.json'
EVIDENCE = PREFIX + 'comparisons/1esdras6_application.2026-10-19.v1.json'
AFFECTED = {1, 8, 9, 10, 24, 26, 30, 31}
ARCHIVES = ('source', 'translation', 'lexical_decisions', 'theological_decisions',
            'status', 'revision_pass', 'cross_check')


def historical(path):
    return subprocess.check_output(['git', '--no-replace-objects', 'show', f'{BASE}:{path}'], cwd=ROOT)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def verse_path(verse):
    return f'{BOOK}/006/{verse:03}.yaml'


class EsdrasSixPartitionTests(unittest.TestCase):
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

    def test_exact_eight_full_records_schema_history_and_note_anchors(self):
        self.assertEqual(self.c['baseline_commit'], BASE)
        self.assertEqual(self.s['read_commit'], BASE)
        self.assertEqual(self.e['baseline_commit'], BASE)
        self.assertNotIn('quarantine', self.c)  # No canonical file is removed.
        self.assertEqual(set(self.s['records']), {str(v) for v in range(1, 34)})
        self.assertEqual(set(self.c['records']), {verse_path(v) for v in AFFECTED})
        self.assertEqual(set(self.e['records']), {str(v) for v in AFFECTED})
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        for v in AFFECTED:
            path = verse_path(v)
            old, new = yaml.safe_load(self.book[path]), self.c['records'][path]
            errors = [f'{list(error.path)}: {error.message}' for error in validator.iter_errors(new)]
            self.assertEqual(errors, [], path)
            for key in ('id', 'reference'):
                self.assertEqual(new[key], old[key], (path, key))
            if v != 24:
                self.assertEqual(new['ai_draft'], old['ai_draft'])
                self.assertNotIn('draft_receipt_provenance', new)
            else:
                self.assertNotIn('ai_draft', old)
                original = subprocess.check_output(
                    ['git', '--no-replace-objects', 'show', f'{RECEIPT_COMMIT}:{path}'], cwd=ROOT)
                self.assertEqual(sha(original), RECEIPT_SHA)
                self.assertEqual(new['ai_draft'], yaml.safe_load(original)['ai_draft'])
                provenance = new['draft_receipt_provenance']
                self.assertEqual(provenance['baseline_commit'], BASE)
                self.assertEqual(provenance['source_commit'], RECEIPT_COMMIT)
                self.assertEqual(provenance['source_record_id'], '1ES.6.24')
                self.assertEqual(provenance['source_path'], path)
                self.assertEqual(provenance['source_sha256'], sha(original))
                self.assertTrue(provenance['target_historical_receipt_missing'])
                self.assertTrue(provenance['receipt_restored_unchanged'])
                self.assertFalse(provenance['certifies_current_record'])
                self.assertIn('receipt', new['source']['note'].lower())
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
            if v == 24:
                changed.update({'ai_draft', 'draft_receipt_provenance'})
            self.assertEqual({k: val for k, val in new.items() if k not in changed},
                             {k: val for k, val in old.items() if k not in changed}, path)
        active1 = json.dumps({k: self.c['records'][verse_path(1)][k]
                              for k in ('translation', 'lexical_decisions', 'theological_decisions')}, ensure_ascii=False)
        self.assertNotIn('οἱ οἱ', active1)
        self.assertNotIn('likely a scribal or transmission irregularity', active1)
        self.assertNotIn("duplicated article in Swete's text", active1)
        active10 = json.dumps(self.c['records'][verse_path(10)]['translation'], ensure_ascii=False)
        self.assertNotIn('ends abruptly', active10)
        self.assertNotIn('unfinished form', active10)
        self.assertNotIn('and—', self.c['records'][verse_path(10)]['translation']['text'])
        self.assertRegex(self.c['records'][verse_path(30)]['translation']['text'].lower(), r'\b(?:life|lives)\b')

    def test_every_old_nonspace_codepoint_has_exact_retained_replaced_or_quarantined_owner(self):
        old = {v: yaml.safe_load(self.book[verse_path(v)])['source']['text'] for v in range(1, 34)}
        additions, corrections, retained, quarantined = [], [], [], []
        definitions = {item['addition_key']: item for item in self.s['addition_definitions']}
        for v in range(1, 34):
            unit, parts = self.s['records'][str(v)], []
            for part in unit['source_parts']:
                kind = part['kind']
                if kind == 'printed_source_addition':
                    self.assertEqual(part, definitions[part['addition_key']])
                    additions.append((v, part['addition_key'], part['greek']))
                    parts.append(part['greek'])
                    continue
                self.assertIn(kind, ('existing_source_slice', 'printed_orthographic_correction'))
                ov = part['old_verse']
                self.assertIn(ov, old)
                self.assertEqual(part['old_source_id'], f'1ES.6.{ov}')
                start, end = part['start_codepoint_inclusive'], part['end_codepoint_exclusive']
                self.assertTrue(0 <= start < end <= len(old[ov]))
                text = old[ov][start:end]
                self.assertEqual(text, part['old_text'])
                self.assertEqual(sha(text.encode()), part['old_slice_sha256'])
                retained.extend((ov, i) for i in range(start, end) if not old[ov][i].isspace())
                if kind == 'printed_orthographic_correction':
                    self.assertEqual(sha(part['replacement_text'].encode()), part['replacement_sha256'])
                    corrections.append(part)
                    parts.append(part['replacement_text'])
                else:
                    parts.append(text.strip())
            self.assertEqual(' '.join(parts), unit['greek'])
        self.assertEqual(additions, [
            (10, 'foundation_question_tail', 'τὰ ἔργα ταῦτα ἐθεμελιοῦτε;'),
            (26, 'permit_building_on_site_tail', 'τὸν οἶκον τοῦ κυρίου ἐκεῖνον οἰκοδομεῖν ἐπὶ τοῦ τόπου.'),
        ])
        self.assertEqual(len(definitions), 2)
        self.assertEqual(len(self.s['addition_definitions']), 2)
        self.assertEqual(corrections, self.s['orthographic_correction_definitions'])
        self.assertEqual(len(corrections), 1)
        correction = corrections[0]
        self.assertEqual((correction['old_verse'], correction['start_codepoint_inclusive'],
                          correction['end_codepoint_exclusive'], correction['old_text'],
                          correction['replacement_text']), (24, 30, 32, 'οὓ', 'οὗ'))
        slices = self.s['quarantined_source_slices']
        self.assertEqual([(p['old_verse'], p['start_codepoint_inclusive'], p['end_codepoint_exclusive'], p['old_text'])
                          for p in slices], [(1, 94, 97, 'οἱ '), (24, 0, 30, 'θύουσιν διὰ πυρὸς ἐνδελεχοῦς, ')])
        for part in slices:
            self.assertEqual(part['kind'], 'quarantined_source_slice')
            ov = part['old_verse']
            self.assertEqual(part['old_source_id'], f'1ES.6.{ov}')
            start, end = part['start_codepoint_inclusive'], part['end_codepoint_exclusive']
            self.assertTrue(0 <= start < end <= len(old[ov]))
            self.assertEqual(old[ov][start:end], part['old_text'])
            self.assertEqual(sha(part['old_text'].encode()), part['old_slice_sha256'])
            quarantined.extend((ov, i) for i in range(start, end) if not old[ov][i].isspace())
        expected = [(v, i) for v in range(1, 34) for i, char in enumerate(old[v]) if not char.isspace()]
        self.assertEqual(len(retained + quarantined), len(set(retained + quarantined)))
        self.assertEqual(sorted(retained + quarantined), expected)
        excluded = set(quarantined)
        self.assertEqual(retained, [key for key in expected if key not in excluded])
        self.assertTrue(self.s['records']['8']['greek'].endswith('διὰ λίθων ξυστῶν πολυτελῶν, ξύλων τιθεμένων ἐν τοῖς οἴκοις,'))
        self.assertTrue(self.s['records']['9']['greek'].startswith('καὶ τὰ ἔργα ἐκεῖνα'))
        self.assertTrue(self.s['records']['24']['greek'].startswith('οὗ τὸ ὕψος'))
        self.assertTrue(self.s['records']['30']['greek'].endswith('ζωῆς.'))
        self.assertTrue(self.s['records']['31']['greek'].startswith('καὶ προστάξαι'))

    def test_historical_inputs_reviewed_pins_and_prior_frozen_proofs_remain_unchanged(self):
        evidence = json.loads((ROOT / EVIDENCE).read_text())
        self.assertEqual(evidence['baseline_commit'], BASE)
        self.assertTrue({SOURCE, ENGLISH, CANDIDATE, NORMALIZED,
                         'docs/1ESDRAS_6_PARTITION_REPAIR_2026-10-19.md',
                         'tools/build_normalized_deuterocanon_corpus.py',
                         'tests/test_1esdras6_partition_application.py',
                         'docs/TEXTUAL_RESTORATION_APPROACH_REVIEW_2026-09-04.md',
                         '.github/workflows/corpus-integrity.yml',
                         'tools/textual_restoration/replay_historical_tests.py'}
                        <= set(evidence['reviewed_file_pins']))
        self.assertIn(CORPUS, evidence['historical_input_pins'])
        manifest = ''.join(path + '\t' + sha(raw) + '\n'
                           for path, raw in sorted(self.book.items()) if '/006/' in path)
        self.assertEqual(sha(manifest.encode()), evidence['canonical_baseline_manifest_sha256'])
        for path, pin in evidence['historical_input_pins'].items():
            self.assertEqual(sha(historical(path)), pin, path)
        self.assertEqual(len(evidence['historical_receipt_inputs']), 1)
        receipt = evidence['historical_receipt_inputs'][0]
        self.assertEqual(receipt['commit'], RECEIPT_COMMIT)
        self.assertEqual(receipt['path'], verse_path(24))
        original = subprocess.check_output(
            ['git', '--no-replace-objects', 'show', f'{RECEIPT_COMMIT}:{verse_path(24)}'], cwd=ROOT)
        self.assertEqual(sha(original), receipt['sha256'])
        self.assertEqual(receipt['sha256'], RECEIPT_SHA)
        for path in evidence['unchanged_live_inputs']:
            self.assertEqual((ROOT / path).read_bytes(), historical(path), path)
        for path, pin in evidence['reviewed_file_pins'].items():
            self.assertEqual(sha((ROOT / path).read_bytes()), pin, path)
        mutable_implementations = {NORMALIZED, 'tools/build_normalized_deuterocanon_corpus.py',
                                  '.github/workflows/corpus-integrity.yml',
                                  'tools/textual_restoration/replay_historical_tests.py',
                                  'tests/test_replay_historical_tests.py',
                                  'docs/TEXTUAL_RESTORATION_APPROACH_REVIEW_2026-09-04.md'}
        for chapter in (5, 8):
            path = PREFIX + f'comparisons/1esdras{chapter}_application.2026-10-19.v1.json'
            self.assertEqual((ROOT / path).read_bytes(), historical(path))
            previous = json.loads(historical(path))
            for frozen_path in set(previous['reviewed_file_pins']) - mutable_implementations:
                self.assertEqual((ROOT / frozen_path).read_bytes(), historical(frozen_path), frozen_path)
        workflow = (ROOT / '.github/workflows/corpus-integrity.yml').read_text()
        for commit in (BASE, RECEIPT_COMMIT, '756074bd3e0bd97c5d849c5ff47125972f4684b2', '97194d2b4c691514373896490110246b0b024219'):
            self.assertIn(f'git fetch --no-tags --depth=1 origin {commit}', workflow)
        for chapter in (5, 8):
            self.assertIn(f'python -m tools.textual_restoration.replay_historical_tests esdras{chapter}_partition', workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_1esdras6_partition_application.py'", workflow)

    def test_normalized495_scope_source_loader_generation_and_drift_guards(self):
        self.assertEqual(len(self.rows), 496)
        self.assertEqual(len(self.normalized), 495)
        self.assertEqual(len(self.dropped), 1)
        self.assertIn('145', self.dropped[0])
        before = {(int(r['chapter']), int(r['verse'])): r for r in self.previous_normalized}
        after = {(int(r['chapter']), int(r['verse'])): r for r in self.normalized}
        self.assertEqual(set(after), set(before))
        self.assertEqual({key for key in after if after[key] != before[key]}, {(6, v) for v in AFFECTED})
        self.assertEqual([int(r['verse']) for r in self.normalized if int(r['chapter']) == 6], list(range(1, 34)))
        for v in AFFECTED:
            row = after[(6, v)]
            self.assertEqual(row['greek'], self.s['records'][str(v)]['greek'])
            self.assertEqual(row['confidence'], 'medium')
            self.assertEqual(row['adjudication']['confidence'], 'medium')
            self.assertNotIn('similarity', row)
            self.assertFalse(any(k.startswith('pre_adjudication') for k in row))
            self.assertEqual(row['source_correction_history'][-1]['record'], before[(6, v)])
            self.assertFalse(row['source_correction_history'][-1]['certifies_corrected_record'])
        with tempfile.TemporaryDirectory(prefix='pob-1es6-source-') as tmp:
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
            units = {r.verse: r for r in loaded if r.chapter == 6}
            self.assertEqual(set(units), set(range(1, 34)))
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

    def test_exact_live_canonical_scope_preserves_all487_unrelated_records(self):
        self.assertEqual(len(self.book), 495)
        live = {str(p.relative_to(ROOT)): p.read_bytes() for p in (ROOT / BOOK).rglob('*.yaml')}
        self.assertEqual(set(live), set(self.book))
        # Exactly the complete baseline or complete applied state is accepted;
        # the parent separately verifies actual application before publication.
        all_baseline = all(live[path] == self.book[path] for path in self.c['records'])
        for path, raw in live.items():
            if path in self.c['records'] and not all_baseline:
                self.assertEqual(yaml.safe_load(raw), self.c['records'][path], path)
            else:
                self.assertEqual(raw, self.book[path], path)
        self.assertEqual(len(set(live) - set(self.c['records'])), 487)
        self.assertEqual(sum('/005/' in path for path in live), 70)
        self.assertEqual(sum('/006/' in path for path in live), 33)
        self.assertEqual(sum('/008/' in path for path in live), 92)

    def test_real495_unit_export_updates_only_chapter6_and_complete_note_objects(self):
        with tempfile.TemporaryDirectory(prefix='pob-1es6-export-') as tmp:
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
        chapter = next(ch for ch in after['chapters'] if ch['chapter'] == 6)
        self.assertEqual([v['verse'] for v in chapter['verses']], list(range(1, 34)))
        for v in range(1, 34):
            record = self.c['records'].get(verse_path(v), yaml.safe_load(self.book[verse_path(v)]))
            translation = record['translation']
            expected = {'verse': v, 'text': translation['text']}
            if translation.get('footnotes'):
                expected['footnotes'] = translation['footnotes']
            self.assertEqual(chapter['verses'][v-1], expected)
        restored = copy.deepcopy(after)
        restored['chapters'][5] = before['chapters'][5]
        self.assertEqual(restored, before)
        applied = all(yaml.safe_load((ROOT / path).read_bytes()) == record
                      for path, record in self.c['records'].items())
        if applied:
            self.assertEqual(exporter.export_apocrypha_book('1ES'), after)


if __name__ == '__main__':
    unittest.main()
