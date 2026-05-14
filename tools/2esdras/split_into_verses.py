#!/usr/bin/env python3
"""split_into_verses.py — derive per-verse 2 Esdras YAMLs from chapter YAMLs.

This is a mechanical splitter for 2 Esdras specifically. Unlike the generic
extra-canonical splitter used for Didache / 1 Clement, 2 Esdras already has
explicit verse markers in both the chapter-level Latin source text and the
chapter-level English translation text, so we can split deterministically.
"""
from __future__ import annotations

import pathlib
import re
from typing import Any

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
BOOK_ROOT = REPO_ROOT / 'translation' / 'extra_canonical' / '2_esdras'
BOOK_CODE = '2ES'
BOOK_NAME = '2 Esdras'
VERSE_RE = re.compile(r'(?m)(?<!\S)(\d+)\s')


def parse_verses(text: str) -> dict[int, str]:
    text = text.strip()
    matches = list(VERSE_RE.finditer(text))
    out: dict[int, str] = {}
    for i, m in enumerate(matches):
        verse = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out[verse] = text[start:end].strip()
    return out


def marker_matches(marker: Any, chapter: int, verse: int) -> bool:
    s = str(marker)
    return s == str(verse) or s == f'{chapter}:{verse}'


def footnote_matches_verse(fn: dict[str, Any], chapter: int, verse: int, verse_text: str) -> bool:
    """Return whether a chapter-level footnote belongs on this verse.

    Older 2 Esdras drafts used the destination verse reference as the marker
    itself (for example ``[7:28]``). Newer normalized drafts use reader-safe
    labels like ``[a]`` / ``[b]``. Support both so rerunning the splitter does
    not reintroduce raw verse-reference markers or drop normalized notes.
    """
    marker = str(fn.get('marker') or '').strip()
    anchor_ref = str(fn.get('anchor_ref') or '').strip()
    return bool(marker) and (
        marker_matches(anchor_ref, chapter, verse)
        or marker_matches(marker, chapter, verse)
        or f'[{marker}]' in verse_text
    )


def ensure_footnote_markers(text: str, footnotes: list[dict[str, Any]]) -> str:
    """Add missing inline markers for verse-level reader exports."""
    out = text
    for fn in footnotes:
        marker = str(fn.get('marker') or '').strip()
        if not marker or f'[{marker}]' in out:
            continue
        for terminator in [', ', '. ', '; ']:
            idx = out.find(terminator)
            if idx > 0:
                out = out[:idx] + f'[{marker}]' + out[idx:]
                break
        else:
            out = out[:-1] + f'[{marker}].' if out.endswith('.') else out + f'[{marker}]'
    return out


def split_chapter(path: pathlib.Path) -> int:
    doc = yaml.safe_load(path.read_text(encoding='utf-8'))
    chapter = int(doc['source']['chapter'])
    expected = int(doc['source']['verse_count'])
    source_verses = parse_verses(doc['source']['text'])
    translation_verses = parse_verses(doc['translation']['text'])
    expected_set = list(range(1, expected + 1))
    if list(source_verses) != expected_set:
        raise ValueError(f'{path}: source verse sequence mismatch')
    if list(translation_verses) != expected_set:
        raise ValueError(f'{path}: translation verse sequence mismatch')

    out_dir = BOOK_ROOT / f'{chapter:03d}'
    out_dir.mkdir(parents=True, exist_ok=True)
    footnotes = doc['translation'].get('footnotes', []) or []
    written = 0
    for verse in expected_set:
        verse_text = translation_verses[verse]
        verse_footnotes = [
            fn for fn in footnotes
            if isinstance(fn, dict) and footnote_matches_verse(fn, chapter, verse, verse_text)
        ]
        verse_text = ensure_footnote_markers(verse_text, verse_footnotes)
        record: dict[str, Any] = {
            'id': f'{BOOK_CODE}.{chapter}.{verse}',
            'reference': f'{BOOK_NAME} {chapter}:{verse}',
            'unit': 'verse',
            'book': BOOK_NAME,
            'appendix': bool(doc.get('appendix', False)),
            'compositional_layer': doc.get('compositional_layer'),
            'source': {
                'edition': doc['source'].get('edition'),
                'text': source_verses[verse],
                'language': doc['source'].get('language'),
            },
            'translation': {
                'text': verse_text,
                'philosophy': doc['translation'].get('philosophy'),
            },
            'note': (
                f'Derived mechanically from the chapter-level draft at '
                f'translation/extra_canonical/2_esdras/{chapter:02d}.yaml '
                f'by tools/2esdras/split_into_verses.py. The chapter-level YAML remains '
                f'the authoritative draft/revision record; these verse YAMLs exist for '
                f'reading surfaces, deep links, and per-verse provenance.'
            ),
            'ai_draft_provenance': doc.get('ai_draft', {}),
        }
        if verse_footnotes:
            record['translation']['footnotes'] = verse_footnotes
        out_path = out_dir / f'{verse:03d}.yaml'
        out_path.write_text(yaml.safe_dump(record, allow_unicode=True, sort_keys=False), encoding='utf-8')
        written += 1
    return written


def main() -> int:
    total = 0
    for path in sorted(BOOK_ROOT.glob('[0-9][0-9].yaml')):
        total += split_chapter(path)
        print(f'wrote {path.stem}: {path.stem} -> {total} verses cumulative', flush=True)
    print(f'total verses written: {total}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
