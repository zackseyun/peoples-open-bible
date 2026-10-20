# Enoch source evidence and safe correction lifecycle

This pipeline supports the complete108-chapter repair objective. It does not
turn an automated test into translation, human-specialist, manuscript or
artwork certification. Schema status remains draft; review scope is explicit.

## Source, not output feedback

Raw Charles1906 OCR stays unchanged. `verse_parser.parse_ocr_chapter` retains
the earlier OCR/cross-file mechanism for diagnostics. Registered complete
chapters instead load exact source transcriptions from **separately stored,
accepted review inputs** through `selected_edition_sources`. The loader never
reads installed canonical verse YAMLs. A failure of registered evidence raises
an error; it does not silently revert to damaged OCR. Unregistered chapters
continue to use the OCR parser and are not thereby certified.

The registry is `sources/enoch/ethiopic/reviewed_source_registry.json`.
Each entry requires a pinned package, exact independent count certificate,
matching count artifact and primary-PDF hash, distinct input-bound reviewer
identities including an independent source reviewer, accepted verdicts, and
the same exact source payload in both inputs and the pinned candidate. The
parser and drafting prompt retain the actual reviewed source PDF pages and
describe the source as a paired-reviewed transcription, not Gemini OCR or
an independent ancient manuscript. Correct source readings therefore do not
have to be distorted to pass a damaged-OCR length comparison.

Individual repaired units can also be registered through the optional `units`
map, inside an already declared printed count. Such an override uses the same
exact paired-reviewed input/candidate checks, never canonical readback. Only
the named unit changes; other OCR rows remain unapproved. An ambiguous raw
address is rejected rather than silently deduplicated. This prevents a repaired
negative or anomalous printed glyph from reverting to OCR before the rest of
its chapter is complete. Source-review editorial controls stay with the Ge'ez
input into drafting prompts; the English running translation is not fed back
as a primary source. Unit registration is not a full-chapter certificate.

## Atomic bounded applications

`bounded_application` checks exact candidate identities, schemas, source and
English/notes equality to accepted inputs, preimage Git blobs/hashes, review
provenance and approval limits. Application rejects any unrelated canonical
change, verifies the actual primary PDF, writes only its scope and records a
receipt. Post-write failures restore originals and remove temporary files.

Wrong addresses require **separately accepted retirement maps**, not implied
permission from acceptance of replacement wording. A retirement identifies
the exact old address/hash, reason and reviewed replacement references. Two
input-bound source assessments must accept that exact map. The transaction
rejects duplicate/overlapping retirements, missing/out-of-scope replacements,
held maps, changed preimages and reappearing wrong-address files. Retired bytes
are retained by existing Git objects, not erased from source history.

## Explicit reviewed supersession

An accepted repair can later need another correction. Historical evidence
must not be rewritten to make the new text appear to have been accepted in
the past. A new package instead declares `supersedes[reference]` with the
old package name, old manifest SHA-256 and old candidate SHA-256. Its own
baseline must equal that old candidate, and its current replacement must
have complete new accepted evidence.

Strict `verify(applied=True)` still rejects any changed installed target.
Historical `verify(evidence_only=True)` checks artifacts but explicitly
reports that current targets were **not** checked; it cannot be combined
with applied/corpus verification. `current_evidence.verify_current` is the
separate current-state check: actual bytes must match the old candidate or
one unique, installed, explicitly reviewed successor, recursively verified.
It rejects arbitrary edits, merely proposed/uninstalled replacements, held
successors, unbound receipts and cycles. Source histories remain unchanged.

These mechanisms are tested with deliberate artifact drift, held verdicts,
wrong hashes, absent replacements, rollback after retirement and attempted
wrong-address resurrection. A complete108-chapter progress report still
cannot claim completion until the independent final requirement audit and
main/public-delivery checks have passed.
