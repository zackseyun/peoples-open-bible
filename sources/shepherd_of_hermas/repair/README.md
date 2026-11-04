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

The first cutoff repair transcribed physical pages 380–381, restoring the
remainder of Similitude 8.4 and all of 8.5, and beginning 8.6. At that
checkpoint 8.6 remained incomplete. Existing imported sequences 1–63 stay stable.
`cutoff-20261103.v1.json` records the source work and unfinished English work.

Printed brackets are retained. In particular 8.5.4 is an editorial Greek
restoration supported by ancient versions and absent from A. It must not be
represented as an extant Greek manuscript reading. Page-level editorial notes
now survive normalization. The flat 063 Greek has been updated; its English
and the reader/simplified records still await repair.

## Continuation through Similitude 9.3, 2026-11-03

Physical pages 382–388 are now manually transcribed. The missing printed-body
tail of Similitude 8 is present through 8.11.5, followed by all of 9.1–3.
Only the opening of 9.4 is transcribed; page 389 is next. There are now 74
normalized source units, with new English drafting and reader migration still
pending. This is a source-transcription count, not a count of finished chapters.

`continuation-20261103.v1.json` records bounded apparatus evidence, source
classification, enlarged-scan corrections to transcription errors, and the
post-transcription validation-only control. The control was not copied into
the repository or used for automatic replacement. Printed editorial readings
remain distinct from the Greek wording reported for A, including the changed
rod proportions, willing suffering versus fear, and the inserted negation in
9.3.3. Version traditions L1/L2/E are not individual manuscript votes.

## Bounded manuscript selections and cutoff English

`manuscript-selection-20261103.v1.json` compares selected readings in the
published Athos transcription and Michigan papyrus edition. It selects the
attested suffering verb in 8.10.4 and retains the attested Greek rock reading
in 9.3.1. The raw printed Lightfoot text remains unchanged; selected working
Greek is explicitly attributed through the unit overrides. Neither complete
chapter adjudication nor a fresh direct-image collation is claimed.

Michigan's evidence is not treated as continuous where it is damaged. It has
Greek evidence for part of 8.5.4, absent from Athos, but its noun at 9.3.1 is
in a lacuna, and a lost leaf prevents it deciding the negation at 9.3.3.
Bonner's bracketed supplements are not counted as preserved Greek words.
The copyrighted consultation volume is not vendored.

`reader-cutoff-20261103.v1.json` records the repaired English end of 63:5 and
new 63:6 in both POB and simplified readers. IDs 63:1–5 remain stable; the
standard parent source and simplified base paragraphs are synchronized.
Earlier English and review history are retained. The complete Hermas reader
directories pass syntax and containment checks; both exports have six
paragraphs in chapter 63. These are still drafts pending final collation and
verified publication. The earlier graphic edition remains a separate pinned
text snapshot.

## Further Similitude 9 restoration

`nine-20261103.v1.json` records twelve more scanned leaves (physical pages
389–400). The printed body now runs through 9.xiii, with 9.xiv incomplete
inside paragraph 3. There are 84 normalized working units, not 84 certified
complete chapters. Twenty-three whole ending chapters remain untranscribed,
along with this partial chapter and the earlier gaps and unresolved boundaries.

The normalizer now preserves printed vertical bars delimiting editorial
supplements, and the dagger-marked crux in 9.viii.5. The standard chapter 63
source references were synchronized with the recovered marks; its English,
IDs, simplified bases, and review history were preserved. Earlier normalized
sections also recover their existing raw-file bars; their translation records
have not been silently rewritten. The audit records eleven scan-verified
transcription corrections and several source choices still requiring witness
comparison. First1KGreek was used only for difference detection after manual
transcription; adopted corrections were checked against the acquired scan.

## Next work

`ending-20261103.v1.json` extends the printed body through 9.xvii and into
9.xviii.3 (88 working units). The next required scan leaf is physical page
405; nineteen whole ending chapters remain beyond the partial chapter.
Corner marks now distinguish supplied letters in worm-damaged Athos text
from the edition's other editorial marks. At 9.xvi.6 the printed apparatus
explicitly derives Greek from Clement's quotation. The bounded comparison
in `clement-quotation-20261103.v1.json` checks the acquired 1906 Clement
edition directly and supports retaining the ascent-alive clause. It also
excludes the Clement editor's corrections taken from Hermas from independent
support. This is indirect quotation evidence, not another continuous
manuscript. The unquarried-stones parallel in 9.xvi.7 is internal
context and is not counted as another witness.

`final-leaves-20261103.v1.json` restores physical pages 405–418 through the
edition's final sentence. All 44 whole chapters beyond the original cutoff
now have working printed source text. This yields 107 working units; seven
earlier historical boundaries and earlier truncations/contamination still
need repair before the 114-chapter source can be certified complete.

The edition switches to edited Latin Vulgata at 9.xxx.3, within physical
page 412. That unit is explicitly Greek and Latin; the later units through
10.iv are Latin. Normalized metadata and drafting prompts now carry that
language and prohibit describing the Latin as surviving Greek. Latin line
hyphens and the major heading are parsed without swallowing chapter text.
The ending retains the printed Latin crux and selected apparatus reports,
including a Cambridge manuscript shelfmark conflict and a pseudo-Cyprian
quotation still requiring direct consultation. The old V.3.iii import also
contains an identified printing footer, now queued for scan-based repair.

Finish the opening's witness comparison and standard/simplified reader
reconciliation, then repair the earlier truncations and the omitted ending.
The complete-source translation, ID crosswalk, checks, and verified
publication remain required; this checkpoint is not the completed edition.
