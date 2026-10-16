"""Verify explicitly reviewed Qumran-Digital display aliases, not physical joins.

This sidecar audit never relaxes the strict transcription index. It exports
locators and structural hashes, not transcription text or preserved-word counts.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path

from tools.textual_restoration.compare_transcription_releases import digest, sha
from tools.textual_restoration.index_published_parallels import (
    Element, direct_text_cell, document, index_document, primary_rows,
)


def structure(node):
    """Preserve decoded text, nested markup, attribute values and child order."""
    if isinstance(node, str):
        return node
    return [node.tag, sorted(node.attrs.items()), [structure(c) for c in node.children]]


def audit(raw, specification):
    fingerprint = sha(raw)
    matching = [i for i in specification['inputs'] if i['sha256'] == fingerprint]
    if len(matching) != 1:
        raise ValueError('input is not uniquely pinned')
    root = document(raw)
    bodies = [n for n in root.walk() if n.tag == 'body']
    times = [n for n in root.walk() if n.tag == 'time']
    if (len(bodies) != 1 or len(times) != 1
            or bodies[0].attrs.get('id') != specification['manuscript_html_id']
            or times[0].attrs.get('datetime') != matching[0]['release']):
        raise ValueError('manuscript/release mismatch')

    rows, occurrences, dom_occurrences = {}, defaultdict(list), defaultdict(list)
    for table, row in primary_rows(root):
        row_id = row.attrs.get('id')
        if not row_id or row_id in rows or not table.attrs.get('id'):
            raise ValueError('missing or duplicate row identity')
        cell = direct_text_cell(row)
        words = [n for n in cell.walk(exclude_alternatives=True) if n.has_class('word')]
        rows[row_id] = (table, row, cell, words)
        for position, word in enumerate(words):
            stable, dom = word.attrs.get('data-word-id'), word.attrs.get('id')
            if not stable or not dom:
                raise ValueError('missing token identity')
            occurrences[stable].append((row_id, position))
            dom_occurrences[dom].append((row_id, position))
    if not rows:
        raise ValueError('no primary rows')

    approved, approved_dom, results = {}, {}, []
    for pair in specification['pairs']:
        ids = pair['word_ids']
        if not ids or len(ids) != len(set(ids)) or any(i in approved for i in ids):
            raise ValueError('overlapping or invalid alias specification')
        if len(pair['placements']) != 2:
            raise ValueError('alias must have exactly two placements')
        payloads, placements, dom_ids = [], [], None
        for place in pair['placements']:
            if place['row_id'] not in rows:
                raise ValueError('missing alias row')
            table, row, cell, words = rows[place['row_id']]
            if (table.attrs['id'] != place['table_id']
                    or table.attrs.get('data-name') != place['column']
                    or row.attrs.get('data-name') != place['line']):
                raise ValueError('alias locator mismatch')
            if any(n.has_class('alternative-reading') for n in cell.walk()):
                raise ValueError('alternative reading in alias row requires review')
            # The final reference and tokens are siblings in one body-text span.
            # Fail closed if the publisher changes this reviewed layout.
            bodies = [c for c in cell.children if isinstance(c, Element)]
            if len(bodies) != 1 or not bodies[0].has_class('body-text'):
                raise ValueError('unreviewed text-cell layout')
            children = [c for c in bodies[0].children if isinstance(c, Element)]
            refs = [n for n in children if n.has_class('secondary-reference')
                    and n.text().strip() == place['reference']]
            if len(refs) != 1:
                raise ValueError('missing or ambiguous exact alias reference')
            tail = bodies[0].children[bodies[0].children.index(refs[0]) + 1:]
            if any(isinstance(c, str) and c.strip() for c in tail):
                raise ValueError('unwrapped text in alias block')
            if any(isinstance(c, Element) and c.has_class('word-space')
                   and (c.attrs != {'class': 'word-space'} or c.children != [' ']) for c in tail):
                raise ValueError('unreviewed alias spacing markup')
            block = [c for c in tail if isinstance(c, Element) and not c.has_class('word-space')]
            if (not all(n.has_class('word') for n in block)
                    or [n.attrs.get('data-word-id') for n in block] != ids):
                raise ValueError('alias block order or boundary mismatch')
            positions = [words.index(n) for n in block]
            current_dom = [n.attrs['id'] for n in block]
            if dom_ids is not None and current_dom != dom_ids:
                raise ValueError('alias DOM identities differ')
            dom_ids = current_dom
            payloads.append([structure(n) for n in block])
            placements.append({**place, 'token_positions_zero_based': positions,
                               'row_structure_sha256': digest(structure(row))})
        if payloads[0] != payloads[1]:
            raise ValueError('alias token structures differ')
        for offset, (stable, dom) in enumerate(zip(ids, dom_ids)):
            wanted = [(p['row_id'], p['token_positions_zero_based'][offset]) for p in placements]
            if occurrences[stable] != wanted or dom_occurrences[dom] != wanted:
                raise ValueError('unexpected alias occurrence or occurrence order')
            approved[stable] = wanted
            approved_dom[dom] = wanted
        results.append({'word_ids': ids, 'dom_ids': dom_ids, 'placements': placements,
                        'token_structure_sha256': digest(payloads[0])})
    if {k for k, v in occurrences.items() if len(v) > 1} != set(approved):
        raise ValueError('unapproved repeated stable ID')
    if {k for k, v in dom_occurrences.items() if len(v) > 1} != set(approved_dom):
        raise ValueError('unapproved repeated DOM ID')
    try:
        index_document(raw)
    except ValueError as error:
        if str(error) != 'missing or duplicate primary word ID':
            raise
        strict_error = str(error)
    else:
        raise ValueError('expected strict index HOLD was not reproduced')
    return {'html_sha256': fingerprint, 'release': matching[0]['release'],
            'specification_sha256': digest(specification), 'pairs': results,
            'strict_index_status': 'HOLD', 'strict_index_error': strict_error,
            'policy': {'scope': 'Explicit published display aliases only',
                       'physical_identity_resolved': False, 'word_joins_validated': False,
                       'preserved_word_count_asserted': False, 'transcription_exported': False,
                       'canonical_source_changed': False, 'english_changed': False}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('html', type=Path)
    parser.add_argument('specification', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.html.read_bytes(), json.loads(args.specification.read_text())), indent=2))


if __name__ == '__main__':
    main()
