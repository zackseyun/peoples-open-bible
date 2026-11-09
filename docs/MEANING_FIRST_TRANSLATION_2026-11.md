# Meaning-first retranslation (November 2026)

In November 2026 the People's Open Bible changed what its main text aims for.
Earlier passes tried to keep the English as close as possible to the surface of
the Hebrew, Aramaic, and Greek: their word order, idioms, and word-for-word
patterns. The main text now aims to convey what each passage actually means:
what its author was saying, and what the church confesses God was saying through
that author, to the people who first heard it.

The words of the original languages are the vessel, not the destination. Their
idioms and conventions were clear to the first hearers, but they often say less,
or something different, to a reader today. The translation carries the meaning
across, with the same weight and force, rather than the shape of the vessel.

## What stays the same

- **Every verse stays auditable.** Each verse file keeps its source text, the
  earlier wording, every revision with its rationale, and the lexical and
  theological decisions. The new wording is added as a revision, not written
  over the history.
- **No added doctrine or commentary.** Where faithful readers disagree about
  what a text means, the best-supported meaning goes in the text and the
  serious alternative goes in a footnote.
- **Verse boundaries hold.** Each verse renders exactly its own content.
- **Standing rulings stay in force:** "Yahweh" for the divine name, "Messiah"
  where Christos is a title, "servant" for doulos, contextual "repent", the
  approved John 21:15–17 wording, and "know" where Hebrew yada or Greek ginosko
  refers to sexual union ("Adam knew Eve his wife").

## Meaning is not the same as sounding modern

A plainer or more contemporary word is not automatically closer to the meaning.
Often the long-established English rendering carries more of it. The
translation keeps weighty words such as soul, righteousness, glory, grace, and
holy wherever the source term carries that weight, and keeps classic images
when they hold more of the meaning than a modern equivalent. Psalm 23 shows
the calibration: "He restores my soul", "paths of righteousness", and "the
valley of the shadow of death", with "deep darkness" in a footnote.

## How the meaning is discerned

Each passage was translated with the whole chapter in view. For every verse the
translator received:

1. the source text in its literary context;
2. the verse's full translation history: the first draft, every revision, and
   the reason for each. Revisions outweigh the first draft, later revisions
   outweigh earlier ones, and maintainer revisions (human editorial decisions)
   weigh most;
3. the documented lexical and theological decisions;

and was told to weigh, after those, the author's usage elsewhere, the wider
canon, and the setting the first hearers shared.

## How it was produced

- **Model:** GPT-6.1 Sol (`gpt-6.1-sol-2026-09-29`) on Azure OpenAI, deployment
  `pob-meaning-gpt-6-1-sol`, high reasoning effort, Flex processing tier.
- **Instructions:** [`tools/prompts/pob_meaning_first_v4.md`](../tools/prompts/pob_meaning_first_v4.md).
  Its SHA-256 is recorded in every verse's `meaning_pass` block.
- **Tool:** [`tools/pob_meaning_pass.py`](../tools/pob_meaning_pass.py)
  (`translate`, `report`, `export`, `import`, `apply`).
- **Second model for refused verses:** Claude Opus 5.5 translated the verses
  Azure would not process, from request bundles that `export` writes with the
  same user message the Azure path sends. `import` validated the answers.
- **Pilot:** 15 passages across every genre were reviewed before the full run.
  Pilot feedback produced the "know" ruling and the "meaning is not the same as
  sounding modern" principle above.

## What each verse records

The applied wording is in `translation.text`, with `translation.philosophy:
dynamic`. A `revisions` entry (`adjudicator: gpt-6.1-sol-meaning-pass`,
`category: meaning_retranslation`) holds the previous and new wording. A
`meaning_pass` block records the model, deployment, prompt id and hash, a
one-sentence statement of the verse's meaning, each substantive decision with
its reason, how the history was weighed, the change level (kept, refined,
retranslated), and the translator's confidence.

## Scope

This pass covers the 66 books of the Protestant canon and the deuterocanonical
books: 37,295 verses, translated in 2,694 passages.

- **36,858 verses** received the meaning-first pass: 11,666 retranslated,
  17,608 refined, and 7,584 kept word for word. A kept verse still gets a
  `meaning_pass` record, but no revision entry, because its wording did not
  change.
- **173 of those** were translated by Claude Opus 5.5 with the same
  instructions and the same per-verse context. Azure's content filter refused
  them (mostly passages describing violence or sexual sin), or repeatedly cut
  the reply off. Their revision entries and `meaning_pass` blocks name that
  model (`adjudicator: claude-opus-5.5-meaning-pass`).
- **437 verses keep their previous wording** for now, because a test or a
  recorded decision pins their exact text: 229 by tests, 145 by applied
  textual-restoration decisions, 59 by the repentance and reorientation
  terminology decisions, and 4 by tools. Changing them needs a separate review
  that updates those records together with the wording. The list is in
  [`MEANING_PASS_HELD_VERSES_2026-11.txt`](MEANING_PASS_HELD_VERSES_2026-11.txt).
- The extra-canonical books are not part of this pass.

The Simplified People's Open Bible (SPOB) is derived from POB and will be
regenerated from the new text in a separate pass. Other-language editions are
translated from the original languages and are not changed by this pass.
