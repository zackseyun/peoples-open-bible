import tempfile
import unittest
from pathlib import Path

import yaml

from tools.audit_footnotes import (
    anchor_phrase_for, audit_one, is_phrase_like, plan_anchors,
    quoted_alternatives,
)


def record(text, markers, lexical=None, notes=None):
    notes = notes or {}
    return {
        'translation': {
            'text': text,
            'footnotes': [
                {'marker': m, 'text': notes.get(m, 'A note.')} for m in markers
            ],
        },
        'lexical_decisions': lexical or [],
    }


def audit(doc):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / '001.yaml'
        p.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False))
        return audit_one(p)


class MarkerRecognitionTests(unittest.TestCase):
    """A marker is whatever the record declares, not [a]-[z]."""

    def test_localised_markers_are_anchored(self):
        for marker, text in [
            ('क', 'यह एक पंक्ति[क] है।'),
            ('أ', 'هذا سطر[أ] هنا.'),
            ('а', 'Это строка[а] здесь.'),
            ('주1', '이것은 한 줄[주1]입니다.'),
        ]:
            self.assertEqual(audit(record(text, [marker]))['status'], 'ok', marker)

    def test_hyphenated_and_numeric_markers_are_anchored(self):
        for marker in ['5-6', '13', '54.1', 'v14-15']:
            doc = record(f'And they multiplied[{marker}] greatly.', [marker])
            self.assertEqual(audit(doc)['status'], 'ok', marker)

    def test_genuinely_unanchored_marker_is_reported(self):
        got = audit(record('And they multiplied greatly.', ['a']))
        self.assertEqual(got['status'], 'orphaned')
        self.assertEqual(got['orphans'], ['a'])

    def test_partial_when_only_some_markers_are_anchored(self):
        got = audit(record('And they[a] multiplied greatly.', ['a', 'b']))
        self.assertEqual(got['status'], 'partial')
        self.assertEqual(got['orphans'], ['b'])


class PhraseKeyedTests(unittest.TestCase):
    def test_phrase_keyed_record_is_not_an_orphan(self):
        text = 'I am she who is found in those who are afraid.'
        got = audit(record(text, ['she who', 'those who are afraid']))
        self.assertEqual(got['status'], 'phrase_keyed')

    def test_marker_carrying_its_own_brackets_is_anchored_not_stray(self):
        got = audit(record('from Judah as a king, [[God and man]];',
                           ['[God and man]']))
        self.assertEqual(got['status'], 'ok')

    def test_short_tokens_are_not_treated_as_phrases(self):
        self.assertFalse(is_phrase_like('a'))
        self.assertFalse(is_phrase_like('13'))
        self.assertFalse(is_phrase_like('v14-15'))
        self.assertTrue(is_phrase_like('those who are afraid'))


class MarkerKeyDefectTests(unittest.TestCase):
    def test_duplicate_marker_key_is_skipped(self):
        """jubilees 20:2, 21:13, 37:14, thunder_perfect_mind/093 —
        anchoring these would emit the same inline marker twice."""
        got = audit(record('And they multiplied greatly.', ['a', 'a']))
        self.assertEqual(got['status'], 'duplicate_marker')
        self.assertEqual(got['declared'], ['a'])

    def test_duplicate_key_is_skipped_even_when_already_anchored(self):
        got = audit(record('And they[a] multiplied greatly.', ['a', 'a']))
        self.assertEqual(got['status'], 'duplicate_marker')
        self.assertEqual(got['orphans'], [])

    def test_blank_marker_key_cannot_be_anchored(self):
        got = audit(record('This marriage is different.', [' ']))
        self.assertEqual(got['status'], 'blank_marker')

    def test_stray_inline_marker_of_a_declared_shape(self):
        got = audit(record('your household[a], which sinned against us[h].',
                           ['a']))
        self.assertEqual(got['status'], 'extra_marker')
        self.assertEqual(got['extras'], ['h'])

    def test_editorial_brackets_are_not_stray_markers(self):
        got = audit(record('he will save [all the nations and] Israel[a].',
                           ['a']))
        self.assertEqual(got['status'], 'ok')


class AnchorFromNoteContentTests(unittest.TestCase):
    """Placement comes from the note's own content, never from clause
    position or from prior revision history."""

    LEXICAL = [{
        'source_word': 'ἀδελφοί',
        'chosen': 'brothers',
        'alternatives': ['brothers and sisters', 'siblings'],
    }]

    def test_quote_extraction_handles_every_quote_style(self):
        self.assertIn('welcomes', quoted_alternatives("Or 'welcomes' here."))
        self.assertIn('welcomes', quoted_alternatives('Or “welcomes” here.'))
        self.assertIn('welcomes', quoted_alternatives('Or "welcomes" here.'))

    def test_quoted_alternative_recovers_the_chosen_phrase(self):
        note = {'text': 'Or “brothers and sisters”; the Greek is masculine.'}
        self.assertEqual(anchor_phrase_for(note, self.LEXICAL), 'brothers')

    def test_note_with_no_matching_alternative_is_unplaceable(self):
        note = {'text': "Or 'is consoling himself concerning you'."}
        self.assertIsNone(anchor_phrase_for(note, self.LEXICAL))

    def test_marker_lands_after_the_phrase_the_note_discusses(self):
        text = 'For consider your calling, brothers: not many were wise.'
        doc = record(text, ['a'], self.LEXICAL,
                     {'a': 'Or “brothers and sisters”.'})
        rec = audit(doc)
        new_text, placed, unplaceable = plan_anchors(rec, doc)
        self.assertEqual(placed, [('a', 'brothers')])
        self.assertEqual(unplaceable, [])
        self.assertEqual(
            new_text,
            'For consider your calling, brothers[a]: not many were wise.')

    def test_markers_are_not_clustered_at_the_first_clause_boundary(self):
        """The defect the old --auto-fix produced: markers piled at a
        clause start with no relation to what each note discusses."""
        lexical = [
            {'chosen': 'receives', 'alternatives': ['welcomes']},
            {'chosen': 'sent me', 'alternatives': ['dispatched me']},
        ]
        text = 'Whoever receives one of such children, not me, but the one who sent me.'
        doc = record(text, ['a', 'b'], lexical,
                     {'a': "Or 'welcomes'.", 'b': "Or 'dispatched me'."})
        new_text, placed, _ = plan_anchors(audit(doc), doc)
        self.assertEqual(
            new_text,
            'Whoever receives[a] one of such children, not me, '
            'but the one who sent me[b].')
        self.assertNotIn('[a][b]', new_text)

    def test_unplaceable_markers_are_left_alone(self):
        text = 'For consider your calling, brothers: not many were wise.'
        doc = record(text, ['a'], self.LEXICAL, {'a': 'A general comment.'})
        new_text, placed, unplaceable = plan_anchors(audit(doc), doc)
        self.assertEqual(new_text, text)
        self.assertEqual(placed, [])
        self.assertEqual(unplaceable, ['a'])


if __name__ == '__main__':
    unittest.main()
