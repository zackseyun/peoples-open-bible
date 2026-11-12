#!/usr/bin/env python3
"""Meaning-first POB in other languages, from the source text and the new English.

For each verse the model sees the source text, the English meaning-first
translation with its notes and stated meaning, the current POB wording in the
target language, and the whole chapter in the new English. Language rules come
from config/meaning_localize_languages.yaml; the prompt is
tools/prompts/pob_meaning_localize_v1.md.

Outputs land under $POB_MEANING_STATE/<run>/<lang>/ (default ~/pob-meaning-state,
outside the checkout). Nothing here edits translation_<lang>/.

  python3 tools/pob_meaning_localize.py translate --lang es --run es-sample-v1 \
      --passage ot/psalms/23 --passage extra_canonical/1_enoch/46
  python3 tools/pob_meaning_localize.py report --lang es --run es-sample-v1
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import pathlib
import random
import sys
import time
import urllib.error
import urllib.request
from typing import Any

import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pob_meaning_pass as base  # noqa: E402

ROOT = base.ROOT
TRANSLATION = base.TRANSLATION
STATE = base.STATE
PROMPT_ID = "pob_meaning_localize_v1"
PROMPT_PATH = ROOT / "tools" / "prompts" / f"{PROMPT_ID}.md"
LANGS = yaml.safe_load((ROOT / "config" / "meaning_localize_languages.yaml").read_text(encoding="utf-8"))
DEFAULT_DEPLOYMENT = base.os.environ.get("POB_LOCALIZE_DEPLOYMENT", "sermon-study-gpt-6-luna")

# USD per 1M tokens for gpt-6-luna (estimate; Flex is half the standard price).
PRICES = {"flex": {"input": 0.05, "cached": 0.005, "output": 0.25},
          "default": {"input": 0.10, "cached": 0.01, "output": 0.50}}
MAX_VERSES = 22
MAX_CHARS = 60_000

OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object", "additionalProperties": False, "required": ["passage_note", "verses"],
    "properties": {
        "passage_note": {"type": "string"},
        "verses": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["id", "text", "footnotes", "decisions", "change_level", "confidence"],
            "properties": {
                "id": {"type": "string"},
                "text": {"type": "string"},
                "footnotes": {"type": "array", "items": {
                    "type": "object", "additionalProperties": False, "required": ["marker", "text", "reason"],
                    "properties": {"marker": {"type": "string"}, "text": {"type": "string"},
                                   "reason": {"type": "string", "enum": base.FOOTNOTE_REASONS}}}},
                "decisions": {"type": "array", "items": {
                    "type": "object", "additionalProperties": False,
                    "required": ["source_phrase", "rendering", "reason"],
                    "properties": {"source_phrase": {"type": "string"}, "rendering": {"type": "string"},
                                   "reason": {"type": "string"}}}},
                "change_level": {"type": "string", "enum": ["kept", "refined", "retranslated"]},
                "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            }}},
    },
}


def system_prompt(lang: str) -> str:
    cfg = LANGS[lang]
    text = PROMPT_PATH.read_text(encoding="utf-8")
    return text.replace("{LANGUAGE_RULES}", cfg["rules"].strip()).replace("{LANGUAGE_NAME}", cfg["name"])


def target_path(lang: str, en_path: pathlib.Path) -> pathlib.Path:
    return ROOT / LANGS[lang]["dir"] / en_path.resolve().relative_to(TRANSLATION)


def verse_context(lang: str, en_path: pathlib.Path) -> dict[str, Any]:
    en = base.load_yaml(en_path)
    tr = en.get("translation") or {}
    mp = en.get("meaning_pass") or {}
    ctx: dict[str, Any] = {
        "id": en.get("id"),
        "reference": en.get("reference"),
        "source": {"edition": (en.get("source") or {}).get("edition"), "text": (en.get("source") or {}).get("text")},
        "english_meaning_first": {
            "text": tr.get("text"),
            "notes": [{"marker": f.get("marker"), "text": base.clip(f.get("text"), 400)}
                      for f in tr.get("footnotes") or [] if isinstance(f, dict)],
            "meaning": mp.get("meaning"),
            "confidence": mp.get("confidence"),
            "decisions": [{"source": d.get("source_phrase"), "rendering": d.get("new_rendering"),
                           "reason": base.clip(d.get("rationale"), 300)} for d in mp.get("meaning_decisions") or []],
        },
    }
    tp = target_path(lang, en_path)
    if tp.exists():
        cur = (base.load_yaml(tp).get("translation") or {})
        ctx["current_wording"] = {
            "text": cur.get("text"),
            "notes": [{"marker": f.get("marker"), "text": base.clip(f.get("text"), 300)}
                      for f in cur.get("footnotes") or [] if isinstance(f, dict)],
        }
    else:
        ctx["current_wording"] = None
    return {k: v for k, v in ctx.items() if v not in ([], "")}


def user_message(label: str, chapter: int, chap_text: str, ctxs: list[dict[str, Any]], lang: str) -> str:
    ids = [c["id"] for c in ctxs]
    return (
        f"# Passage: {label} chapter {chapter}\n\n"
        f"## The whole chapter in the new English meaning-first POB (for context)\n\n{chap_text}\n\n"
        f"## Verses to translate into {LANGS[lang]['name']} now ({len(ids)}): {', '.join(ids)}\n\n"
        "```json\n" + json.dumps(ctxs, ensure_ascii=False, indent=1) + "\n```\n\n"
        f"Translate exactly these {len(ids)} verses, in order, using their exact ids."
    )


def call_model(system: str, user: str, *, deployment: str, effort: str, tier: str) -> dict[str, Any]:
    endpoint, key = base.azure_credentials()
    url = f"{endpoint}/openai/deployments/{deployment}/chat/completions?api-version={base.API_VERSION}"
    body: dict[str, Any] = {
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "max_completion_tokens": 64000, "reasoning_effort": effort,
        "response_format": {"type": "json_schema",
                            "json_schema": {"name": "pob_meaning_localize", "strict": True, "schema": OUTPUT_SCHEMA}},
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
                time.sleep(float(exc.headers.get("retry-after") or delay) + random.uniform(0, 3))
                delay = min(delay * 2, 240)
                continue
            raise RuntimeError(f"Azure HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt < 7:
                time.sleep(delay)
                delay = min(delay * 2, 240)
                continue
            raise
    raise RuntimeError("unreachable")


def cost(usage: dict[str, Any], tier: str) -> float:
    p = PRICES["flex" if tier == "flex" else "default"]
    prompt = int(usage.get("prompt_tokens") or 0)
    cached = int((usage.get("prompt_tokens_details") or {}).get("cached_tokens") or 0)
    out = int(usage.get("completion_tokens") or 0)
    return ((prompt - cached) * p["input"] + cached * p["cached"] + out * p["output"]) / 1e6


def plan_jobs(args: argparse.Namespace) -> list[dict[str, Any]]:
    units = [base.parse_passage(s) for s in args.passage or []]
    for b in args.book or []:
        bdir = base.book_dir(b)
        units += [(bdir, ch, None, None) for ch in base.book_chapters(bdir)]
    jobs = []
    for bdir, ch, first, last in units:
        files = base.chapter_files(bdir, ch)
        targets = [p for p in files if first is None or first <= base.verse_num(p) <= (last or first)]
        if not targets:
            continue
        ctxs = {p: verse_context(args.lang, p) for p in targets}
        chap = base.chapter_text(files)
        label = base.load_yaml(files[0]).get("reference", "").rsplit(" ", 1)[0] or bdir.name
        total = sum(len(json.dumps(ctxs[p], ensure_ascii=False)) for p in targets)
        n = max(1, -(-len(targets) // MAX_VERSES), -(-total // MAX_CHARS))
        size = -(-len(targets) // n)
        for i in range(0, len(targets), size):
            group = targets[i:i + size]
            out = (STATE / args.run / args.lang / bdir.relative_to(TRANSLATION)
                   / f"{ch:03d}_{base.verse_num(group[0]):03d}-{base.verse_num(group[-1]):03d}.json")
            jobs.append({"out": out, "label": label, "chapter": ch, "files": group,
                         "contexts": [ctxs[p] for p in group], "chapter_text": chap})
    return jobs


def run_job(job: dict[str, Any], args: argparse.Namespace, system: str) -> dict[str, Any]:
    out: pathlib.Path = job["out"]
    if out.exists() and not args.force and not json.loads(out.read_text()).get("missing"):
        return json.loads(out.read_text())
    ctxs, want = job["contexts"], [c["id"] for c in job["contexts"]]
    started, responses, got, note, filtered = time.time(), [], {}, "", []
    pending = list(ctxs)
    for _ in range(3):
        if not pending:
            break
        msg = user_message(job["label"], job["chapter"], job["chapter_text"], pending, args.lang)
        try:
            resp = call_model(system, msg, deployment=args.deployment, effort=args.effort, tier=args.tier)
        except RuntimeError as exc:
            if "content_filter" not in str(exc):
                raise
            filtered = [c["id"] for c in pending]
            break
        responses.append({"usage": resp.get("usage"), "model": resp.get("model"),
                          "service_tier": resp.get("service_tier")})
        try:
            parsed = json.loads(resp["choices"][0]["message"].get("content") or "{}")
        except json.JSONDecodeError:
            continue
        note = note or parsed.get("passage_note", "")
        for v in parsed.get("verses") or []:
            if v.get("id") in want and v.get("id") not in got and not base.validate_verse(v):
                got[v["id"]] = v
        pending = [c for c in ctxs if c["id"] not in got]
    result = {
        "run": args.run, "lang": args.lang, "prompt_id": PROMPT_ID, "prompt_sha256": base.sha256(system),
        "deployment": args.deployment, "model": responses[-1].get("model") if responses else None,
        "reasoning_effort": args.effort, "service_tier": args.tier, "timestamp": base.utc_now(),
        "seconds": round(time.time() - started, 1), "requests": responses,
        "estimated_cost_usd": round(sum(cost(r["usage"] or {}, args.tier) for r in responses), 5),
        "passage_note": note,
        "en_paths": [str(p.relative_to(ROOT)) for p in job["files"]],
        "paths": [str(target_path(args.lang, p).relative_to(ROOT)) for p in job["files"]],
        "verses": [got[i] for i in want if i in got],
        "missing": [i for i in want if i not in got and i not in filtered],
        "content_filtered": filtered,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, ensure_ascii=False, indent=1))
    tmp.replace(out)
    return result


def cmd_translate(args: argparse.Namespace) -> int:
    system = system_prompt(args.lang)
    jobs = plan_jobs(args)
    base.log(f"run={args.run} lang={args.lang} jobs={len(jobs)} verses={sum(len(j['files']) for j in jobs)} "
             f"deployment={args.deployment} effort={args.effort} tier={args.tier}")
    spent, failures = 0.0, 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futs = {pool.submit(run_job, j, args, system): j for j in jobs}
        for fut in concurrent.futures.as_completed(futs):
            j = futs[fut]
            try:
                r = fut.result()
                spent += r.get("estimated_cost_usd") or 0
                base.log(f"ok {j['out'].relative_to(STATE)} verses={len(r['verses'])} missing={len(r['missing'])} "
                         f"filtered={len(r['content_filtered'])} ${r.get('estimated_cost_usd')} {r.get('seconds')}s")
            except Exception as exc:  # rerun picks up failures
                failures += 1
                base.log(f"FAIL {j['out'].relative_to(STATE)}: {exc}")
    base.log(f"done: ~${spent:.3f}, failures={failures}")
    return 1 if failures else 0


def cmd_report(args: argparse.Namespace) -> int:
    rows = []
    for f in sorted((STATE / args.run / args.lang).rglob("*.json")):
        res = json.loads(f.read_text())
        by_id = {v["id"]: v for v in res.get("verses") or []}
        for en_rel, tgt_rel in zip(res["en_paths"], res["paths"]):
            en = base.load_yaml(ROOT / en_rel)
            tgt = base.load_yaml(ROOT / tgt_rel) if (ROOT / tgt_rel).exists() else {}
            new = by_id.get(en.get("id"))
            rows.append({
                "id": en.get("id"), "reference": en.get("reference"),
                "source": (en.get("source") or {}).get("text"),
                "english": (en.get("translation") or {}).get("text"),
                "english_notes": [[n.get("marker"), n.get("text")] for n in (en.get("translation") or {}).get("footnotes") or []],
                "current": (tgt.get("translation") or {}).get("text"),
                "current_notes": [[n.get("marker"), n.get("text")] for n in (tgt.get("translation") or {}).get("footnotes") or []],
                "new": new, "cost": res.get("estimated_cost_usd"), "model": res.get("model"),
            })
    out = STATE / f"{args.run}-{args.lang}-report.json"
    out.write_text(json.dumps({"run": args.run, "lang": args.lang, "rows": rows}, ensure_ascii=False, indent=1))
    print(len(rows), "rows", out)
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("translate")
    t.add_argument("--lang", required=True, choices=sorted(LANGS))
    t.add_argument("--run", required=True)
    t.add_argument("--passage", action="append")
    t.add_argument("--book", action="append")
    t.add_argument("--deployment", default=DEFAULT_DEPLOYMENT)
    t.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh"])
    t.add_argument("--tier", default="flex", choices=["default", "flex"])
    t.add_argument("--workers", type=int, default=6)
    t.add_argument("--force", action="store_true")
    t.set_defaults(func=cmd_translate)
    r = sub.add_parser("report")
    r.add_argument("--lang", required=True, choices=sorted(LANGS))
    r.add_argument("--run", required=True)
    r.set_defaults(func=cmd_report)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
