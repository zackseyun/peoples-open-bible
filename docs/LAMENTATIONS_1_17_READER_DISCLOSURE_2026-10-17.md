# Reader disclosure for the alternate Lamentations stanza

## Scope and decision

Readers should be told about the connected 4Q111 alternative without silently
changing POB's Hebrew form. This exact candidate adds one factual variant note
at Lamentations 1:17 and places the existing impurity note at its actual phrase.
The complete Hebrew source object and marker-free English remain unchanged.
The [source comparison](LAMENTATIONS_1_15_18_LINKED_FORM_2026-10-17.md)
leaves historical priority unresolved; this reader change does not reopen it.

The [contract](../sources/textual_restoration/comparisons/lamentations1_17_reader_contract.2026-10-17.v1.json)
fixes the baseline, exact candidate and permitted delta. Actual review,
application and validation belong to the separate
[receipt](../sources/textual_restoration/applications/lamentations1_17_reader.2026-10-17.v1.json).
This report remains a frozen account of the candidate, not a mutable release
certificate or a whole-verse scholarly approval.

## Exact note and anchors

Append note `[b]` to the whole verse, with reason `textual_variant`:

> An ancient Hebrew scroll (4Q111) places this stanza before the weeping stanza of 1:16 and includes an address affirming Yahweh's righteousness. Another righteousness statement is preserved at 1:18, but its rebellion clause is not preserved here. POB provisionally retains the Masoretic order and wording.

The note describes the published Hebrew form. It does not reconstruct its
lost ending, assign a single narrator or call the added address a confession
of personal guilt. It is not a claim that the whole stanza matches POB word
for word. The underlying comparison records the other wording, grammatical
and preservation differences without combining them into a new Hebrew text.

Existing note `[a]` keeps its exact body and reason but moves from “comfort
her” to “an unclean thing.” It explains impurity imagery, not consolation.
The resulting text ends “an unclean thing[a] among them.[b]”. Nothing in the
main English is rewritten or reinterpreted by this anchor correction.

## Evidence and strongest objection

The published transcription's connected junctions establish the alternative
order. Its justice address and ensuing justice opening coexist; the latter's
title completion and causal word are supplied, and the rebellion clause is
unpreserved. Therefore the note cannot say that the first statement simply
replaces verse 18 or that rebellion was removed. The comparison's frozen
packet retains those precise bounds and the distinction between publication
and newly observed ink. It does not claim a new discovery.

The strongest objection is that a short note might make an alternative sound
historically original or a simple reordered copy of the retained text. Naming
one witness, mentioning its added address, disclosing the missing clause and
keeping retention provisional constrain that inference. A complete parallel
edition would be a different application; this note is not one.

## Application controls

Archive the five exact former values for status, revision-pass data,
cross-check data, English with markers and footnotes. Each archive identifies
the immutable baseline commit and file hash without inventing input bindings
for an old review. The candidate is draft/needs-review, with no active old
revision-pass approval. Preserve original generation metadata, all lexical
and theological decisions, earlier history and the existing note body.

The [focused checker](../tests/test_lamentations1_17_reader_application.py)
derives the complete allowed record independently of the contract's proposed
text, validates schema and semantic anchors, and exercises the real full-book
exporter against an immutable Git-archive baseline. All 154 raw record paths
are controlled; only 1:17 may change, and all other 153 exported units and
book metadata must remain identical.

One independent context-aware factual/application review must bind the exact
candidate, contract, report and checker before application. This is not a
blind English preference vote or a repeat-until-agreement loop. Local integrity,
required remote checks, main integration, publisher revision and actual public
reader behavior are separate gates. Existing on-demand provenance supplies
the disclosure route; no external reader or publisher code is changed.
