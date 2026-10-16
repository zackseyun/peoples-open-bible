"""Compare primary-row bytes across Qumran-Digital releases, not original texts.

Raw pages remain private. Output contains IDs and hashes, never transcriptions.
An unchanged row is unchanged published markup, not a new manuscript vote or
certification of its editorial restoration. Parallel rows are not primary text.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

from tools.textual_restoration.index_published_parallels import (
    Document, document, index_document, primary_rows,
)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha(json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode())


class RawRows(Document):
    """Use parser events, never tag-like text in comments/attributes, as bounds."""

    def __init__(self, source, selected):
        super().__init__()
        self.source = source
        self.line_offsets = [0] + [m.end() for m in re.finditer('\n', source)]
        self.selected = selected
        self.active = None
        self.rows = []

    def source_offset(self):
        line, column = self.getpos()
        return self.line_offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            if self.active is not None:
                raise ValueError('nested row unsupported')
            row_id = dict(attrs).get('id')
            if row_id in self.selected:
                self.active = (row_id, self.source_offset())
        super().handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        super().handle_endtag(tag)
        if tag == 'tr' and self.active is not None:
            end = self.source_offset()
            closing = re.match(r'</tr\s*>', self.source[end:], re.IGNORECASE)
            if closing is None:
                raise ValueError('unsupported raw row closing tag')
            row_id, start = self.active
            raw_row = self.source[start:end + closing.end()].encode('utf-8')
            self.rows.append((row_id, sha(raw_row)))
            self.active = None


def primary_snapshot(raw):
    # Validate complete HTML, manuscript/date metadata, primary IDs and word joins
    # before using the raw row slices. Do not accept a valid-looking error page.
    index = index_document(raw)
    expected = [row.attrs['id'] for _, row in primary_rows(document(raw))]
    if not expected:
        raise ValueError('no primary transcription rows')
    source = raw.decode('utf-8')
    parser = RawRows(source, set(expected))
    parser.feed(source)
    parser.close()
    if len(parser.stack) != 1 or parser.active is not None:
        raise ValueError('incomplete raw row parsing')
    rows = parser.rows
    if [r[0] for r in rows] != expected:
        raise ValueError('raw row slices disagree with validated primary-row order')
    return {
        'html_sha256': sha(raw),
        'bytes': len(raw),
        'manuscript_html_id': index['manuscript_html_id'],
        'release': index['release'],
        'parser_repairs': index['html_repairs'],
        'primary_rows': len(rows),
        'ordered_primary_row_digest': digest(rows),
        'row_hashes': rows,
    }


def compare(old_raw, new_raw):
    old, new = primary_snapshot(old_raw), primary_snapshot(new_raw)
    if old['manuscript_html_id'] != new['manuscript_html_id']:
        raise ValueError('different manuscript HTML IDs; resolve identity before comparing')
    a, b = dict(old['row_hashes']), dict(new['row_hashes'])
    common = set(a) & set(b)
    old_order = [k for k, _ in old['row_hashes'] if k in common]
    new_order = [k for k, _ in new['row_hashes'] if k in common]
    for data in (old, new):
        data.pop('row_hashes')
    changed = sorted(k for k in common if a[k] != b[k])
    added, removed = sorted(set(b) - set(a)), sorted(set(a) - set(b))
    return {
        'old': old, 'new': new,
        'common_rows': len(common),
        'identical_primary_rows': sum(a[k] == b[k] for k in common),
        'changed_primary_row_ids': changed,
        'added_primary_row_ids': added,
        'removed_primary_row_ids': removed,
        'common_row_order_unchanged': old_order == new_order,
        'primary_layer_identical': not (changed or added or removed) and old_order == new_order,
        'policy': {
            'compared_layer': 'Exact raw primary tr elements, including markup and supplied-character sigla; not normalized consonants',
            'parallel_rows_compared': False,
            'changed_markup_is_reading_change': False,
            'unchanged_markup_certifies_original_reading': False,
            'new_release_is_independent_witness': False,
            'text_exported': False,
            'next_action_if_changed': 'Inspect changed primary rows in both complete edition contexts before classifying textual, metadata or presentation changes',
        },
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('old_html', type=Path)
    parser.add_argument('new_html', type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(compare(args.old_html.read_bytes(), args.new_html.read_bytes()), indent=2))


if __name__ == '__main__':
    main()
