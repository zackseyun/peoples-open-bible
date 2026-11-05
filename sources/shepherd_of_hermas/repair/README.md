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


## Mandate 9 prayer/source alignment, 2026-11-04

`nine-prayer-alignment-20261104.v1.json` attaches the restored continuous Greek
in place of the retired web patch. Both English drafts retain all twelve
paragraphs. The repair restores the reflexive itself in paragraph 10 and the
working placement of anything in paragraph 1, relocates notes, and preserves the
contextual repentance choice and difficult salvation/delayed-request assertions.
The original full record and all 24 nested standard/simplified records are
preserved in `legacy36-before-prayer-alignment-20261104.v1.json`; no artwork or
reader reference was reassigned.

Lake's Athos transcription and the Vulgata/Palatina printed Latin texts expose
sister/daughter, cleansing/observing prior words, saved/live-to-God, certainly/
perhaps, and thinking/doing alternatives. A bounded enlargement of Lake's
Plate VII photographic facsimile, physical page 35 line 30, is visually
consistent with sister; this is not a full all-letter or correcting-hand
collation. The separately consulted Athanasius De decretis4.3 publisher preview
has an offspring allusion rather than the same daughter clause. It is not
counted as an exact quotation that decides this variant. Primary source
locators, acquisition hashes and limitations are in the audit.

The immutable 397-record repentance plan remains unchanged. Its validator pins
the exact complete later Mandate 9 record through
`contextual-policy-nine-followup-20261104.v1.json` before projecting the original
historical record. Tests reject source, English, notes and review-status drift.
The separate Azure model review in `model_reviews/legacy036-20261104-r2/`
accepted both exact draft files. Its scope is the supplied source/disclosures;
independent scholarship, other excerpt witnesses, reader migration and
whole-book publication remain pending.


## Mandate 10 sorrow/source alignment, 2026-11-04

`ten-sorrow-alignment-20261104.v1.json` records the complete three-section
comparison. All sixteen historical paragraphs were already in the English,
in six, one, and four reader paragraphs. The new flat drafts use six, six,
and four paragraphs per edition; this is a paragraph crosswalk, not a claim
that sixteen missing paragraphs were translated. The repair attaches the
restored continuous Greek, restores against you in ii.5, follows working now
and God where the old attached source differed, preserves the comparative
more quickly, and correctly anchors the notes. Full original records and all
22 nested standard/simplified records remain in
`legacy37-39-before-sorrow-alignment-20261104.v1.json`. Reader artwork and
legacy references were not reassigned.

Athos Plate VII and both printed Latin traditions were compared at bounded
loci. The notes expose Athos’s extra and again saves at ii.2, the working
bracketed against you and differing petition constructions at ii.5, and the
not praying/not obtaining and God/Lord differences at iii.2. The difficult
saving assertion, qualified seems to have salvation, departure warning,
prayer/altar imagery, same-prayer comparison, and final conditions remain.
The Greek body is unchanged; these editions are not extra independent
manuscript votes, and full photograph/excerpt collation remains pending.

The contextual repentance decision in ii.3–4 and the immutable 397-record
plan remain intact. An exact full-record follow-up in
`contextual-policy-ten-ii-followup-20261104.v1.json` pins the later source and
English repair before the validator projects the earlier record. Tests reject
source, English, annotation, and review-status drift.

Separate Azure reviews in `model_reviews/legacy037-20261104-r2/`,
`legacy038-20261104-r2/`, and `legacy039-20261104-r2/` accepted all six exact
draft files after the recorded corrections. Earlier raw responses are retained.
The review scope is fidelity to the supplied source and disclosures; it does
not authenticate manuscript handwriting or replace independent scholarship.
Nested reader migration, remaining witness comparisons, artwork and verified
whole-book publication are still pending.


## Complete Mandate 12 dialogue restoration, 2026-11-04

`twelve-dialogue-restoration-20261104.v1.json` records six complete historical
sections, 30 paragraphs in each flat edition. Sections iii and iv had broken
or displaced material, and vi was cut off and then misjoined to Similitude 1.
The repair restores the full virtue list, salvation warning including children
and household, anger/creation dialogue, lips/heart contrast, and final pure-heart
conditions. Sections i, ii and v were already complete in extent and receive
source alignment and notes. The normalized Greek bodies are unchanged.

Lightfoot/Harmer, Lake’s Athos diplomatic transcription, and both Latin editions
were compared at bounded loci. Palatina lacks iii through part of v.3; its
editor supplies that stretch from Vulgata, so it is not independent Palatina
evidence. The resumed text and editorial negations at printed129 are separately
documented. Leipzig-held leaves are absent from Lake’s reproduction, not lost.
The v1/v2 witness extracts preserve exact locators and source hashes, with
edition reports distinguished from fresh manuscript photograph certification.

All twelve exact flat files have model acceptance receipts: sections i–iv/vi
in r2, v in r3 after documenting the two remaining note claims. Original requests,
responses and revisions are retained; the audit verifies final file hashes.
These are model fidelity reviews, not independent scholarship. All records
remain drafts, and the immutable 397-record policy plan is preserved with exact
full-record follow-ups for iv and vi. 77 Hermas tests, 20 contextual tests,
397 policy checks, both reader guards and 62 repair hash checks passed.

All 48 original nested records and the old slot47 donor remain unchanged and
archived in `legacy41-47-before-twelve-restoration-20261104.v1.json`. Slot47
still contains displaced Mandate material and a bad join: repair Similitude 1
and migrate the nested reader before publishing this range. Historical reader
IDs and artwork have not been reassigned. The remaining source/translation
queue is 34 sections needing collation and 17 needing repaired-source comparison;
whole-book verification and publication remain incomplete.


## Similitude 1 boundary and source correction, 2026-11-04

`one-city-restoration-20261104.v1.json` records eleven complete paragraphs per
flat edition in legacy slot47. The old record began with Mandate12.vi material,
joined its pure-heart condition to the city teaching, and ended within S1.5.
Slot48 contained S1.9–11 material alongside S2 and unsupported additions.
The repair restores S1.1–2, the warning’s continuation, sufficient provision,
promises conditional on keeping commandments, buying afflicted souls, widows
and orphans, and the complete closing commands and salvation assertion.
The old48 donor still needs S2 repair and reader migration before publication.

The physical357 scan exposed an additional transcription error: printed
διανοεῖται, does not intend, had been replaced by reported Athos δύναται, can.
The printed body and Hollenberg apparatus attribution are corrected, while the
Athos alternative is disclosed. Both printed Latin editions have non cogitat.
This corrects transcription of the edition; it is not a newly chosen manuscript
reading. Other normalized bodies, including Mandate12.vi, are unchanged.
Bounded notes expose editorial brackets, actions/possessions, wishes/comes,
city movement, God/Lord and cheerful/holy differences. Latin traditions remain
distinct from Greek manuscripts. The Bodmer holding catalogue confirms its
Hermas text is Visions, despite a secondary guide’s Similitudes label; it is
not counted as S1 evidence. Leipzig photograph collation remains pending.

The full old47/48 records, raw357 and normalizedS1 are archived in
`legacy47-48-before-city-restoration-20261104.v1.json`; all16 nested files and
slot48 remain unchanged. The earlier M12 donor guard now compares that exact
original record to this subsequent archive and requires the specific S1 repair,
rather than exempting arbitrary future changes. All12 final M12 review input
hashes still match their receipts. No397policy record contains flat047.

Separate Azure model review `model_reviews/legacy047-20261104-r1` accepts both
exact final drafts against the supplied source and located evidence. The
receipt and raw response are retained; independent scholarly and manuscript
review remain pending. 79 Hermas tests,20 contextual tests,397policy checks,
both reader guards(439/395 YAML files),and63 repair hash checks pass. The
remaining earlier queue is34 sections needing collation plus16 needing
repaired-source comparison. Full-book verification and publication remain open.


## Similitude 2 and three early papyrus comparisons, 2026-11-04

`two-elm-vine-restoration-20261104.v1.json` records ten complete historical
paragraphs per flat edition in slot48. The old record mixed S1 luxury teaching
with S2.4’s conclusion and omitted S2.1–4’s opening dialogue/comparison; its
second paragraph contained S2.5–8 until a cutoff. Slot49 contained S2.8–10
before S3/S4. Complete S2 is now in48, with faithful wage, without doubting,
and abundant with God choices retained and notes correctly anchored. The old
full48/49 records and28 nested files are archived; donor49 and all nested files
remain unchanged pending their explicit next repair and reader migration.

An enlarged physical361/printed345 scan reversed a mistaken earlier repair:
the print reads souls, ψυχὰς, not prayers. `earlier-gaps-20261103.v1.json`’s
contrary historical claim is superseded by this located evidence; its original
record is preserved. P.Oxy1172 line40 prints psi outside brackets; Michigan
supplies psi, and Berlin reports only a trace. Those are different evidence
strengths, not three complete preserved votes. Palatina printed139 has animas.
Raw361 is corrected; other raw source bodies remain unchanged.

New primary editions acquired from public scans, with hashes in the witness
extracts, supply bounded comparisons for Berlin5513 and Oxyrhynchus1172.
Together with Michigan917 they support the singular understanding/service
construction in the closing explanatory sentence. The selected normalized
source follows Michigan there, retaining its supplied letters in brackets.
Berlin lacks good, and Oxyrhynchus has a damaged/corrected object; the former
1891 plural think/do reading and Athos’s reported omission remain disclosed.
This is the twelfth bounded selected locus across eleven override units, not
an exhaustive critical edition or new manuscript-photo authentication. The
raw1891 closing text remains intact. Other early-papyrus differences in Lord/
God, above, resting/relying, confession and ministry are exposed in the notes.
Both Latin versions were compared; the Vulgata editor’s longer Palatina supply
is not counted as independent Vulgata manuscript evidence.

The separate Azure r1 review caught inherited added ascent in no power to go
up above; both drafts now preserve no power above. Fresh r2 review accepts
both exact final files, with immutable requests, responses and evidence hashes.
All101 tests(81Hermas+20contextual),397policy checks,439/396 YAML guards and
64repair source/payload/base checks pass. Flat048 is not a member of the397
policy plan. The S1 donor guard now requires the exact archived original48 and
the specific complete S2 successor; its checks were not broadly disabled.

Independent scholarship, remaining witness/photo collation, nested reader and
artwork migration, and whole-book publication remain incomplete. The earlier
queue is34 sections needing source collation and15 needing repaired-source
comparison. Next repair the S2-tail/S3/S4 compound in legacy49.


## Complete tree parables in legacy reader49, 2026-11-04

`three-four-trees-restoration-20261104.v1.json` records complete S3(3paras) and
S4(8paras) in each flat edition. The old49 record began with displaced S2.8–10,
then contained all S3 and only S4.1–4opening. S2 is already restored in48;
S4’s actual missing4tail–8 now includes burning and its two stated reasons,
repentance, many activities, both request outcomes, pure-mind condition and
the final fruit-bearing promise. S3was already complete in extent; its full
source collation remains queued. The full old49 and24 nested files are
archived in `legacy49-before-trees-restoration-20261104.v1.json`; nested reader
and artwork migration remain pending.

The unchanged S4reader identity anchors a complete chronological S3/S4 source.
`identity_anchor_unit_id` explicitly declares the non-leading anchor. The review
tool accepts this only with a unique anchor in unique, contiguous, historically
ordered spans and exact normalized source offsets/hashes. Tests reject absent
or wrong anchors, duplicates, reordering, sequence drift and source hash drift.
The earlier implicit-leading contract still applies when no anchor is declared.

A thirteenth bounded selection across twelve override units omits the1891
bracketed those-who-are-least conjecture in S4.3, following the shorter Michigan
reading, with qualified Berlin comparison. Michigan’s supplied letters and
Berlin’s largely supplied/different continuation are documented; Palatina’s
least wording and reported Athos repetition remain exposed. Raw1891 remains
intact. Other difficult differences, including Michigan invisible versus working
manifest at4.4 and to-all versus all at4.2, are disclosed without harmonization.
The complete Vulgata continuation was also checked: it omits the negative
request outcome retained in Greek/Palatina and distinguishes God/Lord at4.7.
Version traditions and edition reports are not extra independent manuscript
votes or new photograph certifications.

Both initial drafts passed Azure r1; completing the Latin continuation changed
notes, so fresh r2 accepted the exact final files against evidencev2. All raw
requests/responses are retained, and evidencev1 remains unchanged for r1.
Independent scholarship and full manuscript/excerpt collation remain pending.
All103 tests(83Hermas+20contextual),397policy checks,439/397 YAML guards and
65source/payload/base checks pass. No397policy record contains flat049; current
contextual repent/serve terminology is preserved. The previous S2donor49 guard
now requires exact archived-original equivalence and the specific S3/S4successor,
rather than exempting arbitrary changes. Remaining earlier queue:34source
collation+14repaired-source comparison=48. Whole-book publication is unfinished.
# Similitude 5 fasting and vineyard restoration, 2026-11-04

`five-fasting-restoration-20261104.v1.json` records complete working standard
and simplified drafts of S.5.i (five historical paragraphs) and S.5.ii
(eleven) in unchanged legacy reader 050, ID HERM.S.5.ii. The source spans
remain in chronological order, with the explicit non-leading S.5.ii identity
anchor. Current source sequences 54–55 are not reader filenames.
`legacy50-before-fasting-restoration-20261104.v1.json` preserves the entire
old flat record and twelve unchanged nested records. The six old paragraphs
are mapped before their malformed narrative joins are removed.

The repair restores the mountain/thanksgiving/early question, complete fasting
teaching and continuous vineyard story. The old English jumped from I.3 to
II.4 and from II.5 to II.11, with an unsupported narrative bridge. Restored
conditions include ethical abstinence, promised freedom, extra work, shared
inheritance, food distribution and the fellow servants’ prayer for favor.

One further bounded source selection restores Hermas’s reply in I.3 from
Michigan917, Bonner1934 printed46, papyrus5 lines11–14. Palatina printed143
directly corroborates its sense; Vulgata printed76 omits it. Bonner’s reported
Hamburg/Coptic support remains attributed. The damaged final divine abbreviation
is explicitly marked and expanded; raw1891 is unchanged. This brings the
selected total to fourteen loci in thirteen override units. No other S.5.i/ii
source wording is silently harmonized. `five-fasting-witness-extracts-20261104.v1.json`
records the bounded primary edition comparisons, including Michigan’s missing
leaf across the central parable and wholly supplied instructions, which cannot
be counted as preserved ink or witness omissions.

Both records remain drafts pending independent scholarly review. Nested reader
migration, artwork and publication remain unfinished. The earlier comparison
queue now contains 34 source-collation sections and 12 repaired-source comparison
sections (46 total); these draft repairs do not certify exhaustive collation.


The exact final050files passed a fresh Azure model review (both accept), with
request/raw response/review/receipt retained in `model_reviews/legacy050-20261104-r1`.
All105tests (85Hermas+20contextual),397policy checks,439/398YAML reader guards
and66source/payload/base hash checks pass. No397policy record contains flat050.
Model acceptance is limited to the supplied working source and attributed
evidence; it does not replace independent scholarship or photo authentication.

## Similitude5.iii–iv fasting and explanation, 2026-11-04

`five-fast-explanation-restoration-20261104.v1.json` restores all nine III and
five IV historical paragraphs in standard and simplified flat reader051,
retaining HERM.S.5.iii and chronological source spans56–57. The old flat record
and ten unchanged nested records are preserved in
`legacy51-before-fast-explanation-20261104.v1.json`, with a five-paragraph
crosswalk. The source bodies remain unchanged.

The old reader joined III.2 to III.7, invented instructions/prudence in place
of humility, and joined III.9’s blessing to IV.4’s understanding request.
The repair restores command keeping/enrollment, comparative glory, extra
service, the bread-and-water fast, calculation and giving of the saved food
expense, recipient prayer, complete asking promise, strong no-question rebuke
and Hermas’s objection. It preserves the tension between asking and the rebuke
without harmonizing it away.

`five-fast-explanation-witness-extracts-20261104.v1.json` records bounded direct
comparison of LH1891physical365–367, Michigan917 printed49–56, Vulgata79–82
and Palatina147–151. Michigan partly corroborates the existing III.2 supplied
passage and III.9 asking conjecture. Actual differences in written/heard,
prayer wording, without-ceasing/without-hesitation and holy/glorious angel are
disclosed. Original photos and primary excerpt witnesses remain pending;
versional/editorial supplies are not counted as preserved ink. No new source
selection was made; totals remain14loci13overrideunits.

Both files remain drafts. The earlier queue is now34source-collation plus
10repaired-source-comparison sections (44total), with broader manuscript
comparison, independent scholarship, nested readers, artwork and publication
unfinished.

The final051files passed a fresh Azure r2review (both accept). Original r1
request/response/review/receipt preserve its footnote-attribution finding; r2
records the corrected exact files. All107tests(87Hermas+20contextual),397policy
checks,439/399YAML reader guards and67source/payload/base hash checks pass.
Flat051 is not in the397contextualpolicyplan. These are model fidelity checks,
not independent scholarship or whole-book completeness certification.

## Similitude5.v–vi and Hamburg evidence, 2026-11-04

`five-servant-explanation-restoration-20261104.v1.json` restores all five V
and eight VI historical paragraphs in flat standard/simplified reader052,
retaining HERM.S.5.v and chronological source spans58–59. The old flat and
eight unchanged nested records are preserved in
`legacy52-before-servant-explanation-20261104.v1.json`, including a four-paragraph
crosswalk and neighbor053 hash. The actual omitted extent was V.1ending–5 and
VI.1–2opening; VI.2tail–8 was already present and is now aligned in full.

The restored text retains the parable identities, servant/Son question,
disputed working negative, full authority statement, creator-Spirit wording,
flesh service/partnership and conditional reward. The source bodies remain
unchanged. `five-servant-witness-extracts-20261104.v1.json` records direct primary
edition comparisons: LH1891physical367–368, Michigan printed56–59, Vulgata82–85
and Palatina151–159. Both Latin versions support the negative in VI.1;
reported Athos lacks it, and Michigan physically loses fifteen lines there.
Vulgata’s additional son-as-Spirit identification is absent from Palatina and
the working Greek. The Latin created-first wording differs from Greek
created-all-creation. These alternatives are exposed without doctrinal
harmonization or treating damaged manuscript gaps as omissions.

`hamburg-parchment-comparison-20261104.v1.json` upgrades the previously
reported Hamburg evidence to a bounded directly consulted1924primary printed
edition: Wessely, PatrologiaOrientalis18.3, printed479–481. It corroborates
the earlier restored fasting reply and shorter S4.7 passage. The inventory
now identifies Hamburg Bibliothekgr24 as parchment, preserving the old alias
without confusing it with documentary P.Hamb.I24 or adding a witness count.
Printed recto fruit-promise coverage is recorded even though the catalogue’s
short description ends at S4.7. No earlier accepted YAML or source body was
changed by this corroboration. Original parchment photos and1909comparison
remain pending; printed letters/supplies are not universally preserved ink.

No source selection was added: totals remain14loci13overrideunits. The earlier
queue is now34source-collation plus8repaired-source-comparison sections
(42total). Draft repair, bounded comparison and model review do not complete
independent scholarship, nested reader/artwork migration or publication.

Final052files passed fresh Azure r2review (both accept), preserving r1 with its
two simplified-clause findings and all raw requests/responses/receipts. All109
tests(89Hermas+20contextual),397policy checks,439/400YAMLreader guards and68
source/payload/base hash checks pass. After the two-clause simplified revision,
the targeted tests/hash/reader checks passed again. Flat052 is not a member
of the397contextualpolicyplan. Exact earlier049/050/051accepted files remain
unchanged. Model review does not certify independent scholarship or the
whole-book edition.

## Similitude5.vii flesh and healing alignment, 2026-11-04

`five-flesh-healing-alignment-20261104.v1.json` aligns the standard reader053
and adds a complete simplified draft to all four historical paragraphs,
retaining HERM.S.5.vii and current source sequence60. The old English already
contained the complete passage across four differently split reader
paragraphs: no new chapter or passage extent is claimed. The full old flat
record and eight unchanged nested records are preserved in
`legacy53-before-flesh-healing-20261104.v1.json` with the paragraph crosswalk.

The repair retains the established clean/clean repetition and working flesh
warning, removes a misattached previous-rendering note, and replaces vague
variant notes with bounded primary evidence. Michigan printed59 partly
corroborates flesh in the second warning, against the suggested Spirit
emendation. Vulgata printed85 has both body and HolySpirit, with other forms
reported in its apparatus; Palatina printed159 has body. The full conditional
healing promise remains, with explicit differences between Michigan’s shorter
wording/pantos, Vulgata’s Almighty and Palatina’s perhaps. Brackets, the dagger,
negatives and original source bodies remain unchanged.

`five-flesh-healing-witness-extracts-20261104.v1.json` records LH1891physical368–369,
Michigan printed59–60, Vulgata85–86 and Palatina159–161. Direct manuscript
photos, remaining versions/excerpts and broader collation remain pending.
The source-collation queue deliberately retains S5.vii; bounded draft
availability is recorded separately. Counts remain34source-collation plus
8repaired-source-comparison sections (42total),14selectedloci13overrideunits.
The old052neighbor053 guard now checks the exact old053 archive hash and the
specific new S5.vii alignment identity; it does not broadly exempt changes.

The exact final053files passed fresh Azure r2review (both accept); r1’s copied
simplified-idiom-note finding and both raw review receipts are preserved.
All111tests(91Hermas+20contextual),397policy checks,439/401YAML reader guards
and69source/payload/base hash checks pass. Targeted tests were rerun after
the note-only correction. Flat053 is not in the397contextualpolicyplan.
No source extent, whole-book completeness or independent scholarly review
is inferred from these checks.

`six-death-renewal-restoration-20261104.v1.json` restores the actual English
omission at S.6.ii.1 after the first question/answer through the end of ii.3.
Standard and simplified reader055 now contain all six historical paragraphs;
ii.4–6 already existed and are not counted as new extent. Reader identity
HERM.S.6.ii remains; its historical source sequence is62. The complete prior
flat record, unchanged nested records and neighbor hashes are archived.
The normalized source is unchanged. Flat054 alignment remains pending.

The missing angel explanation, living God's commandments, no repentance of
life, name-blasphemy and life-is-death statements are restored alongside the
second group's hope of renewal and the explicit eternal destruction contrast.
Earlier very bitter look, corruption, final at ease wording, and the
contextual repentance choice remain. The immutable397record terminology
plan is preserved with a complete-record, separately pinned historical
follow-up for055; changed source, English or notes cannot pass that pin.

`six-death-renewal-witness-extracts-20261104.v1.json` records direct printed
comparison of LH1891physical370–371, Michigan printed63–67, Vulgata88–89 and
Palatina163–165. Notes disclose Michigan's different first verb and added
description, active blasphemy accusation and shorter death formula. Palatina's
printed some-to-death is an editorial addition absent its codex and cannot
be counted as independent manuscript ink. Critical brackets and damaged or
supplied letters remain distinguished. No new source selection is made.
Seven sections now await repaired-source comparison, alongside34sections
still requiring broader source collation. All draft/review/migration and
publication requirements remain open until independently verified.

The exact final055 pair passed Azure r1 review (both accept), with request,
raw response and input/evidence receipts retained. All114targeted tests
(94Hermas+20contextual),397policy checks,439/402YAML corpus guards and
70payload/source/base checks pass. Model acceptance does not certify
independent scholarship, complete collation, reader migration or publication.

`seven-household-restoration-20261104.v1.json` reunites S.7 into complete
standard and simplified reader059, preserving HERM.S.7/current sequence66.
Old059 stopped mid-paragraph4. Read-only donor060 already contained4tail
through5opening under S.8.i; the genuinely missing English starts with
beneficial affliction in5 and continues through7. Full old059/nested and
donor060 records are archived. Normalized Greek and donor060 are unchanged;
the latter must be migrated before publication to avoid duplicate material.
The paragraph3 contrast now explicitly says while you are at ease,
correcting the old ambiguous being steadfast.

All seven paragraphs retain the non-immediate-forgiveness question and
negative reply, afflicting one's own soul, endurance/clean-heart conditions,
healing, advance warning, lesser affliction, restoration, children/household,
and the conditional closing promises. Misattached previous-rendering notes
are archived rather than attached to unrelated new words. The397record
terminology plan stays unchanged; the later complete-record repair has a
separately pinned historical follow-up that rejects altered English/notes.

`seven-household-witness-extracts-20261104.v1.json` records direct LH1891
physical374–375, Michigan printed77–83, Vulgata94–97, Palatina171–173 and
Sinaiticus Project global66.1–6 comparison. Michigan partly corroborates
immediately and healing previously supplied in the1891 edition; no new
normalized selection is made. Both Latin versions have perhaps rather than
surely. Easily/whole/God retain disclosed working brackets; return to place
in Michigan/Sinaiticus/Latin differs from working house. Palatina omits the
first explicit household-if clause; it is retained in the working English.
Sinaiticus supplies, corrected readings and physical gaps are distinguished: its
fragment cannot attest the creator/healing/clean-heart stretch or unpreserved
closing paragraph. Six sections remain in repaired-source comparison and34
in broader source collation. Independent review, other witnesses, nested
reader migration and whole-book publication remain pending.

The final059pair passed fresh Azure r2 review (both accept). R1 accepted
the standard but requested an explicit advance-warning purpose in simplified5;
that link is now restored, with the original finding/raw receipts retained.
All117tests (97Hermas+20contextual),397policy checks,439/403YAMLguards and
71payload/source/base checks passed. After the one-sentence correction, the
three targeted chapter checks and71hash checks passed again. These checks do
not establish independent scholarly review or whole-book publication.

`eight-willow-restoration-20261104.v1.json` restores the complete18paragraphs
of S.8.i in standard and simplified reader060, keeping HERM.S.8.i/current
sequence67. The actual new extent is I.1 and I.15–18; I.2–14already existed.
The misassigned S.7.4–5opening is removed from060 and remains in complete059
and the full historical archive. All thirteen rod groups I.6–18remain
distinct, including proportions, splits, shoots, fruit and the final joy.
Old060/nested records and unchanged061neighbor hashes are archived.

`eight-willow-witness-extracts-20261104.v1.json` records direct LH1891
physical375–377, Michigan printed83–88, Berlin6789BKTprinted17–20,
Vulgata97–99, Palatina173–177 and Sinaiticus Project global67comparison.
The notes distinguish first hands, corrections, supplies and physical gaps.
Sinaiticus has opening large without supply/correction markup, but branch
handing in2is a corrector addition; paragraph15green is an S1correction.
Vulgata’s printed paragraph10is supplied from Palatina, not independent
Vulgata manuscript evidence. Palatina omits several groups; those are not
silently inserted into that version. Berlin’s paragraph10opening is mostly
supplied across damage, not intact early ink. Full Greek working body,
critical bars/brackets and14selectedloci/13overrideunits remain unchanged.

The397record terminology plan is unchanged; a separately pinned complete
record follow-up preserves060’s former judgment in its actual S7context.
The preceding059donor guard now matches the exact old060archive hash and
the specific new S8i repair identity; accepted059r2input hashes stay exact.
Five sections remain in repaired-source comparison;34still require broader
source collation. Independent scholarship, other witnesses, nested reader
and artwork migration, and whole-book publication remain pending.

The exact final060 pair passed Azure r1 review (both accept), with raw
request/response and input/evidence hash receipts retained. All120targeted
tests (100Hermas+20contextual),397policy checks,439/404YAMLcorpus guards
and72payload/source/base checks pass. This does not certify independent
scholarship, full manuscript collation, reader migration or publication.

`eight-crowns-planting-alignment-20261104.v1.json` aligns complete S.8.ii
in standard reader061 and adds the simplified flat draft, preserving
HERM.S.8.ii/current sequence68. All nine historical paragraphs already
existed; no missing chapter or paragraph extent is claimed. Small corrections
render II.2singular a seal, II.4bracketed white, and II.6explicit departure.
The original flat and two unchanged nested records are fully archived.
Old notes stacked at the end of9are replaced by anchored source disclosures.

`eight-crowns-witness-extracts-20261104.v1.json` records LH1891physical377–378,
Michigan printed88–92, Vulgata99–101, Palatina177–179 and Sinaiticus Project
global68.1–5comparison. Sinaiticus and Michigan corroborate white in4against
the older edition’s bracket and reported Athos omission; seals retain their
working singular/plural distinction. Sinaiticus breaks within5and cannot
attest the subsequent warning/planting/hope. Michigan omits the full repeated
if-anyone clause and second careful instruction, while the working English
retains them; its Lord-of-the-tree differs from working Creator. Both Latin
versions preserve the conditional altar warning. Palatina omits Hermas’s
question about the dry rods. All these differences remain disclosed.

The Creator’s desire for all branch recipients to live stays distinct from
the shepherd’s hope for the greater part, the moisture/planting condition
and possible failure. The normalized Greek is unchanged, including the
critical bracket;14selectedloci/13overrideunits remain unchanged. Flat061
is not in the397record contextual terminology plan. The old060neighbor061
guard is adapted only through the exact archived old061hash and specific
new S8ii alignment identity; accepted060r1inputs remain exact. Four sections
remain in repaired-source comparison, alongside34requiring broader source
collation. Other witnesses, independent scholarship, nested reader/artwork
migration and whole-book publication remain pending.

The exact final061 pair passed Azure r1 review (both accept), with raw
request/response and input/evidence hash receipts retained. All122targeted
tests (102Hermas+20contextual),397policy checks,439/405YAMLcorpus guards
and73payload/source/base checks pass. These do not certify independent
scholarship, exhaustive manuscript collation, migration or publication.

`vision-nine-ten-boundaries-20261104.v1.json` reunites Vision 3.ix in017
and separates 3.x in018, ten historical paragraphs each in both editions.
The older017ended mid-sentence;018contained the rest of ix and all of x.
All of that English already existed across the two slots: this is boundary
repair, not newly recovered whole-book extent. Full prior flat history and
18unchanged nested records are archived. Raw328’s first tower noun is
corrected from OCR πύργου to printed πύργον; no manuscript selection is
added. The IXsource body remains unchanged, including printed παῆναι.

`vision-nine-ten-witness-extracts-20261104.v1.json` records LH1891pages326–328,
Lake1907PlateIII transcription (same Athos codex), Sinaiticus Project17/18,
Vulgata25–28 and Palatina51–57. Notes distinguish first hands and correctors,
the bracketed goods adjective and among-them/yourselves ambiguity, Palatina’s
ask-me-later/believe variants and Vulgata’s alternative rebuke. Sinaiticus’s
sufficiency sentence in18.8is a caaddition, not intact first-hand evidence.
Polite sir addresses the young man; divine Lord remains distinct.

Fresh final017r2and018r2Azure reviews accept both editions after corrections
to simplified training/purpose/scope, intensive cheerfulness and the negative
expectation of the stronger-revelations question. Exact inputs/evidence hashes
match the receipts. All124tests (104Hermas+20contextual),397policy checks,
439/407YAMLguards and75payload/source/base checks pass. Two sections remain
in repaired-source comparison (V3iii,M4i), alongside34broader-collation flags.
These are not counts of known missing chapters. Independent scholarship,
other witnesses, nested reader/artwork migration and publication are unfinished.

`bodmer38-availability-20261104.v1.json` identifies the official Bodmer Lab
52-canvas manifest and the DCLP metadata record. DCLP’s edition element is
empty, so the catalogue’s digital-text link must not be described as an
acquired transcription. Images and the1991edition still require passage-level
comparison; no Bodmer reading is selected on the basis of this availability check.

`vision-three-tower-alignment-20261104.v1.json` aligns complete V.3.iii in
standard011 and adds five paragraphs in simplified011. All five historical
English paragraphs already existed; no new whole-book extent is claimed.
The source attached to the older reader still contained a printer footer,
although the normalized source had already removed it. Raw322/printed306
now correctly reads imperative ἐπερώτα and ἄξιόν με ἡγήσω, replacing corrupt
OCR. The normalized body changes only those printed readings, not a newly
selected manuscript locus. The prior flat record/adjudications and ten
unchanged nested records are archived.

`vision-three-tower-witness-extracts-20261104.v1.json` records LH1891pages321–322,
AthosLake1907PlateIIlines27–36, Sinaiticus Project11.1–5, Vulgata16–17and
Palatina35–37. The cheerful/these-things supplement remains marked in English;
the note explains that two English bracket spans represent one Greek span
because the hearing verb itself is outside it. Conditions for rejoicing,
completed revelations, rebuke, the Church’s self-identification, imperative
asking, limits on disclosure and both past/future saved-through-water verbs
remain. God/Lord, honorifying/knowing, the Palatina alternative to the rebuke
and Vulgata’s added scriptures phrase are disclosed rather than harmonized.

The397record policy plan is unchanged. A separately SHA-pinned complete
record follow-up preserves011’s historical contextual repentance judgment,
reader note and terminology metadata. Fresh Azure011r1accepts both editions;
input and evidence hashes match. All126tests (106Hermas+20contextual),397policy,
439/408YAMLguards and76payload/source/base checks pass. One earlier repaired
comparison item remains (M4i), plus34broader-collation flags. Independent
scholarship, other witnesses, nested reader/artwork migration and publication
remain unfinished.

Bodmer canvas017’s info.json resolves, but two image-size requests returned
HTTP500. No new Bodmer image, reading or transcription is claimed. Its resolved
manifest and catalogue metadata remain useful access records; actual passage
comparison still requires the images or the1991edition.

`four-reception-alignment-20261104.v1.json` expands the earlier bounded
M.4.i alignment into eleven numbered paragraphs per English edition and
adds simplified029. All eleven historical paragraphs already existed in
six reader paragraphs; neither new source nor new whole-book English extent
is claimed. Quote boundaries are clarified, source-supplied and/wife are
bracketed, and the full old record, twelve nested records and prior policy
follow-up are archived. Normalized Greek and14loci/13overrideunits are unchanged.

`four-reception-witness-extracts-20261104.v1.json` records LH1891pages336–337,
AthosPlateVlines15–32, Sinaiticus29.1–11, Vulgata39–40andPalatina77–81.
Remember-wife/Lord, wickedness/fornication corrections, damaged letters,
frequency/duration, image-making/imitation and the first-hand/corrector
healing difference are disclosed. Ignorance/knowledge, continued sin,
repentance/return, required reception, one repentance, no remarriage and
both-sex application remain; the closing states healing ability rather
than importing Vulgata’s promised remedy.

The earlier029alignment contract is checked against its exact archived
record; the live full-record terminology follow-up is separately pinned.
The397record plan remains unchanged. Azure029r1found both reader texts
faithful but caught inherited metadata choosing slave and misattributing it
to current policy. Current decision records now choose servant and retain
bonded-status nuance; superseded metadata remains archived. Fresh029r2accepts
both editions, with exact input/evidence hashes verified. All128tests
(108Hermas+20contextual),397policy,439/409YAMLguards and77payload/source/base
checks pass; the five focused Mandate4tests and hash/policy checks were rerun
after metadata correction.

The earlier repaired-source comparison queue is now empty. The34broader
source-collation flags remain, including chapters that already have bounded
complete drafts. This does not establish exhaustive manuscript collation,
independent scholarship, reader/artwork migration or whole-book publication.

`four-understanding-alignment-20261104.v1.json` aligns M.4.ii in four
numbered paragraphs and adds simplified030. All four historical paragraphs
already existed; normalized source and English extent are unchanged. The
supplied man is visibly bracketed. Bounded LH1891, Athos Plate V,
Sinaiticus30 and Vulgata/Palatina comparisons disclose Lord/God,
hardened/blinded, the supplied noun, lavish good, the difficult soul verb,
and Harmer’s then-I-do-not-know conjecture against so-that-I-may-know.
Sinaiticus30.3 is damaged and incorporates supplied later material; it
cannot be counted as complete evidence for the disputed conjunction or II.4.

The full old flat record, eight nested records and prior terminology
follow-up remain archived. The397-record plan is unchanged, with an exact
full-record follow-up pin. Azure030r1accepted the reader texts but requested
a simplified lexical-record correction: many and various now matches its
reader wording. Fresh030r2accepted both editions. A copied Athos source
method’s plate locator was then corrected from III to V;030r3accepts both
editions with current input/evidence hashes verified. All130tests
(110Hermas+20contextual),397policy,439/410YAML guards and78payload/source/base
hashes passed; two focused tests and78hashes passed after the metadata fix.
The34broader source-collation flags remain, including M.4.ii. Nested reader,
artwork, independent scholarship, other witnesses and publication remain
unfinished.

`opening-alignment-20261104.v1.json` aligns all nine V.1.i paragraphs in
standard001 and adds complete simplified001. All nine were already present
in the restored standard draft; no new whole-book extent or source-body
change is claimed. Eight orphan numeric note markers now have live notes,
and Rhoda, Cumae and the negative-question variant receive bounded notes.
The full old flat record, six nested records and prior terminology follow-up
are archived. The397-record plan remains unchanged; the opening follow-up
now pins the entire later record before projecting the original judgment.

`opening-witness-extracts-20261104.v1.json` records LH1891physical313–314,
Athos Plate I, Sinaiticus1.1–9, Vulgata printed2–4 and Palatina printed3–9.
Names, place/way, goddess/daughter/lady, the negative-question correction,
heavenly honor, wealth/vices and healing/forgiveness differences are
disclosed. The working future will repent is now a statement, matching
the printed working edition. Athos will greatly regret and the different
Latin formulations remain explicit alternatives. Neither the difficult
hopelessness statement nor the promise to the whole household and all the
holy ones is removed. This choice does not claim that manuscript punctuation
independently settles the rhetorical interpretation.

Azure001r1caught a shared terrain-description defect: cut off by the waters
implied isolation, whereas the Greek describes ground broken by water.
Both editions now say broken up by the waters; Vulgata and Palatina also
describe damaged terrain. Fresh001r2accepts both editions, with current
input/evidence hashes verified. All132tests (112Hermas+20contextual),397policy,
439/411YAML guards and79payload/source/base hashes passed. The two opening
tests,79hashes and397policy checks passed again after the terrain correction.
Bodmer availability is not counted as an acquired reading. Other witnesses,
full collation, independent scholarship, nested reader/artwork migration and
publication remain unfinished. The34broader collation flags are unchanged.

`first-elder-alignment-20261104.v1.json` aligns V.1.ii in four numbered
paragraphs and adds complete simplified002. All four paragraphs were already
present in standard English. Greetings, chair, atonement, completed sins,
older woman, wool, temperament and spirit notes are now attached to their
own clauses instead of being clustered after self-controlled Hermas.
The old flat record, stale review claims and eight nested records are
archived. Edition-specific lexical and theological decisions now match the
reader text, including servant and the source’s completed-sins modifier.

`first-elder-witness-extracts-20261104.v1.json` records LH1891physical314–315,
Athos Plate I, Sinaiticus2.1–4, Vulgata printed4–5 and Palatina printed9–11.
The Sinaiticus first hand’s rejoicing and absent snowy differ from ca’s
weeping and added snowy. Its added reproach phrase contains supplied letters.
The Latin perhaps differs from working surely, and Palatina’s you-are-full
words are explicitly an editorial supply absent from the reported codex.
The difficult atonement questions, tested spirit desiring evil, and complete
every/all virtue scope remain. No source-body change or new manuscript
selection is made; the34broader collation flags remain.

Azure002r1accepts both editions with input/evidence hashes verified.
All114Hermas tests pass; the unchanged20contextual tests passed at the
opening checkpoint. The397policy check,439/412YAML guards and80payload/source/base
hashes pass. Other witnesses, original photographs, independent scholarship,
nested reader/artwork migration and publication remain unfinished.

`first-household-alignment-20261104.v1.json` aligns V.1.iii in four
numbered paragraphs and adds simplified003. All four paragraphs already
existed. Raw315 and normalized Greek now correctly read printed ὑμᾶς, you,
where the import had ἡμᾶς, us. The English follows the printed working
edition; actual Sinaiticus ca us remains a disclosed variant. The complete
old flat record, eight nested records and old raw315/normalized text are
archived. A separately SHA-pinned full-record follow-up preserves the
original397-record terminology decision without altering that plan.

`first-household-witness-extracts-20261104.v1.json` records LH1891physical315–316,
Athos Plate I, Sinaiticus3.1–4, Vulgata printed5–7 and Palatina printed11–17.
Orphan notes b–g and misplaced a are repaired. The household’s correction,
all past evils, daily righteous word, conditional whole-heart repentance,
plural books with the holy ones, terrifying/remembered words, full creation
recital, moving/leveling and final statutes/faith condition remain. Differences
in pronouns, conditionality, book number, remembered words and invisible
power are disclosed, not harmonized.

D’Abbadie1860’s Ethiopic edition was acquired. Its Latin rendering of V.1.iii
(printed114–115, physical126–127) is now also compared. It retains the
repentance condition, but has singular book, forgiveness versus healing,
a different creation/purification recital and hoped-for hope language.
Its proposed foundation reading is an editorial change, not preserved
Ethiopic words. This is expressly evidence through the printed Latin
translation, not direct Geʿez or manuscript-photo collation. The complete
Vision I Latin rendering was visually read at physical125–127; integrating
the remaining opening/closing notes is pending.

Azure003r1accepted standard and requested two simplified corrections:
the corrective purpose of anger, and fondness explaining non-admonition.
Those relationships are explicit now. Fresh003r2accepts both editions,
including the added Ethiopic evidence; exact input/evidence hashes match.
All136tests (116Hermas+20contextual),397policy,439/413YAML guards and81
payload/source/base hashes passed before the final revisions. The three
focused household tests,81hashes and397policy passed after them. There
are still34broader collation flags. Other witnesses, direct photographs,
independent scholarship, nested reader/artwork migration and publication
remain unfinished. Further Bodmer image requests returnedHTTP500; no
Bodmer image, transcription or reading is claimed.

`first-departure-alignment-20261104.v1.json` aligns V.1.iv in three
numbered paragraphs and adds simplified004. All three paragraphs already
existed; no source body or whole-book English extent is added. The misplaced
last/earlier-things note is now attached to that distinction rather than
the chair. The full old flat record and six nested records are archived.

`first-departure-witness-extracts-20261104.v1.json` records LH1891physical316,
Athos Plate I, Sinaiticus4.1–3, Vulgata printed7, Palatina printed17, and
d’Abbadie1860’s Latin-rendered Ethiopic printed115. Sinaiticus first hand
lacks the chair-lifting clause and the please/but-earlier phrase; ca and S1
respectively add them. The working fuller narrative is retained with those
corrections distinguished. Four chair-carriers and two woman-carriers,
later-pleasing/earlier-harsh, the two response groups, elbows, east, cheerful
departure and courage exhortation remain. The Latin versions’ shoulders/
with-their-hands wording and the Ethiopic rendering’s different farewell
are disclosed, not substituted. No direct Geʿez or all-letter manuscript
photograph collation is claimed.

Azure004r1accepts both editions, with current input/evidence hashes verified.
All119Hermas tests,397policy,439/414YAML guards and82payload/source/base
hashes pass; the unchanged20contextual tests passed at the household
checkpoint. The34broader collation flags remain. Other witnesses, independent
scholarship, nested reader/artwork migration and publication remain unfinished.

`second-book-alignment-20261104.v1.json` aligns V.2.i in four numbered
paragraphs and adds simplified005. All four paragraphs already existed;
source body and whole-book English extent are unchanged. Notes formerly
clustered after the snatched book now accompany Cumae, spirit, kneeling,
little book, copying and elect. The full old flat record and eight nested
records are archived.

`second-book-witness-extracts-20261104.v1.json` records LH1891physical316,
Athos Plate I, Sinaiticus5.1–4, Vulgata printed8, Palatina printed17–19, and
d’Abbadie1860’s Latin-rendered Ethiopic printed115–116. Cumae/villages,
God/Lord, last-year/before, the absent first-hand take-and-return reply
added by ca, and copying formulations are disclosed. Vulgata’s withdrawing
is an editorial emendation against reported sitting; the continuous-script
explanation and the Ethiopic translator’s illiteracy alternative are not
treated as an explicit cause in the selected Greek. The causal worthiness/
former-sins clause, entire letter-for-letter copying, and unidentified
snatching agent remain. No direct Geʿez or original-photo collation is claimed.

Azure005r1accepted standard and caught an omitted spatial detail in
simplified: in front of me is now restored. Fresh005r2accepts both editions;
current input/evidence hashes match. All121Hermas tests,397policy,439/415YAML
guards and83payload/source/base hashes pass; two focused tests and83hashes
passed after the spatial fix. The unchanged20contextual tests passed at the
household checkpoint. The34broader collation flags remain. Other witnesses,
independent scholarship, nested reader/artwork migration and publication
remain unfinished.

`second-warning-alignment-20261104.v1.json` aligns V.2.ii in eight numbered
paragraphs and adds simplified006. All eight paragraphs already existed.
The printed verb in II.8, ἀπεγνωρίσθαι, had lost ρι in the import; raw317,
normalized source and attached source now match the print, Athos and Sinaiticus.
This is a transcription correction, with zero new manuscript-selection loci.
The full old flat record, raw page and sixteen unchanged nested records are
archived. The contextual policy uses an exact full-record follow-up pin.

`second-warning-witness-extracts-20261104.v1.json` compares LH1891physical317,
Athos Plate I, Sinaiticus6.1–8, Vulgata printed8–10, Palatina printed19–23,
and d’Abbadie1860's Latin-rendered Ethiopic printed116. Notes distinguish
Sinaiticus's first-hand Christ/corrected Lord, Vulgata's positive profit,
negative versus positive life-denial, editorial emendations, forgiveness
scope and past/future mercy. The selected whole-heart repentance AND
removal of double-mindedness condition, no-salvation warning, distinct
group/time limits, negative life clause and past mercy remain explicit.
No direct Geʿez or original-photograph collation is claimed.

Azure006r1 caught a stale lexical rationale identifying the passage with
death/judgment. Both rationales now leave its kind unspecified, as the
source does; the English paragraphs are unchanged. Fresh006r2 accepts
both editions and the current YAML/evidence hashes match its receipt.
All123Hermas tests,21contextual tests,397policy,439/416YAML guards and84
payload/source/base hashes passed before the rationale correction. The
two focused warning tests,397policy and84hashes passed after it. There
remain34broader source-collation flags; other witness comparisons, reader/
artwork migration, whole-book verification and publication are unfinished.

`maximus-warning-alignment-20261104.v1.json` aligns V.2.iii in four numbered
paragraphs and adds simplified007. All four paragraphs already existed;
source body and whole-book English extent are unchanged. Notes now accompany
the sister, discipline, death, tribulations, business dealings, continuation
condition, eternal life, denial, returners and written citation. The full
old flat record and eight unchanged nested records are archived.

`maximus-warning-witness-extracts-20261104.v1.json` compares LH1891physical318,
Athos Plates I–II, Sinaiticus7.1–4, Vulgata printed10–11, Palatina printed23,
and d’Abbadie1860's Latin-rendered Ethiopic printed116–117. It distinguishes
the conjectural denial infinitive from manuscript arnesai, Athos's bracketed
negative, Sinaiticus's unreadable first-hand letter/correction, corrected
sins versus first-hand business dealings, and the versions' additional or
different death, virtue, hope and return wording. The selected causes,
no-grudge condition, perfect saved/if continue, eternal-life language and
Maximus warning remain. No direct Geʿez or original-photo collation is claimed.

Azure007r1 accepts both editions; current YAML/evidence hashes match the
receipt. All125Hermas tests,397policy,439/417YAML guards and85payload/source/
base hashes pass. The unchanged21contextual tests passed at006. The34broader
source-collation flags remain. Further witness comparison, reader/artwork
migration, whole-book verification and publication remain unfinished.

`church-booklets-alignment-20261104.v1.json` aligns V.2.iv in three numbered
paragraphs and adds simplified008. All three historical paragraphs already
existed; source body and English extent are unchanged. The flat record had
lost footnotes, lexical/theological decisions and drafting metadata while
keeping orphan markers. Its prior complete record was recovered from Git
commit286c9666699e4062546f8ce60358d0d59667aa4a. Both full flat histories and
six unchanged nested records are archived. Notes and editorial metadata are
restored, with all markers localized and the duplicated elders marker removed.

`church-booklets-witness-extracts-20261104.v1.json` compares LH1891physical318–319,
Athos PlateII, Sinaiticus8.1–3, Vulgata printed11–12, Palatina printed25/27/29,
and d’Abbadie1860's Latin-rendered Ethiopic printed117. Notes distinguish
Sinaiticus's S1 old-age-question addition, Athos's uncertain sleeping line
and bracketed admonish letters, Vulgata's conjectural through-you wording,
and Palatina/Ethiopic-rendering absence of a separately named Grapte. The
Ethiopic rendering also addresses Hermas as the one completing the words,
unlike the selected old woman's I complete. The source's first-created
Church, world ordered for her sake, all elect through Hermas, two recipients,
distinct commissions and reading with presiding elders remain explicit.
No direct Geʿez or original-photograph collation is claimed.

Azure008r1 caught an inherited rejected Sibyl identity listed as a viable
alternative; r2 caught an unsupported causative reading alternative. Both
metadata defects are corrected, with the narrative unchanged. Fresh008r3
accepts both editions; current input/evidence hashes match its receipt.
All127Hermas tests,397policy,439/418YAML guards and86payload/source/base
hashes passed before metadata corrections; two focused tests and86hashes
passed after each correction. The unchanged21contextual tests passed at006.
There remain34broader source-collation flags. Further witness comparison,
reader/artwork migration, whole-book verification and publication are unfinished.

`first-seat-alignment-20261104.v1.json` aligns V.3.i in nine numbered
paragraphs and adds simplified009. All nine paragraphs already existed.
Scans confirm seven imported transcription errors: the cushion word,
two linen accents, three seat-word pi/psi forms on319, and the remain
command on320. Raw/normalized/attached source now matches the print for
those words; adjacent V.2.iv and V.3.ii normalized bodies are unchanged.
These are print corrections, with zero new manuscript-selection loci.
The full old flat record, raw pages and eighteen unchanged nested records
are archived. All note anchors are localized.

`first-seat-witness-extracts-20261104.v1.json` compares LH1891physical319–320,
Athos PlateII, Sinaiticus9.1–9, Vulgata printed12–14, Palatina printed29–33,
and d’Abbadie1860's Latin-rendered Ethiopic printed117–118. Notes distinguish
fifth/sixth hour, bracketed Vulgata furniture supplement, the arrival/listening
block absent in Sinaiticus/Palatina, the conjectural stood-near form,
Sinaiticus's S1/ca left-gesture additions, bare/my/his Name, and different
share, confession and perseverance wording. The selected scene, imperative,
sitting promise and works/endurance conditions remain. No direct Geʿez or
original-manuscript photograph collation is claimed.

Azure009r1 caught two stale lexical metadata entries: a clock-conversion
claim and do-their-deeds instead of the actual do-their-works. These are
corrected. Additional scan/XML comparison corrected the three seat-word
forms before fresh009r2, which accepts both editions; current input/evidence
hashes match its receipt. All129Hermas tests and397policy pass after the
final changes;87payload/source/base hashes and two focused tests also pass.
439/419YAML guards passed before the final source/metadata revision. The
unchanged21contextual tests passed at006. The34broader source-collation flags,
further witness comparisons, reader/artwork migration, whole-book verification
and publication remain unfinished.

`tower-stones-alignment-20261104.v1.json` aligns V.3.ii in nine numbered
paragraphs and adds simplified010. All nine historical paragraphs already
existed. The printed sympselion was imported as symplesion, leading to an
unsupported plaited-bench material claim. Raw320, normalized and attached
source now match the print; the English and lexical decision read bench.
The prior full flat record, raw page and eighteen unchanged nested records
are archived. The shared-leaf regression proves that009's exact repaired
raw320 is010's input, then allows only this one audited print correction.
The accepted009 translation/evidence and normalized body are unchanged.
This adds no manuscript-selection locus or English extent.

`tower-stones-witness-extracts-20261104.v1.json` compares LH1891physical320–321,
Athos PlateII, Sinaiticus10.1–9, Vulgata printed14–16, Palatina printed33/35,
and d’Abbadie1860's Latin-rendered Ethiopic printed118–119. It distinguishes
Sinaiticus's two first-hand sixty counts corrected by ca to six, unreadable
first-hand letters and S1 readings, the selected not-double-minded qualifier
from the Ethiopic rendering's positive doubtful wording, and the editor's
comment about a lost negative. The latter is not preserved negative evidence.
Bracketed You, different rod descriptions, stone categories, road/no-road
readings and the added Sinaiticus burning clause are disclosed. Equal gifts/
promises, definite future cleansing, all stone groups and inability despite
desire remain. No direct Geʿez or original-photograph collation is claimed.

Azure010r1 accepts both editions; exact current input/evidence hashes match.
All131Hermas tests,397policy,439/420YAML corpus guards and88payload/source/
base hashes pass. The unchanged21contextual tests passed at006. There remain
34broader source-collation flags. Further manuscript/version/excerpt comparison,
reader/artwork migration, whole-book verification and publication are unfinished.


`builders-revelation-alignment-20261105.v1.json` aligns V.3.iv as three
complete historical paragraphs, joining six existing dialogue blocks and
adding simplified012. It archives the full old flat record and twelve
unchanged nested records, including prior growth/build and outcome
adjudications. Duplicated and misplaced notes are localized. No source-body
or English-extent change or new manuscript-selection locus is claimed.

The bounded evidence compares LH1891 printed306, Athos PlateII, official
Sinaiticus12.1–3, Vulgata17–18, Palatina37/39, and Latin-rendered Ethiopic
119–120. It newly acquires Gonis2005's P.Oxy.LXIX edition and identifies
Oxford4706 fragment1 at V3iv3/global12.3 in both print and the photograph.
Surviving right-edge word parts are distinguished from reconstructed
pronouns, conjunctions, verbs and spacing-based article omission. Correct
DCLP/TM69384 has empty edition metadata; it supplies no transcript. Four
Oxford images and the modern scan remain outsideGit for consultation.
Bodmer readings remain edition-reported, without fresh Bodmer collation.

Sinaiticus's sixty-to-six correction, deletion of the second six, added
past revelation and added doubt question are distinguished from its first
hand. Athos's diaphora/exodos, eti and estai differences and the versions'
different titles/wording are disclosed. Azure012r1 caught inherited
softening of edei to mere fitness; the standard now preserves ought-to-
have-been, while simplified retains should-have-been. Both lexical records
now describe the actual obligation. Azure012r2 accepts both editions;
exact current input and evidence hashes are verified.

All133Hermas tests,397policy records,439/421YAML guards and89repair
payload/source/base hashes pass. All34broader collation flags remain;
independent review, other manuscript comparison, reader/artwork migration
and publication remain unfinished.


`stones-meaning-alignment-20261105.v1.json` aligns V.3.v in five complete
paragraphs and adds simplified013. All five paragraphs already existed.
The actual print has eripton with pi, where the import had eritton with
tau; raw323/normalized/attached source now agree with the print. The old
variant note mistook that import error for manuscript variation and is
superseded. The prior full flat record, ten unchanged nested records, raw
page and recovered pre-bulk-edit record (20notes/31lexical/7theological
decisions) are archived. The accomplished-commandments adjudication and
contextual repentance wording remain. No new manuscript-selection locus
or English extent is claimed.

The bounded evidence compares LH1891printed307, Athos PlatesII/III, official
Sinaiticus13.1–5, Vulgata18–20, Palatina39/41/43, and Latin-rendered Ethiopic
120. The selected positive evil-was-found agrees with Sinaiticus/Palatina;
Athos/Vulgata/Ethiopic rendering have a negative. That disagreement is
disclosed rather than harmonized. Name-of-God versus Lord, extra death
wording, unreadable first-hand letters, later correctors and Athos bracketed
restorations are distinguished. All four roles, triple service, stone
groups, repeated repentance conditions, construction deadline, no-place
denial and exclusion remain. The historical397-record policy plan stays
immutable; one exact complete-record followup is independently hash-pinned
and mutation-tested for013.

Azure013r1 identified a nonexistent elect-policy citation, a simplified
metadata mismatch and a mislabeled unsupported genitive alternative. These
were corrected with historical records preserved; reader wording stayed
the same. Azure013r2 accepts both editions, with exact current YAML/evidence
hashes verified. All135Hermas tests,22contextual-policy tests,397policy
records,439/422YAML guards and90repair payload/source/base hashes pass.
The34broader collation flags, remaining witnesses, independent review,
reader/artwork migration and publication remain unfinished.


`wealth-stones-alignment-20261105.v1.json` aligns V.3.vi as seven complete
paragraphs and adds simplified014. All seven paragraphs already existed.
The printerfooter20—2 interrupted dia/touto across the323/324 join; raw323
and normalized/attached source now exclude it. No ancient words were added.
The old full flat record, fourteen unchanged nested records and raw323 are
archived. The shared-leaf guard proves013's exact repaired page is014's
input, then permits only this footer removal. Accepted013 YAML/evidence
and normalized body are unchanged. No manuscript-selection locus is added.

The bounded evidence compares LH1891printed307–308, Athos PlateIII, official
Sinaiticus14.1–7, Vulgata20–22, Palatina43/45 and Latin-rendered Ethiopic
120–121. Newly compared P.Oxy.4706 fragment2 has only central word-parts
of14.6; its large surrounding restorations and uncertain gar/ti/kai
reconstructions are distinguished. The Oxford photo-edition match supplies
no later Lord/Christ title or closing14.7 clause. Athos has Christ in the
second comparison, Palatina says denyGod, and Sinaiticus omits several
clauses. The Vulgata righteousness/iniquity supplement is explicitly from
Palatina, not unbroken Vulgata manuscript evidence. These are disclosed
without harmonizing the selected source.

Prior serviceable/scabbed/holyones/truncated/captivates/cutback/trimmed/sheds
choices remain. The contextual passive closing interpretation is retained
with the active alternative and its uncertainty disclosed. The versions'
being-of-the-stones formulations are not described as active-use evidence;
Sinaiticus omits the clause. Plural address and bracketed de are explicit.
Azure014r1 caught an inherited overgeneralization identifying all remaining
stones as scabbed; both editions now preserve that subgroup distinction.
Azure014r2 accepts both editions; exact current YAML/evidence hashes match.

All137Hermas tests,397policy records,439/423YAML guards and91repair
payload/source/base hashes pass. The unchanged22contextual-policy tests
passed at013. All34broader collation flags remain; other witnesses,
independent review, reader/artwork migration and publication are unfinished.


`repentance-transfer-alignment-20261105.v1.json` aligns V.3.vii as six
complete paragraphs and adds simplified015. All six already existed in
five English blocks. Two imported demonstratives on physical325 now match
the printed rough breathing/circumflex; no negation, manuscript-selection
locus or English extent is added. The complete flat history, raw/normalized
input and ten unchanged nested records are archived. Nineteen notes now
attach once at their actual clauses.

The evidence compares LH1891printed308–309, Athos PlateIII, official
Sinaiticus15.1–6, Vulgata22–23, Palatina45/47 and the Ethiopic edition’s
Latin rendering121–122. It preserves the selected positive and negative
transfer conditions while disclosing Sinaiticus/Palatina’s different
because-of construction. Bracketed Vulgata repentance wording, the
Palatina editorial proposal and the Ethiopic rendering’s supplied negative
are distinguished from preserved manuscript words. Athos’s difficult
conditional is not silently repaired into corroboration. Bodmer imagery
remains unacquired after another HTTP500 tile response.

The contextual repent in2/change-their-mind in3 distinction and prior
cravings, courage, righteous-word and plural-pronoun choices remain. The
full later record and historical397-policy contract are exactly pinned
and mutation-tested. Azure015r1 accepts both editions; current YAML and
evidence hashes match its receipt. All139Hermas tests,23contextual-policy
tests,397policy records,439/424YAML guards and92repair payload/source/base
hashes pass. All34broader collation flags remain; independent review,
other witnesses, reader/artwork migration and publication are unfinished.


`seven-virtues-alignment-20261105.v1.json` aligns V.3.viii as eleven
complete historical paragraphs and adds simplified016. All eleven already
existed in seven English blocks. The source is unchanged; raw325/326 and
fourteen nested records remain hash-guarded. The complete old record,
including the hold-fast lexical and compound-renewal grammar adjudications,
is archived. Eighteen notes replace misplaced and repeated markers.

The evidence compares LH1891printed309–310, Athos PlateIII, official
Sinaiticus16.1–11, Vulgata23–25, Palatina47/49/51 and the mediated Ethiopic
Latin rendering122–123. It discloses differing virtue lists and birth
chains, the believing/if construction, singular/plural address and titles,
and corrections versus first-hand words. The final speak is an explicit
contextual resolution of the obelized Greek infinitive; all corresponds
to bracketed editorial panta. Vulgata omnia and Palatina’s live/Caritas
emendations are distinguished from their codex words. The Ethiopic
rendering’s proposed passive revealed is not treated as preserved text.

The prior hold-fast and compound reminder-and-renewal choices remain, as
do all seven women, salvation through Faith, abstention/inheritance
condition, serve-and-hold requirements, tower/end/quick-completion and
hearing-and-doing cleansing with Hermas included. Azure016r1 accepted
standard but found simplified11 had lost the explicit purpose connector.
Simplified now restores so that; the added regression guard protects it.
Fresh Azure016r2 accepts both editions, with current YAML/evidence hashes
verified against the receipt. All141Hermas tests,397policy records,
439/425YAML guards and93repair payload/source/base hashes pass. The
unchanged23contextual-policy tests passed at015. All34broader collation
flags remain; other witnesses, independent review, reader/artwork
migration and publication remain unfinished.

CI42029340121 exposed a machine-local raw archive path in the new016
history test. The original path remains as provenance; an explicit
repository-relative path now drives the portable hash check. The raw
bytes and accepted016 YAML/evidence are unchanged.
