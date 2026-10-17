"""Check recorded numerical relationships, not transcription or source priority."""
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / 'sources/textual_restoration/comparisons/genesis5_age_systems.2026-10-16.v1.json'


class GenesisFiveAgeComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(RECORD.read_text())
        cls.rows = cls.data['rows']

    def test_all_linked_triads_and_loci(self):
        self.assertEqual(len(self.rows), 9)
        self.assertEqual(len({r['person'] for r in self.rows}), 9)
        loci = [v for r in self.rows for v in r['verses']]
        self.assertEqual(sorted(loci), list(range(3, 24)) + [25, 26, 27, 28, 30, 31])
        count = 0
        for row in self.rows:
            for profile in self.data['profiles']:
                with self.subTest(person=row['person'], profile=profile):
                    before, after, total = row[profile]
                    self.assertTrue(all(type(n) is int and n > 0 for n in row[profile]))
                    self.assertEqual(before + after, total)
                    count += 1
        self.assertEqual(count, self.data['derived_checks']['balanced_triads'])

    def test_patterns_do_not_collapse_distinct_profiles(self):
        expected = self.data['derived_checks']
        for profile in ('greek_swete', 'greek_rh2006'):
            paired = [r['person'] for r in self.rows
                      if [a-b for a, b in zip(r[profile], r['wlc'])] == [100, -100, 0]]
            self.assertEqual(paired, expected['greek_relative_to_wlc_plus100_minus100_same_total'])
        self.assertEqual([r['person'] for r in self.rows if r['sp_tf2024'] != r['wlc']],
                         expected['sp_differs_from_wlc'])
        self.assertEqual([r['person'] for r in self.rows if r['greek_swete'] != r['greek_rh2006']],
                         expected['greek_selected_profiles_differ'])
        methuselah = next(r for r in self.rows if r['person'] == 'Methuselah')
        self.assertEqual(methuselah['greek_swete'], [187, 782, 969])
        self.assertEqual(methuselah['greek_rh2006'], [167, 802, 969])

    def test_conditional_sums_and_inconsistent_hybrid(self):
        for profile, total in self.data['derived_checks']['sum_begetting_ages'].items():
            self.assertEqual(sum(r[profile][0] for r in self.rows), total)
        hybrid = self.data['derived_checks']['unattested_mixing_example']
        before, after, total = hybrid['triad']
        self.assertEqual(before + after, hybrid['sum'])
        self.assertNotEqual(before + after, total)
        self.assertFalse(hybrid['balanced'])

    def test_preservation_and_application_boundaries(self):
        q = self.data['qumran_control']
        self.assertFalse(q['numeral_preserved'])
        self.assertTrue(q['numeral_editorially_supplied'])
        self.assertFalse(q['discriminates_840_vs_740'])
        enoch = next(r for r in self.rows if r['person'] == 'Enoch')
        self.assertFalse(enoch['total_is_death_age'])
        for key in ('canonical_change', 'reader_application', 'novel_decipherment'):
            self.assertFalse(self.data[key])


if __name__ == '__main__':
    unittest.main()
