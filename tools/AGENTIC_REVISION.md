# Agentic Revision Pass — Design and Rollout

This is the upgrade path from the single-shot revision pass
(`azure_bulk_revise.py`, `gemini_bulk_revise.py`) to a multi-turn,
evidence-gathering reviewer agent. The framework that governs the
reviewer's *thinking* is in `tools/prompts/revision_policy.md`. This
document explains the *architecture* that makes the framework
operate per verse.

## Why agentic

The 2026-04-23 Azure revision-pass regression (e.g. 1 Pet 5:8
"clear-minded" → "sober-minded") happened because the reviewer
made one model call with one decision, no evidence-gathering, no
ability to:

- Check whether `DOCTRINE.md` already had a binding rule for the
  contested word.
- Look up how the same Greek lemma was rendered in its other NT
  occurrences (to test "is this figurative throughout?").
- Engage with the drafter's `lexical_decisions` rationale before
  overriding it.

These are evidence-gathering steps, and they require tool calls,
which requires multi-turn agency. Single-shot reviewers cannot do
this kind of work — they can only pattern-match against their
training prior.

## Architecture

Three layers. Each is replaceable.

### 1. Audit (deterministic, no LLM)

`audit_corpus()` in `tools/agentic_revise.py` walks
`translation/**/*.yaml` and flags any verse whose
`lexical_decisions[].source_word` matches a contested-term entry in
`DOCTRINE.md`. This is the candidate queue. Most verses won't touch
contested terms — running the agentic reviewer over them is wasted
compute.

CLI:

```bash
python3 tools/agentic_revise.py --audit-only --out /tmp/audit.json
```

Output: JSON manifest of flagged verses with their contested terms.

### 2. Per-verse reviewer agent

For each flagged verse, the reviewer agent runs a tool-calling loop
(max 6 iterations, hard cap) with these tools:

| Tool | Purpose |
|---|---|
| `lookup_doctrine(source_word)` | Returns DOCTRINE.md's contested-terms entry for a word, if one exists. |
| `lookup_occurrences(source_word, limit)` | Returns every POB verse where the source_word appears in `lexical_decisions`, with current renderings and distribution counts. |
| `lookup_book_context(book)` | Returns book-level translation notes (currently a stub — book notes aren't indexed yet). |
| `read_drafter_reasoning(verse_yaml_path)` | Returns the verse's `lexical_decisions`, `theological_decisions`, `footnotes`, and prior `revisions[]`. |
| `submit_revision(revised_text, rationale)` | Terminal: propose a change. The rationale must address Q1/Q2/Q3 from the policy. |
| `submit_unchanged(brief_reason)` | Terminal: the draft stands. Default outcome. |

The system prompt is the policy file
(`tools/prompts/revision_policy.md`) plus a short framing header.

The reviewer's output is a **proposal** — never a direct write to a
YAML. Proposals collect into a manifest JSON for human review.

CLI:

```bash
# Reviewer over an audit set, dry-run (proposals only, no YAML writes)
python3 tools/agentic_revise.py --from-audit /tmp/audit.json \
    --limit 20 --out /tmp/proposals.json

# Single verse, for debugging the framework
python3 tools/agentic_revise.py --verse \
    translation/nt/1_peter/005/008.yaml --out /tmp/one.json
```

### 3. Apply (human-gated)

The proposals manifest is hand-reviewed. To approve a proposal, set
`"approved": true` on the entry. Then:

```bash
python3 tools/agentic_revise.py --apply /tmp/proposals.json
```

The applier appends a `revisions[]` entry with category
`agentic_revision`, updates `translation.text`, and refreshes
`revision_pass`. Unapproved proposals are skipped.

**No proposal is auto-applied.** The first 100+ runs through this
pipeline are dry-run reviews; auto-apply is a later enhancement
once confidence in the framework is established on contested-term
verses.

## Sub-agents (not in this first cut)

The harness is structured so the reviewer can spawn focused
sub-agents when its in-context evidence is thin, but no sub-agents
ship in the first version. Planned candidates, in priority order:

1. **Lemma analyst** — given a Greek lemma, return its full
   NT/OT/deuterocanon distribution with verse-by-verse renderings
   and a verdict ("figurative in N/N occurrences" / "split N
   literal, M figurative, here are the discriminators"). The
   single highest-value sub-agent — would have caught the νήφω
   case alone.
2. **Author-pattern analyst** — given a verse and author, summarize
   that author's usage of the word/concept across their corpus.
3. **Parallel-passage analyst** — for synoptic parallels and
   cross-book quotations, surface how the parallel was rendered.

Each sub-agent gets its own narrow tool surface so context stays
focused. Recursion is capped at one level — sub-agents never spawn
sub-agents.

## Cost / safety controls

- **Max iterations per verse**: 6 (constant in `agentic_revise.py`).
- **Cap-reached behavior**: the verse is flagged for human review;
  no automatic decision is made.
- **Default model**: `claude-sonnet-4-6` (env override
  `ANTHROPIC_MODEL=claude-opus-4-7` for the hardest cases).
- **Default outcome**: `submit_unchanged`. The framework explicitly
  rewards leaving verses alone; the reviewer is told that every
  verse left alone is a verse it has validated.
- **No silent YAML writes**: every change goes through the
  proposals manifest and an explicit `--apply` step.

## Rollout plan

1. **Audit run.** Build the candidate queue.
   `python3 tools/agentic_revise.py --audit-only --out /tmp/audit.json`
2. **Validate on 20 known-stress verses** — verses touching νήφω,
   μετανοέω, σάρξ, δοῦλος, Χριστός, πίστις, ἱλαστήριον. Compare
   outputs to DOCTRINE.md defaults; tune the framework / system
   prompt if needed.
3. **Expand to the audited set in batches of 100.** Read the
   proposals JSON. Approve / reject by hand. Apply the approved
   ones.
4. **Add the lemma-analyst sub-agent** if and only if reviewer
   performance on cross-book figurative-vs-literal calls is
   demonstrably weak.
5. **Maintain a per-decision audit log** at
   `state/agentic_pass/<verse_id>.json` — every tool call, every
   terminal rationale, full trace. This is the project's defense
   against "the AI just decided X" and the cleanest training data
   for a future project-specific reviewer.

## What this does NOT do (yet)

- No corpus-wide auto-apply. Every change requires human approval.
- No sub-agent spawning — single reviewer per verse for now.
- No book-context indexing — `lookup_book_context` is a stub.
- No automatic re-runs of `azure_bulk_revise.py` /
  `gemini_bulk_revise.py` for verses the agentic reviewer flags;
  the audit set is sufficient.
- No integration with the public revisions page beyond what the
  existing `revisions[]` entries already provide (the
  `agentic_revision` category will appear in `revisions.json`
  after the regen flywheel runs).

## Files

- `tools/agentic_revise.py` — the harness, tools, reviewer loop,
  audit, and apply logic. Single file for now; split into a package
  when it exceeds ~800 lines.
- `tools/prompts/revision_policy.md` — the framework (Q1/Q2/Q3,
  override authority, agentic tools section, backstop prohibitions).
- `DOCTRINE.md` contested-terms table — the authoritative source
  for binding word-level rules; parsed by `lookup_doctrine`.
