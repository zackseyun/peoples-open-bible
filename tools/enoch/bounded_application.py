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
    certificates = {}
    for certificate in manifest.get('chapter_inventories', []):
        c = certificate['chapter']
        units = certificate['units']
        chapter_refs = [v for chapter,v in numbers if chapter == c]
        if certificate.get('independent_count_confirmation') is not True:
            raise ValueError('Complete chapter certificate is not independently bound')
        if c in certificates or not units or units != list(range(1,len(units)+1)) or \
                chapter_refs != units or \
                certificate.get('artifact') not in manifest['files']:
            raise ValueError('Complete chapter certificate differs from exact candidate scope')
        inventory = json.loads(artifact(package,certificate['artifact']).read_text())
        rows = [row for row in inventory['chapters'] if row['chapter'] == c]
        if inventory.get('primary_pdf_sha256') != PRIMARY_SHA or len(rows) != 1 or \
                rows[0]['units'] != units:
            raise ValueError('Complete chapter certificate differs from pinned inventory')
        certificates[c] = units
    # These counts bind individual source ingress only. They deliberately do
    # not confer full chapter wording approval or alter reader/export counts.
    source_counts = set()
    for certificate in manifest.get('source_only_count_inventories', []):
        c, units = certificate['chapter'], certificate['units']
        if c in source_counts or c in certificates or not units or \
                units != list(range(1, len(units)+1)) or \
                certificate.get('independent_count_confirmation') is not True or \
                certificate.get('artifact') not in manifest['files']:
            raise ValueError('Source-only count certificate scope differs')
        inventory = json.loads(artifact(package, certificate['artifact']).read_text())
        matches = [r for r in inventory['chapters'] if r['chapter'] == c]
        if inventory.get('kind') != 'enoch-source-ingress-counts-v1' or \
                inventory.get('primary_pdf_sha256') != PRIMARY_SHA or \
                inventory.get('wording_approval') is not False or \
                inventory.get('reader_release_policy_changed') is not False or \
                len(matches) != 1 or matches[0]['units'] != units:
            raise ValueError('Source-only count artifact or release limit differs')
        chapter_refs = [ref for ref in refs if parse_ref(ref)[0] == c]
        if not chapter_refs:
            raise ValueError('Source-only count has no exact approved individual unit')
        # Each already-pinned author/reader input and explicit decision list
        # must actually represent the entire numbered structural scope. Held
        # decisions stay held and are never passed to reviewed_rows as accepts.
        bindings = manifest['review_bindings'][chapter_refs[0]]
        reviewed_rows(package, bindings, chapter_refs[0], manifest['files'])
        for binding in bindings:
            inputs = json.loads(artifact(package, binding['input']).read_text())
            decisions = review_entries(json.loads(artifact(package, binding['review']).read_text()))
            for rows in (inputs, decisions):
                observed = sorted(parse_ref(r['reference'])[1] for r in rows
                                  if parse_ref(r['reference'])[0] == c)
                if observed != units:
                    raise ValueError('Source-only count differs from full paired submitted scope')
        source_counts.add(c)
    retired = [row['reference'] for row in manifest.get('retirements', [])]
    if len(retired) != len(set(retired)) or set(retired) & set(refs) or \
            [parse_ref(ref) for ref in retired] != sorted(parse_ref(ref) for ref in retired):
        raise ValueError('Retired references overlap candidates, duplicate or are unsorted')
    for row in manifest.get('retirements', []):
        c,v = parse_ref(row['reference'])
        baseline = manifest['canonical_baseline_sha256'].get(f'{c:03d}/{v:03d}.yaml')
        replacements = row.get('replacement_references', [])
        if row.get('action') != 'retire_misaddressed_record' or not row.get('reason') or \
                not baseline or row.get('baseline_sha256') != baseline or \
                not replacements or len(replacements) != len(set(replacements)) or \
                not set(replacements) <= set(refs):
            raise ValueError('Retirement lacks an exact preimage, reason or reviewed replacement')
        replacement_chapters = {parse_ref(ref)[0] for ref in replacements}
        if c not in certificates or not replacement_chapters <= set(certificates) or \
                v in certificates[c]:
            raise ValueError('Retirement requires complete corrected-address and replacement chapters; valid selected addresses cannot be deleted')
    for ref, prior in manifest.get('supersedes', {}).items():
        if ref not in refs:
            raise ValueError('Supersession must name a candidate in this exact scope')
        c,v = parse_ref(ref)
        old_package = artifact(APPLICATIONS, prior['package'])
        if old_package.parent != APPLICATIONS.resolve() or old_package == package.resolve():
            raise ValueError('Supersession package is not a distinct direct application')
        old_manifest = old_package/'manifest.json'
        old_candidate = old_package/f'{c:03d}-{v:03d}.candidate.yaml'
        old_hash = sha(old_candidate.read_bytes())
        if sha(old_manifest.read_bytes()) != prior['manifest_sha256'] or \
                old_hash != prior['candidate_sha256'] or \
                manifest['canonical_baseline_sha256'].get(f'{c:03d}/{v:03d}.yaml') != old_hash:
            raise ValueError('Supersession does not bind the historical manifest/candidate/preimage')
    for ref in manifest.get('supersedes_legacy_individuals',{}):
        from tools.enoch.legacy_individual_evidence import validate_declared_successor
        validate_declared_successor(package,manifest,ref)
    if 'supersedes_legacy97' in manifest:
        from tools.enoch.legacy97_evidence import validate_declared_successor
        validate_declared_successor(package, manifest)
    if 'supersedes_legacy_editorial' in manifest:
        from tools.enoch.legacy_editorial_evidence import validate_declared_successors
        validate_declared_successors(package,manifest)
    if 'supersedes_legacy21' in manifest:
        from tools.enoch.legacy21_evidence import validate_declared_successor
        validate_declared_successor(package, manifest)
    if 'supersedes_legacy32' in manifest:
        from tools.enoch.legacy32_evidence import validate_declared_successor
        validate_declared_successor(package, manifest)
    return manifest


def review_entries(result: dict) -> list[dict]:
    """Read either retained receipt serializer without rewriting signed bytes.

    The 48–49 reader emitted ``results``; other readers emitted ``reviews``.
    Both contain explicit reference/verdict rows. Ambiguous dual containers,
    absent decisions and duplicates fail closed, never infer acceptance.
    """
    keys = [key for key in ('reviews', 'results') if key in result]
    if len(keys) != 1 or not isinstance(result[keys[0]], list):
        raise ValueError('Review receipt must contain one explicit decision list')
    rows = result[keys[0]]
    if any(not isinstance(row, dict) or not row.get('reference') or
           row.get('verdict') not in ('accept', 'hold', 'revise', 'reject') for row in rows) or \
            len({row['reference'] for row in rows}) != len(rows):
        raise ValueError('Review receipt has invalid or duplicate explicit decisions')
    return rows


def review_row(package: Path, binding: dict, ref: str, pinned: dict) -> dict:
    for key in ('input', 'review', 'provenance'):
        if binding.get(key) not in pinned:
            raise ValueError(f'Unpinned {key} evidence for {ref}')
    inputs = json.loads(artifact(package, binding['input']).read_text())
    results = json.loads(artifact(package, binding['review']).read_text())
    decisions = review_entries(results)
    if len({row['reference'] for row in inputs}) != len(inputs):
        raise ValueError('Duplicate input/review references')
    selected = [row for row in inputs if row['reference'] == ref]
    verdicts = [row for row in decisions if row['reference'] == ref]
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


def reviewed_rows(package: Path, bindings: list[dict], ref: str,
                  pinned: dict) -> list[dict]:
    if len(bindings) < 2 or len({b['reviewer_id'] for b in bindings}) < 2:
        raise ValueError(f'Two distinct reviewers required: {ref}')
    rows, roles = [], []
    for binding in bindings:
        rows.append(review_row(package, binding, ref, pinned))
        provenance = json.loads(artifact(package, binding['provenance']).read_text())
        if provenance['reviewer_id'] != binding['reviewer_id']:
            raise ValueError('Reviewer identity differs from pinned provenance')
        roles.append(provenance.get('role'))
    if 'independent_reviewer' not in roles:
        raise ValueError(f'Independent source assessment required: {ref}')
    return rows


def verify_git_preimage(manifest: dict, relative: str, expected: str) -> None:
    blob = manifest['baseline_git_blobs'][relative]
    preimage = subprocess.run(['git', 'cat-file', 'blob', blob['blob']], cwd=ROOT,
                              check=True, capture_output=True).stdout
    if sha(preimage) != expected:
        raise ValueError(f'Historical Git preimage changed: {relative}')


def verify(package: Path, *, applied: bool = False,
           check_corpus: bool = False, evidence_only: bool = False) -> dict:
    if evidence_only and (applied or check_corpus):
        raise ValueError('Historical evidence validation cannot claim installed targets')
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
                candidate['source'].get('edition') != 'charles-1906-enoch' or \
                candidate['source'].get('language') != 'Geez' or \
                candidate['source'].get('confidence') not in ('medium','low'):
            raise ValueError(f'Candidate identity/lifecycle differs: {ref}')
        correction = candidate['source_correction']
        if correction.get('individual_unit_application_approved') is not True or \
                correction.get('full_book_verified') is not False or \
                correction.get('human_specialist_certification') is not False or \
                correction.get('manuscript_witness_certification') is not False or \
                correction.get('graphic_publication_approved') is not False:
            raise ValueError(f'Candidate approval scope differs: {ref}')
        if correction.get('selected_edition_chapter_reviewed') is True and not any(
                certificate['chapter'] == c for certificate in manifest.get('chapter_inventories', [])):
            raise ValueError(f'Candidate claims an unbound complete-chapter review: {ref}')
        findings = record_issues(candidate, c, v)
        # Real source poetry can repeat: repeated spans are review signals,
        # not a license to delete a source-supported refrain.
        errors = [f for f in findings if f['kind'] != 'repeated_english_span_review']
        if errors:
            raise ValueError(f'Candidate has mechanical errors: {ref}: {errors}')
        for row in reviewed_rows(package, manifest['review_bindings'][ref], ref, manifest['files']):
            if candidate['source'].get('confidence')=='low' and (
                    row['source'].get('confidence')!='low' or
                    not candidate['source'].get('transcription_uncertainties') or
                    not candidate['source'].get('note') or
                    not row['source'].get('note') or row['source']['note'] not in candidate['source']['note'] or
                    not candidate['translation'].get('footnotes')):
                raise ValueError(f'Low-confidence critical treatment lacks exact accepted uncertainty/explanation controls: {ref}')
            if any(candidate['source'].get(key) != row['source'].get(key)
                   for key in ('edition', 'language', 'text', 'pages', 'additional_translation_input', 'transcription_uncertainties')) or \
                    ('confidence' in row['source'] and candidate['source'].get('confidence')!=row['source']['confidence']) or \
                    candidate['translation'] != row['translation']:
                raise ValueError(f'Candidate differs from accepted source/English/notes: {ref}')
        witnesses = candidate.get('enoch_witnesses', {}).get('available_witnesses', [])
        if len(witnesses) != 1 or witnesses[0]['witness'] != 'charles_1906' or \
                witnesses[0]['text'] != candidate['source']['text']:
            raise ValueError(f'Selected-edition witness/source mismatch: {ref}')
        baseline = manifest['canonical_baseline_sha256'].get(relative)
        if correction['baseline_sha256'] != baseline:
            raise ValueError(f'Preimage hash differs: {ref}')
        if baseline is not None:
            verify_git_preimage(manifest, relative, baseline)
        target = TRANSLATION / relative
        if evidence_only:
            candidates[relative] = raw
            continue
        if applied:
            if not target.exists() or target.read_bytes() != raw:
                raise ValueError(f'Applied candidate differs: {ref}')
            expected[relative] = sha(raw)
        elif (target.exists() and sha(target.read_bytes()) != baseline) or \
                (not target.exists() and baseline is not None):
            raise ValueError(f'Canonical preimage changed: {ref}')
        candidates[relative] = raw
    for retirement in manifest.get('retirements', []):
        ref = retirement['reference']
        c,v = parse_ref(ref)
        relative = f'{c:03d}/{v:03d}.yaml'
        expected_row = {k:v for k,v in retirement.items() if k != 'review_bindings'}
        for row in reviewed_rows(package, retirement['review_bindings'], ref, manifest['files']):
            if row != expected_row:
                raise ValueError(f'Retirement differs from accepted exact address map: {ref}')
        verify_git_preimage(manifest, relative, retirement['baseline_sha256'])
        target = TRANSLATION / relative
        if evidence_only:
            continue
        if applied:
            if target.exists():
                raise ValueError(f'Retired misaddressed record still exists: {ref}')
            del expected[relative]
        elif not target.exists() or sha(target.read_bytes()) != retirement['baseline_sha256']:
            raise ValueError(f'Retirement preimage changed: {ref}')
    if check_corpus and corpus_hashes() != expected:
        raise ValueError('Canonical changes exceed the exact bounded scope')
    return {'references': manifest['references'], 'candidate_files': len(candidates),
            'retired_references': [r['reference'] for r in manifest.get('retirements', [])],
            'snapshot_file_count': len(expected), 'full_book_verified': False,
            'canonical_targets_checked': not evidence_only,
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
            target.parent.mkdir(parents=True, exist_ok=True)
            originals[target] = target.read_bytes() if target.exists() else None
            temporary = target.with_suffix('.yaml.enoch-pending')
            temporary.write_bytes(artifact(package, f'{c:03d}-{v:03d}.candidate.yaml').read_bytes())
            os.replace(temporary, target)
        for retirement in manifest.get('retirements', []):
            c,v = parse_ref(retirement['reference'])
            target = TRANSLATION / f'{c:03d}/{v:03d}.yaml'
            originals[target] = target.read_bytes()
            target.unlink()
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
