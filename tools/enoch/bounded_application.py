#!/usr/bin/env python3
"""Apply exact, independently reviewed Enoch units from a pinned package.

This is an editorial transaction, not an automatic translator or approval
algorithm. It rejects held/revised inputs, changed preimages and schema drift.
It never pushes Git, deploys a reader or publishes artwork.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.enoch.audit_editorial_issues import record_issues

APPLICATIONS = ROOT / 'sources/textual_restoration/applications'
TRANSLATION = ROOT / 'translation/extra_canonical/1_enoch'
PRIMARY_SHA = '505f248c667cebd5136991d7c570841a0a3ed9396d5b28b85bf07f4a3957053e'
LOADER = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def corpus_hashes(root: Path | None = None) -> dict[str, str]:
    root = TRANSLATION if root is None else root
    return {str(p.relative_to(root)): sha(p.read_bytes())
            for p in sorted(root.glob('[0-9][0-9][0-9]/[0-9][0-9][0-9].yaml'))}


def parse_ref(reference: str) -> tuple[int, int]:
    match = re.fullmatch(r'1 Enoch ([1-9][0-9]*):([1-9][0-9]*)', reference)
    if not match or not 1 <= int(match[1]) <= 108:
        raise ValueError(f'Invalid bounded reference: {reference}')
    return int(match[1]), int(match[2])


def artifact(package: Path, relative: str) -> Path:
    path = (package / relative).resolve()
    if not path.is_relative_to(package.resolve()) or path == package.resolve():
        raise ValueError('Artifact path escapes the application package')
    return path


def load_manifest(package: Path) -> dict:
    manifest = json.loads((package / 'manifest.json').read_text())
    refs = manifest.get('references', [])
    if manifest.get('kind') != 'enoch-reviewed-units-v1' or not refs or \
            len(refs) != len(set(refs)) or \
            manifest.get('primary_pdf_sha256') != PRIMARY_SHA or \
            manifest.get('full_book_verified') is not False or \
            manifest.get('graphic_publication_approved') is not False:
        raise ValueError('Application kind, scope or approval limit differs')
    numbers = [parse_ref(ref) for ref in refs]
    if numbers != sorted(numbers):
        raise ValueError('Bounded references must be sorted')
    for name, expected in manifest.get('files', {}).items():
        if sha(artifact(package, name).read_bytes()) != expected:
            raise ValueError(f'Pinned application artifact changed: {name}')
    if set(manifest.get('review_bindings', {})) != set(refs):
        raise ValueError('Review binding set differs from application scope')
    for ref in refs:
        c, v = parse_ref(ref)
        if f'{c:03d}-{v:03d}.candidate.yaml' not in manifest['files']:
            raise ValueError(f'Candidate is not hash-pinned: {ref}')
    return manifest


def review_row(package: Path, binding: dict, ref: str, pinned: dict) -> dict:
    for key in ('input', 'review', 'provenance'):
        if binding.get(key) not in pinned:
            raise ValueError(f'Unpinned {key} evidence for {ref}')
    inputs = json.loads(artifact(package, binding['input']).read_text())
    results = json.loads(artifact(package, binding['review']).read_text())
    if len({row['reference'] for row in inputs}) != len(inputs) or \
            len({row['reference'] for row in results['reviews']}) != len(results['reviews']):
        raise ValueError('Duplicate input/review references')
    selected = [row for row in inputs if row['reference'] == ref]
    verdicts = [row for row in results['reviews'] if row['reference'] == ref]
    if len(selected) != 1 or len(verdicts) != 1 or verdicts[0]['verdict'] != 'accept':
        raise ValueError(f'Exact submitted unit is not accepted: {ref}')
    provenance = json.loads(artifact(package, binding['provenance']).read_text())
    if provenance.get('input_sha256') != sha(artifact(package, binding['input']).read_bytes()) or \
            provenance.get('review_sha256') != sha(artifact(package, binding['review']).read_bytes()):
        raise ValueError(f'Review provenance does not bind exact artifacts: {ref}')
    if not provenance.get('reviewer_id'):
        raise ValueError('Reviewer identity is missing')
    if provenance.get('source_pdf_sha256') != PRIMARY_SHA or \
            not provenance.get('scan_image_sha256') or \
            any(not re.fullmatch('[0-9a-f]{64}', digest)
                for digest in provenance['scan_image_sha256'].values()):
        raise ValueError(f'Review lacks pinned primary scan evidence: {ref}')
    return selected[0]


def verify(package: Path, *, applied: bool = False,
           check_corpus: bool = False) -> dict:
    manifest = load_manifest(package)
    schema = jsonschema.Draft202012Validator(json.loads((ROOT / 'schema/verse.schema.json').read_text()))
    expected = dict(manifest['canonical_baseline_sha256'])
    candidates = {}
    for ref in manifest['references']:
        c, v = parse_ref(ref)
        relative = f'{c:03d}/{v:03d}.yaml'
        candidate_path = artifact(package, f'{c:03d}-{v:03d}.candidate.yaml')
        raw = candidate_path.read_bytes()
        candidate = yaml.load(raw, Loader=LOADER)
        schema.validate(candidate)
        if candidate['id'] != f'1EN.{c}.{v}' or candidate['reference'] != ref or \
                candidate.get('book') != '1 Enoch' or candidate.get('status') != 'draft' or \
                candidate['source'].get('confidence') != 'medium':
            raise ValueError(f'Candidate identity/lifecycle differs: {ref}')
        correction = candidate['source_correction']
        if correction.get('individual_unit_application_approved') is not True or \
                correction.get('full_book_verified') is not False or \
                correction.get('human_specialist_certification') is not False or \
                correction.get('manuscript_witness_certification') is not False or \
                correction.get('graphic_publication_approved') is not False:
            raise ValueError(f'Candidate approval scope differs: {ref}')
        findings = record_issues(candidate, c, v)
        # Real source poetry can repeat: repeated spans are review signals,
        # not a license to delete a source-supported refrain.
        errors = [f for f in findings if f['kind'] != 'repeated_english_span_review']
        if errors:
            raise ValueError(f'Candidate has mechanical errors: {ref}: {errors}')
        bindings = manifest['review_bindings'][ref]
        if len(bindings) < 2 or len({b['reviewer_id'] for b in bindings}) < 2:
            raise ValueError(f'Two distinct reviewers required: {ref}')
        roles = []
        for binding in bindings:
            row = review_row(package, binding, ref, manifest['files'])
            provenance = json.loads(artifact(package, binding['provenance']).read_text())
            if provenance['reviewer_id'] != binding['reviewer_id']:
                raise ValueError('Reviewer identity differs from pinned provenance')
            roles.append(provenance.get('role'))
            if any(candidate['source'].get(key) != row['source'].get(key)
                   for key in ('edition', 'language', 'text', 'pages')) or \
                    candidate['translation'] != row['translation']:
                raise ValueError(f'Candidate differs from accepted source/English/notes: {ref}')
        if 'independent_reviewer' not in roles:
            raise ValueError(f'Independent source assessment required: {ref}')
        witnesses = candidate.get('enoch_witnesses', {}).get('available_witnesses', [])
        if len(witnesses) != 1 or witnesses[0]['witness'] != 'charles_1906' or \
                witnesses[0]['text'] != candidate['source']['text']:
            raise ValueError(f'Selected-edition witness/source mismatch: {ref}')
        baseline = manifest['canonical_baseline_sha256'].get(relative)
        if correction['baseline_sha256'] != baseline:
            raise ValueError(f'Preimage hash differs: {ref}')
        if baseline is not None:
            blob = manifest['baseline_git_blobs'][relative]
            preimage = subprocess.run(['git', 'cat-file', 'blob', blob['blob']], cwd=ROOT,
                                      check=True, capture_output=True).stdout
            if sha(preimage) != baseline:
                raise ValueError(f'Historical Git preimage changed: {ref}')
        target = TRANSLATION / relative
        if applied:
            if not target.exists() or target.read_bytes() != raw:
                raise ValueError(f'Applied candidate differs: {ref}')
            expected[relative] = sha(raw)
        elif (target.exists() and sha(target.read_bytes()) != baseline) or \
                (not target.exists() and baseline is not None):
            raise ValueError(f'Canonical preimage changed: {ref}')
        candidates[relative] = raw
    if check_corpus and corpus_hashes() != expected:
        raise ValueError('Canonical changes exceed the exact bounded scope')
    return {'references': manifest['references'], 'candidate_files': len(candidates),
            'snapshot_file_count': len(expected), 'full_book_verified': False,
            'graphic_publication_approved': False}


def apply(package: Path) -> dict:
    verify(package, check_corpus=True)
    pdf = ROOT / 'sources/enoch/scans/charles_1906_ethiopic.pdf'
    if not pdf.exists() or sha(pdf.read_bytes()) != PRIMARY_SHA:
        raise ValueError('Rehydrate and verify actual primary PDF before applying')
    originals = {}
    receipt_path = package / 'application.json'
    old_receipt = receipt_path.read_bytes() if receipt_path.exists() else None
    try:
        manifest = load_manifest(package)
        for ref in manifest['references']:
            c, v = parse_ref(ref)
            target = TRANSLATION / f'{c:03d}/{v:03d}.yaml'
            originals[target] = target.read_bytes() if target.exists() else None
            temporary = target.with_suffix('.yaml.enoch-pending')
            temporary.write_bytes(artifact(package, f'{c:03d}-{v:03d}.candidate.yaml').read_bytes())
            os.replace(temporary, target)
        receipt = {'status': 'applied_verified',
                   **verify(package, applied=True, check_corpus=True),
                   'canonical_after_sha256': corpus_hashes(),
                   'unrelated_canonical_files_unchanged_at_application': True,
                   'manifest_sha256': sha((package / 'manifest.json').read_bytes()),
                   'canonical_changed': True, 'deployed_by_transaction': False}
        pending_receipt = package / 'application.json.pending'
        pending_receipt.write_text(json.dumps(receipt, indent=2) + '\n')
        os.replace(pending_receipt, receipt_path)
        return receipt
    except Exception:
        for target, raw in originals.items():
            target.with_suffix('.yaml.enoch-pending').unlink(missing_ok=True)
            if raw is None:
                target.unlink(missing_ok=True)
            else:
                target.write_bytes(raw)
        (package / 'application.json.pending').unlink(missing_ok=True)
        if old_receipt is None:
            receipt_path.unlink(missing_ok=True)
        else:
            receipt_path.write_bytes(old_receipt)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['verify', 'apply', 'verify-applied'])
    parser.add_argument('--package', required=True)
    args = parser.parse_args()
    package = (APPLICATIONS / args.package).resolve()
    if package.parent != APPLICATIONS.resolve() or not package.name.startswith('enoch_'):
        parser.error('Package must be a direct enoch_* application directory')
    result = apply(package) if args.operation == 'apply' else verify(package, applied=args.operation == 'verify-applied')
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
