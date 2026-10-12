# Pseudo-Clementine historical-library publication

## Goal and release boundary

Zack authorized proceeding through actual historical-library publication with
the usual source, translation, licensing and reader checks. Source registration
is not completion. The four catalog rows remain `publish: false`; no new reader
book or website deployment is claimed by this checkpoint.

## Azure reviewer (2026-10-12)

At Zack's explicit request, deployed **GPT-6.1 Sol**, model version
`2026-09-29`, as `gpt-6-1-sol-review` on the existing
`cartha-aoai-truth-1c9177c8` resource in `rg-cartha-truth-openai`, East US 2.
SKU is `GlobalStandard`, capacity 100 (100,000 tokens/minute and 100 requests/
minute reported by Azure), not provisioned throughput. Existing deployments
were not modified. The [deployment/readback receipt](receipts/pseudo-clementine-sol61-deployment-20261012.json)
records the resource and successful live source-intake review.

Calls use the existing authorized Azure CLI session with `az rest` and the
Cognitive Services audience. No API key or bearer token was retrieved into
context, printed, committed, or rotated. The account's existing
`gpt-5-6-sol-atlas` deployment generates drafts; **GPT-6.1 Sol is the separate
review model**, as requested. No model substitution is allowed on reviewer failure.

The earlier Bedrock pilot was explicitly denied by IAM; its failed attempt is
retained as evidence. No AWS policy or role was changed and the denial was not
bypassed. The Azure route is the user's subsequently requested route, and the
repository already documents its existing identity approval in
[Enoch Azure CLI drafting](ENOCH_AZURE_CLI_DRAFTING.md).

## Evidence produced so far

- A fresh Greek-derived draft of all three sections of Peter's letter, generated
  by `gpt-5.6-sol-2026-07-09`. Request, full response, usage and hash-bound
  candidate record are under the work's `translation_workflow/` directory.
- Its draft flags suspected Greek digitization errors. These remain blocking
  source issues, not silently adopted corrections. Explicit elided audit
  quotations are accepted only when every literal span occurs in source order.
- The full three-section English/Greek review request is preserved as
  `azure-v1.review.request.json`. Its first call received an Azure HTTP 500;
  the same request was retried once, with a separate attempt-2 response file.
  **The retry completed successfully on GPT-6.1 Sol.** Sections 1 and 2 are
  `blocked` by unresolved source defects; section 3 is `revise` for lexical
  wording and uncertainty disclosure. All three passed coverage, added-claims,
  names and negations checks, but none is approved for publication. Findings
  include defective Greek verbs, the syntactic attachment of the seventy,
  “received” versus “inherited” the seat, and the range of plural `πίστεις`.
  The request, raw attempt-2 response, and hash-bound review record are retained.
- GPT-6.1 Sol independently confirmed that the supplied Homilies 19.14 ends
  mid-sentence. This is a successful actual model call, not just deployment
  availability. Request and response are under the Homilies' workflow directory.
- A complete 1865 Lagarde edition was located at the Internet Archive.
  Printed p.183 / PDF p.225 includes all of 19.14 and its continuation;
  printed p.199 / PDF p.241 includes Homily 20.23 and the conclusion.
  The [supplement source record](../sources/early_christian_texts/pseudo_clementine_homilies/supplement/lagarde1865-source.json)
  preserves the PDF hash, page mapping, archive metadata, and separate rights
  cautions. The downloaded OCR is noisy and is **not** an approved transcription.

## Full remaining work (do not redefine completion around this checkpoint)

1. Transcribe and separately check the Greek continuation from inside 19.14
   through 20.23, preserving printed lacunae/restorations and edition differences.
   Do not silently splice editions; retain the overlap and selected-source record.
2. Verify and document suspected source errors against print images, starting
   with the Peter-letter issues; preserve the original upstream XML.
3. Generate the remaining English from checked Greek. Run a separate GPT-6.1
   Sol comparison for every passage; revise and re-review failed passages.
   Bind every accepted review to exact Greek and English hashes.
4. Resolve and display the applicable licensing. Imported OGL Greek retains
   CC BY-SA 4.0; do not silently export adaptations under CC BY-only defaults.
5. Add validated reader records, historical metadata and passage navigation;
   replace the source-only gate only with real release evidence, not a flag flip.
6. Pass corpus/export/footnote tests, land finished work on public `main`, run
   the existing publisher and website sync path without duplicating active jobs,
   and verify all four works in the live historical library. Inspect actual
   rendered reader text, source disclosures, license labels and ending coverage.

## Page-image preparation and pilot findings

The 1865 edition contains all four requested works on PDF pages 45–241
(printed pp.3–199). The first three documents are followed by the Homilies;
Homily 19 ends at section 25 and Homily 20 at section 23. The final counts
still require extraction from the checked transcription, not inference alone.

An independent image-derived source is being prepared under
`sources/pseudo_clementines/lagarde1865/`. This keeps the original OGL XML and
its license intact rather than silently correcting or relicensing it. New
Greek transcription does not assert copyright in the ancient wording; original
notes follow the repository license. Scan access/redistribution rights remain
separate, and image pixels are not committed.

The full-page pilot exposed an important failure: GPT-6.1 Sol accepted PDF
page 45 even though its text retained `παρᾷ` where zoomed print shows `ναρκᾷ`.
The draft/review also misread other words on pp.45–46. This acceptance is
**not release evidence**. The exact pilot output is retained, and
`visual_controls.json` plus `pilot-evaluation.json` record the contradiction.

The next evidence series, `pages-zoom`, supplies the full page plus six
overlapping 300dpi PDF-rendered views. Every correction receives a fresh
Sol 6.1 comparison. Acceptance must also satisfy independent visual controls,
source-image hashes, the actual saved model response, and complete line coverage.
Do not scale the entire edition or publish a candidate merely because a model
returns `accept`. Genuinely unreadable ink and print lacunae are distinct.

That zoom pilot also missed a substantive word: `ὁμόφρονοι` was retained where
the print reads `ὁμό|εθνοι`. A separate **blind, focused** Sol 6.1 crop reading
correctly returned the latter. False `checked.json` claims for page 45 were
quarantined as `rejected-model-acceptance.json`; no underlying response was erased.

The current pilot, `pages-blind`, therefore adds an independent Sol 6.1 image
transcription made **without seeing the proposed text**, before adjudicating
differences and doing another image review. Crops are now sized from each PDF
page's actual dimensions: the scanned text pages are 404×635 points, unlike
the first PDF page's letter-size canvas. New acceptance is written only after
all evidence and visual controls pass. A separate deterministic Tesseract
Ancient Greek probe was also tested as a diagnostic; it is not an approved
source or an automatic replacement for image review.

## Actual historical-library integration target

Fresh GitHub `cartha.website` main inspected at
`558ba3dc22ec4ba851846855ff4ae3f53e5acc13` contains a separate historical archive,
not just the Bible reader's extra-canonical list:

- `public/historical-library/catalog.json` and `texts/*.txt` drive it.
- `src/app/(main)/peoples-open-bible/historical-library/HistoricalArchive.jsx`
  verifies the fetched text and displays source/rights information.
- `archiveVisibility.mjs` currently defaults to three LDS works. The four
  requested Christian historical works must not remain accidentally hidden.
- `EditionCard` currently says **“No AI rewriting or translation.”** That must
  become origin-aware; it would be false for these generated translations.
- `archiveStructure.mjs` needs correct Homily/section navigation rather than
  invented verse numbers or undifferentiated pagination.
- Validate with the actual archive tests and live rendered reader, including
  first and final units, no omissions/duplication, source/review disclosures,
  exact download hashes and noncanonical labeling. Keep native/hosted parity.

The old shared-drive checkout has a broken `refs/stash` and could not fetch;
do not repair/delete unrelated state. `cartha.website-ci` fetched the matching
current main successfully and is the verified repository to derive an isolated
website worktree from when implementation is ready. No website files were
changed during this discovery.

## Workflow tooling

`tools/extra_texts/pseudo_clementine_translation.py` prepares requests and checks
responses without accessing secrets or publishing anything. Azure is the
default. Every generated result remains `candidate_only`.

Checks reject changed requests/sources, empty or truncated responses, missing
passages, fabricated Greek quotations, stale English review targets, missing
review criteria and acceptance that contradicts failed checks. Blocking source
issues require separate source evidence; a model cannot certify them away.

Run the focused tests with:

```sh
python3 -m unittest discover -s tests -p 'test_pseudo_clementine*.py'
```

An automated review is not human scholarly approval or a stable-edition claim.
Full publication and source completeness remain unproven until the remaining
requirements above are evidenced and checked.
