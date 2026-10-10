# OT selected-source redraft safeguard

## Outcome

Ordinary OT drafting now refuses a raw-base redraft when the saved source text
or edition differs, or the record carries critical-source integration. This
prevents the normal drafting path from silently undoing a selected Hebrew source
before spending model tokens. It is a stop gate, not selected-source loading,
textual adjudication, publication approval or general historical preservation.

The gap was detected while applying the
[Isaiah 9:2 qere candidate](ISAIAH_9_2_JOY_SOURCE_COMPARISON_2026-10-10.md).
`tools.draft.load_source_verse` still returns WLC's written negative. The saved
record and reader export select the recorded reading form. Ordinary prompting,
validation and record construction would otherwise use the raw object and
replace the whole record. Existing Isaiah 53:11's critical source has the same
raw-redrafting problem. No upstream XML, source selection or English changes
are part of this safeguard.

## Implemented boundary

`assert_raw_ot_draft_source_safe` checks an existing canonical OT YAML's verse
identity and valid source fields, then compares exact source text and edition
against the incoming ordinary drafting verse. It refuses divergence and any
`critical_source_integration`. It does not infer approval from mutable YAML or
normalize away differences. Missing first drafts and exact base matches retain
the existing drafting behavior. Parse/read failures and malformed records raise
nonretryable validation errors rather than inviting token-spending retries.

The check runs inside `draft_verse` before prompt/model work, in `build_user_prompt`
for CLI dry-run, and again before the ordinary drafting write in case source
selection changed during the model call. The pre-write check is not an atomic
lock. Batch/direct calls into drafting are covered; no batch job was executed.
Raw loading, iterator behavior and morphology remain base-edition operations.
The separate provenance-verified critical-source composition/validation tools
are unchanged; they are not a generic regeneration implementation.

## Independent review and tests

One read-only engineering assessor first mapped the actual loading/prompt paths,
then performed one bounded independent application review of the safeguard.
The verdict is PASS for raw OT redraft refusal only, with no correctness blocker.
Exact reviewed SHA256 values are:

- `tools/draft.py`: a6b89a6e6ffa98fded7156e0da652478ac778043bfdc674d45400afbb8969440
- `tests/test_ot_selected_source_redraft_guard.py`: e34315ccc044800b147855cd0ab4d88440beeeb571b6a1cc900f4b78cd66727c

Root and reviewer separately run the same focused suite; both runs pass all
36 tests. This includes nine new safeguard tests and the existing source-
distinction suite, not 36 new tests. Checks cover the real qere and critical
records without editing them, missing/exact-base controls, text/edition/integration
divergence, malformed IDs/sources/YAML, read errors, direct/retry callers, CLI
dry-run and a source change during a mocked model call. The safeguard test suite
is added to corpus-integrity CI; local success is not remote CI success.

A further safeguard/distinction/WLC run passes all 42 tests. A wider 73-test
exploratory run is not clean: eleven errors occur in the old critical-source/
critical-verse replay tests, and one historical application-preflight test fails.
The critical review still pins older method/doctrine hashes; both already differ
on this branch's parent. The Deuteronomy preflight differs in exporter/schema
hashes and candidate schema errors, while those inputs and its builder are
unchanged from the parent. No archival pin or receipt is rewritten to make a
historical review appear current. Existing composition machinery must therefore
not be described as a currently passing generic selected-source resolver.

## Residual limits and next integration

This guard assumes the ordinary incoming raw verse object. It does not approve
arbitrary programmatically fabricated verse objects or enforce every writer.
Direct low-level `write_verse_yaml` calls are outside its protected entry points.
A matching-source redraft can still replace historical metadata or note-only
restoration work; this is not a general archival-preservation system. Exact
comparison intentionally refuses formatting-only differences and other source
edition labels. NT, deuterocanonical, revision and localization routes are not
newly protected by this OT-only change.

The assessor also identifies a Spanish prompting conflict: its raw canonical
source packet can sit beside a saved selected-source payload. That is a separate
unfixed fidelity issue. Reader export reads canonical YAML and does not redraft
English. Nothing here claims every consumer has been synchronized.

The next integration should resolve an explicitly trusted selection bundle,
binding the full source payload to reviewed candidate/application provenance
and immutable base input. Main prompt, distinction checks, lexical validation,
emitted source and generation provenance must use the same resolved source.
Qere morphology must come from the actual qere record, not the negative ketiv;
unaligned composite morphology must be disclosed as unavailable. Selected-source
redrafts should first be separate candidates, preserving historical canonical
records until separately reviewed application. Do not remove this refusal merely
because a saved record labels itself approved or a model prefers its English.
