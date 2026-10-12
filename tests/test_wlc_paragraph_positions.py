"""Existing WLC position semantics; no canonical renderer migration."""
from pathlib import Path
import unittest

from tools import wlc
from tools.textual_restoration import compare_uxlc_wlc as comparison


ROOT = Path(__file__).resolve().parents[1]


def fixture(body):
    raw = ('<osis><verse osisID="Gen.1.1">' + body
           + '</verse></osis>').encode('utf-8')
    return comparison.parse_wlc(raw)[(1, 1)]


class ParagraphPositionTests(unittest.TestCase):
    def test_actual_chronicles_marker_position_and_legacy_output(self):
        row = comparison.parse_wlc(
            (ROOT / 'sources/ot/wlc/1Chr.xml').read_bytes())[(12, 14)]
        words = row['written']
        marker = next(a for a in row['annotations']
                      if a['attributes'].get('type') == 'x-samekh')
        self.assertEqual(marker['code'], 'ס')
        self.assertEqual(marker['position'], 3)
        self.assertEqual([w['text'] for w in words], [
            'יִרְמְיָ֨הוּ֙', 'הָ/עֲשִׂירִ֔י', 'מַכְבַּנַּ֖י',
            'עַשְׁתֵּ֥י', 'עָשָֽׂר'])
        self.assertLess(words[1]['position'], marker['position'])
        self.assertLess(marker['position'], words[2]['position'])
        # Record current behavior, not an endorsement of diplomatic accuracy.
        self.assertEqual(wlc.load_verse('1CH', 12, 14, ROOT / 'sources').hebrew_text,
                         'יִרְמְיָ֨הוּ֙ הָ/עֲשִׂירִ֔י מַכְבַּנַּ֖י עַשְׁתֵּ֥י עָשָֽׂרס׃')
        stream = comparison.written_stream(row)
        self.assertEqual(stream, ''.join(w['text'] for w in words) + '׃')
        self.assertNotIn('ס', stream)

    def test_internal_pe_and_samekh_preserve_annotation_word_order(self):
        for kind, letter in [('x-pe', 'פ'), ('x-samekh', 'ס')]:
            with self.subTest(kind=kind):
                row = fixture(f'<w>אב</w><seg type="{kind}">{letter}</seg><w>גד</w>')
                self.assertEqual([(w['position'], w['text']) for w in row['written']],
                                 [(0, 'אב'), (2, 'גד')])
                self.assertEqual(row['annotations'], [{
                    'position': 1, 'kind': 'seg',
                    'attributes': {'type': kind}, 'code': letter}])
                self.assertEqual(comparison.written_stream(row), 'אבגד')

    def test_paragraph_symbols_excluded_not_genuine_word_letters(self):
        row = fixture('<w>ספר</w><seg type="x-samekh">ס</seg>'
                      '<w>פס</w><seg type="x-pe">פ</seg>'
                      '<seg type="x-maqqef">־</seg><w>אב</w>'
                      '<seg type="x-sof-pasuq">׃</seg>')
        self.assertEqual(comparison.written_stream(row), 'ספרפס־אב׃')
        self.assertEqual(comparison.normalized(comparison.written_stream(row),
                                               'consonants'), 'ספרפסאב')


if __name__ == '__main__':
    unittest.main()
