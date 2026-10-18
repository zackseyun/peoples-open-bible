# Zacynthius line controls and the unresolved Luke 9:7 reading

Deterministic color differences now make two neighboring undertext lines on
leaf 61r easier to locate. A separate patch check supports a provisional mapping
between the public spectral JPEGs and the published composite. **The uncertain
letters in Luke 9:7 remain unresolved.** The selected spectral component does
not justify a new transcription or any change to POB.

This follows the [42-exposure PCA pilot](ZACYNTHIUS_SPECTRAL_PILOT_2026-10-17.md).
The [inspection record](../sources/textual_restoration/discovery/zacynthius_line_controls.2026-10-17.v1.json)
preserves the failed feature-matching checks, navigation transform, patch results,
line bands, all 42 control correlations and output hashes. Image files remain
outside Git. The Cambridge composite is processed source material, not a new
independent spectral measurement; its colors are not natural ink colors.

## Lines located from neighboring words

Subtracting green from blue, with floating-point arithmetic and a 1st-to-99th-
percentile display stretch, suppresses some cyan later writing. A second view
uses blue minus the greater of red and green. Neither transformation fills a
gap, recognizes a character, sharpens a stroke or adds pixels from expected text.

Both the initial reader and a separate visual pass had already seen the edition;
neither is a blind reading. The improved views support the following navigation
estimates in the 9051 x 13100 composite's source coordinates:

| Undertext anchor | Approximate source rectangle or band |
| --- | --- |
| Line 2 opening, `ΧΗϹ...` | x 2000-2400, y 3340-3510 |
| Line 3, `ΡΕΙΔΙΑΤΟ...` | x 2000-2950, y 3590-3780 |
| Preceding first line | y 3070-3240 |

These line openings agree with the pinned edition's physical line breaks. Its
first line ends with `τετρ[αα]ρ`, while `χης` continues the word on line 2. The
uncertain pair cannot yet be bounded by visible word-level anchors. The broad
first-line inspection band, x 1800-6700, is not an alpha bounding box.

## Mapping the measured exposures to the composite

The composite crop at source `(1000,1200,6800,4500)` was requested at width 2044
but arrived at **2000 x 1324**. Calculations use the received dimensions. Modern
57r's raw JPEG is rotated counterclockwise to 2044 x 1533 for comparison.

Initial SIFT matching with grayscale and inverted grayscale produced only 15
and 19 ratio-test matches. Subsequent inspection of the three color channels and
their inversions yielded at most 68 matches, with inverted blue. A partial-affine
fit had 24 fit inliers and a held-out median error of 1.125 crop pixels, but its
held-out 95th-percentile error was **918.174 pixels**. It therefore failed the
feature-level check. That failed check remains in the record; it was not silently
converted into an accepted registration by dropping inconvenient matches.

The resulting transform was retained only as a candidate navigation map. A
different check compared gradient magnitudes in 35 fixed, disjoint 128 x 128
patches. Gaussian smoothing used a 3 x 3 kernel and sigma 0.8; Sobel magnitudes
used a 3-pixel kernel. Phase correlation used a Hann window. The fixed grid has
x centers 240 through 1680 in steps of 240, and y centers 320 through 1120 in
steps of 200, in the received composite crop.

Before this check, its acceptance thresholds were set to at least 20 patches
with response at least 0.3, median residual shift at most 1.5 pixels and 95th-
percentile shift at most 3 pixels. **33 patches met the response threshold**;
their residual shifts had median 0.645 and 95th percentile 1.475 pixels. The
paired patches were also visually inspected. This supports coarse page mapping.
It is a cross-method sanity check, not independent validation: the patches can
contain features used in the preceding fit, and the match is dominated by later
writing. It does not establish correct attribution of a faint undertext stroke.

## Frozen component check

All 42 existing PCA components were cropped to the known line-3 control. PC7
was selected visually there, before opening the line-2 control or first-line
band. The PCA was not refitted. PC7 was then used unchanged for both comparisons.

As a descriptive check, the published composite's blue-minus-green values were
mapped into the PCA display coordinates and correlated with negative display
intensity. PC7's Pearson correlations were 0.444 on the selection strip and
0.395 on the line-2 check. For context, PC1 scored 0.321 and 0.382, while PC11
scored 0.374 and 0.509. PC7 was not replaced with PC11 after seeing the check.
The small advantage over PC1 on the second strip is not strong evidence of
undertext-specific separation. All component results, not only favorable ones,
are retained.

These are correlations with a previously processed rendering, not reading
accuracy, probabilities or independent ink identification. Adjacent pixels are
not independent samples. Line 2 was withheld from the *component choice*, not
from the original unsupervised PCA, which used the larger page rectangle.

The first-line strip still contains obscured and ambiguous shapes. No alpha,
erasure trace or alternative wording was accepted. The measured JPEGs can
preserve some structure associated with the known-line controls, but this pass
has not resolved the correction described by the edition.

## Reproduction

The recorded affine transform is deliberately fixed in the replay tool. It maps
rotated raw coordinates to the received composite crop; source-to-crop scaling
uses 2000/6800 horizontally and 1324/4500 vertically. PCA display coordinates
subtract `(200,273)` from rotated raw coordinates. Three pixels of navigation
padding are added around each mapped line band.

Download the exact composite URL recorded in the JSON, and reuse the immutable
raw reference and 42 component PNGs from the preceding pilot:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python tools/textual_restoration/check_zacynthius_line_controls.py \
  --raw-reference /data/57r/00057-R+MB530GN_005.jpg \
  --composite /data/61r-upper-composite.jpg \
  --pca-dir /data/57r-pca --output-dir /data/new-line-controls
python -m unittest tests.test_zacynthius_line_controls tests.test_zacynthius_spectral -v
```

The tool verifies input hashes and dimensions and refuses an existing output
directory. The portable replay reproduced all patch measurements, correlations,
coordinate boxes and six strip-image hashes exactly in the recorded environment.
Fourteen focused tests passed with image dependencies installed; they test code
and coordinate handling, not manuscript interpretation.

## Next candidate

Further tuning of this double-alpha correction has not earned priority over a
different surviving-ink uncertainty. In the pinned TEI, undertext 83v at Luke
10:33 has unclear spans in `κατ εν`; the editors explicitly state that the
space does not accommodate `κατα αυτον` and that the remaining letters are very
unclear. This is a published uncertainty, not our discovery.

The manifest identifies that leaf as canvas 166, reconstructed from modern
164v and 165r. The next bounded test should first locate its passage in the
published image, then acquire spectral exposures only for the relevant modern
half. Neither a familiar verse completion nor the edition's spacing judgment
may be substituted for visible traces. No new reading of that passage is claimed
here.

Follow-up: the [83v spectral test](ZACYNTHIUS_83V_SPECTRAL_2026-10-18.md)
acquired modern 164v's 51 exposures and tested the published uncertainty. A fixed
spectral contrast improved check-line image agreement, but no new reading was
established.
