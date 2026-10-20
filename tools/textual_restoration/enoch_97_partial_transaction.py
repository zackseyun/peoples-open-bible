#!/usr/bin/env python3
"""Hash-guarded individual 1 Enoch 97:1,3,5,8 source repair.

The complete chapter remains held. ``verify`` is read-only, ``apply`` changes
only four canonical verse files, and ``verify-applied`` checks their exact bytes.
No command in this script deploys or publishes Graphic Reader content.
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
from tools.enoch import audit_pob_source_coverage as source_coverage

PACKAGE = ROOT / 'sources/textual_restoration/applications/enoch_97_1_3_5_8_20261019'
REVIEW = ROOT / 'sources/textual_restoration/applications/enoch_97_review_20261019/individual_1_3_5_8'
TRANSLATION = ROOT / 'translation/extra_canonical/1_enoch'
VERSES = (1, 3, 5, 8)
PRIMARY_PDF = ROOT / 'sources/enoch/scans/charles_1906_ethiopic.pdf'
PRIMARY_SHA = '505f248c667cebd5136991d7c570841a0a3ed9396d5b28b85bf07f4a3957053e'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verse_file(verse: int) -> Path:
    return TRANSLATION / '097' / f'{verse:03d}.yaml'


def name(verse: int) -> str:
    return f'097-{verse:03d}'


def verify(*, applied: bool = False, require_primary_pdf: bool = True) -> dict:
    manifest = json.loads((PACKAGE / 'manifest.json').read_text())
    refs = [f'1 Enoch 97:{n}' for n in VERSES]
    expected_files = {f'{name(n)}.{kind}.yaml' for n in VERSES
                      for kind in ('baseline', 'candidate')}
    if manifest.get('status') != 'reviewed_individual_candidates_ready_for_bounded_application' or \
            manifest.get('references') != refs or \
            manifest.get('chapter_publication_approval') is not False or \
            manifest.get('canonical_changed') is not False or \
            set(manifest.get('files', {})) != expected_files:
        raise ValueError('Application scope or manifest differs')
    if manifest['source_pdf_sha256'] != PRIMARY_SHA:
        raise ValueError('Primary source identity changed')
    if PRIMARY_PDF.exists() and sha(PRIMARY_PDF.read_bytes()) != PRIMARY_SHA:
        raise ValueError('Primary PDF changed')
    if not PRIMARY_PDF.exists() and require_primary_pdf:
        raise ValueError('Rehydrate the pinned primary PDF before applying or reviewing a new transaction')
    for filename, digest in manifest['files'].items():
        if sha((PACKAGE / filename).read_bytes()) != digest:
            raise ValueError(f'Application package changed: {filename}')

    accepted_bytes = (REVIEW / 'review/review.json').read_bytes()
    accepted = json.loads(accepted_bytes)
    provenance = json.loads((REVIEW / 'review/provenance.json').read_text())
    inputs = json.loads((REVIEW / 'review-input.json').read_text())
    if sha(accepted_bytes) != manifest['accepted_review_sha256'] or \
            provenance['review_sha256'] != manifest['accepted_review_sha256'] or \
            [r['reference'] for r in inputs] != refs or \
            [r['reference'] for r in accepted['reviews']] != refs or \
            any(r['verdict'] != 'accept' for r in accepted['reviews']) or \
            accepted['chapter_complete'] is not False:
        raise ValueError('Individual review is not exactly accepted')
    for filename, digest in provenance['package_input_sha256'].items():
        if sha((REVIEW / filename).read_bytes()) != digest:
            raise ValueError(f'Review input changed: {filename}')
    for index in (1, 2):
        diagnostic = ROOT / f'sources/textual_restoration/applications/enoch_97_review_20261019/pass{index}/review.json'
        if sha(diagnostic.read_bytes()) != manifest['diagnostic_review_sha256'][index - 1]:
            raise ValueError('Diagnostic review changed')

    candidates = {}
    for verse, row in zip(VERSES, inputs):
        key = name(verse)
        baseline = (PACKAGE / f'{key}.baseline.yaml').read_bytes()
        candidate_bytes = (PACKAGE / f'{key}.candidate.yaml').read_bytes()
        candidate = yaml.safe_load(candidate_bytes)
        target = verse_file(verse)
        if not target.exists() or target.read_bytes() != (candidate_bytes if applied else baseline) or \
                candidate.get('id') != f'1EN.97.{verse}' or \
                candidate.get('reference') != row['reference'] or \
                candidate.get('book') != '1 Enoch' or \
                candidate.get('status') != 'revised' or \
                candidate['source']['text'] != row['source']['text'] or \
                candidate['source']['pages'] != row['source']['pages'] or \
                candidate['translation'] != row['translation'] or \
                candidate['source_correction']['baseline_sha256'] != sha(baseline) or \
                candidate['source_correction']['individual_unit_application_approved'] is not True or \
                candidate['source_correction']['chapter_publication_approval'] is not False or \
                candidate['source_correction']['human_specialist_certification'] is not False or \
                candidate['source_correction']['manuscript_witness_certification'] is not False or \
                candidate['cross_check']['accepted_review_sha256'] != manifest['accepted_review_sha256']:
            raise ValueError(f'Canonical preimage or candidate differs: {key}')
        if candidate['enoch_witnesses']['available_witnesses'][0]['text'] != candidate['source']['text']:
            raise ValueError(f'Witness/source text differs: {key}')
        if candidate.get('review_history') != [{'baseline_file': f'{key}.baseline.yaml',
                'baseline_sha256': sha(baseline), 'certifies_this_candidate': False}]:
            raise ValueError(f'Historical baseline reference differs: {key}')
        markers = re.findall(r'\[([a-z])\]', candidate['translation']['text'])
        notes = candidate['translation'].get('footnotes', [])
        if not candidate['translation']['text'] or len(set(markers)) != len(markers) or \
                set(markers) != {n['marker'] for n in notes} or \
                any(not n['text'] for n in notes):
            raise ValueError(f'Footnote anchor differs: {key}')
        candidates[verse] = candidate_bytes
    return {'references': refs, 'accepted_review_sha256': manifest['accepted_review_sha256'],
            'candidate_sha256': {name(n): sha(candidates[n]) for n in VERSES},
            'primary_pdf_checked': PRIMARY_PDF.exists()}


def verify_export_delta() -> dict:
    before = exporter.export_extra_canonical_book('ENO')
    if not before:
        raise ValueError('Baseline 1 Enoch export unavailable')
    with tempfile.TemporaryDirectory(prefix='enoch97-export-') as temp:
        temp_root = Path(temp)
        shutil.copytree(TRANSLATION, temp_root / '1_enoch')
        for verse in VERSES:
            shutil.copyfile(PACKAGE / f'{name(verse)}.candidate.yaml',
                            temp_root / '1_enoch/097' / f'{verse:03d}.yaml')
        with patch.object(exporter, 'EXTRA_CANONICAL_ROOT', temp_root):
            after = exporter.export_extra_canonical_book('ENO')
        source_row = source_coverage.audit([97], temp_root / '1_enoch')['chapters'][0]
    if not after:
        raise ValueError('Candidate 1 Enoch export unavailable')
    old = {chapter['chapter']: chapter['verses'] for chapter in before['chapters']}
    new = {chapter['chapter']: chapter['verses'] for chapter in after['chapters']}
    changed = [chapter for chapter in sorted(set(old) | set(new)) if old.get(chapter) != new.get(chapter)]
    # The exporter correctly omits an incomplete chapter 97. Repairing four
    # individual units must not cause premature mobile-reader publication.
    if changed or 97 in old or 97 in new:
        raise ValueError(f'Incomplete chapter 97 unexpectedly exported: {changed}')
    if source_row['missing_verse_numbers'] != [10] or source_row['inventory_complete']:
        raise ValueError('Source completeness gate changed unexpectedly')
    return {'changed_export_chapters': [], 'individual_source_verses_repaired': list(VERSES),
            'chapter97_still_excluded_from_mobile_export': True,
            'source_missing_verses': [10]}


def verify_applied() -> dict:
    # Installed artifact/receipt verification works in a clean CI checkout,
    # where ignored source binaries are not rehydrated. New applications still
    # require the actual PDF; a present but corrupt PDF is never ignored.
    verified = verify(applied=True, require_primary_pdf=False)
    manifest = json.loads((PACKAGE / 'manifest.json').read_text())
    for verse in VERSES:
        if sha(verse_file(verse).read_bytes()) != manifest['files'][f'{name(verse)}.candidate.yaml']:
            raise ValueError(f'Applied verse differs: {verse}')
    receipt = json.loads((PACKAGE / 'application.json').read_text())
    if receipt['status'] != 'applied_verified' or receipt['verses'] != list(VERSES) or \
            receipt.get('manifest_sha256') != sha((PACKAGE / 'manifest.json').read_bytes()) or \
            receipt.get('review_sha256') != verified['accepted_review_sha256'] or \
            receipt.get('installed_sha256') != verified['candidate_sha256'] or \
            receipt.get('chapter97_publication_approved') is not False:
        raise ValueError('Application receipt differs')
    return {**receipt, 'primary_pdf_checked': verified['primary_pdf_checked']}


def apply() -> dict:
    verified = verify()
    delta = verify_export_delta()
    originals = {verse_file(n): verse_file(n).read_bytes() for n in VERSES}
    try:
        for verse in VERSES:
            target = verse_file(verse)
            pending = target.with_suffix('.yaml.enoch-pending')
            pending.write_bytes((PACKAGE / f'{name(verse)}.candidate.yaml').read_bytes())
            os.replace(pending, target)
    except Exception:
        for target, data in originals.items():
            target.write_bytes(data)
        raise
    receipt = {'status': 'applied_verified', 'verses': list(VERSES),
               'review_sha256': verified['accepted_review_sha256'],
               'export_delta': delta,
               'manifest_sha256': sha((PACKAGE / 'manifest.json').read_bytes()),
               'installed_sha256': {name(n): sha(verse_file(n).read_bytes()) for n in VERSES},
               'chapter97_publication_approved': False}
    (PACKAGE / 'application.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return verify_applied()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('verify', 'apply', 'verify-applied'))
    args = parser.parse_args()
    if args.action == 'verify-applied':
        result = verify_applied()
    elif args.action == 'apply':
        result = apply()
    else:
        result = {**verify(), 'export_delta': verify_export_delta()}
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
