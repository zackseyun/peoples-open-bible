# Native manuscript images for the next recovery attempt

Research session: October 13, 2026, America/Los_Angeles; acquisitions continued
on October 14 UTC. This follows the [AI recovery experiments](AI_MANUSCRIPT_RECOVERY_2026-10-13.md).

The next useful investment is **measured imagery and exact edition comparison**,
not a larger generative-model run. Two previously incomplete acquisitions now
work: regional Zuqnin photographs at requested native-coordinate dimensions,
and native-level color/infrared tiles for 4Q122. The latter pair passes a bounded
geometric correspondence test. Neither acquisition has produced a defensible
new biblical letter or a source/English revision.

The ongoing objective remains a genuine, verified advance in biblical source
recovery. These results are progress toward that objective, not its completion.
Confirming a published word, improving a photograph, and discovering an
unpublished reading require different evidence.

## Zuqnin acquisition and reading limit

The [acquisition receipt](../sources/textual_restoration/discovery/zuqnin_measured_regions.2026-10-13.v1.json)
records eight files, their custodial URLs, SHA256 values and actual dimensions.
The manifest and ordinary spread were retained from the preceding experiment;
the image-service metadata, alternate spread and regional responses are new.

Canvas `p0222` represents current 107r-106v; `p0223` is the additional capture
labeled `107r.[02.wl.0000]-106v.[02.wl.0000]`. Their whole-spread JPEG responses
are 5000 by 3976 and 5000 by 3886 pixels. The second image is visibly different,
with a blue background and changed contrast. Neither that appearance nor the
label establishes the wavelength or a calibrated multispectral exposure.

The first image service advertises 8168 by 6495 coordinates. A request for
`1200,1800,1400,1400/1400,/0/default.jpg` returns 1400 by 1400 pixels. Its
180-degree counterpart and the same numeric region in the alternate capture
also return 1400 by 1400. These are usable 1:1 requested regional responses,
not a newly acquired original camera file. The overview alone had been reduced
to 5000 pixels wide. No full native-resolution spread is claimed.

All three square regions were inspected at native display detail. The rotated
left-leaf overview was also inspected, but the display reduced its 2000 by 2987
pixels to 1280 by 1912. The two full spreads were likewise displayed smaller.
Rotation and cropping were requested directly from the public IIIF service;
no local inpainting, generated completion or sharpening was performed.

The consulted edition remains Tisserant, printed 220 / PDF 322: column I has
vanished writing, while column II contains partial readings assigned to
Ezekiel 39:23-24. Printed 274 / PDF 376 maps this to current 107r and assigns
39:22-24. This is ZV, not the ZVI renewal-promise witness on current 78r.
Fresh visual consultation of complete printed lxvi-lxviii / PDF 80-82 adds
useful layout constraints: normally two columns, 21 lines, approximately
8-10 letters per line, and unusually corroded leaves including 105-108.
Those general measurements do not establish an image-to-line transform.

The regional images did not provide a secure Greek sequence or baseline
separable from Syriac writing, surface marks and watermark. A second visual
observer, given no expected biblical text, likewise abstained. Its useful
contribution was a registration warning: large gray Latin-looking forms in
the alternate crop belong to the custodial watermark, which continues onto
the backing. They must not enter an ancient-ink mask.

Two red four-dot ornaments support overlap of the crops, with an approximate
80-pixel horizontal and 14-pixel vertical displacement after accounting for
rotation. This is a visual starting point, not a computed registration.
The same numeric crop coordinates in different captures are not the same
physical rectangle. No subtraction, Greek-column registration or character
label was accepted. This is a failed reading attempt at the inspected regions,
not proof that every surviving part of the leaf is unreadable.

### Historical photographs and later scholarship

A bounded research agent located the [IRHT ARCA record](https://arca.irht.cnrs.fr/ark%3A/63955/md472v23z87n).
Its search-indexed catalogue lists black-and-white microfilm MF 52533 covering
ff. 1-173v, acquired in 1997, and SYR 8 including ff. 96-130, acquired in 2017.
These acquisition years are not photography dates. The films have not been
obtained or inspected; direct ARCA access returned 403. They are leads for
different photographic states, not verified superior or spectral images.
The catalogue limits redistribution and permits internal consultation.

[Pinakes manuscript 73150](https://pinakes.irht.cnrs.fr/notices/cote/73150/)
supplies later bibliographic leads: Crisci 1996, pp. 152-154; D'Aiuto 2003,
pp. 240-241; Rahlfs-Fraenkel 2004, pp. 352-358; and Orsini 2005, pp. 158-162.
The Vatican catalogue additionally cites Voicu, *Note sui palinsesti conservati
nella Biblioteca Apostolica Vaticana* (2009), pp. 445-454,
[DOI 10.1400/213551](https://www.torrossa.com/en/resources/an/2656219).
These passages remain unconsulted. A limited search found no verified later
decipherment of the target column, but historical novelty is not established.

## 4Q122 native color and infrared acquisition

The IAA identifies [B-472934](https://www.deadseascrolls.org.il/explore-the-archive/image/B-472934)
as full-spectrum color and [B-472935](https://www.deadseascrolls.org.il/explore-the-archive/image/B-472935)
as infrared, both recto, plate 265 fragment 24, photographed by Shai Halevi in
May 2014. The current color page was read through the web tool; the current
infrared HTML was acquired directly after web rendering failed. Its viewer
URL and metadata match the earlier source record.

Both public `=g` metadata responses specify a 3296 by 3296 pyramid, 512-pixel
tiles, and native inverse scale 1 at level 3. The site's public viewer code
documents the `=x{column}-y{row}-z{level}` request pattern. Four unmodified JPEG
tiles per exposure, at `(2,2)`, `(3,2)`, `(2,3)` and `(3,3)`, were acquired and
inspected at 512 by 512 pixels. Their union is the source-coordinate rectangle
`[1024,1024,1024,1024]`; no stitched image was made. This covers the hole-adjacent
target and nearby writing, not the entire fragment or all associated scraps.

The [receipt](../sources/textual_restoration/discovery/4q122_native_tiles.2026-10-13.v1.json)
preserves all ten files: eight tiles plus two XML metadata files, 370,916 bytes.
This resolves the earlier acquisition limit in the [September image follow-up](4Q122_DEUT11_IMAGE_FOLLOWUP_2026-09-06.md),
which received only 1200-square previews. The pyramid coordinate scale is
3296/1200, approximately 2.75 times as many pixels per dimension. This ratio
describes sampling, not a measured optical-resolution gain or character accuracy.
Raw spectral frames and original camera files remain unavailable here.

The color views resolve parchment texture and backing fibers through the hole;
the infrared views provide a different ink/background contrast and softer
texture. The physical gaps remain gaps. Inspection does not supply a complete
new letter in the missing region or a revised diplomatic transcription.

### Geometric development test

The [numeric correspondence result](../sources/textual_restoration/discovery/4q122_tile_correspondence.2026-10-13.v1.json)
fits color-to-infrared affine coordinates using tile column 2 and evaluates
the separate tile column 3. Before execution the script fixed SIFT at 2000
features and contrast threshold 0.04, mutual matching with a 0.7 nearest-neighbor
ratio, and affine RANSAC with a 3-pixel threshold, 2000 iterations, confidence
0.99, 10 refinement iterations and seed 1776. The regional check requires at
least 25 validation matches, both validation tiles represented, and at least
90 percent within 3 native pixels. Parameters were not retuned after the run.

The result uses 138 fitting matches, including 120 RANSAC inliers. Of 139
held-out matches, 129 (92.8 percent) lie within 3 pixels. Median validation
residual is 0.786 pixels; the worst is 477.24 pixels. All failures remain in
the receipt. A passing regional check therefore does not make every automatic
match correct or establish precise alignment of any particular thin stroke.

These are feature matches, not independently authenticated landmarks or ink
labels; multiple descriptors may describe related features. The held-out
regions are from the same fragment and pair of photographs. This is geometric
development evidence, not a blind transcription benchmark, an additional
textual witness, or an image-restoration accuracy score. The model never reads
Greek or emits a modified bitmap. OpenCV 4.13.0 and NumPy 2.3.5 were used;
OpenCV again reported eight threads despite one being requested.

### Where novelty could still lie

[Kraft's section 01](https://ccat.sas.upenn.edu/rak/earlylxx/jewishpap.html#01)
already reports an unusual space inside the conventional red-word reading,
after upsilon, and the fragility of that identification. Root verified the
saved source section; the research agent also fetched it afresh. Rediscovering
that spacing or recognizing the familiar word is not a new scholarly result.
The damaged theta/second-rho area is our image target, not an assertion about
which letters the unconsulted DJD edition underdots.

The required primary edition is Ulrich in DJD IX (1992), pp. 195-197, plate
XLIII. Parsons's pp. 11-12 belong to the same volume's introduction, not a
separate publication. The [IAA manuscript record](https://www.deadseascrolls.org.il/explore-the-archive/manuscript/4Q122-1)
also names the edition. No open inspectable copy of those pages or plate was
obtained in the bounded search. The [institutional inventory](https://lyingpen.uia.no/dssinventoryproject/fascicle7/)
supplies historical photo leads PAM 43.291 and miscellaneous 41.867/41.933.
These photographs have not been acquired in this run.

The higher-value continuation is to compare those historical plates with the
native pair and establish the identity of associated, incompletely identified
scraps. Their group membership must be checked before proposing a biblical
alignment. Searching many short strings against a known Bible can produce
chance matches; physical dimensions, handwriting, line geometry and competing
nonbiblical identifications must constrain any proposed join or identification.

## Reproduction and decision

Source photographs stay in the private cache. The repository receives tools,
numeric receipts and observations, not custodial images or new license claims.
The acquisition tool validates the expected pyramid geometry and native level;
four unit tests check valid geometry and rejection of changed origin, reduced
scale and preview dimensions. The correspondence tool verifies every input
tile's hash against the acquisition receipt. Neither overwrites a differing
existing report.

```sh
python tools/textual_restoration/acquire_4q122_native_tiles.py \
  --cache /path/to/private/cache --output /path/to/private/acquisition.json
python tools/textual_restoration/measure_4q122_tile_correspondence.py \
  --cache /path/to/private/cache --receipt /path/to/private/acquisition.json \
  --output /path/to/private/correspondence.json
python -m unittest discover -s tests -p test_4q122_native_tiles.py -v
```

NumPy, Pillow and OpenCV are optional research-runtime dependencies; no changes
to the production corpus dependencies are required. Cached inputs must be the
original downloaded responses; their provenance is recorded, not inferred from
filenames. A future server response or runtime may differ from this receipt.

Prioritize the 4Q122 historical-plate/associated-scrap comparison next. Keep
Zuqnin active only for better measured views or a secure column locator; do
not spend a training run on its presently unseparated layers. The two bounded
agent tasks supplied acquisition/prior-art research and image geometry, not a
swarm of transcription votes. No discovery or goal-completion claim follows
from this session's successful acquisition and regional correspondence.
