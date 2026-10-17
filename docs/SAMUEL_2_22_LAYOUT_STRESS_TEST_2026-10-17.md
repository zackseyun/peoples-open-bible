# 1 Samuel 2:22 layout stress test

Date: 2026-10-17. Baseline: `16d3193fbe86773b959454631ec91bb2e839d202`.
Follow-up to the [image and intertext controls](SAMUEL_2_22_IMAGE_AND_INTERTEXT_FOLLOWUP_2026-10-17.md).

## Result

A common-line calculation supports the edition's short reconstruction, but
does not yet reproduce it from independently measured manuscript coordinates.
The exact long clause tested would require **92 letter-plus-space units** where
the edition reconstructs **48**. That is a substantial density problem, not a
newly recovered omission. The shorter reading remains provisionally preferred;
no source, English, note or approval change is applied.

## Physical constraints and their authority

DJD XVII printed **16–17 / PDF 39–40**, read completely in text and images,
describes column III as preserving its top and lateral margins and reports an
inscribed width of **9 cm**. It also warns of shrinkage and markedly different
column widths elsewhere. Thus a whole-scroll average is inappropriate. These
are **published physical observations**, not dimensions newly measured here.
Its statement about 43 lines does not make their entire wording surviving ink.

The edition's table 3 supplies letter-and-space counts, including reconstructed
wording. They must not be relabeled an independent sample of fully preserved
lines or an empirical maximum capacity. In particular, table 3's 48 for the
disputed line already incorporates the short reconstruction.

The [QDR primary rows](https://lexicon.qumran-digital.org/transcriptions/4Q51/2026-05-21/index.html?v=2026-05-21#c317847-i317979)
place `לבני ישרא֯ל֯ ו֯[יאמר להם למה]` on line 14 and
`תעשו֯[ן כדברים האל]ה` at the beginning of line 15. The following word is
therefore not merely a conjectural text ending on a distant detached fragment.
The native photograph shows the upper column's adjacent lines, but the lost
left end of line 14 is not restored ink. QDR and DJD describe the same witness.

## The same-input comparison

The count removes editorial brackets/uncertainty marks and uses one ordinary
space between words. This normalization is only for calculation; it does not
upgrade supplies into letters. The shared line is the edition's reconstruction,
not WLC's different opening and not a new diplomatic transcription:

`וישמע את אשר עושים בניו לבני ישראל ויאמר להם למה`

Insert the exact previously recorded MT consonantal clause before `ויאמר`:

`ואת אשר ישכבון את הנשים הצבאות פתח אהל מועד`

| Candidate with the same surrounding wording | Letters | Spaces | Units |
| --- | ---: | ---: | ---: |
| Short reconstructed line | 39 | 9 | 48 |
| Same line plus the specified long clause | 74 | 18 | 92 |
| Difference | 35 | 9 | 44 |

The extra joining space accounts for the ninth added space. This is not a
comparison between two differently normalized full verses. Given the published
line-15 identification and ordinary continuous writing, the insertion must fit
before its preserved beginning; it cannot simply spill into an invented extra
line without displacing that anchor.

For reproducibility, table 3's complete column-III sequence, lines 1–43, is:

```text
47,51,48,50,46,-,50,48,45,44,47,48,47,48,45,50,49,50,50,-,-,
47,48,47,49,54,48,50,53,51,51,49,47,47,48,48,48,50,-,47,52,50,47
```

Excluding line 14 and the four dashes leaves **38** counts, ranging **44–54**.
The widest count is a comparison value, not a hard physical ceiling. Under an
explicit equal-average-unit-width model, 92 units would need about **1.704×**
the width used by 54 units, or an average advance **0.587×** as large at the
same width. Increasing the assumed width by 10%, 20%, 30% or 50% gives capacities
of 59.4, 64.8, 70.2 or 81 units, still below 92. These are sensitivity scenarios,
not measured shrinkage ranges, character widths or confidence percentages.

Even an illustrative five-unit reduction of the long candidate leaves 87,
requiring average advance about 0.621× the 54-unit comparison. That artificial
perturbation is not an attested alternate spelling. Conversely, different
letters and spaces occupy different widths; counting alone cannot establish
the minimum physical width of this particular clause.

## What would independently settle the local capacity

The calculation exposes what a long-form reconstruction must explain under
the published arrangement. It is not independent confirmation of that arrangement.
A decisive image-based test still needs validated lateral-margin positions,
documented joins/deformation between the target and surviving margin, and
advance measurements for the actual letter/space mixture from the same hand.
Both candidates must use the same constraints. The newly consulted introduction
narrows the next task to testing the reported margin transfer and local writing
density; searching for a generic scroll-wide width is no longer appropriate.

Neither a failure of this particular long-line model nor successful short-line
fitting proves which reading was earliest in Samuel's transmission. A copy can
omit an earlier clause. Josephus and the positive long Greek branches remain
part of that separate historical question. ImageGen cannot supply the lost
margin, joins or letters as physical evidence.

## Retained evidence

Private sources remain at the root recorded in the predecessor packet. The
existing DJD PDF SHA256 is
`6866ffbfa230c44dc439dfaef8f229cd41219acfe31d6d9478d4e6002a70604d`;
the pinned QDR HTML is
`7460cc778d390185c93449d1799294d219c12cbeb71005cb0bf286e768016068`.
The fresh public QDR reader confirms the target primary rows, not a full
release comparison. Existing original-photo tiles were inspected without editing.

New complete-page reading derivatives, rendered with `pdftoppm -f 39 -l 40
-scale-to 2400 -png`, are:

| Private path | Bytes | SHA256 |
| --- | ---: | --- |
| `tmp/pdfs/samuel2-22-root/djd-layout-039.png` | 554934 | `f0719236f5861a305d88e5081451911910f2cc450769e055196ca42166e01084` |
| `tmp/pdfs/samuel2-22-root/djd-layout-040.png` | 312793 | `63a4bff0af5c0936bf017217295f032a8dc32bb0ea5f61e926d3b6c884a18a75` |

These derivatives assist reading the edition; their pixel dimensions do not
calibrate manuscript millimetres. No new test framework, bulk export or
canonical mutation is needed to reproduce this bounded calculation.
