#!/usr/bin/env python3
"""Bounded, hash-checked POB correction for 1 Enoch 12:1-6.

``verify`` is read-only. ``apply`` writes only these three verse YAMLs after
source, independent-review, footnote, and local export checks; it never pushes
or deploys. ``verify-applied`` checks exact installed candidate bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools import export_mobile_bible as exporter
from tools.enoch import verse_parser

PACKAGE = ROOT / 'sources/textual_restoration/applications/enoch_12_20260930'
TRANSLATION = ROOT / 'translation/extra_canonical/1_enoch'
REFS = tuple((12, verse) for verse in range(1, 7))
SCAN_SHA = '505f248c667cebd5136991d7c570841a0a3ed9396d5b28b85bf07f4a3957053e'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_for(chapter: int, verse: int) -> Path:
    return TRANSLATION / f'{chapter:03d}' / f'{verse:03d}.yaml'


def package_name(chapter: int, verse: int) -> str:
    return f'{chapter:03d}-{verse:03d}'


def verify_structure() -> dict:
    manifest = json.loads((PACKAGE / 'manifest.json').read_text())
    review_bytes = (PACKAGE / 'final-source-review.json').read_bytes()
    review = json.loads(review_bytes)
    if manifest.get('status') != 'reviewed_candidates_ready_for_bounded_application' or \
            manifest.get('primary_scan_sha256') != SCAN_SHA or \
            manifest.get('final_source_review_sha256') != digest(review_bytes):
        raise ValueError('Review or source manifest drift')
    if set(review.get('reviews', {})) != {package_name(*ref) for ref in REFS}:
        raise ValueError('Review set differs from bounded references')
    expected_files = {f'{package_name(*ref)}.candidate.yaml' for ref in REFS} | {
        '012-001.baseline.yaml'}
    if set(manifest.get('files', {})) != expected_files:
        raise ValueError('Candidate/baseline set differs from bounded references')
    for name, expected in manifest['files'].items():
        if digest((PACKAGE / name).read_bytes()) != expected:
            raise ValueError(f'Package file changed: {name}')
    candidates = {}
    for chapter, verse in REFS:
        name = package_name(chapter, verse)
        candidate = yaml.safe_load((PACKAGE / f'{name}.candidate.yaml').read_text())
        source, _warnings = verse_parser.load_verse(chapter, verse)
        if not source or candidate.get('id') != f'1EN.{chapter}.{verse}' or \
                candidate.get('reference') != f'1 Enoch {chapter}:{verse}' or \
                candidate['source']['text'] != source.text:
            raise ValueError(f'Source or reference differs: {name}')
        if candidate.get('status') != 'revised' or \
                candidate.get('cross_check', {}).get('status') != 'high_agreement' or \
                candidate.get('source_correction', {}).get('publication_approval') is not True or \
                review['reviews'][name]['verdict'] != 'accept':
            raise ValueError(f'Editorial review is not accepted: {name}')
        text = candidate['translation']['text']
        markers = re.findall(r'\[([a-z])\]', text)
        notes = candidate['translation'].get('footnotes', [])
        if not text or len(set(markers)) != len(markers) or \
                set(markers) != {n.get('marker') for n in notes} or \
                any(not n.get('text') for n in notes):
            raise ValueError(f'Footnote anchors differ: {name}')
        original = file_for(chapter, verse)
        if chapter == 12 and verse >= 2:
            if original.exists():
                raise ValueError(f'{chapter}:{verse} already exists; use explicit correction instead')
        else:
            baseline = (PACKAGE / f'{name}.baseline.yaml').read_bytes()
            if not original.exists() or original.read_bytes() != baseline or \
                    candidate['source_correction']['baseline_sha256'] != digest(baseline):
                raise ValueError(f'Canonical baseline changed: {name}')
            old = yaml.safe_load(baseline)
            history = candidate.get('review_history', [])
            for field in ('status', 'revision_pass', 'cross_check'):
                if field not in old:
                    continue
                if not any(row.get('field') == field and row.get('value') == old[field]
                           and row.get('certifies_this_candidate') is False for row in history):
                    raise ValueError(f'Old {field} approval not archived: {name}')
        candidates[name] = candidate
    return candidates


def verify_export_delta() -> dict:
    before = exporter.export_extra_canonical_book('ENO')
    if not before:
        raise ValueError('1 Enoch exporter returned no baseline')
    with tempfile.TemporaryDirectory(prefix='enoch-twelve-export-') as temp:
        temp_root = Path(temp)
        shutil.copytree(TRANSLATION, temp_root / '1_enoch')
        for chapter, verse in REFS:
            name = package_name(chapter, verse)
            destination = temp_root / '1_enoch' / f'{chapter:03d}' / f'{verse:03d}.yaml'
            shutil.copyfile(PACKAGE / f'{name}.candidate.yaml', destination)
        with patch.object(exporter, 'EXTRA_CANONICAL_ROOT', temp_root):
            after = exporter.export_extra_canonical_book('ENO')
    if not after:
        raise ValueError('Candidate 1 Enoch exporter returned no book')
    a = {row['chapter']: row['verses'] for row in before['chapters']}
    b = {row['chapter']: row['verses'] for row in after['chapters']}
    changed = sorted(chapter for chapter in set(a) | set(b) if a.get(chapter) != b.get(chapter))
    if changed != [12] or 12 in a or [row['verse'] for row in b[12]] != list(range(1, 7)):
        raise ValueError(f'Unexpected chapter 12 export delta: {changed}')
    return {'changed_chapters': changed, 'chapter_12_verses': len(b[12]),
            'baseline_export_chapters': len(a), 'candidate_export_chapters': len(b)}


def verify_applied() -> dict:
    manifest = json.loads((PACKAGE / 'manifest.json').read_text())
    for chapter, verse in REFS:
        name = package_name(chapter, verse)
        if not file_for(chapter, verse).is_file() or \
                digest(file_for(chapter, verse).read_bytes()) != manifest['files'][f'{name}.candidate.yaml']:
            raise ValueError(f'Applied source differs: {name}')
    receipt = json.loads((PACKAGE / 'application.json').read_text())
    if receipt.get('status') != 'applied_verified' or receipt.get('refs') != [f'{c}:{v}' for c, v in REFS]:
        raise ValueError('Application receipt differs')
    return receipt


def apply() -> dict:
    verify_structure()
    delta = verify_export_delta()
    originals = {file_for(c, v): file_for(c, v).read_bytes() if file_for(c, v).exists() else None
                 for c, v in REFS}
    try:
        for chapter, verse in REFS:
            name = package_name(chapter, verse)
            target = file_for(chapter, verse)
            payload = (PACKAGE / f'{name}.candidate.yaml').read_bytes()
            temporary = target.with_suffix('.yaml.enoch-pending')
            temporary.write_bytes(payload)
            os.replace(temporary, target)
    except Exception:
        for target, original in originals.items():
            if original is None:
                target.unlink(missing_ok=True)
            else:
                target.write_bytes(original)
        raise
    receipt = {'status': 'applied_verified', 'refs': [f'{c}:{v}' for c, v in REFS],
               'export_delta': delta, 'manifest_sha256': digest((PACKAGE / 'manifest.json').read_bytes()),
               'candidate_sha256': {package_name(c, v): digest(file_for(c, v).read_bytes()) for c, v in REFS}}
    (PACKAGE / 'application.json').write_text(json.dumps(receipt, indent=2) + '\n')
    verify_applied()
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('verify', 'apply', 'verify-applied'))
    args = parser.parse_args()
    if args.action == 'verify-applied':
        result = verify_applied()
    elif args.action == 'apply':
        result = apply()
    else:
        verify_structure()
        result = verify_export_delta()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
