# 7Q1: measured photographs and reconstruction limits

## Outcome

Two real photographic states and sixteen native-level tiles are now inspected.
The small separate fragment preserves two incomplete ink rows, but the inspected
images do not establish complete glyph widths or original line boundaries.
**No unique completion, new letter, physical join or POB revision is accepted.**
This is an image-based limit on the proposed experiment, not a demonstrated
geometric fit of both rival completed lines.

This follows the original-edition comparison at immutable commit
[`04442f1602`](https://github.com/zackseyun/peoples-open-bible/blob/04442f1602e27a446bdcbfa677dd64a5ae308554/docs/7Q1_EXODUS_28_RECONSTRUCTION_CONTROL_2026-10-15.md).
That separate revision remains in PR214; this packet does not alter its live
CI head. The [catalogue dossier](JUDEAN_GREEK_SOURCE_FOLLOWUP_2026-09-05.md)
provides the earlier acquisition context.

## Original inputs and inspection

The [receipt](../sources/textual_restoration/discovery/7q1_measured_image_control.2026-10-15.v1.json)
pins 22 original responses totaling 761,536 bytes: two catalogue HTML pages,
two pyramid descriptions, two previews and sixteen JPEG tiles. No custodial
images are committed, stitched, sharpened, upscaled or generated.

| IAA record | Catalogue attribution | Native pyramid | Acquired preview |
|---|---|---|---|
| [B-299346](https://www.deadseascrolls.org.il/explore-the-archive/image/B-299346) | Plate789; color photograph; January1999; Tsila Sagiv | 4570 × 3643 | 512 × 408 |
| [B-284859](https://www.deadseascrolls.org.il/explore-the-archive/image/B-284859) | Plates789/789a; PAM M42.961; scanned infrared negative; April1959; Najib Anton Albina | 4434 × 6248 | 363 × 512 |

These are different photographic states, not a contemporaneous calibrated
spectral pair or two independent textual witnesses. Native dimensions follow
from the level 4 tile grid minus its empty edge pixels. Each acquired tile is
512 square and level 4 has inverse scale 1. Regional coverage is x1–2/y0–3 for
color and x1–2/y1–4 for infrared, not complete native plates. The root inspected
all sixteen tiles and both previews. Many peripheral tiles contain backing;
their coverage is recorded rather than counted as useful character evidence.

The large fragment at the plate's upper left and the small separate piece
below it correspond visually across the two states. The large piece's taper,
surviving rows and lower omega-shaped mark, and the small piece's two-row
pattern, support the working correspondence with the edition's fragment pair.
This is a report-aware visual association, not a fresh passage identification,
verified ancient join or a substitute for inspecting printed plate XXX.
Neither plate arrangement proves the missing distance between the pieces.

## Small-fragment observations

A second same-family observer received four original tiles containing the
small piece without proposed words or an edition transcription. Paths were
not anonymized; this is not a fully identity-blinded or cross-model accuracy
test. It reported the following approximate ink envelopes in IR tile x2/y3;
y above 511 continues into the adjacent y4 tile. Root inspected those originals
as well. Bounds are manual estimates, not segmentation or error bars.

| Row | Ink clusters, approximate (left, top, right, bottom) |
|---|---|
| Upper | (7,394,23,413), (31,389,45,409), (54,386,85,411), (95,381,124,406) |
| Lower | (29,465,76,496), (70,458,109,515), (119,467,149,512) |

Clusters are not letter counts. A detached mark at (165,490,178,507) remains
unassigned. The faint inter-row patch is not counted as another writing row.
The lower row's first clear ink lies approximately 22 pixels to the right of
the upper row's first clear ink. That is not evidence of indentation: neither
is an intact original line start. The roughly 100-pixel separation of surviving
lower endpoints is not a secure baseline interval because the upper ink is
broken. Color corroborates two bands but cannot be directly overlaid with IR
without registration; mounting and photographic coordinates differ.

## Consequence for restoration and English

The acquisition succeeded; the prerequisites for a uniquely discriminating
line-width test did not. We did not fit complete rival strings, prove either
reconstruction impossible, or infer complete widths from partial letter
remnants. Any later simulation must expose its uncertain glyph-width model,
orthography, fragment placement and line-boundary assumptions. It must not
report a high-confidence restoration merely because an expected sentence can
be drawn around these traces.

Do not spend further ImageGen calls or repeated model readings on completing
these same gaps. Reopen for a demonstrably discriminating exposure or trace,
a defensible same-hand width calibration, or the original plate and physical
fragment-placement evidence. Otherwise move to a target whose missing reading
is constrained by more measured evidence. The [existing method](TEXTUAL_ADJUDICATION_METHOD.md#imagegen-and-restoration)
continues to treat generated completions as illustrations, never recovered ink.

No source, English, note, registry count or canon decision changes. The
unchanged Exodus28:7 hash remains
`9127b74f3ff97c5e8d794298cc0a5eccf37d60992597975e7b247a2e2eda11e9`.
The protected unrelated Genizah file is preserved. This closes neither the
all-OT witness comparison nor the broader recovery objective.

## Verification

All 22 saved responses were re-read and their hashes and byte counts verified;
all JPEGs decoded with the recorded dimensions. Both native dimensions were
recomputed from the pyramid metadata. The canonical and protected unrelated
file hashes remain unchanged. The repository environment lacked Pillow, so
these read-only checks used the already-installed bundled runtime; no package
was installed and no images were edited.

The observer's bounded four-tile consistency review required one correction:
the receipt must say the inter-row patch is **not counted** as another row,
not assert that it cannot be writing. That correction is applied. The remaining
image descriptions passed within that scope; custody metadata, whole-plate
correspondence and the other tiles are root-only checks. No repeated judge
loop or model agreement is treated as manuscript evidence.
