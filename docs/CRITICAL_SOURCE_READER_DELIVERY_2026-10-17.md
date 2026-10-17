# Critical Hebrew source delivery and the Samuel application boundary

Date: 2026-10-17. Research baseline: `c1ddab1660b541f6ed1383c936f1f88819dd0428`.

The existing critical-source route can represent the complete 1 Samuel 2:22
proposal without a schema change. The remaining application decision must
identify the intended reader surface and its disclosure. The local exporter,
live CDN payload and public provenance page provide different information.
No canonical verse or reader implementation is changed by this follow-up.

## The supported source route

The alternative `schemas/ot-critical-verse.schema.json` and
`tools/textual_restoration/critical_verse.py` already support an honestly labelled
`POB-critical` source and its pinned integration record. Current canonical
Isaiah 53:11, Deuteronomy 32:8, Psalm 145:13 and 1 Samuel 17:4 use that route.
The legacy edition enum rejects this label by design; its rejection alone is
not an application blocker. The preceding Samuel preflight overstated the need
for new schema/consumer integration. Its frozen result remains unchanged;
this follow-up corrects that inference rather than weakening the schema.

The [Samuel source record](../sources/ot/pob_critical/1_samuel/002/022.json)
now belongs to the partial research corpus. It is byte-identical to the frozen
reviewed-source record, not a new witness or new editorial vote. The
[canonical-format candidate](../sources/textual_restoration/applications/samuel2_22_application_20261017/candidate.v1.yaml)
differs from the frozen reviewed verse only in the path to that identical
source record. Its Hebrew, English, notes, rationales and history are unchanged.
Existing verification and three negative source/English/note probes passed;
the [preparation receipt](../sources/textual_restoration/applications/samuel2_22_application_20261017/preparation.v1.json)
records the pins and unchanged canonical target. This is preparation, not an
application approval or an edit to `translation/`.

`tools/export_mobile_bible.py` loads canonical YAML and exports English plus
referenced footnotes. It intentionally does not carry the Hebrew/source object.
The raw WLC drafter separately refuses to overwrite an already selected critical
source. Neither behavior resolves the external publisher's output.

## Live delivery observation

The [dated probe](../sources/textual_restoration/applications/samuel2_22_application_20261017/delivery_probe.v1.json)
pins a successful GET of the [CDN manifest](https://bible.cartha.com/manifest.json)
and its declared [payload](https://bible.cartha.com/cob_preview.json). At the
observation time, the manifest identified main commit
`5fae1212c4725f1bae775d114db3f07f02be9a12`; the payload was 13,826,374 bytes,
SHA-256 `6f0c0a57a7f4110fdeacbe4955680e0afafb7cc94b94f07753ed7ce8f4c2e793`.
These are dated delivery observations, not permanent claims about those URLs.

The DEU 32:8 and 1SA 2:22 objects contain only `verse` and `text`. Their English
matches local canonical English after removing inline note markers; their
referenced notes are absent. The root, target-book and target-chapter objects
provide no alternate note channel. A recursive key scan finds no footnote,
apparatus, provenance or critical-integration keys. It does find 29 book-level
`source_witness_url` fields elsewhere; do not generalize this to an absence of
every source-related field. A separate agent independently reproduced the
manifest/payload pins and target shapes, not the browser inspection.

Root inspected the actual public Deuteronomy chapter and provenance interfaces.
The chapter shows the adopted sons-of-God wording without inline note markers
or uncertainty prose. Selecting verse 8 exposes **Check Provenance**. Clicking
it opens the correct [DEU 32:8 record](https://peoplesbible.com/verse/?ref=DEU.32.8),
where `POB-critical`, Hebrew, composite-source disclosure, apparatus and both
anchored notes are visibly readable. The page also says the current cross-check
is incomplete, not passed. Thus the disclosure is accessible through a separate
action; it is not absent from the whole website. No mobile UI or offline reader
was tested, and this does not verify future Samuel rendering after adoption.

The workflow `.github/workflows/publish-pob.yml` triggers on main pushes touching
`translation/**`, invokes an external publisher and then requests a website
rebuild. It does not run the local exporter as its publishing implementation.
A canonical application followed by ordinary merge therefore enters a publishing
workflow. The exact external code responsible for the missing payload notes
has not been inspected, and no external implementation has been changed.

## Clean reading and the next application decision

The user's concern is that inline disclosure can make the Bible look messy.
Delivering note data does not require inserting explanatory prose into verses.
The proposed design keeps the reading text unchanged and offers **Textual
notes** when a verse is selected, opening a compact panel with alternatives and
uncertainty. Full Hebrew and apparatus remain under Check Provenance. No such
UI change is approved or implemented here; the existing provenance action is
the demonstrated baseline.

Inline display is not an invented prerequisite for source adjudication. A
separate application review must specify whether the existing on-demand
provenance route adequately delivers this candidate's essential disclosure,
or whether a different arrangement is required before release. The absent CDN
notes cannot be counted as successfully delivered merely because the local
exporter preserves them. Conversely, their absence does not invalidate the
Hebrew selection or prove that readers cannot access its rationale.

The Samuel source and English remain provisionally reviewed research, with
no canonical application approval. No new source-priority vote, manuscript
decipherment, canon change, publication certificate or agreement loop occurred.
The next concrete step is the exact application/disclosure assessment using
this observed route; any publisher or reader-code changes need their own scope
and implementation checks. A second export format is not required to represent
this source in the repository.
