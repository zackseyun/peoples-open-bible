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
| 5:14; f1i:1 | כיא / כאשר: conjunction interpretation open. |
| 6:3–4; f1ii+3_6i:1–2 | Reordered stillborn comparison; raised corrections and deleted שמו; corrected הלך / ילך. The [bounded follow-up](#ecclesiastes-6-3-and-6-4-correction-stages-2026-10-05) retains source/English and separates correction stages. |
| 6:6; same:3 | ואם לוא / ואלו: conditional/spelling analysis needed; do not infer negation mechanically. |
| 6:8; same:6–7 | כמה / כי מה; following traces unresolved. |
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
