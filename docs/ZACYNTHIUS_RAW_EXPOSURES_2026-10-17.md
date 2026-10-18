# Codex Zacynthius raw exposure access

On 2026-10-17, four separate spectral-capture JPEGs of modern folio 57r
became available for inspection through the public Birmingham archive. This
removes the access obstacle recorded in the
[October 14 probe](ZACYNTHIUS_PUBLIC_RECOVERY_2026-10-14.md), but does not resolve
the uncertain writing in Luke 9:7. No new letter or biblical reading is accepted.

## Acquired evidence

The [official archive](https://edata.bham.ac.uk/428/) now returns the actual
dataset record and supports byte-range downloads. Its record lists the archive
files under CC BY 4.0 and credits D.C. Parker, H.A.G. Houghton and Michael
Phelps. EMEL captured the images for the Codex Zacynthius Project in July 2018.

The existing `tools/dss/inspect_remote_zip.py` indexed the 1,046,756,775-byte
`00041-00060.zip` archive, then retrieved four selected members. It verified
HTTP ranges, consistent ETags, ZIP member lengths and CRCs; SHA256 values are
in the [acquisition receipt](../sources/textual_restoration/discovery/zacynthius_raw_access.2026-10-17.v1.json).
The complete archive was not downloaded or checksum-verified. The selected
payloads total 1,902,004 bytes; that acquisition transferred 2,197,159 verified
range bytes including directory and header data. Earlier access/index probes
are additional traffic, not included in that figure.

| Archive member within `00057-R/` | Bytes | Inspection |
| --- | ---: | --- |
| `00057-R+MB530GN_005.jpg` | 577,036 | Strong later writing and decorative heading |
| `00057-R+MB940IR_016.jpg` | 489,361 | Much of the heading is suppressed relative to MB530GN |
| `00057-R+W365G58_022.jpg` | 331,795 | Dark overall exposure with strong later writing |
| `00057-R+TX940IR_051.jpg` | 503,812 | Substantial additional writing consistent with show-through |

All four are **1533 by 2044, 8-bit grayscale JPEGs**, not sensor RAW or the
full-resolution TIFF masters. The archive's term "raw capture" distinguishes
individual exposures from processed composites; it must not be read as a claim
that these JPEGs preserve the original sensor values or maximum spatial detail.
The index contains 51 JPEGs for 57r, of which only four were acquired here.
The other modern half of undertext leaf 61r, folio 64v, was not acquired.

The four original files were visually inspected without local rotation,
normalization, contrast changes or generative editing. The marked differences
show that the exposures contain different visual information. They do not show
that any particular extra trace belongs to the sought undertext: the transmission
image especially requires controls for writing showing through from the reverse.
The much darker W365G58 exposure also makes unnormalized visual comparisons
unreliable as measures of ink separation.

## What this enables

Modern folio 57r supplies the upper half of the published reconstructed leaf
61r. That leaf contains a published faded-ink uncertainty involving the first
hand and a correction in Luke 9:7. The exact uncertainty still needs a registered
image rectangle; a folio match is not a letter-level match. The model has already
seen the edition's proposed reading, so its inspection cannot count as blind.

The next useful experiment is alignment and controlled separation of measured
exposures, with known undertext, later writing, reverse-side show-through and
parchment controls. It should compare these JPEG derivatives against the sharper
published composite before requesting or acquiring more data. A brighter or
cleaner-looking result is not itself a recovered letter. No expected verse text
should enter pixel separation, and no generative filling belongs in the evidence.

Full-resolution TIFFs are described by the repository as available by contacting
its research-data team with project reference `2018/houghtha-codex-zacynthius`.
No request has been sent and no TIFF has been acquired. The working public JPEG
route now supports a bounded pilot before considering that separate access step.

## Reproduction

From a full repository checkout, with a new output directory:

```sh
python tools/dss/inspect_remote_zip.py https://edata.bham.ac.uk/428/3/00041-00060.zip \
  --size 1046756775 --output-dir /path/to/new-probe \
  --member '00057-R/00057-R+MB530GN_005.jpg' \
  --member '00057-R/00057-R+MB940IR_016.jpg' \
  --member '00057-R/00057-R+W365G58_022.jpg' \
  --member '00057-R/00057-R+TX940IR_051.jpg'
python -m unittest tests.test_remote_zip -v
```

All nine acquisition-tool tests passed on October 17. They check download and
ZIP integrity behavior, not spectral interpretation or transcription accuracy.
Image files remain outside Git; the repository holds provenance and findings.
The observation changes the next research action from finding access to testing
actual exposures. It is not a manuscript decipherment or a completed breakthrough.
