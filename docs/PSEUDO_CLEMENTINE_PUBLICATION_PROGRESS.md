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
  A running request is not an accepted review. Do not restart one merely because
  an observation wait expires; inspect its process and eventual response first.
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
