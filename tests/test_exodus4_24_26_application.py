"""Hash-bound encounter disclosure application; not original-wording proof."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest
from unittest.mock import patch

import yaml
from jsonschema import Draft202012Validator
from tools import audit_footnotes
from tools import export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]
BASE = 'b4fdc5b8ae007e9771907e9be692ae6208442b89'
VERSES = (24, 25, 26)
TARGETS = {v: f'translation/ot/exodus/004/{v:03}.yaml' for v in VERSES}
PREFIX = 'sources/textual_restoration/'
CANDIDATES = {v: PREFIX + f'candidates/exodus4_{v}_encounter.2026-10-10.v1.json'
              for v in VERSES}
RECEIPT = PREFIX + 'applications/exodus4_24_26_encounter.2026-10-10.v1.json'
CHANGED_UNITS = [[4, v] for v in VERSES]


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact_sha(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode())


class Exodus42426ApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.before_raw = {v: subprocess.check_output(
            ['git', 'show', f'{BASE}:{TARGETS[v]}'], cwd=ROOT) for v in VERSES}
        cls.before = {v: yaml.safe_load(raw) for v, raw in cls.before_raw.items()}
        cls.current = {v: yaml.safe_load((ROOT / TARGETS[v]).read_text()) for v in VERSES}
        cls.candidates = {v: json.loads((ROOT / CANDIDATES[v]).read_text()) for v in VERSES}
        cls.receipt = json.loads((ROOT / RECEIPT).read_text())

    def test_exact_candidates_schema_source_generation_and_rendering_scope(self):
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        for verse in VERSES:
            with self.subTest(verse=verse):
                record, old = self.current[verse], self.before[verse]
                self.assertEqual(record, self.candidates[verse])
                validator.validate(record)
                for field in ('source', 'ai_draft'):
                    self.assertEqual(record[field], old[field])
                clean = re.sub(r'\[[a-z]\]', '', record['translation']['text'])
                old_clean = re.sub(r'\[[a-z]\]', '', old['translation']['text'])
                expected = old_clean.replace('Then she said', 'At that time she said') if verse == 26 else old_clean
                self.assertEqual(clean, expected)
        self.assertIn('Yahweh', self.current[24]['translation']['text'])
        self.assertNotIn('angel', self.current[24]['translation']['text'])
        self.assertIn('touched his feet', self.current[25]['translation']['text'])

    def test_ten_notes_have_correct_anchors_and_meaningful_alternatives(self):
        anchors = {
            24: ['lodging place[a]', 'Yahweh[b]', 'met him[c]'],
            25: ['his feet[a]', 'with it[b]', 'bridegroom of blood[c]'],
            26: ['let him alone[a]', 'At that time[b]', 'bridegroom of blood[c]', 'circumcision[d]'],
        }
        expected_notes = {
            24: [('night encampment', 'commercial inn'),
                 ('Greek', 'Onkelos', 'angel of the Lord', 'original priority remains uncertain'),
                 ('does not name', 'Moses', 'his son', 'not explicit wording')],
            25: [('not named', 'Moses', 'son', 'divine attacker', 'genitals'),
                 ('caused contact', 'without an explicit object', 'infers the cut foreskin', 'falling'),
                 ('addressee', 'uncertain', "child's circumcision blood", 'alternative versional form')],
            26: [('from him', 'from her', '4Q1', 'masculine-form ending', 'does not identify'),
                 ("Or 'Then.'", 'another utterance', 'may explain', 'uncertain'),
                 ('repeats', 'ritual or emotional sense', 'uncertain'),
                 ('plural', 'circumcisions', 'circumcision rites', 'Singular English', 'with regard to')],
        }
        self.assertEqual(sum(len(r['translation']['footnotes']) for r in self.current.values()), 10)
        for verse in VERSES:
            with self.subTest(verse=verse):
                text = self.current[verse]['translation']['text']
                notes = self.current[verse]['translation']['footnotes']
                markers = list('abcd'[:len(anchors[verse])])
                self.assertEqual(re.findall(r'\[([a-z])\]', text), markers)
                self.assertEqual([n['marker'] for n in notes], markers)
                self.assertEqual(audit_footnotes.audit_one(ROOT / TARGETS[verse])['status'], 'ok')
                for anchor in anchors[verse]:
                    self.assertIn(anchor, text)
                for note, phrases in zip(notes, expected_notes[verse], strict=True):
                    for phrase in phrases:
                        self.assertIn(phrase, note['text'])

    def test_exact_seven_field_archives_and_preserved_revisions(self):
        fields = ['status', 'translation', 'lexical_decisions', 'theological_decisions',
                  'revision_pass', 'cross_check', 'ai_draft']
        for verse in VERSES:
            with self.subTest(verse=verse):
                record, old = self.current[verse], self.before[verse]
                history = record['review_history']
                self.assertEqual([h['field'] for h in history], fields)
                self.assertEqual({h['field']: h['value'] for h in history}, {f: old[f] for f in fields})
                for entry in history:
                    self.assertEqual(entry['archived_from_baseline_sha256'], sha(self.before_raw[verse]))
                    self.assertFalse(entry['certifies_this_candidate'])
                previous = old.get('revisions', [])
                self.assertEqual(previous, [])
                self.assertEqual(record['revisions'][:-1], previous)
                self.assertEqual(record['revisions'][-1]['from'], old['translation']['text'])
                self.assertEqual(record['revisions'][-1]['to'], record['translation']['text'])
                self.assertEqual(record['status'], 'draft')
                self.assertEqual(record['cross_check'], {'status': 'needs_review'})
                self.assertNotIn('revision_pass', record)

    def test_connected_rationale_and_source_comparison_boundaries(self):
        lex = {v: {d['source_word']: d for d in self.current[v]['lexical_decisions']} for v in VERSES}
        encounter = lex[24]['וַיִּפְגְּשֵׁהוּ']['rationale']
        for phrase in ('פגש (pgš)', 'Qal wayyiqtol', '4:27', 'not פגע', 'death clause'):
            self.assertIn(phrase, encounter)
        for phrase in ('Hiphil', 'נגע', 'implicit object', 'different action'):
            self.assertIn(phrase, lex[25]['וַתַּגַּע']['rationale'])
        self.assertEqual(lex[26]['אָז']['chosen'], 'At that time')
        for phrase in ('qatal', 'Then remains viable', 'explanation is not proved'):
            self.assertIn(phrase, lex[26]['אָז']['rationale'])
        self.assertIn('not a new narrative wayyiqtol', lex[26]['אָמְרָה']['rationale'])
        for phrase in ('OSHB tag', 'first-person plural', 'not authority', 'nun-vav', 'feminine ending'):
            self.assertIn(phrase, lex[26]['מִמֶּנּוּ']['rationale'])
        revised_words = {24: {'וַיִּפְגְּשֵׁהוּ', 'יְהוָה'},
                         25: {'וַתַּגַּע', 'לְרַגְלָיו', 'חֲתַן דָּמִים'},
                         26: set(lex[26])}
        for verse in VERSES:
            for old in self.before[verse]['lexical_decisions']:
                if old['source_word'] not in revised_words[verse]:
                    self.assertEqual(lex[verse][old['source_word']], old)
            record = self.current[verse]
            for key in ('source_changed', 'original_meaning_settled', 'publication_approved'):
                self.assertFalse(record['source_audit'][key])
            self.assertTrue(record['source_audit']['no_fresh_halot_consultation'])
            comparison = record['textual_comparison']
            self.assertIn('unresolved', comparison['historical_priority'])
            for key in ('fresh_image_reading', 'novel_reading_demonstrated', 'canon_changed', 'publication_approved'):
                self.assertFalse(comparison[key])
        assessment = json.loads((ROOT / self.receipt['assessment']).read_text())
        contract = json.loads((ROOT / self.receipt['contract']).read_text())
        self.assertIn('Line2', contract['source_controls']['dss_body']['preservation'])
        self.assertIn('wholly supplied', contract['source_controls']['dss_body']['preservation'])
        self.assertIn('not4:24 evidence', contract['source_controls']['dss_body']['preservation'])
        self.assertEqual(assessment['independent_comparison']['status'], 'completed')
        self.assertFalse(assessment['independent_comparison']['application_approved'])
        for key in ('fresh_manuscript_reading', 'novel_reading_demonstrated', 'source_changed',
                    'original_priority_settled', 'canon_changed', 'publication_approved'):
            self.assertFalse(assessment['boundaries'][key])

    def test_actual_full_exodus_export_isolates_three_units_and_keeps_all_notes(self):
        after = exporter.export_book('EXO')
        loader = exporter.load_translation_record
        def baseline_loader(code, chapter, verse):
            if code == 'EXO' and chapter == 4 and verse in self.before:
                return self.before[verse]
            return loader(code, chapter, verse)
        with patch.object(exporter, 'load_translation_record', side_effect=baseline_loader):
            before = exporter.export_book('EXO')
        def index(book):
            return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 40)
        self.assertEqual(len(before['chapters']), 40)
        self.assertEqual(len(a), 1213)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([list(k) for k in a if a[k] != b[k]], CHANGED_UNITS)
        for verse in VERSES:
            self.assertEqual(a[(4, verse)]['text'], self.current[verse]['translation']['text'])
            self.assertEqual(a[(4, verse)]['footnotes'], self.current[verse]['translation']['footnotes'])
        self.assertEqual(compact_sha(before), self.receipt['preflight']['export_before_sha256'])
        self.assertEqual(compact_sha(after), self.receipt['preflight']['export_candidate_sha256'])
        # Git's immutable tree plus a locally computed blob hash verifies all
        # other records byte-for-byte, including metadata absent from export.
        tree = subprocess.check_output(['git', 'ls-tree', '-r', BASE, '--', 'translation/ot/exodus'], cwd=ROOT).decode()
        old_blobs = {line.split('\t', 1)[1]: line.split()[2] for line in tree.splitlines()
                     if line.endswith('.yaml') and line.split('\t', 1)[1] not in TARGETS.values()}
        current_paths = {str(p.relative_to(ROOT)) for p in (ROOT / 'translation/ot/exodus').rglob('*.yaml')
                         if str(p.relative_to(ROOT)) not in TARGETS.values()}
        self.assertEqual(len(old_blobs), 1210)
        self.assertEqual(current_paths, old_blobs.keys())
        manifest = {}
        for path, blob in old_blobs.items():
            raw = (ROOT / path).read_bytes()
            self.assertEqual(hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest(), blob, path)
            manifest[path] = sha(raw)
        self.assertEqual(self.receipt['preflight']['other_verse_files'], len(old_blobs))
        self.assertEqual(compact_sha(manifest), self.receipt['preflight']['other_verse_manifest_sha256'])

    def test_hash_bound_receipt_and_narrow_applied_approval(self):
        receipt = self.receipt
        self.assertEqual(receipt['baseline_revision'], BASE)
        self.assertEqual(set(receipt['units']), {str(v) for v in VERSES})
        for verse in VERSES:
            unit = receipt['units'][str(verse)]
            self.assertEqual(unit['target'], TARGETS[verse])
            self.assertEqual(unit['candidate'], CANDIDATES[verse])
            self.assertEqual(unit['baseline_sha256'], sha(self.before_raw[verse]))
            self.assertEqual(unit['candidate_sha256'], sha((ROOT / CANDIDATES[verse]).read_bytes()))
            self.assertEqual(unit['candidate_yaml_sha256'], sha((ROOT / TARGETS[verse]).read_bytes()))
        for field in ('contract', 'assessment'):
            self.assertEqual(receipt[field + '_sha256'], sha((ROOT / receipt[field]).read_bytes()))
        self.assertEqual(receipt['schema_sha256'], sha((ROOT / 'schema/verse.schema.json').read_bytes()))
        self.assertEqual(receipt['review']['status'], 'pass')
        for field in ('candidate_sha256s', 'candidate_yaml_sha256s'):
            unit_field = field[:-1]
            self.assertEqual(receipt['review'][field],
                             {str(v): receipt['units'][str(v)][unit_field] for v in VERSES})
        self.assertEqual(receipt['review']['assessment_sha256'], receipt['assessment_sha256'])
        self.assertEqual(receipt['application']['status'], 'applied-verified')
        self.assertEqual(receipt['application']['changed_units'], CHANGED_UNITS)
        self.assertEqual(receipt['application']['yaml_sha256s'],
                         {str(v): receipt['units'][str(v)]['candidate_yaml_sha256'] for v in VERSES})
        self.assertEqual(receipt['application']['export_after_sha256'],
                         receipt['preflight']['export_candidate_sha256'])
        self.assertTrue(receipt['application']['preflight_digest_matches'])
        self.assertFalse(receipt['application']['deployed_reader_verified'])
        for key in ('source_changed', 'original_priority_settled', 'original_meaning_settled',
                    'novel_reading_demonstrated', 'canon_changed', 'publication_approved'):
            self.assertFalse(receipt['decision'][key])


if __name__ == '__main__':
    unittest.main()
