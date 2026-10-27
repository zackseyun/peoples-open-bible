# Enoch review serialization preflight
Run this **before an author freezes an integration-ready input**, and again after writing a review receipt. It checks serialization only, never source/English correctness or publication approval.

```sh
python3 -m tools.enoch.review_input_preflight /absolute/path/review-input.json
python3 -m tools.enoch.review_input_preflight /absolute/path/review-input.json --review /absolute/path/author-review.json --provenance /absolute/path/provenance.json
```

- Preserve exact input bytes, source fidels, English, complete explanation, and actual exposure/failed-reading history. Do not normalize source letters to dictionary heads or familiar wording.
- Use canonical `translation.philosophy`, footnote `marker` (not `id`), and a supported reason enum. Low confidence needs an honest accepted selected-critical-scope explanation. Never invent an unknown fidel or increase confidence to pass a check. True unresolved fidels/meaning remain whole holds; a note is not approval.
- Receipts must contain one explicit `reviews` list of `{reference, verdict, rationale}` rows; verdict is `accept`, `hold`, `revise`, or `reject`. A direct `APPROVE` field is not silently converted by the transaction. If serialization needs adaptation, preserve the raw receipt and emit a separately hash-bound, same-actor wrapper with zero additional language passes/photos/provider calls.
- Flat provenance: `reviewer_id`, `role`, `input_sha256`, `review_sha256`, `source_pdf_sha256`, and `scan_image_sha256` mapping actual photo paths to hashes. Identity/role must agree with the review. Do not invent photo views or human/MSS/provider certification.
- A well-formed HOLD remains HOLD. Passing this preflight does not inspect photographic content, certify language, replace distinct whole-verse review, or relax the existing bounded transaction/current-evidence gates.
- Broad Azure character collations can omit/misread even unflagged words. Target diagnostics may supply useful leads, but actual full native source/Table-I/Latin/grammar controls must resolve them. API success, agreeing models, or consistent codepoints do not prove the reading.

Batch32 additionally rejects blank source and blank English, including medium-confidence/no-anchor inputs. This is an integration-readiness boundary, not language approval; a valid adverse/HOLD receipt can still serialize independently.
