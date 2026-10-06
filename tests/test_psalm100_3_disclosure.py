"""Scoped evidence/application integrity, not philology or earliest-text proof."""
import hashlib
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import yaml
from jsonschema import Draft202012Validator
from tools import audit_footnotes, export_mobile_bible as exporter

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'sources/textual_restoration/'
RECEIPT = ROOT / (PREFIX + 'applications/psalm100_3.2026-10-06.v1.json')
SHA = lambda raw: hashlib.sha256(raw).hexdigest()


class Psalm100DisclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(RECEIPT.read_text())
        cls.evidence = json.loads((ROOT / cls.receipt['assessment']).read_text())
        cls.target = ROOT / cls.receipt['target']
        cls.raw = subprocess.check_output(['git', 'show',
            f"{cls.receipt['baseline_revision']}:{cls.receipt['target']}"], cwd=ROOT)
        cls.before = yaml.safe_load(cls.raw)
        cls.after = yaml.safe_load(cls.target.read_text())

    def test_hebrew_written_and_read_annotations_are_distinct(self):
        r = self.evidence
        raw = subprocess.check_output(['git', 'show',
            f"{r['baseline_revision']}:{r['hebrew']['path']}"], cwd=ROOT)
        self.assertEqual(SHA(raw), r['hebrew']['sha256'])
        ns = {'o': 'http://www.bibletechnologies.net/2003/OSIS/namespace'}
        verse = ET.fromstring(raw).find('.//o:verse[@osisID="Ps.100.3"]', ns)
        ketiv = verse.find('o:w[@type="x-ketiv"]', ns)
        qere = verse.find('o:note/o:rdg[@type="x-qere"]/o:w', ns)
        for key, word in [('ketiv', ketiv), ('qere', qere)]:
            self.assertEqual(word.text, r['hebrew'][key]['text'])
            self.assertEqual(word.get('id'), r['hebrew'][key]['word_id'])
        for path, digest in r['context_files'].items():
            frozen = subprocess.check_output(['git', 'show',
                f"{r['baseline_revision']}:{path}"], cwd=ROOT)
            self.assertEqual(SHA(frozen), digest)

    def test_exact_candidate_preserves_source_main_english_and_history(self):
        r = self.receipt
        cp = ROOT / r['candidate']
        self.assertEqual(self.after, json.loads(cp.read_text()))
        self.assertEqual(SHA(self.raw), r['baseline_sha256'])
        self.assertEqual(SHA(cp.read_bytes()), r['candidate_sha256'])
        self.assertEqual(SHA(self.target.read_bytes()), r['application']['yaml_sha256'])
        self.assertEqual(SHA((ROOT / r['assessment']).read_bytes()), r['assessment_sha256'])
        Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text())).validate(self.after)
        for field in ('source', 'ai_draft', 'revisions'):
            self.assertEqual(self.before[field], self.after[field])
        self.assertEqual(self.before['translation']['text'], self.after['translation']['text'])
        for old, new in zip(self.before['theological_decisions'], self.after['theological_decisions']):
            self.assertEqual({k:v for k,v in old.items() if k != 'rationale'},
                {k:v for k,v in new.items() if k != 'rationale'})
        for old, new in zip(self.before['lexical_decisions'], self.after['lexical_decisions']):
            if old['source_word'] == 'וְלֹא אֲנַחְנוּ':
                self.assertEqual({k:v for k,v in old.items() if k not in ('rationale','lexicon')},
                    {k:v for k,v in new.items() if k not in ('rationale','lexicon')})
            else:
                self.assertEqual(old, new)

    def test_note_and_review_boundaries(self):
        self.assertEqual(self.after['translation']['footnotes'][0]['text'], self.receipt['note_a'])
        self.assertEqual(audit_footnotes.audit_one(self.target)['status'], 'ok')
        fields = ('status','revision_pass','cross_check','source_audit')
        self.assertEqual({r['field']:r['value'] for r in self.after['review_history']},
            {f:self.before[f] for f in fields})
        self.assertTrue(all(not r['certifies_this_candidate'] and
            r['archived_from_baseline_sha256'] == SHA(self.raw) for r in self.after['review_history']))
        self.assertEqual(self.after['status'], 'draft')
        self.assertEqual(self.after['cross_check'], {'status':'needs_review'})
        self.assertNotIn('revision_pass', self.after)
        self.assertFalse(self.receipt['decision']['publication_approved'])
        self.assertEqual(self.receipt['decision']['historical_priority'], 'unresolved')

    def test_live_full_psalms_export_only_target_note_differs(self):
        after = exporter.export_book('PSA')
        reader = Path.read_text
        # Psalms walks normalized files directly, not load_translation_record.
        with patch.object(Path, 'read_text', autospec=True, side_effect=lambda p,*a,**kw:
            self.raw.decode() if p.resolve() == self.target else reader(p,*a,**kw)):
            before = exporter.export_book('PSA')
        index = lambda b: {(c['chapter'],v['verse']):v for c in b['chapters'] for v in c['verses']}
        a,b = index(before),index(after)
        self.assertEqual(len(after['chapters']), 150)
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual([k for k in a if a[k] != b[k]], [(100,3)])
        self.assertEqual(b[(100,3)]['text'], self.before['translation']['text'])
        self.assertEqual(b[(100,3)]['footnotes'], self.after['translation']['footnotes'])
        self.assertEqual({k:v for k,v in a[(100,3)].items() if k != 'footnotes'},
            {k:v for k,v in b[(100,3)].items() if k != 'footnotes'})

    def test_version_and_access_limits_do_not_become_attestation(self):
        r = self.evidence
        self.assertEqual(r['greek']['print']['printed_pages'], [345,346])
        self.assertEqual(r['greek']['print']['pdf_pages'], [361,362])
        self.assertEqual(r['latin'][0]['critical_excerpt'], 'ipse fecit nos et ipsius sumus')
        self.assertEqual(r['latin'][1]['critical_excerpt'], 'ipse fecit nos et non ipsi nos')
        self.assertTrue(all(not a['reading_support'] for a in r['failed_acquisitions']))
        self.assertFalse(r['decision']['source_changed'])
        self.assertFalse(r['decision']['main_english_changed'])
        route = json.loads((ROOT / (PREFIX + 'discovery/deut32_8_new_primary_routes.2026-10-06.v1.json')).read_text())
        self.assertEqual(route['catalogue']['diktyon'], '15673')
        self.assertFalse(route['catalogue']['correction_description_is_locus_specific'])
        self.assertFalse(route['catalogue']['canViewImages'])
        self.assertFalse(route['edition']['modern_adjacent_apparatus_read'])
        self.assertTrue(all(not value for key,value in route['decision'].items() if key != 'outcome'))


if __name__ == '__main__':
    unittest.main()
