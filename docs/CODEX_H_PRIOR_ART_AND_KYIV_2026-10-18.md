# Codex H: prior art and a bounded Kyiv transfer check

**Result: no newly recovered letter, word or biblical reading.** Primary-source
checking confirms that the Paris control belongs to a much older recovery
tradition. A different public image, Kyiv transfer page 41r, supports coordinate
comparison but yields no securely additional sequence in the selected native
strip. This does not establish that the entire page is unreadable.

This follows the [Paris coordinate controls](CODEX_H_COORDINATE_CONTROLS_2026-10-18.md).
The [evidence record](../sources/textual_restoration/discovery/codex_h_prior_art_kyiv.2026-10-18.v1.json)
contains source hashes, the metadata audit, all acquisition receipts, every
patch measurement, exact native crop mappings and validation limits. Public
images and source PDFs remain outside Git. No original spectral exposures were
acquired in this pass; no generated letters or pixels were used.

## What was already published

J. Armitage Robinson, [*Euthaliana* (1895), pp. 48-49 and 51](https://archive.org/details/EuthaliusTextsAndStudies),
was checked in the rendered page images, not merely its unreliable Greek OCR.
Printed pages 48, 49 and 51 are PDF pages 65, 66 and 68, counted from one.

Robinson describes transfer reading, confusion from writing visible through
the parchment, reversed photographs, and Cronin's checking against photographs
and the manuscript. His convention distinguishes supplied bracketed minuscules
from uncertain unbracketed minuscules. His confidence in uncials concerns the
reinked state, not necessarily an earlier hand.

Page 51 explicitly concerns the writing opposite Coislin 202 folio 1v, our
Paris transfer target. It already prints the familiar control sequence and
fourteen textual lines, followed by two dotted rows. Those dots supply no
letters. They make it particularly inappropriate to describe the lower gap
or familiar control as a newly discovered problem or reading. They do not
settle what can now be recovered from that gap.

Allen and Fowler's [2025 primary study, pp. 174 and 190-192](https://eprints.gla.ac.uk/342036/2/342036.pdf),
places the modern project after Robinson and Lake. It reports 2023 spectral
imaging in Paris, Torino and Athos, but recovery from supplied digital images
for Kyiv, in part. Its appendix maps the Paris pair to Coislin 202 1v/1vT and
lists Kyiv 2vT, new foliation 41r, as having no transfer recovered. This is a
dated publication state, not proof of present-day novelty. We have not
established a raw Kyiv spectral stack or the exact processing pipeline of
either public Kyiv presentation.

## Why inspect 41r

The saved public edition metadata contains 144 navigation entries, 125 with
images and 126 marked with transcriptions. Eight entries have an image but
no transcription flag: 41r, 44r, 71r, 77v, 79r, 86v, 95v and 97r. The inspected
transcription archive has 125 page-break milestones and none for 41r. These
counts describe these saved releases, not all scholarship or every extant
manuscript page. In particular, 79r already has a recovered content range in
the 2025 appendix despite its absent website transcription flag.

41r was selected because it combines an available public image, archive
absence and an explicit unrecovered entry in that primary publication. These
are reasons to screen an image, not evidence that any mark is new text.

The comparison pair is [40v](https://codexh.arts.gla.ac.uk/#/the-greek-edition?folio=40v)
and [41r](https://codexh.arts.gla.ac.uk/#/the-greek-edition?folio=41r), the direct
and transfer presentations associated with Kyiv, Vernadsky National Library,
physical folio 2v. The website's proposed transfer range remains metadata, not
a transcription produced by this investigation.

## Fixed-coordinate comparison

Both DZI sources are 2791x3517 pixels at native level 12. Their level-11
overviews are 1396x1759. We horizontally reversed the direct view and tested
identity coordinates; no fitted warp or subtraction was used. The same fixed
70 patch centers and unchanged gradient/phase-correlation recipe from the
Paris controls were frozen before the Kyiv measurements. The images had
already been visually inspected, so this is not independent validation.

| Field | Supported patches | Median shift | 95th percentile | Gate |
| --- | ---: | ---: | ---: | --- |
| Upper/middle | 30/35 | 0.307 px | 1.040 px | Pass |
| Lower | 30/35 | 0.446 px | 1.516 px | Pass |

The inherited engineering gate requires at least 20 patches with response
at least 0.3, supported median shift at most 1.5 pixels and 95th percentile
at most 3 pixels. It tests navigation, not letter accuracy. Common host
features and shared image preparation can explain strong agreement.

## Native strip and its limit

After inspecting the processed overview, we selected native rectangle
400,2200,2400,2500 in 41r, including the conspicuous dark forms near overview
y1170-1210. Its counterpart in 40v is 391,2200,2391,2500: native width 2791
gives mirror mapping x -> 2790-x. The 2000x300 direct crop was reversed and
each view split into two exact 1000x300 halves. No resampling or enhancement
was applied to those details. Selection was not blind and did not securely
locate a missing textual line.

Both the root investigator and an AI-assisted geometric reader accepted no
continuous additional sequence. In the left half, dark forms around
x325-430/y125-225 and x450-530/y125-220 broadly correspond to faint contours
or brown material already present in the direct view. Clearer shapes farther
right coincide with host letters. The other half is dominated by host writing,
holes and discoloration. These observations do not determine the chemical
source of faint marks or rule out every possible transfer trace.

The reader received no verse wording, but had worked on the Paris material;
the root investigator knew the website's proposed range. A follow-up shared
the root's geometric assessment. This is corroborative AI screening, not an
independent blind reading or expert palaeographical validation. No glyph
identity, continuous text or theological conclusion is accepted from it.

## Reproduction and next input

The five acquisitions, including the initial preview, contain 124 preserved
JPEG tiles totaling 1,711,408 bytes. All five assemblies were reconstructed
pixel for pixel, with every original tile hash unchanged. The native mirror
and four halves were verified exactly. Portable replay reproduced all 70
measurements, and the existing Paris upper control remained numerically and
visually unchanged. Eleven focused code tests passed; they test processing,
not a historical reading.

Acquire the two descriptors from the source URLs in the evidence record and
save them as `codex-h-40v.dzi` and `codex-h-41r.dzi` in the chosen data folder.
The existing acquisition tool now accepts these two verified folio names.
Level 11 without a box supplies each overview; level 12 with the respective
rectangle above supplies the native strip. With those pinned inputs:

```sh
python tools/textual_restoration/check_codex_h_coordinates.py --work-dir /data/h --pair kyiv --region upper --output-dir /data/h/kyiv-upper
python tools/textual_restoration/check_codex_h_coordinates.py --work-dir /data/h --pair kyiv --region lower --output-dir /data/h/kyiv-lower
python -m unittest tests.test_codex_h_coordinates tests.test_zacynthius_line_controls -v
```

Do not continue tuning this strip against expected Thessalonian wording.
Additional work here needs distinguishable trace geometry, stronger capture
provenance or materially different measured data. For the Paris gap, the
[single-leaf data request](CODEX_H_DATA_REQUEST_DRAFT_2026-10-18.md) remains
prepared but unsent, pending authorization for that external message and a
recipient email. No address has been inferred, disclosed or committed. The
present results do not justify a Bible-text change.
