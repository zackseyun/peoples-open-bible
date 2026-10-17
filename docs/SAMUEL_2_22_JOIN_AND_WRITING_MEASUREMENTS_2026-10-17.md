# 1 Samuel 2:22 join and writing measurements

Date: 2026-10-17. Baseline: `c340da4165e43bd50144ed48c4c5dd08e42a09f6`.
Follow-up to the [conditional layout test](SAMUEL_2_22_LAYOUT_STRESS_TEST_2026-10-17.md).

## Result and limit of the physical experiment

Five writing spans provide actual image-coordinate estimates, but do not
independently settle the missing line width. A newly consulted edition note
explicitly locates the relevant line-14 trace at an internal join of composite
fragment a. The shorter reading remains provisionally preferred on the
published textual/spatial case; no new letters or canonical changes follow.

Do not repeat the same previews or fit increasingly elaborate models to these
five spans. Further independent physical confirmation requires validated joins
and margin transfer, and sufficient glyph/space measurements or defensible
bounds for the clause's actual letter mixture. Published evidence remains
usable without pretending this project independently reproduced its geometry.

## An assembled fragment is not uninterrupted skin

DJD XVII printed **40–41 / PDF 63–64**, read completely in text and images,
lists PAM **41.169, 41.174, 41.766, 43.122**, inventory **998**. Its line-14
note places the waw trace at the meeting of two pieces among several making
up fragment a. Consequently, the previously recorded photographic adjacency
is adjacency in the assembled presentation, not certification that the
relevant area is one uninterrupted original piece of leather. This sharpens,
rather than contradicts, the preceding warning that joins were not validated.
The note does not show that the published join is wrong.

The line-2 note concerns **2:16**, not the disputed clause: an unnamed
pre-complete-assembly photograph preserves traces later lost through handling.
The line-18 note likewise describes lost traces in an earlier unassembled
photograph. Only the line-29 discussion specifically identifies **41.766**
for lower-fragment traces. None assigns the line-2 photograph to a particular
one of the three early PAM numbers. Do not transfer those earlier-letter
claims into recovered text at 2:22.

One bounded public IAA search/navigation pass did not obtain early-PAM pixels.
The [known owner](https://www.deadseascrolls.org.il/explore-the-archive/image/B-277400?locale=en_US)'s
observed 4Q51-2/4Q51-3 navigation exposed reader shells without a photograph
list; the supported browser entry was unavailable. This access result is not
evidence that the photographs do not exist. No opaque image IDs were guessed.

## Actual writing spans

A separate image reader selected extant upper-column spans, without using the
disputed clause to fit them. All are in original tile
`c7e9163b510b1950`, viewer **x1-y1-z3**, **512×512**. Coordinates are approximate
manual native-image endpoints, not automated word segmentation. Root checked
the native image and derived the arithmetic; no new transcription variant is
claimed. A context y-band is not a tight single-line bounding rectangle.

| Edition line | Observed consonants | x endpoints | Context y band | Nominal span |
| --- | --- | --- | --- | ---: |
| 2 | נפשך | 397–455 | 55–130 | 58 px |
| 2 | ואמר לא כי | 244–389 | 45–113 | 145 px |
| 2 | עתה | 173–235 | 60–112 | 62 px |
| 3 | מזלג | 278–352 | 100–166 | 74 px |
| 7 | אפוד | 185–254 | 305–353 | 69 px |

Each endpoint has a stated **±8 px selection tolerance**, giving worst-case
width intervals **42–74, 129–161, 46–78, 58–90, 53–85 px** respectively.
These are manual tolerances, not statistical confidence intervals. The
three-word span includes two spaces; its component words are not extra samples.
The reader rejected precise target Israel/next-line-prefix boxes as insecure.

## Why these spans do not determine clause width

Even an optimistic additive model, with one advance per distinct glyph and
one for space, has **23** variables across these spans and the proposed clause,
but only **five independent equations**. Its count matrix has rank **5** and
nullity **18**. The clause uses **ב ח ם ן צ**, which occur in none of the five
calibration spans. Final forms are not silently merged with other shapes.
Bounding ink spans are also not automatically complete typographic advances.

A simple non-unique-fit demonstration makes the problem reproducible. Assign
all observed glyphs an assumed 17 px advance and space 10 px. Predicted spans
are **68, 156, 51, 68, 68 px**, all within the stated tolerances. Assigning
the five unobserved glyphs 8 px or 25 px leaves those predictions unchanged
but changes the specified 43-character long clause's predicted width from
**621** to **723 px**. Neither assignment is a measured scribal model, and
621–723 is **not** a physical bound or uncertainty interval. These examples
only show that accepting the calibration tolerances does not select a unique
clause-width prediction. The clause is the same exact consonantal string
recorded in the preceding test, without the extra joining space.

Non-uniqueness alone does not rule out useful conservative bounds. Such bounds
still need a justified model of glyph widths, spacing, endpoint selection and
local deformation, plus a supported available width. This pass establishes
neither a physical lower bound excluding the long clause nor its successful
fit. It must not be cited as an independent confirmation of the 48-versus-92
count test. No ImageGen, image enhancement or restored letters enter the test.

## Research consequence

The bounded physical experiment has identified the important missing inputs:
internal join validation, margin transfer and representative advances. Until
one of those changes, more previews or model agreement are not a new test.
Continue the complete Hebrew-source and English adjudication using the
published witness evidence with this conditional geometry explicitly attached;
do not substitute automatic WLC retention or an unreviewed deletion. A short
reading in this copy would still not alone prove priority in Samuel's history.
The [measurement packet](../sources/textual_restoration/comparisons/samuel2_22_join_measurements.2026-10-17.v1.json)
retains the exact spans, model recipe, source bytes and consultation limits.
