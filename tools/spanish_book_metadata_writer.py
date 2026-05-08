#!/usr/bin/env python3
"""spanish_book_metadata_writer.py — companion script for in-session Sonnet
subagents translating book_metadata.json (Author / Audience / Date) into
Spanish.

The subagent reads /tmp/spanish_metadata_inputs/<file>.json (one book's
English fields) and pipes back a single-line JSON object:

  {"book_name": "Genesis",
   "author_es": "...",
   "audience_es": "...",
   "date_es": "..."}

This helper merges the Spanish fields into book_metadata.json under
each book's `localized.es` key, atomically. Idempotent — re-running on
the same book overwrites the prior es block.

Run, per book, via:
  cat translated.json | python3 tools/spanish_book_metadata_writer.py
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
META_PATH = REPO_ROOT / "book_metadata.json"
LOCK_PATH = META_PATH.with_suffix(META_PATH.suffix + ".writer.lock")


def acquire_lock(timeout: float = 30.0) -> int:
    import time
    start = time.time()
    while True:
        try:
            fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            return fd
        except FileExistsError:
            if time.time() - start > timeout:
                raise RuntimeError(f"timed out waiting for {LOCK_PATH}")
            time.sleep(0.05)


def release_lock(fd: int) -> None:
    try:
        os.close(fd)
    except Exception:
        pass
    try:
        LOCK_PATH.unlink()
    except FileNotFoundError:
        pass


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR json_decode: {exc}", file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        print("ERROR payload not object", file=sys.stderr)
        return 2

    book_name = (payload.get("book_name") or "").strip()
    if not book_name:
        print("ERROR missing book_name", file=sys.stderr)
        return 2
    es_fields = {
        k.removesuffix("_es"): v
        for k, v in payload.items()
        if k.endswith("_es") and isinstance(v, str) and v.strip()
    }
    if not es_fields:
        print("ERROR no Spanish fields provided", file=sys.stderr)
        return 2

    fd = acquire_lock()
    try:
        meta = json.loads(META_PATH.read_text(encoding="utf-8"))
        books = meta.get("books") or {}
        if book_name not in books:
            print(f"ERROR unknown book: {book_name}", file=sys.stderr)
            return 2
        entry = books[book_name]
        localized = entry.get("localized") or {}
        es_block = localized.get("es") or {}
        es_block.update(es_fields)
        localized["es"] = es_block
        entry["localized"] = localized
        books[book_name] = entry
        meta["books"] = books

        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=str(META_PATH.parent),
            delete=False,
        ) as tmp:
            json.dump(meta, tmp, ensure_ascii=False, indent=2)
            tmp.write("\n")
            tmp_path = pathlib.Path(tmp.name)
        tmp_path.replace(META_PATH)
    finally:
        release_lock(fd)

    print(f"OK wrote es block for {book_name}: fields={sorted(es_fields)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
