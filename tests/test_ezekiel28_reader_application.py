"""Hash-bound reader disclosure; not proof of original source priority."""
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile
import unittest
from unittest.mock import patch

import yaml
from jsonschema import Draft202012Validator
from tools import audit_footnotes
from tools import export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]
BASE = 'c74fa8fb0d5a1fdc18face8b35cc195a91f1a936'
RECEIPT = ROOT / 'sources/textual_restoration/applications/ezekiel28_14_16_reader.2026-10-10.v1.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact_sha(value):
    return sha(json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':')).encode())


def index(book):
    return {(c['chapter'], v['verse']): v for c in book['chapters'] for v in c['verses']}


class Ezekiel28ReaderApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(RECEIPT.read_text())
        cls.units = cls.receipt['units']
        cls.raw = {v: subprocess.check_output(['git', 'show', f"{BASE}:{u['target']}"],
                                              cwd=ROOT) for v, u in cls.units.items()}
        cls.before = {v: yaml.safe_load(raw) for v, raw in cls.raw.items()}
        cls.candidates = {v: json.loads((ROOT / u['candidate']).read_text())
                          for v, u in cls.units.items()}
        cls.current = {v: yaml.safe_load((ROOT / u['target']).read_text())
                       for v, u in cls.units.items()}

    def test_complete_records_schema_source_generation_and_main_words(self):
        validator = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        clean = lambda text: re.sub(r'\[[a-z]\]', '', text)
        self.assertEqual(set(self.units), {'14', '16'})
        for v, record in self.current.items():
            validator.validate(record)
            self.assertEqual(record, self.candidates[v])
            for field in ('source', 'ai_draft'):
                self.assertEqual(record[field], self.before[v][field])
            self.assertEqual(clean(record['translation']['text']),
                             clean(self.before[v]['translation']['text']))

    def test_eight_notes_have_true_anchors_and_qualified_alternatives(self):
        anchors = {'14': ['You[a]', 'anointed[b]', 'guardian cherub[c][d]'],
                   '16': ['trade[a]', 'cast you as profane[b]', 'destroyed you[c]', 'guardian cherub[d]']}
        self.assertEqual(sum(len(r['translation']['footnotes']) for r in self.current.values()), 8)
        for v, record in self.current.items():
            tr = record['translation']
            self.assertEqual(re.findall(r'\[([a-z])\]', tr['text']), list('abcd'))
            self.assertEqual([n['marker'] for n in tr['footnotes']], list('abcd'))
            self.assertEqual(audit_footnotes.audit_one(ROOT / self.units[v]['target'])['status'], 'ok')
            for anchor in anchors[v]:
                self.assertIn(anchor, tr['text'])
        a = self.current['14']['translation']['footnotes']
        b = self.current['16']['translation']['footnotes']
        for phrase in ('male addressees', 'Numbers11:15', 'Deuteronomy5:27', 'alone'):
            self.assertIn(phrase, a[0]['text'])
        for phrase in ('outspread', 'extended', 'disputed', 'provisionally'):
            self.assertIn(phrase, a[1]['text'])
        for phrase in ('selected Greek', 'with the cherub', 'verse16', 'priority is uncertain'):
            self.assertIn(phrase, a[3]['text'])
        for phrase in ('wounded', 'cherub brought', 'agent', 'unchanged pointed Hebrew', 'priority is uncertain'):
            self.assertIn(phrase, b[2]['text'])

    def test_seven_archives_exact_old_revisions_preserved_and_approval_not_transferred(self):
        fields = ['status', 'translation', 'lexical_decisions', 'theological_decisions',
                  'revision_pass', 'cross_check', 'ai_draft']
        for v, record in self.current.items():
            old = self.before[v]
            history = record['review_history']
            self.assertEqual([h['field'] for h in history], fields)
            self.assertEqual({h['field']: h['value'] for h in history}, {f: old[f] for f in fields})
            self.assertTrue(all(h['archived_from_baseline_sha256'] == sha(self.raw[v]) and
                                not h['certifies_this_candidate'] for h in history))
            self.assertEqual(record['revisions'][:-1], old.get('revisions', []))
            self.assertEqual(len(old.get('revisions', [])), 0 if v == '14' else 2)
            self.assertEqual(record['revisions'][-1]['from'], old['translation']['text'])
            self.assertEqual(record['revisions'][-1]['to'], record['translation']['text'])
            self.assertEqual(record['status'], 'draft')
            self.assertEqual(record['cross_check'], {'status': 'needs_review'})
            self.assertNotIn('revision_pass', record)

    def test_rationale_matches_source_form_and_application_scope(self):
        lex = {v: {d['source_word']: d for d in r['lexical_decisions']}
               for v, r in self.current.items()}
        self.assertIn('does not by itself establish corruption', lex['14']['אַ֨תְּ']['rationale'])
        self.assertIn('provisional', lex['14']['מִמְשַׁ֖ח']['rationale'])
        self.assertEqual(lex['16']['וָאֶחַלֶּלְךָ']['chosen'], 'so I cast you as profane')
        self.assertIn('first person', lex['16']['וָאַבֶּדְךָ']['rationale'])
        self.assertNotIn('anointed covering', lex['16']['הַסֹּכֵךְ']['alternatives'])
        changed = {'14': {'אַ֨תְּ', 'מִמְשַׁ֖ח'},
                   '16': {'וָאֶחַלֶּלְךָ', 'וָאַבֶּדְךָ', 'הַסֹּכֵךְ'}}
        for v, record in self.current.items():
            for old in self.before[v]['lexical_decisions']:
                if old['source_word'] not in changed[v]:
                    self.assertEqual(lex[v][old['source_word']], old)
            self.assertIn('unresolved', record['textual_comparison']['historical_priority'])
            for flag in ('fresh_image_reading', 'novel_reading_demonstrated', 'canon_changed', 'publication_approved'):
                self.assertFalse(record['textual_comparison'][flag])
            self.assertTrue(record['source_audit']['no_fresh_halot_consultation'])

    def test_current_full_reader_export_isolates_two_units_and_keeps_notes(self):
        after = exporter.export_book('EZK')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v:
            self.before[str(v)] if c == 'EZK' and ch == 28 and str(v) in self.before else loader(c, ch, v)):
            before = exporter.export_book('EZK')
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 48)
        self.assertEqual(len(a), 1273)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([list(k) for k in a if a[k] != b[k]], [[28, 14], [28, 16]])
        for v in self.current:
            self.assertEqual(a[(28, int(v))]['footnotes'], self.current[v]['translation']['footnotes'])

    def test_historical_export_digests_and_non_target_manifest(self):
        # Historical receipt remains valid after legitimate future applications.
        archive = subprocess.check_output(['git', 'archive', BASE, 'translation/ot/ezekiel'], cwd=ROOT)
        historical, manifest = {}, {}
        targets = {u['target'] for u in self.units.values()}
        with tarfile.open(fileobj=io.BytesIO(archive)) as snapshot:
            for member in snapshot.getmembers():
                if member.isfile() and member.name.endswith('.yaml'):
                    raw = snapshot.extractfile(member).read()
                    p = Path(member.name)
                    historical[(int(p.parent.name), int(p.stem))] = yaml.safe_load(raw)
                    if member.name not in targets:
                        manifest[member.name] = sha(raw)
        self.assertEqual(len(historical), 1273)
        self.assertEqual(len(manifest), 1271)
        self.assertEqual(compact_sha(manifest), self.receipt['preflight']['other_verse_manifest_sha256'])
        loader = exporter.load_translation_record
        def snapshot_record(c, ch, v, candidate=False):
            if c != 'EZK':
                return loader(c, ch, v)
            if candidate and ch == 28 and str(v) in self.candidates:
                return self.candidates[str(v)]
            return historical.get((ch, v))
        with patch.object(exporter, 'load_translation_record', side_effect=snapshot_record):
            before = exporter.export_book('EZK')
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v:
            snapshot_record(c, ch, v, candidate=True)):
            after = exporter.export_book('EZK')
        self.assertEqual(compact_sha(before), self.receipt['preflight']['export_before_sha256'])
        self.assertEqual(compact_sha(after), self.receipt['preflight']['export_candidate_sha256'])
        self.assertEqual(compact_sha(after), self.receipt['application']['export_after_sha256'])

    def test_receipt_pins_exact_application_and_narrow_approval(self):
        r = self.receipt
        self.assertEqual(r['baseline_revision'], BASE)
        for v, u in self.units.items():
            self.assertEqual(sha(self.raw[v]), u['baseline_sha256'])
            self.assertEqual(sha((ROOT / u['candidate']).read_bytes()), u['candidate_sha256'])
            self.assertEqual(sha((ROOT / u['target']).read_bytes()), u['candidate_yaml_sha256'])
            self.assertEqual(r['review']['candidate_sha256s'][v], u['candidate_sha256'])
            self.assertEqual(r['review']['candidate_yaml_sha256s'][v], u['candidate_yaml_sha256'])
        for field in ('reader_contract', 'source_contract', 'source_assessment'):
            self.assertEqual(sha((ROOT / r[field]).read_bytes()), r[field + '_sha256'])
        self.assertEqual(sha((ROOT / 'schema/verse.schema.json').read_bytes()), r['schema_sha256'])
        self.assertEqual(r['review']['status'], 'pass')
        self.assertEqual(r['application']['status'], 'applied-verified')
        self.assertEqual(r['application']['changed_units'], [[28, 14], [28, 16]])
        self.assertFalse(r['application']['deployed_reader_verified'])
        for flag in ('source_changed', 'marker_free_main_english_changed', 'original_priority_settled',
                     'original_meaning_settled', 'novel_reading_demonstrated', 'canon_changed', 'publication_approved'):
            self.assertFalse(r['decision'][flag])


if __name__ == '__main__':
    unittest.main()
