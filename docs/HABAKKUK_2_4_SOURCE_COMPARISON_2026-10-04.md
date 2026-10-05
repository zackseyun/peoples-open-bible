# Habakkuk source comparison and English implications

Habakkuk 2:4 comparison, begun 2026-10-04 local time. Application baseline:
`f7865a66bf4f93dd4a775efe316a979daa6704b6`. The question is whether published
Hebrew and Greek evidence justifies replacing POB's **his faithfulness**.
Decision: retain the WLC source and marker-free English provisionally, while
adding separate source-variant and lexical disclosures. This is a negative
source adjudication with a reader improvement, not a new decipherment or a
demonstrated earliest wording. The [controlling method](TEXTUAL_ADJUDICATION_METHOD.md)
continues to govern the wider all-book comparison.

## Hebrew preservation check

The baseline record has באמונתו, a third-person possessive, in the declared
WLC text. Its SHA256 is
`fa1a8428bd49045a3353c40b3e95d99ec1794a2735062ee8cf804609fb1fca33`.
The published Qumran-Digital release is dated 2026-05-21, not a manuscript date.
Complete physical-line context, rather than extracted biblical parallels,
determines whether the suffix survives.

| Published witness and locator | Decisive preservation context | Implication |
|---|---|---|
| [1QpHab](https://lexicon.qumran-digital.org/transcriptions/1QpHab/2026-05-21/index.html), VII 14–17; VIII 1–3 | VII 17 prints `[-- וצדיק באמונתו יחיה]`; the whole biblical colon is supplied | The surviving commentary discusses adherents' trust/fidelity toward the Teacher of Righteousness; this is indirect interpretation evidence, not preserved biblical suffix ink |
| [Mur 88](https://lexicon.qumran-digital.org/transcriptions/Mur._88/2026-05-21/index.html), XVIII 19–23, especially 21 | `[לא ישרה נפשו בו וצדיק באמונתו יחיה ואף כי היין בוגד גב]ר֯ י[היר]` | The bracket closes in the following verse; the entire disputed colon remains supplied |
| [4Q82](https://lexicon.qumran-digital.org/transcriptions/4Q82/2026-05-21/index.html), fragment 102 line 3 | `[הנה עפלה לא] י֯ש֯ר֯ה נפש֯[ו בו וצדיק באמונתו יחיה ]` | Some preceding wording survives uncertainly, but the disputed colon does not |

These are published transcriptions, not new observations of manuscript images.
The three supplied clauses must not become three independent votes for his.
The pesher may adapt a lemma, so its commentary cannot uniquely restore one.
No attested omission follows from these physical gaps. The root web reader
failed on Mur 88 and 4Q82; ordinary public HTML retrieval succeeded and exposed
their own full-line brackets. This was not a fresh acquisition of images.

## Greek forms and the edition boundary

[Swete volume III, third edition 1905](https://archive.org/details/theoldtestamenti03swetuoft),
printed pp. 59–60 (PDF 83–84), and preface v–ix (PDF 9–13), were inspected.
Its Vaticanus-oriented main text has `ὁ δὲ δίκαιος ἐκ πίστεώς μου ζήσεται`:
the righteous will live by my faith/faithfulness. Its verse 4 apparatus reports
`δικαιος] δικαιος μου A`. That unit reports an addition after righteous;
it does **not**, by itself, report removal of the later my. A higher-resolution
check corrected the initial overreading of this note as complete relocation.
No C attribution is present in this Swete unit. A modern C-group must not be
silently identified as a physical codex or another independent early witness.

[Martin Meiser's scholarly chapter](https://publikationen.uni-tuebingen.de/xmlui/bitstream/handle/10900/162331/Meiser_141a.pdf?isAllowed=y&sequence=1),
section 3.6, printed pp. 321–323 (PDF 13–15), separately reports a my-righteous
form, a my-faith form and a possessive-free form. These are the chapter's
edition-derived reports, not our manuscript collations. Footnote 93 reports
8HevXIIgr, “Col. VII 30,” as `καὶ δίκαιος ἐν πίστει αὐτοῦ ζήσεται`.
The paper was successfully downloaded after the agent's web reader returned
403. The underlying DJD transcription, preservation brackets, hand and photograph
remain unchecked; its third person is reported Greek revision evidence, not
newly verified Hebrew or an independent early Hebrew branch. The institutional
watermark date is not used as the chapter's publication year.

[Timothy H. Lim's 2015 accepted manuscript](https://www.pure.ed.ac.uk/ws/portalfiles/portal/22024443/LIM_2015.pdf),
author pp. 12–17 (PDF 13–18), supplies scholarly arguments, not additional
manuscripts. He acknowledges the missing pesher colon, proposes restoration
from its commentary, and discusses possible vav/yod confusion and NT influence
on Greek transmission. These are hypotheses, not observed copying events.
His alternate-position reports are kept separate from Swete's single addition
unit; their exact witness relationships are not resolved here. No fresh
Jerome, modern critical-apparatus or manuscript-image collation is claimed.

## Source decision and English tradeoff

Retain third-person Hebrew as the declared working base, not as a demonstrated
historical victory. The strongest objection is that Greek my could reflect a
different Hebrew ending rather than merely interpretation. Proposed באמונתי
is a back-translation hypothesis, not attested Hebrew in the consulted material.
An earlier physical witness has no chronological advantage on a missing suffix;
removing the modest age preference does not change this provisional retention.
Greek revision toward Hebrew is also a possible explanation of the reported
third-person Greek, so its antiquity alone cannot defeat the competing form.

The paragraph's waiting for the vision and contrast with arrogance support
steadfast fidelity as a reasonable reading of the current Hebrew. Faith or
trust remains possible; retaining faithfulness emphasizes fidelity and may
underemphasize trust. Neither gloss alone settles later faith-and-works debates.
The candidate therefore retains the full marker-free sentence and adds two
notes, anchored separately to his and faithfulness. This is not approval of
every clause or neighboring verse, and no new lexicon consultation is claimed.
Other first-half Greek differences are not spliced into a reconstructed Hebrew.

Current stored SBLGNT controls distinguish the quotations: Romans 1:17 and
Galatians 3:11 lack a possessive in this quoted colon; Hebrews 10:38 places
my with righteous one. These are checks of existing POB source fields, not
a new NT witness census. Their theological contexts and citation forms must
not be flattened into one Hebrew reconstruction. No NT record is changed.

## Review application and reopening conditions

The [frozen candidate](../sources/textual_restoration/applications/habakkuk2_4_disclosure_candidate.2026-10-04.v1.yaml)
is now applied byte-for-byte to the draft record. It preserves historical revision
objects and does not invent a missing ai_draft. One independent contextual
candidate/application assessment passed this exact disclosure scope, not the
entire verse's translation, historical priority or publication. It independently
reproduced the source/main/history and reader invariants; no blinded claim is made.
The [application receipt](../sources/textual_restoration/applications/habakkuk2_4_disclosure_application.2026-10-04.v1.json)
pins the baseline, candidate, assessment, source PDFs and actual checks.
The baseline lacks ai_draft and translation philosophy. Adding a justified
philosophy field does not repair historical generation provenance; full-schema
approval cannot be claimed while ai_draft remains missing.

Actual before/after export retains all three chapters and 56 expected verse IDs;
only 2:4's markers and notes differ. All new fields validate, 20 reader-note
tests and 18 footnote-audit tests pass, and the full reader-corpus validator
exits successfully. The latter is not full generation-schema or historical
approval. Source/main English and original historical objects remain unchanged;
the three NT controls remain byte-identical. Active status is draft/needs-review.
The initial direct audit-test command failed because PYTHONPATH was absent;
the corrected invocation passed without an implementation repair.

Reopen source priority only for discriminating direct-language preservation,
the actual DJD VIII Habakkuk transcription/apparatus/photo and corrections,
or an actually consulted modern Greek apparatus/manuscript resolving the
forms and their transmission. DJD VIII is Tov with Kraft and Parsons,
*The Greek Minor Prophets Scroll from Nahal Hever*, 1990. Do not repeat failed
access without a changed route, or repeat these same comparisons for agreement.
No fresh ink, autograph, complete source coverage, canon change, public deployment
or publication approval follows from this bounded case.

Qumran-Digital is © DFG project 465277421, CC BY-SA 4.0, based on the earlier
Qumran-Wörterbuch/Abegg text. The bounded ancient excerpts above retain that
attribution; this is not full-edition redistribution or a CC0 relicensing.
Swete is an old public-domain edition. The Lim and Meiser PDFs retain their
copyrights and are local study copies, not files added to this repository.
PDF hashes and actual review/check outcomes are recorded in the receipt.
