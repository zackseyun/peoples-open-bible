# Luke 10:33: measured spectral contrast, no new reading

We acquired all 51 public spectral JPEGs for modern folio 164v, which contains
the upper half of Zacynthius undertext 83v. A fixed linear contrast learned on
a neighboring line reproduces the published rendering better than the selected
PCA component does on a separate check line. **The uncertain phrase in Luke
10:33 remains unresolved. No new letters or Bible-text change are justified.**

This is a bounded follow-up to the [61r line-control experiment](ZACYNTHIUS_LINE_CONTROLS_2026-10-17.md).
The [machine-readable record](../sources/textual_restoration/discovery/zacynthius_83v_spectral.2026-10-18.v1.json)
contains all acquisition receipts, alignment measurements, component weights,
failed cross-modal feature checks, patch checks, regression coefficients and
output hashes. Images remain outside Git. Neither new processing nor improved
agreement with an existing image is a textual discovery.

## Why this passage

The [pinned project edition](https://github.com/itsee-birmingham/codex-zacynthius-xml/blob/1dceaa3f798abda1b2df74ffbc0ed47abce40a7f/Zacynthius-gospel.xml)
marks the tau and the following `εν` as unclear in `κατ εν`. Its note states:

> There is not enough space for κατα αυτον here. The remaining letters are very unclear.

That is a previously published uncertainty, not our discovery. It cannot be
resolved by inserting familiar wording from another witness. The edition file
has SHA-256 `789dbe9d7840b8d224f925c7ce50d79aca260b6adabc326b646a9efa8e56bdd0`.

[Cambridge canvas 166](https://cudl.lib.cam.ac.uk/view/MS-ADD-10062-UNDERTEXT/166)
is labelled `83v_LXXXIIIv_164v and 165r`. Visible neighboring lines place the
passage in modern 164v. Inspection supports only a broad second-line navigation
band: source x 2800-7100, y 4930-5210 in the 9051 x 13100 composite. Neither
the initial nor a second visual pass could securely bound the uncertain word.
Both readers had seen the edition; neither pass was blind.

## Acquisition and preservation

The [Birmingham dataset](https://edata.bham.ac.uk/428/), DOI
10.25500/edata.bham.00000428, credits D.C. Parker, H.A.G. Houghton and Michael
Phelps, with EMEL capture in July 2018. The public files carry CC BY 4.0.
We used `00164-V/` in the 798,881,705-byte archive
[`00161-00176.zip`](https://edata.bham.ac.uk/428/9/00161-00176.zip).

All 51 members were length/CRC checked and individually SHA-256 hashed, totaling
24,967,308 bytes. They are grayscale 8-bit JPEG derivatives at 1533 x 2044,
not sensor RAW files or full-resolution TIFF masters. The archive ETag was
`63a05604cf5580427cc434cdadd66d16`; **the whole archive hash was not verified**.

An initial single-block download timed out before publishing any member. The
successful retry used six payload ranges of at most 4 MiB, plus the ZIP index
ranges. HTTP status, exact Content-Range, length and stable ETag were checked.
All 51 originals remained unchanged after processing. The existing ZIP verifier
is reused; the acquisition wrapper refuses an existing output directory.

The repository describes TIFF copies as available by request. No such request
was sent, and no master TIFF was obtained. This experiment stays within the
user's public-source and non-generative-processing constraints.

## Alignment and PCA

The preceding pilot's algorithm and acceptance gates were retained. The script
now accepts `--folio 164v`, while defaulting to 57r. A full 57r regression run
reproduced all 42 component PNG hashes, alignments, means, standard deviations,
eigenvector weights and variance fractions exactly.

The 42 MB/W exposures were selected before fitting; Aux, RL, RR and TX were
excluded. All 41 non-reference bands passed the existing alignment checks
against `00164-V+MB530GN_005.jpg`. Held-out feature-error medians ranged from
0.043 to 0.420 original pixels; 95th percentiles ranged from 0.171 to 1.285.
These are feature-level measurements dominated by later writing, not independent
undertext-stroke validation. SIFT orientation duplicates are not independent
physical controls.

The fixed raw-image rectangle is x 280-1260, y 200-1800. Standardized PCA uses
every eighth pixel in each direction, retaining all 42 components. As before,
component signs are fixed by the largest-magnitude coefficient and displays use
1st-to-99th-percentile stretches. No text, character model, inpainting,
deconvolution or sharpening enters the calculation.

## Navigation is not letter registration

The [published composite crop](https://images.lib.cam.ac.uk/iiif/MS-ADD-10062-UNDERTEXT-000-00166.jp2/1000,2000,7000,4500/2000,/0/default.jpg)
arrived at 2000 x 1286. Its SHA-256 is
`338dbac8f176629f42f780b528d7d26aa195c130529ad23899b7e5060d52dc29`.
Eight grayscale/color representations were tried for SIFT matching, using the
same 6000-feature, 0.7-ratio, alternating fit/check procedure as the prior leaf.
Only inverted blue supplied at least 40 matches: 88, with 28 fit inliers.
Its held-out median error was 1.206 crop pixels, but its 95th percentile was
739.382. **That feature check failed**, and its outliers remain in the record.

The candidate partial-affine transform was retained only for navigation. The
same separate 35-patch gradient/phase-correlation sanity check supported 33
patches, with residual median 0.935 and 95th percentile 1.586 pixels. It passed
the previously fixed thresholds. Patch pairs were visually inspected.
This is not independent validation: patches may contain fit features, and later
writing dominates their match. The transform has an approximately 180-degree
orientation reversal relative to the counterclockwise-rotated raw image.

## Frozen control comparison

The selection strip is the right end of line 1, source x 6000-7000,
y 4720-4900. The separate check strip is the right end of line 3,
x 6000-7000, y 5260-5480. PC7 was chosen visually from all 42 selection strips
before viewing the target at full size, then kept fixed. The whole-page contact
sheet had already been seen, and the PCA training rectangle included the target;
this was not a fully blinded or target-excluded PCA experiment.

The table reports Pearson correlation with mapped blue-minus-green values from
the already processed Cambridge composite. It is descriptive image agreement,
not reading accuracy or a probability that a letter is correct.

| Fixed method | Selection line 1 | Check line 3 |
| --- | ---: | ---: |
| PC1, negative display intensity | 0.390 | 0.478 |
| Visually selected PC7, negative display intensity | 0.703 | 0.435 |
| Linear spectral contrast | 0.876 | 0.854 |

The PC correlations use their existing clipped displays; regression correlations
use unclipped predictions. This is not a controlled reading-performance benchmark.

PC7 therefore did not outperform PC1 on this check strip. The negative result
was not hidden by switching to another component after seeing the check.

## One additional non-generative contrast

For a bounded alternative, a ridge regression maps the 42 aligned measured
intensities to the composite's B-G values **using only the selection strip**.
Bands are standardized using that strip's means and standard deviations. The
fixed penalty is 0.1 in `X'X/n + 0.1 I`; it was not tuned against the check or
uncertain line. The regression has no spatial neighborhood or text input:
each prediction is a linear combination of that pixel's measured exposures.
Weights, intercept and training-only display limits are then frozen for the
check and target strips.

The separate check-line agreement is substantially higher than for PC7, but this
fits a processed reference, not independently identified ink classes. Adjacent
pixels are correlated, and the reference derives from the same imaging campaign.
It can improve a viewing contrast without establishing a newly recovered letter.
The training and check RMSEs are 19.629 and 20.354 composite-difference units.

The uncertain strip is 1082 x 77 working pixels. The second inspection found no
new securely attributable stroke and no defensible narrower anchor. Prominent
dark marks also occur in the comparison rendering; contrast alone does not
establish which writing layer produced them. **Accepted new characters: zero.**

## Reproduction and next gate

With NumPy, Pillow and OpenCV installed, use new output directories:

```sh
python tools/textual_restoration/acquire_zacynthius_164v.py --output-dir /data/164v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python tools/textual_restoration/probe_zacynthius_spectral.py \
  --folio 164v --source-dir /data/164v --output-dir /data/164v-pca
python tools/textual_restoration/check_zacynthius_83v_controls.py \
  --source-dir /data/164v --pca-dir /data/164v-pca --composite /data/83v-composite.jpg --output-dir /data/83v-controls
python tools/textual_restoration/probe_zacynthius_83v_contrast.py \
  --source-dir /data/164v --pca-dir /data/164v-pca --composite /data/83v-composite.jpg --output-dir /data/83v-contrast
python -m unittest tests.test_zacynthius_spectral tests.test_zacynthius_line_controls tests.test_zacynthius_83v_contrast -v
```

Twenty-four focused tests and nine ZIP-verifier tests passed with image
dependencies installed. The portable
control replay matched all patch measurements, component correlations, boxes and
six strip-image hashes exactly. A second linear-contrast run reproduced its
complete report and all three image hashes exactly. Tests validate processing
code, not ancient text.

This pass has not earned an open-ended search for more flattering parameters.
Further investment in this phrase requires a concrete attributable trace,
materially better source measurements available within the access constraints,
or a stronger independent paleographical control. A familiar completion, a
generated restoration or a sharper-looking image is not sufficient. POB remains
unchanged by this experiment.
