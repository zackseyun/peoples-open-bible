# Exodus incense altar: order is not wording

Checked: 2026-09-05. Published/digital-text comparison by Codex, not a fresh
image reading, independent blind review, or completed historical adjudication.

## Result

The whole-Torah screen's ten unmatched Exodus labels represent relocated
instructions in this Samaritan reference, not missing instructions. An explicit
11-segment map connects its extended Exodus 26:35 to WLC 26:35 and 30:1–10.

| Control | Incense instructions | Mercy-seat placement clause corresponding to MT 30:6 |
|---|---|---|
| WLC / Masoretic base | 30:1–10 | Present |
| Pinned Samaritan transcription | Within extended 26:35, after the table/lampstand instruction | Absent |
| Pinned Rahlfs Greek control | 30:1–10 | Absent |

Passage order and clause wording require separate decisions. This is an
edition/transcription comparison, not a census of manuscript support. Locally
similar shorter wording does not establish identical Hebrew exemplars behind
the two traditions.

## Reproducible alignment

The [metadata receipt](../sources/textual_restoration/discovery/exodus_incense_alignment.v1.json)
records unique, editor-selected instruction boundaries. All spans are zero-based,
half-open offsets in raw Samaritan sign text, including spaces. They exactly
reassemble all 721 characters, including its one trailing space.

| WLC target | SP character span | Consonantal comparison |
|---|---|---|
| 26:35 | 0–92 | Different |
| 30:1 | 92–132 | Different |
| 30:2 | 132–186 | Different |
| 30:3 | 186–260 | Equal |
| 30:4 | 260–354 | Different |
| 30:5 | 354–392 | Equal |
| 30:6 | 392–447 | Different |
| 30:7 | 447–508 | Different |
| 30:8 | 508–577 | Different |
| 30:9 | 577–628 | Equal |
| 30:10 | 628–721 | Different |

Differences include spelling, not only substantive variants. Normalization
ignores pointing and word division but preserves matres and final letter forms.
POB's source is checked against WLC, allowing paragraph signs only where its
XML explicitly encodes them. The final pe in 30:10 is such a sign, not an extra
lexical letter or a reason to change the source.

SP input: DT-UCPH 7.1.3, commit
`2f2120286ac48d4ff3d04e0107e33efd864aa9e1`; Exodus uses Chester Beatty Library
751, not the separate Rylands manuscript. Greek input: `lxx-morph`, commit
`c91f6b1e8fb3ba37df701e6ae31f675ace71a2b2`, file
`db/seeds/lxx_morph/exodus.json`. Feature files, WLC books, Greek input, segments,
and current POB verse files have content hashes in the receipt. The external
SP corpus is not vendored or relicensed; the receipt exports metadata only.

```bash
.venv/bin/python tools/textual_restoration/build_samaritan_screen.py /path/to/sp/tf/7.1.3 --incense-alignment --greek-json /path/to/lxx-morph/db/seeds/lxx_morph/exodus.json
.venv/bin/python tools/textual_restoration/build_samaritan_screen.py /path/to/sp/tf/7.1.3 --incense-alignment --greek-json /path/to/lxx-morph/db/seeds/lxx_morph/exodus.json --verify-only
.venv/bin/python -m unittest tests.test_samaritan_screen tests.test_ot_witness_registry
```

## Qumran evidence: preserve its limits

The versioned 4Q11 transcription, fragments 30 ii–34, lines 10–11, presents the
table/lampstand instruction followed by the entrance-screen instruction
(26:35→36), with damaged and supplied letters marked. This supports the
published arrangement without an intervening incense block, not a fresh
inspection of the manuscript photograph.
[Qumran-Digital, version 2026-05-21](https://lexicon.qumran-digital.org/transcriptions/4Q11/2026-05-21/index.html?v=2026-05-21).

Dayfani's section 3 reports chapter-26 placement for 4Q22 and SP, and its absence
there in 4Q11. Chapter 30 is not preserved in 4Q11; that witness does not establish
where it originally placed the block. Neither this order evidence nor a general
family label establishes its wording at 30:6. Direct 4Q22 transcription/material
verification remains pending: our 4Q22 statement rests on this scholarly report,
not a newly inspected edition or image.
[Hila Dayfani, Textus 30 (2021), 105–129, section 3](https://doi.org/10.1163/2589255X-BJA10017).

## Actual POB impact

In [Exodus 30:6](../translation/ot/exodus/030/006.yaml), an existing note offered
“atonement cover” at the ark-of-testimony marker. It belongs to “mercy seat.”
The corrected notes distinguish those terms, disclose the shorter Samaritan/
standard Greek reading, and explain retention of MT's wording and order. The
stale lexical entry now matches the displayed “before.” Hebrew source and
English words are unchanged; markers, notes and explanatory metadata changed.

The UBS handbook also identifies the mercy seat as the ark's cover and discusses
the shorter Greek reading. Its unspecified additional Hebrew manuscripts are
not converted into identified witnesses in our ledger.
[UBS commentary on Exodus 30:6](https://tips.translation.bible/story/translation-commentary-on-exod-306/).

`EXO.30.6.mercy-seat-clause` is the twelfth formal OT comparison case. Its three
digital controls add no physical coverage record. It remains unadjudicated;
the registry still has 22 entries and 19 passage-coverage records.

## Next decision gates

Inspect the appropriate Hebrew/Greek apparatuses, Samaritan critical edition,
and direct 4Q22 publication before assigning broader support. Test omission
through repeated phrasing, explanatory expansion, and local translation
technique against context. Natural furniture order could reflect editorial
rearrangement; a shorter clause is not necessarily earlier. Do not combine
preferred order and preferred wording into a synthetic source without an
explicit literary target and a coherent transmission argument.

This pass closes a mapping problem and a reader-note defect, not the historical
source-selection question. It does not recover previously unread text.

## Direct attestation follow up

October 5, 2026, against main `d8475036b0d2abb6382c9acb4a78b42abad68143`:
the direct published-transcription gate is now partly closed. The historical
priority of either order and the wording at 30:6 remain unresolved. No source,
English, reader note, application receipt or frozen alignment is changed.

The complete own-manuscript rows of QDR's 4Q22 column 30
(`table#c291064 tr.line-verse`) place portions identified as 30:10 in lines
12–13 before portions of 27:1–3 in lines 17–19. Column 29 ends with 26:30;
the first ten lines of column 30 and the immediate insertion point after 26:35
are missing. The surviving pieces support the published arrangement, not an
intact inspected transition or an independently verified physical join.
Line 12's closing bracket follows a supplied lead-in: do not count its complete
annual-atonement wording as visible ink. The positive fragments include `על`
and the horn-word prefix in line 12, generations wording in line 13, and
corner wording in line 18, with the transcription's uncertain letters retained.
**30:6 is not preserved here.** Its absence from these rows supports neither
the longer clause nor its omission.
[QDR 4Q22, version 2026-05-21](https://lexicon.qumran-digital.org/transcriptions/4Q22/2026-05-21/index.html#c291064-i291068).

Dayfani's 2023 material study, printed pages 85–88 (PDF pages 6–9), supplies
the relevant reconstruction context. It locates the incense instructions in
chapter 26 in column XXX. It also explicitly uses Samaritan text to fill gaps,
while warning that 4Q22 need not have identical wording. A digital-font
reconstruction is therefore not a second witness to the missing 30:6 clause.
The complete printed page 86 and Figure I were visually inspected; the figure
was not used to claim a fresh letter reading or independently prove joins.
[Dayfani, Material Reconstruction of 4Q22, 2023](https://www.aabner.org/ojs/index.php/beabs/article/download/1031/1002).

QDR's 4Q11 own rows `c281526-i281610` and `c281526-i281622` preserve portions
of the table/lampstand wording and the entrance-screen wording on consecutive
physical lines 10–11. This supports no intervening incense block there,
without establishing its location elsewhere or its 30:6 wording. Related
4Q22 and Samaritan forms must not become two automatically independent votes.
[QDR 4Q11](https://lexicon.qumran-digital.org/transcriptions/4Q11/2026-05-21/index.html#c281526-i281610).

The complete Cambridge 1909 printed page 257 (PDF page 115), including its
apparatus, was read and visually inspected. Its selected Greek text lacks the
mercy-seat clause, but its apparatus reports longer Greek forms with mercy-seat
wording. Thus the earlier **selected Greek control** result is reproducible;
it is not unanimity of Greek manuscripts. The lowercase `m` reading and the
uppercase `M` reading in the separate bottom apparatus are different units,
not interchangeable labels or identical equivalents of the full MT clause.
The Genesis 1906 apparatus conventions, printed page viii (PDF page 16),
identify the addition sign, marginal notation and Hexaplaric asterisk. Some
long-form reports carry marginal or asterisk qualifications. Their manuscript
identities, hands and transmission relationships require a separate apparatus
assessment before they can support a source-priority decision; this pass does
not enumerate a complete Greek support list. Longer Greek forms could reflect
alignment to Hebrew rather than independent evidence for earlier Hebrew.
[Cambridge Exodus and Leviticus 1909](https://tmcdaniel.palmerseminary.edu/Brooke%26McLean/LXX_Brooke%26McLean_1-2.pdf).

The whole Hebrew controls remain intact: all eleven segment spans and hashes
and their current POB record pins reproduce the frozen receipt. The disputed
MT clause has 18 consonants, but the aligned Samaritan segment differs by 16
because its surrounding words contain two additional vowel letters. It is not
an exact consonantal match to MT with only the clause deleted. MT's repeated
testimony endings provide a plausible skipping mechanism; explanatory
expansion linking the altar to the meeting place provides the strongest
alternative. Neither plausibility alone establishes direction of change.

The source outcome is **provisional retention**, with historical priority held;
the main-English outcome is **unchanged**. Ancient alternative order is a real
literary comparison result, not evidence to delete an unpreserved clause, a
newly deciphered reading or a reason to expand the canon. Reopen for
manuscript-specific apparatus evidence or material evidence that distinguishes
the alternatives, not another model preference vote.

Private input hashes for this follow-up: QDR 4Q22
`90a832f021579ac4544984c827b2c3b0014c117c6f09ceddab741d9346cca313`;
QDR 4Q11 `1ff2f554b2880fdeda2d8db680a68ecdd856a12c6d4c5a4741ea2c9378a7900c`;
Dayfani 2023 `19daf46d9014dc99b59aa4f065d2dccd9b7671a0231c5797f32086eb6cad5d30`;
Cambridge Exodus 1909 `8d63914f75fd1e4539fb953fa8ec50223be6b41e91509ea37c401e03d32d16c9`;
Cambridge Genesis 1906 `c5031defb2e2f8de3e4db1f47244f0565ea001a529e3f924680e4f3c7ead1519`.
These pin consulted publications, not fresh ancient photographs. No licensed
corpus or PDF is vendored.
