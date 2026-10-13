#!/usr/bin/env python3
"""Inventory/acquire EVERY leaf of D&C 1835, without inference or publication.

The two copies have different bindings/page counts. Preserve both complete
inventories, including apparently blank pages. OCR/printed labels do not prove
page equivalence; never automatically approve a page from matching text.
Private research snapshots only: no JSP annotations enter reader translations.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import re
import sys
import time
import urllib.error
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.historical_archive_review import digest, dump, fetch, parse_jsp_page

IA = 'https://archive.org'
JSP = 'https://www.josephsmithpapers.org'
ARCHIVE_SHA256 = '741155ac0e498c886e96d7524b144e9d927745fbeccef635d3e904fa8346374c'


def next_data(raw: bytes) -> dict:
    match = re.search(rb'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', raw, re.S)
    if not match:
        raise ValueError('JSP page schema changed')
    data = json.loads(match[1])['props']['pageProps']
    if data.get('is404') or data.get('statusCode') != 200:
        raise ValueError('JSP returned an error document')
    if data['summary']['uri'] != 'doctrine-and-covenants-1835':
        raise ValueError('Unexpected JSP document identity')
    return data


def ia_inventory(scandata: bytes, djvu: bytes) -> list[dict]:
    scan = ET.fromstring(scandata)
    count = int(scan.findtext('bookData/leafCount'))
    if scan.findtext('bookData/bookId') != 'GR_711':
        raise ValueError('Unexpected archive identity')
    pages = scan.findall('pageData/page')
    leaves = [int(page.attrib['leafNum']) for page in pages]
    if leaves != list(range(count)):
        raise ValueError('Missing, duplicate, or reordered scanned leaves')
    objects = ET.fromstring(djvu).findall('.//OBJECT')
    if len(objects) != count:
        raise ValueError('OCR/scan leaf-count mismatch')
    rows = []
    for leaf, page, obj in zip(leaves, pages, objects):
        if obj.get('usemap') != f'GR_711_{leaf:04d}.djvu':
            raise ValueError('OCR leaf identity/order mismatch')
        # Keep coordinates for checking omissions, running heads and bleed-through.
        lines = [[{'text': word.text or '', 'coords': word.get('coords')}
                  for word in line.findall('WORD')]
                 for line in obj.findall('.//LINE')]
        text = '\n'.join(' '.join(word['text'] for word in line) for line in lines)
        rows.append({'reference': f'newberry-leaf-{leaf:04d}', 'leaf': leaf,
                     'metadata_page_number': page.findtext('pageNumber'),
                     'metadata_page_type': page.findtext('pageType'),
                     'included_in_access_formats': page.findtext('addToAccessFormats'),
                     'scan_url': f'{IA}/download/GR_711/page/n{leaf}.jpg',
                     'ocr': {'text': text, 'sha256': digest(text.encode()),
                             'lines': lines, 'role': 'unproofread_comparison_only'},
                     'review_status': 'not_started', 'publication_allowed': False})
    return rows


def jsp_inventory(raw: bytes) -> list[dict]:
    data = next_data(raw)
    count = int(data['summary']['numberOfPages'])
    pages = data['gallery']
    if [int(page['page']) for page in pages] != list(range(1, count + 1)):
        raise ValueError('Missing, duplicate, or reordered JSP pages')
    rows = []
    for page in pages:
        number = int(page['page'])
        href = f'/paper-summary/doctrine-and-covenants-1835/{number}'
        if page['href'] != href:
            raise ValueError('JSP gallery link identity mismatch')
        rows.append({'reference': f'jsp-page-{number:04d}', 'page': number,
                     'metadata_page_label': page['label'], 'url': JSP + href,
                     'review_status': 'not_started', 'publication_allowed': False})
    return rows


def fetch_retry(url: str, path: Path) -> bytes:
    # Receipt mismatch is never retried/replaced as though it were transient.
    for attempt in range(3):
        try:
            return fetch(url, path)
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)
    raise AssertionError('unreachable')


def read_snapshot(path: Path, url: str) -> bytes:
    """Verify a previously acquired file without any network or repair fallback."""
    raw = path.read_bytes()
    receipt = json.loads(path.with_name(path.name + '.receipt.json').read_text())
    if receipt.get('url') != url or receipt.get('sha256') != digest(raw) or receipt.get('bytes') != len(raw):
        raise ValueError(f'Snapshot provenance mismatch: {path}')
    return raw


def audit(out: Path) -> dict:
    """Verify every acquired source/job against receipts and the current parser.

    Successful acquisition audit is NOT independent scan review or publication.
    Stale extracted comparisons require explicit regeneration after the live
    acquisition has terminated; this function never silently rewrites sources.
    """
    raw_dir = out / 'raw/archive'
    scandata = read_snapshot(raw_dir / 'GR_711_scandata.xml', f'{IA}/download/GR_711/GR_711_scandata.xml')
    djvu = read_snapshot(raw_dir / 'GR_711_djvu.xml', f'{IA}/download/GR_711/GR_711_djvu.xml')
    ocr = read_snapshot(raw_dir / 'GR_711_djvu.txt', f'{IA}/download/GR_711/GR_711_djvu.txt')
    if digest(ocr) != ARCHIVE_SHA256:
        raise ValueError('Archived reader witness mismatch')
    seed = read_snapshot(out / 'raw/jsp/preface-iii.html', f'{JSP}/paper-summary/doctrine-and-covenants-1835/11')
    primary, comparison = ia_inventory(scandata, djvu), jsp_inventory(seed)
    target = out / 'doctrine-and-covenants/whole-edition'
    ledger = json.loads((target / 'acquisition.json').read_text())
    if not ledger.get('acquisition_complete') or ledger.get('failures'):
        raise ValueError('Full source acquisition is not complete')
    errors = []
    expected = {'primary': primary, 'comparison': comparison}
    completed = {}
    for kind, rows in expected.items():
        records = ledger['completed'][kind]
        if [record['reference'] for record in records] != sorted(row['reference'] for row in rows):
            raise ValueError(f'{kind} ledger coverage mismatch')
        completed[kind] = {record['reference']: record for record in records}
    for row in primary:
        scan = read_snapshot(target / 'scans' / f"n{row['leaf']:04d}.jpg", row['scan_url'])
        job_path = target / 'jobs' / (row['reference'] + '.json')
        job = json.loads(job_path.read_text())
        record = completed['primary'][row['reference']]
        if job['reference'] != row['reference'] or job['source']['leaf'] != row['leaf']:
            errors.append(f"Primary job identity: {row['reference']}")
        if job['source']['url'] != row['scan_url'] or job['source']['path'] != str((target / 'scans' / f"n{row['leaf']:04d}.jpg").resolve()):
            errors.append(f"Primary scan locator: {row['reference']}")
        if job['source']['kind'] != 'facsimile' or job['source']['language'] != 'en' or job['mode'] != 'english_edition_scan_review':
            errors.append(f"Primary scan mode: {row['reference']}")
        if digest(scan) != job['source']['sha256'] or digest(scan) != record['source_sha256']:
            errors.append(f"Primary scan binding: {row['reference']}")
        if digest(job_path.read_bytes()) != record['job_sha256']:
            errors.append(f"Primary job binding: {row['reference']}")
        if job['english_comparisons'] != [row['ocr']]:
            errors.append(f"Primary OCR identity/coordinates: {row['reference']}")
    for row in comparison:
        raw = read_snapshot(target / 'jsp' / f"page-{row['page']:04d}.html", row['url'])
        identity = next_data(raw)
        if int(identity['summary']['numberOfPages']) != len(comparison):
            errors.append(f"Comparison copy page count: {row['reference']}")
        page = json.loads((target / 'jsp' / f"page-{row['page']:04d}.json").read_text())
        text, summary = parse_jsp_page(raw, allow_empty=True)
        record = completed['comparison'][row['reference']]
        if page['reference'] != row['reference'] or int(summary['requestedPageNumber']) != row['page']:
            errors.append(f"Comparison identity: {row['reference']}")
        if page['url'] != row['url'] or page['page'] != row['page']:
            errors.append(f"Comparison locator: {row['reference']}")
        if digest(raw) != page['webpage_sha256'] or digest(raw) != record['source_sha256']:
            errors.append(f"Comparison snapshot binding: {row['reference']}")
        if page['printed_text'] != text or digest(text.encode()) != page['printed_text_sha256'] or digest(text.encode()) != record['printed_text_sha256']:
            errors.append(f"Stale comparison extraction: {row['reference']}")
    report = {'expected_primary_leaves': len(primary), 'expected_comparison_pages': len(comparison),
              'all_source_artifacts_valid': not errors, 'errors': errors,
              'checked_source_artifacts': len(primary) + len(comparison),
              'source_facing_model_reviews': 0, 'independent_model_reviews': 0,
              'whole_work_verified': False, 'publication_allowed': False,
              'verification_limit': 'Full snapshot/job integrity only; no scan-reading verdicts or full-book approval.'}
    dump(target / 'artifact-audit.json', report)
    if errors:
        raise ValueError(f'{len(errors)} artifact failures; see artifact-audit.json')
    return report


def acquire(out: Path, workers: int = 2) -> dict:
    raw_dir = out / 'raw/archive'
    metadata = fetch_retry(f'{IA}/metadata/GR_711', raw_dir / 'metadata.json')
    files = {file['name']: file for file in json.loads(metadata)['files']}
    raws = {}
    for name in ['GR_711_scandata.xml', 'GR_711_djvu.xml', 'GR_711_djvu.txt']:
        raw = fetch_retry(f'{IA}/download/GR_711/{name}', raw_dir / name)
        if len(raw) != int(files[name]['size']):
            raise ValueError(f'Archive file size mismatch: {name}')
        raws[name] = raw
    if digest(raws['GR_711_djvu.txt']) != ARCHIVE_SHA256:
        raise ValueError('OCR is not the preserved reader archive witness')
    seed = fetch_retry(f'{JSP}/paper-summary/doctrine-and-covenants-1835/11',
                       out / 'raw/jsp/preface-iii.html')
    primary = ia_inventory(raws['GR_711_scandata.xml'], raws['GR_711_djvu.xml'])
    comparison = jsp_inventory(seed)
    target = out / 'doctrine-and-covenants/whole-edition'
    target.mkdir(parents=True, exist_ok=True)
    dump(target / 'inventory.json', {'primary': primary, 'comparison': comparison,
         'scope': 'Every physical leaf, including covers, apparent blanks and back matter',
         'scope_source_hashes': {'scandata': digest(raws['GR_711_scandata.xml']),
                               'djvu_xml': digest(raws['GR_711_djvu.xml']),
                               'jsp_gallery_page': digest(seed)},
         'page_alignment': 'not_established; separate copies must not share assumed offsets',
         'whole_work_verified': False, 'publication_allowed': False})

    def primary_page(row):
        path = target / 'scans' / f"n{row['leaf']:04d}.jpg"
        scan = fetch_retry(row['scan_url'], path)
        if not scan.startswith(b'\xff\xd8\xff'):
            raise ValueError('Scan response is not JPEG')
        job = {'schema_version': 2, 'work': 'Doctrine and Covenants (1835)',
               'reference': row['reference'], 'mode': 'english_edition_scan_review',
               'source': {'kind': 'facsimile', 'language': 'en', 'url': row['scan_url'],
                          'sha256': digest(scan), 'path': str(path.resolve()),
                          'edition': 'Newberry GR_711, 1835', 'leaf': row['leaf']},
               'english_comparisons': [row['ocr']],
               'required_checks': ['read every foreground printed line from the scan',
                   'do not assume empty OCR means a blank page',
                   'separate print from handwriting, running heads and bleed-through',
                   'preserve printed spelling; mark illegibility without inventing text',
                   'compare another copy only after independent scan transcription',
                   'do not infer a missing ancient-language original'],
               'review_status': 'not_started', 'whole_work_verified': False,
               'publication_allowed': False}
        job_path = target / 'jobs' / (row['reference'] + '.json')
        dump(job_path, job)
        return {'reference': row['reference'], 'source_sha256': digest(scan),
                'job_sha256': digest(job_path.read_bytes()), 'bytes': len(scan)}

    def comparison_page(row):
        path = target / 'jsp' / f"page-{row['page']:04d}.html"
        raw = fetch_retry(row['url'], path)
        data = next_data(raw)
        page = data['summary']
        if int(page['requestedPageNumber']) != row['page']:
            raise ValueError('JSP request returned another page')
        if int(page['numberOfPages']) != len(comparison):
            raise ValueError('JSP document page count changed')
        text, _ = parse_jsp_page(raw, allow_empty=True)
        record = {**row, 'webpage_sha256': digest(raw), 'printed_text': text,
                  'printed_text_sha256': digest(text.encode()),
                  'editorial_page_number': page.get('editorialPageNumber'),
                  'role': 'published_reading_of_other_copy_same_edition',
                  'empty_text_status': 'no_lexical_text_requires_scan_check_not_automatically_blank' if not re.search(r'\w', text) else None,
                  'rights': 'private_research_only; modern annotations not republished'}
        dump(target / 'jsp' / f"page-{row['page']:04d}.json", record)
        return {'reference': row['reference'], 'source_sha256': digest(raw),
                'printed_text_sha256': digest(text.encode()), 'bytes': len(raw)}

    tasks = [('primary', row) for row in primary] + [('comparison', row) for row in comparison]
    completed = {'primary': [], 'comparison': []}
    failures = []

    def write_status():
        status = {'work': 'Doctrine and Covenants (1835)',
                  'scope': 'whole digitized copies; no leaf excluded',
                  'expected_primary_leaves': len(primary), 'expected_comparison_pages': len(comparison),
                  'acquired_primary_leaves': len(completed['primary']),
                  'acquired_comparison_pages': len(completed['comparison']),
                  'failures': failures, 'source_facing_model_reviews': 0,
                  'independent_model_reviews': 0, 'whole_work_verified': False,
                  'publication_allowed': False,
                  'acquisition_complete': len(completed['primary']) == len(primary)
                     and len(completed['comparison']) == len(comparison) and not failures,
                  'completed': {kind: sorted(rows, key=lambda row: row['reference'])
                                for kind, rows in completed.items()}}
        dump(target / 'acquisition.json', status)
        return status

    write_status()
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(primary_page if kind == 'primary' else comparison_page, row): (kind, row)
                   for kind, row in tasks}
        for number, future in enumerate(as_completed(futures), 1):
            kind, row = futures[future]
            try:
                completed[kind].append(future.result())
            except Exception as exc:
                failures.append({'kind': kind, 'reference': row['reference'],
                                 'error_type': type(exc).__name__, 'error': str(exc)})
            if number % 25 == 0 or number == len(tasks):
                status = write_status()
                print(json.dumps({key: status[key] for key in ['acquired_primary_leaves',
                      'acquired_comparison_pages', 'acquisition_complete']}), flush=True)
    status = write_status()
    if not status['acquisition_complete']:
        raise RuntimeError(f'{len(failures)} source acquisitions failed; see acquisition.json')
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, choices=range(1, 5), default=2)
    parser.add_argument('--audit-only', action='store_true', help='Verify every cached artifact offline; never fetch or rewrite it')
    args = parser.parse_args()
    if args.audit_only:
        print(json.dumps(audit(args.output.resolve()), indent=2))
    else:
        acquire(args.output.resolve(), args.workers)


if __name__ == '__main__':
    main()
