# Complete-source repair

The existing 63 imported units are an incomplete edition of Hermas. They end
mid-sentence at Similitude 8.4.5. Completing that import's artwork did not
complete the historical book. The original import also skipped the opening
body leaf and has earlier omissions and merged boundaries.

`coverage.v1.json` keeps the full 114-chapter scope visible. Its 44
`absent_after_cutoff` rows are entirely absent chapters; the incomplete cutoff
chapter and earlier gaps are additional. `boundary_unresolved` does **not**
mean missing: the text may be merged into a neighboring imported unit.
`imported_unverified` does **not** mean complete or critically checked.

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

## Next work

Finish the opening's witness comparison and standard/simplified reader
reconciliation, then repair the earlier truncations and the omitted ending.
The complete-source translation, ID crosswalk, checks, and verified
publication remain required; this checkpoint is not the completed edition.
