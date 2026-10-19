# Exodus tabernacle reconstruction and surviving Hebrew controls

Date: 2026-10-19. Baseline: `58e3e17ec780af836f1db0629fd1f93450ce98c8`.

## Result

The numerical terminal-length argument for 4Q22 needs clarification before
POB uses it as a precise exclusion test for a shorter Exodus 35–40 account.
One published sum does not reproduce from its explicit terms; two intermediate
sums do. This is not a refutation of the longer-form reconstruction or evidence
that the shorter form was original. Published surviving Hebrew independently
supports particular longer-form content, without supplying every missing clause.
Keep POB's Hebrew and English unchanged pending the wider comparison.

## The argument being tested

Hila Dayfani's [2023 original article](https://www.aabner.org/ojs/index.php/beabs/article/view/1031),
*Material Reconstruction of 4Q22 in Aid of Literary Criticism of the Book of
Exodus*, 81–107, argues that reconstructed scroll capacity favors a longer
MT/SP-like account over a shorter Greek-like account. The model fills gaps
with Samaritan wording and a matching font; it does not recover missing ink.
It estimates a terminal length of 186–188 cm, assumes some column/margin
widths and an approximately 10 cm terminal blank, and treats the shorter
account as about two columns shorter (95–104). Its four-form history also
uses Old Latin Monacensis; this audit has not independently collated that text.

The [incense study](EXODUS_INCENSE_ALIGNMENT_2026-09-05.md) previously read
only 85–88 of this article. This continuation reads its complete text and
notes, including the different reconstruction argument, with full-page visual
checks of 91,93–94,99–104. The current ordinary publisher download is
byte-identical to the earlier PDF. A bounded erratum search and article-page
check found no correction; that is not proof that none exists elsewhere.

## Recomputed quantities

The full printed page 99 and footnote 29 visibly specify the descending series
10.9, 10.6, 10.3, …, 1 cm and print its sum as 188 cm. Exact decimal arithmetic
instead gives 34 terms and **202.3 cm**. Ending on the same lattice at 3.1 cm
gives 27 terms and 189.0 cm. The endpoint convention must therefore be explicit;
these calculations do not reproduce the stated 186–188 cm interval.

| Calculation | Recomputed result | Interpretation |
| --- | --- | --- |
| 11.5 + 11.8 + 12.1 + 12.4 + 12.7 | 60.5 cm | Reproduces the intermediate five-turn check |
| Ten terms from 10.9 down to 8.2, step 0.3 | 95.5 cm | Reproduces the intermediate ten-turn check |
| 34 terms from 10.9 down to 1.0, step 0.3 | 202.3 cm | Does not reproduce printed 188 |

This recipe reproduces the terminal calculation without floating-point error:

```python
from decimal import Decimal as D

terms = [D("10.9") - D("0.3") * i for i in range(34)]
assert terms[-1] == D("1.0")
assert sum(terms) == D("202.3")
```

The 14.3 cm difference from printed 188 is approximately one assumed
12.5 + 1.5 cm column pitch. It is consequently relevant to a two-column
discrimination, not merely a display-rounding issue. But **202.3 is the sum
of a printed model, not a newly measured scroll length**. An unreported
truncation, phase convention, transcription error or different underlying
calculation could explain the mismatch. The existing fragments and geometric
constraints must be refitted before assigning its effect to either literary
form. Increasing capacity alone cannot validate a shorter text; it also
increases the unused length for any fixed text.

More fundamentally, textual filling helps determine horizontal distances in
this reconstruction. Those fitted distances cannot be treated as independent
measurements of the very wording used to obtain them. This does not make
material reconstruction useless: secure margins, seams, repeated damage and
surviving text can constrain a model. The discriminating test must hold those
constraints fixed, declare uncertainty and fit competing text lengths under
the same rules. Verse counts alone are not a Hebrew character/space model.

## Actual Hebrew preservation

Root read the complete own-manuscript Qumran-Digital tables, not their linked
parallel texts, for 4Q22 columns 44–45 and 4Q17 fragment 1 ii. These are
published transcriptions, not fresh image decipherments.

The [4Q22 column 44 table](https://lexicon.qumran-digital.org/transcriptions/4Q22/2026-05-21/index.html#c292979)
has portions of Exodus 36:21–24 across five lines, including part of the
twenty-frames and southern-side wording. Much surrounding frame language is supplied;
one cannot quote all four verses as surviving. Column 45 continues with
parts of the ark/table account through 37:16. The direct text supports
particular content, not the unseen ending of Exodus or every SP reading.

The [4Q17 target row](https://lexicon.qumran-digital.org/transcriptions/4Q17/2026-05-21/index.html#c285977-i286014)
reads `ויעש את האורים ו[את התמים כאשר צוה יהוה את]`.
The Urim-making wording precedes the opening supply bracket; the following
Thummim and command-formula words are supplied. The next row preserves Moses
and part of the robe transition, so the placement is not inferred from a
search hit alone. This is positive Hebrew evidence for an extra Urim-making
clause, not separately visible evidence for every word of the reconstructed
pair. QDR's May 21 release is an edition date, not the date of the manuscript.

Current POB 39:21 moves from fastening the breastpiece to making the robe
at 39:22, without this clause. Its checked 36:20–24 retains the frame account;
37:25–29 retains incense-altar construction and oil/incense preparation;
40:24–27 retains lampstand and gold-altar placement. These observations do
not certify all their English or notes. Adding the Urim clause could explain
command fulfillment; omission, expansion and different literary forms still
require assessment before changing the declared Hebrew source.

## Decision and next evidence

Do not use this capacity argument as proof of exact missing wording or as
a new decisive source-priority vote. Neither its numerical mismatch nor a
locally preserved expansion establishes the earliest whole account. The next
useful work is the actual competing Greek/Old Latin text and apparatus,
especially the preserved-versus-supplied Monacensis distinction, plus an
equal-constraint reconstruction if the terminal calculation can be clarified.
Winter's opposing translation study was not acquired: the old journal routes
returned 404 and the new journal index supplied no full target. Its argument
is not represented as read. No repeated failed acquisition is warranted.

The [packet](../sources/textual_restoration/comparisons/exodus_tabernacle_reconstruction.2026-10-19.v1.json)
records inputs, calculations, exact row IDs and private inspection scope.
No new general checker, source/English application, reader note, generated
restoration image or canon proposal follows. The PDF workflow caught the
printed numerical mismatch; the documentation workflow preserves the earlier
bounded incense result rather than retroactively turning it into a full reading.
