#!/usr/bin/env python3
"""Evidence-backed progress toward the complete 108-chapter repair.

This is not a translation approval mechanism. It counts exact current units
whose submitted source, English and notes have retained accepted evidence.
Unimported historical evidence is pending audit, not proof that its text is bad.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.enoch import audit_pob_source_coverage as coverage
from tools.enoch import bounded_application as transaction


def build() -> dict:
    current = transaction.corpus_hashes()
    accepted = {}
    inventories = {}
    warnings = []
    # This earlier application has its own versioned schema/review normalizer.
    from tools.textual_restoration import enoch_20261020_transaction as previous
    try:
        from tools.enoch.current_evidence import verify_current
        verify_current(previous.PACKAGE)
        for c, v in previous.REFS:
            accepted[(c, v)] = {'application': str(previous.PACKAGE.relative_to(transaction.ROOT)),
                                'kind': 'earlier_bounded_unit_repair'}
    except (ValueError, OSError) as error:
        warnings.append('Earlier 15-unit application requires supersession/evidence audit: ' + str(error))
    for package in sorted(transaction.APPLICATIONS.glob('enoch_full_repair_batch*')):
        receipt_path = package / 'application.json'
        if not receipt_path.exists():
            continue
        try:
            transaction.verify(package, evidence_only=True)
            manifest = transaction.load_manifest(package)
            receipt = json.loads(receipt_path.read_text())
            if receipt.get('status') != 'applied_verified' or \
                    receipt.get('manifest_sha256') != transaction.sha((package/'manifest.json').read_bytes()):
                raise ValueError('Application receipt does not bind the current manifest')
            for ref in manifest['references']:
                c, v = transaction.parse_ref(ref)
                candidate_name = f'{c:03d}-{v:03d}.candidate.yaml'
                if current.get(f'{c:03d}/{v:03d}.yaml') != manifest['files'][candidate_name]:
                    continue  # A later repair can legitimately supersede a unit.
                bindings = manifest['review_bindings'][ref]
                if len({b['reviewer_id'] for b in bindings}) < 2:
                    raise ValueError('Distinct review identities missing')
                for binding in bindings:
                    transaction.review_row(package, binding, ref, manifest['files'])
                accepted[(c, v)] = {'application': str(package.relative_to(transaction.ROOT)),
                                    'kind': 'paired_selected_edition_unit_review'}
            for certificate in manifest.get('chapter_inventories', []):
                if not certificate.get('independent_count_confirmation'):
                    continue
                if certificate['artifact'] not in manifest['files']:
                    raise ValueError('Unpinned chapter-count certificate')
                inventories[certificate['chapter']] = certificate
        except (ValueError, OSError, KeyError) as error:
            warnings.append(f'{package.name}: {error}')
    chapters = []
    for chapter in range(1, 109):
        present = sorted(int(Path(name).stem) for name in current
                         if name.startswith(f'{chapter:03d}/'))
        certificate = inventories.get(chapter)
        count = len(certificate['units']) if certificate else coverage.EXPECTED_VERSES.get(chapter)
        reviewed = sorted(v for c, v in accepted if c == chapter)
        expected = list(range(1, count + 1)) if count is not None else None
        complete = bool(certificate) and present == expected and reviewed == expected
        chapters.append({'chapter': chapter, 'current_records': present,
                         'expected_units': expected,
                         'count_basis': ('paired_scan_inventory' if certificate else
                                         'legacy_declared_count_needs_completion_evidence' if count else
                                         'count_not_yet_completion_certified'),
                         'current_units_with_imported_review_evidence': reviewed,
                         'selected_edition_chapter_review_complete': complete})
    return {'objective': 'Fully repair the complete POB translation of 1 Enoch, all108 chapters',
            'scope': 'Source text, complete correctly addressed English units, source/lexical notes and canonical delivery; not an ancient-autograph or human-specialist certification',
            'canonical_file_count': len(current),
            'current_units_with_imported_review_evidence': len(accepted),
            'chapters_with_complete_imported_selected_edition_review': [c['chapter'] for c in chapters
                if c['selected_edition_chapter_review_complete']],
            'chapters': chapters, 'evidence_inventory_warnings': warnings,
            'limits': 'Historical accepted packages not yet imported require evidence audit, not automatic retranslation. Parser lengths and file presence do not prove source fidelity.',
            'completion_proven': False,
            'remaining_completion_gates': [
                'All108 chapter inventories independently checked against selected printed boundaries',
                'Every actual current source/English/note payload supported by accepted source and lexical review',
                'All wrong addresses, clipped/combined units, unjustified wording and oracle-source violations repaired',
                'All remaining true glyph/lexical holds resolved or defensible source-critical treatment reviewed',
                'Complete schema, identity, footnote, export and regression checks on the actual final corpus',
                'Exact final source state on main and verified canonical/public delivery',
                'Requirement-by-requirement final completion audit; no narrow green-test substitute'],
            'artwork_publication_approval': False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    report = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('canonical_file_count',
        'current_units_with_imported_review_evidence',
        'chapters_with_complete_imported_selected_edition_review', 'completion_proven')}, indent=2))
    return 0


if __name__ == '__main__':
    main()
