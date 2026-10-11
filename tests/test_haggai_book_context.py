"""Source-form and prompt-delivery guards, not translation certification."""
from pathlib import Path
import unicodedata
import unittest
import xml.etree.ElementTree as ET

from tools import build_review_brief

ROOT = Path(__file__).resolve().parents[1]


def consonants(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                   if '\u05d0' <= c <= '\u05ea')


class HaggaiBookContextTests(unittest.TestCase):
    def test_target_morphology_and_actual_clause_reach_consumer(self):
        xml = ET.parse(ROOT / 'sources/ot/wlc/Hag.xml')
        verse = next(v for v in xml.iter() if v.get('osisID') == 'Hag.2.7')
        words = {consonants(w.text or ''): w for w in verse.iter()
                 if w.tag.endswith('w')}
        self.assertEqual(words['ובאו'].get('morph'), 'HC/Vqp3cp')
        self.assertEqual(words['חמדת'].get('morph'), 'HNcfsc')
        context = build_review_brief.load_book_context('haggai', None)
        self.assertIn('ובאוחמדתכלהגוים', consonants(context))
        self.assertNotIn('החמדתיאתכלהגוים', consonants(context))
        self.assertIn('feminine singular construct noun', context)
        self.assertIn('plural verb', context)
        self.assertNotIn('plural in MT', context)

    def test_interpretation_is_not_a_number_only_or_versional_source_rule(self):
        context = build_review_brief.load_book_context('haggai', None)
        self.assertIn('Number alone does not settle the referent', context)
        self.assertIn('plural genitive', context)
        self.assertIn('silver/gold context', context)
        self.assertIn('Neither rendering alone proves different Hebrew letters', context)
        self.assertIn('do not force or exclude', context)
        self.assertIn('τὰ ἐκλεκτά', context)
        self.assertIn('desideratus cunctis gentibus', context)

    def test_explanation_link_resolves(self):
        context = build_review_brief.load_book_context('haggai', None)
        path = 'docs/HAGGAI_2_7_NUMBER_AND_VERSION_COMPARISON_2026-10-10.md'
        self.assertIn(path, context)
        self.assertTrue((ROOT / path).is_file())


if __name__ == '__main__':
    unittest.main()
