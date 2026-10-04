# Hebrew Sirach (Ben Sira) — Source Materials

Sirach (also called Ecclesiasticus) was composed in Hebrew around 180 BC
by Yeshua ben Eleazar ben Sira in Jerusalem. The Greek translation by his
grandson (c. 132 BC) was preserved in the Septuagint tradition. Greek
and surviving Hebrew forms must be compared passage by passage; this
guide does not establish which source every modern translation uses.

Roughly **two-thirds of the original Hebrew text has been recovered**
from:

- **Cairo Genizah manuscripts A, B, C, D, E, F** (10th–12th century
  copies of earlier Hebrew), discovered by Schechter in 1896 onwards
- **Masada scroll** (c. 100 BC, covers Sirach 39:27–43:30)
- **Qumran fragments** (2Q18, 11QPsa — small)

Our goal is to translate Sirach *primarily from the Hebrew* where we
have it, consulting the Greek where the Hebrew is lost or damaged.
This is an editorial preference, not proof that each extant Hebrew
reading is earlier or preferable. Declare the target literary form,
align content rather than verse numbers, and disclose meaningful
alternatives under the [adjudication method](../../docs/TEXTUAL_ADJUDICATION_METHOD.md).

## Clean-licensed source path

Do not vendor modern edition content (including Beentjes 1997,
Skehan & Di Lella 1987 and Ben-Ḥayyim 1973) without compatible
rights or permission. The source paths below distinguish
redistributable material from deferred image inclusion. Restrictions
on reproducing an image do not by themselves prohibit comparing a
published reading with an appropriate citation.

### 1. Schechter & Taylor 1899 (MSS A and B)
See [`schechter_1899/`](schechter_1899/). Public-domain scholarly
edition with Schechter's printed Hebrew transcription and facsimile
plates of MSS A and B. This covers the first Genizah manuscripts
discovered (about half of the total recovered Hebrew Sirach). Already
downloaded and vendored here.

### 2. Planned AI transcription from appropriately licensed photographs
See [`genizah_photos/`](genizah_photos/). For manuscripts and folios
not covered by Schechter 1899 (MSS C, D, E, F, additional B folios),
the planned workflow would produce our own transcription from:
- Cambridge Digital Library (cudl.lib.cam.ac.uk) — Taylor-Schechter
  collection images. License terms vary per item; we use only those
  with permissive research+redistribution terms or request explicit
  permission where needed.
- Oxford Bodleian public-domain imagery.
- JTS New York and BnF Paris for their respective holdings.
- Friedberg Genizah Project (genizah.org) — images require
  registration; we do not vendor their files. Citations only.

Provenance for each transcribed folio is recorded in
`genizah_photos/PROVENANCE.md` as pages are processed.
This is not a claim of completed, calibrated transcription. Fresh readings
remain subject to the [image-reading calibration and review gates](../../docs/TEXTUAL_ADJUDICATION_METHOD.md#calibration-and-review).

### 3. Masada scroll (deferred)
See [`masada/`](masada/). The Masada Ben Sira scroll photographs are
currently hosted by the **Israel Antiquities Authority Leon Levy Dead
Sea Scrolls Digital Library** under a restrictive license
(`© 2026 IAA — reproduction prohibited without written permission`).

We have drafted a formal licensing request to the IAA (see
`masada/IAA_LICENSING_REQUEST.md`). Pending their response, Masada
Sirach remains **blocked for direct inclusion** in POB. This affects
approximately Sirach 39:27–43:30.

In the interim we use Schechter-era transcription for sections where
MS B overlaps with the Masada scroll, and clearly annotate the
transcription gap where it does not.

## What this gives us

| Sirach section | Primary Hebrew witness we can use | Status |
|---|---|---|
| 3:6 – 16:26 (approx.) | MS A (Schechter 1899) | Public domain, vendored |
| 30:11 – 33:3, 35:11 – 38:27, 39:15 – 51:30 | MS B (Schechter 1899 + later publications) | Public domain, vendored where 1899 covers |
| 4:23 – 5:13, 6:5 – 37, 18:31 – 19:3, 20:5 – 7, 25:8 – 26:2 | MS C | Via later PD publications — to verify |
| 51:13 – 30 | MS B, folio 21 recto/verso | Published transcription consulted; not an image-verified POB transcription |
| 39:27 – 43:30 | Masada scroll | **Blocked on IAA licensing** |
| 6:14–15, 6:20–31 | Qumran 2Q18 | Image redistribution/access to be checked separately from published comparison |
| 51:13–20 and final 51:30 phrase | Qumran 11QPsa / 11Q5, columns 21–22 | Published transcription consulted; damaged and missing content is not supplied as attestation |

Where usable Hebrew is absent, the Greek working source must be clearly
marked. The current Sefaria/Kahana data are a composite edition, not a
single surviving manuscript. The [2026-10-04 comparison](../../docs/OT_SOURCE_COMPARISON_CONTINUATION_2026-10-04.md#sirach-poem-comparison-and-delivery-findings)
documents the poem's source alignment and attribution defects. The
[B viewer](https://bensira.org/navigator.php?Manuscript=B&PageNum=41)
identifies T-S 16.315 at 51:12–20; the
[E viewer](https://bensira.org/navigator.php?Manuscript=E&PageNum=1)
identifies chapter 32–33 material, not this poem. The table's earlier
assignment of 51:13–30 to E and grouping of 11QPsa with chapter 6
were incorrect. Other table ranges are not newly verified by this pass.

## Methodology

Every verse of Sirach in POB will declare its primary-source witness
in the per-verse YAML:

```yaml
source:
  edition: Hebrew Sirach MS A (Schechter 1899)
  text: "…Hebrew text…"
  greek_parallel: "…LXX Greek for comparison…"
```

Where the Hebrew and Greek diverge materially, both readings are
preserved: Hebrew in the main `source.text` field, Greek in
`source.greek_parallel`, and a footnote on the English translation
flags the divergence.

This records POB's intended workflow, not an achieved superiority over
other translations or certification of the current verse records.
