#!/usr/bin/env python3
"""manual_summary_io.py — export prompts / import hand-generated summaries
into BibleSummaryCache when no API backend is available.

export: writes one JSON per book with, for every tool, the system prompt and
        each chapter's user prompt (identical to gemini_summary_prewarm.py).
import-chapters / import-books: reads JSON [{book, chapter, tool, output}]
        and writes cache entries with the same key scheme + source_hash as
        the prewarm script. Entries go in the fallback (gemini) key slot so a
        future primary-model run takes precedence, and carry a `generator`
        attribute recording who actually wrote them.
"""
import argparse, hashlib, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import boto3
import gemini_summary_prewarm as g

TABLE = "BibleSummaryCache-alpha"
SLOT = g.GEMINI_MODEL_VERSION


def chapters_for(book):
    bk = g.normalize_token(book)
    return sorted([c for c in g.load_chapters("POB") if c["book_label"] == bk], key=lambda c: c["chapter"])


def put(ddb, entry, generator):
    g.put_summary(ddb, TABLE, entry)
    ddb.update_item(TableName=TABLE, Key={"summary_key": {"S": entry["summary_key"]}},
                    UpdateExpression="SET generator = :g", ExpressionAttributeValues={":g": {"S": generator}})


def cmd_export(a):
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    for book in a.books:
        chs = chapters_for(book)
        data = {"book": g.normalize_token(book), "tools": {}}
        for tool in g.TOOLS:
            data["tools"][tool] = {
                "system_chapter": g.summary_system_prompt(tool, g.SCOPE_CHAPTER, book),
                "system_book": g.summary_system_prompt(tool, g.SCOPE_BOOK, book),
            }
        data["chapters"] = [{"chapter": c["chapter"], "user_prompt": g.format_chapter_passage("POB", book, c["chapter"], c["verses"])} for c in chs]
        p = out / (g.normalize_token(book).replace(" ", "_") + ".json")
        p.write_text(json.dumps(data, ensure_ascii=False, indent=1))
        print(p, len(chs), "chapters", sum(len(c["user_prompt"]) for c in data["chapters"]), "chars")


def cmd_import_chapters(a):
    ddb = boto3.client("dynamodb", region_name="us-west-2")
    rows = json.load(open(a.file)); n = 0
    by_book = {}
    for r in rows:
        bk = g.normalize_token(r["book"])
        if bk not in by_book:
            by_book[bk] = {c["chapter"]: c for c in chapters_for(bk)}
        ch = by_book[bk][int(r["chapter"])]
        text = g.normalize_summary_output(r["output"])
        assert text, r
        key = g.summary_key("POB", "unspecified", g.SCOPE_CHAPTER, bk, ch["chapter"], r["tool"], g.PROMPT_VERSION, SLOT)
        put(ddb, {"summary_key": key, "translation": "POB", "translation_version": "unspecified",
                  "scope": g.SCOPE_CHAPTER, "book": bk, "chapter": ch["chapter"], "tool": r["tool"],
                  "output": text, "prompt_version": g.PROMPT_VERSION, "model_version": SLOT,
                  "source_hash": g.canonical_source_hash(ch["verses"]), "verse_count": len(ch["verses"]),
                  "generated_at": g.now_iso(), "updated_at": g.now_iso()}, a.generator)
        n += 1
    print("wrote", n, "chapter entries")


def cmd_import_books(a):
    ddb = boto3.client("dynamodb", region_name="us-west-2")
    rows = json.load(open(a.file)); n = 0
    for r in rows:
        bk = g.normalize_token(r["book"]); chs = chapters_for(bk)
        sums = [g.fetch_existing_chapter_output(ddb, TABLE, bk, c["chapter"], r["tool"]) for c in chs]
        assert all(sums), f"{bk} {r['tool']}: chapter summaries missing"
        key = g.summary_key("POB", "unspecified", g.SCOPE_BOOK, bk, 0, r["tool"], g.PROMPT_VERSION, SLOT)
        put(ddb, {"summary_key": key, "translation": "POB", "translation_version": "unspecified",
                  "scope": g.SCOPE_BOOK, "book": bk, "chapter": 0, "tool": r["tool"],
                  "output": g.normalize_summary_output(r["output"]), "prompt_version": g.PROMPT_VERSION,
                  "model_version": SLOT, "source_hash": hashlib.sha256("\n".join(sums).encode()).hexdigest(),
                  "verse_count": sum(len(c["verses"]) for c in chs),
                  "generated_at": g.now_iso(), "updated_at": g.now_iso()}, a.generator)
        n += 1
    print("wrote", n, "book entries")


def cmd_book_inputs(a):
    """Print book-scope user prompts built from cached chapter summaries."""
    ddb = boto3.client("dynamodb", region_name="us-west-2")
    out = {}
    for book in a.books:
        bk = g.normalize_token(book)
        for tool in g.TOOLS:
            sums = [(c["chapter"], g.fetch_existing_chapter_output(ddb, TABLE, bk, c["chapter"], tool)) for c in chapters_for(bk)]
            out[f"{bk}|{tool}"] = {"system": g.summary_system_prompt(tool, g.SCOPE_BOOK, bk),
                                   "user": g.format_book_passage("POB", bk, sums),
                                   "missing": [c for c, s in sums if not s]}
    json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1); print("wrote", a.out)


ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
e = sp.add_parser("export"); e.add_argument("--out", required=True); e.add_argument("books", nargs="+")
for name in ("import-chapters", "import-books"):
    p = sp.add_parser(name); p.add_argument("file"); p.add_argument("--generator", required=True)
b = sp.add_parser("book-inputs"); b.add_argument("--out", required=True); b.add_argument("books", nargs="+")
a = ap.parse_args()
{"export": cmd_export, "import-chapters": cmd_import_chapters, "import-books": cmd_import_books, "book-inputs": cmd_book_inputs}[a.cmd](a)
