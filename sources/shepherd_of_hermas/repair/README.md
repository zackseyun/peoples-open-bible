# Complete-source repair

The original 63 imported units were an incomplete edition of Hermas. They ended
mid-sentence at Similitude 8.4.5. Completing that import's artwork did not
complete the historical book. The original import also skipped the opening
body leaf and has earlier omissions and merged boundaries.

The working source now represents all 114 historical chapters and includes the
printed ending. The earlier marker/length repair queue and six missing chapter
boundaries have been resolved. Full word-level verification, manuscript
comparison and English reader revision remain unfinished. The legacy reader's 63 chapter IDs stay
unchanged; source-index changes are recorded in the migration inventory below.

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
checkpoint 8.6 remained incomplete and imported sequences 1–63 were unchanged.
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
reconciliation, and repair the remaining earlier omissions and boundaries.
The complete-source translation, ID crosswalk, checks, and verified
publication remain required; this checkpoint is not the completed edition.

## Earlier source repair and reader migration inventory

`earlier-gaps-20261103.v1.json` restores omitted Mandate 12.iii/iv/vi text,
the first Similitude's missing opening and ending, and the second's missing
opening. Greek-encoded Roman X is recognized at Vision 3.x, returning its
preceding continuation to 3.ix. The printing footer in 3.iii is removed
from body and preserved in an editorial note. Unnumbered Other Similitude
headings now separate the S.2 tail, complete S.3 and S.4 opening. There are
108 working units and six remaining historical boundary questions.

The page audit also identifies 21 short or unclosed raw-page candidates.
This is a review queue, not proof that all 21 lack text: some have later
unit overrides and some may simply lack an end marker. Unflagged pages are
not certified complete by that heuristic. S.4's raw-page 362 truncation is
confirmed and still needs repair. A scan check also corrects prayers versus
souls in the S.2.8 source; corresponding reader review remains pending.

`reader-source-crosswalk-20261103.v1.json` preserves the identities of all
63 legacy reader chapters while recording the corrected source order and
legacy source containers spanning several chapters. It is not a finished
paragraph redirect map. No English or reader ID is changed here. The draft
writer now rejects a source-index destination occupied by a different reader
ID, including overwrite mode, so inserted source chapters cannot erase
existing English before the explicit reader migration is completed.


## Mandate boundary repairs

`mandate-boundaries-20261103.v1.json` records direct scan restoration of
physical pages338,340,342. Missing M.4.iv, M.5.ii and M.6.ii headings now
separate their formerly misassigned continuations. There are111 working
units, with three S.5 boundaries still outstanding. The previous21-page
review queue has18 unresolved candidates; this is not a missing-word count.

`reader-source-crosswalk-20261103.v2.json` updates source ordering while
preserving all63 legacy reader IDs. Its prior version remains a checkpoint.
M.4.iii, M.5.i and M.6.i legacy source containers each included the following
chapter's surviving tail. English paragraph alignment remains pending.
The newly transcribed apparatus records substantive readings, including
Athos's negation at M.4.iii.6 and the edition-reported Sinaitic endpoint.
These are edition reports awaiting further witness comparison, not fresh
manuscript-image collation or completed English adjudications.


## Similitude 5 and full chapter-boundary inventory

`similitude-five-20261103.v1.json` records restored body from physical
pages362–367, including S.4's ending, S.5's opening and the missing S.5.iv
and vi headings. All114 historical divisions now have working source units.
This establishes chapter representation, not complete source verification:
twelve earlier page candidates, older overrides and full witness collation
remain. The English and illustrated readers are still incomplete.

`reader-source-crosswalk-20261103.v3.json` preserves all63 legacy IDs and
updates source order (S.8.iv is now70 in source order, still63 in the legacy
reader). Earlier crosswalks remain checkpoint evidence. S.5.ii's old source
included the S.5.i tail; S.5.iii included S.5.iv's tail; S.5.v included S.5.vi.
No English or artwork is silently reassigned. Printed supplements and
conjectures, including the substantive negation at S.5.vi.1, remain explicitly
distinguished from manuscript readings pending adjudication.


## Earlier leaves and end-marker audit

`earlier-leaves-20261103.v1.json` records scan review of331,336,351,352,
370,372,375,377. Seven pages had body omissions;351's printed body was
already complete and only its apparatus/end marker needed repair. Page377
had a marker despite missingS.8.i.15–18 and the opening ofii.6. Completeness
cannot be inferred from markers or114 chapter labels. Four earlier raw
candidates345–348 and all older overrides still need primary-scan checking;
a comprehensive source and witness audit remains required.

`reader-source-crosswalk-20261103.v4.json` records that oldS.8.i also held
theS.7 continuation from375. All63 legacy English IDs remain unchanged.
Printed conjectures and substantive alternatives, includingM.11.14's
earthly/holy spirit andS.8.ii.2's seal/seals, remain explicitly recorded
for adjudication and corresponding English review. No completed-reader or
publication claim follows from these source repairs.


## Primary-scan provenance for Mandates8–10

`override-provenance-20261103.v1.json` records restored raw345–348 and
scan review of344–350. Five modern-web whole-unit overrides (M.8,M.9,
M.10.i–iii) are retired; these chapters now normalize directly from the
primary printed source. Baseline commit and hashes retain their audit trail.
The two explicit bounded manuscript selections remain active.

This resolves the original marker/length-based raw-page queue, not the full
source audit. Printed brackets and version-supported bars dropped by the
old patches are now retained. Source/English differences, includingM.8.6's
dialogue division, require adjudication and reader revision. The legacy
English, artwork and63 IDs remain unchanged; all114 source divisions are
represented but the completed edition is still unproven.

A broader comparison of106 purely Greek units against an external
validation-only digital edition flags three large source-only spans. All
three are printed supplements inS.5.iii,vi,vii, checked in primary scans;
no additional large control-only gap was found at the12-word threshold.
This does not verify every word, shorter or shared omissions, the mixed/Latin
ending, or any manuscript choice. The comparison text is not vendored.


## Greek fragments and new English ending drafts

`oxy404-ending-20261103.v1.json` recordsP.Oxy.III404 alongside continuous
Latin. Published correctedGreek know informsS.10.iii.4; sourceLatin see is
unchanged and the full English alternative is exposed. Purity/dwelling and
plural-guilt differences remain open. PlateIV404(c)recto was inspected;
this does not certify the verso or reported correction. Restorations are
not ink. The continuous source language remainsLatin.

New standard/simplified flat drafts113–114 coverS.10.iii–iv, five paragraphs
each. Previously empty slots preserve all63legacy IDs. These are unreviewed
source-based drafts with alternatives, not completed English, paragraph
migration, artwork or publication. No fullGreek ending is invented.


## Amherst Greek at the continuous-source boundary

`amherst190-ten-drafts-20261103.v1.json` records primary-edition and
PlateXXIV inspection of P.Amh.II190. Fragment h overlaps S.9.xxx.1–4;
its verso preserves some Greek beyond the continuous Athos cutoff.
It does not cover S.10.i–ii. Missing letters, proposed future-belief wording
and the separate xxx.5 crux are not certified by this fragment. The source
body remains unchanged; the comparison is attached to the source warning.

New standard/simplified flat108–112 draft S.9.xxxi–xxxiii and S.10.i–ii
from Latin. Together with113–114, all seven purely Latin tail chapters
now have English drafts, not independent review or reader/artwork migration.
Thirty-seven of the44 whole ending chapters still need drafts, alongside
earlier English repairs. Bracketed editorial supplies and conjectures remain
visible in footnotes, including the supplied death penalty in S.9.xxxii.4.


## Greek/mixed-source drafts through the white mountain

`white-mountain-drafts-20261103.v1.json` records new standard/simplified
flat105–107 for S.9.xxviii–xxx. Greek changes to edited Latin at xxx.3;
the English preserves that declared basis. Amherst h is consulted only
for its overlapping fragment. It cannot settle the conjectural inventi
or the separate dagger-marked Latin crux in xxx.5. Those uncertainties,
the Greek fruit adjective variant and restored blessing remain explicit.

Ten of the44 wholly omitted ending chapters now have drafts, leaving34;
this does not complete earlier English repairs, independent review,
reader/artwork migration or publication. The source body is unchanged.


## Cambridge Latin witness identity

`cambridge-identity-20261103.v1.json` checks the primary1856 library
catalogue entries186–187: Hermas is Dd.IV.11, ff.68a–90a, with the
reported ending inside S.10.iii.2. Dd.IV.12 is a different Jerome volume.
The former inventory label is corrected, retaining its legacy ID as an
alias for traceability, not an additional witness. The S.10.ii.4 faciunt
report still needs direct manuscript collation; catalogue identity alone
does not verify that reading. Draft112 footnotes/provenance reflect this
resolution, with English text unchanged.


## Further ending drafts and bounded excerpt comparisons

`service-mountain-drafts-20261103.v1.json` records new standard/simplified
flat102–104 for S.9.xxv–xxvii,13paragraphs per edition. The office-term
conjecture and Athos alternative remain explicit. Thirteen of the44 wholly
omitted ending chapters now have drafts;31still need drafts. Earlier
English repairs, review, migration and publication remain incomplete.

`florilegium-comparison-20261103.v1.json` records bounded comparisons
and draft revisions. The current108–112 draft checkpoint is
`amherst190-ten-drafts-20261103.v2.json`; v1 is preserved as history.
No continuous source body, legacy reader ID or artwork is replaced.


## Earlier dialogue repair and further mountain drafts

`six-four-repair-20261103.v1.json` selects one reported Lavra duration
clause in S.6.iv.2 in place of the older conjectural supplement. The raw
printed source remains intact; the third bounded working override is
explicit. Paragraph numbering differs from the study’s locus label, and
punctuation is editorial. Legacy flat057 is repaired to four complete
paragraphs, and a new flat simplified057 is added. Prior flat standard and
nested simplified records are archived. Source sequence64 remains reader57;
no nested reader/artwork repinning or publication is claimed.

`forgiveness-mountain-drafts-20261103.v1.json` records new standard and
simplified flat099–101 for S.9.xxii–xxiv,13paragraphs per edition.
Foolishness, childlikeness/gentleness and spirit/seed alternatives remain
explicit. Sixteen of44wholeomittedendingchapters now have drafts;28remain.
Full source collation, earlier English repairs, review, migration and
publication are still incomplete.

## Later Greek witnesses: coverage correction and image inspection

`sinaiticus-new-finds-20261103.v1.json` withdraws the inventory's incorrect
rejection of later Sinaiticus coverage. The Codex Sinaiticus Project reports
1975 finds in Similitudes 6–7 and a leaf containing 9.xiv.4–xviii.5. These are
separated regions of the same codex. The project's reconstruction of lost
text is not surviving text, and no new Sinaiticus reading is selected here.

`oxy3528-images-20261103.v1.json` records official DCLP metadata and private
inspection of two Oxford photographs. Only small portions of 9.xx.3–4 and
9.xxii.1 survive. They cannot certify the supplied negation in 9.xx.2 or the
entire repentance condition in 9.xx.4. The metadata has no Greek transcription;
the copyrighted photographs remain outside the repository.


## Responsibility and further mountain drafts

`accountability-drafts-20261103.v1.json` records standard and simplified
flat095–098 for S.9.xviii–xxi:16paragraphs per edition. The first
God/Christ/Lord question, bare/high/dry mountain, supplied negation and
repentance conditions, and women/activities alternative remain explicit.
Twenty of44wholeomittedendingchapters have drafts;24remain. These are
unreviewed drafts; earlier English repairs and reader/artwork migration
remain incomplete. No source-body change or publication is claimed here.


## Primary Sinaiticus transcription and seal chapters

`sinaiticus-passages-20261103.v1.json` records acquisition of the official
Birmingham backup of the Codex Sinaiticus Project transcription v1.05. The
modern XML remains outside the repository; this record contains bounded
ancient-word observations, hashes and editorial decisions. Supplies, gaps
and correcting hands are kept separate. Its wrongly labelled chapter65
division must be located by its explicit identifier, not the n attribute.
The separated New Finds regions extend into S.8.ii.5 as well as the later
S.9.xiv.4–xviii.5 leaf; they are not continuous coverage of the gaps.

The fourth bounded working source selection replaces the old conjectural
“who ought to do good” with the Sinaiticus “who loves to do good” at
S.9.xviii.2. The final letters of the infinitive are dotted as uncertain,
not supplied. The first God noun atxviii.1 is also attested in the primary
transcription; the following verb has distinct original/corrected forms.
Prior source and English are archived in `chapter95-before-sinaiticus-20261103.v1.json`.
`accountability-drafts-20261103.v2.json` records current hashes; v1 remains
a historical checkpoint. Only this source phrase and its corresponding
English change; no full Sinaiticus adoption or image verification is claimed.

`seal-drafts-20261103.v1.json` records new flat091–094 for S.9.xiv–xvii,
24paragraphs in each English edition. The negative conditional and entry
clause have bounded Sinaiticus support. The alive-again phrase retains
Clement quotation support alongside the shorter Sinaiticus alternative.
Twenty-four of44wholeomittedendingchapters now have drafts;20remain.
Independent review, earlier English repairs, reader/artwork migration and
publication remain incomplete.


## Tower, gate and clothing drafts

`gate-drafts-20261104.v1.json` records new standard and simplified flat087–090
for S.9.x–xiii:33paragraphs per edition. Lord/world, Son/holy-name and
him/God alternatives remain visible, as does the long version-supported
supplement in xiii.4. The affection, brother/husband distinction, prayer,
plural holy spirits and clothing metaphor are preserved.

`amherst190-gate-20261104.v1.json` bounds fragmentsf/g to their actual
partly surviving passages. Fragmentf stops before the Lord/world variant;
fragmentg has its twelve in brackets. Existing flat094 receives a note and
provenance clarification only. No new source-body selection is made.
Twenty-eight of44wholeomittedendingchapters now have drafts;16remain.
Review, earlier English repair, reader/artwork migration and publication
remain incomplete.


## Stone inspection and restoration drafts

`stone-drafts-20261104.v1.json` records flat083–086, S.9.vi–ix:29paragraphs
per edition. `stone-witness-comparison-20261104.v1.json` records two bounded
source selections: three staff strikes and no joint in the completed tower.
It preserves the exact before/after text and hashes, as well as the older
positive-joint alternative. The new public-domain Latin editions are used
only at declared passages; editions are not counted as new manuscripts.

The white-stones Greek crux remains dagger-marked. The certainly/all/perhaps
variant and version-supported long supplements are exposed in English notes.
All new English remains draft with independent review pending.32of44whole
omittedendingchapters now have drafts;12remain. Reader/artwork migration,
earlier English repairs, full collation and publication remain incomplete.


## Foundation and building-pause drafts

`foundation-drafts-20261104.v1.json` records flat079–082 for S.9.ii–v:
27paragraphs in each edition. The existing rock selection remains; no new
source-body override is made. `foundation-witness-comparison-20261104.v1.json`
bounds Michigan’s lost leaf, shorter reason and damaged instruction, and
Amherst190e’s partial overlap. Latin editorial non and rock are not counted
as independently preserved readings. The supplied negative, 25/20/15 counts,
foundation supplements and long return-promise supplement stay explicit.

Thirty-six of44wholeomittedendingchapters now have drafts;8remain. All new
drafts still need independent review. Earlier English repairs, full manuscript
comparison, reader/artwork migration and publication remain incomplete.


## Rods, repentance offer and twelve mountains

`rod-mountain-drafts-20261104.v1.json` records flat075–078, S.8.ix–xi and
S.9.i:23paragraphs per edition. Three bounded source selections are archived
in `rod-mountain-witness-comparison-20261104.v1.json`: the conjunction extending
the offer to both groups, only-believed, and their-wickedness. The papyrus
conjunction’s alpha is restored; the only-word in Michigan is wholly supplied
from spacing, so Athos supplies that selection’s preserved Greek evidence.

Michigan partly preserves clauses earlier supplied from versions in xi.3–4,
without making their full reconstructed wording intact manuscript testimony.
The existing suffering verb is carried forward without supplied willingness.
The Spirit/Son identification and all twelve mountain descriptions remain.
Forty of44wholeomittedendingchapters now have drafts;4remain. Full source
collation, earlier English repairs, independent review, reader/artwork
migration and publication remain incomplete.


## Last four omitted ending drafts

`final-omitted-drafts-20261104.v1.json` records flat 071–074, S.8.v–viii:
23 paragraphs per edition. All 44 whole chapters omitted after the original
cutoff now have standard and simplified flat drafts. They remain drafts with
independent review and reader/artwork migration pending. This milestone does
not certify the whole source or complete the earlier English repairs.

`final-omitted-witness-comparison-20261104.v1.json` archives the exact
S.8.vi.6 sins/sinners noun selection: Athos reads sinners; Michigan partly
preserves the noun, with its ending restored. The 1891 historical wording is
unchanged. The new drafts expose the name/law variant, Michigan’s shorter
rod list and omitted negative condition, and the version-supported green/dry
reversal that Michigan’s gap cannot decide. P.Oxy1599 remains a reported lead
awaiting direct primary-edition comparison, not a freshly collated witness.


## Vision 4.ii missing dialogue and warning

`vision-four-dialogue-20261104.v1.json` restores all six historical paragraphs
in flat standard reader slot 023 and a new flat simplified draft. The former
three-paragraph English joined the opening of paragraph 2 to the ending of
paragraph 5, losing the church identification, beast dialogue and warning’s
conditions. Prior flat and six nested records are preserved in
`legacy23-before-dialogue-repair-20261104.v1.json`. Nested reader/artwork
migration remains pending, with the malformed paragraph mapped explicitly.

Renewed print review corrects an earlier transcription’s singular beast to
plural beasts. The bounded name selection follows Athos Thegri against the
printed Segri conjecture, with corrected Sinaiticus’s corresponding spelling
and its disturbed earlier form distinguished. Primary Sinaiticus project XML
23.1–6 also supplies substantive white-hands and holy-angel/name alternatives.
No modern XML is vendored and no full manuscript photograph collation or
independent English review is claimed.


## Mandate 11 missing tests and illustrations

`mandate-eleven-repair-20261104.v1.json` restores the flat standard chapter 040
and creates a complete simplified flat draft, all 21 historical paragraphs.
The former Heaven placeholder at 14 now contains the missing 14–18: the
assembly test, empty jar, test by life and works, two kinds of spirit, and
stone/water examples. Prior flat and nested records are archived in
`legacy40-before-dialogue-repair-20261104.v1.json`; reader/artwork migration
and independent review remain pending.

Athos’s holy-spirit reading at 14 is exposed against the working earthly
correction. Bounded printed Vulgata and Palatina comparisons support earthly;
this is versional evidence, not preserved Athos Greek or a fresh manuscript
photograph collation. The angel-of-prophet alternative at 9 is also explicit.
No source body changes in this follow-up.

The 397-record terminology plan remains unchanged. Paragraph 4, its contextual
reader note, lexical choice and revision metadata are retained. The separately
hash-pinned `contextual-policy-eleven-followup-20261104.v1.json` permits only
the exact later source/text repair while continuing the original terminology
checks. It adds no general exemption or live-record self-certification.


## Mandate 4.iii–iv baptism dialogue and remarriage

`four-baptism-repair-20261104.v1.json` repairs legacy flat reader 031 and
adds a complete simplified draft: seven historical paragraphs of iii and
four of iv. Both complete normalized sources are retained in declared
character spans. III/IV labels expose the boundary. Reader 032 remains M.5.i;
no index-based overwrite, new public redirect or artwork reassignment occurs.
The former flat and 16 nested records are archived in
`legacy31-before-baptism-repair-20261104.v1.json`.

The positive repentance warning is provisionally retained with the substantive
Athos negative alternative explicit. Printed Vulgata/Palatina comparisons
support the positive/repeated-repentance sense; damaged Sinaiticus breaks off
before that clause and cannot decide it. Its XML also files portions of iii.3
inside chapter 30.3; supplied words are not treated as manuscript ink. Older
and later Athos edition reports disagree at iii.3 and the calling phrase.
No normalized source body changes or full photograph collation are claimed.

The historical 397-record terminology plan remains unchanged. The separately
hash-pinned `contextual-policy-four-followup-20261104.v1.json` validates the
complete repaired record before projecting its prior terminology history.
Independent review and reader/artwork migration remain pending.


## Mandate 4.i–ii recorded-source and annotation alignment

`four-source-alignment-20261104.v1.json` distinguishes a missing source
record from missing English: standard 029 already contained all eleven
historical paragraphs in six reader paragraphs. Its attached Greek still
skipped from i.5 into i.8; it now matches the restored normalized source,
including printed supplements. Standard 030 already matched its normalized
source and retains that source unchanged. English wording in both is
unchanged; numeric footnotes now attach to their actual phrases. The obsolete
029a rendering is preserved in the before-record archive rather than displayed
as a current variant. Contextual repentance notes and lexical decisions remain.

The new i.11 note distinguishes Sinaiticus's shorter first-hand text from
its ca/d corrections containing the healing clause. Athos's diplomatic
transcription and the printed Vulgata also contain healing. The working
reading is retained without treating correcting hands or editions as additional
independent manuscripts. No normalized source body changes are made.

The two finite, separately hash-pinned `contextual-policy-four-029-followup-`
and `contextual-policy-four-030-followup-20261104.v1.json` records validate
each complete repaired record before historical projection. The immutable
397-record terminology plan is unchanged. This bounded source/annotation
alignment does not clear either chapter's full review queue. Simplified flat
drafts, independent review, nested-reader reconciliation and publication remain
pending.


## Mandate 5.i–ii patience and quick temper

`five-temper-repair-20261104.v1.json` restores the lost prayer clause at i.6,
the household warning and whole-heart repentance promise at i.7, and ii.1–3's
opening explanation of quick temper. Complete standard and simplified flat
drafts cover i.1–7 and ii.1–8 in fifteen paragraphs. Character spans and I/II
labels retain both historical sections within legacy032; legacy033 remains
Mandate6i. Fourteen old nested records and the former flat record are archived
unchanged. No normalized source bodies or artwork are changed.

Bounded comparisons distinguish Athos's feminine prayer pronoun and my-power
reading from the working source's masculine pronoun and the Lord's power.
The printed Vulgata and Palatina divine-power renderings support the latter
sense without becoming identical Greek testimony. The justification by the
most revered angel and all conditions remain explicit. Sinaiticus ends before
this passage and cannot decide its variants. These are working drafts; fresh
photograph adjudication, independent review and reader migration remain pending.


## Mandate 6.i–ii roads and the two angels

`six-two-angels-repair-20261104.v1.json` restores the straight-road conclusion,
wholehearted turning to the Lord, the two-angel introduction, and the complete
working description of the righteous angel. Standard and new simplified flat
drafts cover i.1–5 and ii.1–10 in fifteen paragraphs. Hashed character spans
and I/II labels retain both sections in legacy033, with legacy034 still M.7.
Six old nested records remain unchanged. The old flat and generation/review
history are archived; they do not certify the repaired candidate.

The bounded Athos transcription has a shorter ii.3 description; the two
printed Latin versions have different lists. Notes expose those differences,
Greek turning versus Vulgata belief at i.5, and edited imperative/now forms
versus Athos indicative/therefore. Both necessity claims and the final positive
and negative work clauses remain. No harmonized manuscript consensus is claimed.

`six-source-corrections-20261104.v1.json` preserves the full prior raw page343
and its hash, correcting the article to printed OR at ii.5 and restoring the
acute in good at ii.8. Normalization reproduces those two corrections only.
They are transcription repairs, not additional manuscript selections.
Independent English review, full photograph adjudication, reader/artwork
reconciliation and whole-book publication remain pending.


## Mandate 7 fear teaching and Clement parallels

`seven-fear-witness-comparison-20261104.v1.json` records that the standard
source and English already cover all five paragraphs. English words are
unchanged; new notes distinguish the fear contrast, both evil/good branches,
editor-supplied Latin text and the singular Greek versus differing Latin
endings. A complete five-paragraph simplified flat draft is added. Ten nested
records remain unchanged. This bounded comparison leaves the full source
collation queue and independent-review status pending.

Clement's Stromata II.12, Stählin1906 printed143 lines5–10, paraphrases the
fear teaching with additional building-up/love explanation. The adjacent
lines10–13 and II.13 discussion on143–144 provide further indirect evidence
for Mandate4ii/iii. These are paraphrase/discussion, not continuous Hermas
manuscript readings, and do not independently decide the exact iii.6 negation.
No Clement expansion or editorially supplied Latin wording enters normalized
Hermas Greek. The final in-them interpretation is retained with an explicit
in-him alternative; independent interpretation review remains required.


## Mandate 8 self-control and practical service

`eight-service-alignment-20261104.v1.json` replaces legacy035's retired web
override with the restored continuous printed source. All twelve English
paragraphs already existed. Standard and new simplified flat drafts follow
the working single-speaker question at6 and needy-debtors adjective at10,
with Athos's dialogue and conjunction alternatives explicit. The stumble
metaphor now reads grammatically; respectful address and footnote anchors are
corrected. Twenty-four old nested records and artwork remain unchanged.

Notes preserve the version-supported printed insertion at2, shorter Athos
vice list, Lord/God at9, brotherhood/goodness at10 and the entire conditional
ending. The available Vulgata scan jumps printed51 to54: pages52–53 have not
been read and are not claimed as service-list evidence. Palatina97/99/101/103
and Athos PlatesVI/VII were compared directly as printed texts. This is no
claim of full manuscript-photo collation or independent review.

`six-servant-policy-followup-20261104.v1.json` also corrects the earlier
Mandate6 draft's accidental use of superseded slave metadata. Both reader
editions now use servants as current DOCTRINE.md requires; bonded status and
allegiance remain explicit in notes. Prior records and wording are archived.


## Mandate 8 review and recovered Latin scan pages, 2026-11-04

The second Hilgenfeld 1873 scan,
[hermaepastorvet01hermgoog](https://archive.org/details/hermaepastorvet01hermgoog),
contains printed pages 52–53 at physical pages 71–72. These pages were visually
read and resolve the first scan's local gap. They supply bounded Vulgata evidence
for the dialogue split, Lord, brotherhood, and its shorter/different service list
and ending. This is the same edition and version tradition, not another
independent manuscript. The acquisition hash and exact scope are recorded in
`eight-service-alignment-20261104.v1.json`. The Greek body was not harmonized to
this Latin text.

`tools/hermas/review_repair_draft.py` reviews explicit standard/simplified paths,
checks their source identity and simplified base, and saves the exact request,
raw response and input hashes. It does not assume that a legacy reader slot is
the current source sequence, rewrite translations, or accept proposed wording.
The separate Azure review in `model_reviews/legacy035-20261104-r7/` accepted both
exact final Mandate 8 drafts after the recorded corrections. Earlier responses
remain intact. Model acceptance covers the supplied source and disclosures;
it does not authenticate external plates or replace independent scholarship.
The YAML records remain drafts, with nested reader/artwork migration and
publication pending. Other chapters have not inherited this review result.
