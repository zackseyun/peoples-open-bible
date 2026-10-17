# Samuel source comparison - pass 2

Checked: 2026-09-04

## Outcome

Two QDR index hits have now received passage-level checks. Neither supplies
secure Hebrew support for the disputed wording. The POB source fields and
English sentences remain unchanged, apart from moving footnote markers to the
phrases they explain. Notes and lexical rationales now disclose the limits.

| Passage | What the controls establish | What the fragment does not establish |
|---|---|---|
| 1 Samuel 14:41 | WLC has the short prayer; the pinned Rahlfs Greek control has a longer prayer | 4Q52 fragment 2 does not securely establish that longer Hebrew prayer: most text is supplied and its passage identification is disputed |
| 2 Samuel 21:19 | WLC Samuel and the Greek control name Goliath; 1 Chronicles 20:5 names Lahmi, his brother | The 1Q7 index hit does not preserve the disputed names or establish their assignment to verse 19 |

These are held comparisons, not adjudications of earliest wording. Keeping the
current WLC-aligned text is an interim publication choice, not a verdict that
WLC must win. The validated ledger now contains nine comparison cases and
16 passage-coverage records; those counts include uncertain coverage, not just
supporting witnesses.

## 1 Samuel 14:41: three distinct questions

The [versioned 4Q52 transcription](https://lexicon.qumran-digital.org/transcriptions/4Q52/2026-05-21/index.html?v=2026-05-21)
assigns fragment 2 to 1 Samuel 14:41-42. Its first line contains the excerpt
`[אם יש בי] או ב֯[יונתן בני העון]`. The brackets mark supplied text;
the dot marks an uncertain letter. The supplied longer line includes Urim,
and the next line supplies Thummim. Neither word is preserved Hebrew ink in
this transcription. We inspected the published transcription, not a newly
acquired image of the manuscript.

The Greek control does attest a longer prayer. Its requests include
`δὸς δήλους` and `δὸς δὴ ὁσιότητα`. Reading those in terms of Urim and Thummim
is an interpretive and source-language reconstruction question, separate from
what the Greek actually prints and from surviving Hebrew characters.

There is also a prior identification question. Sarah Yardney's
[author-hosted 2019 presentation abstract](https://chicago.academia.edu/SarahYardney)
explicitly challenges the assignment of fragment 2 to this passage. Her
[2024 Textus article](https://doi.org/10.1163/2589255X-bja10040),
*Correcting Some Claims of LXX Readings in the Publication of the Samuel
Scrolls from Qumran (DJD XVII)*, addresses misreadings and misidentifications.
The author abstract and publisher metadata were checked; the full 2024 article
and its image arguments were unavailable in this pass. We therefore record
the dispute without claiming to have independently settled it.

The author's [2017 dissertation](https://knowledge.uchicago.edu/records/sn039-sg771),
*Interpretation in the Septuagint of Samuel*, pp. 136-138 (PDF pages 148-150),
represents an earlier assessment. Those complete relevant pages, including the
Hebrew reconstruction and footnotes, were visually inspected. The dissertation
accepts broad support for a longer form, but warns that a reconstruction guided
by Greek cannot independently establish its exact Hebrew wording. It must not
be cited as if it answers the author's later identification challenge.

Current disposition: `coverage-only-disputed-identification`, with coverage
itself marked uncertain. The fragment contributes no positive support to a
preferred source selection until the identification dispute is examined.
This does not refute the longer Greek reading or settle its historical priority.

## 2 Samuel 21:19: a parallel is not a Samuel manuscript

The [versioned 1Q7 transcription](https://lexicon.qumran-digital.org/transcriptions/1Q7/2026-05-21/index.html?v=2026-05-21)
locates fragment 3 at 2 Samuel 21:16-18. Line 5 reads
`[הרפה -- ]ל[ -- ]ל[ -- ]`. Its supplied opening links to verse 18;
QDR assigns the isolated lamed traces to verse 19. This pass does not securely
establish that verse assignment. The disputed opponent, patronymic, and
“brother of” wording are not preserved by these traces.

WLC Samuel and the pinned Greek control name Goliath as Elhanan's opponent.
The local WLC text of 1 Chronicles 20:5 names Lahmi, Goliath's brother, but
Chronicles is a distinct parallel composition. It is relevant to the literary
and textual problem, not another copy of Samuel to add to a witness count.
Neither corruption nor the direction of literary revision has been established
merely by comparing these forms. Importing “brother of” to resolve the narrative
tension would exceed the current evidence review.

Current disposition: `coverage-only-unassigned-traces-after-21-18`. The note
now explains the parallel and why 1Q7 does not decide it. The patronymic note
has been moved from “Philistines” to “Jaare-oregim.”

## Reproducibility and review limits

- Greek controls: OpenScriptorium `lxx-morph` commit
  `c91f6b1e8fb3ba37df701e6ae31f675ace71a2b2`; exact verse strings are stored in
  the comparison record. This is an edited Greek control, not individual Greek
  codex collation.
- Hebrew controls: local WLC source fields, with current verse-file SHA256
  values in the comparison record; Chronicles has its own pinned parallel
  source entry.
- Institutional identity/access: [IAA 4Q52](https://www.deadseascrolls.org.il/explore-the-archive/manuscript/4Q52-1?locale=en_US)
  and [IAA 1Q7](https://www.deadseascrolls.org.il/explore-the-archive/manuscript/1Q7-1?locale=en_US).
  Exact manuscript image regions remain unacquired and uncollated.
- Earlier model scores and revision timestamps in the verse YAML are historical
  records. They do not certify the newly edited notes. No new blind or
  independent model review is claimed.

The [comparison records](../sources/textual_restoration/comparisons/samuel_controls.v1.json)
and [coverage records](../sources/textual_restoration/coverage/samuel_pilot.v1.json)
preserve these distinctions. Regression tests reject positive support claims
for the two disputed/unassigned entries and keep the Chronicles relationship
separate from Samuel manuscript evidence.

## Consequence for the approach

A transcription webpage's recent release date does not prove that it
incorporates every later correction to the edition it represents. Check
identification disputes, errata, and changes in an author's assessment before
using decisive readings. Hold unresolved evidence out of positive support;
do not replace one unexamined authority with another.

Next work: obtain and examine the full 2024 discussion and exact institutional
images; collate the relevant Greek manuscript traditions; continue the
1 Samuel 1:24 and 10:27-11:1 candidates. No generated image has been used as
manuscript evidence, and no critical Hebrew or English main-text selection is
promoted by this pass.

## 1 Samuel 14:41: later argument accessed — 2026-09-07

The [author-hosted 2024 article](https://www.academia.edu/119887795/Correcting_Some_Claims_of_LXX_Readings_in_the_Publication_of_the_Samuel_Scrolls_from_Qumran_DJD_XVII_)
now provides readable extracted text of section 5, pp. 36–41, including its
footnotes. This advances the earlier abstract-only review, but is **not** a
visual review of the PDF or its figures. The publisher PDF returned HTTP 403;
the author download link failed, and no local PDF was acquired.

Yardney's argument concentrates on line 2: the proposed aleph–vav fits poorly;
the reconstructed “and he said” lacks space for aleph and has an incompatible
medial mem shape. She leaves line 1 and the replacement identification open.
Crucially, footnote 53 still favors the longer prayer: repeated “Israel” could
have triggered omission, leaving the difficult Masoretic phrase. Her rejection
of the fragment therefore does not amount to rejection of the longer reading.

POB consequence: keep the fragment outside positive support and retain the
current translation provisionally. Omission from a longer Hebrew prayer and
expansion of a difficult shorter prayer remain competing explanations; this
pass does not settle them or establish exact retroverted Hebrew. The existing
reader note already distinguishes these issues, so it needs no new edit.

The remaining physical check is now specific: figures 40–44 against IAA
[B-359488](https://www.deadseascrolls.org.il/explore-the-archive/image/B-359488)
and historical PAM 43.072,
[B-284874](https://www.deadseascrolls.org.il/explore-the-archive/image/B-284874).
These are article-cited locators, not newly inspected images. Greek
manuscript-level comparison remains a separate source-selection gate.
Do not repeat abstract searches or the failed download routes without new
access evidence. No ImageGen, fresh transcription, independent review,
canonical change, or deployment occurred.

## October 16 full chapter review and distinct Greek forms

The [new evidence record](../sources/textual_restoration/comparisons/samuel14_41_greek_forms.2026-10-16.v1.json)
extends the earlier three-page dissertation check. A delegated reader read
Yardney's complete chapter 3, printed pp. 129–201 / PDF pp. 141–213, including
notes, and visually checked Figure 2, Table 12 and Figure 3. Root read the
specified argument and counterargument pages and visually checked Figure 2
and Table 12. This is a full chapter consultation, not a full-dissertation
reading or new manuscript decipherment.

**The chapter does not argue that a Greek translator invented the longer
prayer.** Yardney favors a longer Hebrew prayer and treats the shorter MT as
copying loss between repeated “Israel.” Her separate claim is that the earliest
Greek interpreted that longer prayer creatively. Her explicit statement on
p. 158 favors Urim/Thummim in the Hebrew Vorlage, not *tāmîm* as its better
reading. Rejecting 4Q52 fragment 2's identification in her later work therefore
must not be represented as rejection of the longer prayer. The fragment remains
excluded from positive support under the earlier disposition.

The actual [Bible Society Rahlfs–Hanhart display](https://www.die-bibel.de/bibel/LXX/1SA.14)
at 14:41 has conditional **εἰ** and **ἐν τῷ λαῷ**, “in the people.” Root also
visually read BMT printed pp. 45–46 / PDF pp. 61–62, including an enlarged
target. Its B-based continuous text instead has initial **ἤ**, lacks that
preposition, and has an additional **δὸς δή** before “to your people.” These
are published edition readings, not independently inspected codex pixels.

| Text under discussion | Relevant construction | Status and meaning |
| --- | --- | --- |
| Rahlfs–Hanhart selected text | Conditional opening; “in the people” | Alternative outcomes, conventionally understood as Urim versus Thummim. |
| BMT's B-based text | Question opening; “to your people”; extra command | Distinct printed wording; not identical to Rahlfs or Yardney's combined text. |
| Yardney's A/B | Combines preferred readings from A and B, removing B's extra command and correcting its verb | Her reconstructed Old Greek asks for an indication and then the people's exoneration. It is not a verbatim witness. |

Her argument on pp. 155–164 relates the requests to the stated result:
Saul/Jonathan are selected and the people cleared. She proposes that a translator
read the consonants תמים as “blamelessness,” making those outcomes explicit.
She acknowledges that selection already implies the requested indication
(p. 156 note 86); the alleged mismatch concerns what is explicitly said.
That proposed motive is an explanation, not an observed copying event.

Her Greek-priority argument on pp. 194–199 treats **ὁσιότης** as inherited in
the Antiochene and V forms even when their syntax restores the Hebrew sense.
Root directly checked the selected Greek **ἀλήθεια** equivalents at Exodus
28:30, Leviticus 8:8 and Deuteronomy 33:8 against local WLC. This supports the
Pentateuchal comparison, not a mandatory rule for another translator. The
chapter itself acknowledges the missing same-book Thummim control (p. 150
note 69). Its V text is reconstructed from apparatuses; its competing
Aejmelaeus text is a proposal quoted in 2017, not our fresh consultation of
the current critical apparatus. Priority therefore remains open.

**POB consequence:** retain source and main English provisionally, without
claiming renewed approval of “Give a perfect lot.” Yardney's pp. 133–134
challenge that supplied-noun interpretation directly; the existing note already
admits that “lot” is supplied. A separate English comparison should weigh the
short Hebrew phrase's grammar and contextual intelligibility. Any revised
reader disclosure should identify the selected Greek edition and distinguish
the other Greek constructions. No candidate is applied in this research step.
Earliest Greek, closest Hebrew rendering, reconstructed Hebrew wording and
English publication are four distinct decisions under the existing method.

## October 16 short Hebrew request and reader disclosure

The follow-up favors clearer disclosure, not a newly preferred main sentence.
The short pointed request **הָבָה תָמִים** leaves its precise force uncertain.
Neither an adjective label nor the absence of a written noun resolves that
uncertainty. The [application record](../sources/textual_restoration/applications/samuel14_41_reader.2026-10-16.v1.json)
pins the baseline, exact reviewed wording, controls and bounded review.

The named WLC controls distinguish constructions. Genesis 17:1 uses *tāmîm*
predicatively. Joshua 24:14, Judges 9:16/19 and Psalm 84:12 use it with **ב**
to express integrity in action; Psalm 15:2 has a bare form after “walking.”
Amos 5:10 is more directly useful for truth-conforming content: “one who
speaks *tāmîm*.” Psalm 85:13 has a giving verb with the substantive adjective
“what is good,” while 1 Samuel 14:40 has “do what is good in your eyes.”
These prevent a blanket rule that a nounless adjective must denote a person
or require an omitted noun. They do not reproduce Samuel's exact request.
Psalm references here follow Hebrew numbering: 84:12 and 85:13 correspond
to English 84:11 and 85:12. The XML morphology is editorial analysis, not
another witness.

Direct lexical and grammatical checks sharpen the distinction. BDB's complete
*tāmîm* entry, enhanced PDF pp. 2606–2607, includes a neuter/substantive use
with truth-conforming content. Its target cross-reference, however, points
to **תֹם** section 4, which proposes **Thummim instead of the pointed form**.
It is not direct certification of “perfect lot” or “answer honestly” at this
verse. [GKC section 118m–q](https://en.wikisource.org/wiki/Gesenius%27_Hebrew_Grammar/118)
describes manner accusatives generally; it does not adjudicate this request.

[Driver's 1913 second edition](https://archive.org/details/2ndednotesonhebr00drivuoft),
printed pp. 117–118 / PDF pp. 253–254, rejects the short-phrase renderings
and favors a longer Hebrew reconstruction from Greek. That is a substantive
objection, not an independently surviving Hebrew prayer. His printed argument
and footnote were visually checked alongside the BDB pages. Yardney's complete
pp. 133–134 were reread: her “answer honestly” takes its answering action
from the oracular context, rather than a separately written Hebrew verb.

| English option | What it interprets |
| --- | --- |
| Give a perfect lot | Supplies “lot” from the division and selection in verses 40–42; “perfect” describes the requested outcome. |
| Give honesty | Uses an abstract/substantive sense, but is awkward and underspecified in English. |
| Answer honestly | Makes the contextual answering action explicit; it is not a literal gloss of “give.” |
| Give a true answer | Supplies “answer” and selects a truth-content interpretation; not established as superior. |
| Give Thummim | Changes the interpretation/vocalization of the source consonants; not simply an English restatement of pointed WLC. |

The delegated Hebrew assessor independently checked the named corpus controls
and favored retaining the main sentence provisionally. Its subsequent exact
note/rationale review passed without factual corrections. It did not freshly
verify Driver/BDB pages, adjudicate source priority or conduct a blinded
whole-verse preference test. The reviewed note explains the supplied noun,
offers “Answer honestly” as an interpretation, and names Rahlfs–Hanhart for
the longer prayer. It retains the disputed-fragment qualification. The lexical
rationale preserves the historical HALOT label without inventing a fresh
consultation. No new source letters or generated-image evidence follow.

The reviewed disclosure and rationale are now applied locally. The Hebrew,
entire main English string, note marker/reason and other semantic fields are
unchanged. Superseded status, revision and agreement flags are preserved
verbatim with their baseline binding; the edited record is draft/needs-review,
not assigned the historical agreement score. The full 811-unit Samuel export
matches preflight exactly: only 14:41's note changes, and all 810 other units
are unchanged. This verifies the exported disclosure, not deployment or a new
claim that the retained main wording is optimal.
