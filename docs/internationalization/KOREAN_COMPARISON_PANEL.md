# Korean comparison panel

Companion to `KOREAN_PIPELINE.md` and `docs/SOURCE_NEAR_EDITORIAL_STANDARD.md`.
It answers one question: **against which Korean Bibles should POB-ko be measured
when the goal is "faithful to the source, but the most natural Korean a modern
reader would actually use"?**

The governing rule from the source-near standard applies unchanged here:

> Published translations are diagnostics, never votes. Agreement does not prove
> accuracy, and novelty does not prove improvement.

A comparator's job is to *surface* a divergence so an editor has to justify it
from the source. It never casts a vote.

## Why the obvious candidate fails

`ebible.org` distributes exactly one Korean Bible under a redistributable
licence: the **Korean Bible 1910** (`kor`, public domain, full OT+NT). It is the
only Korean text that could legally be vendored into `sources/references/`
alongside BSB/WEB/ASV/KJV.

It is also the wrong model for this project's stated goal. The 1910 text and its
descendant 개역한글 / 개역개정 line are deliberately archaic: 문어체 endings
(`-니라`, `-더라`, `-나이다`), `이르되` for ordinary speech verbs, `대저` as a
connective. That is precisely the register `KOREAN_PIPELINE.md` rules out, and
precisely the register that leaked into POB-ko in the verses repaired on
2026-09-12 (see *Findings* below).

**Use it as a negative control, not as a target.** When POB-ko agrees closely
with the 1910 wording, that is a signal to re-read the verse aloud, not a
reassurance.

## The recommended panel

All three are copyrighted. None may be committed to this repository. They are
retrieved into a private, gitignored path and used exactly the way NKJV/NIV/NLT
are used for English — see `docs/LICENSED_TRANSLATION_COMPARISONS.md`,
"Safe operating boundary".

| Rank | Translation | Publisher | Why it belongs on the panel |
|---|---|---|---|
| 1 | **새번역** (RNKSV, 표준새번역 개정) | 대한성서공회 | The closest institutional analogue to what POB-ko is trying to be: a scholarly, source-first revision that deliberately moved off the 개역 register into contemporary Korean while keeping a dignified liturgical voice. `KOREAN_PIPELINE.md` already names it as the register benchmark. Best single comparator. |
| 2 | **우리말성경** | 두란노서원 | Pushes further toward ordinary modern usage and shorter sentences. Useful as the *upper bound* on naturalness: where POB-ko is stiffer than 우리말성경 without a source reason, the stiffness is probably gloss-Korean. |
| 3 | **공동번역 개정판** | 대한성서공회 | The Catholic–Protestant common translation. Valuable for two things the others do not give you: a genuinely different *lexical* tradition (including 하느님 vs 하나님) and a meaning-first philosophy that exposes places where POB-ko has preserved Hebrew/Greek syntax at the cost of Korean sense. |
| — | **개역개정 4판** | 대한성서공회 | Negative control only, per above. Also the highest-recognition text among Korean churchgoers, so it is the useful reference for *which* traditional phrasings a reader will expect POB-ko to depart from, and therefore which departures deserve a footnote. |

### Why not others

- **현대인의 성경** is a paraphrase from the Living Bible line, not a source
  translation. It would answer a question POB-ko is not asking. It belongs on
  the SPOB (simplified) panel if anywhere, not here.
- **한글킹제임스** inherits the Textus Receptus base and would introduce textual
  divergence that has nothing to do with naturalness, contaminating the signal.

## Decision-level comparison

Because the comparator texts cannot be reproduced here, the table records the
*decisions* each tradition makes, which is what an editor actually needs when
adjudicating a POB-ko rendering. Verify each cell against the licensed text at
review time rather than trusting this summary.

| Decision | POB-ko | 새번역 | 공동번역 개정 | 우리말성경 | 개역개정 |
|---|---|---|---|---|---|
| Tetragrammaton | **야훼** | 주 | 야훼 | 여호와 | 여호와 |
| Θεός | **하나님** | 하나님 | 하느님 | 하나님 | 하나님 |
| Narrative ending | **합쇼체** (`-습니다`) | 해라체 (`-었다`) | 해라체 | 해라체 | 문어체 (`-니라`) |
| Address to God | **합쇼체 존대** (`-십니다`) | `-습니다` | `-습니다` | `-습니다` | `-나이다` |
| Speech verb | **말했습니다** | 말하였다 | 말하였다 | 말했다 | 이르되 |
| δοῦλος | **종**, 노예 where EN POB flags bonded status | 종 | 종 | 종 | 종 |
| ἐκκλησία | **회중** preferred over 교회 | 교회 | 교회 | 교회 | 교회 |
| Χριστός (titular) | **메시아** | 그리스도 | 그리스도 | 그리스도 | 그리스도 |

Two rows deserve comment.

**Narrative ending is POB-ko's single biggest divergence from every Korean Bible
on the panel.** All four comparators narrate in 해라체 or 문어체; POB-ko narrates
in 합쇼체. This is a deliberate, documented project choice, and the panel will
therefore flag divergence on essentially every narrative verse. Do not treat
that as signal — filter it out before ranking, the same way
`build_translation_divergence.py` excludes short rows, or the Korean divergence
report will be pure noise.

**야훼 and 메시아 are also deliberate** and will diverge from most of the panel.
They are already justified in `KOREAN_PIPELINE.md`; the panel adds nothing.

The rows where the panel *is* informative are the ones not listed above:
sentence segmentation, connective choice, word order, and whether a Hebrew or
Greek idiom was carried across as an idiom or as a gloss. Those are exactly
where POB-ko's defects have actually been found.

## Wiring it in

Nothing is committed. Follow the English precedent exactly:

1. Obtain a licence expressly covering commercial and AI-assisted evaluation
   use. API.Bible is the likely route; confirm Korean availability and rights
   on the specific plan before fetching anything.
2. Store retrieved text only under `state/licensed_references/` (gitignored).
3. Extend `tools/fetch_api_bible_licensed_references.py`, whose
   `load_config` currently hard-rejects anything outside
   `divergence.LICENSED_TARGETS` (NKJV/NIV/NLT). Korean targets must be added
   there before the fetcher will accept them.
4. Pass every reference through the versification map, as the English path
   does. Korean editions follow English chapter/verse numbering, while POB
   follows Hebrew numbering in the OT — the Psalms offsets are real and will
   silently misalign rows if skipped.
5. Commit only numeric scores and non-sensitive metadata.

The 1910 negative control is the exception: it is public domain and *can* be
vendored into `sources/references/` via `build_reference_panel.py`, which needs
a Korean corpus path added to `fetch_corpora()`. Doing so is cheap and gives an
immediate, licence-free archaism detector: high similarity to 1910 is a
readability smell.

## Findings from the 2026-09-12 readability pass

What the comparison framing above was built to catch, found by direct audit:

- **32 canonical verses** carried 개역 register in violation of
  `KOREAN_PIPELINE.md`. Seven were verbatim 개역한글, unpunctuated. Repaired.
- Register damage is heavily concentrated in `extra_canonical/jubilees`, which
  reads as though drafted from a 개역-family Korean text rather than from the
  source. **Not yet repaired** — it needs a book-level redraft, not verse edits.
- **`translation.philosophy`** had drifted: 1,069 records said `formal` against
  the documented `optimal-equivalence`, and 2 held an entire prose paragraph in
  the enum field. Normalized.
- Real mistranslations surfaced underneath the register problems, including
  `요강` (a chamber pot) for the Nile in Genesis 41:3 — the same error already
  corrected in Exodus 7:18/7:21.
- **1,360 records hold a `review_pass` with `verdict: revise`, a `revised_text`,
  and `applied_revision: false`.** 736 were blocked on `unanchored footnote`,
  624 record no reason. 577 are canonical. This is a *tracked* queue, not a
  silent break: 1,359 of the 1,360 are already `needs_human_review`. But
  Genesis 41:3 shows the queue can hide genuine mistranslations behind a purely
  mechanical block — there, the reviewer's own `revised_text` simply forgot to
  place the `[a]` marker it also supplied in `revised_footnotes`.

  Worth a dedicated pass: for records blocked *only* on `unanchored footnote`,
  the fix is usually to anchor a marker the reviewer already wrote. That is
  mechanical enough to script with review, and would unblock several hundred
  verses. It should not be bulk-applied unreviewed — per the source-near
  standard, a model verdict is evidence the draft passed that prompt, nothing
  more.
