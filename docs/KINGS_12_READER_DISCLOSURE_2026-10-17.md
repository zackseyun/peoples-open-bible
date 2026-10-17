# Reader disclosure for Jeroboam at Shechem

## Decision and scope

The [source comparison](KINGS_12_JEROBOAM_NARRATIVE_COMPARISON_2026-10-17.md)
establishes a meaningful alternative without settling historical priority.
The candidate adds a factual note at 1 Kings 12:3, explaining why the named
participation in the current Hebrew is not uniform across Greek forms.
Hebrew, marker-free main English, existing note bodies and original AI-draft
provenance remain unchanged. No reconstructed Hebrew or expanded canon is
approved. This is a separate reader application, not a replacement of the
frozen source dossier or its review.

The [contract](../sources/textual_restoration/comparisons/kings12_reader_contract.2026-10-17.v1.json)
binds baseline commit `6bec58a26e31d30f1b7a4a8a530c2c3fee398058`, the complete
candidate, source evidence, allowed delta and review criteria. Its source
snapshot remains historically no-application; later application status must
not be retroactively attributed to that source review.

## Exact note and anchors

The candidate ends the narrative clause with `[c]` after “Rehoboam,” before
“saying.” This attaches the new note to the whole participation clause.
Existing `[a]` stays after “him.” Existing `[b]` moves from “saying” to
“assembly,” the word its unchanged note actually explains. No neighboring
verse or unrelated note is edited.

> Brooke, McLean and Thackeray’s Greek edition, based on Vaticanus, does not
> name Jeroboam as participating here or in verse 12; his return from Egypt
> appears at 11:43. That text also includes a different account after 12:24,
> with varying wording and extent among Greek witnesses. POB follows the
> Hebrew here; the earliest narrative form remains uncertain.

The reason is `textual_variant`. Attribution to the inspected edition avoids
claiming new codex-image transcription or uniform Greek wording. “Not named
as participating” does not mean that Jeroboam cannot have been present, and
does not erase the Ahijah/Jeroboam reference at regular 12:15. The alternative
story is not appended to the main translation or translated from a synthetic
Hebrew reconstruction.

The strongest objection is compression: readers may infer a single Greek
edition history or assume shorter means earlier. Naming the edition, explicitly
stating manuscript variation and retaining uncertainty prevents that inference
without filling the reader note with a scholarly apparatus. Exact witness
profiles remain in the linked source comparison. The modern article discussed
below was not a drafting source for this note or the unchanged main English.

## Modern argument now accessible

Darshan’s complete author-uploaded reader text is now consulted at its
pre-pagination 1–23, including notes and bibliography, through the
[public author page](https://www.academia.edu/114635645/The_Story_of_Adoram_the_Taskmaster_over_the_Forced_Labor_and_the_Traditions_Regarding_the_Kingdoms_Division).
The published PDF remains unacquired; flattened tables are not a verified
collation. His Hebrew alternative-story column is explicitly reconstruction.
He proposes shared sources and independently developed branches, with
12:18a+19 an originally separate Adoram report. His broader source model is
partly deferred to a future study.

The argument does not compel deletion: the Hebrew names Adoram’s office,
not this mission’s explicit purpose; sending him does not prove the king was
far away. The already-read Greek apparatus also preserves an Adoram addition
inside an expanded-story witness. These qualifications leave Hebrew priority
HOLD and the proposed note accurate. No commercial English Bible quotations
embedded in the article are reused as drafting inputs.

New Joosten author/institution searches yielded no chapter; the ordinary
Peeters preview route returned 404. The 2020 chapter remains unread, not an
authority silently substituted by snippets. The earlier frozen access status
is preserved as history; only the present Darshan consultation supersedes
its abstract-only status.

## Application gate and reproducible validation

The complete candidate archives five exact old values: status, revision-pass
data, cross-check data, English with markers, and notes. The archive binds
the immutable baseline and file hash; it does not verify the original reviews’
input hashes. Active status becomes draft, cross-check becomes needs_review,
and the inherited revision-pass approval is removed. Existing lexical
rationales and their historical lexicon labels are preserved, not newly approved.

The [read-only checker](../sources/textual_restoration/applications/kings12_reader_checks.2026-10-17.py)
validates schema, exact full-record delta, all archives, source/provenance
preservation, anchors and all other 816 book records against the pinned Git
archive. Its full mode uses the actual exporter with baseline/candidate loader
overlays and verifies that only 12:3 changes, with note body and reason intact.
Applied mode additionally checks the live canonical loader. Structural-only
mode explicitly does not certify the export. No full-book output file is
generated, and no runtime exporter or CI workflow is modified.

Run from the repository root:

```sh
.venv/bin/python sources/textual_restoration/applications/kings12_reader_checks.2026-10-17.py preflight
.venv/bin/python sources/textual_restoration/applications/kings12_reader_checks.2026-10-17.py applied
```

Independent review must approve the frozen note, complete candidate, contract
and evidence before application. This is a bounded factual review, not a blind
stylistic contest, whole-verse certification or a repeated vote on source
priority. The separate
[receipt](../sources/textual_restoration/applications/kings12_reader.2026-10-17.v1.json)
will bind actual preflight, review and application results. Schema acceptance,
local export, required publication CI, merge and deployed-reader behavior
remain separate claims.

## Applied result

One independent context-aware factual review passed the exact frozen report,
contract, complete candidate and checker hashes recorded in the receipt. The
reviewer reproduced the structural-only preflight, six private source pins,
all 142 composite reader lines and 108 matching overlap lines. It reused its
preceding complete Greek source/key review and checked selected modern-article
paragraphs, not that whole article. It did not duplicate the full export,
certify source priority or review this subsequently added status section.

Root applied the exact reviewed candidate bytes. Both full preflight and
post-application checks pass: 22 chapters, 817 exported units, changed ID only
12:3, with the other 816 records, exported units and metadata unchanged.
The applied canonical loader and target export match the reviewed candidate;
the candidate book-export digest is
`ea5569ce0098ee0699b54e17c95f7cfb9290836ec0a7cd6768c0769191b0af1f`.
Schema, exact five archives, source, marker-free English, provenance, anchors
and protected unrelated work pass. The 24 targeted existing audit/export
tests also pass. No whole-corpus local rerun or deployed-reader verification
is claimed. The active record remains draft/needs_review; commit, required
CI and merge are still separate publication stages.
