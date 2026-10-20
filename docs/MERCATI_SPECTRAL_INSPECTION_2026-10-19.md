# Mercati fragments spectral inspection

Two fixed tests on public spectral images of Ambrosiana O 39 sup. (Ra 1098)
establish usable contrast between the erased Psalms text and later writing,
but yield **no newly accepted character or Bible-text change**. The first is
a known-reading control at Psalm 49(48):12a. The second tests an obscured
Greek abbreviation at Psalm 31(30):24 and leaves it unresolved.

The [measurements](../sources/textual_restoration/discovery/mercati_spectral_measurements.2026-10-19.v1.json)
retain every acquired crop's source URL, geometry, byte order, hash and HTTP
range receipt. The [interpretation record](../sources/textual_restoration/discovery/mercati_spectral_interpretation.2026-10-19.v1.json)
separates these observations from published readings and editorial hypotheses.

## Sources and scope

The [Jubilees Palimpsest Project](https://jubilees.stmarytx.edu/) provides ten
sample page captures from its 2017 work on O 39 sup., not the entire codex's
spectral coverage. Its [IIIF manifest](https://jubilees.stmarytx.edu/iiifp/Ambrosiana_O39sup/manifest.json)
identifies pages 001, 008, 027, 030, 060, 061, 066, 067, 078 and 081. The
[archive](https://palimpsest.stmarytx.edu/AmbrosianaArchive/Ambrosiana_O39sup/)
includes individual-band, fluorescence and processed views. The measured
inputs here are the provider's no-gamma TIFF exports, not newly acquired
photographs or a reprocessing of camera DNG masters.

Carrera Companioni's 2022 dissertation, *The Mercati Fragments: A New Edition
of Rahlfs 1098*, was obtained through the
[repository record](https://repository.sbts.edu/entities/publication/3c120a39-1f97-4603-9486-348d9e597933).
Relevant transcriptions and commentary were extracted and visually inspected:
printed p156/PDF181 and p342/PDF367 for page27; p104/PDF129 and pp243-244/PDF268-269
for page60. This is not a claim to have read all 437 PDF pages. The original
Mercati edition was not consulted; statements about it are explicitly mediated
through Carrera or Kyle Young's
[2025 discussion](https://septuaginta.uni-goettingen.de/blog/contributions-towards-a-critical-edition-of-aquila/).

The manuscript preserves later copies of ancient versions and commentary.
It is not Origen's autograph. A reading of this witness would not by itself
recover an original Hebrew wording or authorize changing POB.

## First test at Psalm 49 verse 12

The [initial protocol](../sources/textual_restoration/discovery/mercati_ps49_12_protocol.2026-10-19.v1.json)
selects page27, line11, column3, Symmachus. The forms under comparison are
`οἰκῶν` and `οἰκείων`, within a phrase about houses. Carrera's figure230
illustrates the longer form.

**Prior-art correction:** the initial protocol's description of Mercati is
incomplete. Young's section49(48):12a says Mercati's footnote already identifies
`οἰκείων` as the physical reading. The distinction between an edited main text
and its footnote must not be treated as a newly discovered manuscript variant.
The frozen protocol remains an honest record of the initial framing; this
correction governs interpretation.

Navigation used the project's published KTK02 derivative. The lower writing is
upright in the stored frame while the large upper writing is inverted. The
fixed measured context is `(3300,3700,1500,900)` and the target is
`(3700,3950,850,300)`, in x, y, width, height. No rotation or interpolation was
applied to the measured views.

The word-shaped undertext persists in UV, visible and filtered-fluorescence
views, while largely fading in the 850IR view. The two neighboring lines remain
available as controls. The final portion also crosses a strong chemical/stain
boundary. The visible shapes are consistent with the published longer reading,
but this inspection does not independently settle every stroke of its ligature.
No new spelling is adopted. The useful result is measured layer contrast and
a located control, not a new word or an improvement over Carrera.

## Follow-up at Psalm 31 verse 24

The [second protocol](../sources/textual_restoration/discovery/mercati_ps31_24_protocol.2026-10-19.v1.json)
tests page60, line2, column4. Carrera reports Mercati's identification of the
Greek nomen sacrum `κν` near the final sigma of the inverted upper word
`ἀδιαφθόρος`, after the article and Hebrew divine name. Carrera cannot confirm
the proposed letters. This is a trace question distinct from reconstructing the
expected wording of the Psalm.

The fixed context is `(3700,2000,3000,700)`. It includes the article/divine-name
locator and a separate search box `(5750,2250,550,250)` around the uppertext
locator. Both single-band contexts and the small target panels were inspected.

Five measured views do not securely isolate the proposed two-letter lower
sequence. A single, predeclared linear diagnostic reduces some large uppertext
contrast and preserves the nearby lower writing, but leaves staining and edge
residuals. It does not supply distinctive target strokes visible in two measured
single-band images. **The proposed abbreviation remains unconfirmed.** This
does not establish its absence or show that the rest of the manuscript is unreadable.

## Acquisition and processing

Each case uses these same five capture codes:

| Capture code | Provider directory |
| --- | --- |
| MB365UV_011 | Captures-Narrowband-NoGamma |
| MB450RB_002 | Captures-Narrowband-NoGamma |
| MB850IR_013 | Captures-Narrowband-NoGamma |
| WBUVB47_023 | Captures-Fluorescence-NoGamma |
| WBUVO22_016 | Captures-Fluorescence-NoGamma |

Source images are 8,176 by 6,132 pixels. Each full TIFF is 100,270,797 bytes with
a single uncompressed 16-bit big-endian pixel strip beginning at byte 333.
Ten exact region crops preserve 34,500,000 bytes of measured samples. The
reader validates HTTP206 responses and exact Content-Range, checks stable
length/ETag within each acquisition, and records the requested row-span hashes.
These are **crop hashes, not full-capture hashes**; no full-capture checksum is
invented for files downloaded only in part. Original used pixel bytes are kept
unchanged outside Git.

The [reader and view tool](../tools/textual_restoration/probe_mercati_spectral.py)
uses Pillow's TIFF directory parser rather than guessing pixel offsets. It
accepts only bounded, unsigned, uncompressed, single-strip gray captures.
A physical control also compared a remotely acquired 64 by 64 region against the
already held full page001 UV TIFF: all 4,096 pixels match, and the full TIFF's
SHA256 remains `b5561e1a50a05d2eaaf0269af0106c2f42d5a1522556bbd41ce9b3f9bf790787`.

The [analysis tool](../tools/textual_restoration/analyze_mercati_spectral.py)
applies one 1st/99th-percentile display stretch per band/context. OpenCV phase
correlation on fixed nontarget patches estimates small inter-band displacement:
the largest absolute component is about 1.51 pixels for page27 and 1.19 for
page60. These are navigation estimates, not a calibrated registration certificate.
No warping was applied. This matters particularly at dark letter edges.

The sole page60 subtraction fits UV intensity as `a * IR + b` on the first 100
and last 100 context rows, excluding the target rows. There are 600,000 fit
pixels; `a = 0.5049577842`, `b = 11.6558459571`. Its residual includes chemical
differences and small geometric edge artifacts as well as writing. Residual-only
shapes cannot authenticate letters. No language completion, OCR, generated
strokes, inpainting, sharpening search or target-trained classifier was used.

Thirteen focused unit tests pass with the image dependencies installed. They
cover byte-order-correct range extraction, TIFF defaults, rejected ignored or
changing range responses, exact cropping, input preservation, constant fields,
RGB navigation, excluded-region linear fitting and overwrite refusal. These
checks validate tools, not the transcription of ancient letters.

## Reproduction and rights

The working cache is `work/mercati-2026-10-19` in this task's workspace, outside
the repository. Acquisition receipts provide the exact URLs and crop geometry.
For example, from the repository:

```sh
python tools/textual_restoration/probe_mercati_spectral.py fetch \
  --url https://palimpsest.stmarytx.edu/AmbrosianaArchive/Ambrosiana_O39sup/Ambrosiana_O39sup_027/Captures-Narrowband-NoGamma/Ambrosiana_O39sup_027_MB365UV_011_F.tif \
  --box 3300 3700 1500 900 --output /data/mercati/page27-365uv.bin
python tools/textual_restoration/analyze_mercati_spectral.py \
  --cache /data/mercati --output /data/mercati-fixed-analysis
python -m unittest tests.test_mercati_spectral -v
```

Acquire all ten named crops from the measurements before running the analysis;
its page27 UV basename is `page27-365uv.bin`, and other names use their capture
code, such as `page60-MB365UV_011.bin`. Analysis requires NumPy, Pillow and
OpenCV. The executed versions are pinned in the measurements. Existing outputs
are not overwritten. The published KTK02 separation `R-(G+B)/2` is only a
navigation aid, not an additional measured exposure or independent witness.

The project licenses Ambrosiana artifact images under
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/), with
attribution to Biblioteca Ambrosiana and the Jubilees Palimpsest Project.
Downloaded images, source crops and derivatives remain outside Git; this work
does not relicense them under POB's text or software license. The repository
contains methods, provenance, hashes and findings, not an imported image corpus
or dissertation PDF.

## Next decision

Keep this source as a viable measured-image resource, but do not retune the two
tested regions against their expected words. Page27 serves as a control;
page60's abbreviation needs an attributable additional trace, stronger
palaeographic control or materially different measured data. Any next Mercati
target must be mapped to available pages and checked against Carrera, Young
and, where necessary, Mercati's actual apparatus before being called unresolved.
