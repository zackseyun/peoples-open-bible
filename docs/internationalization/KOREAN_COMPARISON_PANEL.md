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

The plumbing is in place. What is missing is the licence, which is the only
step that cannot be done in code.

`tools/fetch_api_bible_licensed_references.py` now accepts the three Korean
target names — `saebeonyeok`, `urimal`, `gongdong` — declared as
`LICENSED_TARGETS_KO` in `tools/build_translation_divergence.py`. Point it at a
config naming a `bible_id` and `license_reference` per target and it will fetch.

Note the deliberate split: `LICENSED_TARGETS_KO` is **not** part of
`LICENSED_TARGETS`. That tuple gates the English divergence build, and every
consumer in that module scores against English POB text, so feeding it Korean
rows would emit meaningless `pob_saebeonyeok_similarity`-style metrics. A
Korean divergence builder needs writing before these targets can be scored;
until then the fetcher stores the text and an editor consults it by hand.

Remaining steps, following the English precedent:

1. Obtain a licence expressly covering commercial and AI-assisted evaluation
   use. API.Bible is the likely route; confirm Korean availability and rights
   on the specific plan before fetching anything.
2. Store retrieved text only under `state/licensed_references/` (gitignored).
3. Pass every reference through the versification map, as the English path
   does. Korean editions follow English chapter/verse numbering, while POB
   follows Hebrew numbering in the OT. These offsets are real and measured: 149
   Korean and 141 Spanish Psalms records had cached the *neighbouring* verse's
   English before the 2026-09-13 correction.
4. Commit only numeric scores and non-sensitive metadata.

### The 1910 negative control is already wired

Being public domain, it needs no licence and is committed. Use
`tools/korean_archaism_panel.py`:

```bash
python3 tools/korean_archaism_panel.py vendor          # -> sources/references_ko/kor1910.json
python3 tools/korean_archaism_panel.py scan --min-similarity 0.45
```

`scan` reports two independent signals: character-trigram similarity to the
1910 counterpart, and direct hits on Gaeyeok-line forms. Two calibration
lessons are baked in:

- **Gate the similarity signal on length.** Genealogies and name lists converge
  in any faithful translation — 1 Chronicles 1:1 scores a perfect 1.000 — and
  produced 280 false positives before `--min-length` cut the flagged set from
  309 to 62.
- **Keep both signals.** Similarity catches archaisms the marker list misses:
  Joshua 10:3 scores 0.824 on `보내어 이르기를`, a form no marker covers.

Used as a regression check, it confirms the repairs move the text away from the
archaic baseline: Numbers 22:3 fell from 0.219 to 0.063 and Judges 18:5 from
0.194 to 0.079. Judges 4:9 barely moved (0.180 to 0.172) because POB-ko and the
1910 independently agree on `파실` for מָכַר — a reminder that the score measures
resemblance, not error.

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

- **Orphaned footnote markers are a cross-edition defect, not a Korean one.**
  A YAML-parsing scan of all 629,992 records found **2,146** whose
  `translation.footnotes` contain a marker that never appears in
  `translation.text`, leaving the note unreachable. Korean holds 64 of them;
  the English POB holds **1,605**, of which 375 are canonical OT/NT and 927 are
  extra-canonical (635 in Jubilees alone). Spanish holds 233, Hindi 131.

  Some losses are substantive rather than cosmetic. `translation/nt/mark/007/016.yaml`
  carries a footnote recording that the verse is absent from the earliest Greek
  manuscripts, but its marker is orphaned — so the reader sees a disputed verse
  with no textual-critical disclosure at all. Orphaned `textual_variant` and
  manuscript-absence notes should be audited ahead of the rest.

  Measure this with a YAML parse, not a line scan. `translation.text` is often a
  multi-line scalar, and a scan that reads only the first `  text:` line
  over-reports by roughly six times.

  **Update (2026-09-13) — measured again, fixed, and the count revised down.**
  The 2,146 figure counts inline markers with `\[([A-Za-z0-9]+)\]`, and that
  regex is wrong in two ways. It cannot see a marker that is not ASCII, and it
  cannot see one containing a hyphen. Re-measured with a marker pattern that
  accepts any declared marker, the derived editions hold **2** genuine orphans,
  not the ~550 first reported:

  | edition | ASCII-only regex | script-aware |
  |---|---|---|
  | hi | 131 | 0 |
  | ko | 64 | 0 |
  | simplified | 32 | 2 |
  | ar | 32 | 0 |
  | ru | 18 | 0 |
  | am | 12 | 0 |
  | te / ta / de / ja / ml / yo | 8 / 6 / 2 / 1 / 1 / 1 | 0 |
  | es | 10 | 0 |

  The editions localise the marker itself: Hindi uses `[क]`, Arabic `[أ]`,
  Russian `[а]`, Korean `[주1]`. Those markers are correctly anchored. Spanish
  was genuinely affected and was fixed by the three anchor passes already on
  `main`; its residual 10 are localised markers too, and `spanish_pipeline.py
  validate` reports `failed=0` for Isaiah and John.

  Three real defects remain in `translation_simplified`
  (`dialogue_of_the_savior/007`, `exegesis_on_the_soul/004`,
  `testaments_twelve_patriarchs/benjamin/010/008`): the declared marker is a
  single space, which cannot be anchored at all. That is a marker-key defect,
  not an anchoring one. (The third surfaced once `tools/audit_footnotes.py`
  learned to report blank marker keys as their own status rather than folding
  them in with the orphans.)

  The English POB was genuinely affected and has been fixed. Canonical OT+NT is
  at **0** orphans (375 records repaired), and the deuterocanon and
  extra-canonical books at **603** (821 records repaired). What remains is
  concentrated in Jubilees (456), 2 Baruch (98) and 1 Clement (32), almost all
  `previous_rendering` notes whose quoted alternative shares too little wording
  with the current text to locate mechanically.

  **Do not anchor these from prior revision history alone.** Earlier passes
  clustered markers at clause starts regardless of what the note discusses —
  `translation/ot/1_chronicles/008/037.yaml` records `Eleasah his son[c][b]`
  when `[b]` discusses "Rephah" and `[c]` discusses "Eleasah". Anchor from the
  note's own content, cross-checked against the verse's `lexical_decisions`.

  Records that declare the same marker key twice must have the keys repaired
  before they can be anchored, since anchoring them emits the same inline
  marker twice. Four were blocking an anchor pass — jubilees 20:2, 21:13,
  37:14 and `thunder_perfect_mind/093` — and `audit_footnotes.py` reports the
  full set: 43 records, 8 of them also carrying an unanchored marker. The
  other 35 are already anchored but still hold the duplicate key.

  Phrase-keyed footnotes (Gospel of Thomas, Gospel of Philip, and others) are
  anchored by the phrase appearing in the text rather than by a bracketed
  token. They are not orphans and must not be "fixed".

  **The measurement now lives in `tools/audit_footnotes.py`.** It matches only
  markers the record itself declares in `translation.footnotes[].marker`, so
  localised and hyphenated markers are seen; it reports `phrase_keyed`,
  `duplicate_marker` and `blank_marker` as separate statuses rather than as
  orphans; and its `--anchor-plan` places each marker from the note's own
  quoted alternative, matched against the verse's `lexical_decisions`, never
  from clause position. Run it per edition with `--root`:

  ```
  python3 tools/audit_footnotes.py translation/ot translation/nt   # 0 orphans
  python3 tools/audit_footnotes.py                                 # 603 markers
  python3 tools/audit_footnotes.py --root translation_ko           # 0 orphans
  ```

  Checked against the 375 records repaired by `cca2bd6603`: replayed on the
  pre-repair text, `--anchor-plan` places 339 markers, every one at the same
  position the manual repair chose, and declines the rest rather than guessing.
  Of the eight it puts elsewhere, six are places where the earlier pass
  clustered the marker at a clause start (for example 2 Kings 20:10, where
  `[a]` discusses "ten steps" but sits after "said") and two are the records
  whose prose was also repaired in that commit.

  Worth a dedicated pass: for records blocked *only* on `unanchored footnote`,
  the fix is usually to anchor a marker the reviewer already wrote. That is
  mechanical enough to script with review, and would unblock several hundred
  verses. It should not be bulk-applied unreviewed — per the source-near
  standard, a model verdict is evidence the draft passed that prompt, nothing
  more.
