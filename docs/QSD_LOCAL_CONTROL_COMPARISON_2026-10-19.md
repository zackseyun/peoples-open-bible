# Qumran ink detection development controls

Local contrast features reduce false ink detections in the existing Qumran
classifier, but the improved models still fail the fixed development screen.
Adding one training fragment increases recall and false detections in this
setup. **None of these models is ready to support a manuscript transcription.**
This is useful method testing while the Glasgow image request is pending, not
a newly recovered biblical reading or an improvement over published MTEM.

The [frozen protocol](../sources/textual_restoration/discovery/qsd_local_controls_protocol.2026-10-19.v1.json)
defines the comparison before inference. The [complete results](../sources/textual_restoration/discovery/qsd_local_controls.2026-10-19.v1.json)
retain every fragment, input hash, prediction digest and failed screen.

## Comparison and results

Four OpenCV random forests combine two training sets with two feature sets.
The original training image is `124_001`; the second set also includes
`690_003`, the first nonempty fragment under that identifier prefix. Each
contributes 30,000 class-balanced labeled pixels. The raw features are the
first measured band, last measured band and their signed difference. The local
variant appends neighborhood-standardized contrast from each band, using the
fixed Gaussian scale, variance floor and clipping limits in the protocol.

All four models evaluate the identical 18 other fragments, every pixel:
55,900,000 pixels per model. Neither training image enters any comparison
score. The published MTEM column uses its released masks on exactly these
18 inputs; MTEM itself was not rerun. These are different fragment images,
not a verified manuscript-disjoint or blind test: all 20 were part of earlier
development, and identifier prefixes are not authenticated witness identities.

| Method | Pooled precision | Pooled recall | Fixed mean F1 | False ink pixels | Empty-control false pixels |
| --- | ---: | ---: | ---: | ---: | ---: |
| Released MTEM | 0.9358 | 0.8720 | 0.7475 | 113,725 | 0 |
| One training image, raw | 0.5220 | 0.9196 | 0.4445 | 1,599,827 | 32,154 |
| One training image, local | 0.6623 | 0.9325 | 0.6223 | 903,327 | 7,672 |
| Two training images, raw | 0.4910 | 0.9444 | 0.4440 | 1,859,924 | 28,289 |
| Two training images, local | 0.6036 | 0.9593 | 0.6063 | 1,196,688 | 9,320 |

Precision and recall refer to pixels matching the released annotations, not
correctly read letters. Fixed mean F1 uses the same 16 nonempty-reference
fragments for every method. Both empty-annotation fragments remain in the
pooled counts and are reported separately. Their annotation status does not
prove that the physical objects contain no ink.

With one training image, the local features reduce false detections by
43.54 percent, from 1,599,827 to 903,327, while increasing recall. On the two
empty-annotation controls, the count falls 76.14 percent, from 32,154 to 7,672.
Both are measurable gains over our prior classifier, but still far from the
released method's performance on the same inputs.

The difficult `124_008` case remains disqualifying. Its local one-image model
has F1 0.1537, versus released MTEM's 0.2037. Its 15,885 true-positive pixels
come with 172,942 false positives: high recall alone is not reliable access to
writing. All four models fail each of the four predeclared conditions: pooled
precision, fixed-subset mean F1, difficult-fragment F1 and empty controls.

The extra training image increases false detections in both feature settings,
despite improving recall. This changes both training coverage and sample count,
so it does not isolate why precision worsens or show that more data is generally
harmful. It does reject assuming that this particular addition automatically
makes the detector safer.

## Source and method boundaries

The public [QSD study](https://arxiv.org/html/2411.10668v1) provides cropped
first-band and last-band 16-bit images and reference masks. Its method separates
ink, parchment and other regions using measured spectral differences and
contour information. Our classifier comparison uses only the already acquired
first and last bands; it is not a twelve-band analysis or a reproduction of
that algorithm.

Every feature derives from those measured pixels. There is no verse text,
letter recognizer, inpainting, generated stroke or language completion. The
output consists of class counts and prediction digests, not restored source
images. Agreement with a mask still does not authenticate a faint physical
stroke, its writing layer or its letter identity. Transfer to Greek palimpsests
would require different validation; passing this development screen could not
authorize a Bible-text change.

The existing cache supplied 98 verified inputs totaling 169,674,433 bytes:
40 spectral TIFFs, 40 reference masks and 18 released prediction masks. Every
input hash was checked again after processing. The original raw-feature model's
confusion counts exactly reproduce the earlier probe on all 18 common fragments.
An independent arithmetic check verifies all 72 new prediction rows and 18
reference rows against their counts, source totals and fixed denominators.
This is one fresh four-model run, not an independently replicated new benchmark.

## Reproduction and next decision

The [tool](../tools/textual_restoration/probe_qsd_local_controls.py) reads only
the pinned cache; it performs no downloads and refuses to overwrite an existing
result. Model parameters, sampled training-index digests and per-fragment binary
prediction digests are retained. NumPy 2.3.5, Pillow 12.3.0 and OpenCV 4.13.0
were used. OpenCV reported eight threads despite one being requested, so an
effective single-thread run is not claimed.

```sh
python tools/textual_restoration/probe_qsd_local_controls.py --cache /data/qsd \
  --protocol sources/textual_restoration/discovery/qsd_local_controls_protocol.2026-10-19.v1.json \
  --output /data/qsd-local-controls.json
python -m unittest tests.test_qsd_local_controls tests.test_qsd_metrics -v
```

Fourteen focused tests passed, covering signed differences, finite local
features, fixed sampling, false-positive accounting and the separation between
a development pass and transcription approval. They test processing/reporting
behavior, not ancient text.

Keep local contrast as a development lead, but do not deploy these masks or
retune this cohort until its figures look favorable. The next discriminating
step needs independently verified ink/layer labels and genuinely separate
manuscript controls. The [Glasgow request](CODEX_H_DATA_REQUEST_DRAFT_2026-10-18.md)
remains the route to the original Codex H measurements; this experiment neither
replaces those data nor supplies a new reading while they are pending.
