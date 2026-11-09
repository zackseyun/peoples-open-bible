# Translation Stance

This document states the translation commitments that guide every
decision in the People's Open Bible. Declaring them is an act of
honesty: critics can assess our output against our stated
commitments rather than guessing at hidden biases.

> **Status: first draft.** This document will be refined as the
> project matures. Input and disagreement are welcomed via GitHub
> issues.

## Theological stance

The People's Open Bible does not commit to a specific denominational
or creedal doctrinal stance. Where the source texts presuppose
theological claims — the divinity of Christ, the resurrection,
the personhood of the Holy Spirit, the unity of God — the
translation reflects those claims as the texts present them, not
as imposed commitments of the translator.

Readers from any tradition (Catholic, Eastern Orthodox, Protestant
of any stripe, non-denominational, inquirer) are invited to
evaluate POB against their own framework. Where a translation
decision is influenced by a theological reading — for example,
where a Greek construction is genuinely ambiguous and the English
choice leans one way or the other — that choice is documented in
the verse's `theological_decisions` block and the alternative
rendering is preserved in a footnote.

We do not pick sides on denominational distinctives (Reformed vs.
Arminian, infant vs. believer's baptism, real presence vs.
symbolic, cessationist vs. continuationist, etc.). Those questions
are for the reader and their faith community, not for the
translation.

## Translation philosophy

Since November 2026 the People's Open Bible is **meaning-first**. The main
text conveys what each passage means: what its author was saying, and what
the church confesses God was saying through that author, to the people who
first heard it. The Hebrew, Aramaic, and Greek words are the vessel, not the
destination. Their word order, idioms, and wording patterns are kept where
they carry meaning, and moved to footnotes where they would obscure it for a
reader today. See
[docs/MEANING_FIRST_TRANSLATION_2026-11.md](docs/MEANING_FIRST_TRANSLATION_2026-11.md)
for the change and how the current text was produced.

Earlier passes aimed at **optimal equivalence**, which weighted the source's
wording patterns alongside its meaning. That history stays in every verse's
revision record.

Specifically:

1. **Meaning over surface, weight over modernity.** The best-supported
   meaning goes in the text; a revealing literal wording or serious
   alternative reading goes in a footnote. A plainer or more contemporary
   word is not automatically closer to the meaning. Keep weighty words
   (soul, righteousness, glory, grace, holy, mercy, sin, covenant) and
   classic images when they carry more of it: Psalm 23 keeps "He restores
   my soul", "paths of righteousness", and "the valley of the shadow of
   death". For *doulos*, the main text uses "servant" consistently while
   notes and the public audit trail preserve bonded-status, ownership, and
   total-allegiance nuance where it is historically or theologically
   salient (Rom 1:1, Phil 1:1).

2. **Translate titles; use conventional name forms.** Christological
   titles are translated to preserve meaning (*Christos* →
   "Messiah" when it functions independently as a title; *Kyrios* →
   "Lord"). In name-like constructions, use the familiar English forms
   "Jesus Christ" and "Christ Jesus." Personal names are otherwise
   transliterated by standard conventions. Thus "Jesus is the Messiah"
   retains the title, while Greek *Iēsous Christos* used as a personal-name
   construction is rendered "Jesus Christ."

3. **Preserve theological tension rather than resolve it.** Where
   the source is genuinely ambiguous on a contested interpretive
   question (e.g., *pistis Christou* — "faith in Christ" vs.
   "faithfulness of Christ"), we render one in the main text and
   preserve the alternative in a footnote, documenting the
   decision in the per-verse YAML.

4. **Consistency of key terms, or documented exception.** A given
   Greek or Hebrew word should receive a consistent English gloss
   across the translation, unless context demands variance — in
   which case the variance is documented per-verse with a
   rationale. The `consistency_lint.py` tool enforces this at
   commit time.

5. **Readable modern English, not archaic or academic.** The
   target reader is a literate 18–35-year-old English speaker.
   Vocabulary should be accessible without flattening theological
   weight. We avoid both ecclesiastical jargon ("propitiation" is
   footnoted, not required) and informality that undersells the
   text's gravity.

## Source distinctions

A significant Greek or Hebrew distinction stays visible when it carries
meaning the reader needs: in the text where it shapes the sense, and in a
footnote otherwise. Prior rationale and earlier revisions are evidence, with
maintainer revisions weighed most; they are not a veto. Do not infer
different meanings from morphology alone or invent theology to justify
different glosses. Record unresolved proposals for maintainer review; do not
silently certify them as unchanged or auto-publish.

**Approved rendering for sexual "knowing":** where Hebrew *yada* or Greek
*ginōskō* refers to sexual union, the text keeps "know": "Adam knew Eve his
wife" (Gen 4:1), "he did not know her" (Matt 1:25), "I have not known a man"
(Luke 1:34). Do not replace it with "was intimate with", "slept with", or
"made love to".

**Approved scoped rendering:** John 21:15–17 uses **agape-love** for ἀγαπάω
and **phileo-love** for φιλέω, including the repeated question in verse 17.
The ἀγάπη noun's general table entry below is not a rule erasing that verb
pattern. Do not revert this approved POB/SPOB wording to generic “love”.

## Contested terms

The following terms appear frequently and carry heavy theological
weight. Our default rendering and rationale are recorded here.
Per-verse variance is documented in the individual YAML files.

| Greek / Hebrew | Default English | Alternatives considered | Rationale |
|---|---|---|---|
| Χριστός *Christos* | Messiah where independently titular; Christ in the name forms "Jesus Christ" / "Christ Jesus" | Christ, Messiah | Preserves the title's Hebraic messianic meaning while using the recognizable conventional English personal name |
| κύριος *Kyrios* | Lord | LORD, Master | Matches covenantal and NT usage |
| δοῦλος *doulos* | servant | bondservant, slave | Uses reader-facing "servant" consistently; documents bonded-status and ownership nuance in notes/audit metadata |
| πίστις *pistis* | faith | faithfulness, trust | Main text: faith; footnote alternatives where contested |
| δικαιοσύνη *dikaiosynē* | righteousness | justice | Both renderings preserved in footnotes for Pauline passages |
| ἱλαστήριον *hilastērion* | atoning sacrifice | propitiation, mercy seat | Dynamic rendering for accessibility; alternatives footnoted |
| ἀγάπη *agapē* | love | charity (archaic) | Lexical cognates in source kept |
| σάρξ *sarx* | flesh (literal) / sinful nature (metaphorical) | — | Context-dependent; per-verse documented |
| μετανοέω / μετάνοια *metanoeō / metanoia* | repent / repentance where context supports moral-spiritual change | change of mind, reconsider, regret and other contextual renderings | See "Repentance terminology (2026-10-13)"; explain the meaning without homogenizing distinct source expressions |
| νήφω *nēphō* | clear-minded (most contexts); sober (where Paul explicitly runs the drunk/sober metaphor) | sober-minded | See revision notes in 1 Pet 5:8, 1 Thess 5:6 |
| יְהוָה YHWH | Yahweh | the LORD, Jehovah | Renders the divine name as a name. Where the NT quotes an OT YHWH passage using *Kyrios*, the NT verse retains "Lord" to preserve the Greek; the OT source verse uses "Yahweh". |
| אָדָם *adam* | man / humankind (context) | — | Context-dependent per usage |

## Repentance terminology (2026-10-13)

The contextual reassessment supersedes the October 11 reorientation default.
Use **repent / repentance** for the moral-spiritual response where the passage
supports it. Familiarity alone is not evidence of accuracy; explain the intended
change of disposition and conduct rather than reducing repentance to sadness
or a change of opinion. Reorientation can explain the concept but is not a
mandatory replacement in reader text. No claim about measured reader reception
or independent scholarly approval is made.

**Context still controls.** Retain regret, remorse, relenting, reconsideration,
change of mind, or turning back where those fit the source and local direction.
Preserve contested readings in Job 42:6 and Hebrews 12:17, the alternate turning
reading in Jeremiah 31:19, and distinct turn/return verbs in Acts 3:19 and 26:20.
Use "repentance toward God" in Acts 20:21 because the sentence explicitly gives
that direction; do not insert it into every occurrence of metanoia.

Keep sorrow and repentance distinct in 2 Corinthians 7:9-10. Retain the
relationship between repentance and its fruits, rather than equating the two.
Use "I repent" in Luke 17:4 without requiring proof of completed reform before
forgiveness. Preserve baptismal grammar without deciding symbolic versus causal
interpretations by a vocabulary substitution.

Do not add intensifiers. Keep source-backed emphasis such as the existing
"completely" and "from their whole heart" in Hermas 21:4. Keep the corrected
"more joy ... than" in Luke 15:7. Extra-canonical writers retain their own
conceptual frameworks, including adverse changes of mind; do not harmonize
them to a canonical Godward formula. Historical English witnesses and source
transcriptions remain untouched; reader adaptations retain their disclosure.

All **397** previously changed records have an explicit new decision, including
retained exceptions and the four October 12 follow-up records. Earlier wording,
notes, plans, and review history are preserved rather than erased. See the
[full decision ledger](docs/REPENTANCE_REASSESSMENT_2026-10-13.md) and exact,
hash-bound plan in `config/terminology/repentance-contextual-2026-10-13.json`.
These remain editorial drafts, not independent scholarly certifications.

## What the translation is not

To prevent misunderstanding:

- **Not a paraphrase.** Every English rendering is tied to a
  specific source-text word or phrase, documented in the per-verse
  YAML.
- **Not a study Bible.** Footnotes document translation decisions,
  not doctrinal application or devotional commentary.
- **Not a denominational product.** The translation is
  intentionally cross-denominational. Contested readings are
  preserved in footnotes, not smoothed away.
- **Not a finalized translation.** Every verse is currently an
  AI-drafted rendering, released openly with full rationale. There
  is no formal scholarly review process at this time.
- **Not a first-century English approximation.** We aim at modern
  English that honors source-language meaning, not at archaism.

## Translating into other languages

The People's Open Bible's long-term intention is to be translated
into every major world language. Scripture belongs to the whole
church; producing POB only in English would contradict the
project's mission.

Each target language is its own translation — drafted directly
from the original-language sources (Hebrew OT, Greek NT, Swete
LXX for the deuterocanonical books) rather than from the English
POB. Translating from English would compound the distance from the
originals and inherit choices that make sense in English but not
elsewhere. Every target language deserves its own encounter with
the Hebrew and Greek.

Each language goes through **several revision passes** before it
is considered stable:

1. **AI-drafted first pass** — a frontier multilingual model
   produces the initial verse-by-verse draft with full per-verse
   provenance, following the same methodology used for English
   (DOCTRINE.md translation philosophy §§1–5, per-verse YAML
   schema, `doctrine_reference` citations where relevant).
2. **AI-reviewer revision** — a second, distinct model reads the
   draft and flags awkward phrasing, dropped nuance, or places
   where the target language's idiom has drifted from the
   source's force. Revisions are discrete commits.
3. **Native-speaker community review** — before a language is
   declared stable, speakers of that language who are also
   familiar with the biblical source languages (or who have
   access to published lexicons in that language) audit the
   text and raise issues publicly.
4. **Public issue window** — a minimum public-review period with
   open GitHub issues before any language moves from "preview"
   to "stable."

**Supported languages will be disclosed publicly based on model
performance and feasibility.** Not every language has an AI model
capable of scholarly-accurate translation yet, and not every
language has a sufficient community of native-speaking reviewers
accessible to the project. We will publish the current supported-
language list, and the ready-but-not-yet-stable list, as we reach
the capability threshold for each. Languages that do not yet meet
the bar are named as such, not silently omitted.

Every language published under this program carries the same
CC-BY 4.0 license, the same per-verse provenance, the same
auditability. There is no tier system across languages — every
supported language gets the full People's Open Bible.

## Change log for this document

Material changes to this document are themselves commits. Prior
versions of the stance are preserved in git history.

- **2026-11-09:** Translation philosophy changed from optimal
  equivalence to meaning-first: the main text conveys what the
  author, and God through the author, meant to the first hearers,
  with revealing literal wording in footnotes. Added the
  meaning-over-modernity principle (Psalm 23 calibration) and the
  approved "know" rendering for sexual union. The canonical and
  deuterocanonical text was retranslated on this basis; see
  [docs/MEANING_FIRST_TRANSLATION_2026-11.md](docs/MEANING_FIRST_TRANSLATION_2026-11.md).

- **2026-04-21:** Removed creedal affirmations (Apostles' Creed,
  Nicene Creed, Chalcedonian Definition) and replaced with a
  theological-stance section that declines specific creedal
  commitment. Translation philosophy and contested-terms table
  preserved unchanged; those are methodology, not creedal
  commitment, and the project actually runs on them. Added a
  "Translating into other languages" section stating POB's long-
  term intention to ship in every feasible major language, with
  the full revision pipeline and transparent supported-language
  disclosure. Per-verse YAML citing the old `doctrine_reference`
  values is preserved as historical record; those are not
  retroactively edited.
