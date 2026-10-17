# Reader disclosure for Solomon's temple poem

## Decision and scope

The attested Greek alternative to 1 Kings 8:12–13 deserves a reader note even
though its historical priority remains unresolved. The candidate adds that
disclosure at 8:13 and corrects existing lexical-note anchors in both verses.
The complete Hebrew source objects and marker-free main English stay unchanged.
This is a factual note application, not a recovered Hebrew poem or a claim that
the whole translation is optimal.

The [source comparison](KINGS_8_TEMPLE_POEM_COMPARISON_2026-10-17.md) and its
[frozen evidence packet](../sources/textual_restoration/comparisons/kings8_temple_poem.2026-10-17.v1.json)
remain the historical no-application snapshot. This later application supersedes
only that snapshot's reader-note status if approved and applied; it does not
silently update its canonical pins or claim new source evidence. The
[application contract](../sources/textual_restoration/comparisons/kings8_reader_contract.2026-10-17.v1.json)
pins baseline commit `6a2cc87cc5085eab28b341999a11d17004db842e`, complete
candidates, allowed changes, review criteria and unchanged inputs.

## Exact reader changes

- At 8:12, move `[a]` from “said” to “thick darkness.” Its existing dark-cloud
  alternative belongs to that expression, not the speech verb.
- At 8:13, retain `[a]` after “exalted house” and move `[b]` to the end of
  “a settled place for you to dwell.” The fixed-place alternative belongs to
  the second phrase, not “house.” Both existing note bodies and reasons remain.
- Add `[c]` at the end of the poem, with reason `textual_variant`:

> Swete's Greek edition reports no 8:12–13 here for Vaticanus but a longer poem
> after 8:53, mentioning the sun and a command to build a house. Alexandrinus
> has a short form here and variants in the later poem. POB provisionally
> retains the shorter Hebrew form; the longer form's priority and any
> reconstructed Hebrew wording remain uncertain.

This note identifies a consequential difference without calling every Greek
witness identical. It attributes the evidence to the consulted edition rather
than implying new inspection of either codex. It does not assign the building
command's addressee, make the sun a speaking subject, or print an eclectic
Hebrew reconstruction. The final qualification distinguishes attestation from
priority and avoids implying that provisional retention proves Hebrew earlier.

## Evidence sufficient for the note

Swete I, printed 692 and 695 / PDF 724 and 727, reports the early Vaticanus
junction without the short poem, the early Alexandrinus insertion, and the
later longer poem with positive Alexandrinus local variants. The same edition's
key and collation conventions were checked in the source comparison. The note
does not reconstruct Alexandrinus's complete later wording from apparatus
silence. Its broad sun/building description does not require adopting the
disputed Hebrew retroversions in Pakkala or Richelle.

The strongest objection is that a compact note cannot explain the whole
literary history and may sound as though the two forms were uniform. Naming
the two codices and Alexandrinus's participation at both locations prevents
the main overstatement; exact reconstruction and priority remain open. A
longer scholarly apparatus belongs in the linked comparison, not in a newly
combined main text. No new manuscript transcription, lexicon consultation or
canonical addition is claimed. Existing lexical and theological rationales,
including their historical lexicon labels, are unchanged and not newly approved.

## Bounded new access checks

The broader Antiochene collation and modern Latin edition are still needed
before stronger source judgments. The new routes did not yield their target
pages; they are not counted as consulted textual evidence.

The [CSIC publisher record](https://editorial.csic.es/publicaciones/libros/3984/978-84-00-07255-1/el-texto-antioqueno-de-la-biblia-griega-tomo-ii-li.html)
identifies the 1992 second volume of *El texto antioqueno de la Biblia griega*
as out of print, without a PDF, ebook or sample link. The delegated check also
searched Digital CSIC and tried the Google Books record, without obtaining
the actual 1 Kings 8 apparatus or its conventions. No complete recensional
distribution follows from catalogue metadata.

For Moreno Hernández's thesis, [Dialnet](https://dialnet.unirioja.es/servlet/tesis?codigo=16321)
led to the UCM eprints record, which timed out. Docta's public title search
and the alternate official PDF route also failed to provide bytes. The
[UNED record](https://portalcientifico.uned.es/documentos/5d1df60a29995204f765f82c)
imports Dialnet metadata and points to the same eprints record; it is not an
independent textual source or an alternative copy. Printed 137–138 and the
thesis conventions remain unread. No account, access bypass, terms acceptance,
purchase or external request was used. Stop these exhausted routes rather
than repeating them as progress.

## Application and validation boundary

Both complete candidates archive the exact old status, revision-pass data,
cross-check data, English-with-markers and notes, with their immutable baseline
commit and file hash. The archive explicitly does not verify the original
reviews' input bindings or certify the candidate. Active status becomes
`draft`, cross-check becomes `needs_review`, and the inherited revision-pass
approval is removed. Original AI-draft provenance is preserved.

The [focused tests](../tests/test_kings8_reader_application.py) compare full
records against an explicit allowed delta, validate schema and note anchors,
and exercise the real full-book exporter. An immutable Git-archive digest
replaces an unnecessary list of 817 file pins. The preflight checks both
targets together and compares all other exported units and book metadata.
Separate live-record checks distinguish baseline from exact candidate bytes
and reject partial application. This does not test a deployed reader.

An independent reviewer must assess this exact candidate and contract before
canonical application. The prior source-comparison pass does not approve this
new note automatically. No blinded stylistic vote is claimed, and review is
not repeated merely to obtain agreement. The
[application receipt](../sources/textual_restoration/applications/kings8_reader.2026-10-17.v1.json)
will record actual review bindings and pre/post-application checks, separate
from publication CI and deployment.

## What would change the source decision

Actual broader Greek target readings and conventions, modern Latin target
pages or manuscript context, and a transmission argument discriminating the
alternatives could reopen priority. Neither another reading of these same
articles nor more model agreement supplies missing Hebrew letters. The cited
Song book remains an ancient source citation, not a recovered work or a reason
to add a text to the canon. This note is a useful bounded contribution, not
completion of the wider OT source-comparison project.

## Applied result

One independent context-aware review passed the exact frozen contract,
candidates and the preceding report text. It reproduced all four focused tests
in 202.432 seconds and verified that canonical files remained baseline during
review. Root then applied the exact reviewed candidate bytes. The preceding
proposal and evidence sections are retained unchanged so their review-input
hash remains reproducible; this status section was added after that review.

Root's preflight passed four focused tests and 24 existing note/export tests.
Post-application, the four focused tests passed again in 199.754 seconds.
The live full-book export exactly matches the candidate digest: 22 chapters,
817 units, changed IDs only 8:12 and 8:13. The other 815 canonical book files,
exported units and book metadata are unchanged, as are the seven pinned inputs
and the protected unrelated local file. Schema, five exact archives per record,
source, marker-free English, original AI provenance and anchors pass. No
whole-corpus local rerun or deployed-reader verification is claimed.

The receipt records these results and their hashes. The two active records
remain draft/needs_review, without transferred historical approvals. The CI
workflow adds only the exact baseline fetch and the four focused tests; all
existing checks remain. Commit, required CI, merge and deployment are separate
publication stages, not evidence that Hebrew priority has been settled.
