# Codex Zacynthius: deterministic spectral pilot

All 51 public spectral-capture JPEGs for modern folio 57r were acquired and
integrity-checked on October 17. A non-generative separation experiment combined
42 of them after alignment checks. **No new letter, new biblical reading, or
improvement over the published composite has been established.** The useful
progress is access to measured exposures and a reproducible processing test,
not a decipherment. No Bible text was changed by this experiment.

This extends the earlier [four-exposure acquisition](ZACYNTHIUS_RAW_EXPOSURES_2026-10-17.md).
The [machine-readable record](../sources/textual_restoration/discovery/zacynthius_spectral_pilot.2026-10-17.v1.json)
contains the acquisition receipts, every input hash, alignment measurements,
PCA coefficients, display limits and hashes of all 42 component images.

## Source and integrity

The [Birmingham dataset](https://edata.bham.ac.uk/428/), DOI
10.25500/edata.bham.00000428, credits D.C. Parker, H.A.G. Houghton and Michael
Phelps, with EMEL capture in July 2018. The archive files are listed as CC BY 4.0.
This license statement concerns those files, not every Cambridge image.

The selected `00057-R/` members in `00041-00060.zip` total **24,945,357 bytes**.
One contiguous range supplied their compressed payloads. The existing range/ZIP
verifier checked exact HTTP ranges, a consistent ETag, local headers, lengths and
member CRCs. The acquisition transferred 25,195,427 range bytes, including the
archive-directory reads. Earlier acquisition probes are additional traffic.
The complete 1,046,756,775-byte archive was not downloaded or checksum-verified.

All 51 files were decoded and confirmed as **1533 x 2044, 8-bit grayscale JPEGs**.
Their hashes were checked again after processing: all originals were unchanged.
These are individual spectral exposures but are lossy, reduced JPEG derivatives,
not sensor RAW or full-resolution TIFF masters. The modern 64v half of the
reconstructed undertext leaf was not acquired in this experiment.

## Fixed experiment

The user expressly authorized ordinary, non-generative image processing. The
pipeline performs normalization, feature matching, bounded affine alignment and
principal-component analysis (PCA). It does not use expected Greek wording,
generative images, inpainting, sharpening, deconvolution, super-resolution or
language-model completion. PCA recombines measured pixel values; it does not
identify which ink layer a component represents.

Before the full-stack run, the candidate set was fixed to all 42 files in the
`MB` and `W` filename families. The nine `Aux`, `RL`, `RR` and `TX` files were
excluded before fitting. Filename selection is an experimental rule, not a
claim that the included exposures have identical optical responses. The `W`
family includes fluorescence/filter combinations. No radiometric calibration
was performed.

The fixed reference is `00057-R+MB530GN_005.jpg`. Processing uses the original
coordinate rectangle `(280, 200, 1260, 1800)`, expressed as x0, y0, x1, y1.
Feature detection operates at half scale after a 1st-to-99th-percentile stretch;
reported errors are converted back to original-image pixels. SIFT uses at most
4,000 features. Descriptor matches must pass a 0.70 ratio test, with at least
40 matches. Alternating matches fit a partial affine transform and check it.
RANSAC uses a 2-pixel threshold, 5,000 maximum iterations and 0.999 confidence.

Acceptance requires all of:

- held-out median error at most 1.5 pixels and 95th-percentile error at most 3;
- scale between 0.98 and 1.02, rotation within 1 degree;
- translation within 10 pixels on each axis;
- held-out matches occupying at least six coarse spatial cells.

These are **feature-level checks**, not independent physical or letter-level
controls. SIFT can produce multiple orientations at the same physical location,
so the alternating split does not guarantee independent landmarks. Matching may
be driven by later writing or parchment features. The numerical thresholds do
not certify that a faint undertext stroke is correctly registered.

Accepted images use bilinear resampling. PCA standardizes each channel by its
mean and standard deviation, using a fixed every-eighth-pixel sample in both
dimensions: 24,600 samples. All 42 components are retained, including weak ones.
The largest absolute eigenvector coefficient fixes each component's sign. Each
display uses its own 1st-to-99th-percentile limits and a 90-degree counterclockwise
rotation. Equal-looking contrast across components does not mean equal signal
strength: this display stretch can make very weak noise look substantial.

## Measured outcome

All 41 non-reference candidates passed the fixed alignment checks; the reference
is carried through without a fit. Median held-out errors range from 0.037 to
0.318 original pixels; 95th-percentile errors range from 0.145 to 1.131 pixels.
Thus 42 of 42 prespecified candidates entered PCA.

The first six components account for approximately 86.534%, 6.722%, 3.521%,
0.968%, 0.826% and 0.381% of standardized sample variance. These percentages are
not transcription confidence, ink-layer purity or probabilities of correctness.

All components were reviewed at contact-sheet scale. Components 6, 8 and 19
were also inspected at full output size, and a published Cambridge crop was
reviewed for comparison. This is exploratory visual inspection, not an exhaustive
letter-by-letter comparison or a blinded evaluation. Components change the
contrast of later writing, folds and texture. None of the inspected residual
shapes was accepted as a newly recovered biblical character.

The published [Cambridge undertext image for 61r](https://cudl.lib.cam.ac.uk/view/MS-ADD-10062-UNDERTEXT/121)
has a 9051 x 13100 source image containing the reconstructed leaf. Modern 57r
supplies only one half. Coarse page orientation is consistent with rotating the
raw JPEG 90 degrees counterclockwise; that is not a measured registration of the
edition's uncertain word. The exact Luke 9:7 uncertainty still lacks a verified
image rectangle. The model had already seen the edition's proposed letters, so
its visual judgments cannot count as blind readings.

The result does not prove that the JPEGs contain no useful undertext signal.
It does show that global, standardized PCA alone has not supplied grounds to
change a transcription. No additional parameter search is being presented as
independent evidence.

## Pilot history and reproducibility

An initial four-exposure probe tested the green reference, MB940IR, W365G58 and
TX940IR. The two non-reference front-side comparisons passed; transmission had
only three descriptor matches and was excluded rather than forcibly combined.
The three-channel separation did not establish a new letter. Its first execution
stopped on an OpenCV non-contiguous-array assertion; copying the sliced fit arrays
fixed that implementation error without changing the thresholds. The failed run
is not evidence about manuscript readability.

The full 42-channel run used the settings above. The portable repository version
was then rerun on the same originals. Alignment results, means, standard
deviations, eigenvectors, variance fractions and every component PNG hash matched
the exploratory run exactly in this environment. The receipt records both script
hashes. Exact numeric or PNG equality across different library builds is not
promised. This replay verifies the recorded computation, not the interpretation.

Use a full checkout, install NumPy, Pillow and OpenCV, and choose new directories:

```sh
python tools/textual_restoration/acquire_zacynthius_57r.py --output-dir /data/new-57r
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python tools/textual_restoration/probe_zacynthius_spectral.py \
  --source-dir /data/new-57r --output-dir /data/new-57r-pca
python -m unittest tests.test_zacynthius_spectral tests.test_remote_zip tests.test_zacynthius_triage -v
```

The focused suite passed **22 tests**, including eight spectral-pilot tests,
nine range/ZIP tests and five TEI-triage tests. Spectral tests cover known
translation recovery, rejection of excessive scale and held-out mismatch,
missing features, input hashes, image dimensions and path traversal. They run
with the image dependencies installed; otherwise that class is explicitly skipped.
They are software checks, not proof of a manuscript reading.

## Next evidence gate

The next useful step is to register the exact published uncertainty and nearby
known undertext, later-writing, reverse-side and bare-parchment controls. A
candidate improvement must persist across measured exposures and sensible
processing choices, and exceed the published composite at that same location.
Only then is an independent, text-blind shape assessment worth commissioning.

The dataset describes full-resolution TIFF access by request. No request has
been sent and no master TIFF has been acquired. If the public JPEGs cannot
separate known undertext controls, increasing the number of speculative
completions will not fix that evidentiary limit. Generated reconstructions may
illustrate a hypothesis, but cannot serve as recovered letters or justify a
change to the Bible.
