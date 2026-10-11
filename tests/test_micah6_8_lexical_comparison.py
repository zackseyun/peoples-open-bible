"""Historical evidence bindings, not proof of an optimum translation."""
import hashlib
import json
from pathlib import Path
import subprocess
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / 'sources/textual_restoration/comparisons/micah6_8_lexical.2026-10-10.v1.json'


class MicahLexicalComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = json.loads(RECEIPT.read_text())

    def test_historical_inputs_not_current_corpus_certification(self):
        for pin in [self.r['canonical_input'], self.r['drafting_policy'],
                    {'path': self.r['sources']['qdr']['book_map_path'],
                     'sha256': self.r['sources']['qdr']['book_map_sha256']}]:
            raw = subprocess.check_output(['git', 'show', self.r['baseline_commit'] + ':' + pin['path']], cwd=ROOT)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), pin['sha256'])
        pin = self.r['canonical_input']
        record = yaml.safe_load(subprocess.check_output(['git', 'show', self.r['baseline_commit'] + ':' + pin['path']], cwd=ROOT))
        self.assertEqual(record['id'], 'MIC.6.8')
        self.assertIn('הַצְנֵ֥עַ לֶ֖כֶת', record['source']['text'])
        self.assertIn(pin['retained_english_phrase'], record['translation']['text'])
        self.assertFalse(self.r['drafting_policy']['independent_lexical_evidence'])

    def test_morphology_is_editorial_and_does_not_settle_lexical_meaning(self):
        s = self.r['sources']['oshb']
        self.assertEqual([w['morph'] for w in s['words']], ['HC/Vha', 'HVqc'])
        self.assertEqual(s['role'], 'editorial-morphology-not-independent-manuscript')
        self.assertFalse(s['lexical_sense_settled'])
        self.assertFalse(self.r['sources']['gesenius']['section113_target_specific'])

    def test_actual_edition_and_greek_not_new_hebrew_variant(self):
        b, s = self.r['sources']['bdb'], self.r['sources']['swete']
        self.assertEqual(b['pdf_page_one_based'], 2080)
        self.assertFalse(b['original_printed_page_verified'])
        self.assertFalse(b['fresh_halot_consultation'])
        self.assertEqual((s['printed_page'], s['pdf_page_one_based']), (35, 59))
        self.assertTrue(s['whole_page_and_apparatus_visually_read'])
        self.assertIn('ἕτοιμον', s['selected_published_phrase'])
        self.assertFalse(s['unique_hebrew_retroversion_established'])
        self.assertFalse(s['comprehensive_greek_apparatus_consulted'])

    def test_coverage_gap_and_inaccessible_counterargument_are_not_support(self):
        q, b = self.r['sources']['qdr'], self.r['sources']['becking']
        self.assertEqual(q['target_tag_counts'], {'4Q81': 0, '4Q82': 0, 'Mur88': 0})
        self.assertFalse(q['attested_omission'])
        self.assertFalse(q['complete_known_manuscript_census'])
        self.assertFalse(b['printed_argument_consulted'])
        self.assertFalse(b['author_error_established'])
        self.assertFalse(b['pdf_acquired'])
        self.assertIsNone(b['pdf_sha256'])
        self.assertEqual(b['ordinary_download_http_status'], 403)
        self.assertFalse(b['auth_or_challenge_bypassed'])

    def test_scoped_research_does_not_promote_canonical_changes(self):
        self.assertTrue(all(value is False for value in self.r['decisions'].values()))
        self.assertFalse(self.r['review']['repeat_until_agreement'])
        self.assertTrue((ROOT / self.r['report']).is_file())


if __name__ == '__main__':
    unittest.main()
