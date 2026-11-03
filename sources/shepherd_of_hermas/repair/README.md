# Complete-source repair

The existing 63 imported units are an incomplete edition of Hermas. They end
mid-sentence at Similitude 8.4.5. Completing that import's artwork did not
complete the historical book. The original import also skipped the opening
body leaf and has earlier omissions and merged boundaries.

`coverage.v1.json` keeps the full 114-chapter scope visible. Its 44
baseline `absent_after_cutoff` rows are entirely absent chapters; the incomplete cutoff
chapter and earlier gaps are additional. `boundary_unresolved` does **not**
mean missing: the text may be merged into a neighboring imported unit.
`imported_unverified` does **not** mean complete or critically checked.
`baseline_source_status` preserves this initial audit, while `source_status`
and `current_source_sequence` track ongoing repair.

`witnesses.v1.json` separates discovered manuscripts, reported readings, and
direct collation. Catalogued witnesses are a work queue, not a completed
comparison. Editions are not extra manuscript votes. The surviving ending
requires ancient versions alongside scattered Greek evidence; never label
Latin text or a reconstructed Greek rendering as an extant Greek witness.

## Opening repair, 2026-11-03

The manually transcribed physical PDF page 313 restores Vision 1.1.1–7 from
the exact Lightfoot–Harmer scan identified in the source manifest. Page 314's
previous first word continues its last sentence. The supplied unit context is
marked `[EDITORIAL UNIT CONTEXT]`; the printed title remains separate.

`opening-20261103.v1.json` records the scan, comparison apparatus, English
draft, retained variants, and unfinished review. The flat standard English
draft has six restored paragraphs and the leading part of the seventh.
Existing review history, the remaining translation, and the repentance
footnote are preserved. This checkpoint does not certify the whole unit's
wording or a completed multi-witness collation.

The October contextual-repentance decision remains immutable. Its validator
accepts this later opening repair only through the exact source/English pair
in `contextual-policy-followup-20261103.v1.json`, whose file hash is pinned in
the validator. Historical checks project the unchanged October decision;
the new source/English pair, live reader note and lexical choices are still
checked. An arbitrary prefix, changed Greek, or a live self-reported hash
cannot grant a follow-up exemption.

Nested standard reader records and simplified records still represent the
earlier partial opening. Reconcile their independent editorial histories and
record an explicit reference migration before publication. The earlier three
reader paragraphs correspond to historical sections 7, 8, and 9. Do not run
the whole-book paragraph splitter over them or silently reassign existing
graphic-reader artwork to the restored paragraphs.

Run the source-regression checks with:

```sh
python3 -m unittest discover -s tests -p test_hermas_source_repair.py -v
```

## Cutoff source repair, 2026-11-03

The completed transcription of physical pages 380–381 restores the remainder
of Similitude 8.4 and all of 8.5, and begins 8.6. Its final sentence remains
incomplete pending page 382. Existing imported sequences 1–63 stay stable.
`cutoff-20261103.v1.json` records the source work and unfinished English work.

Printed brackets are retained. In particular 8.5.4 is an editorial Greek
restoration supported by ancient versions and absent from A. It must not be
represented as an extant Greek manuscript reading. Page-level editorial notes
now survive normalization. The flat 063 Greek has been updated; its English
and the reader/simplified records still await repair.

## Next work

Finish the opening's witness comparison and standard/simplified reader
reconciliation, then repair the earlier truncations and the omitted ending.
The complete-source translation, ID crosswalk, checks, and verified
publication remain required; this checkpoint is not the completed edition.
