#!/usr/bin/env python3
"""Compile hash-bound original-language Enoch repair inputs, not translations.

This tool never writes translation YAMLs. The queue is an editorial input:
OCR-derived readings and source marks still need scan/witness review.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

try:
    from . import audit_pob_source_coverage as coverage, verse_parser
except ImportError:
    import audit_pob_source_coverage as coverage
    import verse_parser


def build(chapters: list[int], pob_root: Path = coverage.POB_ROOT) -> dict:
    report = coverage.audit(chapters, pob_root)
    tasks = []
    for chapter in report['chapters']:
        number = chapter['chapter']
        rows, warnings = verse_parser.parse_chapter(number)
        recovered = {row.verse: row for row in rows}
        correction_numbers = {int(lead.split(':')[1])
                              for lead in chapter['existing_source_review']}
        for verse in sorted(set(chapter['missing_verse_numbers']) | correction_numbers):
            row = recovered.get(verse)
            baseline = pob_root / f'{number:03d}/{verse:03d}.yaml'
            tasks.append({
                'reference': f'1 Enoch {number}:{verse}',
                'kind': 'existing_source_review' if baseline.exists() else 'absent_verse',
                'baseline_sha256': hashlib.sha256(baseline.read_bytes()).hexdigest() if baseline.exists() else None,
                'source_edition': 'Charles 1906 Ethiopic',
                'source_text': row.text if row else None,
                'source_text_sha256': hashlib.sha256(row.text.encode()).hexdigest() if row else None,
                'source_files': row.chapter_file.split(' + ') if row else [],
                'source_warnings': warnings,
                'status': 'scan_and_translation_review_required',
            })
    return {'scope': 'Original-language repair queue only; no canonical changes or editorial approvals',
            'chapter_range': [min(chapters), max(chapters)],
            'missing_verse_total': report['missing_verse_total'],
            'existing_source_review_total': report['source_review_total'],
            'tasks': tasks}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chapters', default='1-35')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    start, end = map(int, args.chapters.split('-', 1))
    if not 1 <= start <= end <= 108:
        parser.error('Chapter range must be within 1-108')
    payload = build(list(range(start, end + 1)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n')
    print(f"Prepared {len(payload['tasks'])} original-language review inputs; canonical text unchanged.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
