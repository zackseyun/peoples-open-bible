# 1 Esdras 5 source import repair

Two family entries present in the selected printed Greek edition are absent
from POB's current source and English. Two verse boundaries are misplaced, and
an extra record duplicates verse47. This bounded repair restores those entries
and boundaries, preserves the duplicate in quarantine, and restores chapter5
to the existing whole-book export. It does not establish the earliest ancient
reading, recover Hebrew, decide canonical authority or certify a full lexical
collation of the book.

## Printed evidence and corrections

The source is the exact volumeII scan in the
[Swete manifest](../sources/lxx/swete/MANIFEST.md), SHA256
`945c5b15bf0f9dfc93890b28ee5b66a388acbf4597f1f2be5430ac6cba9c30b0`.
The source author and root each read complete printed pages141–147, one-based
PDF pages159–165, including apparatus and adjoining chaptersIV/VI. The seven
raw transcription filenames use zero-based scan leaves158–164, not printed
page numbers. The legacy edition key is retained without claiming a newly
verified imprint date. Rendering is non-generative; the original PDF is unchanged.

The [complete Greek candidate](../sources/textual_restoration/candidates/1esdras5_source_partition.2026-10-19.v1.json)
maps all70 printed units to exact slices of the existing source. Every nonspace
codepoint from existing units1–70 is consumed once in its original order. Only
two printed entries are added; no general spelling or punctuation polishing
is included.

| Unit | Bounded correction |
|---|---|
| 25 | Restore `υἱοὶ Χαρμή, διακόσιοι δέκα ἑπτά·`, the sons of Charme,217, after Phassor1247 |
| 28 and29 | Move the Tobeis139 entry into28; inline29 begins `οἱ ἱερόδουλοι` |
| 31 | Restore `υἱοὶ Βασαλέμ,`, the sons of Basalem, before inline32 |
| 38 and39 | Move `καὶ ἐκλήθη ἐπὶ τῷ ὀνόματι αὐτοῦ.` into38; inline39 begins `καὶ τούτων` |
| Extra145 | Quarantine the exact Greek duplicate of47;145 is the printed page footer, not another body verse |

The initial private scout misread the first restored number as1017 and the
second name with eta (`Βασαλήμ`). Root's direct page check corrects the number;
the source author's reread also corrects the name to epsilon (`Βασαλέμ`). The
candidate records both corrections and pins the unchanged earlier diagnostic.
It does not treat that diagnostic as authority for the insertions.

At25, the main body has217. The apparatus reads
`διακοσιοι 2°] χιλιοι A`: A has “thousand” for the second occurrence of “two
hundred,” producing1017. The English follows the selected edition's main text
and discloses the reported alternative. The apparatus report is evidence for
that difference, not a fresh direct collation of manuscript A or a judgment
that217 is earliest. Main text, apparatus and modern transcription must remain
separate evidence layers.

## Processing trace and English application

Both omitted entries survive raw transcription, parsed AI and the ours-only
stream, although some names and boundaries there are inaccurate. They are
absent from the complete final-adjudicated chapter, which the current71 YAML
source fields reproduce exactly. The two boundary mistakes are already present
in the parsed/ours-only layers. Extra145 appears only in the later adjudicated
layer; its rationale itself names printed145 and Swete V47. These observations
bound the losses and duplication without claiming a specific model-internal
cause.

The [English candidate](../sources/textual_restoration/candidates/1esdras5_english_partition.2026-10-19.v1.json)
and [complete application](../sources/textual_restoration/candidates/1esdras5_application.2026-10-19.v1.json)
cover exactly six records:25,28,29,31,38,39. Existing wording moves with its
clause; the two absent entries receive English. Notes and active lexical and
theological decisions must describe the actual surviving passage. Misleading
same-number Hebrew-list comparisons are archived rather than represented as
verified textual variants. This does not deny genuine Hebrew parallels or
authorize a reconstructed Hebrew Vorlage.

Each replacement archives the old source, translation, active decisions and
review state with its original file hash and baseline commit
`756074bd3e0bd97c5d849c5ff47125972f4684b2`. Genuine AI draft receipts remain
unchanged as historical provenance. The replacements use `draft`,
`needs_review` and medium source confidence; old high-agreement labels do not
approve these changes. The complete redundant145 YAML, including its distinct
English draft and metadata, is retained byte-for-byte in
[quarantine](../sources/textual_restoration/quarantine/1esdras5_duplicate145.2026-10-19.v1.yaml).
It is not merged into47 as if it were another ancient witness.

## Recurrence and verification

Historical raw, parsed, ours-only and adjudicated inputs remain immutable.
The existing normalized override lane applies the six chapter5 corrections
and excludes only the redundant145 row, while preserving the chapter8 repair:

```sh
.venv/bin/python tools/build_normalized_deuterocanon_corpus.py --book 1ES
.venv/bin/python -m unittest discover -s tests -p 'test_1esdras5_partition_application.py'
.venv/bin/python -m tools.textual_restoration.replay_historical_tests esdras8_partition
```

The live tests require the exact six full records, correct note bindings,
archived review state, two literal Greek additions, source-slice conservation,
historical and reviewed-file pins, and byte-identical preservation of all489
unrelated surviving canonical records. The source loader must return495 units
and reproduce the normalized source; unexpected source drift is an error.

A real before/after export must change from eight chapters/425 units to nine
chapters/495 units, with chapter5 exactly1–70 and every other exported chapter
unchanged. Removing145 alone would restore export inclusion but leave the
omissions and boundary errors unresolved. Contiguous IDs are therefore not
enough to establish completeness.

Chapter8's original six assertions and receipts remain unchanged at their
applied checkpoint756074b and are replayed there using original baseline97194d.
Their old496-record/eight-chapter expectations are historical, not weakened or
repinned to approve this successor. Separate live tests protect every current
chapter8 record. One independent review checks the exact assembled chapter5
application before canonical replacement; the
[evidence packet](../sources/textual_restoration/comparisons/1esdras5_application.2026-10-19.v1.json)
binds that review to the prepared files.

Reader/publisher layout stays on hold. Existing note routing is part of the
content repair, not a new disclosure system. Publication requires the exact
new head's integrity checks and an ordinary merge/push; Git publication does
not establish that a separate website/CDN deployment has refreshed.
