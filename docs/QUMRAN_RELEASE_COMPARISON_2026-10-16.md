# Qumran-Digital release comparison: Ezekiel cohort

## Result and scope

The October 6 release date does **not** supply new primary transcription text
in the six successfully compared entries. All 230 primary rows are byte-identical
to their May 21 versions. The seventh entry, 11Q4, remains **HOLD**, because
repeated word IDs prevent the existing strict index from producing a valid
comparison. It must not be counted as either changed or unchanged.

This is the complete seven-label Ezekiel cohort in our pinned legacy book map,
not all Ezekiel witnesses, quotations, or all Old Testament sources. A release
is an edition state, not another ancient witness. No Hebrew, English, source
priority or recovered manuscript letter changes in this pass.

| Catalogue label | Accepted identical primary rows | Status |
|---|---:|---|
| 1Q9 | 7 | Compared |
| 3Q1 | 3 | Compared |
| 4Q73 | 53 | Compared |
| 4Q74 | 33 | Compared |
| 4Q75 | 3 | Compared |
| Mas1d | 131 | Compared |
| 11Q4 | — | Held: repeated primary word IDs |

The [machine-readable receipt](../sources/textual_restoration/discovery/ezekiel_transcription_release_comparison.2026-10-16.v1.json)
pins input files, catalogue URLs, release metadata, whole-file hashes, ordered
primary-row digests and the failed input diagnostics. Full transcriptions and
images are not copied into Git. Attribution belongs to Qumran-Digital, DFG
project 465277421, continuing Qumran-Wörterbuch; matching project labels do not
establish independent physical objects.

## Whole index versus transcription contents

The [live transcription index](https://lexicon.qumran-digital.org/transcription-index/latest/index.html)
contains 1,173 entries: 866 `dss`, 263 `dss-biblical`, and 44 `non-dss`.
Every listed version is October 6. Replacing the literal date `2026-10-06`
with `2026-05-21` in the acquired index bytes reproduces the historical pinned
index SHA256 exactly. Thus the index's labels, order and classifications have
not changed beyond dates in this comparison. The old raw index file was not
available and is not claimed as freshly read. This hash comparison says nothing
about unexamined transcription contents; the historical receipt remains frozen.

## Masada and the unresolved restoration

Mas1d row `c394328-i394359`, column 1 line 5, still publishes **כ֯שמח[ת]**
at Ezekiel 35:14: uncertain initial kaf and supplied final tav. The primary row
and all other Mas1d primary rows are identical across the two releases. A new
release date therefore cannot upgrade the tav from editorial supply to surviving
ink, or resolve the noun/verb argument in the
[Ezekiel 35 comparison](EZEKIEL_35_VARIANT_EDITIONS_2026-10-16.md).

The earlier bounded publication-access search found no decisive accessible Talmon page
or plate. Keep the two acquisition targets distinct: Talmon's 1997 contribution
in *Tehillah le-Moshe* (especially pp.57*–59* and the restoration key), and the
later *Masada VI* edition (reported pp.59–75 and plate 8). These are acquisition
locators, not a claim to have read those pages or inspected that plate. The
tested official routes and secondary locator did not establish the rationale
for the supplied tav. Repeated blocked downloads are not new textual evidence;
seek an accessible library scan or a different decisive source.

Access references: the [JSTOR book record](https://www.jstor.org/stable/10.5325/j.ctv1bxh2df)
did not expose the required Hebrew chapter; the
[Peeters article route](https://poj.peeters-leuven.be/content.php?url=article&id=583536&journal_code=OLP&download=yes)
offered subscription/purchase and only a preview, not the decisive body. The
[Mas1d archive record](https://www.deadseascrolls.org.il/explore-the-archive/manuscript/Mas%201d-1)
did not supply a target plate. The later-edition plate/page locators came from
[Conroy's bibliography](https://www.cjconroy.net/bib/ezek-text.htm), a secondary
locator, not inspection of the edition. No access restriction was bypassed.

## Why 11Q4 stays held

Both releases repeat eleven stable word IDs across distinct primary rows:
`803932`–`803934` and `200822`–`200829`. Diagnostic DOM enumeration finds 28
primary rows, but that is not an accepted 28-row comparison. The receipt records
both occurrences of every repeated ID and each input's failure.

The displayed cross-labels make the issue concrete: row `c377905-i377915` in
fragment 2 and row `c803932-i803932` in fragment 2a refer to overlapping placements
involving 11Q30 fragment 17 and 11Q4. This is not evidence for eleven additional
independent words or witnesses. It does not itself prove a physical join or
decide the manuscript identity of each piece.

Next resolve occurrence-level placements and edition attribution before using
these IDs for word joins or coverage. Do not silently deduplicate by stable ID,
relax uniqueness to obtain a passing result, or count cross-displayed material
as independent support. The broader OT inventory must retain unresolved cases.

### Follow-up: the repeated displays are now explicitly mapped

Root and a separate reader inspected the six primary cells in both pinned
releases and the official FAQ. The repeats are three identical edited token
blocks displayed under reciprocal fragment references, not alternative-reading
wrappers. This resolves the **display relationship**, not the physical join or
reassignment history between 11Q30 fragment 17 and 11Q4 fragment 2a.

| First display | Repeated display | Shared reference | Repeated token IDs |
|---|---|---|---|
| 11Q4 frg. 2, line 2 | frg. 2a, line 0 | 11Q30 frg. 17, line 0 | 803932–803934 |
| 11Q4 frg. 2, line 3 | frg. 2a, line 1 | 11Q30 frg. 17, line 1 | 200822–200825 |
| 11Q4 frg. 3a, line 0 | frg. 2a, line 2 | 11Q30 frg. 17, line 2 | 200826–200829 |

The FAQ's [alternative-reference explanation](https://lexicon.qumran-digital.org/faq/v1/en/index.html#nebeneintraege)
includes older numbering, composite-text references in either direction and
fragment reassignments. Its [reading-variant explanation](https://lexicon.qumran-digital.org/faq/v1/en/index.html#varianten-im-handschriften-text)
describes another mechanism. A plus sign or repeated ID alone does not select
which physical history applies here. The [sigla](https://lexicon.qumran-digital.org/faq/v1/en/index.html#sigla)
also matter: six repeated spans are gap-boundary notation; the other five
include fragmentary text and unreadable traces. Eleven token IDs are not eleven
preserved manuscript words. The longer reconstructed context and appended
fragment blocks must remain separate representations.

The [explicit specification](../sources/textual_restoration/discovery/11q4_display_alias_specification.2026-10-16.v1.json)
pins both HTML inputs and the consulted FAQ. The [sidecar audit](../sources/textual_restoration/discovery/11q4_display_alias_audit.2026-10-16.v1.json)
records each occurrence by page hash, table, row and token position. It verifies
the exact reviewed references, ordered blocks, stable and DOM IDs, and complete
decoded token subtrees, including nested markup and supplied/uncertain marks.
It scans all primary rows for unapproved duplicates; parallels are excluded.
Row-structure hashes retain context without exporting transcriptions. These
hashes are structural, not raw-byte hashes; attribute order/entity spelling is
not compared by this sidecar. Whole input bytes remain pinned separately.

Both releases reproduce the same three alias pairs and six contextual-row
structures. **The strict index still returns HOLD**, and the accepted whole-page
comparison is still absent. No join validation, independent-witness count,
preserved-letter count, Hebrew replacement or English change follows. The
original receipt and strict comparator are unchanged.

```sh
python -m tools.textual_restoration.audit_display_aliases INPUT.html sources/textual_restoration/discovery/11q4_display_alias_specification.2026-10-16.v1.json
python -m unittest tests.test_display_alias_audit tests.test_transcription_release_comparison tests.test_published_parallel_index
```

The next discriminating source is edition commentary or plate evidence that
explains the reassignment/composite placement, not another duplicate count or
an AI-generated reconstruction. A future occurrence-aware comparison must
validate row-local parallel joins before admitting this page to coverage.

The subsequent [edition-attribution and Ezekiel 4 comparison](EZEKIEL_4_NUMBERS_AND_FRAGMENT_ATTRIBUTION_2026-10-16.md)
locates the earlier DJD possible-quotation note and Puech's revised readings
at p. 229. This advances the bibliographic question without proving the
physical placement. It also documents a directly checked Greek numerical
difference suitable for a separate reader-note candidate.

## Reusable control and verification

Run the comparator against ordinary publicly acquired release files:

```sh
python -m tools.textual_restoration.compare_transcription_releases OLD.html NEW.html
python -m unittest tests.test_transcription_release_comparison tests.test_published_parallel_index
```

It validates manuscript identity, release metadata, primary rows and word joins;
then compares exact primary-row bytes using parser-derived source boundaries.
Editorial alternatives inside primary rows remain included. Displayed parallel
rows are not primary text. An altered style or markup is a review item, not
automatically a reading change. Missing/extra/reordered rows are explicit.
Changed table-level context or external apparatus is outside this row comparison;
unchanged rows cannot certify unchanged scholarship or original wording.

A bounded independent review found a real defect in the initial regex slicer:
a tag-like closing string inside an HTML comment could hide a subsequent text
change. Parser-event boundaries replace that slicer. Regression tests cover
comments, quoted attributes, supplied-letter boundaries, uncertainty marks,
alternatives, Unicode/newlines, ordering, metadata and duplicate-ID rejection.
The first repair test run caught an inherited parser attribute-name collision;
renaming the helper fixed it. All 27 comparison/index tests then passed.
Root reproduced every stored successful result with the corrected implementation
and reproduced the 11Q4 hold in both inputs. These are software/data-boundary
checks, not scholarly votes on the earliest text.

The same reviewer then verified the fix, reproduced all six saved comparison
objects with the corrected code, and confirmed that 11Q4 still fails closed.
Additional Unicode/CRLF/uppercase-tag and raw-hash checks passed in that bounded
review. This repair verification is not an additional independent source vote.

Final local validation reran all 27 tests successfully in 0.016 seconds, parsed
the receipt/workflow, resolved 540 relative file-link targets across the five
changed reports, and passed `git diff --check`. The canonical Ezekiel 35:14
and protected unrelated Genizah file retain their pre-task hashes. CI and
main-branch publication are separate from these local checks.

The next broad use is change triage for evidence already acquired, expanding
coverage by an explicit cohort when it can affect an open source question.
Do not bulk-recount unchanged releases as discoveries or declare the global
source census complete. ImageGen supplies no evidence in this comparison.
