"""Integrity of acquired metadata, not Armenian philology or ancient priority."""
import hashlib
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / 'sources/textual_restoration/discovery/deut32_8_armenian_controls.2026-10-06.v1.json'


class ArmenianControlTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(RECORD.read_text())

    def test_control_labels_excerpt_and_acquisition_pins(self):
        r = self.record
        self.assertEqual(len(r['acquisitions']), 4)
        self.assertTrue(all(a['http_status'] == 200 and a['bytes'] > 0 and len(a['sha256']) == 64 for a in r['acquisitions']))
        self.assertEqual(r['critical_excerpt_sha256'], hashlib.sha256(r['critical_excerpt'].encode()).hexdigest())
        self.assertEqual([c['working_gloss'] for c in r['controls']], ['sons of God', 'sons of God'])
        self.assertIn('1895 Bagratuni', r['controls'][0]['label'])
        self.assertIn('Zohrap 1805', r['controls'][1]['label'])
        self.assertIn('software slot', r['controls'][1]['edition_identity_basis'])
        self.assertIn('excluding outer td', r['extraction_rules']['main_verse_row'])
        self.assertIn('U+0020', r['extraction_rules']['main_word_sequence'])

    def test_frozen_inspected_context_pins(self):
        r = self.record
        self.assertEqual(len(r['context_files']), 8)
        for path,digest in r['context_files'].items():
            raw = subprocess.check_output(['git', 'show', f"{r['baseline_revision']}:{path}"], cwd=ROOT)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)

    def test_observed_version_not_promoted_to_unique_hebrew(self):
        r = self.record
        self.assertTrue(all(not value for value in r['decision'].values()))
        self.assertFalse(r['dayfani_partial']['adaptation_gate_closed'])
        self.assertEqual(r['dayfani_partial']['ordinary_http_status'], 403)
        self.assertEqual(r['critic']['status'], 'completed_with_metadata_clarification')
        self.assertIn('KJV', r['alignment'])
        self.assertIn('not vendored replay artifacts', r['retention'])


if __name__ == '__main__':
    unittest.main()
