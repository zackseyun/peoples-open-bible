# Habakkuk pesher quotation map and comparison leads

The complete published 1QpHab text supplies several concrete comparison leads
that the biblical-only discovery index missed. The strongest concern wine
versus wealth at 2:5, a net versus a sword at 1:17, and exposure of
uncircumcision versus an intoxication expression at 2:16. These could change
POB's meaning, but their historical priority is not yet decided. No Hebrew,
English or reader notes change in this map.

## Quotation coverage and boundaries

The October 6, 2026 [Qumran Digital publication](https://lexicon.qumran-digital.org/transcriptions/1QpHab/2026-10-06/index.html?v=2026-10-06)
contains 206 primary rows across thirteen columns. Root read all primary rows,
the displayed alternative branches and the corresponding 37 local source and
English records in Habakkuk 1–2. Two read-only subtasks separately covered
columns I–VII, 117 rows, and VIII–XIII, 89 rows. This is a complete screen of
that publication, not a complete Habakkuk witness census or new decipherment.
Its modern release date is not the ancient object's date.

The [machine-readable map](../sources/textual_restoration/comparisons/habakkuk_pesher_quotation_map.2026-10-12.v1.json)
records 46 bounded quotation segments, including repeated quotations and a
locally adapted excerpt. Endpoints identify primary digital word slots in
physical row order, not arithmetic ID ranges or independent manuscript votes.
Boundaries follow citation formulas, dividers and interpretation transitions;
damaged/supplied boundaries remain qualified. The map locates material
associated with all 37 Habakkuk 1–2 verse labels, not 37 complete surviving
verses. It makes no Habakkuk 3 coverage claim.

Two fully supplied quotations lack Habakkuk parallel links: I.4 at 1:2 and
III.17 at 1:10. Conversely, IX.7 links the remnant-of-peoples phrase to 2:8,
but that phrase belongs to commentary; the next lemma starts at IX.8. These
positive examples show why reference links cannot define quotation boundaries.
Some rows begin in commentary and end in quotation, or the reverse.

The familiar 2:4 righteous/faithfulness/life colon is wholly supplied at
VII.17 in this publication. Its associated commentary survives at VIII.1–3,
but that does not make the missing biblical pronoun visible. At 1:5, the
address remains supplied. The new map changes coverage, not those earlier
preservation judgments.

## Meaning bearing comparisons

These are newly collated project leads, not newly discovered variants. The
published wording and the possible English effects remain separate claims.

| Passage and locus | Published primary reading versus current WLC | Possible English consequence and strongest caution |
|---|---|---|
| 2:16 XI.9, word 10278 | והרעל versus והערל | Investigate staggering/intoxication versus POB's “show your uncircumcision.” The word has no supply or correction markup; XI.13 nevertheless interprets an uncircumcised heart. That commentary is a competing interpretive control, not replacement lemma letters. |
| 2:5 VIII.3, word 9874 | הון versus היין | Wealth versus POB's wine. The following commentary repeatedly concerns amassed wealth, which can reflect its reading or suggest interpretive adaptation. |
| 1:17 VI.8, word 9681 | חרבו versus חרמו | Sword versus POB's net. Commentary subsequently invokes a sword, but it is dependent interpretation rather than another witness. The opening also differs in its interrogative wording. |
| 1:11 IV.9, word 9458 | וישם versus ואשם | A placing/attribution construction versus becoming guilty needs complete-clause grammatical comparison. In the IV.13 repetition, a proposed verb is only an alternative restoration of a gap. |
| 2:15 XI.3, words 10237 and 10243 | חמתו and מועדיהם versus חמתך and מעוריהם | His versus your, and appointed times versus nakedness. The Day of Atonement commentary creates a strong local-adaptation possibility; evaluate the suffix and noun separately. |

Other preserved leads are למוכיחו at 1:12, תביטו at 1:13, למשל בו at 1:14
and מצורי at 2:1. The unpointed spelling at 1:13 does not automatically choose
a plural grammatical analysis. At 1:14, compare the actual merged/segmented
forms rather than declaring a standalone negation omission. The receipt keeps
their exact word locators. At 2:17, primary יחתה and alternative וחתה remain
distinct; the preceding beasts clause is supplied, so the complete subject–verb
construction is not surviving attestation.

The altered clause order at 1:15–16 is also worth examining, but much of its
bridge wording is supplied. XII.6–7's introduced 2:17 excerpt shortens and
reorders the earlier lemma. Such repetitions can show interpretation or local
adaptation without creating independent support for earliest wording.

## Digital reading safeguards

The new [parallel-reference indexer](../tools/textual_restoration/index_published_parallels.py)
exports only locators, IDs and displayed reference joins. It identifies 1,405
primary word slots, 260 parallel reference groups and 101 Hab-linked primary
rows. These count digital slots and links, not preserved words or quotations.
Its output explicitly says quotation roles and preservation are unassessed.
The manual map supplies the separately reasoned boundaries.

Nine primary rows contain alternative-reading branches. Their repeated
`data-word-id` values must not become extra primary words. Nested alternatives
at XII.15, a deleted letter at VIII.14, the inserted word at IX.8 and the modern
editorial addition within XI.9 word 10274 require separate reading layers.
In particular, the editorial addition in word 10274 does not contaminate the
independently unqualified word 10278 used for the 2:16 lead. The navigation
indexer does not flatten any of these into textual evidence.

The actual publisher HTML has 269 unclosed decorative spans and one redundant
final table close. The parser records these bounded repairs and rejects
structural truncation, duplicate primary IDs and joins outside the current row.
No missing row/table closures are inferred. Repair counts and the normalized
metadata digest are pinned in the receipt; a clean HTML parse is not evidence
of a clean manuscript reading.

## Next source judgments and reader work

Begin with 2:16: compare the exact lexical forms, surrounding drinking and
shame imagery, preserved Mur88 wording, selected Greek and actual apparatus,
then test quotation adaptation and the uncircumcision commentary. Compare the
transmission explanations before choosing Hebrew or an English candidate.
The same process applies to 2:5 and 1:17; familiar scholarly alternatives and
model agreement are not substitutes for those controls.

A separate factual reader defect at 2:1 is worth correcting after its own
application check: the inward-speech note is anchored after rampart, and the
complaint/reproof note after speak in me. This map identifies the mismatch
but neither applies it nor transfers prior approval to a changed record.

ImageGen remains display-only. No generated letters, fresh manuscript pixels,
critical-text selection, canon expansion or corpus-wide English improvement
is claimed. Broader source acquisition and varied image calibration continue.

## Inputs rights and verification

Baseline: `faea235b7f9d8fcc43d1643833d34890812671c1`; method 2.0.4. The receipt
pins all 37 inspected POB files and the source HTML SHA256
`5e4c2a2fe7af80df2c3609d2cd9123246ae9beada802c30eb4dea919e5b27891`.
The acquired HTML remains outside Git. Qumran Digital attributes the text to
DFG project 465277421, Qumran Wörterbuch and its Abegg precursor, with
CC-BY-SA 4.0 terms; no whole transcription is imported or relicensed as POB.
The separately pinned QDR snapshot retains its own CC-BY-NC 4.0 terms.

Ten new offline tests cover navigation/primary separation, split references,
alternative IDs, display ellipses, malformed structure, foreign joins and map
claim limits. The final focused run passed 20 tests in 3.422 seconds, including
four existing reference-capability and six Habakkuk reader-application tests.
Root reproduced the actual HTML digest, metadata counts and all 46 ordered,
nonoverlapping endpoints; all 37 current POB inputs remain byte-identical.

One bounded independent review passed all 206 primary rows, nine alternative
rows, all 46 boundaries and the 37 current/historical input hashes. It reproduced
the digests and counts, passed the same 20 tests and six additional adversarial
guard checks, and corrected the first-half row count to 117. Its originally
reviewed hashes are retained in the receipt; the review completion additions
do not introduce new readings. This verifies published navigation, boundaries
and lead attestation, not manuscript pixels, historical priority or English
approval. Git publication and its integrity jobs remain separate milestones.
