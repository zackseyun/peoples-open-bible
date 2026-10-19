# Codex H coordinate controls and native comparisons

A matching native crop now distinguishes several dark shapes from the large
host letters in the public Codex H images. The upper and middle page support
comparison at shared coordinates. A separate lower-page check fails its
coverage requirement, and the lower native crops yield no accepted additional
sequence. **No new biblical reading or Bible-text change is justified.**

This follows the [initial public-image investigation](CODEX_H_PUBLIC_TRACE_GATE_2026-10-18.md).
The [machine-readable evidence](../sources/textual_restoration/discovery/codex_h_coordinates.2026-10-18.v1.json)
preserves all 70 patch measurements, acquisition receipts, exact crop mappings,
inspection limits and validation results. The earlier failed feature matches
remain part of the record.

## Shared coordinates

The published [2v direct-text view](https://codexh.arts.gla.ac.uk/#/the-greek-edition?folio=2v)
and [3r ink-transfer view](https://codexh.arts.gla.ac.uk/#/the-greek-edition?folio=3r)
represent the same physical leaf, Paris, BnF, Coislin 202, 1v. Visual inspection
suggested nearly matching framing after horizontal reversal of 2v. Individual
capture and processing provenance remain unverified; both inputs are public
edition presentations. Neither is an acquired raw spectral stack.

We tested the identity coordinates without estimating another transform. The
upper/middle grid was chosen after seeing the overviews and frozen before its
measurements. It contains 35 non-overlapping 128-pixel patches at x centers
220, 370, 520, 670, 820, 970 and 1120; y centers are 350, 500, 650, 800 and
950. The existing Gaussian 3x3/sigma 0.8 and Sobel 3x3 gradient helper supplies
the inputs to Hanning-window phase correlation.

The engineering gate is inherited unchanged from the Zacynthius control:
at least 20 patches with response at least 0.3, supported-patch median shift
at most 1.5 pixels and ninety-fifth percentile at most 3 pixels. These are
navigation thresholds, not calibrated probabilities of correct letters.

| Field | Supported patches | Median shift | 95th percentile | Gate |
| --- | ---: | ---: | ---: | --- |
| Upper and middle | 26/35 | 0.627 px | 1.358 px | Pass |
| Separate lower field | 16/35 | 0.691 px | 1.424 px | Fail |

The lower field uses the same x centers and y centers 1070, 1198, 1326,
1454 and 1582. Its supported residuals are small, but there are too few
supported patches. Only one supported patch lies on its y=1326 row. This
failure prevents extending the upper result across the lower text area.
All weak patches remain in the record; no threshold was relaxed.

This is a spatial check on related presentations of the same physical page.
Host writing and shared photography can dominate agreement. No subpixel warp,
image subtraction, language model or generated stroke was used.

## Native comparisons

Three additional native acquisitions supply 143 JPEG tiles totaling 1,832,408
bytes. They supplement the previously acquired 3r control crop.

| New acquisition | Source rectangle x0,y0,x1,y1 | Tiles |
| --- | --- | ---: |
| 2v control | 1280,3060,3880,3840 | 44 |
| 3r lower band | 600,4880,4600,5600 | 48 |
| 2v lower band | 680,4880,4680,5600 | 51 |

The 5280-pixel source width gives a horizontal mapping x -> 5279-x.
The 2v control crop therefore reverses into the previously acquired 3r
rectangle 1400,3060,4000,3840. Reversal changes pixel order only. The lower
pair is split into exact 2000x720 halves for inspection without display
downscaling. The broad lower band is not a secure coordinate assignment of
the edition's two illegible lines.

The same AI reader who previously inspected 3r alone compared the native
control pair without being given the verse wording. It had already seen and
described the shapes, so this is a revised assessment with new image evidence,
not an independent blind reading or expert palaeographical validation.

The epsilon-like form around control-relative x650-815,y300-465, the upright
around x885-930,y305-445, and the curve around x1015-1170,y315-465 occupy
broadly pale locations in the direct-text view. The large host letters on
that row begin farther right, around x1370. This makes it reasonable to
distinguish the additional shapes from the host's visible large-letter strokes
at those locations. It does not establish chemical composition, layer order,
or a complete transcription. A final exact-pixel detail still leaves the
third curved shape ambiguous; no additional secure glyph identity is accepted.

The lower pair does not provide a comparable result. Dark patches remain
irregular; visible contours often follow existing host letters, mottling or
repair boundaries. Neither the main investigator nor the AI reader accepted a
continuous additional sequence or a securely separate letter there. The failed
lower navigation check remains a further limit on any fine comparison.

The private comparison image shows exact 750x300 panels from the control,
with labels added outside the source pixels. Its panels, native reversal and
all four lower halves were verified pixel for pixel. Labels use the project's
direct-text and ink-transfer terminology; an earlier private label calling
the direct view an ordinary photograph was corrected because its full capture
pipeline has not been established. The published spectral recovery belongs to
the Glasgow/EMEL team. Our contribution here is a better documented control
comparison, not a newly recovered ancient word.

## Reproduction

The [existing tile acquisition tool](../tools/textual_restoration/acquire_codex_h_public_tiles.py)
accepts the three rectangles above with `--level 13`. The earlier report gives
the two overview acquisitions and descriptor setup. With those pinned images:

```sh
python tools/textual_restoration/check_codex_h_coordinates.py --work-dir /data/h --region upper --output-dir /data/h/coordinates-upper
python tools/textual_restoration/check_codex_h_coordinates.py --work-dir /data/h --region lower --output-dir /data/h/coordinates-lower
python -m unittest tests.test_codex_h_coordinates tests.test_zacynthius_line_controls -v
```

Eight focused tests passed with image dependencies installed. The synthetic
identity input passes both fields; a three-pixel displacement fails the
unchanged gate. Portable execution reproduced every measurement and both patch
sheets exactly. All six input assemblies were rebuilt from their preserved
JPEG tiles, with all 271 original tile hashes unchanged. The code tests and
pixel checks validate processing, not a historical reading.

## Next source input

The [Glasgow repository](https://researchdata.gla.ac.uk/1865/) offers a download
link for the approximately 241GB spectral collection through a public data
request form. A [single-leaf request draft](CODEX_H_DATA_REQUEST_DRAFT_2026-10-18.md)
asks for original wavelength files, calibration/capture metadata, correct
file-to-leaf mapping and any existing reading or known recovery limit for the
two illegible lines. It avoids acquiring the whole collection unnecessarily.

The form requires an email address. The request has not been sent, and no
personal address is recorded in Git. This source input could distinguish a
limit of the public composite from a limit of the surviving measurements;
the present images do not settle that question.
