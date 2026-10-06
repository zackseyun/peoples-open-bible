"""Disclosure bindings and export behavior, not earliest-Greek certification."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest
from unittest.mock import patch

import yaml
from jsonschema import Draft202012Validator
from tools import audit_footnotes, export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'sources/textual_restoration/'
SHA = lambda raw: hashlib.sha256(raw).hexdigest()


class Psalm151DisclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((ROOT / (PREFIX + 'applications/psalm151_4.2026-10-06.v1.json')).read_text())
        cls.evidence = json.loads((ROOT / cls.receipt['assessment']).read_text())
        cls.target = ROOT / cls.receipt['target']
        cls.raw = subprocess.check_output(['git', 'show',
            f"{cls.receipt['baseline_revision']}:{cls.receipt['target']}"], cwd=ROOT)
        cls.before = yaml.safe_load(cls.raw)
        cls.after = yaml.safe_load(cls.target.read_text())

    def test_exact_candidate_preserves_source_words_and_history(self):
        r = self.receipt
        candidate = ROOT / r['candidate']
        self.assertEqual(SHA(self.raw), r['baseline_sha256'])
        self.assertEqual(self.after, json.loads(candidate.read_text()))
        self.assertEqual(SHA(candidate.read_bytes()), r['candidate_sha256'])
        self.assertEqual(SHA(self.target.read_bytes()), r['application']['yaml_sha256'])
        self.assertEqual(SHA((ROOT / r['assessment']).read_bytes()), r['assessment_sha256'])
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(self.after)
        for field in ('source', 'ai_draft', 'revisions'):
            self.assertEqual(self.before[field], self.after[field])
        plain = lambda text: re.sub(r'\[[a-z]+\]', '', text)
        self.assertEqual(plain(self.before['translation']['text']), plain(self.after['translation']['text']))
        self.assertNotIn('Samuel', self.after['translation']['text'])

    def test_reader_notes_and_archival_approvals(self):
        self.assertEqual(audit_footnotes.audit_one(self.target)['status'], 'ok')
        notes = self.after['translation']['footnotes']
        self.assertEqual([n['marker'] for n in notes], ['a', 'c'])
        self.assertEqual(notes, self.receipt['reader_notes'])
        archived = {row['field']: row['value'] for row in self.after['review_history']}
        for field in ('status', 'revision_pass', 'cross_check'):
            self.assertEqual(archived[field], self.before[field])
        self.assertEqual(archived['translation.footnotes'], self.before['translation']['footnotes'])
        self.assertTrue(all(not row['certifies_this_candidate'] and
            row['archived_from_baseline_sha256'] == SHA(self.raw) for row in self.after['review_history']))
        self.assertEqual(self.after['status'], 'draft')
        self.assertEqual(self.after['cross_check'], {'status': 'needs_review'})
        self.assertNotIn('revision_pass', self.after)
        self.assertFalse(self.after['restoration_review']['publication_approval'])

    def test_full_book_export_changes_only_target_disclosure(self):
        after = exporter.export_apocrypha_book('PS151')
        reader = Path.read_text
        with patch.object(Path, 'read_text', autospec=True, side_effect=lambda p,*a,**kw:
            self.raw.decode() if p.resolve() == self.target else reader(p,*a,**kw)):
            before = exporter.export_apocrypha_book('PS151')
        index = lambda b: {(c['chapter'],v['verse']):v for c in b['chapters'] for v in c['verses']}
        a,b = index(before),index(after)
        self.assertEqual(list(a), [(1,v) for v in range(1,8)])
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([k for k in a if a[k] != b[k]], [(1,4)])
        self.assertEqual(b[(1,4)]['footnotes'], self.after['translation']['footnotes'])
        # Compare scoped substitution, not a historical digest of later edits to other verses.
        plain = lambda text: re.sub(r'\[[a-z]+\]', '', text)
        self.assertEqual(plain(a[(1,4)]['text']), plain(b[(1,4)]['text']))

    def test_published_encoding_and_priority_limits_remain_distinct(self):
        r = self.evidence
        self.assertEqual(r['sinaiticus']['critical_word'], 'ελεει')
        self.assertEqual(r['sinaiticus']['decisive_line_id'], 'S-64-1r-2-21')
        self.assertEqual(r['sinaiticus']['verse4_app_count'], 0)
        self.assertFalse(r['sinaiticus']['word_app_or_supply'])
        self.assertEqual(r['mediated_rahlfs']['reported_mercy_sigla'], "S' R'' Ga L\\pau A")
        self.assertFalse(r['edition_status']['actual_modern_passage_apparatus_read'])
        for key in ('source_changed', 'main_english_words_changed', 'new_ancient_reading', 'canon_changed'):
            self.assertFalse(r['decision'][key])
        self.assertEqual(self.receipt['decision']['historical_priority'], 'unresolved')
        self.assertFalse(self.receipt['review']['whole_verse_approval'])
        self.assertFalse(self.receipt['review']['blind'])


if __name__ == '__main__':
    unittest.main()
