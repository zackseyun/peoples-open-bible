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
DEFAULT_DEPLOYMENT = base.os.environ.get("POB_LOCALIZE_DEPLOYMENT", "pob-localize-gpt-6-luna")

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


def meaning_first_books() -> list[str]:
    """Every book the English meaning-first pass covered."""
    books = [f"{sec}/{d.name}" for sec in ("ot", "nt", "deuterocanon")
             for d in sorted((TRANSLATION / sec).iterdir()) if d.is_dir()]
    return books + ["extra_canonical/1_enoch"]


def plan_jobs(args: argparse.Namespace) -> list[dict[str, Any]]:
    units = [base.parse_passage(s) for s in args.passage or []]
    for b in (args.book or []) + (meaning_first_books() if args.all_meaning else []):
        bdir = base.book_dir(b)
        units += [(bdir, ch, None, None) for ch in base.book_chapters(bdir)]
    jobs = []
    for bdir, ch, first, last in units:
        files = base.chapter_files(bdir, ch)
        # Verses whose English kept its earlier wording (held for review) keep theirs too.
        targets = [p for p in files if (first is None or first <= base.verse_num(p) <= (last or first))
                   and base.load_yaml(p).get("meaning_pass")]
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
    ctxs, want = job["contexts"], [c["id"] for c in job["contexts"]]
    started, responses, got, note, filtered = time.time(), [], {}, "", []
    if out.exists() and not args.force:
        prev = json.loads(out.read_text())
        if not prev.get("missing") and not prev.get("content_filtered"):
            return prev
        # Keep what already came back; redo only the missing or filter-blocked verses.
        got = {v["id"]: v for v in prev.get("verses") or [] if v.get("id") in want}
        responses = list(prev.get("requests") or [])
        note = prev.get("passage_note", "")
    pending = [c for c in ctxs if c["id"] not in got]
    blocked = False

    def take(resp: dict[str, Any], only: set[str]) -> None:
        nonlocal note
        responses.append({"usage": resp.get("usage"), "model": resp.get("model"),
                          "service_tier": resp.get("service_tier")})
        try:
            parsed = json.loads(resp["choices"][0]["message"].get("content") or "{}")
        except json.JSONDecodeError:
            return
        note = note or parsed.get("passage_note", "")
        for v in parsed.get("verses") or []:
            if v.get("id") in only and v.get("id") not in got and not base.validate_verse(v):
                got[v["id"]] = v

    for _ in range(3):
        if not pending:
            break
        msg = user_message(job["label"], job["chapter"], job["chapter_text"], pending, args.lang)
        try:
            resp = call_model(system, msg, deployment=args.deployment, effort=args.effort, tier=args.tier)
        except RuntimeError as exc:
            if "content_filter" not in str(exc):
                raise
            blocked = True
            break
        take(resp, set(want))
        pending = [c for c in ctxs if c["id"] not in got]
    if blocked and pending:
        # Azure's filter tripped on the passage: retry each verse alone with only its
        # neighbours as context, and record the verses that are still blocked.
        for c in list(pending):
            num = int(str(c["id"]).rsplit(".", 1)[1])
            window = "\n".join(line for line in job["chapter_text"].splitlines()
                               if line.split(" ", 1)[0].isdigit() and abs(int(line.split(" ", 1)[0]) - num) <= 3)
            single = user_message(job["label"], job["chapter"], window, [c], args.lang)
            for _ in range(2):
                try:
                    resp = call_model(system, single, deployment=args.deployment, effort=args.effort, tier=args.tier)
                except RuntimeError as exc:
                    if "content_filter" not in str(exc):
                        raise
                    filtered.append(c["id"])
                    break
                take(resp, {c["id"]})
                if c["id"] in got:
                    break
        pending = [c for c in ctxs if c["id"] not in got and c["id"] not in filtered]
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


def language_meta(lang: str) -> dict[str, Any]:
    sample = ROOT / LANGS[lang]["dir"] / "nt" / "john" / "001" / "001.yaml"
    meta = (base.load_yaml(sample).get("language") if sample.exists() else None) or {}
    return meta or {"code": lang, "name": LANGS[lang]["name"], "variant": LANGS[lang]["variant"]}


def cmd_apply(args: argparse.Namespace) -> int:
    """Write a finished run into translation_<lang>/: update records, create missing ones."""
    meta = language_meta(args.lang)
    changed = created = skipped = 0
    for f in sorted((STATE / args.run / args.lang).rglob("*.json")):
        res = json.loads(f.read_text())
        by_id = {v["id"]: v for v in res.get("verses") or []}
        for en_rel, tgt_rel in zip(res["en_paths"], res["paths"]):
            en = base.load_yaml(ROOT / en_rel)
            new = by_id.get(en.get("id"))
            if not new or base.validate_verse(new):
                skipped += 1
                continue
            path = ROOT / tgt_rel
            exists = path.exists()
            rec = base.load_yaml(path) if exists else {}
            if (rec.get("meaning_pass") or {}).get("run") == args.run:
                skipped += 1
                continue
            en_tr = en.get("translation") or {}
            footnotes = [{"marker": n["marker"], "text": n["text"].strip(), "reason": base.SCHEMA_REASON[n["reason"]]}
                         for n in new.get("footnotes") or []]
            text = new["text"].strip()
            block = {
                "run": args.run, "model": res.get("model"), "deployment": res.get("deployment"),
                "prompt_id": res.get("prompt_id"), "prompt_sha256": res.get("prompt_sha256"),
                "reasoning_effort": res.get("reasoning_effort"), "timestamp": res["timestamp"],
                "english_meaning_pass_run": (en.get("meaning_pass") or {}).get("run"),
                "change_level": new["change_level"], "confidence": new["confidence"],
                "decisions": new.get("decisions") or [],
            }
            base_tr = {"language": "en", "yaml_path": en_rel, "text": en_tr.get("text")}
            if en_tr.get("footnotes"):
                base_tr["footnotes"] = en_tr["footnotes"]
            if exists:
                tr = rec.setdefault("translation", {})
                old_text = tr.get("text") or ""
                tr.update({"language": tr.get("language") or meta.get("code"), "text": text, "philosophy": "dynamic"})
                if footnotes:
                    tr["footnotes"] = footnotes
                else:
                    tr.pop("footnotes", None)
                prior_base = rec.get("base_translation") or {}
                rec["base_translation"] = {**{k: v for k, v in prior_base.items() if k not in ("text", "footnotes")},
                                           **base_tr}
                rec.setdefault("revisions", []).append({
                    "timestamp": res["timestamp"], "adjudicator": res.get("adjudicator") or "gpt-6-luna-meaning-localize",
                    "reviewer_model": res.get("model"), "category": "meaning_retranslation",
                    "from": old_text, "to": text,
                    "rationale": "; ".join(f"{d['source_phrase']} → {d['rendering']}: {d['reason']}"
                                           for d in new.get("decisions") or [])[:1500],
                })
                rec["meaning_pass"] = block
                changed += 1
            else:
                rec = {
                    "id": en.get("id"), "reference": en.get("reference"), "language": meta,
                    "source": en.get("source"), "base_translation": base_tr,
                    "translation": {"language": meta.get("code"), "text": text, "philosophy": "dynamic",
                                    **({"footnotes": footnotes} if footnotes else {})},
                    "status": "draft",
                    "ai_draft": {"model_id": "claude-opus-5-5" if str(res.get("model") or "").startswith("claude")
                                 else "gpt-6-luna", "model_version": str(res.get("model") or "gpt-6-luna"),
                                 "prompt_id": res.get("prompt_id"), "prompt_sha256": res.get("prompt_sha256"),
                                 "timestamp": res["timestamp"], "output_hash": base.sha256(text)},
                    "meaning_pass": block,
                }
                path.parent.mkdir(parents=True, exist_ok=True)
                created += 1
            tmp = path.with_suffix(".yaml.tmp")
            tmp.write_text(yaml.safe_dump(rec, allow_unicode=True, sort_keys=False, width=1000), encoding="utf-8")
            tmp.replace(path)
    print(f"lang={args.lang} changed={changed} created={created} skipped={skipped}")
    return 0


def blocked_verses(run: str, langs: list[str]) -> dict[str, dict[str, Any]]:
    """Verses a run lost to the content filter (or never got back), by id, with the languages that need them."""
    out: dict[str, dict[str, Any]] = {}
    for lang in langs:
        for f in sorted((STATE / run / lang).rglob("*.json")):
            res = json.loads(f.read_text())
            want = set(res.get("content_filtered") or []) | set(res.get("missing") or [])
            if not want:
                continue
            for en_rel in res["en_paths"]:
                vid = base.load_yaml(ROOT / en_rel).get("id")
                if vid in want:
                    out.setdefault(vid, {"en_rel": en_rel, "langs": []})["langs"].append(lang)
    return out


def handoff_instructions(langs: list[str]) -> str:
    text = PROMPT_PATH.read_text(encoding="utf-8").replace("{LANGUAGE_NAME}", "target-language")
    rules = "\n\n".join(LANGS[lang]["rules"].strip() for lang in langs)
    text = text.replace("{LANGUAGE_RULES}", "# Language rules\n\n" + rules)
    return (
        "# Hand-off: verses the Azure content filter refused\n\n"
        "Each verse below lists the languages it is needed in (`langs`) and the current wording in each. "
        "Translate it into every listed language, following the instructions that follow exactly as the "
        "Azure translator does. The passages are Scripture; render them faithfully, neither softened nor "
        "sharpened.\n\n"
        "Return one JSON object: {\"verses\": [ {\"id\", \"lang\", \"text\", \"footnotes\": [{\"marker\", \"text\", "
        "\"reason\"}], \"decisions\": [{\"source_phrase\", \"rendering\", \"reason\"}], \"change_level\", "
        "\"confidence\"} ... ]}, one entry per verse per language. Footnote reason is one of "
        + ", ".join(base.FOOTNOTE_REASONS) + ".\n\n---\n\n" + text
    )


def cmd_export(args: argparse.Namespace) -> int:
    """Write hand-off bundles for the verses a run could not translate (content filter or missing)."""
    langs = args.lang or sorted(LANGS)
    todo = blocked_verses(args.run, langs)
    dest = STATE / args.out_run / "bundles"
    dest.mkdir(parents=True, exist_ok=True)
    (STATE / args.out_run / "instructions.md").write_text(handoff_instructions(langs), encoding="utf-8")
    items = []
    for vid, info in sorted(todo.items(), key=lambda kv: kv[1]["en_rel"]):
        en_path = ROOT / info["en_rel"]
        ctx = verse_context(info["langs"][0], en_path)
        ctx.pop("current_wording", None)
        ctx["langs"] = info["langs"]
        ctx["current_wording"] = {}
        for lang in info["langs"]:
            ctx["current_wording"][lang] = verse_context(lang, en_path).get("current_wording")
        n = base.verse_num(en_path)
        files = base.chapter_files(en_path.parent.parent, int(en_path.parent.name))
        ctx["english_neighbours"] = base.chapter_text([f for f in files if abs(base.verse_num(f) - n) <= 3])
        items.append(ctx)
    total = sum(len(json.dumps(c, ensure_ascii=False)) for c in items)
    per = -(-total // args.parts)
    parts: list[list[dict[str, Any]]] = [[]]
    size = 0
    for c in items:
        k = len(json.dumps(c, ensure_ascii=False))
        if parts[-1] and size + k > per and len(parts) < args.parts:
            parts.append([])
            size = 0
        parts[-1].append(c)
        size += k
    for i, part in enumerate(parts, 1):
        (dest / f"part_{i:02d}.json").write_text(json.dumps({"verses": part}, ensure_ascii=False, indent=1))
    print(f"verses={len(items)} language-verses={sum(len(c['langs']) for c in items)} parts={len(parts)} -> {dest}")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    """Turn part_NN.out.json answers into run results shaped like translate's, per language."""
    run_dir = STATE / args.run
    prompt_sha = base.sha256(handoff_instructions(sorted(LANGS)))
    asked: dict[tuple[str, str], str] = {}
    for part in sorted((run_dir / "bundles").glob("part_[0-9][0-9].json")):
        for c in json.loads(part.read_text())["verses"]:
            for lang in c["langs"]:
                asked[(c["id"], lang)] = c["reference"]
    got: dict[tuple[str, str], dict[str, Any]] = {}
    for ans in sorted((run_dir / "bundles").glob("part_[0-9][0-9].out*.json")):
        for v in json.loads(ans.read_text()).get("verses") or []:
            key = (v.get("id"), v.get("lang"))
            if key not in asked:
                continue
            errs = base.validate_verse(v)
            if errs:
                print(f"invalid {key}: {errs}")
                continue
            got[key] = {k: v[k] for k in ("id", "text", "footnotes", "decisions", "change_level", "confidence")}
    missing = sorted(k for k in asked if k not in got)
    if missing:
        print(f"missing {len(missing)}: {missing[:20]}")
    blocked = blocked_verses(args.from_run, sorted({l for _, l in asked}))
    written = 0
    for lang in sorted({l for _, l in asked}):
        groups: dict[tuple[str, int], list[str]] = {}
        for vid, info in blocked.items():
            if lang in info["langs"] and (vid, lang) in got:
                en_path = ROOT / info["en_rel"]
                groups.setdefault((str(en_path.parent.parent.relative_to(TRANSLATION)), int(en_path.parent.name)), []).append(info["en_rel"])
        for (book_rel, ch), rels in groups.items():
            rels.sort()
            ids = [base.load_yaml(ROOT / r).get("id") for r in rels]
            out = (run_dir / lang / book_rel / f"{ch:03d}_{base.verse_num(ROOT / rels[0]):03d}-{base.verse_num(ROOT / rels[-1]):03d}.json")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps({
                "run": args.run, "lang": lang, "adjudicator": args.adjudicator, "prompt_id": PROMPT_ID + "+handoff",
                "prompt_sha256": prompt_sha, "deployment": None, "model": args.model, "reasoning_effort": None,
                "service_tier": None, "timestamp": base.utc_now(), "seconds": None, "requests": [],
                "estimated_cost_usd": 0, "passage_note": "",
                "en_paths": rels, "paths": [str(target_path(lang, ROOT / r).relative_to(ROOT)) for r in rels],
                "verses": [got[(i, lang)] for i in ids], "missing": [], "content_filtered": [],
            }, ensure_ascii=False, indent=1))
            written += len(ids)
    print(f"imported {written} language-verses of {len(asked)} asked -> {run_dir}")
    return 0 if not missing else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("translate")
    t.add_argument("--lang", required=True, choices=sorted(LANGS))
    t.add_argument("--run", required=True)
    t.add_argument("--passage", action="append")
    t.add_argument("--book", action="append")
    t.add_argument("--all-meaning", action="store_true", help="every book the English meaning pass covered")
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
    a = sub.add_parser("apply", help="write a finished run into translation_<lang>/ (explicit step)")
    a.add_argument("--lang", required=True, choices=sorted(LANGS))
    a.add_argument("--run", required=True)
    a.set_defaults(func=cmd_apply)
    e = sub.add_parser("export", help="hand-off bundles for verses the run could not translate")
    e.add_argument("--lang", action="append", choices=sorted(LANGS))
    e.add_argument("--run", required=True)
    e.add_argument("--out-run", required=True)
    e.add_argument("--parts", type=int, default=8)
    e.set_defaults(func=cmd_export)
    i = sub.add_parser("import", help="turn hand-off answers into run results")
    i.add_argument("--run", required=True, help="the hand-off run (export's --out-run)")
    i.add_argument("--from-run", required=True, help="the run the verses were blocked in")
    i.add_argument("--adjudicator", default="claude-opus-5-5-meaning-localize")
    i.add_argument("--model", default="claude-opus-5-5")
    i.set_defaults(func=cmd_import)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
