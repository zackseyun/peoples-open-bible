# Old Testament source provenance checkpoint

## Result and scope

At repository revision `e0550475abcb86738b365fabe34a582793503327`, all 23,264
OT records in 39 book folders have accounted-for source representations. No
unexplained WLC wording difference was found. The five declared critical verses
also pass their existing source-composition and full-record binding checks.
This verifies the Hebrew/Aramaic working corpus against its declared sources,
not the historical priority of every reading or a complete manuscript collation.

The [machine-readable checkpoint](../sources/textual_restoration/comparisons/ot_source_provenance.2026-10-18.v1.json)
records actual counts, input digests, procedures and delivery observations.
It follows the older [October 10 checkpoint](TEXTUAL_ADJUDICATION_METHOD.md#source-provenance-checkpoint)
because Deuteronomy 32:8 and 1 Samuel 2:22 subsequently adopted explicit
critical sources. Historical checkpoints and review receipts remain unchanged.

## Current source accounting

| Non-Psalm category | Records |
| --- | ---: |
| Exact legacy WLC written rendering | 20,680 |
| Canonically equivalent Unicode combining order only | 1 |
| Explicit registered qere selection | 1 |
| Declared critical source | 4 |
| Total across the other 38 books | 20,686 |

Ecclesiastes 1:2 remains equal under both NFC and NFD; the code-point order
difference is not a different Hebrew letter or vowel. Isaiah 9:2 passes the
actual registered selection resolver rather than a silent WLC exception.

The existing Psalms context-map test passed for all 2,578 records. Its 2,527
WLC contexts, 52 reused contexts, combined Psalm 60 heading and explicit
73:10/145:13 overlays retain their distinct rules. Numbering and segmentation
do not manufacture extra manuscript witnesses. The non-Psalm total and Psalm
record total together account for the full 23,264-record working corpus.

The critical verses are Deuteronomy 32:8, 1 Samuel 2:22, 1 Samuel 17:4,
Psalm 145:13 and Isaiah 53:11. Existing verification checked the actual
compositions, review/candidate bindings and complete current critical records.
No new source-preference vote, historical certainty or publication authority
is inferred from those integrity results.

## Procedure and preservation

The read-only scan parsed each non-Psalm XML book once and assembled direct
word children with `tools.wlc.word_text`, followed by the legacy punctuation
rule. It compared each declared WLC source, used the existing resolver for
registered selections and enumerated non-WLC records explicitly. Critical
validation used externally recorded literal hashes, not approval inferred
from an edition label. The existing Psalm test supplied the separate mapping
and overlay verification.

The scan took 58.293 seconds; the Psalm test passed in 7.485 seconds. Raw
path/hash inventories for all OT records and XML inputs were identical before
and after the scan. No verse, XML source, selection index or implementation
changed. These are integrity checks, not a new reusable validation framework
or a rerun of the entire publication suite.

The legacy renderer moves paragraph symbols to verse ends. Matching it does
not certify original XML segment positions or manuscript pixels. The ordered
source view remains necessary for that different question. Unicode equivalence,
selected qere and critical-source composition are recorded separately, not
collapsed into an undifferentiated exact-match rate.

## Public reader baseline and infrastructure boundary

At 00:02:15 UTC, the actual Lamentations 1 chapter displayed marker-free text.
Its selected-verse action opened the correct public 1:17 provenance record.
That record still had one old note anchored to consolation, not the new
4Q111 disclosure. Its review label was “Review result not established”; the
historical 95% display was not approval of the new candidate. This is a
before-release observation, not a deployed-note pass.

At 00:04:45 UTC, website run `39076928993`, job `117525901034`, remained
queued with no assigned runner. The sole repository-visible runner matching
its required self-hosted Linux/ARM64/cartha-ci labels was offline and not busy;
the repository had no in-progress workflow run. This establishes a concrete
runner-availability problem at the inspected scope, not an organization-wide
runner census or a proven cause of earlier cancellations.

Runner recovery requires separate authority, which was requested and remained
pending at this observation. No infrastructure, external publisher or reader
code was changed. Bible-repository CI and provenance delivery are separate from
that website build; the offline runner does not establish failure of those
other processes. No new inline panel or canon change follows.
