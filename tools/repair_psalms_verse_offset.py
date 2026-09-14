#!/usr/bin/env python3
"""repair_psalms_verse_offset.py — repair the Psalms superscription verse offset
in the Korean and Spanish editions.

BACKGROUND

`translation_ko` and `translation_es` were drafted while the English tree was
mid-migration to storing a Psalm's superscription as verse 0: at that moment the
English chapter carried the superscription *twice*, at `000` and at `001`, and
the psalm body at `002..N`. Both editions were drafted straight off that tree, so
every chapter with a superscription (63 of them) came out with one record too
many: two renderings of the superscription, and the body shifted one slot late.
Those 63 chapters are exactly the ones whose record count exceeds the English.

The two editions then diverged, and they need different repairs:

* `translation_es` was never touched again. Its records still sit exactly as
  drafted — `source.text`, `base_translation` and the rendering all describe the
  verse one slot earlier than the path claims. So it needs a true shift.

* `translation_ko` was largely repaired in place on 2026-07-13 by a
  `gpt-5.6-terra` pass that re-translated each record *against its path* and
  pushed the offset draft into `revisions[].from`. It left `source.text` stale,
  and it skipped some records. So most Korean records already hold the right
  verse and only need their source relabelled — but wherever the pass skipped a
  record, the verse the pass overwrote at the *next* path was lost from the live
  tree and survives only in that record's revision history.

Because of this the repair cannot be a blind shift: shifting Korean would
re-break the chapters the July pass already fixed. Nor can records be moved by
`source.text` the way `realign_by_source.py` does, because for Korean the source
label is the stale part and the rendering is the corrected part.

EVIDENCE MODEL (per record, all deterministic)

    drafted   the English verse this record was drafted from, found by matching
              its `source.text` against the English record carrying the same
              Hebrew. `source.text` was never rewritten, so it still names the
              verse the draft rendered.
    realigned whether a revision replaced the rendering wholesale — a revision
              whose `to` is the current text and whose `from` is a different
              verse's rendering rather than a copy-edit of the same one. Copy
              edits and verse replacements separate cleanly on similarity
              (Korean replacements cluster at <=0.5, Spanish copy edits at
              >=0.6), so REALIGN_MAX sits between them.
    content   which verse the record's *live* rendering translates: its own path
              if a realignment rewrote it against that path, else `drafted`.

From `content` the chapter's coverage follows: which English verses have a live
rendering, which have two, and which have none. A verse with none is recovered
from the `revisions[].from` of the realigned record that was drafted from it —
that string is the rendering the July pass discarded. Its footnote *definitions*
did not survive (the record's footnote array describes the replacement), so the
recovered text has its now-undefined markers stripped and the record is left at
`needs_human_review` for a footnote pass. The full original string is kept
verbatim in the new revisions entry, so nothing is discarded silently.

A surplus record is only ever dropped when the verse it renders already has a
keeper elsewhere in the chapter, and its rendering is preserved in that keeper's
revisions entry.

    python3 tools/repair_psalms_verse_offset.py report --edition translation_ko
    python3 tools/repair_psalms_verse_offset.py plan   --edition translation_ko --chapter 084
    python3 tools/repair_psalms_verse_offset.py apply  --edition translation_ko --all
"""
from __future__ import annotations

import argparse
import collections
import difflib
import pathlib
import re
import sys

import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
HEBREW_ONLY = re.compile(r"[^א-ת]")
MARKER = re.compile(r"\[[a-z]\]")

# A revision whose from/to similarity is below this replaced the verse; above it
# the revision is a copy edit of the same verse. See module docstring.
REALIGN_MAX = 0.55

BOOK = "ot/psalms"

# Chapters where the Hebrew superscription itself is split across records, so a
# record's source is a fragment of the English verse rather than the whole of it.
# Handled by the substring fallback in `verse_of_source`; listed here so `report`
# can call them out rather than leaving them looking like unmatched records.
SPLIT_SUPERSCRIPTION = {"060"}


def norm_source(text: str) -> str:
    """Consonantal skeleton — vowel points and cantillation differ per edition."""
    return HEBREW_ONLY.sub("", text or "")


def load(path: pathlib.Path) -> dict:
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError(f"{path}: not a YAML mapping")
    return doc


def dump(path: pathlib.Path, doc: dict) -> None:
    path.write_text(
        yaml.dump(doc, allow_unicode=True, sort_keys=False, width=10**9), encoding="utf-8"
    )


def text_of(doc: dict) -> str:
    return str((doc.get("translation") or {}).get("text") or "")


class Chapter:
    """One chapter of one edition, paired with the English chapter."""

    # Spanish records were never re-filed, so their position carries the offset
    # and `source.text` is only a cross-check. Korean records were re-filed in
    # place by the July 2026 pass, so position means the opposite there.
    MODES = {"translation_es": "shift", "translation_ko": "in_place"}

    def __init__(self, edition: str, chapter: str):
        self.edition = edition
        self.chapter = chapter
        self.mode = self.MODES.get(edition, "in_place")
        en_dir = REPO_ROOT / "translation" / BOOK / chapter
        ed_dir = REPO_ROOT / edition / BOOK / chapter
        self.en = {p.stem: load(p) for p in sorted(en_dir.glob("*.yaml"))}
        self.recs = {p.stem: load(p) for p in sorted(ed_dir.glob("*.yaml"))}
        self.ed_dir = ed_dir
        self.ambiguous: dict[str, tuple[list[str], str]] = {}
        self._src_index: dict[str, list[str]] = collections.defaultdict(list)
        for verse, doc in self.en.items():
            self._src_index[norm_source((doc.get("source") or {}).get("text", ""))].append(verse)

    def verse_of_source(self, raw: str, path: str | None = None) -> str | None:
        """Which English verse carries this Hebrew. None if not resolvable.

        A psalm with a refrain repeats a verse's Hebrew verbatim (Ps 46:7 and
        46:11, Ps 42:5 and 42:11), so an exact match can name two verses. The
        offset being repaired is one or two slots, never the distance between a
        refrain's occurrences, so the candidate nearest the record's own path is
        the one it was drafted from. `ambiguous` records which records needed
        this so `report` can surface them.
        """
        key = norm_source(raw)
        if not key:
            return None
        exact = self._src_index.get(key) or []
        if len(exact) == 1:
            return exact[0]
        if exact:
            if path is None:
                return None
            best = min(exact, key=lambda v: (abs(int(v) - int(path)), int(v)))
            self.ambiguous[path] = (sorted(exact), best)
            return best
        # The superscription is split across records in a few chapters, so the
        # record's source is a fragment of the English verse's source.
        hits = [v for k, vs in self._src_index.items() for v in vs if k and key in k]
        return hits[0] if len(set(hits)) == 1 else None

    def realignment(self, doc: dict) -> str | None:
        """The rendering a realigning revision replaced, or None if none did."""
        current = text_of(doc)
        for rev in doc.get("revisions") or []:
            was, now = rev.get("from"), rev.get("to")
            if not isinstance(was, str) or not isinstance(now, str):
                continue
            if now != current:
                continue
            if difflib.SequenceMatcher(None, was, now).ratio() < REALIGN_MAX:
                return was
        return None

    def superscription_run(self, ev: dict[str, dict]) -> int:
        """How many leading records render the superscription (English verse 0).

        Both editions were drafted off an English tree that carried the
        superscription at both `000` and `001`, so this is normally 2. Where the
        Hebrew superscription is itself split across records it is longer.
        """
        run = 0
        for path in sorted(self.recs):
            if ev[path]["drafted"] != "000":
                break
            run += 1
        return run

    def evidence(self) -> dict[str, dict]:
        out = {}
        for path, doc in self.recs.items():
            replaced = self.realignment(doc)
            drafted = self.verse_of_source((doc.get("source") or {}).get("text", ""), path)
            out[path] = {
                "drafted": drafted,
                "realigned": replaced is not None,
                "replaced_text": replaced,
                "content": path if replaced is not None else drafted,
            }
        return out


def build_plan(ch: Chapter) -> dict:
    """Decide, for every English verse, which rendering ends up at its path."""
    ev = ch.evidence()
    if ch.mode == "shift":
        return plan_shift(ch, ev)
    return plan_in_place(ch, ev)


def plan_shift(ch: Chapter, ev: dict[str, dict]) -> dict:
    """Spanish: the whole body sits one slot late, so re-file it by position.

    Position is the evidence here, not `source.text`: nothing has re-filed these
    records since they were drafted, so record *p* renders the verse *p* slots
    after the superscription run. `source.text` agrees on 1116 of 1118 records
    and is reported as a cross-check rather than used to place anything.
    """
    problems: list[str] = []
    run = ch.superscription_run(ev)
    if not 1 <= run <= 3:
        return {"assign": {}, "surplus": [], "evidence": ev, "mismatched": [],
                "problems": [f"superscription run is {run} record(s); expected 1-3"]}

    assign: dict[str, dict] = {"000": {"kind": "keep", "from": "000"}}
    surplus = [p for p in sorted(ch.recs) if int(p) < run and p != "000"]
    mismatched: list[str] = []
    for path in sorted(ch.recs):
        if int(path) < run:
            continue
        verse = f"{int(path) - run + 1:03d}"
        if verse not in ch.en:
            problems.append(f"record {path} would land at {verse}, which has no English verse")
            continue
        if verse in assign:
            problems.append(f"verse {verse} claimed twice")
            continue
        if ev[path]["drafted"] not in (verse, None):
            mismatched.append(f"{path}: source names {ev[path]['drafted']}, position gives {verse}")
        if ev[path]["realigned"]:
            # A revision replaced this record's rendering with the next verse's,
            # so the rendering for `verse` survives only in that revision.
            assign[verse] = {"kind": "recover_here", "from": path}
        else:
            assign[verse] = {"kind": "keep" if path == verse else "move", "from": path}

    missing = sorted(set(ch.en) - set(assign))
    if missing:
        problems.append(f"no record lands at verse(s) {', '.join(missing)}")
    return {"assign": assign, "surplus": surplus, "evidence": ev,
            "mismatched": mismatched, "problems": problems}


def plan_in_place(ch: Chapter, ev: dict[str, dict]) -> dict:
    """Korean: most records already hold the right verse; fill what was lost."""
    problems: list[str] = []
    holders: dict[str, list[str]] = collections.defaultdict(list)
    for path, e in ev.items():
        if e["content"] is not None:
            holders[e["content"]].append(path)

    assign: dict[str, dict] = {}
    for verse in sorted(ch.en):
        cands = sorted(holders.get(verse, []))
        if verse in cands:
            assign[verse] = {"kind": "keep", "from": verse}
        elif cands:
            assign[verse] = {"kind": "move", "from": cands[0]}
        else:
            donors = sorted(p for p, e in ev.items() if e["realigned"] and e["drafted"] == verse)
            if len(donors) != 1:
                problems.append(
                    f"verse {verse}: no live rendering and "
                    f"{len(donors)} recovery donor(s) — cannot repair automatically"
                )
                continue
            assign[verse] = {"kind": "recover_donor", "from": donors[0]}

    used_as_keeper = {a["from"] for a in assign.values() if a["kind"] in ("keep", "move")}
    # A recovery donor keeps its own slot; it only lends its discarded rendering.
    donor_paths = {a["from"] for a in assign.values() if a["kind"] == "recover_donor"}
    surplus = sorted(set(ch.recs) - used_as_keeper - donor_paths)
    # A donor that is itself surplus would be dropped after being read, which is
    # fine, but a donor that is also a keeper elsewhere must not be deleted.
    surplus = [p for p in surplus if p not in donor_paths]

    for path in surplus:
        content = ev[path]["content"]
        if content is None:
            problems.append(f"record {path}: unidentifiable content, refusing to drop it")
        elif content not in assign:
            problems.append(f"record {path}: renders verse {content}, which nothing keeps")

    final_count = len(assign)
    if final_count != len(ch.en) and not problems:
        problems.append(f"final count {final_count} != English {len(ch.en)}")

    return {"assign": assign, "surplus": surplus, "evidence": ev,
            "mismatched": [], "problems": problems}


def rationale(edition: str, kind: str, origin: str, verse: str, chapter: str) -> str:
    ref = f"시편 {int(chapter)}:{int(verse)}" if edition.endswith("ko") else f"Salmo {int(chapter)}:{int(verse)}"
    if edition.endswith("_ko"):
        if kind == "move":
            return (
                f"이 편의 표제를 절 0으로 옮기는 재번호 작업 이전에 초안이 작성되어, 이 장의 기록이 "
                f"영어 본문보다 하나씩 밀려 있었습니다. 이 기록의 번역문은 {ref}에 해당하므로 "
                f"{origin}에서 이 경로로 다시 배치했습니다. 번역문 자체는 변경하지 않았습니다."
            )
        if kind == "recover":
            return (
                f"{ref}의 번역문이 2026-07-13 재정렬 과정에서 다음 절의 번역문으로 덮어써져 "
                f"본문에서 사라졌습니다. {origin}의 개정 이력에 남아 있던 원래 번역문을 이 경로에 "
                f"복원했습니다. 각주 정의는 이력에 남아 있지 않아 정의가 없는 각주 표시는 제거했으며, "
                f"각주 재작업을 위해 상태를 needs_human_review로 두었습니다."
            )
        return (
            f"이 장에 {ref}의 번역문이 두 개 있었습니다. 이 경로의 번역문을 정본으로 두고, "
            f"중복된 기록은 제거했습니다. 제거된 번역문은 아래에 함께 기록해 두었습니다."
        )
    if kind == "move":
        return (
            f"El borrador se hizo antes de la renumeración que traslada el encabezamiento del salmo "
            f"al versículo 0, de modo que los registros de este capítulo quedaron desplazados un "
            f"lugar respecto del inglés. La traducción de este registro corresponde a {ref}, así que "
            f"se reubicó aquí desde {origin}. El texto de la traducción no se modificó."
        )
    if kind == "recover":
        return (
            f"La traducción de {ref} había sido sobrescrita por la del versículo siguiente y ya no "
            f"figuraba en el texto. Se restauró aquí la traducción original conservada en el "
            f"historial de revisiones de {origin}. Las definiciones de las notas no se conservaron, "
            f"así que se quitaron los marcadores sin definición y el registro queda en "
            f"needs_human_review para una pasada de notas."
        )
    return (
        f"Este capítulo tenía dos traducciones de {ref}. Se conserva como texto principal la de esta "
        f"ruta y se eliminó el registro duplicado, cuya traducción queda registrada abajo."
    )


def add_revision(doc: dict, *, was: str, now: str, why: str, timestamp: str) -> None:
    doc.setdefault("revisions", [])
    if not isinstance(doc["revisions"], list):
        doc["revisions"] = []
    doc["revisions"].insert(0, {
        "from": was,
        "to": now,
        "category": "verse_boundary_redraft",
        "rationale": why,
        "adjudicator": "claude-opus-5-psalms-verse-offset",
        "reviewer_model": "claude-opus-5",
        "timestamp": timestamp,
    })


def relabel(doc: dict, en_doc: dict, chapter: str, verse: str, edition: str) -> None:
    """Point a record's identity and source metadata at the verse it now holds."""
    doc["id"] = f"PSA.{int(chapter)}.{int(verse)}"
    doc["reference"] = f"Psalms {int(chapter)}:{int(verse)}"
    en_source = en_doc.get("source") or {}
    source = doc.setdefault("source", {})
    source["edition"] = en_source.get("edition", source.get("edition", "WLC"))
    source["text"] = en_source.get("text", "")
    en_tr = en_doc.get("translation") or {}
    base = doc.setdefault("base_translation", {})
    base["language"] = "en"
    base["yaml_path"] = f"translation/{BOOK}/{chapter}/{verse}.yaml"
    base["text"] = en_tr.get("text", "")
    if en_tr.get("footnotes"):
        base["footnotes"] = en_tr["footnotes"]
    else:
        base.pop("footnotes", None)
    grounding = doc.get("source_grounding")
    if isinstance(grounding, dict) and "english_pob_path" in grounding:
        grounding["english_pob_path"] = base["yaml_path"]


def apply_chapter(ch: Chapter, plan: dict, timestamp: str, dry_run: bool) -> list[str]:
    log: list[str] = []
    # Build every final document in memory before touching disk, so a refusal
    # mid-chapter cannot leave the tree half-shifted.
    final: dict[str, dict] = {}
    for verse, act in sorted(plan["assign"].items()):
        origin = act["from"]
        src_doc = yaml.safe_load(yaml.dump(ch.recs[origin], allow_unicode=True, sort_keys=False))
        en_doc = ch.en[verse]
        if act["kind"] in ("recover_donor", "recover_here"):
            was = plan["evidence"][origin]["replaced_text"]
            restored = re.sub(r"\s+", " ", MARKER.sub("", was)).replace(" .", ".").strip()
            tr = src_doc.setdefault("translation", {})
            tr["text"] = restored
            # The footnote array describes the rendering that replaced this one;
            # the definitions behind the restored text did not survive.
            tr["footnotes"] = []
            src_doc["status"] = "needs_human_review"
            relabel(src_doc, en_doc, ch.chapter, verse, ch.edition)
            add_revision(src_doc, was=was, now=restored,
                         why=rationale(ch.edition, "recover", origin, verse, ch.chapter),
                         timestamp=timestamp)
            log.append(f"  {verse} <- recovered from {origin} revision history")
        elif act["kind"] == "move":
            relabel(src_doc, en_doc, ch.chapter, verse, ch.edition)
            add_revision(src_doc, was=text_of(src_doc), now=text_of(src_doc),
                         why=rationale(ch.edition, "move", origin, verse, ch.chapter),
                         timestamp=timestamp)
            log.append(f"  {verse} <- record {origin} (re-keyed)")
        else:
            relabel(src_doc, en_doc, ch.chapter, verse, ch.edition)
            log.append(f"  {verse} stays (source relabelled)")
        final[verse] = src_doc

    # A `recover_donor` lends a rendering but stays put. Its lexical and
    # theological decisions were made while drafting the verse it lent, so they
    # belong with the restored record and would be stale if left behind too.
    for verse, act in sorted(plan["assign"].items()):
        if act["kind"] != "recover_donor":
            continue
        donor_verse = act["from"]
        if donor_verse in final:
            for key in ("lexical_decisions", "theological_decisions"):
                if final[donor_verse].get(key):
                    final[donor_verse][key] = []

    # Preserve each dropped rendering in the record that keeps its verse.
    for path in plan["surplus"]:
        verse = plan["evidence"][path]["content"]
        dropped = text_of(ch.recs[path])
        keeper = final[verse]
        add_revision(keeper, was=dropped, now=text_of(keeper),
                     why=rationale(ch.edition, "dedupe", path, verse, ch.chapter),
                     timestamp=timestamp)
        log.append(f"  drop {path} (second rendering of {verse}; kept in {verse}'s history)")

    # Whatever the mode, the chapter ends up holding exactly the English verses.
    # The paths to remove are therefore the ones no verse lands on — not the
    # surplus paths themselves, which a re-keyed record may well reuse.
    doomed = sorted(set(ch.recs) - set(final))
    if dry_run:
        return log
    for verse, doc in final.items():
        dump(ch.ed_dir / f"{verse}.yaml", doc)
    for path in doomed:
        (ch.ed_dir / f"{path}.yaml").unlink()

    on_disk = {p.stem for p in ch.ed_dir.glob("*.yaml")}
    if on_disk != set(ch.en):
        raise SystemExit(
            f"{ch.edition} chapter {ch.chapter}: after repair the chapter holds "
            f"{sorted(on_disk)}, expected {sorted(ch.en)}"
        )
    return log


def affected_chapters(edition: str) -> list[str]:
    out = []
    for en_dir in sorted((REPO_ROOT / "translation" / BOOK).iterdir()):
        if not en_dir.is_dir():
            continue
        ed_dir = REPO_ROOT / edition / BOOK / en_dir.name
        if not ed_dir.is_dir():
            continue
        if len(list(ed_dir.glob("*.yaml"))) != len(list(en_dir.glob("*.yaml"))):
            out.append(en_dir.name)
    return out


def cmd_report(args) -> int:
    chapters = affected_chapters(args.edition)
    print(f"{args.edition}/{BOOK}: {len(chapters)} chapter(s) with a record-count mismatch")
    ready, blocked = [], []
    kinds = collections.Counter()
    for name in chapters:
        ch = Chapter(args.edition, name)
        plan = build_plan(ch)
        for act in plan["assign"].values():
            kinds[act["kind"]] += 1
        kinds["drop"] += len(plan["surplus"])
        (blocked if plan["problems"] else ready).append((name, plan))
    print(f"  repairable: {len(ready)}   blocked: {len(blocked)}")
    print(f"  record actions: " + ", ".join(f"{k}={v}" for k, v in sorted(kinds.items())))
    recovered = [(n, v) for n, p in ready for v, a in p["assign"].items()
                 if a["kind"] in ("recover_donor", "recover_here")]
    mismatched = [(n, m) for n, p in ready for m in p.get("mismatched", [])]
    print(f"\n  verses with no live rendering, recovered from revision history: {len(recovered)}")
    for name, verse in recovered:
        print(f"      {name}:{verse}")
    if mismatched:
        print(f"\n  records where source.text disagrees with position: {len(mismatched)}")
        for name, note in mismatched:
            print(f"      {name}/{note}")
    if blocked:
        print(f"\n  blocked chapters:")
        for name, plan in blocked:
            for why in plan["problems"]:
                print(f"      {name}: {why}")
    return 1 if blocked else 0


def cmd_plan(args) -> int:
    ch = Chapter(args.edition, args.chapter)
    plan = build_plan(ch)
    print(f"{args.edition} chapter {args.chapter}: "
          f"{len(ch.recs)} record(s) -> {len(ch.en)} English verse(s)")
    if args.chapter in SPLIT_SUPERSCRIPTION:
        print("  note: the Hebrew superscription is split across records in this chapter")
    for verse, act in sorted(plan["assign"].items()):
        origin = act["from"]
        doc = ch.recs[origin]
        if act["kind"] in ("recover_donor", "recover_here"):
            shown = MARKER.sub("", plan["evidence"][origin]["replaced_text"] or "")
            print(f"  {verse} <- RECOVER from {origin} history: {shown.strip()[:66]}")
        else:
            tag = "keep   " if act["kind"] == "keep" else f"move {origin}"
            print(f"  {verse} <- {tag}: {text_of(doc)[:66]}")
    for path in plan["surplus"]:
        verse = plan["evidence"][path]["content"]
        print(f"  DROP {path} (second rendering of {verse}): {text_of(ch.recs[path])[:60]}")
    for note in plan.get("mismatched", []):
        print(f"  cross-check: {note}")
    for why in plan["problems"]:
        print(f"  BLOCKED: {why}")
    return 1 if plan["problems"] else 0


def cmd_apply(args) -> int:
    chapters = [args.chapter] if args.chapter else affected_chapters(args.edition)
    plans = []
    for name in chapters:
        ch = Chapter(args.edition, name)
        plan = build_plan(ch)
        if plan["problems"]:
            print(f"refusing {args.edition} {name}:")
            for why in plan["problems"]:
                print(f"  {why}")
            return 1
        plans.append((ch, plan))
    for ch, plan in plans:
        log = apply_chapter(ch, plan, args.timestamp, args.dry_run)
        print(f"{ch.edition} chapter {ch.chapter}:")
        for line in log:
            print(line)
    if args.dry_run:
        print("\n(dry run — nothing written)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("report", "plan", "apply"):
        p = sub.add_parser(name)
        p.add_argument("--edition", required=True)
        if name == "plan":
            p.add_argument("--chapter", required=True)
        if name == "apply":
            g = p.add_mutually_exclusive_group(required=True)
            g.add_argument("--chapter")
            g.add_argument("--all", action="store_true")
            p.add_argument("--dry-run", action="store_true")
            p.add_argument("--timestamp", default="2026-09-13T00:00:00Z")
    args = ap.parse_args()
    return {"report": cmd_report, "plan": cmd_plan, "apply": cmd_apply}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
