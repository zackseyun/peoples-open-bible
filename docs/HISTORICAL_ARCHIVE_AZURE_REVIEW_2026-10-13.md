# Historical source review - approved keyless execution

## Verified execution, not a finished-book claim

The user explicitly approved using the existing Azure sign-in. The new
`tools/historical_scan_review.py` uses Microsoft Entra via AzureCliCredential,
restricted to the verified subscription and HTTPS Azure OpenAI endpoint. It
does not retrieve AWS secrets, API keys, passwords, or create roles/resources.
The older automatic-key-loading Azure helpers were not invoked.

Real inference has succeeded with two separately provisioned model families:
the writer deployment declares GPT-6.1 Sol (2026-09-29), and the independent
review deployment declares GPT-5.6 Terra (2026-07-09). Azure API responses report
deployment aliases; exact declared versions are saved from read-only ARM
metadata, not invented from the response alias. Prompts, source hashes, actual
response IDs, outputs, usage and final/cached record hashes are retained in a
private research directory. These are actual calls, not model-name placeholders.

## Source-facing protocol

1. Read the complete Newberry scan without any English transcription/OCR in
   the primary prompt. Preserve all foreground textual lines and separately
   describe printed graphics, avoiding empty graphic-as-text entries.
2. A different actual model reviews every line and checks omitted regions.
3. Only after those recorded passes, compare unproofread archive OCR and the
   published reading of another copy. Location leads remain proposals, not
   independently approved scan equivalences. Adjudicate differences against
   the source, preserve genuine uncertainty, then independently re-review.
4. Aggregate every physical leaf and resolve/disclose source issues before
   claiming book completion. Rights and publication are separate decisions.

The two-page pilot covered the title and first preface. A title-page delimiter
disagreement persisted between models; it is not declared solved by majority
vote or by accepting JSP's bracket-encoding convention as a literal glyph.
Supplemental lossless original-pixel crops retain parent-image hashes and
coordinates and accompany, never replace, the complete source image. No
generative restoration, font reconstruction, or invented missing text is used.
The reviewer also placed a confident bleed-through observation in its
uncertainty field on a preface pass; the protocol now separates observations
from unresolved reading questions rather than silently accepting all flags.

The initial credential probe failed before any HTTP inference request because
Azure CLI rejects simultaneous subscription and tenant selectors. The saved
failure was inspected and retained, and the approved subscription alone is now
used. An optional later review timed out before its response ID was observed;
that unknown outcome was retained and **not blindly retried or used as evidence**.

## Long-run controls and remaining work

Background responses are persisted and polled using their same actual response
ID; transient observation failures do not create another billable POST. Unknown
creation outcomes stop that unit and remain explicitly unresolved. No automatic
POST retries are enabled. SDK/credential/HTTP diagnostic logging is suppressed,
and failures retain error type/status rather than arbitrary credential output.

The whole-book run selects the other 296 leaves, while preserving the two
pilot leaves as their own traceable records. Four bounded workers operate under
a conservative writer token window based on the verified existing quota; no
capacity or resource settings are changed. All 298 leaves remain the declared
scope, including covers, apparent blanks, index/contents and errata. Failures and
unresolved source questions remain in the ledger, never silently counted as
verified. Source integrity tests: 21; keyless/protocol offline tests: 13.

No reader file has been replaced or newly published in this execution. The
existing OCR warnings remain appropriate until full-scope review, adjudication,
source/rights decisions and publication verification actually finish.

Official implementation references:
- [Azure Responses and Entra authentication](https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/responses?view=foundry-classic)
- [OpenAI image inputs and original-detail limits](https://developers.openai.com/api/docs/guides/images-vision)
- [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses)
- [OpenAI background response polling](https://developers.openai.com/api/docs/guides/background)

Structured formatting and two model labels do not prove source fidelity or
approve a book; the actual source-bound outputs and full-scope audit are required.

## Approved isolated public-domain review configuration

On 2026-10-13 the user explicitly approved a scoped, isolated configuration for
D&C 1835. The default policy's optional protected-text matcher returned
`content_filter` on original-source transcriptions while the harm categories
were safe. Those refused outputs were never accepted as source readings.

The subscription and tenant were reverified. The live policy-list response
exposed `Microsoft.DefaultV2`; direct GET for that built-in name returned 404.
New policy `pob-dc-1835-public-domain-review` clones the live baseline, changing
only completion Protected Material Text `blocking` true to false, while keeping
its detector enabled. All other settings remain identical, including the
baseline's annotation-only Protected Material Code. The harm-category filters
remain enabled/blocking at Medium; the direct prompt shield remains blocking.

Separate `pob-dc-1835-writer` and `pob-dc-1835-reviewer` deployments provisioned
successfully, each GlobalStandard capacity 100, using the same two verified
model versions and no automatic version upgrades. Available regional quota was
checked first. ARM before/after snapshots confirm every preexisting deployment
is unchanged. No reader/production route or source text was changed.
Checked-in ARM payloads and operational boundaries are in
`infrastructure/historical-review/`. No credentials or private execution
traces are checked in. Keyless runtime acquisition now serializes token-provider
access and allows 120 seconds for the Azure CLI subprocess; no keys are read.

The runner now bounds dispatch to active worker capacity. Creating its `STOP`
marker stops new units and drains existing ones, preserving API handles.
A GET-only recovery retrieved the four earlier credential-interrupted response
IDs to terminal completion without any new POST. Unknown creation outcomes with
no response ID remain untouched. A newly versioned, previously terminal-filtered
leaf 10 is the isolated lane's end-to-end probe, not an observation-timeout retry.
Configuration/test success is not a whole-book source or rights approval.

## Alternative encoding, not visual restoration

Native JPEG close-ups resolved at least one punctuation question while several
other readings remain ambiguous. The archived `GR_711_jp2.zip` was acquired and
checked against its published Internet Archive metadata SHA-1 and file size.
Its SHA-256 is
`2c3f38b3a209f9d471e6c3bea7aac5d20b3b7ef929467e722b8bbf1b508e8f52`.
The archive is described as Single Page Processed JP2 ZIP; do not call it a
pristine scanner original or a newly discovered physical copy.

For selected problematic leaves, a lossless PNG representation of the decoded
archival JPEG2000 is available alongside the prior JPEG. No interpolation,
upscaling, contrast filtering, restoration, or generated glyphs are used. The
runner pins the complete archive, checks the exact leaf/member and its hash,
and verifies that the supplied PNG has exactly the decoded JPEG2000's mode,
dimensions, and pixel bytes. Both full-page representations stay attached.
The model record includes the alternate representation's provenance, and the
request hash includes its pixels. A changed pixel, leaf, member, archive, or
parent JPEG fails closed. This is source evidence, not an automatic confidence
promotion. Genuine unresolved readings remain flagged.

The Newberry's current open-access policy permits collection-image use for
lawful purposes without library licensing or permission fees:
https://www.newberry.org/collection/order-digital-files . Underlying-work rights
remain a separate responsibility. JSP's linked website terms restrict reuse;
no permission to redistribute its modern editorial material or facsimiles is
claimed, and no new JSP image is added to the model lane. The primary remains
the independently acquired Newberry scan of the 1835 English edition.

## Initial whole-copy audit outcome - 2026-10-14

The full-scope execution and bounded replacement monitor have finished. All
**298 Newberry scan leaves (page images, including covers and blank faces)**
have actual source-only drafts and hash-bound separate-model source reviews.
Two recovered source-only drafts were paired with their initial reviews across
execution-version directories by exact draft-record SHA-256, not folder names.

Final source/comparison/re-review outcomes are **109 page images without model
flags, 188 with unresolved readings, and one blocked comparison/adjudication
stage**. These are model-assessment outcomes, not a claim that 109 pages are
infallible or that the full book is verified. The private issue ledger contains
856 entries across 189 pages; repeated draft/reviewer descriptions remain, so
this is not a count of 856 distinct errors. There is no corrected whole-book
reader publication or rights/editorial sign-off.

Observed API execution is real: 313 unique draft response IDs, 738 adjudication
response IDs, and 1,038 review response IDs were recorded, deduplicated across
copied caches. This lower bound includes terminal failed/filtered responses;
it is not an exact request total, a completed-reading count or billing proof.
34 distinct creation-outcome attempts lack a response ID and remain preserved.
The explicitly approved bounded-replacement ledger contains 30 completed
replacement stages. Later-stage first failures were separately budgeted; an
already failed replacement stage was not automatically posted again.

The remaining Azure block is Newberry scan leaf 242, printed page 239. Its
source-only draft and separate-model source review both completed, but the
completion violence classifier blocked post-comparison generation at Medium.
Protected-text matching was not the blocker here. All other filters remained
unchanged. This stage was **not** repeatedly posted, fragmented, paraphrased,
sent through a hidden alternate route or counted as completed.

A non-generative lexical diff followed by direct full-page/native-crop
inspection found a concrete false negative on that page: lines L005 and L010
both contain printed **hearken**, while both initial Azure models accepted
**harken**. The two earlier English comparisons retain the e. These are
recorded source-backed correction observations, not altered original model
responses, a named third-model execution or a human-editor sign-off. This
example demonstrates why agreement between two models is not enough.

A Cincinnati-hosted candidate was also inspected:
https://cdm16998.contentdm.oclc.org/digital/collection/p16998coll18/id/10166/ .
Its metadata and printed title indicate 1835; metadata describes No Copyright -
United States, not a worldwide license. The acquired PDF contains 285 pages;
its monochrome text images are 150 PPI and JBIG2-encoded, while the cover is
color. Native image extraction did not add resolution or perform restoration.
The candidate must not be silently treated as an independent physical witness,
a superior scan, or a confidence promotion without physical-copy/alignment
review. No new JSP image was brought into the inference lane.

The current raw OCR edition therefore stays `ocr_unproofread`, the source-pass
verified flag stays false, and publication stays false. A source-collated reading
edition using documented witness readings is a different deliverable from an
exact damaged-copy diplomatic transcript; the choice has been requested before
changing that target. The author/audience/date/summary work is separate from
this unfinished source-verification and corrected-reader-publication decision.
