# Samaritan digital source editorial audit

The pinned DT-UCPH Samaritan Pentateuch is useful for broad Hebrew comparison,
but its digital readings and linguistic analyses must not be presented as an
independently verified, unaltered manuscript transcription. This audit checks
every entry in its textual issue file against the current reference controls
and existing discovery leads. It changes source documentation, not biblical
wording or the historical preference between readings.

## Annotation inventory and affected layer

The [pinned issue file](https://raw.githubusercontent.com/DT-UCPH/sp/2f2120286ac48d4ff3d04e0107e33efd864aa9e1/textual_issues/issues.json)
contains 29 annotations at 27 distinct book/chapter/verse sections. Thirteen
carry data-version label 4.1 and sixteen carry label 6.3. Fourteen explanations
report harmonization to MT and two to the core Samaritan tradition; the other
thirteen concern reading or linguistic analysis. These are annotation counts,
not verified numbers of changes to the raw signs.

The [source README](https://raw.githubusercontent.com/DT-UCPH/sp/2f2120286ac48d4ff3d04e0107e33efd864aa9e1/README.md)
identifies Dublin Chester Beatty Library 751 and Garizim 1 as manuscript bases,
describes changed verse grouping at Genesis 30:36, and directs readers to its
issue annotations. The retained private inputs contain the seven sign/section
features used by the existing screen, the README and issue file—not the
linguistic features or revision history needed to locate the affected layer.
Whether a reported harmonization changed current `sign.tf`, linguistic
analysis, or both remains unresolved. The annotations cannot reconstruct the
unedited manuscript spelling. No new manuscript pixels or critical apparatus
are supplied by this audit.

Each historical node number is retained with its annotation version. Mapping
uses only the declared section. An independent diagnostic found that all 29
numbers currently land on word nodes in those sections; that coincidence does
not establish stable token identity across versions. It is not used as a
token remapping or a restored-letter claim.

## What the intersections establish

The metadata audit reproduces the entire frozen screen from all pinned inputs:
5,841 Samaritan verse nodes and 5,853 WLC written verses. All 27 annotated
sections are whole-verse consonantally different from WLC. A difference can
coexist with a local correction; it cannot identify the corrected feature or
prove that the raw signs were untouched.

| Existing reference pool | Distinct labels | Annotated sections found |
|---|---:|---:|
| Large length-difference targets | 20 | 0 |
| Numbering or repetition targets | 15 | 0 |
| Their exact WLC reference alternatives | 46 | 0 |
| Parallel-discovery targets | 20 | 0 |
| Parallel-discovery Samaritan alternatives | 124 | 0 |
| Parallel-discovery WLC alternatives | 92 | 0 |

These are separate, overlapping navigation pools, not additive witness counts.
None of these existing leads is flagged by this annotation inventory. That
does not certify that their readings are diplomatic, that the issue list is
complete, or that a parallel is historically independent. The frozen screens
are preserved without changing their counts, extraction rules or conclusions.

## Effect on the comparison method

The central registry now describes version-local interpretive/harmonization
annotations and their unverified affected layer. For consequential units, keep
three things separate: raw digital signs, linguistic analyses, and published
manuscript/apparatus readings. An English or Hebrew change needs the evidence
for its own unit, not a global source-quality label. No annotation should be
silently reversed to manufacture a supposed manuscript reading.

The next useful source task is to identify the affected feature and manuscript
reading for an explicitly flagged unit, such as Exodus 19:24, which has both
an interpretation annotation and a later harmonization annotation. This is a
discriminating access/feature check, not an invitation to rerun the same
source-preference vote. Separately, breadth discovery must include small and
equal-consonant units; the twenty largest deltas are not a semantic census.

## Reproducible metadata and validation boundary

The [audit receipt](../sources/textual_restoration/discovery/samaritan_editorial_audit.2026-10-10.v1.json)
preserves annotation/version/node locators, section-level current text hashes,
input pins and reference intersections. It exports no Hebrew source corpus
or full annotation explanations. Højgaard, Naaijer and Schorch's dataset
attribution and CC BY-NC 4.0 terms remain attached to the private input; no
rights or relicensing change is implied.

```bash
.venv/bin/python -m tools.textual_restoration.audit_samaritan_editorial_issues /path/to/sp/tf/7.1.3 /path/to/issues.json --verify-only
.venv/bin/python -m unittest tests.test_samaritan_editorial_audit
```

The verifier checks byte pins and reproduces the audit from private source
inputs. Repository-only tests cover public pins, counts, section mapping,
duplicate annotations, distinct alternative pools and evidence boundaries.
Neither certifies manuscript transcription, source priority, recovered letters,
all-known-source coverage, deployed publication, or a change to the canon.
