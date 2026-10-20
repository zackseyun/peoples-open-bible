#!/usr/bin/env python3
"""Bounded hash-checked Enoch repairs; no artwork or deployment commands.

Only manifest-listed exact candidates with accepted input-bound reviews may
be installed. Entire-chapter or independent-manuscript approval is not granted.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
from pathlib import Path
import sys

import yaml
import jsonschema

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.enoch.audit_editorial_issues import record_issues

PACKAGE = ROOT / 'sources/textual_restoration/applications/enoch_source_repairs_20261020'
TRANSLATION = ROOT / 'translation/extra_canonical/1_enoch'
PRIMARY_SHA = '505f248c667cebd5136991d7c570841a0a3ed9396d5b28b85bf07f4a3957053e'
REFS = [(18, n) for n in (1, 2, 3, 4, 6, 7, 8, 10, 11, 14, 15)] + [(28, 1), (63, 7), (81, 4), (89, 26)]
NOTE_REASON_MAPPING = {'source_control': 'textual_variant',
                       'editorial_bracketing': 'textual_variant',
                       'previous_rendering': 'alternative_reading'}


def schema_translation(translation: dict) -> dict:
    """Normalize category names only; never change reviewed prose or anchors."""
    result = copy.deepcopy(translation)
    result.setdefault('philosophy', 'optimal-equivalence')
    for note in result.get('footnotes', []):
        note['reason'] = NOTE_REASON_MAPPING.get(note.get('reason'), note.get('reason'))
    return result


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical_hashes() -> dict:
    return {str(p.relative_to(TRANSLATION)): sha(p.read_bytes())
            for p in sorted(TRANSLATION.glob('[0-9][0-9][0-9]/[0-9][0-9][0-9].yaml'))}


def load_manifest() -> dict:
    manifest = json.loads((PACKAGE / 'manifest.json').read_text())
    expected = [f'1 Enoch {c}:{v}' for c, v in REFS]
    if manifest['references'] != expected or manifest['primary_pdf_sha256'] != PRIMARY_SHA or \
            manifest['chapter_publication_approval'] is not False:
        raise ValueError('Application scope changed')
    for name, digest in manifest['files'].items():
        if sha((PACKAGE / name).read_bytes()) != digest:
            raise ValueError(f'Package artifact changed: {name}')
    return manifest


def verify(applied: bool = False, check_corpus: bool = False, *, evidence_only: bool = False) -> dict:
    if evidence_only and (applied or check_corpus):
        raise ValueError('Historical evidence validation cannot claim installed targets')
    manifest = load_manifest()
    schema = json.loads((ROOT / 'schema/verse.schema.json').read_text())
    expected_corpus = dict(manifest['canonical_baseline_sha256'])
    bindings = manifest['review_bindings']
    for chapter, verse in REFS:
        ref = f'1 Enoch {chapter}:{verse}'
        key = f'{chapter:03d}-{verse:03d}'
        path = TRANSLATION / f'{chapter:03d}/{verse:03d}.yaml'
        rel = str(path.relative_to(TRANSLATION))
        raw = (PACKAGE / f'{key}.candidate.yaml').read_bytes()
        candidate = yaml.safe_load(raw)
        jsonschema.validate(candidate, schema)
        if candidate['reference'] != ref or candidate['id'] != f'1EN.{chapter}.{verse}' or \
                candidate['status'] != 'draft' or \
                candidate['source_correction']['chapter_publication_approval'] is not False or \
                candidate['source_correction']['human_specialist_certification'] is not False:
            raise ValueError(f'Candidate scope changed: {ref}')
        if record_issues(candidate, chapter, verse):
            raise ValueError(f'Candidate contains mechanical issues: {ref}')
        # At least an initial author review and an independent scan review;
        # this guards input identity, not majority voting over difficult text.
        if len(bindings[ref]) != 2:
            raise ValueError(f'Two input-bound review records required: {ref}')
        for binding in bindings[ref]:
            inputs = json.loads((PACKAGE / binding['input']).read_text())
            reviewed = next(r for r in inputs if r['reference'] == ref)
            result = json.loads((PACKAGE / binding['review']).read_text())
            verdict = next(r for r in result['reviews'] if r['reference'] == ref)
            if verdict['verdict'] != 'accept' or \
                    candidate['source']['text'] != reviewed['source']['text'] or \
                    candidate['source']['pages'] != reviewed['source']['pages'] or \
                    candidate['translation'] != schema_translation(reviewed['translation']):
                raise ValueError(f'Candidate differs from accepted review input: {ref}')
        baseline = manifest['canonical_baseline_sha256'].get(rel)
        if candidate['source_correction']['baseline_sha256'] != baseline:
            raise ValueError(f'Candidate baseline differs: {ref}')
        if baseline is not None:
            archived = PACKAGE / f'{key}.baseline.yaml'
            if archived.exists():
                preimage = archived.read_bytes()
            else:
                # The inherited 28:1 contains oracle-derived wording. Bind its
                # existing Git blob without vendoring that text again.
                blob = manifest.get('baseline_git_blobs', {}).get(rel)
                if not blob:
                    raise ValueError(f'Archived baseline absent: {ref}')
                preimage = subprocess.run(['git', 'cat-file', 'blob', blob['blob']],
                                          cwd=ROOT, check=True, capture_output=True).stdout
            if sha(preimage) != baseline:
                raise ValueError(f'Archived baseline differs: {ref}')
        if evidence_only:
            continue  # Historical artifact validation, explicitly not current proof.
        if applied:
            if not path.exists() or path.read_bytes() != raw:
                raise ValueError(f'Applied candidate differs: {ref}')
            expected_corpus[rel] = sha(raw)
        elif (path.exists() and sha(path.read_bytes()) != baseline) or \
                (not path.exists() and baseline is not None):
            raise ValueError(f'Canonical preimage changed: {ref}')
    if check_corpus and canonical_hashes() != expected_corpus:
        raise ValueError('Canonical corpus changed beyond the exact bounded application')
    return {'references': manifest['references'], 'canonical_files': len(expected_corpus),
            'canonical_targets_checked': not evidence_only,
            'chapter_publication_approval': False, 'human_specialist_certification': False}


def apply() -> dict:
    verify(check_corpus=True)
    pdf = ROOT / 'sources/enoch/scans/charles_1906_ethiopic.pdf'
    if not pdf.exists() or sha(pdf.read_bytes()) != PRIMARY_SHA:
        raise ValueError('Rehydrate and verify the actual primary PDF before application')
    originals = {}
    try:
        for chapter, verse in REFS:
            path = TRANSLATION / f'{chapter:03d}/{verse:03d}.yaml'
            originals[path] = path.read_bytes() if path.exists() else None
            raw = (PACKAGE / f'{chapter:03d}-{verse:03d}.candidate.yaml').read_bytes()
            temporary = path.with_suffix('.yaml.enoch-pending')
            temporary.write_bytes(raw)
            os.replace(temporary, path)
        receipt = {'status': 'applied_verified', **verify(applied=True, check_corpus=True),
                   'unrelated_canonical_files_unchanged_at_application': True,
                   'canonical_after_sha256': canonical_hashes(),
                   'canonical_changed': True, 'full_book_verified': False,
                   'graphic_art_published': False, 'app_deployed_by_transaction': False}
        (PACKAGE / 'application.json').write_text(json.dumps(receipt, indent=2) + '\n')
        return receipt
    except Exception:
        for path, raw in originals.items():
            path.with_suffix('.yaml.enoch-pending').unlink(missing_ok=True)
            if raw is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(raw)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['verify', 'apply', 'verify-applied'])
    args = parser.parse_args()
    result = apply() if args.operation == 'apply' else verify(args.operation == 'verify-applied')
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
