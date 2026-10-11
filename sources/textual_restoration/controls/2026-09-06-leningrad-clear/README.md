# Leningrad 321v: sharper image, unresolved control label

Acquired 2026-09-06. **The image is useful for further inspection, but its
proposed character-level answer key is not approved.** No model accuracy,
restoration, textual variant or translation change is established here.

The [source record](source.json) binds the downloaded photograph, publisher's
checksum, provenance limits and reported rights label. The full original is
3,756 × 4,208 pixels; it shows substantially more distinct letter shapes than
the blurred 1QM development photographs. That is a visual assessment, not an
optical-resolution measurement, proof of image authenticity, or evidence of
textual priority. The publisher is a public mirror, not the holding institution.

The selected crop is the first complete main-text line in the middle column.
Root's visual reading matches a substring of the local WLC source at Zechariah
7:1. However, an independent image-only reviewer, not given the expected words,
reference or other repository files, offered a different tentative reading.
Both are preserved in [reference-candidate.json](reference-candidate.json).
The local edition and photograph represent the same manuscript tradition, not
two historical votes. The reviewer is not a second model-family calibration run.

This is a **label-review disagreement**, not evidence that the manuscript has
a variant against WLC. A contextual reading may correctly resolve ambiguous
shapes, but using it as an answer key requires explicit justification rather
than circularly proving the image by the expected verse. Do not score this crop
as a secure character benchmark yet or rerun reviewers merely until they agree.

Preparation reused `tools/dss/pilot.py prepare` for its generic exact-crop
operation. This medieval codex is not added to the DSS registry; the DSS-specific
`validate` command is not applicable to its identity record. Source/crop hashes,
dimensions and exact pixel correspondence were checked directly. The first
selection was expanded before review to retain tall strokes and descenders;
the final crop still includes small next-line edge traces outside the proposed
line's label scope. No restoration, resampling, sharpening, masking or ImageGen
operation was performed. The source and final crop are retained for reproducible
inspection; no frozen evaluation set or provider pass is fabricated.

Next resolve the label with larger native-scale context or an independently
established diplomatic control, preserving the distinction between published
wording and visible marks. Even successful clear medieval-square-script reading
would not establish performance on ancient scripts or damaged manuscript ink.

## Full photograph context followup October 10

The [dated context check](context-followup.2026-10-10.v1.json) does not resolve
the reference label. A fresh reviewer received only the full photograph and
existing crop, without the expected text, passage or earlier responses. Its
tentative reading differs from the earlier root candidate in a medial letter
and an additional claimed consonant. The response is preserved as given, not
corrected to the edition or promoted into a manuscript variant.

The full photograph was **downsized in the model display**: the reviewer reports
1485 × 1664 rather than the stored 3756 × 4208, even when requesting original
detail. Root received a different resized display, 2999 × 3359. Neither full-page
view establishes a native-resolution context check. The existing 830 × 245 crop
remains byte-identical; its review produced no resize notice. This display
distinction changes the next step: obtain actual native-pixel context or a
defensible diplomatic reference, not more votes on the resized page.

No character score, accepted answer key, two-family calibration, damaged-letter
restoration or source change follows. The original reference disagreement and
all frozen images remain intact. The [continuation record](../../../../docs/RESTORATION_CONTROL_AND_NAHUM_DELIVERY_2026-10-10.md)
separates this unresolved calibration result from the reviewed reader-note
changes now merged into main.
