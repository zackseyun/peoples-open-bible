"""Two-verse application integrity, not proof of historical priority."""
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
RECEIPT = ROOT / 'sources/textual_restoration/applications/exodus18_24_25.2026-10-05.v1.json'
SHA = lambda raw: hashlib.sha256(raw).hexdigest()


class ExodusAppointmentDisclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(RECEIPT.read_text())
        cls.records = {}
        for target in cls.receipt['targets']:
            raw = subprocess.check_output(['git', 'show',
                f"{cls.receipt['baseline_revision']}:{target['target']}"], cwd=ROOT)
            cls.records[int(Path(target['target']).stem)] = (
                target, raw, yaml.safe_load(raw),
                yaml.safe_load((ROOT / target['target']).read_text()))

    def test_complete_candidates_source_and_english(self):
        schema = Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
        clean = lambda t: re.sub(r'\[[a-z]+\]', '', t)
        for target, raw, before, after in self.records.values():
            schema.validate(after)
            candidate = ROOT / target['candidate']
            self.assertEqual(after, json.loads(candidate.read_text()))
            self.assertEqual(SHA(raw), target['baseline_sha256'])
            self.assertEqual(SHA(candidate.read_bytes()), target['candidate_sha256'])
            self.assertEqual(SHA((ROOT / target['target']).read_bytes()), target['yaml_sha256'])
            self.assertEqual(after['source'], before['source'])
            self.assertEqual(clean(after['translation']['text']), clean(before['translation']['text']))

    def test_notes_have_referent_anchors_and_qualified_attestation(self):
        for target, _, before, after in self.records.values():
            old_notes = before['translation']['footnotes']
            self.assertEqual(after['translation']['footnotes'][:len(old_notes)], old_notes)
            self.assertEqual(audit_footnotes.audit_one(ROOT / target['target'])['status'], 'ok')
            for note in after['translation']['footnotes']:
                self.assertEqual(after['translation']['text'].count(f"[{note['marker']}]"), 1)
        a = self.records[24][3]['translation']
        b = self.records[25][3]['translation']
        self.assertIn('father-in-law[a]', a['text'])
        self.assertIn('said[b].', a['text'])
        self.assertIn('capable men[a]', b['text'])
        self.assertIn('heads over the people[b]', b['text'])
        for phrase in ('transcription compared here', '1:9–18', 'consultation',
                       'impartial judgment', 'Portions', '4Q22', 'not every word', 'provisionally'):
            self.assertIn(phrase, a['footnotes'][1]['text'])

    def test_provenance_preserved_and_old_reviews_not_transferred(self):
        for target, raw, before, after in self.records.values():
            self.assertEqual({h['field']: h['value'] for h in after['review_history']},
                {f: before[f] for f in ('status', 'revision_pass', 'cross_check')})
            self.assertTrue(all(not h['certifies_this_candidate'] and
                h['archived_from_baseline_sha256'] == SHA(raw) for h in after['review_history']))
            for field in ('ai_draft', 'lexical_decisions', 'theological_decisions', 'revisions'):
                self.assertEqual(after.get(field), before.get(field))
            self.assertEqual(after['status'], 'draft')
            self.assertEqual(after['cross_check'], {'status': 'needs_review'})
            self.assertNotIn('revision_pass', after)
            self.assertFalse(after['textual_comparison']['publication_approved'])

    def test_complete_exodus_export_only_two_units_change(self):
        after = exporter.export_book('EXO')
        loader = exporter.load_translation_record
        with patch.object(exporter, 'load_translation_record', side_effect=lambda c, ch, v:
            self.records[v][2] if c == 'EXO' and ch == 18 and v in self.records else loader(c, ch, v)):
            before = exporter.export_book('EXO')
        index = lambda b: {(c['chapter'], v['verse']): v for c in b['chapters'] for v in c['verses']}
        a, b = index(after), index(before)
        self.assertEqual(len(after['chapters']), 40)
        self.assertEqual(len(a), 1213)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([k for k in a if a[k] != b[k]], [(18, 24), (18, 25)])
        for v in (24, 25):
            self.assertEqual(a[(18, v)]['footnotes'], self.records[v][3]['translation']['footnotes'])
        for key, book in (('export_before_sha256', before), ('export_after_sha256', after)):
            self.assertEqual(SHA(json.dumps(book, ensure_ascii=False, sort_keys=True).encode()),
                self.receipt['application'][key])

    def test_lossless_alignment_metadata_and_limits(self):
        nodes = self.receipt['alignment']['nodes']
        self.assertEqual([n['sp_reference'] for n in nodes], ['Exod.18.24', 'Exod.18.25'])
        for node in nodes:
            cursor = 0
            for s in node['segments']:
                self.assertEqual(s['span'][0], cursor)
                cursor = s['span'][1]
                self.assertEqual(s['raw_characters'], s['span'][1] - s['span'][0])
            self.assertEqual(cursor, node['raw_characters'])
            self.assertEqual(sum(s['consonants'] for s in node['segments']), node['consonants'])
        parts = [s for n in nodes for s in n['segments']]
        summary = self.receipt['alignment']['summary']
        self.assertEqual(len(parts), 12)
        for classification, prefix in [('equal-to-at-least-one-control', 'equal_to_at_least_one_control'),
                                      ('adapted-parallel', 'adapted_parallel')]:
            selected = [s for s in parts if s['classification'] == classification]
            for measure in ('raw_characters', 'consonants'):
                self.assertEqual(sum(s[measure] for s in selected), summary[f'{prefix}_{measure}'])
        self.assertEqual(summary['raw_characters'], 658)
        self.assertEqual(summary['consonants'], 531)
        self.assertEqual(summary['unassigned_raw_characters'], 0)
        self.assertFalse(summary['difference_is_pure_verbatim_insertion'])
        self.assertFalse(summary['unique_origin_inference'])
        for flag in ('source_changed', 'marker_free_english_changed', 'novel_reading_demonstrated',
                     'canon_changed', 'fresh_locus_image_reading', 'imagegen_used', 'publication_approved'):
            self.assertFalse(self.receipt['decision'][flag])


if __name__ == '__main__':
    unittest.main()
