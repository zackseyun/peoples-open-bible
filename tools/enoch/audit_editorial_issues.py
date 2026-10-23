#!/usr/bin/env python3
"""Read-only Enoch issue register: inventory, English structure and review holds.

No finding from this tool is translation approval. Missing files under an
undeclared chapter count are parser leads, not certified missing verses.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

import yaml

try:
    from . import audit_pob_source_coverage as coverage
except ImportError:
    import audit_pob_source_coverage as coverage

ROOT = Path(__file__).resolve().parents[2]
LOADER = getattr(yaml, 'CSafeLoader', yaml.SafeLoader)


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def record_issues(record: dict, chapter: int, verse: int) -> list[dict]:
    """Mechanical findings only; never infer a replacement translation."""
    issues = []

    def add(kind: str, detail: str) -> None:
        issues.append({'kind': kind, 'detail': detail})

    for field, expected in (('id', f'1EN.{chapter}.{verse}'),
                            ('reference', f'1 Enoch {chapter}:{verse}'),
                            ('book', '1 Enoch')):
        if record.get(field) != expected:
            add('identity_mismatch', f'{field}: expected {expected!r}')
    source = record.get('source') or {}
    translation = record.get('translation') or {}
    if not isinstance(source, dict) or not isinstance(translation, dict):
        add('invalid_record_shape', 'source and translation must be maps')
        return issues
    if not str(source.get('text') or '').strip():
        add('empty_source', 'Source text is empty')
    origin_note = str(source.get('note') or '').casefold()
    if any(signal in origin_note for signal in (
            'source corrected to full beta', 'source text corrected against beta',
            'full text recovered from oracle')):
        add('source_origin_policy_review',
            'Current source explicitly comes from the validation oracle; replace from inspected permitted edition, not a copied oracle')
    for witness in (record.get('enoch_witnesses') or {}).get('available_witnesses', []):
        if witness.get('witness') == 'charles_1906' and witness.get('text') != source.get('text'):
            add('charles_witness_source_mismatch',
                'Loaded Charles text differs from the declared selected source; adjudicate rather than inheriting stale witness claims')
    text = str(translation.get('text') or '')
    if not text.strip():
        add('empty_translation', 'English text is empty')
    notes = translation.get('footnotes') or []
    if not isinstance(notes, list) or any(not isinstance(n, dict) for n in notes):
        add('invalid_footnotes', 'Footnotes must be a list of maps')
        return issues
    names = [str(n.get('marker') or '') for n in notes]
    # Only single-letter anchors are recognized as reader footnotes. A word
    # such as [him] can be a supplied word and must not be silently deleted.
    anchors = re.findall(r'\[([a-z])\]', text)
    for marker, count in Counter(names).items():
        if not re.fullmatch('[a-z]', marker):
            add('invalid_note_marker', f'Non-letter footnote marker {marker!r}')
        if count > 1:
            add('duplicate_note_marker', f'{marker!r} defines {count} notes')
    for marker, count in Counter(anchors).items():
        if count > 1:
            add('repeated_note_anchor', f'[{marker}] occurs {count} times; inspect mapping')
    for marker in sorted(set(anchors) - set(names)):
        add('missing_footnote', f'[{marker}] has no note')
    for marker in sorted(set(names) - set(anchors)):
        add('unanchored_footnote', f'Note {marker!r} has no single-letter anchor')
    for note in notes:
        if not str(note.get('text') or '').strip():
            add('empty_footnote', f'Note {note.get("marker")!r} has no text')
    # Repetition is an inspection lead, not proof of corruption: poetry can
    # repeat on purpose. Require a substantial exact, case-insensitive span.
    words = re.findall(r"[\w’'-]+", re.sub(r'\[[a-z]\]', '', text).casefold())
    spans = Counter(tuple(words[n:n + 12]) for n in range(max(0, len(words) - 11)))
    repeated = next((span for span, count in spans.items() if count > 1), None)
    if repeated:
        add('repeated_english_span_review', 'Repeated 12-word span: ' + ' '.join(repeated))
    return issues


def build(chapters: list[int], pob_root: Path = coverage.POB_ROOT,
          applications: Path = ROOT / 'sources/textual_restoration/applications') -> dict:
    from tools.enoch.structural_counts import load_all_inventories
    counts=load_all_inventories()
    mapping_reviews={c:v for c,v in counts.items() if v.get('canonical_mapping_pending') is True}
    inventory = coverage.audit(chapters, pob_root, diagnostic_counts={
        c: len(v.get('canonical_address_units',v['units'])) for c, v in counts.items() if c not in mapping_reviews})
    issues = {}
    hashes = {}

    def row(chapter: int, verse: int) -> dict:
        key = (chapter, verse)
        return issues.setdefault(key, {
            'reference': f'1 Enoch {chapter}:{verse}', 'chapter': chapter, 'verse': verse,
            'findings': [], 'canonical_sha256': None, 'translation_approved': False})

    for c,proof in mapping_reviews.items():
        if c in chapters:
            row(c,1)['findings'].append({
                'kind':'printed_source_to_canonical_mapping_review',
                'detail':f"Selected print has{len(proof['units'])} body units versus{coverage.EXPECTED_VERSES.get(c)} declared POBaddresses. Review source-to-canonical segmentation; no spurious-verse, missing-ancient-text or retirement conclusion from counts alone.",
                'count_basis':'separately_paired_printed_source_units',
                'artifact':proof['artifact']})
    for chapter in inventory['chapters']:
        number = chapter['chapter']
        for verse in chapter['missing_verse_numbers']:
            row(number, verse)['findings'].append({
                'kind': 'absent_verse_file',
                'detail': ('Absent under a declared selected-edition count' if
                           chapter['versification_inventory_declared'] else
                           'Parser-derived absent-unit lead; verify count and combined units'),
                'count_basis': chapter['expected_count_basis']})
        for verse in chapter['unexpected_verse_numbers']:
            row(number, verse)['findings'].append({
                'kind': 'unexpected_verse_file',
                'detail': 'Record number exceeds the selected count; check printed addressing before retiring or relocating it',
                'count_basis': chapter['expected_count_basis']})
        for signal in chapter['existing_source_review']:
            verse = int(signal.split(':')[1])
            row(number, verse)['findings'].append({'kind': 'source_alignment_review', 'detail': signal})
        for path in sorted((pob_root / f'{number:03d}').glob('[0-9][0-9][0-9].yaml')):
            verse = int(path.stem)
            raw = path.read_bytes()
            hashes[f'{number:03d}/{verse:03d}.yaml'] = sha(raw)
            try:
                record = yaml.load(raw, Loader=LOADER)
                findings = (record_issues(record, number, verse) if isinstance(record, dict)
                            else [{'kind': 'invalid_record_shape', 'detail': 'YAML must be a map'}])
            except yaml.YAMLError as error:
                findings = [{'kind': 'malformed_yaml', 'detail': str(error)}]
            if findings or (number, verse) in issues:
                item = row(number, verse)
                item['canonical_sha256'] = sha(raw)
                item['findings'].extend(findings)
    # Preserve existing status records as evidence, not merged/majority-vote
    # approval. A later application can supersede a diagnostic. Consumers must
    # inspect its receipt before treating a historical finding as unresolved.
    reviews = []
    for path in sorted(applications.glob('enoch*/status.json')):
        raw = path.read_bytes()
        status = json.loads(raw)
        reviews.append({'path': str(path.relative_to(applications)),
                        'sha256': sha(raw), 'record': status})
    findings = [finding for issue in issues.values() for finding in issue['findings']]
    declared = sum(len(c['missing_verse_numbers']) for c in inventory['chapters']
                   if c['versification_inventory_declared'])
    return {
        'scope': 'Read-only mechanical audit and historical source-review register; not full linguistic verification or publication approval',
        'chapter_range': [min(chapters), max(chapters)],
        'summary': {'canonical_files': len(hashes), 'affected_references': len(issues),
                    'absent_files_under_declared_counts': declared,
                    'absent_unit_leads_under_parser_counts': inventory['missing_verse_total'] - declared,
                    'source_alignment_signals': inventory['source_review_total'],
                    'findings_by_kind': dict(sorted(Counter(f['kind'] for f in findings).items()))},
        'corpus_sha256': sha(json.dumps(hashes, sort_keys=True).encode()),
        'canonical_file_sha256': hashes,
        'issues': [issues[key] for key in sorted(issues)],
        'historical_review_status': reviews,
        'historical_review_limit': 'Status snapshots can be superseded by later bounded applications; acceptance of a candidate does not certify installed text or an entire chapter',
        'inventory': inventory, 'printed_source_mapping_reviews':sorted(c for c in mapping_reviews if c in chapters),
        'canonical_changed': False, 'full_book_verified': False, 'publication_approved': False,
    }


def markdown(report: dict) -> str:
    summary = report['summary']
    lines = ['# 1 Enoch - verse-by-verse repair register', '', report['scope'], '',
             f"- Canonical verse files inspected: {summary['canonical_files']}",
             f"- Absent files under declared counts: {summary['absent_files_under_declared_counts']}",
             f"- Parser-derived absent-unit leads: {summary['absent_unit_leads_under_parser_counts']}",
             f"- Source-alignment signals: {summary['source_alignment_signals']}",
             '- Do not add these categories as a count of proven translation errors.',
             '- Unflagged text has not thereby passed source or linguistic verification.',
             '- Check later application receipts before acting on historical reviews.', '',
             '| Reference | Findings |', '|---|---|']
    for row in report['issues']:
        detail = '; '.join(f"{f['kind']}: {f['detail']}" for f in row['findings'])
        lines.append(f"| {row['reference']} | {detail.replace('|', '/').replace(chr(10), ' ')} |")
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--markdown', type=Path)
    args = parser.parse_args()
    report = build(list(range(1, 109)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    if args.markdown:
        args.markdown.parent.mkdir(parents=True, exist_ok=True)
        args.markdown.write_text(markdown(report))
    print(json.dumps(report['summary'], indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
