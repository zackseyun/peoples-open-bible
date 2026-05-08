#!/usr/bin/env python3
"""claude_es_review_subagent_helper.py — companion to in-session subagents
that source-grounded-review existing Spanish POB records.

Usage (subagent-side, per verse):
  python3 tools/claude_es_review_subagent_helper.py <<'JSONEOF'
  {"en_path": "translation/extra_canonical/.../001.yaml",
   "verdict": "approve|revise|reject",
   "source_alignment_summary": "...",
   "spanish_quality_summary": "...",
   "glossary_alignment": "...",
   "issues": [...],
   "revised_spanish_text": "...",
   "revised_footnotes": [...],
   "revision_rationale": "...",
   "requires_gpt54_adjudication": false}
  JSONEOF

The helper updates translation_es/<path>.yaml in place, mirroring what
spanish_pipeline.py review --apply-revisions does:
  - if verdict == "revise" and the revision validates, apply it (translation
    text + footnotes), append to record.revisions[], set status to
    spanish_reviewed
  - if verdict == "approve", set status to spanish_reviewed without edits
  - else set status to spanish_needs_revision (or _needs_adjudication when
    requires_gpt54_adjudication)
  - always write the review_pass block with model_id=claude-sonnet-4-6 (or
    overridden via CARTHA_CLAUDE_REVIEW_MODEL env)
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools"))

import spanish_pipeline as sp  # type: ignore

PROMPT_ID = "spanish_source_review_claude_subagent_v1"
MODEL_ID = os.environ.get("CARTHA_CLAUDE_REVIEW_MODEL", "claude-sonnet-4-6")


def normalize_en_path(raw: str) -> pathlib.Path:
    p = pathlib.Path(raw.strip())
    if p.is_absolute():
        p = p.relative_to(REPO_ROOT)
    s = str(p).replace("translation_es/", "translation/", 1)
    if not s.startswith("translation/"):
        raise ValueError(f"{raw!r}: not under translation/")
    return REPO_ROOT / s


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

    en_raw = payload.pop("en_path", None)
    if not en_raw:
        print("ERROR missing en_path", file=sys.stderr)
        return 2
    try:
        en_path = normalize_en_path(en_raw)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR en_path: {exc}", file=sys.stderr)
        return 2

    target = sp.SPANISH_ROOT / en_path.relative_to(sp.TRANSLATION_ROOT)
    if not target.exists():
        print(f"ERROR target_missing {target.relative_to(REPO_ROOT)}", file=sys.stderr)
        return 2

    try:
        spanish_record = sp.safe_load_yaml(target)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR read_es: {exc}", file=sys.stderr)
        return 2

    if spanish_record.get("review_pass"):
        print(f"SKIP_ALREADY_REVIEWED {target.relative_to(REPO_ROOT)}")
        return 0

    required = {
        "verdict",
        "source_alignment_summary",
        "spanish_quality_summary",
        "glossary_alignment",
        "issues",
        "revised_spanish_text",
        "revised_footnotes",
        "revision_rationale",
        "requires_gpt54_adjudication",
    }
    missing = required - set(payload.keys())
    if missing:
        print(f"ERROR missing fields: {sorted(missing)}", file=sys.stderr)
        return 2

    translation_obj = dict(spanish_record.get("translation") or spanish_record.get("spanish_translation") or {})
    old_text = str(translation_obj.get("text") or "").strip()

    revised = str(payload.get("revised_spanish_text") or "").strip()
    revised_footnotes = payload.get("revised_footnotes") or []
    apply_revision = (
        payload.get("verdict") == "revise"
        and revised
        and revised != old_text
        and not bool(payload.get("requires_gpt54_adjudication"))
    )

    auto_apply_blocked_errors: list[str] = []
    if apply_revision:
        candidate = dict(spanish_record)
        candidate_translation = dict(translation_obj)
        candidate_translation["text"] = revised
        if revised_footnotes:
            candidate_translation["footnotes"] = revised_footnotes
        else:
            candidate_translation.pop("footnotes", None)
        candidate["translation"] = candidate_translation
        temp_validate = target.with_suffix(target.suffix + ".review-candidate")
        sp.write_yaml_atomic(temp_validate, candidate)
        auto_apply_blocked_errors = sp.validate_spanish_record(temp_validate)
        temp_validate.unlink(missing_ok=True)
        if auto_apply_blocked_errors:
            apply_revision = False

    if apply_revision:
        spanish_record.setdefault("revisions", []).append(
            {
                "from": old_text,
                "to": revised,
                "rationale": payload.get("revision_rationale") or payload.get("source_alignment_summary"),
                "reviewer_model": MODEL_ID,
                "timestamp": sp.utc_now(),
            }
        )
        translation_obj["text"] = revised
        if revised_footnotes:
            translation_obj["footnotes"] = revised_footnotes
        else:
            translation_obj.pop("footnotes", None)
        spanish_record["translation"] = translation_obj
        spanish_record["status"] = "spanish_reviewed"
    elif payload.get("verdict") == "approve":
        spanish_record["status"] = "spanish_reviewed"
    else:
        spanish_record["status"] = (
            "spanish_needs_adjudication"
            if payload.get("requires_gpt54_adjudication")
            else "spanish_needs_revision"
        )

    raw_args = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    review_pass_block = sp.prune_empty(
        {
            **payload,
            "model_id": MODEL_ID,
            "model_version": MODEL_ID,
            "azure_deployment": "claude_code_subagent",
            "prompt_id": PROMPT_ID,
            "prompt_sha256": sp.sha256_text(raw_args),
            "timestamp": sp.utc_now(),
            "output_hash": sp.sha256_text(raw_args),
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "reasoning_tokens": 0,
                "estimated_cost_usd": 0.0,
                "billed_to": "claude_code_max_session",
            },
            "applied_revision": apply_revision,
            "auto_apply_blocked_errors": auto_apply_blocked_errors,
            "provider": "anthropic_claude_code_subagent",
            "fallback_reason": "azure_review_alternate_path",
        }
    )
    spanish_record["review_pass"] = review_pass_block

    sp.write_yaml_atomic(target, spanish_record)
    errs = sp.validate_spanish_record(target)
    if errs:
        invalid = target.with_suffix(target.suffix + f".review-invalid-{int(time.time())}")
        # Don't replace the original — but keep a copy for diagnosis
        import shutil
        shutil.copy2(target, invalid)
        print(f"ERROR validation: {errs}", file=sys.stderr)
        return 1
    print(f"OK reviewed {target.relative_to(REPO_ROOT)} verdict={payload.get('verdict')} applied={apply_revision}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
