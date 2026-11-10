"""Verse files as they stood just before the November 2026 meaning-first pass.

Some older application and proposal guards prove that one narrow change touched
nothing else by freezing every other verse in the book, or a passage's context,
to its live bytes. The meaning-first pass (docs/MEANING_FIRST_TRANSLATION_2026-11.md)
later revised those verses on purpose, and every file it revised carries a
top-level ``meaning_pass`` block. For those files the guards read the bytes from
the last commit before the pass, which is exactly what they verified when they
were written. Files without the block, including the reviewed target verses the
pass held back, are still read live, so the guards keep catching any other edit.
"""
from __future__ import annotations

import contextlib
import subprocess
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[1]
# Last commit before the meaning-first retranslation landed. corpus-integrity
# fetches it with the other reviewed baselines.
PRE_MEANING_PASS = '0097010636b2a5ba606c33329f3c1ca470122dd9'

_cat_file = None


def revised_by_meaning_pass(raw: bytes) -> bool:
    return raw.startswith(b'meaning_pass:') or b'\nmeaning_pass:' in raw


def _pre_pass_blob(rel: str) -> bytes:
    global _cat_file
    if _cat_file is None:
        _cat_file = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    _cat_file.stdin.write(f'{PRE_MEANING_PASS}:{rel}\n'.encode())
    _cat_file.stdin.flush()
    header = _cat_file.stdout.readline().split()
    if len(header) != 3 or header[1] != b'blob':
        raise FileNotFoundError(f'{rel} is not in {PRE_MEANING_PASS}')
    data = _cat_file.stdout.read(int(header[2]))
    _cat_file.stdout.read(1)
    return data


def corpus_bytes(path) -> bytes:
    """Live bytes, or the pre-pass bytes when the meaning-first pass revised the file."""
    p = Path(path)
    p = p if p.is_absolute() else ROOT / p
    raw = p.read_bytes()
    if revised_by_meaning_pass(raw):
        return _pre_pass_blob(p.relative_to(ROOT).as_posix())
    return raw


@contextlib.contextmanager
def pre_meaning_pass_records(exporter):
    """Make ``exporter.export_book`` read each verse through ``corpus_bytes``."""
    def load(code, chapter, verse):
        path = exporter.draft.translation_path_for_verse(
            exporter.draft.load_source_verse(code, chapter, verse))
        if not path.exists():
            return None
        return yaml.safe_load(corpus_bytes(path).decode('utf-8'))

    with patch.object(exporter, 'load_translation_record', side_effect=load):
        yield
