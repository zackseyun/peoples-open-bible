"""Nahum published-source packet integrity, not proof of earliest wording."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import unittest

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from tools.textual_restoration.validate_ot_witness_registry import validate

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / 'sources/textual_restoration/comparisons/nahum3_6_11_pesher.2026-10-10.v1.json'


class NahumPesherFollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads(RECEIPT.read_text())
        raw = subprocess.check_output(['git', 'show', cls.r['baseline_commit'] + ':' +
                                       cls.r['registry']['path']], cwd=ROOT)
        cls.before = json.loads(raw)
        cls.before_raw = raw

    def test_historical_registry_and_exact_scoped_entry_not_current_corpus_certification(self):
        r = self.r
        self.assertEqual(hashlib.sha256(self.before_raw).hexdigest(), r['registry']['before_sha256'])
        self.assertEqual(len(self.before['witnesses']), 41)
        proposed = copy.deepcopy(self.before)
        target = r['registry']['frozen_updated_entry']
        i = next(i for i, w in enumerate(proposed['witnesses']) if w['id'] == target['id'])
        proposed['witnesses'][i] = target
        self.assertEqual([w['id'] for w in proposed['witnesses']],
                         [w['id'] for w in self.before['witnesses']])
        changed = [a['id'] for a, b in zip(proposed['witnesses'], self.before['witnesses']) if a != b]
        self.assertEqual(changed, ['8hev-greek-minor-prophets'])
        self.assertEqual(r['registry']['other_records_unchanged'], 40)
        schema = json.loads((ROOT / 'schemas/ot-witness-registry.schema.json').read_text())
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(proposed)
        self.assertEqual(validate(proposed), [])
        current = json.loads((ROOT / r['registry']['path']).read_text())
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(current)
        self.assertEqual(validate(current), [])

    def test_historical_comparison_inputs_have_exact_source_and_english_pins(self):
        for pin in self.r['canonical_records']:
            raw = subprocess.check_output(['git', 'show', self.r['baseline_commit'] + ':' +
                                           pin['path']], cwd=ROOT)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), pin['sha256'])
            old = yaml.safe_load(raw)
            self.assertEqual(old['source'], pin['source'])
            self.assertEqual(old['translation']['text'], pin['main_english'])
        self.assertEqual({p['id'] for p in self.r['canonical_records']}, {'NAM.3.6', 'NAM.3.11'})

    def test_quotation_variants_preserve_missing_and_uncertain_controls(self):
        units = {u['id']: u for u in self.r['units']}
        six, last = units['NAM.3.6'], units['NAM.3.11']
        self.assertEqual(six['published_reading'], 'כאורה')
        self.assertEqual(last['published_reading'], 'מעוז בעיר מאויב')
        self.assertIs(six['mur_decisive_ending_supplied'], True)
        self.assertIs(last['mur_entire_refuge_clause_supplied'], True)
        self.assertIs(last['commentary_city_final_resh_uncertain'], True)
        self.assertIs(last['definite_city_settled'], False)
        self.assertIn('Qal-passive', six['lexicon_analysis'])
        self.assertTrue(all(u['priority'] == 'HOLD' for u in units.values()))
        self.assertTrue(all(u['strongest_counterargument'] for u in units.values()))

    def test_actual_greek_control_not_fresh_pixels_or_exhaustive_apparatus(self):
        sources = {s['id']: s for s in self.r['sources']}
        self.assertFalse(sources['qdr4q169']['fresh_manuscript_pixels'])
        swete = sources['swete1905']
        self.assertEqual((swete['printed_page'], swete['pdf_page_one_based']), (56, 80))
        self.assertEqual(swete['sha256'],
                         '5f0bfffabf0e588fd32e15bdb24b027872616da219e7f02da3dbdc115cf97d85')
        self.assertFalse(swete['fresh_manuscript_pixels'])
        self.assertEqual(len(self.r['unconsulted_target_apparatus']), 4)

    def test_recent_routes_keep_identity_rights_and_actual_access_limits(self):
        p = self.r['recent_publications']
        self.assertEqual(p['scroll_count_hypotheses_preserved'], [1, 2])
        self.assertEqual(p['new_independent_manuscript_votes'], 0)
        self.assertFalse(p['assignment_independently_verified'])
        self.assertFalse(p['global_survival_map_completed'])
        self.assertFalse(p['individual_figure_credits_consulted'])
        d = p['article2025_download']
        self.assertFalse(d['pdf_acquired'])
        self.assertIsNone(d['pdf_sha256'])
        self.assertFalse(d['figure_visual_check'])
        self.assertFalse(d['auth_or_challenge_bypassed'])
        self.assertTrue(d['equivalent_automated_retries_parked'])
        entry = self.r['registry']['frozen_updated_entry']
        self.assertEqual(entry['identification_review']['status'],
                         'published-proposal-not-independent-physical-verification')
        routes = {a['url']: a for a in entry['access']}
        self.assertTrue(set(p['new_routes']) <= set(routes))
        self.assertEqual(routes[p['new_routes'][0]]['license_url'],
                         'https://creativecommons.org/licenses/by-nc/4.0/')
        self.assertEqual(routes[p['new_routes'][1]]['rights_status'], 'open-license')
        self.assertEqual(routes[p['new_routes'][1]]['license_url'],
                         'https://creativecommons.org/licenses/by/4.0/')

    def test_research_and_review_do_not_promote_source_english_or_canon(self):
        self.assertTrue(all(v is False for v in self.r['decisions'].values()))
        self.assertFalse(self.r['canonical_changes_applied'])
        self.assertEqual(self.r['source_priority'], 'HOLD')
        self.assertEqual(self.r['main_english_priority'], 'HOLD')
        self.assertEqual(self.r['review']['status'], 'pass')
        self.assertFalse(self.r['review']['repeat_until_agreement'])
        self.assertTrue((ROOT / self.r['report']).is_file())


if __name__ == '__main__':
    unittest.main()
