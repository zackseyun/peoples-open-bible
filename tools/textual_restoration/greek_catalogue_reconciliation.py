"""Verify a manually reviewed catalogue overlay, not manuscript readings.

Normal checks need only Git artifacts. --verify-private-inputs additionally
replays exact held-row hashes against the privately retained catalogue HTML.
Neither mode independently adjudicates the manual book classifications.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

from tools.textual_restoration.greek_catalogue_screen import detail_payload

ROOT = Path(__file__).resolve().parents[2]
RECORD = 'sources/textual_restoration/discovery/greek_catalogue_held_rows.2026-10-15.v1.json'
CATEGORIES = {'navigation', 'excerpts', 'expanded-corpus', 'identity-hold',
              'mixed-non-ot', 'nt', 'other-christian', 'paratext', 'unidentified'}
FALSE_CONTROLS = {'previous_specific_rows_changed', 'original_snapshot_changed',
                  'navigation_is_preserved_letters', 'range_normalized_to_pob',
                  'new_independent_witnesses_counted', 'canonical_source_or_english_changed',
                  'imagegen_used_as_evidence', 'raw_catalogue_descriptions_exported'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def row_hash(row):
    raw = json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    return hashlib.sha256(raw).hexdigest()


def validate(record, *, root=ROOT, verify_private=False):
    raw = (root / record['base']['path']).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == record['base']['sha256'], 'Snapshot pin mismatch')
    base = json.loads(raw)
    candidates = {c['catalogue_id']: c for c in base['candidates']
                  if c['unresolved_content_row_ordinals']}
    expected = {(i, ordinal) for i, c in candidates.items()
                for ordinal in c['unresolved_content_row_ordinals']}
    rows = record['rows']
    keys = [(r['catalogue_id'], r['row_zero_based']) for r in rows]
    require(len(keys) == len(set(keys)) and set(keys) == expected, 'Held-row coverage mismatch')
    require(record['controls']['held_rows_accounted_for'] == len(expected), 'Count mismatch')
    require(set(record['controls']) == FALSE_CONTROLS | {'held_rows_accounted_for'},
            'Missing or unknown coverage control')
    require(all(record['controls'][k] is False for k in FALSE_CONTROLS),
            'Unsupported coverage/promotion claim')
    inputs = record['source_inputs']
    require(len(inputs) == len(candidates) and
            {p['catalogue_id'] for p in inputs} == set(candidates), 'Input coverage mismatch')
    pins = {p['url']: p for p in base['acquisition_inputs']}
    payloads = {}
    for item in inputs:
        c = candidates[item['catalogue_id']]
        require(item['rid'] == c['rid'] and item['url'] == c['url'], 'Identity mismatch')
        require(all(item[k] == pins[c['url']][k] for k in ('path', 'url', 'sha256')),
                'Source pin mismatch')
        if verify_private:
            source = Path(item['path']).read_bytes()
            require(hashlib.sha256(source).hexdigest() == item['sha256'], 'Private input drift')
            payload = detail_payload(source.decode())
            require(payload['canRead'] is True and
                    payload['manuscript']['id'] == item['catalogue_id'] and
                    payload['manuscript']['rid'] == item['rid'], 'Private identity/access mismatch')
            payloads[item['catalogue_id']] = payload
    book_set = {b['book'] for b in base['pob_book_navigation']}
    for r in rows:
        require(r['category'] in CATEGORIES, 'Unknown category')
        require(set(r['books']) <= book_set and len(set(r['books'])) == len(r['books']),
                'Unknown or duplicate book')
        require(bool(r['books']) == (r['category'] == 'navigation'), 'Navigation role mismatch')
        require(re.fullmatch('[0-9a-f]{64}', r['row_sha256']) is not None, 'Invalid row hash')
        if verify_private:
            entry = payloads[r['catalogue_id']]['contentOverview'][r['row_zero_based']]
            require(row_hash(entry) == r['row_sha256'], 'Private held-row drift')
    require(record['category_counts'] == dict(Counter(r['category'] for r in rows)),
            'Category counts mismatch')
    navigation = []
    for b in base['pob_book_navigation']:
        original = set(b['specific_structured_detail_ids'])
        added = {r['catalogue_id'] for r in rows if b['book'] in r['books']} - original
        navigation.append({'book': b['book'], 'original_catalogue_ids': sorted(original),
                           'additional_catalogue_ids': sorted(added),
                           'combined_catalogue_ids': sorted(original | added)})
    require(record['pob_book_navigation'] == navigation, 'Derived navigation mismatch')
    return {'held_rows': len(rows), 'private_inputs_verified': verify_private,
            'source_files': len(inputs), 'categories': record['category_counts'],
            'books_with_navigation': sum(bool(b['combined_catalogue_ids']) for b in navigation),
            'additional_book_catalogue_pairs': sum(len(b['additional_catalogue_ids']) for b in navigation),
            'manuscript_readings_verified': False, 'source_priority_approved': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-private-inputs', action='store_true')
    args = parser.parse_args()
    record = json.loads((ROOT / RECORD).read_text())
    print(json.dumps(validate(record, verify_private=args.verify_private_inputs), indent=2))


if __name__ == '__main__':
    main()
