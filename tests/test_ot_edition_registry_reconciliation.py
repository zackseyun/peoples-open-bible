"""Bounded source-route integrity, not completed manuscript collation."""
import hashlib
import json
from pathlib import Path
import subprocess
import unittest

from jsonschema import Draft202012Validator, FormatChecker
from tools.textual_restoration.validate_ot_witness_registry import validate

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / 'sources/textual_restoration/discovery/ot_edition_registry_reconciliation.2026-10-10.v1.json'


class EditionRegistryReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads(RECEIPT.read_text())
        cls.registry = json.loads((ROOT / cls.receipt['registry']).read_text())
        cls.entries = {w['id']: w for w in cls.registry['witnesses']}

    def test_current_schema_and_registry_evidence_boundaries(self):
        schema = json.loads((ROOT / 'schemas/ot-witness-registry.schema.json').read_text())
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(self.registry)
        self.assertEqual(validate(self.registry), [])
        self.assertIs(self.registry['policy']['imagegen_is_evidence'], False)
        self.assertIs(self.registry['policy']['automatic_translation_changes'], False)

    def test_eight_edition_routes_are_not_physical_objects_or_pixel_restoration(self):
        r = self.receipt
        self.assertEqual(len(r['added_ids']), 8)
        self.assertEqual(len(set(r['added_ids'])), 8)
        self.assertEqual(r['before_records'] + len(r['added_ids']), r['after_records'])
        self.assertEqual(r['unchanged_existing_records'] + len(r['changed_existing_ids']), r['before_records'])
        self.assertEqual(r['changed_existing_ids'], ['ohb-sample-editions-2008'])
        self.assertGreaterEqual(len(self.entries), r['after_records'])
        for wid in r['added_ids']:
            w = self.entries[wid]
            self.assertEqual(w['witness_class'], 'critical-edition')
            self.assertEqual(w['date_basis']['kind'], 'edition-publication')
            self.assertEqual(w['restoration_suitability'], 'none')
        for flag in ('counts_are_physical_objects', 'all_citations_reconciled',
                     'all_known_sources_discovered', 'new_apparatus_collation',
                     'canonical_source_or_english_changed', 'generated_images_used',
                     'licenses_or_rights_expanded'):
            self.assertIs(r[flag], False)

    def test_historical_baseline_and_evidence_pins_are_not_current_corpus_claims(self):
        r = self.receipt
        read = lambda path: subprocess.check_output(
            ['git', 'show', r['evidence_baseline_revision'] + ':' + path], cwd=ROOT)
        self.assertEqual(r['baseline_revision'], r['evidence_baseline_revision'])
        raw = read(r['registry'])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), r['baseline_registry_sha256'])
        old = json.loads(raw)
        self.assertEqual(len(old['witnesses']), r['before_records'])
        for path, pin in r['evidence_pins'].items():
            self.assertEqual(hashlib.sha256(read(path)).hexdigest(), pin)
        self.assertEqual({x['id'] for x in r['route_evidence']}, set(r['added_ids']))
        self.assertTrue(all(x['source_body_hash'] is None for x in r['route_evidence']))
        self.assertEqual(r['review']['status'], 'pass')
        self.assertIs(r['review']['repeat_until_agreement'], False)

    def test_ohb_browser_consultation_does_not_invent_local_pdf_or_other_samples(self):
        r = self.receipt
        old = json.loads((ROOT / r['ohb_correction']['receipt']).read_text())
        self.assertFalse(old['source']['local_pdf_saved'])
        self.assertIsNone(old['source']['sha256'])
        self.assertEqual(r['ohb_correction']['printed_pages'], [354, 355, 357])
        self.assertEqual(r['ohb_correction']['pdf_pages'], [4, 5, 7])
        self.assertFalse(r['ohb_correction']['other_samples_consulted'])
        self.assertFalse(r['ohb_correction']['local_pdf_saved'])
        self.assertIsNone(r['ohb_correction']['source_pdf_sha256'])

    def test_nets_english_remains_companion_not_a_greek_witness(self):
        c = self.receipt['companion']
        source = json.loads((ROOT / c['source_contract']).read_text())
        self.assertEqual(source['controls']['nets']['pdf_sha256'], c['pdf_sha256'])
        self.assertFalse(c['registry_row_added'])
        self.assertFalse(c['full_greek_apparatus_consulted'])
        self.assertFalse(any('nets' in wid for wid in self.receipt['added_ids']))
        self.assertEqual(self.entries['rahlfs-hanhart-2006-publisher']['languages'], ['Greek'])
        self.assertEqual(self.entries['weber-gryson-vulgate-2007']['languages'], ['Latin'])


if __name__ == '__main__':
    unittest.main()
