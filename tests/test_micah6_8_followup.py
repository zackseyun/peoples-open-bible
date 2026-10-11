"""Evidence-role and historical-input guards, not translation certification."""
import hashlib
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / 'sources/textual_restoration/comparisons/micah6_8_followup.2026-10-10.v1.json'


class MicahFollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads(RECEIPT.read_text())

    def test_historical_corpus_pin_and_preserved_predecessor(self):
        pin = self.r['canonical_input']
        raw = subprocess.check_output(['git', 'show', self.r['baseline_commit'] + ':' + pin['path']], cwd=ROOT)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), pin['sha256'])
        old = subprocess.check_output(['git', 'show', self.r['predecessor_commit'] + ':' + self.r['predecessor_receipt']], cwd=ROOT)
        self.assertEqual(old, (ROOT / self.r['predecessor_receipt']).read_bytes())
        self.assertFalse(json.loads(old)['sources']['becking']['pdf_acquired'])

    def test_new_access_does_not_erase_old_failure_or_approve_whole_verse(self):
        b = self.r['becking']
        self.assertEqual(b['prior_route_http_status'], 403)
        self.assertTrue(b['pdf_acquired'])
        self.assertEqual(b['bytes'], 156204)
        self.assertEqual(b['printed_labels'], {'הצנע': 'infinitive-construct', 'לכת': 'infinitive-absolute'})
        self.assertFalse(b['auth_or_challenge_bypassed'])
        self.assertFalse(b['cause_of_error_assigned'])
        self.assertFalse(b['whole_verse_proposal_approved'])

    def test_syriac_edition_is_not_two_independent_hebrew_votes(self):
        s = self.r['peshitta']
        self.assertEqual(s['explicit_chapter_locator'], '06:08')
        self.assertIn('ܥܬܝܕ', s['target'])
        self.assertIn('#2#', s['displayed_lord_name_annotation'])
        self.assertFalse(s['annotation_resolved'])
        self.assertFalse(s['local_independence_from_greek_established'])
        self.assertFalse(s['unique_hebrew_retroversion_established'])
        self.assertFalse(s['fresh_manuscript_pixels'])

    def test_modern_latin_is_not_ancient_attestation(self):
        l = self.r['latin']
        self.assertIn('1986', l['edition'])
        self.assertEqual(l['role'], 'modern-revised-latin-interpretation-not-ancient-attestation')
        self.assertFalse(l['ancient_latin_manuscript_attestation_established'])
        self.assertFalse(l['clementine_or_stuttgart_target_consulted'])

    def test_sirach_alignment_and_lexical_not_manuscript_role(self):
        s = self.r['sirach']
        self.assertIn('Muraoka', s['edition'])
        self.assertEqual(s['targets'][1]['viewer_reference'], '32:3')
        self.assertEqual(s['targets'][1]['target'], 'והצנע שכל')
        self.assertEqual(s['לכת_status'], 'marginal-gloss-not-second-base-text-occurrence')
        self.assertEqual(s['witness_period'], 'medieval-Genizah')
        for k in ['fresh_manuscript_pixels', 'ancient_attestation_of_these_targets_established',
                  'additional_micah_witness', 'uniquely_establishes_prudence_over_modesty']:
            self.assertFalse(s[k])

    def test_no_canonical_promotion_and_no_repeated_agreement_loop(self):
        self.assertTrue(all(v is False for v in self.r['decisions'].values()))
        self.assertFalse(self.r['review']['repeat_until_agreement'])
        self.assertTrue((ROOT / self.r['report']).is_file())
        self.assertIn('BHQ13 target apparatus/commentary', self.r['unconsulted_controls'])


if __name__ == '__main__':
    unittest.main()
