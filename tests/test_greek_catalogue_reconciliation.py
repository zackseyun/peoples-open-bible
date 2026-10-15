import copy
import json
import unittest

from tools.textual_restoration import greek_catalogue_reconciliation as module


class GreekHeldRowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads((module.ROOT / module.RECORD).read_text())

    def row(self, identifier, ordinal):
        return next(r for r in self.record['rows']
                    if (r['catalogue_id'], r['row_zero_based']) == (identifier, ordinal))

    def test_complete_pinned_overlay(self):
        result = module.validate(self.record)
        self.assertEqual(result['held_rows'], 73)
        self.assertEqual(result['source_files'], 11)
        self.assertEqual(result['books_with_navigation'], 39)
        self.assertEqual(result['additional_book_catalogue_pairs'], 45)
        self.assertFalse(result['manuscript_readings_verified'])
        self.assertFalse(result['private_inputs_verified'])

    def test_greek_order_is_not_hebrew_order(self):
        self.assertEqual(len(self.row(2, 17)['books']), 12)
        self.assertEqual(self.row(2, 17)['books'], self.row(3, 24)['books'])
        self.assertEqual(self.row(13, 22)['books'],
                         ['Joel', 'Obad', 'Jonah', 'Nah', 'Hab', 'Zeph', 'Hag', 'Zech', 'Mal'])

    def test_esdras_crosswalk_and_unresolved_labels_remain_distinct(self):
        for key in [(2, 26), (3, 13), (13, 9)]:
            self.assertEqual(self.row(*key)['books'], ['Ezra', 'Neh'])
        self.assertEqual(self.row(2, 25)['category'], 'expanded-corpus')
        for key in [(2, 13), (3, 12)]:
            self.assertEqual(self.row(*key)['category'], 'identity-hold')
        self.assertEqual(len(self.record['nomenclature_sources']), 2)

    def test_context_does_not_override_an_explicit_other_work(self):
        self.assertEqual(self.row(1307, 1)['books'], ['Gen'])
        self.assertEqual(self.row(1311, 0)['books'], [])
        self.assertEqual(self.row(1311, 0)['category'], 'mixed-non-ot')
        for i in range(8):
            self.assertEqual(self.row(966, i)['books'], ['Ps'])

    def test_excerpt_and_composite_dates_are_not_early_continuous_witnesses(self):
        self.assertEqual(self.row(2, 36)['category'], 'excerpts')
        self.assertEqual(self.row(2, 36)['books'], [])
        controls = self.record['special_controls']
        psalter = next(c for c in controls if c.get('catalogue_id') == 370)
        self.assertEqual(psalter['component_date'], 's. X')
        self.assertIn('Latin characters', psalter['note'])
        self.assertEqual(self.row(370, 19)['category'], 'unidentified')

    def test_missing_duplicate_or_extra_rows_fail(self):
        for mutation in ('missing', 'duplicate', 'extra'):
            d = copy.deepcopy(self.record)
            if mutation == 'missing': d['rows'].pop()
            elif mutation == 'duplicate': d['rows'].append(d['rows'][0])
            else: d['rows'][0]['row_zero_based'] = 999
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                module.validate(d)

    def test_source_identity_and_hash_drift_fail(self):
        for key, value in [('rid', 'Ra_wrong'), ('url', 'https://example.org'), ('sha256', '0' * 64)]:
            d = copy.deepcopy(self.record)
            d['source_inputs'][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                module.validate(d)

    def test_promotion_and_navigation_drift_fail(self):
        for mutation in ('promotion', 'navigation', 'category'):
            d = copy.deepcopy(self.record)
            if mutation == 'promotion': d['controls']['navigation_is_preserved_letters'] = True
            elif mutation == 'navigation': d['pob_book_navigation'][0]['combined_catalogue_ids'] = []
            else: d['rows'][0]['books'] = ['Gen']
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                module.validate(d)


if __name__ == '__main__':
    unittest.main()
