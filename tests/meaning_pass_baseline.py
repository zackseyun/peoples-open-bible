"""Verse files as they stood just before the November 2026 meaning-first pass.

Some reviewed application and proposal tests prove that one narrow change
touched nothing else by freezing every other verse in a book, or a passage's
context, to its live bytes. The meaning-first pass
(docs/MEANING_FIRST_TRANSLATION_2026-11.md) later revised those verses on
purpose, and every file it revised carries a top-level ``meaning_pass`` block.

The reviewed test files stay byte-for-byte as approved. A ``*_live.py``
successor reruns each frozen check inside ``pre_meaning_pass_view()``, which
serves the pre-pass bytes for verse files the pass revised: exactly what the
check verified when it was written. Every other file, including each reviewed
target verse the pass held back, is still read live.
"""
from __future__ import annotations

import contextlib
import subprocess
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
# Last commit before the meaning-first retranslation landed. corpus-integrity
# fetches it with the other reviewed baselines.
PRE_MEANING_PASS = '0097010636b2a5ba606c33329f3c1ca470122dd9'

_cat_file = None


def revised_by_meaning_pass(raw: bytes) -> bool:
    return raw.startswith(b'meaning_pass:') or b'\nmeaning_pass:' in raw


def pre_pass_blob(rel: str) -> bytes:
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


def _verse_rel(path: Path) -> str | None:
    p = path if path.is_absolute() else Path.cwd() / path
    try:
        rel = p.relative_to(ROOT).as_posix()
    except ValueError:
        return None
    return rel if rel.startswith('translation/') and rel.endswith('.yaml') else None


@contextlib.contextmanager
def pre_meaning_pass_view():
    """Serve pre-pass bytes for verse files the meaning-first pass revised."""
    read_bytes, read_text = Path.read_bytes, Path.read_text

    def corpus_bytes(self):
        raw = read_bytes(self)
        rel = _verse_rel(self)
        if rel and revised_by_meaning_pass(raw):
            return pre_pass_blob(rel)
        return raw

    def corpus_text(self, encoding=None, errors=None, *args, **kwargs):
        if _verse_rel(self) is None:
            return read_text(self, encoding, errors, *args, **kwargs)
        return corpus_bytes(self).decode(encoding or 'utf-8', errors or 'strict')

    with patch.object(Path, 'read_bytes', corpus_bytes), patch.object(Path, 'read_text', corpus_text):
        yield
