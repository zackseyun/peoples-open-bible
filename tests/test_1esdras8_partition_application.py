"""Printed-source completeness, not a new ancient reading or a layout change."""
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

BASE = '97194d2b4c691514373896490110246b0b024219'
BOOK = 'translation/deuterocanon/1_esdras'
CORPUS = 'sources/lxx/swete/final_corpus_adjudicated/1ES.jsonl'
NORMALIZED = 'sources/lxx/swete/final_corpus_normalized/1ES.jsonl'
PREFIX = 'sources/textual_restoration/'
SOURCE = PREFIX + 'candidates/1esdras8_source_partition.2026-10-19.v1.json'
ENGLISH = PREFIX + 'candidates/1esdras8_english_partition.2026-10-19.v1.json'
CANDIDATE = PREFIX + 'candidates/1esdras8_application.2026-10-19.v1.json'
EVIDENCE = PREFIX + 'comparisons/1esdras8_application.2026-10-19.v1.json'
AFFECTED = {13, 14, 17, 18, 25, *range(39, 63), *range(76, 93)}
ARCHIVES = ('source', 'translation', 'lexical_decisions', 'theological_decisions',
            'status', 'revision_pass', 'cross_check')


def historical(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class EsdrasPartitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads((ROOT / CANDIDATE).read_text())
        cls.s = json.loads((ROOT / SOURCE).read_text())
        cls.e = json.loads((ROOT / ENGLISH).read_text())
        archive = subprocess.check_output(['git', 'archive', BASE, BOOK], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            cls.book = {m.name: tar.extractfile(m).read() for m in tar.getmembers()
                        if m.isfile() and m.name.endswith('.yaml')}
        cls.raw = historical(CORPUS)
        cls.rows = [json.loads(x) for x in cls.raw.splitlines()]
        cls.normalized, dropped = normalizer.normalize_1es(copy.deepcopy(cls.rows))
        assert not dropped

    def test_exact_full_records_schema_metadata_and_note_anchors(self):
        self.assertEqual(self.c['baseline_commit'], BASE)
        self.assertEqual(self.s['read_commit'], BASE)
        self.assertEqual(self.e['baseline_commit'], BASE)
        self.assertEqual(set(self.s['records']), {str(v) for v in range(1, 93)})
        paths = {f'{BOOK}/008/{v:03}.yaml' for v in AFFECTED}
        self.assertEqual(set(self.c['records']), paths)
        self.assertEqual(set(self.e['records']), {str(v) for v in AFFECTED})
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        for v in AFFECTED:
            path = f'{BOOK}/008/{v:03}.yaml'
            old, new = yaml.safe_load(self.book[path]), self.c['records'][path]
            errors = [f'{list(error.path)}: {error.message}' for error in validator.iter_errors(new)]
            self.assertEqual(errors, [], path)
            self.assertEqual(new['id'], old['id'])
            self.assertEqual(new['reference'], old['reference'])
            if 'ai_draft' in old:
                self.assertEqual(new['ai_draft'], old['ai_draft'])
                self.assertNotIn('draft_receipt_provenance', new)
            else:
                origin = {41:42, 85:86, 87:88}[v]
                origin_path = f'{BOOK}/008/{origin:03}.yaml'
                self.assertEqual(new['ai_draft'], yaml.safe_load(self.book[origin_path])['ai_draft'])
                provenance = new['draft_receipt_provenance']
                self.assertEqual(provenance['source_path'], origin_path)
                self.assertEqual(provenance['source_sha256'], sha(self.book[origin_path]))
                self.assertTrue(provenance['target_historical_receipt_missing'])
                self.assertTrue(provenance['receipt_relocated_unchanged'])
                self.assertFalse(provenance['certifies_current_record'])
            self.assertEqual(new['source']['edition'], old['source']['edition'])
            self.assertEqual(new['source']['text'], self.s['records'][str(v)]['greek'])
            self.assertEqual(new['source']['pages'], self.s['records'][str(v)]['source_pages'])
            self.assertNotIn('parallel_sources', new['source'])
            self.assertEqual(new['source']['confidence'], 'medium')
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
            text = new['translation']['text']
            marks = re.findall(r'\[([a-z])\]', text)
            notes = new['translation'].get('footnotes', [])
            self.assertEqual(marks, [n['marker'] for n in notes], path)
            self.assertEqual(len(marks), len(set(marks)), path)
            self.assertEqual(marks, [chr(97+i) for i in range(len(marks))], path)
            changed = {*ARCHIVES, 'review_history', 'revisions'}
            if 'ai_draft' not in old:
                changed.update({'ai_draft', 'draft_receipt_provenance'})
            self.assertEqual({k: val for k, val in new.items() if k not in changed},
                             {k: val for k, val in old.items() if k not in changed})

    def test_historical_inputs_and_reviewed_candidate_pins(self):
        evidence = json.loads((ROOT / EVIDENCE).read_text())
        self.assertEqual(evidence['baseline_commit'], BASE)
        self.assertTrue({SOURCE, ENGLISH, CANDIDATE, NORMALIZED,
                         'docs/1ESDRAS_8_PARTITION_REPAIR_2026-10-19.md',
                         'tools/build_normalized_deuterocanon_corpus.py',
                         'tests/test_1esdras8_partition_application.py'}
                        <= set(evidence['reviewed_file_pins']))
        self.assertIn(CORPUS, evidence['historical_input_pins'])
        manifest = ''.join(path + '\t' + sha(raw) + '\n'
                           for path, raw in sorted(self.book.items()) if '/008/' in path)
        self.assertEqual(sha(manifest.encode()), evidence['canonical_baseline_manifest_sha256'])
        for path, pin in evidence['historical_input_pins'].items():
            self.assertEqual(sha(historical(path)), pin, path)
        for path in evidence['unchanged_live_inputs']:
            self.assertEqual((ROOT / path).read_bytes(), historical(path), path)
        for path, pin in evidence['reviewed_file_pins'].items():
            self.assertEqual(sha((ROOT / path).read_bytes()), pin, path)
        workflow = (ROOT / '.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn(f'git fetch --no-tags --depth=1 origin {BASE}', workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_1esdras8_partition_application.py'", workflow)

    def test_every_existing_nonspace_codepoint_consumed_once_in_order(self):
        old = {v: yaml.safe_load(self.book[f'{BOOK}/008/{v:03}.yaml'])['source']['text']
               for v in range(1,93)}
        consumed, restored = [], []
        for v in range(1,93):
            unit = self.s['records'][str(v)]
            parts = []
            for part in unit['source_parts']:
                if part['kind'] == 'existing_source_slice':
                    ov = part['old_verse']
                    start, end = part['start_codepoint_inclusive'], part['end_codepoint_exclusive']
                    self.assertTrue(0 <= start < end <= len(old[ov]))
                    parts.append(old[ov][start:end].strip())
                    consumed.extend((ov,i) for i in range(start,end) if not old[ov][i].isspace())
                else:
                    self.assertEqual(part['kind'], 'printed_restoration')
                    restored.append(part['restoration_id'])
                    self.assertEqual(part['text'], self.s['restorations'][part['restoration_id']]['greek'])
                    parts.append(part['text'])
            self.assertEqual(' '.join(parts), unit['greek'])
        expected = [(v,i) for v in range(1,93) for i,char in enumerate(old[v]) if not char.isspace()]
        self.assertEqual(consumed, expected)
        self.assertEqual(restored, ['25b', '92'])

    def test_normalized_source_loader_complete_scope_and_omissions(self):
        self.assertEqual(len(self.rows), len(self.normalized))
        changed = {(int(a['chapter']), int(a['verse']))
                   for a, b in zip(self.normalized, self.rows) if a != b}
        self.assertEqual(changed, {(8, v) for v in AFFECTED})
        self.assertEqual([int(r['verse']) for r in self.normalized if int(r['chapter']) == 8], list(range(1,93)))
        for row, old in zip(self.normalized, self.rows):
            if (int(row['chapter']), int(row['verse'])) not in changed:
                self.assertEqual(row, old)
                continue
            self.assertNotIn('similarity', row)
            self.assertNotIn('pre_adjudication', row)
            self.assertFalse(any(k.startswith('pre_adjudication') for k in row))
            self.assertEqual(row['confidence'], 'medium')
            self.assertEqual(row['adjudication']['confidence'], 'medium')
            self.assertEqual(row['source_correction_history'][-1]['record'], old)
            self.assertFalse(row['source_correction_history'][-1]['certifies_corrected_record'])
        with tempfile.TemporaryDirectory(prefix='pob-1es-source-') as tmp:
            folder = Path(tmp)
            with patch.object(normalizer, 'OUT_DIR', folder):
                normalizer.write_book('1ES', self.normalized)
            self.assertEqual((folder / '1ES.jsonl').read_bytes(), (ROOT / NORMALIZED).read_bytes())
            with patch.object(lxx_swete, 'NORMALIZED_CORPUS_DIR', folder):
                loaded = list(lxx_swete.iter_source_verses('1ES'))
        units = {r.verse: r for r in loaded if r.chapter == 8}
        self.assertEqual(set(units), set(range(1,93)))
        for v in AFFECTED:
            self.assertEqual(units[v].greek_text, self.s['records'][str(v)]['greek'])
            self.assertEqual(units[v].source_confidence, 'medium')
        self.assertIn('δοξάσαι τὸν οἶκον αὐτοῦ τὸν ἐν Ἰερουσαλήμ', units[25].greek_text)
        self.assertIn('ὥρκισεν', units[92].greek_text)
        self.assertTrue(units[92].greek_text.endswith('καὶ ὤμοσαν.'))
        self.assertTrue(units[83].greek_text.endswith('σὺ γάρ, Κύριε, ὁ κουφίσας τὰς ἁμαρτίας ἡμῶν,'))
        self.assertTrue(units[84].greek_text.startswith('ἔδωκας'))

    def test_scoped_generation_and_historical_drift_guard(self):
        with tempfile.TemporaryDirectory(prefix='pob-1es-generate-') as tmp:
            folder = Path(tmp)
            (folder / 'SUMMARY.md').write_text('unchanged summary\n')
            (folder / 'WIS.jsonl').write_text('unrelated override\n')
            with patch.object(normalizer, 'OUT_DIR', folder), redirect_stdout(io.StringIO()):
                self.assertEqual(normalizer.main(['--book', '1ES']), 0)
            self.assertEqual({p.name for p in folder.iterdir()}, {'1ES.jsonl', 'WIS.jsonl', 'SUMMARY.md'})
            self.assertEqual((folder / 'SUMMARY.md').read_text(), 'unchanged summary\n')
            self.assertEqual((folder / 'WIS.jsonl').read_text(), 'unrelated override\n')
            (folder / '1ES.jsonl').write_text('{}\n')
            with patch.object(normalizer, 'SRC_DIR', folder), self.assertRaises(ValueError):
                normalizer.normalize_1es(self.rows)

    def test_real_whole_book_export_and_live_scope(self):
        self.assertEqual(len(self.book), 496)
        live = {str(p.relative_to(ROOT)): p.read_bytes() for p in (ROOT / BOOK).rglob('*.yaml')}
        self.assertEqual(set(live), set(self.book))
        for path, raw in live.items():
            if path in self.c['records']:
                self.assertIn(yaml.safe_load(raw), [yaml.safe_load(self.book[path]), self.c['records'][path]])
            else:
                self.assertEqual(raw, self.book[path], path)
        with tempfile.TemporaryDirectory(prefix='pob-1es-export-') as tmp:
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
        # The real pre-existing export withholds chapter5: its IDs are1..70,145.
        # Do not silently drop145, synthesize71..144, or call this a complete export.
        self.assertEqual([ch['chapter'] for ch in before['chapters']], [1,2,3,4,6,7,8,9])
        self.assertEqual([ch['chapter'] for ch in after['chapters']], [1,2,3,4,6,7,8,9])
        self.assertEqual(sum(len(ch['verses']) for ch in before['chapters']), 425)
        self.assertEqual(sum(len(ch['verses']) for ch in after['chapters']), 425)
        chapter5 = {int(Path(path).stem) for path in self.book if '/005/' in path}
        self.assertEqual(chapter5, {*range(1,71), 145})
        a = next(ch for ch in before['chapters'] if ch['chapter'] == 8)['verses']
        b = next(ch for ch in after['chapters'] if ch['chapter'] == 8)['verses']
        self.assertEqual([x['verse'] for x in a], list(range(1,93)))
        self.assertEqual([x['verse'] for x in b], list(range(1,93)))
        expected = {int(path.rsplit('/',1)[1].split('.')[0]) for path, record in self.c['records'].items()
                    if record['translation'] != yaml.safe_load(self.book[path])['translation']}
        self.assertEqual({x['verse'] for x, y in zip(a,b) if x != y}, expected)
        for v in AFFECTED:
            t = self.c['records'][f'{BOOK}/008/{v:03}.yaml']['translation']
            expected_verse = {'verse': v, 'text': t['text']}
            if t['footnotes']:
                expected_verse['footnotes'] = t['footnotes']
            self.assertEqual(b[v-1], expected_verse)
        self.assertIn('glorify', b[24]['text'])
        self.assertIn('swear', b[91]['text'])
        self.assertTrue(b[91]['text'].endswith('and they swore.'))
        self.assertIn('For you, Lord, who have lightened our sins,', b[82]['text'])
        self.assertTrue(b[83]['text'].startswith('have given us'))
        self.assertIn('we are with you to act with strength', b[90]['text'])
        restored = copy.deepcopy(after)
        index = next(i for i,ch in enumerate(restored['chapters']) if ch['chapter'] == 8)
        restored['chapters'][index] = before['chapters'][index]
        self.assertEqual(restored, before)


if __name__ == '__main__':
    unittest.main()
