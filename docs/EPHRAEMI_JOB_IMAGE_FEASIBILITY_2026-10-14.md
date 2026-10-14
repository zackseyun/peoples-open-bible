# Codex Ephraemi Job image recovery feasibility

Research session: October 14, 2026. Continuation of the
[AI manuscript recovery investigation](AI_MANUSCRIPT_RECOVERY_2026-10-13.md).

## Result

Codex Ephraemi offers a concrete palimpsest target with both accessible
photographs and a directly consultable historical edition. The present pass
locates Job on folio 33 recto and verso, acquires unmodified Gallica images,
and identifies gaps in Tischendorf's printed transcription. **No new biblical
letter or word is accepted.** POB's source text and English remain unchanged.

The positive result is a reproducible target, not decipherment. Faint writing
is visible in the lower verso, but its attribution and exact correspondence
to the printed missing line are not secure. Reading the expected verse into
those traces would not recover evidence.

## Manuscript and edition location

The object is Paris, Bibliotheque nationale de France, Grec 9, Codex Ephraemi
Syri rescriptus, Rahlfs C. The [Gallica viewer](https://gallica.bnf.fr/ark:/12148/btv1b8470433r)
labels view 78 as folio 33r and view 79 as 33v. These are viewer sequence
numbers, not manuscript folio numbers.

Tischendorf's 1845 *Codex Ephraemi Syri rescriptus, sive fragmenta Veteris
Testamenti* is available as a [complete scan](https://archive.org/details/codexephraemisyr00tisc).
Its printed prolegomena page 5, PDF page 17, maps the Job transcription on
printed pages 7 and 8 to codex folio 33. The difficulty grades are h for the
recto and f for the verso. Section 5 explains the a-to-h scale, with h at the
most difficult end. The table also records damage from the later writing
and numerous holes. These are nineteenth-century observations, not a modern
diagnosis of recoverability.

| Manuscript surface | Gallica view | Printed edition page | PDF page, one based | Printed footer coverage |
|---|---|---|---|---|
| 33r | f78 | 7 | 31 | Job 10:9 to 11:5 |
| 33v | f79 | 8 | 32 | Job 11:5 to 12:2 |

All three relevant edition pages were rendered and visually consulted. OCR
was acquired for navigation, but does not control the folio mapping, Greek
letters or editorial gap signs. The footer ranges do not mean every intervening
verse survives legibly.

The recto transcription contains extensive gaps. On the verso, printed line
13 has an incomplete right end, and printed line 38 is entirely represented
by gap marks. These two positions are historical targets for comparison,
not claims that present scholarship has failed to read them. No modern
apparatus reading is supplied by this report.

## Photographs actually inspected

The [acquisition receipt](../sources/textual_restoration/discovery/ephraemi_job_feasibility.2026-10-14.v1.json)
records 12 original responses totaling 19,081,263 bytes, including the edition,
OCR, catalogue and photographs. Three local edition renders are recorded
separately. URLs, byte counts, SHA256 hashes and received dimensions allow
later comparison without committing custodial manuscript images to Git.

| Asset | Received dimensions | Observation limit |
|---|---|---|
| Gallica f78 `.highres` overview | 1024 x 1353 | Overview with bottom attribution, not full-resolution source |
| Gallica f79 `.highres` overview | 1024 x 1350 | Same limitation |
| f78 viewer export | 2052 x 2651 | Whole-page display was resized during inspection |
| f79 viewer export | 2054 x 2648 | Lower writing additionally inspected at received-pixel scale in browser |
| Four f78 central IIIF regions | 256 x 256 each | Each covers a 512 x 512 source region, so these are half-scale tiles |

The four recto regions start at source coordinates (1536, 2048), (2048, 2048),
(1536, 2560) and (2048, 2560). The filename `native.jpg` is not proof of
native resolution: the IIIF size parameter explicitly requests 256 pixels
across a 512-pixel source region. Likewise, the full-page exports request
2052 and 2054 pixels across; they are not new captures or spectral exposures.

Direct terminal requests for the manifest and a verso region returned HTTP
403. The normal Gallica browser viewer was accessible after its automatic
verification, and its ordinary export/download controls supplied the images.
No CAPTCHA was solved and no access control was bypassed.

No manuscript bitmap was locally sharpened, inpainted, recolored, stitched
or generated for this pass. Viewing and server resampling must nevertheless
be distinguished from acquisition of camera-original pixels.

## Reading outcome

The recto contains strongly obscured writing beneath the later text. The
central regions show overlapping strokes without a secure new sequence.
The verso is more legible overall, and faint large letter-like marks are
visible below and between the darker later writing. The lower region around
export y=2050 to 2180 was inspected as a possible location for the final
printed lines. That approximate region is not an accepted line registration.

The principal reader had already consulted Tischendorf, so these observations
are not blind. A separate image-only observer could not access the specified
browser tab and returned an abstention without seeing an image. That is an
access failure, not an independent negative reading, and supplies no model
agreement. No literal character candidates are promoted from this attempt.

The missing printed line is not filled from another Bible text. A text model
could readily propose a plausible completion, but that would answer what is
expected in context, not which strokes this manuscript preserves. A future
candidate must retain separate fields for observed traces, uncertain letters
and supplied text.

## Later scholarship and novelty

The [current institutional catalogue](https://septuaginta.uni-goettingen.de/catalogue/Ra_C/)
records an Old Testament revision begun by Felix Albrecht in 2010 and cites
Ziegler's *Iob* (1982), pages 9 to 10. Its Job coverage distinguishes surviving
ranges around this leaf. The catalogue is an access and bibliography source,
not a substitute for the target apparatus. Ziegler's introduction and exact
Job readings remain unconsulted in this pass.

Albrecht's 2010 article, [DOI 10.1515/zaw.2010.021](https://doi.org/10.1515/zaw.2010.021),
reports improved Ecclesiastes readings using fluorescence photographs. The
bounded prior-art check consulted its abstract and author bibliography, not
the full article. This establishes relevant prior work, not a new POB result
or a reading of Job folio 33. No numerical result from that abstract is used
as a performance estimate for our target.

The [SCHRIFT-BILDER manuscript project](https://schrift-bilder.org/en/manuscript-research/)
describes multispectral 3D work on Ephraemi and illustrates folio 73r. Its
demonstration is not a downloaded band stack for folio 33. The possibility
of better measured images is therefore real, but their availability for
this target has not been established. Modern photographs must also be
compared with already published recoveries before any novelty claim.

## Next discriminating experiment

1. Obtain the lawful target-specific Ziegler apparatus and any later Job
   revision. Determine whether the two historical gaps remain unresolved.
   A reading absent from Tischendorf alone is not a discovery.
2. Obtain native-resolution or actual fluorescence/multispectral captures of
   the relevant surface, with wavelength and capture metadata where available.
   Another enlargement of this export does not satisfy that input.
3. Register securely legible neighboring undertext to the edition before
   assigning a gap. Freeze image regions and an image-only shape pass before
   introducing the expected wording.
4. If real spectral bands become available, compare measured channel
   separation against the untouched images and held-out known strokes. Include
   blank parchment, later writing, holes and stains as false-ink controls.
   Evaluate recovered characters and abstentions, not visual attractiveness.
5. Promote only reproducible, spatially anchored traces through the existing
   [adjudication method](TEXTUAL_ADJUDICATION_METHOD.md). Even a genuinely new
   manuscript reading still needs a separate textual-history and POB adoption
   argument before changing English.

Without either a consulted modern comparison or materially better measured
imagery, repeated reading of the same export is low-yield. Generative image
or video completion may illustrate a documented hypothesis, but must remain
outside the evidence, OCR and source-selection paths. The overall breakthrough
objective remains unachieved.
