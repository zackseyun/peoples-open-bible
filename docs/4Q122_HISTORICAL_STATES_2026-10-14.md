# 4Q122: historical photographs and associated scraps

Research session: October 13, 2026, America/Los_Angeles; October 14 UTC.
Continuation of [native-image recovery](NATIVE_MANUSCRIPT_RECOVERY_2026-10-13.md).

## Result

Two historical infrared negatives, dated January 1956 and February 1960 by the
IAA, are now acquired as previews and selected native-level tiles. Four further
catalogued scraps have been inspected in modern color and infrared. This adds
real observations from different photographic states, not generated content.
**No new biblical character, manuscript join, textual identification, or POB
source/English revision is accepted.** The breakthrough objective remains active.

The distinction matters: a different photograph of the same object can preserve
additional optical evidence, but is not an independent textual witness. Likewise,
multiple catalogue entries do not increase the biblical witness count.

## Source acquisition

The [machine-readable receipt](../sources/textual_restoration/discovery/4q122_historical_states.2026-10-14.v1.json)
records 46 original responses, totaling 3,142,383 bytes, with URLs and SHA256
hashes. These comprise 11 image-record HTML pages, 11 pyramid metadata files,
11 previews, 10 native tiles, two catalogue API pages, and the institutional
photographic inventory. No custodial photographs are committed to the repository.
No images were sharpened, inpainted, stitched, or synthetically completed.

The public site's `search.js` specifies `/api/search?t=image` with
`q=manuscript_numbers:'4Q122'` and the page parameter `p`. Reading both pages
resolved the previously unseen thirteenth result. The full result set has five
modern fragment pairs, one modern mixed plate, and two historical mixed plates.
The receipt preserves the returned catalogue data, including associations;
these are not independently adjudicated fragment identifications.

| Record | Catalogue description | Native pyramid dimensions | Received preview |
|---|---|---|---|
| [B-280375](https://www.deadseascrolls.org.il/explore-the-archive/image/B-280375) | PAM M41.933; January 1956; scanned infrared negative | 4190 x 3135 | 512 x 383 |
| [B-284329](https://www.deadseascrolls.org.il/explore-the-archive/image/B-284329) | PAM M43.291; February 1960; scanned infrared negative | 4464 x 6237 | 366 x 512 |
| [B-496220](https://www.deadseascrolls.org.il/explore-the-archive/image/B-496220) | Plate 265; December 2014; color photograph | 3258 x 4272 | 915 x 1200 |

Both historical record pages name Najib Anton Albina. The modern plate names
Shai Halevi. API dates include a day field; the public historical descriptions
give only month and year, so this report does not claim a verified capture day.
The old pyramids lack top-level image dimensions: native dimensions are obtained
from tile count times 512 minus empty edge pixels, and agree with the API.

For M43.291, native level 4 tiles `(1,8)`, `(2,8)`, `(3,8)`, `(1,9)`, `(2,9)`
and `(3,9)` cover the main-fragment area and its right-hand neighbour, with some
backing. For M41.933, level 4 tiles `(5,0)`, `(6,0)`, `(5,1)` and `(6,1)` cover
the corresponding main-fragment area and surrounding objects. All ten are
unaltered 512-square JPEG responses, inspected at original display detail.
These are regional acquisitions, not complete native plates or camera originals.

The [institutional inventory, fascicle 7](https://lyingpen.uia.no/dssinventoryproject/fascicle7/)
was directly acquired as HTML. Its 4Q122 entry links SN49, plate 265 and 43.291,
with miscellaneous 41.867 and 41.933. Its 43.291 listing describes 4Q122 as
published by Ulrich, fragments a-f, alongside other manuscripts including
4Q126. The historical inventory's publication-status language is historical,
not evidence that DJD IX remains forthcoming today. PAM 41.867 was not acquired.

## Historical comparison

The main fragment is visually recognizable in both historical plates from its
outline, central damage and surviving lines. The inspected historical regions
show the same recognizable damaged text as the modern infrared preview and
previously acquired native target tiles. This is visual correspondence, not a
computed cross-date registration or a new diplomatic transcription.

The lower broken row is visible in the 1960 native tile `(2,9)`, the 1956 tile
`(6,1)`, and the modern main-fragment infrared preview. Its appearance differs
with scale, backing, wrinkles and capture contrast. No particular extra
character or loss of ink between dates was established. A brighter old trace
alone cannot distinguish surviving ink from photographic or surface effects.

The scrap matching modern catalogue fragment 25 is placed to the main
fragment's right in the 1960 photograph. It appears separately below the main
fragment in the 1956 overview/target area, and separately to its right in the
2014 plate. These arrangements are not demonstrations of an ancient join.
Even the historical proximity is not newly discovered text. No edge fit,
original line spacing or common-hand assignment is accepted from placement.

The 2014 whole-plate catalogue lists 4Q121, 4Q122, 4Q126 and 4Q9999. The older
plates also contain multiple manuscripts. Do not search or train as though
every visible Greek scrap belongs to one Deuteronomy manuscript.

## Additional scraps: image-only observations

| Plate 265 fragment | Color / infrared record | Native dimensions per image | Inspected preview |
|---|---|---|---|
| 25 | B-472938 / B-472939 | 2296 x 2296 | 1200 x 1200 |
| 35 | B-472978 / B-472979 | 1792 x 1792 | 1200 x 1200 |
| 36 | B-472982 / B-472983 | 1736 x 1736 | 1200 x 1200 |
| 37 | B-472986 / B-472987 | 1816 x 1816 | 1200 x 1200 |

All eight previews were inspected at original 1200-square display detail. Their
advertised larger native images were not acquired in this pass. The plates and
API identify these as May 2014 photographs by Shai Halevi. Catalogue fragment
numbers have not been mapped to DJD's editorial fragment letters/numbers.

A bounded second observer received only the four original previews for 35 and
37, without the manuscript name, proposed passage or expected words. It did
not consult editions or search a corpus. This is an exploratory same-family
model reading, **not** the project's independent-model consensus gate and not
a calibrated accuracy measurement. The following candidates were frozen before
any proposed biblical alignment. Coordinates are approximate preview-pixel
`(left, top, right, bottom)` rectangles, not generated segmentation masks.

| Fragment / row | Shape-only candidate | Approximate rectangle |
|---|---|---|
| 35 upper | Cut upright and adjoining oblique; abstain | (549,605,655,686) |
| 35 upper | Pi-like top and two descending strokes | (752,620,867,704) |
| 35 upper | Uninterpretable edge mark | (882,683,909,705) |
| 35 lower | Cut strokes; abstain | (305,911,361,943), (346,870,403,902) |
| 35 lower | Open-right curve, compatible with lunate sigma | (408,849,474,931) |
| 35 lower | Tau-like top and descending stem | (498,849,634,945) |
| 35 lower | Iota-like upright; stroke clearer than identity | (648,847,685,951) |
| 35 lower | Cut right-edge ink; abstain | (707,855,755,913) |
| 37 upper | Tau-like, upper bar against broken edge | (550,635,632,728) |
| 37 upper | Rounded ink mass with bent descending stroke; abstain | (634,637,700,730) |
| 37 upper | Cut curved/oblique mark; abstain | (703,678,766,725) |
| 37 lower | Partial pi-like form | (466,859,579,946) |
| 37 lower | Partial rounded epsilon-like form | (584,886,658,977) |

Infrared makes the same ink shapes easier to delimit. The strongest reported
clarification is the middle horizontal in the epsilon-like form on fragment
37, approximately `(613,908,652,925)` in B-472987. It is poorly separated from
the background in color, but neither observer establishes a securely new,
color-absent stroke or letter. For fragment 25, the root observer noted an
epsilon/nu-like upper remnant and uncertain lower strokes; fragment 36 has
an angular form and nu-like form. These remain informal candidates, not
accepted readings, completed words or biblical assignments.

## Decision and reopening conditions

The historical acquisition lead succeeded; the attempted new-letter reading
did not. Do not repeat the same preview inspection or scale up generative
completion in the absence of a new discriminating observation. The current
scrap strings are too short and damaged to establish a unique biblical match.
A Bible-only search would exclude the serious nonbiblical alternative by design.

The next decisive input for this target is the actual consulted primary
edition: Ulrich, DJD IX (1992), pp. 195-197 and plate XLIII, with Parsons's
introductory pp. 11-12 where relevant. It has not been obtained in this run.
Until its fragment map, readings, underdots and exclusions are inspected, no
scrap reassignment or historical-photo trace can honestly be called unpublished.

Reopen image analysis for a specific edition-disputed trace, a demonstrably
different historical state, a physical join candidate with matched scale and
orientation, or a new measured exposure. Fit any cross-date transform on
unchanged landmarks and evaluate separate regions; the previous modern-pair
geometric pass does not validate these historical photographs. Preserve blank,
broken and nonbiblical alternatives, and test candidate readings against more
than the expected biblical passage. Generated completions may illustrate such
hypotheses but cannot supply manuscript evidence for them.

If exact edition access remains unavailable, pursue a different target with
both inspectable measured imagery and a consultable critical edition rather
than prolonging this particular uncertainty with more model votes. The broader
recovery goal remains open; this bounded target's present outcome is unresolved.

Local validation re-read every receipt input, checked saved hashes and byte
counts, checked the 13 unique catalogue results, and reconciled native pyramid
dimensions with the API. Regenerating the receipt produced identical content.
The four existing native-pyramid unit tests and `git diff --check` pass. These
checks validate acquisition bookkeeping, not the proposed letter shapes.
