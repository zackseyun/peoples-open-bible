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
