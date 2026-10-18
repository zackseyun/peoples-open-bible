# Public-source recovery probe: Codex Zacynthius

Research date: 2026-10-14. Scope: public sources only, following the user's
confirmation that private Ephraemi spectral images and the requested Job edition
are unavailable. **No new biblical reading has been established.** POB's source
text and English remain unchanged.

Update on 2026-10-17: [four raw-capture JPEG exposures were acquired](ZACYNTHIUS_RAW_EXPOSURES_2026-10-17.md)
after public archive access recovered. The access failures below describe
October 14, not the current availability. No new letter has been accepted.

## What actually became available

The [Birmingham project](https://www.birmingham.ac.uk/research/centres-institutes/textual-scholarship-and-electronic-editing/projects/codex-zacynthius)
already used multispectral imaging to produce an edition of the erased Luke
text and its surrounding commentary. This is published scholarship, not our
discovery. The [Cambridge viewer](https://cudl.lib.cam.ac.uk/view/MS-ADD-10062-UNDERTEXT/121)
provides processed composites, and the project's
[official XML repository](https://github.com/itsee-birmingham/codex-zacynthius-xml)
provides the transcription and editorial uncertainty annotations.

The archival XML download returned an IT status HTML page in our direct request.
The raw-exposure archive also failed in the attempted public requests. Neither
failure proves the data are permanently unavailable. We recovered valid TEI from
the project's GitHub repository instead, pinned at
`1dceaa3f798abda1b2df74ffbc0ed47abce40a7f`. Its header contains both edition
`n="2.0"` and the wording `Version 1.0`; the commit and file hash identify the
actual input without silently resolving that inconsistency.

The [acquisition receipt](../sources/textual_restoration/discovery/zacynthius_acquisition.2026-10-14.v1.json)
records ten acquired files, 3,651,496 bytes, their URLs and SHA256 values. These
include two overviews, three source-scale regions, metadata and edition files.
No raw spectral exposure stack was acquired. The failed HTML response is excluded.
Images remain outside Git; their redistribution terms are not assumed to match
the XML's CC BY 4.0 license.

## What the uncertainty inventory tells us

The [derived inventory](../sources/textual_restoration/discovery/zacynthius_uncertainty.2026-10-14.v1.json)
contains all 20 `unclear` elements plus eight `supplied` elements attributed to
the transcriber. These are **XML element counts**, not counts of unread letters,
unresolved words, new variants, or independent witnesses.

Nineteen of these 28 annotations concern paratext, including numbers or headings.
Some numbers are above a line rather than in a `margin` segment, so merely
excluding marginal segments would incorrectly count them as biblical wording.
The nine body-text annotations are seven unclear spans and two supplements:

| Folio | Passage | Published annotation | Recovery priority |
| --- | --- | --- | --- |
| 20r | Luke 2:21 | Transcriber-supplied word | Check visible support, not novelty by default |
| 43r | Luke 7:4 | Transcriber-supplied letter | Check visible support |
| 46r | Luke 7:25 | Unclear letter in first-hand reading | Requires abbreviation/correction analysis |
| 60v | Luke 9:4 | Unclear letters in gutter | Physical visibility may be limiting |
| 61r | Luke 9:7 | Two unclear alphas in first hand | Bounded faded-ink/correction probe |
| 72r | Luke 9:50 | Unclear letter, page damage | Check whether ink-bearing material survives |
| 75v | Luke 10:1 | Unclear epsilon, faded ink | Candidate for independent spectral comparison |
| 83v | Luke 10:33 | Two faded-ink spans | Candidate for independent spectral comparison |

This is not an exhaustive unresolved-text list: for example, the complete count
table also retains 171 Tregelles-supplied `illegible` elements and 278
Tregelles-supplied `gutter` elements. They are not included in the 28-entry
priority subset. Published supplements are hypotheses or inherited readings,
not pixels newly recovered by us. Document-order foliation and explicit placement
targets are both retained; conflicting location labels must be checked against
the viewer before extracting a target.

## Image probe and its limit

Canvas 121 is labelled `61r_LXIr_57r and 64v`, a reconstructed undertext leaf
composed of two modern pages. Its image service advertises 9051 by 13100 pixels.
The requested 1600-pixel-width overview actually arrived at 1381 by 2000, so it
must not be mistaken for source-scale evidence. Three additional IIIF regions
were acquired with `full` sizing and their returned dimensions verified:

| Source x,y,width,height | Returned dimensions |
| --- | --- |
| 2000,2400,2000,2000 | 2000 by 2000 |
| 4000,2800,2000,1000 | 2000 by 1000 |
| 6000,2800,1600,1000 | 1600 by 1000 |

Visual inspection shows horizontal older writing amid strong, roughly
perpendicular later writing. Colors are products of spectral processing, not
natural ink colors or independently measured wavelength channels. The inspection
did not securely register the exact uncertainty's bounding box. It therefore
does not establish whether this specific pair of letters is recoverable.

The edition already distinguishes a first-hand double-alpha spelling in Luke
9:7 from a corrected reading involving erasure and a supplied alpha. That
distinction was known to the inspecting model, so this was not a blind reading.
No alpha, correction, alternative spelling, or theological implication is claimed
as newly discovered. Even a successful confirmation would initially be a small
palaeographical result, not a breakthrough in biblical meaning.

## What would justify another experiment

1. Register one surviving-ink uncertainty to an exact source rectangle using
   legible neighboring lines; preserve the edition's alternative hands.
2. Obtain genuinely different measured exposures or independently produced
   spectral renderings for that same rectangle. The public raw-data record is
   [DOI 10.25500/edata.bham.00000428](https://doi.org/10.25500/edata.bham.00000428),
   but its files were not acquired in this run. A working public mirror or restored
   service would materially change the available evidence.
3. Freeze the target and controls before testing separation methods. Use known
   letters, overtext crossings and blank parchment as controls; measure false
   ink as well as apparent legibility. Color separation of one composite can
   help inspection, but cannot count as independent spectral confirmation.
4. Ask an independent reader to record shapes without the expected verse, then
   compare with the edition and prior scholarship. All completions stay labelled
   conjectural until supported by the surviving traces and scholarly review.

Generative image or video completion cannot supply missing physical evidence.
It may illustrate a hypothesis, but generated strokes cannot settle this test.
Likewise, replacing a gap with the familiar Luke wording is prediction, not
recovery. Missing parchment needs another witness or a separately labelled
reconstruction, not sharpening. The earlier
[AI recovery experiments](AI_MANUSCRIPT_RECOVERY_2026-10-13.md) remain relevant.

## Reproduction and decision

Clone the public XML repository, check out the pinned commit, then run:

```sh
python tools/textual_restoration/triage_zacynthius.py /path/to/Zacynthius-gospel.xml --output /path/to/inventory.json
python -m unittest discover -s tests -p test_zacynthius_triage.py -v
```

The command rejects inputs whose hash differs from the pinned transcription.
Tests cover wrong-format responses, paratext, separate reading hands, page/line
state and element-versus-letter counts. The source authors are the Codex
Zacynthius Project: R. Kevern, P. Manafis, A.C. Myshrall and H.A.G. Houghton;
the JSON is our derived inventory under the source's CC BY 4.0 attribution terms.

Decision: retain this as a concrete public-source target set, not a discovery.
Do not launch a broad model swarm on identical composites or repeatedly generate
sharper-looking versions. Proceed when an exact registered target and a new
discriminating observation are available. The acquisition and triage are real
progress; a new accepted reading remains unachieved.
