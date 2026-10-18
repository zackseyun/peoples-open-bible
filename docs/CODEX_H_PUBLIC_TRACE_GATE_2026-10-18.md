# Codex H public images and the remaining reading barrier

Codex H provides a real example of recovering lost-page text from ink left on
surviving parchment. That recovery belongs to the Glasgow and EMEL team, not
POB. Our bounded inspection establishes public image access and a remaining
two-line uncertainty, but **does not establish a new reading**. A native
resolution control crop still leaves writing-layer attribution uncertain, and
the attempted direct-view comparison failed its feature-match gate. POB's
Bible text remains unchanged.

The [evidence record](../sources/textual_restoration/discovery/codex_h_public_trace_gate.2026-10-18.v1.json)
contains source hashes, every acquired tile URL and hash, display coefficients,
the failed comparison, and reproduction checks. Only non-generative processing
was used. Images and the downloaded edition remain outside Git.

## What is publicly accessible

The [project manuscript account](https://codexh.arts.gla.ac.uk/#/the-manuscript)
reports 42 additional pages recovered through ink offsets after re-inking.
Its date range is sixth to eighth century. These are existing research results,
not newly discovered biblical books or results of this experiment. See Allen
and Fowler, [JBL 144 (2025), 167-196](https://doi.org/10.15699/jbl.1441.2025.9).

The [digital edition](https://codexh.arts.gla.ac.uk/#/the-greek-edition) provides
processed images and folio-specific XML. The public application data currently
contains 144 navigation entries. The [December 2025 TEI deposit](https://researchdata.gla.ac.uk/2105/)
contains 125 TEI documents in a 55,549-byte ZIP, under CC BY 4.0. Its authors
are Garrick V. Allen, Kimberley A. Fowler, Emanuele Scieri, Maxim Venetskov and
Ivan Bacher. The different counts are a version/scope warning, not evidence
of 19 new recovered leaves.

The [multispectral dataset](https://researchdata.gla.ac.uk/1865/), credited to
Allen, Fowler and Michael Phelps, is approximately 241GB and requires a data
request to obtain a download link. It is licensed CC BY-NC 4.0. No request was
sent and no raw exposures were acquired. The public display tiles are not a
substitute for measured spectral bands. Public availability also does not mean
that the images can be redistributed under POB's own license.

## Editorial completion is not observed ink

The archived TEI inventory contains 1,300 `unclear`, 836 `supplied`, and 50
`gap` elements. These count XML elements, not independent textual problems,
letters, or opportunities for discovery. Apparatus alternatives and markup
segmentation can affect such counts. The inventory preserves the original
attributes and does not promote supplied text to observed testimony.

For example, live folio 1v identifies some completions as supplied from `na28`.
Live folio 3r uses both `Robinson` and `na28` source labels. A complete-looking
rendered transcription therefore cannot establish that all its words were
read from this manuscript. The archived inventory alone also cannot establish
what remains unresolved in the current edition.

## Candidate and exact image access

[Current folio 3r](https://codexh.arts.gla.ac.uk/#/the-greek-edition?folio=3r)
is labelled Paris, BnF, Coislin 202, 1vT, covering 1 Corinthians 10:29-32.
Its [current XML](https://codexh.arts.gla.ac.uk/data/G015-Images/3r/3r.xml)
retains a gap with `reason="illegible"`, `unit="line"`, `extent="2"` after the
verse 32 material. The UI displays gaps at lines 15-16. This does not identify
the missing words or securely locate their image coordinates.

The public application exposes [folio metadata](https://codexh.arts.gla.ac.uk/data/output_data.json)
and a conventional Deep Zoom pyramid. The [3r descriptor](https://codexh.arts.gla.ac.uk/data/G015-Images/3r/3r.dzi)
specifies 5280 x 7100 pixels, 256-pixel JPEG tiles and zero overlap. Level 13
is native resolution; level 11 is 1320 x 1775. We acquired:

| Published view | Level and region | Tiles |
| --- | --- | ---: |
| 3r transferred-text presentation | Level 11, complete overview | 42 |
| 3r control crop | Level 13, x1400-4000, y3060-3840 | 44 |
| 2v direct-text presentation | Level 11, complete overview | 42 |

The 128 JPEGs total 1,770,222 bytes. Each decoded tile was dimension checked
and pasted at its integer position, with no interpolation. Every original
tile hash remained unchanged, and offline reconstruction reproduced all three
assembled images pixel for pixel. Hashes record the acquired bytes; they are
not independently published authenticity checksums.

## Control observations and comparison failure

One AI reader inspected the 3r overview and native control without the expected
wording or another transcription. This is a limited blinded observation, not
independent expert palaeographical validation. It found a dark epsilon-like
shape and an adjacent upright, but could not securely assign these to a
separate readable-direction layer. The control was selected from those visible
shapes; it is not a newly established locator for the two missing lines.

The main investigator also inspected fixed R, G, B, R-G, R-B and G-B views,
each stretched between its image's first and ninety-ninth percentiles. These
are channel combinations of an already processed RGB image, not new spectral
separation. No text model, generated pixel, sharpening or inpainting was used.
No character was accepted from the changes in contrast.

The direct view, [folio 2v](https://codexh.arts.gla.ac.uk/#/the-greek-edition?folio=2v),
is labelled Coislin 202, 1v, covering 1 Corinthians 10:27-29. It supplies a
different rendering of the same physical page, not another witness. Visual
comparison shows it is not merely the identical composite mirrored. That does
not establish independent capture or independent spectral evidence.

For a bounded navigation check, we horizontally mirrored the 2v overview,
converted it to grayscale, and compared it with inverted grayscale 3r using
SIFT with 6000 features and a 0.7 nearest-neighbor ratio. It produced **22
matches**, below the pre-existing 40-match minimum. No transform was fitted or
accepted. The failed count was reproduced exactly with the portable script.
This rejects that comparison attempt, not all possible registration methods.
We did not relax the gate or subtract the images to manufacture a residual.

## Reproduction and next decision

The bounded acquisition script accepts only 2v and 3r. Place each public
descriptor in a new working directory as `codex-h-2v.dzi` and
`codex-h-3r.dzi`. Place the public TEI ZIP there as `codex-h-2105_data.zip`.
The scripts require Python; acquisition additionally needs Pillow, channel
views NumPy/Pillow, and registration NumPy/Pillow/OpenCV.

```sh
python tools/textual_restoration/acquire_codex_h_public_tiles.py --work-dir /data/h --folio 3r --level 11 --output /data/h/codex-h-3r-overview
python tools/textual_restoration/acquire_codex_h_public_tiles.py --work-dir /data/h --folio 3r --level 13 --box 1400 3060 4000 3840 --output /data/h/codex-h-3r-native-control
python tools/textual_restoration/acquire_codex_h_public_tiles.py --work-dir /data/h --folio 2v --level 11 --output /data/h/codex-h-2v-overview
python tools/textual_restoration/inspect_codex_h_tei.py --work-dir /data/h
python tools/textual_restoration/inspect_codex_h_channels.py /data/h/codex-h-3r-native-control/assembled.png /data/h/native-channels
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python tools/textual_restoration/register_codex_h_pair.py --work-dir /data/h
python -m unittest tests.test_codex_h_inventory -v
```

Four inventory tests passed. Portable replay reproduced the inventory, failed
registration report, all six native channel PNGs, their receipt and contact
sheet exactly. The acquisition algorithm was verified by offline tile replay;
the portable path-argument change was not re-downloaded solely for testing.
These checks validate record handling and processing, not a biblical reading.

This candidate needs an attributable target trace, stronger correspondence to
the physical page, or independently interpretable source measurements before
a new reading attempt is justified. The unresolved-line locator and existing
recovery achievement make it a legitimate candidate, but the current test
does not show that further contrast tuning would be productive. Keep the
public-source restriction, preserve the failure, and do not turn an editorial
completion or isolated glyph-like shape into manuscript testimony.
