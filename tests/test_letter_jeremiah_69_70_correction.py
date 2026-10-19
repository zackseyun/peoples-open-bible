"""Two scan-fidelity repairs; no new ancient reading or reader-layout changes."""
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

import yaml
from jsonschema import Draft202012Validator
from tools import export_mobile_bible as exporter, lxx_swete

ROOT = Path(__file__).resolve().parents[1]
BASE = 'b388ce5089ea64ecd3adac354dbd1118c7dbea85'
BOOK = 'translation/deuterocanon/letter_of_jeremiah'
CORPUS = 'sources/lxx/swete/final_corpus_adjudicated/LJE.jsonl'
CANDIDATE = 'sources/textual_restoration/candidates/letter_jeremiah_69_70.2026-10-19.v1.json'
EVIDENCE = 'sources/textual_restoration/comparisons/letter_jeremiah_69_70.2026-10-19.v1.json'
ARCHIVES = ('source', 'translation', 'lexical_decisions', 'theological_decisions',
            'status', 'revision_pass', 'cross_check')
GREEK = {
    69: 'Ὥσπερ γὰρ ἐν σικυηράτῳ προβασκάνιον οὐδὲν φυλάσσον, οὕτως οἱ θεοὶ αὐτῶν εἰσὶν ξύλινοι καὶ περίχρυσοι καὶ περιάργυροι.',
    70: 'τὸν αὐτὸν τρόπον καὶ τῇ ἐν κήπῳ ῥάμνῳ, ἐφ’ ἧς πᾶν τὸ ὄρνεον ἐπικάθηται, ὡσαύτως δὲ καὶ νεκρῷ ἐρριμμένῳ ἐν σκότει ἀφωμοίωνται οἱ θεοὶ αὐτῶν ξύλινοι καὶ περίχρυσοι καὶ περιάργυροι.',
}
TEXT = {
    69: 'For just as a scarecrow in a cucumber patch guards nothing[a], so their gods are wooden and overlaid with gold and silver.',
    70: 'In the same way, their wooden gods overlaid with gold and silver are like a thornbush[a] in a garden, on which every bird sits, and also like a dead body thrown out in the dark.',
}
NOTES = {
    69: "Or 'protective charm.' The Greek names a protective object, here one that guards nothing.",
    70: "Greek names a thorny shrub; 'buckthorn' is another possible rendering.",
}


def historical(path):
    return subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def serialized_corpus(old, replacements):
    """Preserve every unrelated JSONL line byte-for-byte."""
    out = []
    for line in old.splitlines(keepends=True):
        record = json.loads(line)
        replacement = replacements.get(str(record['verse']))
        out.append((json.dumps(replacement, ensure_ascii=False) + '\n').encode()
                   if replacement else line)
    return b''.join(out)


class LetterJeremiahCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.c = json.loads((ROOT / CANDIDATE).read_text())
        raw = subprocess.check_output(['git', 'archive', BASE, BOOK], cwd=ROOT)
        with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
            cls.book = {m.name: archive.extractfile(m).read() for m in archive.getmembers()
                        if m.isfile() and m.name.endswith('.yaml')}
        cls.corpus_raw = historical(CORPUS)
        cls.corpus = [json.loads(x) for x in cls.corpus_raw.splitlines()]

    def test_complete_records_exact_scope_schema_and_archives(self):
        self.assertEqual(self.c['baseline_commit'], BASE)
        self.assertEqual(set(self.c['records']),
                         {f'{BOOK}/001/{v:03}.yaml' for v in (69, 70)})
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        for v in (69, 70):
            path = f'{BOOK}/001/{v:03}.yaml'
            old = yaml.safe_load(self.book[path])
            new = self.c['records'][path]
            validator.validate(new)
            self.assertEqual(new['source']['text'], GREEK[v])
            self.assertEqual(new['source']['pages'], [407])
            self.assertEqual(new['source']['edition'], old['source']['edition'])
            self.assertEqual(new['source']['language'], 'Greek')
            self.assertEqual(new['source']['confidence'], 'medium')
            self.assertEqual(new['source']['validation'], 'scan_correction_pending_full_review')
            self.assertIn('printed p. 384', new['source']['note'])
            self.assertEqual(new['translation'], {
                'text': TEXT[v], 'philosophy': old['translation']['philosophy'],
                'footnotes': [{'marker': 'a', 'text': NOTES[v], 'reason': 'lexical_alternative'}]})
            self.assertEqual(new['status'], 'draft')
            self.assertEqual(new['cross_check'], {'status': 'needs_review'})
            self.assertNotIn('revision_pass', new)
            entry = new['review_history'][-1]
            self.assertEqual(entry['baseline_commit'], BASE)
            self.assertEqual(entry['baseline_sha256'], sha(self.book[path]))
            self.assertFalse(entry['certifies_this_candidate'])
            self.assertFalse(entry['historical_review_inputs_verified'])
            self.assertEqual(entry['fields'], {key: old[key] for key in ARCHIVES})
            self.assertEqual(new['review_history'][:-1], old.get('review_history', []))
            self.assertEqual(new['revisions'][:-1], old.get('revisions', []))
            revision = new['revisions'][-1]
            self.assertEqual(revision['from'], old['translation']['text'])
            self.assertEqual(revision['to'], TEXT[v])
            self.assertEqual(revision['case_document'], self.c['report'])
            changed = {'source', 'translation', 'lexical_decisions', 'status', 'cross_check',
                       'revision_pass', 'review_history', 'revisions'}
            if v == 70:
                changed.add('theological_decisions')
            self.assertEqual({k: val for k, val in new.items() if k not in changed},
                             {k: val for k, val in old.items() if k not in changed})
            changed_lex = {1, 2} if v == 69 else {1, 4, 5}
            self.assertEqual(len(new['lexical_decisions']), len(old['lexical_decisions']))
            for i, item in enumerate(old['lexical_decisions']):
                if i not in changed_lex:
                    self.assertEqual(new['lexical_decisions'][i], item)
            self.assertEqual(new['lexical_decisions'][1]['source_word'],
                             'προβασκάνιον' if v == 69 else 'ῥάμνῳ')
            self.assertEqual(new['lexical_decisions'][1]['chosen'],
                             'a scarecrow' if v == 69 else 'a thornbush')
            if v == 70:
                # This article was an OCR insertion, not present in the selected print.
                self.assertNotIn('τῷ νεκρῷ', new['source']['text'])
                self.assertEqual(new['lexical_decisions'][4]['source_word'],
                                 'νεκρῷ ἐρριμμένῳ ἐν σκότει')
                self.assertNotIn('lifeless', new['theological_decisions'][0]['chosen_reading'])
                self.assertIn('not literally lifeless', new['theological_decisions'][0]['rationale'])

    def test_frozen_evidence_and_ci_setup(self):
        evidence = json.loads((ROOT / EVIDENCE).read_text())
        self.assertEqual(evidence['baseline_commit'], BASE)
        for path, pin in evidence['historical_input_pins'].items():
            self.assertEqual(sha(historical(path)), pin, path)
        for path, pin in evidence['reviewed_file_pins'].items():
            self.assertEqual(sha((ROOT / path).read_bytes()), pin, path)
        for path in evidence['unchanged_live_inputs']:
            self.assertEqual((ROOT / path).read_bytes(), historical(path), path)
        workflow = (ROOT / '.github/workflows/corpus-integrity.yml').read_text()
        self.assertIn(f'git fetch --no-tags --depth=1 origin {BASE}', workflow)
        self.assertIn("python -m unittest discover -s tests -p 'test_letter_jeremiah_69_70_correction.py'", workflow)

    def test_source_loader_and_corpus_scope(self):
        self.assertEqual(len(self.corpus), 72)
        corrected = serialized_corpus(self.corpus_raw, self.c['corpus_records'])
        rows = [json.loads(x) for x in corrected.splitlines()]
        self.assertEqual([r['verse'] for r, old in zip(rows, self.corpus) if r != old], [69, 70])
        for v in (69, 70):
            row = rows[v - 1]
            self.assertEqual(row['greek'], GREEK[v])
            self.assertEqual(row['source_pages'], [407])
            self.assertEqual(row['validation'], 'scan_correction_pending_full_review')
            self.assertNotIn('similarity', row)
            history = row['source_correction_history'][-1]
            self.assertEqual(history['record'], self.corpus[v - 1])
            self.assertFalse(history['certifies_corrected_record'])
            self.assertEqual(history['baseline_commit'], BASE)
        with tempfile.TemporaryDirectory(prefix='pob-epjer-source-') as tmp:
            folder = Path(tmp)
            (folder / 'LJE.jsonl').write_bytes(corrected)
            with patch.object(lxx_swete, 'FINAL_CORPUS_DIR', folder), \
                    patch.object(lxx_swete, 'NORMALIZED_CORPUS_DIR', folder / 'absent'):
                loaded = list(lxx_swete.iter_source_verses('LJE'))
        self.assertEqual(len(loaded), 72)
        for v in (69, 70):
            self.assertEqual(loaded[v - 1].greek_text, GREEK[v])
            self.assertEqual(loaded[v - 1].source_pages, [407])
            self.assertEqual(loaded[v - 1].source_validation, 'scan_correction_pending_full_review')
            self.assertNotEqual(loaded[v - 1].source_confidence, 'high')

    def test_real_complete_letter_export(self):
        self.assertEqual(len(self.book), 72)
        with tempfile.TemporaryDirectory(prefix='pob-epjer-export-') as tmp:
            folder = Path(tmp)
            for path, raw in self.book.items():
                dest = folder / path
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(raw)
            with patch.object(exporter, 'APOCRYPHA_ROOT', folder / 'translation/deuterocanon'):
                before = exporter.export_apocrypha_book('LJE')
                for path, record in self.c['records'].items():
                    (folder / path).write_text(yaml.safe_dump(record, allow_unicode=True, sort_keys=False))
                after = exporter.export_apocrypha_book('LJE')
        self.assertEqual(len(before['chapters']), 1)
        a = before['chapters'][0]['verses']
        b = after['chapters'][0]['verses']
        self.assertEqual(len(a), 72)
        self.assertEqual(len(b), 72)
        self.assertEqual([x['verse'] for x, y in zip(a, b) if x != y], [69, 70])
        for v in (69, 70):
            self.assertEqual(b[v - 1], {'verse': v, 'text': TEXT[v], 'footnotes': [
                {'marker': 'a', 'text': NOTES[v], 'reason': 'lexical_alternative'}]})
        restored = copy.deepcopy(after)
        restored['chapters'][0]['verses'][68:70] = copy.deepcopy(a[68:70])
        self.assertEqual(restored, before)

    def test_live_tree_is_exact_baseline_or_reviewed_candidate(self):
        live = {str(p.relative_to(ROOT)): p.read_bytes()
                for p in (ROOT / BOOK).rglob('*.yaml')}
        self.assertEqual(set(live), set(self.book))
        for path, raw in live.items():
            if path in self.c['records']:
                self.assertIn(yaml.safe_load(raw),
                              [yaml.safe_load(self.book[path]), self.c['records'][path]])
            else:
                self.assertEqual(raw, self.book[path], path)
        self.assertIn((ROOT / CORPUS).read_bytes(), [
            self.corpus_raw, serialized_corpus(self.corpus_raw, self.c['corpus_records'])])
        for path in ['sources/lxx/swete/transcribed/vol3_p0407.txt',
                     'sources/lxx/swete/transcribed/vol3_p0407.meta.json']:
            self.assertEqual((ROOT / path).read_bytes(), historical(path))


if __name__ == '__main__':
    unittest.main()
