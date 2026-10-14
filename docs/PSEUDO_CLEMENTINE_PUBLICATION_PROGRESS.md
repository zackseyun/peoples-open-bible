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

The blind pilot completed pp.45–46, passed the stored-response and independent
visual-control checks, and then received focused crop adjudications for two
remaining glyph readings in Peter's letter: `ἐνέγκωσιν` and `γίνηται`.
Corrections are separately recorded, not silently written over either model's
response. A complete three-section selected Greek source is now assembled at
`sources/pseudo_clementines/lagarde1865/selected/pseudo_clementine_peter_to_james.json`.
The assembler preserves the closing farewell, excludes the following Contestation,
and documents dehyphenation, whitespace and pagination-bar normalization.

The `lagarde-v2` English was separately reviewed by Sol 6.1, which requested
connective-word repairs and fuller uncertainty disclosures. The visibly printed
repetition `ἐφοδιάζειν ἐφοδιάζωσιν` was retained and distinguished from an OCR
error. Earlier candidates remain historical evidence and must not be exported.

The subsequent **`lagarde-v3` English revision passed Sol 6.1 review for all
three Peter-letter sections**. It restores connective words and carries the
required lexical/attachment alternatives. The review expressly accepts the
disclosed uncertainties, not a claim that their interpretation is settled.
`reviewed-english-candidate.json` binds the source, final English and review
hashes; `reader_candidate/pseudo-clementine-peter-to-james.txt` preserves the
accepted English plus mandatory notes. This is ready for archive integration,
not a claim of live publication. Other three works remain incomplete.

The next source batch covers PDF pp.47–54 and 225–241 using the blind protocol,
two workers, and bounded revision attempts. Page-level `needs_manual_source_read`
or `review_limit_reached` outcomes require actual follow-up rather than approval.
The entire edition and all four English works are still incomplete.

Follow-ups identified so far: p.47 has an obscured initial letter in the scan;
an alternate publicly accessible 1865 copy is being inspected. P.50 passed a
fourth image check after its third-pass correction. P.53 reached the initial
review limit. P.227 produced a truncated model response; retain it and retry
only that terminal request with an adequate bounded output budget, not by
restarting the live batch. The current batch remains a real running process;
check its handle before taking further action.

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

## Organized reader and remaining-work checkpoint

- The website staging branch now contains the accepted Peter letter, a source-bound
  proof verifier, a full work introduction, editorial section titles and numbered
  display paragraphs. Tests reconstruct the approved English exactly once, with
  all wording and uncertainty notes preserved. The numbers are explicitly modern
  navigation aids, not ancient verses. Browser verification is local, not live
  publication. Website checkpoint: fd96a0c5.
- The complete selected print source is now assembled for the Contestation (5
  sections) and Clement's letter (20 sections), including Clement's undotted
  printed section 11. The page-47 reading is tied to the separately verified
  alternate scan. Actual Azure English generation and independent Sol 6.1 review
  batches are running; no acceptance/publication is implied by starting them.
- The Homilies assembler now preserves homily/section hierarchy, page
  continuations, printed gaps and exact normalized word coverage. It requires all
  checked pages, twenty sequential homilies, and the verified final 20.23 ending.
  It cannot produce a complete source while any required page is unaccepted.
- An exact-request diagnostic retry of a previously terminal page-56 CLI failure
  identified a connection error. The transport now records only allowlisted error
  categories (not raw CLI output), and bounds retries of observed terminal network
  failures. Authorization and content-filter failures still stop. Original
  failure and diagnostic receipts remain intact.
- Scope remains all four works. Other works, complete Homilies evidence, final
  production build, main integration and authorized live deployment are pending.
  No goal-completion or public-availability claim is made.

## Post-restart source recovery and substantive review findings

The host restarted and cleared the temporary directory. Both registered PDFs
were re-downloaded from Internet Archive's official mirrors and matched their
original SHA-256 hashes. Source images, request caches and logs now use the
ignored persistent .cache/pseudo-clementine directory. Only stopped jobs were
resumed; successful receipt files were reused.

- Primary PDF page 64 / printed page 22 now has a separately accepted review
  against alternate-copy PDF page 58. Its obscured line reads ἡμῖν. The selected
  page map points to this supplemented evidence, with both scan identities.
- Page 68's exact diagnostic request succeeded after its earlier terminal CLI
  failure. The ordinary complete source review subsequently accepted that page.
- Contestation English sections 1–5 completed the bounded v0–v2 workflow but did
  NOT pass overall. Section 3's opening remains syntactically unresolved.
  A separate targeted Sol 6.1 investigation tested contextual ellipsis and
  genitive/postposition analyses without changing the Greek; it returned no
  defensible complete reading. This is a meaning block, not a demonstrated OCR
  error. Do not erase it, force acceptance, or present the investigation as
  scholarly sign-off. Exact additional evidence requested is preserved in
  syntax-investigation.response.json under that work's batch-001 workflow.
- Historical English consultation:
  https://www.ecatholic2000.com/fathers/untitled-371.shtml
  This supports only a comparison of a prior translator's interpretation, not
  the grammar of the selected Greek. No older English wording was adopted into
  the generated draft as a shortcut.
- Clement's first five sections also reached editorial-attention status after
  bounded revisions. Its remaining batches and the Homilies source job continue.
- The website staging code now handles the separate 5-section Contestation and
  20-section Clement inventories. Neither is made visible before acceptance.

## Review-standard alignment

DOCTRINE.md explicitly permits a defensible main rendering with material
alternatives preserved in notes; it does not require a uniquely settled
interpretation. The earlier prompt's example `blocks_publication: true` and its
undifferentiated treatment of source/meaning questions sometimes caused ordinary
disclosed ambiguity to become an automatic hold. The prompt now distinguishes
that from an unreadable source, missing meaning, invented restoration, or a
rendering that is not defensible from the Greek. Those actual defects still block.

No acceptance flag in an existing record was changed. Held Clement passages are
being freshly generated/revised and independently reviewed under the explicit
existing policy. All uncertainty notes and lexical rationales must survive reader
export. A proposed alternative is still not an approval, and no model response is
treated as human scholarly sign-off. The specialist-review packet remains useful
where no defensible rendering can be established.

Preparation and ingestion now use one shared print-source variant loader, with
tests for both Homily 1 and Homily 2 and rejection of unknown variants. Homily 2
cannot be prepared until every required page has accepted evidence. These partial
source variants remain incomplete-work drafting inputs; complete-work source and
review coverage are still mandatory for export and publication.

## Completion resumed in the owning chat (2026-10-13)

The current owner is chat `01a137cb-59aa-7583-bcbd-c19c83155be5`; a brief
coordination handoff has ended. The objective still includes **all four works**,
complete reviewed English, correctly organized historical reader entries,
verified main integration, and authorized live publication. The three
introductory works alone are not completion.

- All three introductory works have complete source-bound accepted reviews:
  Peter (3 sections), Contestation (5), and Clement (20). Their local archive
  integration has full metadata, editorial titles, explicitly modern paragraph
  references, separate notes, honest model-review disclosures and provenance.
- Fresh generation plus independent Sol 6.1 comparison resolved the held
  editorial findings at Homilies 1.17, 2.38 and 2.44. Earlier adverse responses
  remain unchanged. Per-homily source-bound selection snapshots now cover all
  sections of Homilies 1, 2 and 7, but are explicitly **not whole-work release**.
- The selected-edition coverage scope is now explicit: all surviving Greek and
  every printed lacuna must be represented. A verified printed gap is not an
  omitted supplied clause or a recovered lost sentence. Its exact dot count and
  source-quoted explanatory note must survive the English; lost wording must
  never be invented or an unbroken original claimed. Missing scan pages,
  unverified ink, unsupported completions and omitted surviving words still
  block. This clarification does not change DOCTRINE.md or clear any existing
  verdict by hand. Fresh drafts and independent reviews of 2.6 and 7.7 accepted
  their faithful surviving wording **with their gaps and uncertainty notes**.
- Python ingestion and the website proof verifier now deterministically reject
  filled, shortened, removed or undisclosed printed gaps. The source tests also
  distinguish an actual provider `content_filter` rejection from truncation;
  no filtered result is ingested or automatically retried/substituted.
- Alternate-copy and focused-crop evidence resolved source pages 105, 148, 156
  and 177. Page156's final accent is supported by a separate blind900dpi reading
  of both scans and a fresh complete-page comparison. The missing section11
  delimiter in Homily17 was an earlier transcription omission, not a reason to
  loosen the parser: the printed period on PDF206 / printed164 is independently
  confirmed by a900dpi crop, retained in a scoped adjudication, and protected by
  a regression test. Homily17 now retains20 sequential source sections.
- Source checking currently validates196/197 required pages; PDF239 remains in
  a bounded new comparison with a visually verified second copy. Exact-request
  diagnostic recoveries resolved old terminal transport failures at239/240
  without changing endpoint, model, permissions or prompts. Page240 passed its
  ordinary independent image comparison. Re-run the audit before quoting counts.
- Translation runs continue in two nonduplicated queues: 7/8/9/12/16 and
  3/4/5/10/11/13/14/15/17/18. Terminal findings remain real follow-up work. The
  whole-work source/acceptance/export gates still prohibit partial publication.
  `pseudo_clementine_consolidate.py` validates actual current-source review
  bundles, avoids older favorable identical wording after a later adverse
  review, and re-runs the original acceptance collector. Its default output is
  partial; `--complete` requires every source section.
- Actual Azure content-filter rejections affect Homily6 sections1-5 and a later
  Homily8 batch. They were not truncation and were not bypassed. A question about
  an authorized alternative translation/human route remains unanswered; no
  Codex subagents or alternate provider were used.
- The focused source/workflow suite passes62 tests and the focused website
  archive/reader suite passes33 tests; the archive validator verifies11 current
  local editions without changing the canon. Production static-build validation
  is running after hydrating missing tracked inputs in the sparse worktree;
  earlier missing-input failures were not represented as a passing build.
- Zack explicitly approved **deploy web after all four works pass all checks**
  in the coordination chat; that does not authorize deploying the three-work
  subset or unchecked Homilies. Nothing has been manually deployed, and neither
  working branch has yet been merged to main for this unfinished goal.

Current process journals and stdout logs are under the ignored persistent
`.cache/pseudo-clementine/` directory. Inspect live process handles and their
specific journals before resuming anything; a quiet call or observation timeout
is not a terminal failure. Source PDFs, crops and base64 request caches stay
local and must not enter Git. Review requests/responses and hash-bound evidence
are retained for the eventual pinned export.
