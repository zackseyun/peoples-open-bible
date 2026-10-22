#!/usr/bin/env python3
"""Current reader export with an isolated Enoch wording-details extension.

The historical export_mobile_bible.py stays byte-identical for its source-review
contracts. All non-Enoch exporters are delegated to that unchanged module.
No monkeypatches or import-time replacement of historical functions are used.
"""
from __future__ import annotations
import argparse
import copy
import json
from pathlib import Path
import sys
from collections import defaultdict

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools import export_mobile_bible as legacy

EXTRA_CANONICAL_ROOT=legacy.EXTRA_CANONICAL_ROOT
# Exact identity, not copies of canonical/apocryphal export implementations.
export_book=legacy.export_book
export_apocrypha_book=legacy.export_apocrypha_book
export_psalms_book=legacy.export_psalms_book
PROTOCOL='pob-enoch-paired-source-review-v1'


def _export_record_verse(verse_num,record):
    out=legacy._export_record_verse(verse_num,record)
    if out is None:return None
    source=record.get('source') or {}
    if out.get('footnotes') and record.get('book')=='1 Enoch' and \
            (record.get('source_correction') or {}).get('individual_unit_application_approved') is True and \
            source.get('edition')=='charles-1906-enoch' and source.get('language')=='Geez' and \
            source.get('text') and source.get('pages'):
        out['footnote_review']=PROTOCOL
        out['source_critical']={key:copy.deepcopy(source[key]) for key in
            ('edition','language','text','pages','note','confidence','transcription_uncertainties',
             'additional_translation_input') if key in source}
    return out


def _enoch_expected_verse_map():
    from tools.enoch import verse_parser
    from tools.enoch.audit_pob_source_coverage import EXPECTED_VERSES
    from tools.enoch.selected_edition_sources import registry_data
    full=(registry_data() or {}).get('chapters',{})
    expected={}
    for chapter in range(1,109):
        # Validate registered evidence even where a release count is declared.
        reviewed,_=verse_parser.parse_chapter(chapter)
        if chapter in EXPECTED_VERSES:
            expected[chapter]=list(range(1,EXPECTED_VERSES[chapter]+1))
        elif str(chapter) in full:
            expected[chapter]=[row.verse for row in reviewed]
        else:
            # Individual source-only overrides cannot alter release eligibility.
            raw,_=verse_parser.parse_ocr_chapter(chapter)
            expected[chapter]=[row.verse for row in raw]
    return expected


def export_extra_canonical_book(book_code):
    if book_code!='ENO':return legacy.export_extra_canonical_book(book_code)
    book_dir=EXTRA_CANONICAL_ROOT/'1_enoch'
    if not book_dir.exists():return None
    by_chapter=defaultdict(dict);source_records=[]
    for chapter_dir in sorted(book_dir.iterdir()):
        if not chapter_dir.is_dir():continue
        try:chapter=int(chapter_dir.name)
        except ValueError:continue
        for file in sorted(chapter_dir.glob('*.yaml')):
            try:verse=int(file.stem)
            except ValueError:continue
            record=legacy.yaml.safe_load(file.read_text(encoding='utf-8')) or {}
            source_records.append(record)
            out=_export_record_verse(verse,record)
            if out is not None:by_chapter[chapter][verse]=out
    expected=_enoch_expected_verse_map();chapters=[]
    for chapter in sorted(by_chapter):
        verses=by_chapter[chapter];numbers=sorted(verses)
        if not numbers or numbers!=expected.get(chapter,[]):continue
        rows=[verses[n] for n in numbers]
        legacy._annotate_jesus_words(rows,
            allow_lord_title='ENO' in legacy._JESUS_LORD_TITLE_BOOKS)
        chapters.append({'chapter':chapter,'verses':rows})
    if not chapters:return None
    payload={'name':legacy.EXTRA_CANONICAL_BOOK_TITLES['ENO'],'chapters':chapters}
    metadata=legacy._book_source_metadata('ENO',source_records)
    if metadata:payload['metadata']=metadata
    return payload


def export_translation():
    books=[]
    for order,export in [(legacy.CANONICAL_BOOK_ORDER,export_book),
                         (legacy.APOCRYPHA_BOOK_ORDER,export_apocrypha_book),
                         (legacy.EXTRA_CANONICAL_BOOK_ORDER,export_extra_canonical_book)]:
        for code in order:
            book=export(code)
            if book is not None:books.append(book)
    return legacy.terminology_policy.normalize_reader_payload_in_place({
        'translation':"POB: People's Open Bible (Preview)",'books':books})


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True)
    args=parser.parse_args(argv);path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    payload=export_translation()
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=4)+'\n',encoding='utf-8')
    books=len(payload['books']);chapters=sum(len(b['chapters']) for b in payload['books'])
    verses=sum(len(c['verses']) for b in payload['books'] for c in b['chapters'])
    print(f'Wrote {path} ({books} books, {chapters} chapters, {verses} verses)')
    return 0

if __name__=='__main__':raise SystemExit(main())
