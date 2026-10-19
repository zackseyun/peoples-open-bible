# 1 Esdras 6 source import repair

The selected printed Greek contains two clauses missing from POB's source and
English. A misplaced boundary also leaves “life” present in Greek but absent
from the English prayer for the king and his sons. This bounded repair covers
eight records, removes two modern duplicate slices and corrects one specified
accent. It does not select an earlier ancient reading, restore damaged ink,
recover Hebrew or adjudicate canonical authority.

## Source evidence and exact scope

The source is the manifest-matched Swete volumeII scan, SHA256
`945c5b15bf0f9dfc93890b28ee5b66a388acbf4597f1f2be5430ac6cba9c30b0`.
The scout, source author and root read complete printed pages147–150,
one-based PDF165–168, including apparatus. ChapterVI occupies147–149;150
confirms the following VII/VIII headings. Raw source filenames164–166 are
zero-based scan leaves, not printed page numbers. Original PDF/images remain
unchanged; Poppler renders are non-generative. The legacy edition key does
not establish a newly verified imprint date.

The [complete source candidate](../sources/textual_restoration/candidates/1esdras6_source_partition.2026-10-19.v1.json)
maps all33 units. All5167 baseline source codepoints are explicitly retained,
replaced or excluded once, in original order after exclusions. Exactly two
whole clauses are added, two duplicate slices totaling33 codepoints are
recoverably excluded, and `οὓ` becomes the printed `οὗ` at24. No other spelling,
accent, numeral or punctuation polishing is included. The moved `ζωῆς.` keeps
its existing period rather than silently changing to the printed middle dot.

| Units | Confirmed import correction |
|---|---|
| 1 | Printed body has one `οἱ` before “prophets”; remove the modern duplicate and the false note blaming scribal transmission |
| 8 and9 | Move stone/timber construction phrase into8; inline9 begins `καὶ τὰ ἔργα ἐκεῖνα` |
| 10 | Restore `τὰ ἔργα ταῦτα ἐθεμελιοῦτε;`, completing the officials' question; remove the false abrupt-and note |
| 24 | Remove `θύουσιν διὰ πυρὸς ἐνδελεχοῦς,` already present as the joined clause in23; printed24 begins `οὗ τὸ ὕψος` |
| 26 | Restore `τὸν οἶκον τοῦ κυρίου ἐκεῖνον οἰκοδομεῖν ἐπὶ τοῦ τόπου.`, permission to build that house on the site |
| 30 and31 | Move `ζωῆς.` into30 and render life in the royal prayer;31 begins `καὶ προστάξαι ἵνα` |

Current23's genuine complete offering statement remains unchanged. Removing
24's residual page-join fragment must not remove23's actual statement. The
relative “whose height” then refers to the house, not another fire-offering
instruction. The candidate explicitly records the two excluded old slices,
their exact offsets/text/hashes and the one accent replacement.

Negative controls matter: current7/8 and28/29 are correct. The scout's initial
low-resolution suspicion at28/29 was withdrawn after checking the actual
inline29 before `ὁμοίως`; a left-margin number is not that body marker. The
private diagnostic remains pinned as the initial assessment, not application
authority. Root reproduces the eight-target source scope and full codepoint
accounting independently of the candidate's self-reported validation.

## Processing trace and active English

The doubled article is already wrong in raw transcription. Both omitted
clauses survive parsing and the ours-only stream as prefixes wrongly assigned
to11 and27; final adjudication replaces those records without moving the
prefixes into10 and26. The whole clauses disappear from the complete chapter.
The24 duplication arises when23 is repaired across a page-break word but24's
old fragment remains. Source30/31 misassigns life to31, and neither English
record translates it. All33 current Greek records equal the final-adjudicated
stream. These are bounded stage observations, not claims about a model's
private reasoning or ancient textual transmission.

The [English candidate](../sources/textual_restoration/candidates/1esdras6_english_partition.2026-10-19.v1.json)
and [complete application](../sources/textual_restoration/candidates/1esdras6_application.2026-10-19.v1.json)
cover1,8,9,10,24,26,30,31. Words move with clauses, both omitted clauses receive
English, and life returns to the royal prayer. Existing notes and active
lexical/theological decisions must match the resulting passage and actual
main wording. False explanations of modern import errors as ancient variants
are archived, not kept as current evidence. Approximate same-number Hebrew
parallels are not promoted into verified source comparisons.

Each replacement archives its original source, English, decisions and review
state under baseline08a8a4 with its full file hash. Active state returns to
draft/needs_review and medium source confidence. Historical raw/parsed/ours/
adjudicated files remain untouched. No canonical record is deleted; all33
chapter6 IDs and495 book records remain.

Record24 has lost its `ai_draft` and other metadata in a later historical
wholesale edit. Its genuine same-verse draft receipt survives at commit
`41ee5f853caacef940590c4136a4947901ed39e8`, file SHA256
`9d04bce5f7b00e2b71b1db86e4e1ac66157d595067d89c738fad79deca4ad604`.
Restore only that receipt unchanged, with explicit source commit/path/hash,
missing-baseline-receipt status and `certifies_current_record: false`. Do not
borrow23's receipt, invent a provider call or weaken schema requirements.

## Recurrence and review boundaries

The existing normalized source lane reproduces the bounded correction while
preserving every chapter5 and8 row. The tests cover all33 source units, the
eight schema-valid full records, exact note anchors and archives, the genuine
historical receipt, all487 unaffected surviving YAML files, source-loader
recurrence and the actual whole-book export. The export must remain nine
chapters/495 units, with only the specified chapter6 output changing. Contiguous
numbering alone cannot prove completeness.

```sh
.venv/bin/python tools/build_normalized_deuterocanon_corpus.py --book 1ES
.venv/bin/python -m unittest discover -s tests -p 'test_1esdras6_partition_application.py'
.venv/bin/python -m tools.textual_restoration.replay_historical_tests esdras5_partition
.venv/bin/python -m tools.textual_restoration.replay_historical_tests esdras8_partition
```

The original chapter5 and8 proofs remain unchanged at their applied snapshots;
their historical assertions are not repinned or weakened to certify this
successor. Separate live checks protect all current chapter5/8 records. The
[evidence packet](../sources/textual_restoration/comparisons/1esdras6_application.2026-10-19.v1.json)
binds one independent review to the complete prepared application before
canonical replacement. Review of this import repair is not whole-verse
lexical approval or an ancient-priority decision.

Reader/publisher layout stays on hold. PR371's chapter5 head remains fixed
while its integrity jobs run; this successor uses a separate branch.
Publication requires ordinary commits/pushes, exact-head checks and merge.
Git delivery alone does not establish a refreshed website/CDN deployment.
