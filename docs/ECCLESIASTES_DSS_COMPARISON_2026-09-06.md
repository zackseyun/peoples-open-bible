# Ecclesiastes: two-record DSS comparison

2026-09-06. Published-reading screen, not image restoration or all-source collation.
Previous goal turn was progress: Lamentations 1:7's disclosure was applied and
pushed. This pass broadens actual comparison coverage without reopening that case.

## Scope and reproducibility

Root read all 36 published 4Q109 line records and compared all 26 QDR-tagged
canonical verse contexts. One bounded agent read all eight published 4Q110 lines,
all eleven older QDR lines and corresponding canonical sources. This is divided
work, not independent replication. Total: **44 published line records**, versus
47 QDR records with 564 tagged word records and 36 distinct verse tags. Tags
include supply and uncertain assignments, not 36 preserved verses.

| Record | QDR units and line IDs | Published coverage |
|---|---|---|
| 4Q109 | f1i:1–8; f2:1; f1ii+3_6i:1–7,11–21; f1iii+6ii_7:1–5,17–20 | 36 records; 385 QDR tagged words |
| 4Q110 | f1_3:1–11 | 8 records; 179 QDR tagged words; mapping below |

References use Hebrew/current POB numbering; chapter 5 differs from many English
editions. The existing [book map](../sources/textual_restoration/discovery/hebrew_bible_book_map.v1.json)
remains a discovery index, not preserved-text evidence. The earlier
[wisdom-book audit](WISDOM_BOOK_SOURCE_AUDIT_2026-08-28.md) assessed English against
WLC; it does not certify a completed ancient-witness comparison.

Input SHA256 pins:

- QDR `qdr.1.1.biblical.json`: `3b90610ab70a737aeb329b3d35af0d941b354d374503866d3dd8b30b914c8295`.
- Local `pob-lxx-morph/db/seeds/lxx_morph/ecclesiastes.json`: `0ec029295874df2ef0d6b6742abf8cb62dc045136187eed19a73e6d9a3a1da24`.
- All 222 canonical Ecclesiastes YAML records: manifest `fd2097c18575f3fd7f6afcee9abeb933b57872e57e48ec46dd554de9225faa06`.

Manifest rule: SHA256 of UTF-8 compact, sorted-key JSON mapping repository-relative
YAML paths to file SHA256. These pins identify inspected inputs, not manuscript dates.

## 4Q109: consequential and controlled differences

From the [versioned published transcription](https://lexicon.qumran-digital.org/transcriptions/4Q109/2026-05-21/index.html?v=2026-05-21):

| Verse; unit/line | Published target against WLC; disposition |
|---|---|
| 5:14; f1i:1 | כיא / כאשר: the [particle comparison](#ecclesiastes-5-14-and-6-8-particles-2026-10-05) retains source/main English provisionally; historical function/priority held. |
| 6:3–4; f1ii+3_6i:1–2 | Reordered stillborn comparison; raised corrections and deleted שמו; corrected הלך / ילך. The [bounded follow-up](#ecclesiastes-6-3-and-6-4-correction-stages-2026-10-05) retains source/English and separates correction stages. |
| 6:6; same:3 | ואם לוא / ואלו: conditional/spelling analysis needed; do not infer negation mechanically. |
| 6:8; same:6–7 | כמה / כי מה: the [particle comparison](#ecclesiastes-5-14-and-6-8-particles-2026-10-05) tests question/affirmation and differing Greek forms; retains source/main English provisionally. Following traces unresolved. |
| 7:2; same:15–16 | [ש]מחה / משתה; כול סוף / סוף כל. Noun preference below; remainder not silently normalized. |
| 7:4–5; same:17–19 | בית / בבית; גערות / גערת; corrected מלשמוע / מאיש שמע. Crossed-out material not recovered. |
| 7:7; f1iii+6ii_7:2 | ויעוה֯ / ויאבד: verb candidate, uncertain final letter. |
| 7:19; same:18–19 | תעזר / תעז; following complement partly supplied/uncertain. |

Other readable lines mostly agree or show spelling/conjunction differences.
The supplied 6:12 line 11 and the trace tagged 7:18 cannot establish omissions or
readings. This is a comparison of published readings, not newly observed ink.

## 4Q110: do not promote older contextual reconstruction

The [published transcription](https://lexicon.qumran-digital.org/transcriptions/4Q110/2026-05-21/index.html?v=2026-05-21)
has eight records labeled fragment 1–2. By surviving text, published lines 1–8
correspond to QDR f1_3 lines 4–11. QDR lines 1–3 have no counterpart on this
page; this does not prove that a physical fragment was lost or reidentified.

Published 1–6 cover surviving runs at 1:10–14, with ordinary spelling differences
and אשר נעשו against שנעשו, equivalent relative constructions. Line 7 has only
גבו֯ between gaps: QDR's supplied 1:15–16 context does not establish a readable
“mighty” variant. Line 8 is an unidentified trace, not the lamed and 1:16 context
in QDR. Neither final line has a secure published verse assignment. No source
change follows; retain upstream identities separately pending editorial explanation.

## Local Greek controls and one source decision

Root read selected Greek surfaces at 5:14; 6:3–4,6,8; 7:2,4–5,7,19, ignoring
generated morphology/confidence. These are selected-text controls, not individual
manuscript votes or a completed critical apparatus. At 7:2 the control has πότου,
whereas 7:4 has εὐφροσύνης: it preserves the feasting/joy distinction. At 7:5 it
retains a man hearing, and at 7:7 its verb expresses destruction, although its
following phrase differs from POB. At 7:19 its helping verb fits the scroll's
root more directly but can interpret the WLC's strengthening sense; no exact
Hebrew spelling follows from that semantic fit. At 6:6 it presents a condition
without negating living; that does not resolve the scroll's orthography.

**7:2 noun decision:** prefer WLC משתה provisionally, with moderate confidence
in this limited preference. The scroll's joy-word could assimilate to 7:4's
nearby בית שמחה. The Greek control preserves the two distinct nouns. Strongest
objection: feasting could instead sharpen a more general joy-word, or the Greek
could already depend on that sharpened form. Neither the date nor the selected
Greek text proves direction. Do not turn this noun judgment into approval of
every clause in 7:2 or every reading of either manuscript.

Full-verse source-distinction check:

```json
{"source_distinction_checks": [{
  "candidate_id": "eccl7_2-feasting-versus-joy",
  "disposition": "retain_after_comparison",
  "source_evidence": "WLC בית משתה (7:2), בית שמחה (7:4); published 4Q109 [בית ש]מחה at 7:2. The supplied prefix/context must remain distinguished from preserved מחה.",
  "proposed_text": "It is better to go to a house of mourning than to go to a house of feasting[a], because that is the end of every person, and the living should take it to heart.",
  "alternative_text": "It is better to go to a house of mourning than to go to a house of joy[a], because that is the end of every person, and the living should take it to heart.",
  "rationale": "Retain the event-specific feasting against the broader emotional joy, preserving the source contrast with 7:4. This alternative tests only the noun; it is not a full translation of the scroll's differently ordered clause. The preexisting note a concerns every person and is misplaced; this pass does not repair it or certify complete verse quality."
}]}
```

## Stop, remaining candidates and limits

No canonical source, English, notes or historical approvals changed. The 7:2
noun question is parked unless apparatus evidence or a locus-specific transmission
argument discriminates the directions; another copy of the same text is insufficient.
The other candidates remain screened, not adjudicated. In particular, contextual
similarity to corruption language in Exodus 23:8 and Deuteronomy 16:19 does not
by itself select Ecclesiastes 7:7's verb: neither parallel has that exact verb.
The surviving correction at 7:5 needs edition/hand analysis before historical
claims; 7:19 needs versional discrimination; 6:6 needs conditional-orthography analysis.

A Brill THB preview acquisition returned HTTP 403; no preview body was read.
Search snippets were not used as scholarly verdicts. No new PDF/image reading,
validator, judge loop, canonical application or deployment occurred. This pass
does not establish exhaustive Ecclesiastes, OT or NT source coverage.

Verification passed: both source pins; QDR 36+11 records, 385+179 tagged words
and 36 unique tags; all 222 canonical file hashes unchanged; exact current
full-verse comparison text; selected Greek noun anchors; local report links;
`git diff --check`. Published 36+8 line coverage was read directly, not inferred
from those QDR counts. No reader export was needed for this documentation-only pass.

## Ecclesiastes 6 3 and 6 4 correction stages 2026 10 05

Against main `bddf986a5cc965618892372b518c250c709ecff3`, retain current
pointed WLC and POB English provisionally for this unit. This completes an
unfinished screen candidate with a reasoned retain decision, not a novel
reading or proof of earliest wording. The [comparison record](../sources/textual_restoration/comparisons/ecclesiastes6_3_4_followup.2026-10-05.v1.json)
pins the actual inputs, stage assemblies, review and limits.

Root read current source/English 6:1–8 and full records 6:3–4. In the complete
[published 4Q109 context](https://lexicon.qumran-digital.org/transcriptions/4Q109/2026-05-21/index.html),
fragment 1 ii+3–6 i lines 1–2 report the closing comparison and correction;
adjacent lines 3–5 were also inspected. Raised additions are not supplied gap
letters. The deleted name-word has a doubtful mem; its raised replacement is
printed without that uncertainty. These are published readings, not root's
new observation of manuscript marks. Attribution: DFG Qumran-Digital project
465277421, CC BY-SA 4.0; the release date does not date the ancient copy.

| State or control | Connected target wording | What it establishes |
|---|---|---|
| WLC 6:3 close | אמרתי טוב ממנו הנפל | Stillborn child better off than the man |
| Reported 4Q109 6:3 close | אמרתי טוב הנפל ממנו | Changed order, same comparison |
| Reported base-line 6:4 before correction | כי בהבל בה ובחושך שמ֯ו יכסה | Shorter arrival/name sequence; doubtful mem retained |
| Reported corrected 6:4 | כי בהבל בה ובחושך הלך ובחושך שמו יכסה | Raised הלך ובחושך שמו, with base-line שמ֯ו deleted; one name-word, not two |

The last two rows analytically assemble the published stages; they are not
new manuscript transcriptions or separate ancient witnesses. Earlier clauses
of 6:3 lie outside this surviving segment, not in an attested omission. Do not
delete the man's children, long life, unsatisfied appetite or burial clause.
Final-he בה can represent the arrival verb's spelling. Raised הלך, unlike
WLC ילך, permits a plausible perfect went, but an unpointed participial
analysis remains possible. The consonants do not certify manuscript vowels.
This aspect question is not resolved by calling the whole verse identical.

Connected diagnostic English, not replacement POB: WLC, I said: better than
he is the stillborn child. For it came in futility, goes in darkness, and in
darkness its name is covered. Corrected scroll, assuming perfect departure:
I said: the stillborn child is better than he. For it came in futility, went
in darkness, and in darkness its name is covered. The shorter pre-correction
stage lacks the departure clause. Current generic-present POB remains a
defensible rendering of the general comparison; no necessary English correction
or doctrinal implication follows from this bounded contrast.

Root visually inspected Swete II's complete printed 492, PDF 510, including
apparatus, and preface viii, PDF 10; sigla PDF 18 was read textually. The
[public scan](https://archive.org/download/theoldtestamenti03swetuoft_202003/oldtestamentingr02swet.pdf)
has SHA256 `945c5b15bf0f9dfc93890b28ee5b66a388acbf4597f1f2be5430ac6cba9c30b0`.
Its Vaticanus-oriented main text retains arrival, departure and name-covering:
ἦλθεν is aorist, πορεύεται present, καλυφθήσεται future passive. Departure is
not Greek future. No 6:4 variant entry occurs on the inspected page; that is
not proof of Greek unanimity or a complete modern apparatus consultation.
The Greek's present departure does not establish the scroll's vocalization.

Inference: repeated darkness phrases make a copying skip and later repair a
plausible account of the shorter state. Contrary inference: a coherent shorter
exemplar could have received expansion or assimilation through correction.
Published additions/deletions establish stages, not the corrector's hand,
exemplar or motive. Neither older wording, shorter wording nor correction
automatically wins. DJD/BHQ/Göttingen full apparatus and direct hand analysis
remain unconsulted; source priority remains unresolved.

One bounded same-model independent assessment supports qualified retention
and the aspect/correction limits, not scholarly approval. Its adjacent longer
mouth-suffix claim was excluded: לפיהו matches segmented WLC ל/פי/הו.
The separate 6:6 conditional wording was not adjudicated. Reopen this unit
only for passage-specific edition/hand evidence or an argument discriminating
skip-and-repair from expansion, not another digital copy or preference vote.

All 222 Ecclesiastes records retain the earlier manifest
`fd2097c18575f3fd7f6afcee9abeb933b57872e57e48ec46dd554de9225faa06`.
The two target hashes and protected unrelated Genizah hash are recorded and
unchanged. This is documentation-only work; no new corpus-test run, export
change, publication, ImageGen evidence, fresh decipherment or canon change.
Existing aggregate validation debt is not erased by this comparison.

## Ecclesiastes 6 6 conditional spelling 2026 10 05

Against `a8283d5071172476c7f5eebb4c4a45bff7356fbf`, retain pointed WLC
and current positive-life English provisionally. The reported scroll spelling
does not require changing Even if he should live to If he did not live.
This completes the conditional-orthography question left open above, not
the whole-book comparison or earliest-spelling adjudication.

The complete [published 4Q109 context](https://lexicon.qumran-digital.org/transcriptions/4Q109/2026-05-21/index.html),
fragment 1 ii+3–6 i lines 3–4, gives the opening `ואם לוא חיה` against
WLC `ואלו חיה`. No restoration, uncertainty or correction mark is displayed
on these opening words. The separate negative before seeing good remains.
This is an attributed published reading from DFG Qumran-Digital, project
465277421, CC BY-SA 4.0, not a fresh observation of manuscript ink or vowels.

| Interpretation of the opening | Connected diagnostic English | Strongest local consideration |
|---|---|---|
| Positive conditional, full אם לו(א) corresponding to contracted אלו | Even if he lived a thousand years twice over and experienced no good, do not all go to one place? | Escalates the many-years hypothesis in 6:3 despite the stillborn child's greater rest in 6:4–5 |
| Conditional אם followed by negative לוא | And if he did not live a thousand years twice over, and experienced no good, do not all go to one place? | Adjacent לוא tokens are negative; denial of that duration remains grammatically and contextually possible |

These are diagnostic renderings, not new ancient transcriptions or replacement
POB. The negative reading need not deny all life: it can deny the stated extreme
duration, or continue attention to the child. Its contextual weakness is that
denying such longevity makes an unexpectedly unremarkable condition. The
positive reading's weakness is that the unpointed spelling does not uniquely
identify the particle. Root provisionally prefers the positive escalation;
neither possibility is decided by counting repeated negative spellings.

[GKC 159l, m, x](https://en.wikisource.org/wiki/Gesenius%27_Hebrew_Grammar/159)
recognizes positive לו/לוא, derives אלו from אם לו, and discusses this verse's
hypothetical clause with a question as consequence. It cautions against a
mechanical distinction between conditional particles. Current pointed Hebrew
at Isaiah 63:19 has positive לוּא; Esther 7:4 has positive אִלּוּ. These controls
make the full positive analysis plausible; they do not establish the scroll's
pronunciation, exact meaning or spelling priority. This grammar was read as
the public-domain web transcription, not checked against a native printed page.

Root visually checked Swete II's complete printed 492–493, PDF 510–511.
Its B-based opening has καὶ εἰ ἔζησεν, positive conditional life, followed by
negated goodness. Its καθόδους is not a simple Greek numeral twice. The B main
text lacks an explicit all in the final question; the second page's apparatus
reports a plural departure verb in א and τα παντα in א/A/C. These controls
must not become a uniform Greek text or unique Hebrew retroversion. They support
the positive interpretation without selecting the exact Hebrew particle spelling.

Root acquired the official [NETS Ecclesiast PDF](https://ccat.sas.upenn.edu/nets/edition/26-eccles-nets.pdf)
after reading its actual index link, and visually checked PDF 1–2 and 6,
printed 648–649 and 653. Gentry's Rahlfs-based translation gives positive life
and renders the duration as recurrences, not twice. Its introduction's statement
that no fully critical edition existed belongs to that older publication:
the [Göttingen project](https://septuaginta.uni-goettingen.de/publications/septuaginta/)
lists Gentry's Ecclesiastes XI/2 in 2019 and Text History in 2022. A lawful
26-page publisher preview was acquired, but the modern 6:6 critical text and
apparatus were not consulted. No modern-edition agreement is claimed.

One bounded read-only same-model assessment by
`/root/malachi2_16_source_assessment` supports qualified retention and tests
the negative alternative. It read Hebrew context, the published transcription
and grammar; the Greek page inspection is root's, not a duplicated agent scan
claim. This is not blinded English testing, specialist approval or full-verse
optimality certification. No source, main English, notes or prior review flags
change. Reopen for consulted DJD discussion, discriminating comparative usage
of full אם לו/לוא, or local version/transmission evidence; exact earlier spelling
remains unresolved. No ImageGen, fresh decipherment or canon implication.

Verification: all 222 Ecclesiastes files retain manifest
`fd2097c18575f3fd7f6afcee9abeb933b57872e57e48ec46dd554de9225faa06`;
6:6 remains `392ad64cfd2367caf5b5586bd40f9d4b468db37346a8045e0d72273b3af5eaed`.
Context 6:3–7 and Isaiah/Esther controls were read from current YAML, not inferred
from old reviews. Swete retains the preceding section's recorded hash; NETS is
`883474c8b532e6523f217284c9ba77e75d428db4c7e710b82692b613ae04bd25`.
The protected unrelated Genizah file remains unchanged. This is documentation
only; no new whole-corpus test, reader export or public deployment is claimed.

## Ecclesiastes 7 7 and 7 19 verbs 2026 10 05

Against main `62e4822f79cbdeb8f351258211859737c2b26264`, retain WLC and
main English provisionally at both verses. Correct two active grammatical
rationales at 7:19; do not amend ancient letters to manufacture a contribution.
The published scroll alternatives deserve disclosure, but no new reader notes
are applied in this metadata-only repair. Their exact wording and export review
remain a separate implementation step.

Root and one bounded source assessment read the complete
[published 4Q109 context](https://lexicon.qumran-digital.org/transcriptions/4Q109/2026-05-21/index.html),
frg. 1 iii+6 ii–7. At 7:7, line 2 prints `חכם ויעוה֯`, with the final he
doubtful; the following heart and gift words are supplied. The preceding
oppression clause is also supplied. MT's destruction verb contrasts with
the reported distortion verb, not with a wholly preserved alternative saying.
Diagnostic second clauses are a gift destroys the heart and, assuming the
supplied continuation, a gift perverts the heart. Neither is new POB wording.

The directly inspected official [NET notes](https://bible.org/download/netbible/ondemand/bybook/ecc.pdf),
PDF 26 / printed 1208, identify MT's Piel destruction verb and the scroll's
Piel distortion verb, noting overlapping moral-corruption meanings. Their
Muilenburg citation was not independently consulted. Earlier direct Hebrew
supports taking the alternative seriously; it could clarify an opaque idiom,
or MT could intensify earlier distortion. These are competing inferences,
not demonstrated scribal motives or a secure transmission direction.

Root visually checked Swete II, printed 494–495 / PDF 512–513, including
apparatus. The 7:7 content aligns to its numbered 7:8: Greek `ἀπόλλυσι`
supports destruction, but the following nobility phrase differs from MT's
gift/bribe clause. Its whole wording must not become corroboration of every
MT word. NETS, printed 653 / PDF 6, uses a Rahlfs-based courage phrase;
different Greek edition controls are not one uniform witness.

At 7:19, published line 18 has `ה֯[חכמה] תעזר א֯[ת …]` with damaged
alternative object reconstruction; the comparison is supplied. The helping
verb is printed without an uncertainty mark. Wisdom and its wise recipient
do not survive completely, nor do ten rulers. Greek `βοηθήσει τῷ σοφῷ`
in Swete's numbered 7:20 and NETS's helping interpretation are compatible
with the scroll, but can also interpret MT's strength-for-beneficiary syntax.
They do not uniquely recover a Hebrew resh. Clarification toward a common
helping verb competes with loss of resh and complement adjustment; the damaged
complement prevents securely establishing that complete transition.

Root acquired and visually read the [Hebrew College enhanced BDB](https://hebrewcollege.edu/wp-content/uploads/2018/10/BDB.pdf),
PDF 1781–1782, the complete עזז entry. It explicitly assigns `תָּעֹז`,
Ecclesiastes 7:19, to Qal imperfect 3fs and explains wisdom as strong for
the wise. The Hiphil section is separate. The current YAML's two causative
rationales are therefore repaired. Gives strength remains a defensible English
interpretation of Qal predication with a beneficiary, not preservation of a
causative stem. This is not a blinded English preference result or certification
that the unchanged whole verse is optimal. Historical claims remain in history.

The source assessor `/root/malachi2_16_source_assessment` independently read
YAML, context, the published transcription and NET notes. Its assessment supports
qualified retention and the grammatical repair; it did not independently read
BDB or root's Greek scans. A separate full-record application critique checks
the frozen metadata candidate, not historical priority. It returned PASS for
metadata repair only after checking schema, exact archives and preservation.
No specialist approval,
fresh ink reading, ImageGen evidence, novel decipherment or canon inference.
Reopen source priority for consulted DJD discussion, discriminating local
transmission evidence or the modern Greek target apparatus; the available
Göttingen preview does not contain that apparatus.

### Metadata repair scope

Only `translation/ot/ecclesiastes/007/019.yaml` changes among the 222 book
records. Before: `013fb552fce4435ec604263539c540a00bbb9e17d1e54a07c9dc25fb74429056`.
Frozen after: `8b5de07e231d0f0d2a3ad525ab68a3b52f0a91e5acce51d127d275f641588f91`.
Source, main English, notes, original AI provenance and historical revisions
remain equal to baseline. Old status, revision-pass, cross-check and source-audit
values are archived verbatim; old scores do not approve edited rationales.
The active record is draft and needs review, not publication-approved.

PDF pins: BDB `9784a8d3b14dd7d4d8bcde138185f1dac86c896c59d32533868b03feab165ce3`;
NET notes `b0f6dfc69819e0954c3945de8ac7ae1b99ffb96e3c28584300c8885c450c2ef8`.
Swete and NETS retain the preceding section's recorded pins. The BDB PDF page
numbers refer to this enhanced digital layout, not original printed pagination.

Actual verification: the verse schema passes; two focused regression tests pass,
including the 12-chapter, 222-verse Ecclesiastes reader export with unchanged
7:19 wording and notes. A baseline comparison verifies all preserved fields,
both affected lexical entries and all four archived values. All other 221 book
records remain byte-identical. The new book manifest is
`44c90f01db68addca5c0a3a40093ddb62f235a96d7ccfe0905b67313cca240eb`.
The protected unrelated Genizah file remains byte-identical. These scoped checks
do not rerun or erase the five previously recorded aggregate registry drifts,
nor certify a deployed reader or a published critical edition.

### Subsequent reader disclosure application

The preceding metadata-only comparison is now followed by a separately reviewed
note application against `5322b57039d54736c05be223a97314f378aae357`.
PR 29 merged at `2f50163c9cf5c750d282bb28c067602220e20a00` after both
exact-head corpus-integrity checks succeeded; that merge delivered the rationale
repair, not these later notes. The [application receipt](../sources/textual_restoration/applications/ecclesiastes7_verb_disclosures.2026-10-05.v1.json)
records the exact two new candidates, evidence and actual scoped verification.

At 7:7, a new note after destroys discloses the reported distortion verb,
doubtful final letter and supplied heart/gift wording. The existing gift and
heart note bodies are unchanged; the heart marker moves before punctuation.
At 7:19, a note after strength distinguishes the retained strength predication
from the reported helping verb and the scroll's damaged or supplied context.
Neither note treats a reconstructed whole clause as surviving ink or selects
earliest wording. Main English with markers removed and the complete pointed
source stay unchanged. No new blinded main-English comparison is claimed.

One independent full-record application critique returned PASS for both exact
note candidates, checking the complete published context, schema, archival
values and actual export. It is a same-model critique, not specialist review.
At 7:7, old review metadata is archived verbatim and active status becomes
draft/needs_review. At 7:19, those states and the earlier history remain, with
the preceding metadata revision pass archived separately. Original generation,
lexical decisions and historical revisions are preserved in both records.

Actual checks pass: source/main-wording and archive preservation against Git,
note-marker matching, both full schemas, two rationale regressions and 25 reader
footnote tests. The real export retains 12 chapters and 222 verses with exact
note bodies and anchors. Exactly two book records change and 220 remain identical;
the receipt gives before/after hashes and book manifests. The protected unrelated
Genizah file is unchanged and excluded from staging. Existing aggregate guard
debt is recorded, not silently repinned or claimed clean. No public deployment,
novel decipherment, ImageGen evidence, source-priority victory or canon change.

This completes the rationale and reader-disclosure application for these two
verb comparisons. Historical priority remains held for the specific evidence
named above. Continue with a different unresolved substantive comparison rather
than revisiting this completed application without new evidence.

## Ecclesiastes 7 5 hearing construction 2026 10 05

Retain pointed WLC provisionally, but make its explicit generic listener visible
in English: It is better to hear the rebuke of a wise man than for a man to hear
the song of fools. This is a narrow source-pattern rendering preference, not
a new doctrine, a different ancient reading or proof that the previous English
misstated the general listening preference. The [comparison and receipt](../sources/textual_restoration/applications/ecclesiastes7_5_listener.2026-10-05.v1.json)
records the candidates, actual assessment, disagreement, frozen application and
verification against `d64ab5dececfc8822346fae83812b57355f9aa28`.

In complete [published 4Q109 context](https://lexicon.qumran-digital.org/transcriptions/4Q109/2026-05-21/index.html),
frg. 1 ii+3–6 i, line 18 prints `טוב לשמוע גערות`. Line 19 has
`[חכם מ]ל` followed by raised shin and `מוע`, unidentified crossed-out signs,
then `שיר כסילים`. Both the wise-man wording and comparative mem are supplied.
The raised shin is a reported correction, not a bracketed restoration. The
deleted signs cannot establish an erased man, an earlier complete sentence,
a corrector's hand, exemplar or motive. Attribution remains DFG Qumran-Digital,
project 465277421, CC BY-SA 4.0; publication date does not date the ancient copy.

The natural plural analysis rebukes differs from pointed MT's singular rebuke;
the unpointed scroll does not certify ancient vowels. Assuming the supplied
words, the final scroll comparison has two hearing infinitives, whereas MT
moves from to hear to a man hearing. Connected diagnostic scroll English is
It is better to hear a wise man's rebukes than to hear the song of fools. It
does not claim that every word of that sentence survives. A pre-correction
sentence remains unassembled rather than filled from familiar MT.

The strongest scroll argument is early direct Hebrew reporting a coherent
balanced comparison. Contrary inference: an uneven infinitive/person comparison
could be smoothed and the rebuke pluralized. In the opposite direction, MT
could elaborate an earlier balanced saying by making the listener explicit,
or transmit a different formulation. Context 7:4–6 accommodates both. Chronology
gives the scroll serious attention, not automatic priority. Neither copying
direction is demonstrated; retain the base while earliest construction remains
held. Reopen for consulted DJD correction/hand discussion or discriminating
transmission/version evidence, not another copy of this transcription.

Root visually read Swete II's complete printed 494 / PDF 512, including apparatus.
Greek numbered 7:6 aligns to Hebrew 7:5. Its singular rebuke and
`ὑπὲρ ἄνδρα ἀκούοντα` preserve the explicit listener construction. No unit-6
variant entry appears on that page; this is not Greek unanimity or consultation
of the modern Göttingen apparatus. Greek wording supports the construction,
not uniquely recoverable Hebrew spelling or historical victory for every MT word.
Root also visually inspected official NET notes, printed 1207 / PDF 25: hearing,
wise rebuke and song/praise/entertainment interpretation. These are translator
arguments, not a new ancient witness or proof of different source letters.

The source assessor provisionally favored a C-type construction, which makes a
man listening explicit through English being-language; its diagnostic sentence
uses the song of fools rather than C's shorter fools' song. A fresh-context reviewer,
without tools or candidate identities, compared A, B and C against fixed Hebrew,
context, policy and rubric. It narrowly preferred B, than for a man to hear.
A, the previous balanced infinitives, preserves practical meaning and is crisper,
but smooths a real structural feature. B makes the participant visible while
still recasting the participle; its asymmetry can briefly suggest a subject
change. C makes being that kind of person more conspicuous and is cumbersome.
Root selects B under source-pattern priority and explains the generic listener
in a note. This is one identity-withheld review with fixed order, not randomized
testing, cross-family confirmation or universally optimal-English certification.

### Application and limits

A new note after rebuke discloses the qualified plural and corrected hearing
construction; another after man explains the MT participle and generic listener.
Old translation, note, lexical and review metadata are archived exactly. Original
generation and both historical revisions remain, including the old identical
before/after entry that claimed restoration; a new append records the actual
change. Two active rationales now describe what the English really expresses.
The active record is draft/needs_review, not approved by old agreement scores.
One full-record independent critique passed the exact candidate only; it does
not decide source priority or confer specialist/publication approval.

Before verse hash: `c55c978f1f7b1aea0d7323a0693d9286b1e9ff8f9b258d1bb994f765e31179b5`.
After: `04251412b26caea560bfff6576f1f7060764412727b0009fb53c3405ec8252f0`.
Actual schema, complete archival equality, source/generation preservation and
marker checks pass. The real export retains 12 chapters and 222 IDs with exact
target English and notes; only 7:5 changes, with 221 book records byte-identical.
All 26 reader-footnote tests and two rationale regression tests pass, including
the new exact-candidate reader check; receipt manifests, local links and whitespace
also pass. These are scoped verification, not new whole-registry certification.
The receipt records both book manifests and the preserved unrelated Genizah pin.
Existing aggregate registry debt remains disclosed, not repinned. No fresh ink,
ImageGen evidence, novel discovery, canon change or deployed-reader verification.

## Ecclesiastes 5 14 and 6 8 particles 2026 10 05

Completed a bounded meaning comparison against main
`050ebd6a8329617f765c394073ccfc6a02e0f9ba`, not another readiness review.
**Retain pointed Hebrew and current main English provisionally at both targets.**
The particles admit alternatives worth disclosing, but neither a spelling
difference nor a selected Greek form settles the earliest connected argument.
This pass changes no verse, reader note, metadata or historical approval.

Root inspected POB 5:13–16 and 6:7–9, the complete surrounding
[published 4Q109 transcription](https://lexicon.qumran-digital.org/transcriptions/4Q109/2026-05-21/index.html),
and native complete PDF pages below, including their apparatus/footnotes.
The transcription is attributed to DFG Qumran-Digital, project 465277421,
under CC BY-SA 4.0. Its 2026 release date is not the date of the ancient copy.
No fresh scroll pixels, newly commissioned transcription or model-family
replication is claimed.

### The birth and departure comparison

At 5:14, fragment 1 i line 1 reports unmarked `כיא` against MT `כאשר`.
Line 2 supplies the entire birth/naked-return sequence before `כ֯שבא`;
the latter's initial kaf is doubtful. Line 3 supplies most of the nothing-carried
clause before surviving `דו`. Thus published particle attestation must not
become a claim that the whole scroll sentence survives.

Current English starts As he came from his mother's womb, naked he will return,
going as he came. Assuming the published supplied clauses, a diagnostic
For he came from his mother's womb; naked he will return, going as he came
would make the transition explanatory rather than initially comparative.
Indeed is another diagnostic. Neither is a verbatim translation of a fully
preserved scroll sentence. The later arrival/departure comparison can remain
under either construction, and 5:13–16 still describes lost wealth, empty hands
and futile gain. Do not infer a new theology of death from the particle alone.

Primary grammar permits causal `כי` in
[Gesenius 158b](https://en.wikisource.org/wiki/Gesenius%27_Hebrew_Grammar/158._Causal_Clauses),
corroborative use in [148d](https://en.wikisource.org/wiki/Gesenius%27_Hebrew_Grammar/148._Exclamations),
and temporal use alongside `כאשר` in
[164d](https://en.wikisource.org/wiki/Gesenius%27_Hebrew_Grammar/164._Temporal_Clauses).
These establish possible functions, not the function of this particular `כיא`.
Do not force causal English solely by substituting a dictionary gloss.

Swete II, printed 491/PDF 509, selects comparative `καθὼς` at local 5:14,
aligned by the mother's-womb clause; the inspected apparatus has no variant
entry for that opener. This is an edition-level observation, not a claim of
unanimous Greek manuscripts. NETS printed 652/PDF 5 and NET printed 1204/PDF 22
(English 5:15) also render a comparison; those translations are not additional
ancient votes. MT's comparative could be clarified into an explanatory particle,
or MT could reinforce a comparison already expressed later. Both directions
remain hypotheses. The early reported scroll form receives weight, not an
automatic victory; without that chronological preference, retention still follows
from the absence of a discriminating transmission argument. Current As faithfully
renders the retained source; no necessary English correction follows.

### The wise person's advantage

At 6:8, fragment 1 ii+3–6 i line 6 preserves published `כמה יותר לחכם מן֯`.
The comparative nun is doubtful; fool, poor-person question and knowing are
supplied. Line 7 has unidentified traces and supplied the living, not a secure
complete conduct clause. The unpointed `כמה` can invite a how-much question
or an exclamation. [BDB, מה 4c](https://biblehub.com/bdb/4100.htm) documents
interrogative and exclamatory uses, including Job 21:17's rhetorically minimal
frequency. A positive amount is not entailed by the expression.

There is consequential Greek variation. Swete II, printed 493/PDF 511, selects
`ὅτι περισσεία τῷ σοφῷ ὑπὲρ τὸν ἄφρονα`, followed by `διότι ὁ πένης οἶδεν`
and the walking-before-life clause. It lacks an explicit interrogative here
and naturally admits a positive assertion plus an explanation. Its verse-8
apparatus reports added `τίς` after `ὅτι`, with the printed corrected-Sinaiticus,
A and C sigla; exact correction chronology and broader relationships are not
adjudicated. The native sigla page, PDF 18, identifies A as Alexandrinus,
C as Ephraemi and B as Vaticanus. NETS printed 653/PDF 6 renders a question for the wise-person
clause but an explanatory poor-person clause. Do not collapse these controls
into one uniform Greek witness supporting MT's two questions.

The positive countercase is stronger than the particle alone: a Hebrew form
capable of exclamation and an affirmative Greek form can converge in meaning.
Diagnostic English for that interpretation is How much advantage the wise
person has over the fool! The comparative target fool is supplied in the scroll;
the complete explanatory poor-person clause is attested in Greek, not established
as surviving Hebrew. This is no unique retroversion of Greek to `כמה`.
In 6:7–9, practical wisdom can offer relative advantage while appetite remains
unsatisfied and the passage ends in vapor. Conversely, the question can challenge
lasting gain without denying every practical benefit. NET printed 1206/PDF 24,
notes 12–14, supports that limited rather than absolute denial; its commentary
is an interpretation, not another manuscript.

Either an affirmative Greek construction could clarify difficult Hebrew questions,
or an interrogative could be added in Greek to align with an interrogative Hebrew
reading. A hypothetical yod omission between `כי מה` and `כמה` also needs local
scribal parallels before it can explain priority. None of these directions is
proved here. The source assessor initially recommended retention, then explicitly
strengthened the positive countercase after root supplied the newly inspected
Greek distinction. The revised conclusion remains provisional retention, not
unanimity manufactured by a repeated preference vote. The early Hebrew evidence
matters, but removing its chronological advantage would not resolve this hold.

### Verification and reopening evidence

At 5:14, reopen for consulted DJD spelling/spacing and clause-restoration arguments
or discriminating versional/translation-practice evidence for the particle's
function. At 6:8, prioritize the modern critical apparatus, exact Greek hand
and relationship evidence, and local interrogative translation practice before
choosing a positive whole-verse reading. DJD and the modern target apparatus
remain unconsulted. These are specific historical holds, not a request for
another general readiness or consensus review.

The scoped comparison is complete; qualified reader disclosures are justified
but not applied or export-verified here. Published attestation and source-priority
confidence remain separate. One independent source-document critique passed
the frozen factual/scope claims, including the Greek apparatus distinction;
it did not certify historical priority, fresh ink or the root's hash checks.
No ImageGen evidence, novel decipherment, canon
expansion or scholarly publication follows.

Inputs and unchanged outputs:

- 5:14 YAML: `7421ba0e52477704551d30e2e6b86111643c88d9c367b58e42542c0719f4420b`.
- 6:8 YAML: `a5fa117fa1066db2b176d230eaf15d16852d5f12122e0454e2ca36d5f197e1b9`.
- All 222 Ecclesiastes files: manifest `d4f6b107d262cdfa8871dffd9ec6ebbe9ad76c90a117082b03d62ec4b2ad2ff5`, using the rule above.
- [Swete II scan](https://archive.org/download/theoldtestamenti03swetuoft_202003/oldtestamentingr02swet.pdf): `945c5b15bf0f9dfc93890b28ee5b66a388acbf4597f1f2be5430ac6cba9c30b0`.
- [NETS Ecclesiastes](https://ccat.sas.upenn.edu/nets/edition/26-eccles-nets.pdf): `883474c8b532e6523f217284c9ba77e75d428db4c7e710b82692b613ae04bd25`.
- [Official NET notes](https://bible.org/download/netbible/ondemand/bybook/ecc.pdf): `b0f6dfc69819e0954c3945de8ac7ae1b99ffb96e3c28584300c8885c450c2ef8`.

Actual scoped verification passed: all 222 verse hashes and both target pins,
protected unrelated Genizah hash, local file links, documentation-only diff
scope and whitespace. No corpus/export rerun is needed when every verse byte
remains unchanged.
Existing broader registry debt is neither repaired nor silently repinned.
