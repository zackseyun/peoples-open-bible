import copy
import json
import unittest

from tools.textual_restoration.audit_display_aliases import audit
from tools.textual_restoration.compare_transcription_releases import sha


TOKENS = ('<span class="word" id="d10" data-word-id="10">[--</span>'
          '<span class="word-space"> </span>'
          '<span class="word" id="d11" data-word-id="11">]x[</span>'
          '<span class="word-space"> </span>'
          '<span class="word" id="d12" data-word-id="12">--]</span>')


def fixture():
    rows = []
    placements = []
    for i, ref in [(1, '(other,0 + test B,0)'), (2, '(other,0 + test A,0)')]:
        prefix = ('<span class="secondary-reference">(other,0)</span>'
                  '<span class="word" id="d20" data-word-id="20">[context]</span>') if i == 1 else ''
        rows.append(f'<table class="chapter-column" id="c{i}" data-name="{i}"><tbody>'
                    f'<tr class="line-verse" id="r{i}" data-name="0"><td class="line-text">'
                    f'<span class="body-text">{prefix}<span class="secondary-reference">{ref}</span>'
                    f'{TOKENS}</span></td></tr></tbody></table>')
        placements.append({'table_id': f'c{i}', 'row_id': f'r{i}', 'column': str(i),
                           'line': '0', 'reference': ref})
    raw = ('<html><body id="transcription_id_1080"><time datetime="2026-10-06"></time>'
           + ''.join(rows) + '</body></html>').encode()
    spec = {'manuscript_html_id': 'transcription_id_1080',
            'inputs': [{'release': '2026-10-06', 'sha256': sha(raw)}],
            'pairs': [{'word_ids': ['10', '11', '12'], 'placements': placements}]}
    return raw, spec


class DisplayAliasTests(unittest.TestCase):
    def changed(self, old, new, error):
        raw, spec = fixture()
        self.assertIn(old, raw)
        raw = raw.replace(old, new, 1)
        spec['inputs'][0]['sha256'] = sha(raw)  # Exercise semantic checks, not only pinning.
        with self.assertRaisesRegex(ValueError, error):
            audit(raw, spec)

    def test_explicit_alias_preserves_occurrences_and_strict_hold(self):
        raw, spec = fixture()
        result = audit(raw, spec)
        self.assertEqual(result['strict_index_status'], 'HOLD')
        self.assertEqual(result['pairs'][0]['placements'][0]['token_positions_zero_based'], [1, 2, 3])
        self.assertEqual(result['pairs'][0]['placements'][1]['token_positions_zero_based'], [0, 1, 2])
        self.assertFalse(result['policy']['physical_identity_resolved'])
        self.assertFalse(result['policy']['word_joins_validated'])
        self.assertNotIn('[context]', json.dumps(result))
        self.assertNotIn(']x[', json.dumps(result))

    def test_unpinned_input_fails(self):
        raw, spec = fixture()
        with self.assertRaisesRegex(ValueError, 'not uniquely pinned'):
            audit(raw + b' ', spec)
        spec['inputs'].append(copy.deepcopy(spec['inputs'][0]))
        with self.assertRaisesRegex(ValueError, 'not uniquely pinned'):
            audit(raw, spec)

    def test_metadata_and_locator_changes_fail(self):
        self.changed(b'transcription_id_1080', b'transcription_id_1081', 'manuscript/release')
        self.changed(b'2026-10-06', b'2026-10-07', 'manuscript/release')
        self.changed(b'id="c1"', b'id="c3"', 'locator')
        self.changed(b'id="r1" data-name="0"', b'id="r1" data-name="1"', 'locator')

    def test_exact_reciprocal_reference_required(self):
        self.changed(b'(other,0 + test B,0)', b'(other,0 + test B,1)', 'exact alias reference')
        self.changed(b'(other,0 + test A,0)', b'(other,0 + test A,1)', 'exact alias reference')

    def test_token_text_attributes_and_nested_markup_are_compared(self):
        self.changed(b']x[', b']y[', 'structures differ')
        self.changed(b'class="word" id="d10"', b'class="word no-details" id="d10"', 'structures differ')
        self.changed(b']x[', b'<b>]x[</b>', 'structures differ')
        self.changed(b']x[', b'<span class="alternative-reading">]x[</span>', 'alternative reading')

    def test_dom_identity_changes_fail(self):
        self.changed(b'id="d10"', b'id="d99"', 'DOM identities differ')

    def test_missing_reordered_inserted_tokens_fail(self):
        self.changed(b'data-word-id="10"', b'data-word-id="13"', 'block order')
        self.changed(b'data-word-id="10"', b'data-word-id="12"', 'block order')
        first = b'<span class="word" id="d10" data-word-id="10">[--</span>'
        self.changed(first, b'', 'block order')
        self.changed(first, first + b'<span class="word" id="d99" data-word-id="99">extra</span>', 'block order')

    def test_extra_duplicate_occurrence_is_not_deduplicated(self):
        extra = (b'<table class="chapter-column" id="c3"><tbody><tr class="line-verse" id="r3">'
                 b'<td class="line-text"><span class="word" id="d10" data-word-id="10">[--</span>'
                 b'</td></tr></tbody></table>')
        self.changed(b'</body>', extra + b'</body>', 'unexpected alias occurrence')

    def test_unapproved_duplicates_fail(self):
        extra = (b'<span class="word" id="d30" data-word-id="30">x</span>'
                 b'<span class="word" id="d30" data-word-id="30">x</span>')
        self.changed(b'<span class="body-text">', b'<span class="body-text">' + extra,
                     'unapproved repeated stable ID')
        extra = (b'<span class="word" id="d30" data-word-id="30">x</span>'
                 b'<span class="word" id="d30" data-word-id="31">x</span>')
        self.changed(b'<span class="body-text">', b'<span class="body-text">' + extra,
                     'unapproved repeated DOM ID')

    def test_spacing_cannot_hide_extra_text(self):
        self.changed(b'<span class="word-space"> </span>', b'<span class="word-space">x</span>', 'spacing markup')
        self.changed(b'<span class="word-space"> </span>', b'x', 'unwrapped text')

    def test_parallel_display_is_not_a_primary_occurrence(self):
        raw, spec = fixture()
        extra = ('<tr class="parallel-line"><td><span class="word" id="d10" '
                 'data-word-id="10">parallel</span></td></tr>').encode()
        raw = raw.replace(b'</tbody>', extra + b'</tbody>', 1)
        spec['inputs'][0]['sha256'] = sha(raw)
        self.assertEqual(audit(raw, spec)['strict_index_status'], 'HOLD')

    def test_overlapping_specification_fails(self):
        raw, spec = fixture()
        spec['pairs'].append(copy.deepcopy(spec['pairs'][0]))
        with self.assertRaisesRegex(ValueError, 'overlapping'):
            audit(raw, spec)


if __name__ == '__main__':
    unittest.main()
