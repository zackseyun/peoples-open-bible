#!/usr/bin/env python3
"""Meaning-first POB retranslation pass on Azure GPT-6.1 Sol.

Each request translates one passage (a chapter, or a slice of a long chapter).
The model sees the whole chapter for context and, for every verse it
translates, the source text, the current POB wording and footnotes, the
lexical/theological decisions, the full revision history (MAINTAINER edits
flagged).

Outputs land under state/meaning_pass/<run>/ (gitignored). Nothing here edits
translation/; `apply` is a separate, explicit step.

  python3 tools/pob_meaning_pass.py translate --run pilot-v1 \
      --passage nt/john/1:1-18 --passage ot/psalms/23
  python3 tools/pob_meaning_pass.py translate --run full-v1 --book romans
  python3 tools/pob_meaning_pass.py report --run pilot-v1
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import os
import pathlib
import random
import re
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from typing import Any

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
TRANSLATION = ROOT / "translation"
STATE = ROOT / "state" / "meaning_pass"
PROMPT_ID = os.environ.get("POB_MEANING_PROMPT", "pob_meaning_first_v4")
PROMPT_PATH = ROOT / "tools" / "prompts" / f"{PROMPT_ID}.md"

AZURE_ACCOUNT = os.environ.get("POB_AOAI_ACCOUNT", "cartha-aoai-truth-1c9177c8")
AZURE_RG = os.environ.get("POB_AOAI_RG", "rg-cartha-truth-openai")
DEFAULT_DEPLOYMENT = os.environ.get("POB_MEANING_DEPLOYMENT", "pob-meaning-gpt-6-1-sol")
API_VERSION = "2025-04-01-preview"

# USD per 1M tokens, Azure retail list price for gpt-6.1-sol, Global, short context.
PRICES = {
    "default": {"input": 2.0, "cached": 0.10, "cache_write": 2.5, "output": 10.0},
    "flex": {"input": 1.0, "cached": 0.05, "cache_write": 1.25, "output": 5.0},
}

MAX_VERSES_PER_REQUEST = 22
MAX_RECORD_CHARS_PER_REQUEST = 70_000

FOOTNOTE_REASONS = [
    "literal_wording",
    "alternative_meaning",
    "textual_variant",
    "cultural_background",
    "cross_reference",
    "name_or_term",
]

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["passage_note", "verses"],
    "properties": {
        "passage_note": {"type": "string"},
        "verses": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": [
                    "id",
                    "meaning",
                    "text",
                    "footnotes",
                    "meaning_decisions",
                    "history_weighed",
                    "change_level",
                    "confidence",
                ],
                "properties": {
                    "id": {"type": "string"},
                    "meaning": {"type": "string"},
                    "text": {"type": "string"},
                    "footnotes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["marker", "text", "reason"],
                            "properties": {
                                "marker": {"type": "string"},
                                "text": {"type": "string"},
                                "reason": {"type": "string", "enum": FOOTNOTE_REASONS},
                            },
                        },
                    },
                    "meaning_decisions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["source_phrase", "prior_rendering", "new_rendering", "rationale"],
                            "properties": {
                                "source_phrase": {"type": "string"},
                                "prior_rendering": {"type": "string"},
                                "new_rendering": {"type": "string"},
                                "rationale": {"type": "string"},
                            },
                        },
                    },
                    "history_weighed": {"type": "string"},
                    "change_level": {"type": "string", "enum": ["kept", "refined", "retranslated"]},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                },
            },
        },
    },
}

MARKER_RE = re.compile(r"\[([a-z]{1,2})\]")
_print_lock = threading.Lock()


def log(msg: str) -> None:
    with _print_lock:
        print(msg, flush=True)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def clip(text: Any, limit: int) -> str:
    s = " ".join(str(text or "").split())
    return s if len(s) <= limit else s[: limit - 1] + "…"


PUNCT_BEFORE_MARKER_RE = re.compile(r"([.,;:!?\u201d\u2019\"')]+)((?:\[[a-z]{1,2}\])+)")


def normalize_text(text: str) -> str:
    """Single line, markers before trailing punctuation ("God[a]," not "God,[a]")."""
    text = re.sub(r"\u2014[ \t]*\n\s*", "\u2014", text or "")
    text = " ".join(text.split())
    return PUNCT_BEFORE_MARKER_RE.sub(lambda m: m.group(2) + m.group(1), text)


def strip_markers(text: str) -> str:
    return re.sub(r"\s+([,.;:!?])", r"\1", MARKER_RE.sub("", text or "")).strip()


# --------------------------------------------------------------------------
# Corpus discovery
# --------------------------------------------------------------------------

def book_dir(spec: str) -> pathlib.Path:
    """Accept 'nt/john', 'john', or a path under translation/."""
    spec = spec.strip("/")
    direct = TRANSLATION / spec
    if direct.is_dir():
        return direct
    hits = [p for p in TRANSLATION.glob(f"*/{spec}") if p.is_dir()]
    if len(hits) != 1:
        raise SystemExit(f"cannot resolve book {spec!r}: {hits}")
    return hits[0]


def chapter_files(bdir: pathlib.Path, chapter: int) -> list[pathlib.Path]:
    cdir = bdir / f"{chapter:03d}"
    if not cdir.is_dir():
        raise SystemExit(f"no chapter dir {cdir}")
    return sorted(p for p in cdir.glob("[0-9][0-9][0-9].yaml"))


def book_chapters(bdir: pathlib.Path) -> list[int]:
    return sorted(int(p.name) for p in bdir.iterdir() if p.is_dir() and p.name.isdigit())


def verse_num(path: pathlib.Path) -> int:
    return int(path.stem)


def load_yaml(path: pathlib.Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


# --------------------------------------------------------------------------
# Context building
# --------------------------------------------------------------------------

def revision_weight(rev: dict[str, Any]) -> str:
    adj = str(rev.get("adjudicator") or "").lower()
    cat = str(rev.get("category") or "").lower()
    if "maintainer" in adj:
        return "MAINTAINER"
    if any(k in adj for k in ("marker", "anchor", "cleanup")) or "footnote" in cat:
        return "formatting"
    if "realignment" in adj or "regression" in adj or "revert" in str(rev.get("rationale") or "")[:120].lower():
        return "automated-policy-revert"
    return "automated-review"


def compact_history(record: dict[str, Any]) -> tuple[list[dict[str, Any]], str, bool]:
    revs = record.get("revisions") or []
    history: list[dict[str, Any]] = []
    has_maintainer = False
    first_text = ""
    for rev in revs:
        if not isinstance(rev, dict):
            continue
        frm = str(rev.get("from") or "")
        to = str(rev.get("to") or "")
        if not first_text and frm:
            first_text = frm
        weight = revision_weight(rev)
        has_maintainer |= weight == "MAINTAINER"
        changed = strip_markers(frm) != strip_markers(to)
        if weight == "formatting" and not changed:
            continue
        entry: dict[str, Any] = {
            "date": str(rev.get("timestamp") or "")[:10],
            "weight": weight,
            "by": rev.get("adjudicator"),
            "category": rev.get("category"),
        }
        if changed:
            entry["from"] = strip_markers(frm)
            entry["to"] = strip_markers(to)
        else:
            entry["note"] = "no text change was recorded for this pass"
        if rev.get("rationale"):
            entry["rationale"] = clip(rev["rationale"], 600)
        history.append(entry)
    return history, first_text, has_maintainer



def verse_context(path: pathlib.Path) -> dict[str, Any]:
    rec = load_yaml(path)
    tr = rec.get("translation") or {}
    history, first_text, has_maintainer = compact_history(rec)
    lexical = []
    for item in rec.get("lexical_decisions") or []:
        if not isinstance(item, dict):
            continue
        lexical.append({
            "source": item.get("source_word"),
            "chosen": item.get("chosen"),
            "alternatives": item.get("alternatives") or [],
            "rationale": clip(item.get("rationale"), 350),
        })
    theological = []
    for item in rec.get("theological_decisions") or []:
        if not isinstance(item, dict):
            continue
        theological.append({
            "issue": item.get("issue"),
            "chosen": item.get("chosen_reading"),
            "alternatives": item.get("alternative_readings") or [],
            "rationale": clip(item.get("rationale"), 450),
        })
    ctx: dict[str, Any] = {
        "id": rec.get("id"),
        "reference": rec.get("reference"),
        "source": {
            "edition": (rec.get("source") or {}).get("edition"),
            "text": (rec.get("source") or {}).get("text"),
        },
        "current_pob": {
            "text": tr.get("text"),
            "footnotes": [
                {"marker": f.get("marker"), "text": clip(f.get("text"), 400)}
                for f in (tr.get("footnotes") or []) if isinstance(f, dict)
            ],
        },
        "first_recorded_text": strip_markers(first_text) if first_text else None,
        "revision_history": history,
        "has_maintainer_revision": has_maintainer,
        "lexical_decisions": lexical,
        "theological_decisions": theological,
    }
    return {k: v for k, v in ctx.items() if v not in (None, [], "")}


def chapter_text(files: list[pathlib.Path]) -> str:
    lines = []
    for p in files:
        rec = load_yaml(p)
        lines.append(f"{verse_num(p)} {strip_markers((rec.get('translation') or {}).get('text') or '')}")
    return "\n".join(lines)


def split_requests(targets: list[pathlib.Path], contexts: dict[pathlib.Path, dict[str, Any]]) -> list[list[pathlib.Path]]:
    total_chars = sum(len(json.dumps(contexts[p], ensure_ascii=False)) for p in targets)
    n = max(1, -(-len(targets) // MAX_VERSES_PER_REQUEST), -(-total_chars // MAX_RECORD_CHARS_PER_REQUEST))
    size = -(-len(targets) // n)
    return [targets[i:i + size] for i in range(0, len(targets), size)]


def build_user_message(book_label: str, chapter: int, chap_text: str, verse_ctxs: list[dict[str, Any]]) -> str:
    ids = [v["id"] for v in verse_ctxs]
    return (
        f"# Passage: {book_label} chapter {chapter}\n\n"
        f"## The whole chapter in the current POB wording (for context)\n\n{chap_text}\n\n"
        f"## Verses to translate now ({len(ids)}): {', '.join(ids)}\n\n"
        "Each record below holds the source text, the current POB wording and footnotes, the first recorded "
        "draft, the full revision history (weight MAINTAINER = human editorial decision), the lexical and "
        "theological decisions.\n\n"
        "```json\n" + json.dumps(verse_ctxs, ensure_ascii=False, indent=1) + "\n```\n\n"
        f"Translate exactly these {len(ids)} verses, in order, using their exact ids."
    )


# --------------------------------------------------------------------------
# Azure
# --------------------------------------------------------------------------

_azure_lock = threading.Lock()


def azure_credentials() -> tuple[str, str]:
    with _azure_lock:
        if not os.environ.get("POB_AOAI_KEY"):
            key = subprocess.check_output(
                ["az", "cognitiveservices", "account", "keys", "list", "-g", AZURE_RG, "-n", AZURE_ACCOUNT,
                 "--query", "key1", "-o", "tsv"], text=True).strip()
            endpoint = subprocess.check_output(
                ["az", "cognitiveservices", "account", "show", "-g", AZURE_RG, "-n", AZURE_ACCOUNT,
                 "--query", "properties.endpoint", "-o", "tsv"], text=True).strip()
            os.environ["POB_AOAI_KEY"] = key
            os.environ["POB_AOAI_ENDPOINT"] = endpoint
        return os.environ["POB_AOAI_ENDPOINT"].rstrip("/"), os.environ["POB_AOAI_KEY"]


def call_model(system: str, user: str, *, deployment: str, effort: str, tier: str) -> dict[str, Any]:
    endpoint, key = azure_credentials()
    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={API_VERSION}"
    body: dict[str, Any] = {
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "max_completion_tokens": 64000,
        "reasoning_effort": effort,
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "pob_meaning_passage", "strict": True, "schema": OUTPUT_SCHEMA},
        },
    }
    if tier == "flex":
        body["service_tier"] = "flex"
    data = json.dumps(body).encode("utf-8")
    delay = 10.0
    for attempt in range(8):
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json", "api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=3600) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:600]
            if exc.code in (408, 429, 500, 502, 503, 504) and attempt < 7:
                wait = float(exc.headers.get("retry-after") or delay) + random.uniform(0, 3)
                log(f"  http {exc.code}; retry in {wait:.0f}s")
                time.sleep(wait)
                delay = min(delay * 2, 240)
                continue
            raise RuntimeError(f"Azure HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            if attempt < 7:
                log(f"  network error {exc}; retry in {delay:.0f}s")
                time.sleep(delay)
                delay = min(delay * 2, 240)
                continue
            raise
    raise RuntimeError("unreachable")


def usage_cost(usage: dict[str, Any], tier: str) -> float:
    p = PRICES["flex" if tier == "flex" else "default"]
    prompt = int(usage.get("prompt_tokens") or 0)
    details = usage.get("prompt_tokens_details") or {}
    cached = int(details.get("cached_tokens") or 0)
    written = int(details.get("cache_write_tokens") or 0)
    plain = max(0, prompt - cached - written)
    out = int(usage.get("completion_tokens") or 0)
    return (plain * p["input"] + cached * p["cached"] + written * p["cache_write"] + out * p["output"]) / 1e6


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def validate_verse(v: dict[str, Any]) -> list[str]:
    v["text"] = normalize_text(v.get("text") or "")
    problems = []
    text = (v.get("text") or "").strip()
    if not text:
        problems.append("empty text")
    markers = MARKER_RE.findall(text)
    notes = [f.get("marker") for f in v.get("footnotes") or []]
    if len(set(markers)) != len(markers):
        problems.append(f"duplicate markers {markers}")
    if sorted(set(markers)) != sorted(set(notes)):
        problems.append(f"markers {markers} != footnotes {notes}")
    expected = [chr(ord("a") + i) for i in range(len(markers))]
    if markers and markers != expected:
        problems.append(f"markers not lettered in order: {markers}")
    if len(notes) > 3:
        problems.append(f"{len(notes)} footnotes > 3")
    return problems


# --------------------------------------------------------------------------
# translate
# --------------------------------------------------------------------------

def parse_passage(spec: str) -> tuple[pathlib.Path, int, int | None, int | None]:
    m = re.fullmatch(r"(.+?)/(\d+)(?::(\d+)(?:-(\d+))?)?", spec.strip())
    if not m:
        raise SystemExit(f"bad passage {spec!r}; use book/chapter[:v1-v2]")
    bdir = book_dir(m.group(1))
    first = int(m.group(3)) if m.group(3) else None
    last = int(m.group(4)) if m.group(4) else first
    return bdir, int(m.group(2)), first, last


def plan_jobs(args: argparse.Namespace) -> list[dict[str, Any]]:
    units: list[tuple[pathlib.Path, int, int | None, int | None]] = []
    for spec in args.passage or []:
        units.append(parse_passage(spec))
    for b in args.book or []:
        bdir = book_dir(b)
        for ch in book_chapters(bdir):
            units.append((bdir, ch, None, None))
    jobs = []
    for bdir, ch, first, last in units:
        files = chapter_files(bdir, ch)
        targets = [p for p in files if (first is None or first <= verse_num(p) <= (last or first))]
        if not targets:
            continue
        contexts = {p: verse_context(p) for p in targets}
        chap = chapter_text(files)
        label = load_yaml(files[0]).get("reference", "").rsplit(" ", 1)[0] or bdir.name
        for group in split_requests(targets, contexts):
            rel_book = bdir.relative_to(TRANSLATION)
            out = STATE / args.run / rel_book / f"{ch:03d}_{verse_num(group[0]):03d}-{verse_num(group[-1]):03d}.json"
            jobs.append({
                "out": out,
                "label": label,
                "chapter": ch,
                "files": group,
                "contexts": [contexts[p] for p in group],
                "chapter_text": chap,
            })
    return jobs


def job_complete(out: pathlib.Path) -> bool:
    """A finished output with every verse present; partial outputs get redone."""
    if not out.exists():
        return False
    try:
        return not json.loads(out.read_text()).get("missing")
    except (OSError, json.JSONDecodeError):
        return False


def run_job(job: dict[str, Any], args: argparse.Namespace, system: str, prompt_sha: str) -> dict[str, Any]:
    out: pathlib.Path = job["out"]
    if job_complete(out) and not args.force:
        return json.loads(out.read_text())
    ctxs = job["contexts"]
    want = [c["id"] for c in ctxs]
    user = build_user_message(job["label"], job["chapter"], job["chapter_text"], ctxs)
    started = time.time()
    responses = []
    got: dict[str, dict[str, Any]] = {}
    passage_note = ""
    pending = list(ctxs)
    for attempt in range(3):
        resp = call_model(system, user, deployment=args.deployment, effort=args.effort, tier=args.tier)
        responses.append({"usage": resp.get("usage"), "model": resp.get("model"),
                          "service_tier": resp.get("service_tier"),
                          "finish_reason": resp["choices"][0].get("finish_reason")})
        content = resp["choices"][0]["message"].get("content") or "{}"
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError as exc:
            log(f"  {out.name}: unparseable response (finish_reason="
                f"{resp['choices'][0].get('finish_reason')}, {len(content)} chars): {exc}; retrying")
            continue
        passage_note = passage_note or parsed.get("passage_note", "")
        for v in parsed.get("verses") or []:
            if v.get("id") in want and v.get("id") not in got and not validate_verse(v):
                got[v["id"]] = v
        pending = [c for c in ctxs if c["id"] not in got]
        if not pending:
            break
        bad = {v.get("id"): validate_verse(v) for v in parsed.get("verses") or [] if v.get("id") in want and validate_verse(v)}
        log(f"  {out.name}: retry {len(pending)} verse(s) {bad or ''}")
        user = build_user_message(job["label"], job["chapter"], job["chapter_text"], pending)
    usage_total = sum(usage_cost(r["usage"] or {}, args.tier) for r in responses)
    result = {
        "run": args.run,
        "prompt_id": PROMPT_ID,
        "prompt_sha256": prompt_sha,
        "deployment": args.deployment,
        "model": responses[-1].get("model"),
        "reasoning_effort": args.effort,
        "service_tier": args.tier,
        "timestamp": utc_now(),
        "seconds": round(time.time() - started, 1),
        "requests": responses,
        "estimated_cost_usd": round(usage_total, 4),
        "passage_note": passage_note,
        "paths": [str(p.relative_to(ROOT)) for p in job["files"]],
        "verses": [got[i] for i in want if i in got],
        "missing": [c["id"] for c in pending],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    tmp.replace(out)
    return result


def cmd_translate(args: argparse.Namespace) -> int:
    system = PROMPT_PATH.read_text(encoding="utf-8")
    prompt_sha = sha256(system)
    jobs = plan_jobs(args)
    todo = [j for j in jobs if args.force or not job_complete(j["out"])]
    log(f"run={args.run} jobs={len(jobs)} todo={len(todo)} verses={sum(len(j['files']) for j in todo)} "
        f"deployment={args.deployment} effort={args.effort} tier={args.tier}")
    if args.dry_run:
        for j in todo:
            chars = len(build_user_message(j["label"], j["chapter"], j["chapter_text"], j["contexts"]))
            log(f"  {j['out'].relative_to(STATE)}  verses={len(j['files'])}  ~{chars // 3} tokens in")
        return 0
    spent = 0.0
    failures = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(run_job, j, args, system, prompt_sha): j for j in todo}
        for fut in concurrent.futures.as_completed(futs):
            j = futs[fut]
            try:
                r = fut.result()
                spent += r.get("estimated_cost_usd") or 0
                log(f"ok {j['out'].relative_to(STATE)} verses={len(r['verses'])} missing={len(r['missing'])} "
                    f"${r.get('estimated_cost_usd')} {r.get('seconds')}s  total=${spent:.2f}")
            except Exception as exc:  # keep going; rerun picks up failures
                failures += 1
                log(f"FAIL {j['out'].relative_to(STATE)}: {exc}")
            if args.budget and spent > args.budget:
                log(f"budget ${args.budget} reached; stopping new work")
                for f in futs:
                    f.cancel()
                break
    log(f"done: spent ~${spent:.2f}, failures={failures}")
    return 1 if failures else 0


# --------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------

def cmd_report(args: argparse.Namespace) -> int:
    run_dir = STATE / args.run
    rows = []
    totals = {"cost": 0.0, "verses": 0, "kept": 0, "refined": 0, "retranslated": 0, "missing": 0}
    for f in sorted(run_dir.rglob("*.json")):
        res = json.loads(f.read_text())
        totals["cost"] += res.get("estimated_cost_usd") or 0
        totals["missing"] += len(res.get("missing") or [])
        by_id = {v["id"]: v for v in res.get("verses") or []}
        for rel in res.get("paths") or []:
            rec = load_yaml(ROOT / rel)
            new = by_id.get(rec.get("id"))
            if not new:
                continue
            new["problems"] = validate_verse(new)
            history, _, has_maint = compact_history(rec)
            tr = rec.get("translation") or {}
            totals["verses"] += 1
            totals[new["change_level"]] += 1
            rows.append({
                "id": rec.get("id"),
                "reference": rec.get("reference"),
                "chunk": str(f.relative_to(run_dir)),
                "passage_note": res.get("passage_note"),
                "source": (rec.get("source") or {}).get("text"),
                "current": {"text": tr.get("text"), "footnotes": [
                    {"marker": x.get("marker"), "text": x.get("text")} for x in tr.get("footnotes") or []]},
                "revisions": len(rec.get("revisions") or []),
                "has_maintainer_revision": has_maint,
                "new": new,
            })
    out = run_dir.parent / f"{args.run}-report.json"
    out.write_text(json.dumps({"run": args.run, "totals": totals, "rows": rows}, ensure_ascii=False, indent=1))
    print(json.dumps(totals, indent=1))
    print(out)
    return 0


# --------------------------------------------------------------------------
# apply
# --------------------------------------------------------------------------

# verse.schema.json allows only these footnote reasons.
SCHEMA_REASON = {
    "literal_wording": "lexical_alternative",
    "alternative_meaning": "alternative_reading",
    "textual_variant": "textual_variant",
    "cultural_background": "cultural_note",
    "cross_reference": "cross_reference",
    "name_or_term": "lexical_alternative",
}


def cmd_apply(args: argparse.Namespace) -> int:
    run_dir = STATE / args.run
    changed = skipped = 0
    for f in sorted(run_dir.rglob("*.json")):
        res = json.loads(f.read_text())
        by_id = {v["id"]: v for v in res.get("verses") or []}
        for rel in res.get("paths") or []:
            path = ROOT / rel
            rec = load_yaml(path)
            new = by_id.get(rec.get("id"))
            if not new or validate_verse(new):
                skipped += 1
                continue
            tr = rec.setdefault("translation", {})
            old_text = tr.get("text") or ""
            if (rec.get("meaning_pass") or {}).get("run") == args.run:
                skipped += 1
                continue
            tr["text"] = new["text"].strip()
            tr["philosophy"] = "dynamic"
            footnotes = [{"marker": n["marker"], "text": n["text"].strip(), "reason": SCHEMA_REASON[n["reason"]]}
                         for n in new.get("footnotes") or []]
            if footnotes:
                tr["footnotes"] = footnotes
            else:
                tr.pop("footnotes", None)
            rec.setdefault("revisions", []).append({
                "timestamp": res["timestamp"],
                "adjudicator": "gpt-6.1-sol-meaning-pass",
                "reviewer_model": res.get("model"),
                "category": "meaning_retranslation",
                "from": old_text,
                "to": tr["text"],
                "rationale": new.get("history_weighed") or "",
            })
            rec["meaning_pass"] = {
                "run": args.run,
                "model": res.get("model"),
                "deployment": res.get("deployment"),
                "prompt_id": res.get("prompt_id"),
                "prompt_sha256": res.get("prompt_sha256"),
                "reasoning_effort": res.get("reasoning_effort"),
                "timestamp": res["timestamp"],
                "change_level": new["change_level"],
                "confidence": new["confidence"],
                "meaning": new["meaning"],
                "meaning_decisions": new.get("meaning_decisions") or [],
                "footnote_kinds": {n["marker"]: n["reason"] for n in new.get("footnotes") or []},
                "history_weighed": new.get("history_weighed") or "",
            }
            rendered = yaml.safe_dump(rec, allow_unicode=True, sort_keys=False, width=1000)
            tmp = path.with_suffix(".yaml.tmp")
            tmp.write_text(rendered, encoding="utf-8")
            tmp.replace(path)
            changed += 1
    print(f"applied={changed} skipped={skipped}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("translate")
    t.add_argument("--run", required=True)
    t.add_argument("--passage", action="append", help="book/chapter[:v1-v2], e.g. nt/john/1:1-18")
    t.add_argument("--book", action="append", help="whole book, e.g. romans or ot/genesis")
    t.add_argument("--deployment", default=DEFAULT_DEPLOYMENT)
    t.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh"])
    t.add_argument("--tier", default="flex", choices=["default", "flex"])
    t.add_argument("--workers", type=int, default=4)
    t.add_argument("--budget", type=float, default=0.0, help="stop starting new requests past this USD estimate")
    t.add_argument("--force", action="store_true")
    t.add_argument("--dry-run", action="store_true")
    t.set_defaults(func=cmd_translate)
    r = sub.add_parser("report")
    r.add_argument("--run", required=True)
    r.set_defaults(func=cmd_report)
    a = sub.add_parser("apply", help="write a finished run into translation/ YAML (explicit step)")
    a.add_argument("--run", required=True)
    a.set_defaults(func=cmd_apply)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
