# Verified selected Hebrew drafting

## Outcome

Isaiah 9:2 can now be drafted as a separate, unapproved candidate from its
explicitly selected Hebrew reading, with matching morphology and fresh source
provenance. Ordinary raw-base redrafting still refuses to replace that selected
record. No canonical source, English, historical generation record or upstream
XML changes in this integration. This repairs source loading; it does not certify
a generated translation or finish the wider OT source-comparison program.

The [Isaiah comparison and application](ISAIAH_9_2_JOY_SOURCE_COMPARISON_2026-10-10.md)
provisionally selects the recorded Masoretic qere, “to it,” for increased joy,
retaining written-negative counterevidence and unresolved earliest wording.
The earlier [redraft safeguard](OT_SELECTED_SOURCE_REDRAFT_GUARD_2026-10-10.md)
stops an unsafe raw-base overwrite. The new explicit route lets further English
comparison proceed against that selection without erasing the saved history.

## Source resolution and trust

The [selection index](../sources/textual_restoration/selections/drafting_sources.2026-10-10.v1.json)
has one registered entry, ISA.9.2. Its exact digest is pinned in the resolver's
code. Candidate, application receipt, verse schema and WLC XML have their own
pins inside that bound index. A file cannot acquire authority by changing its
own approval label or updating self-declared hashes. Adding or changing an entry
requires an explicit code-pin update and independent review of the new inputs.
These hashes establish input identity, not historical truth.

The resolver freshly parses the pinned XML and verifies the incoming raw verse,
including words, morphology, annotations and punctuation. It copies that object
and replaces only written token23qch, לא, with the actual adjacent reading
token23VmY, ל֖/וֹ. The replacement has the qere's own lemma `l` and morphology
`HR/Sp3ms`, not the written negative's analysis. Its complete source payload,
including apparatus and provisional disclosure, matches the reviewed candidate
and the saved canonical source. Other words and punctuation remain unchanged.
No normalization, generated letters or mutation of the parser's raw object is
used. Unsupported selections are not silently adopted from arbitrary YAML.

The full canonical source must match, but a later English change is allowed
before invocation. The actual canonical file digest is recorded with source,
candidate, receipt, schema and index pins in fresh generation provenance. A
second resolution after generation detects changed inputs before returning a
successful candidate. This is not an atomic filesystem transaction.

## Candidate generation and review boundary

`draft_selected_source_candidate` uses the resolved verse for main source text,
morphology, lexical validation and distinction binding. It emits the complete
selected source and fresh `ai_draft.selected_source_at_draft` provenance, not the
old generation approval. Selected mode forbids canonical writes. A candidate is
generated in memory; CLI selected mode prints it to stdout. Existing distinction
proposal handling may write noncanonical pending-review state before the final
resolver recheck. That state is not an applied verse or a publication approval.

The prompt labels the selected Masoretic reading honestly and asks for material
alternatives to remain disclosed. Neighboring raw text is explicitly base-edition
context, not a synchronized selection. The raw `draft_verse` route remains guarded;
selected drafting is a separate explicit opt-in, not a bypass flag on that route.

An independent judge exposes a real limit: an adversarial mocked model response
with negative English and no footnotes still returns a schema-valid `draft`
candidate. The selected source, apparatus and provisional provenance remain, and
canonical bytes are unchanged. Source coherence and a current structural
distinction receipt therefore do not prove source-to-English meaning or reader
disclosure. Every such candidate still needs separate translation and application
review. Do not present a model-generated candidate as a validated improvement.

## Verification

The [independent review record](../sources/textual_restoration/reviews/selected_source_drafting.2026-10-10.v1.json)
pins the actual implementation, index and tests. Its verdict is PASS for source
resolution and candidate-only generation, not translation quality or publication.
The implementer runs thirteen resolver tests; root's final combined run passes
64 tests, including twenty-two new resolver/integration tests plus existing
raw-guard, distinction and WLC tests. The independent judge separately passes
twenty-two new tests and a 58-test combined subset. These are overlapping runs,
not additional independent manuscript witnesses or corpus-quality measurements.

Tests cover real qere text/morphology, immutable inputs, unknown selections,
missing/tampered files, forged self-declared approval/pins, canonical source and
identity drift, later English, incoming morphology/punctuation, symlinks and
fresh verification after earlier success. Integration checks main prompt,
validation/binding source, emitted payload, provenance, CLI dry-run/stdout,
pre-model refusal and post-model drift. Model responses are fixtures; no live
inference or newly improved English is claimed by these tests.

The real script-style selected dry-run succeeds without calling a model. The
actual full Isaiah reader export remains identical to the prior application:
66 chapters, 1,291 entries, SHA256
05a5db9a7cfc7bf3c84ebf4fe666571b39b63557c35b20f796a5632205a0a388.
The new resolver/integration suites are wired into corpus CI; remote CI and
deployed-reader verification remain separate from these local checks.

## Usage and remaining work

Inspect the verified prompt without inference:

```bash
.venv/bin/python tools/draft.py --ref 'Isaiah 9:2' --selected-source-candidate --dry-run
```

The same selected flag without dry-run invokes the configured model and prints
an unapproved YAML candidate only. Review and save it separately before any
application. The Python API has no canonical-write option.

One qere entry is currently supported. Earlier critical composites such as
Isaiah 53:11 remain refused here; their historical review pins need a new
versioned evaluation, not silent repinning. General composite loading, direct
low-level writers, archival preservation for matching-source redrafts and the
Spanish raw/selected prompt conflict remain unfinished. NT, deuterocanonical
and localization routes are not covered by this OT integration. Further entries
must retain the same source, morphology, provenance, candidate-review and reader-
disclosure boundaries. The scientific next step remains evidence-led comparison,
not speculative image generation or repeated preference voting.
