# Hebrew pointing differences and Proverbs 7 22

The complete pinned UXLC/WLC OT screen contains 374 verse rows whose first
difference is pointing, not consonants. This follow-up makes every one of those
rows available for a reproducible word-level review. Its first published-source
comparison, Proverbs 7:22, finds a reported vowel correction but no demonstrated
change to POB's existing “going to slaughter.” It does not discover a new ancient
reading or validate the original wording.

## Complete queue and its limits

The [original screen](UXLC_WLC_WHOLE_OT_SCREEN_2026-09-06.md) covers all 39
ordinary books and 23,213 shared verse labels in two digital transcriptions of
the Leningrad tradition. They are not independent manuscripts. The
[new queue](../sources/textual_restoration/discovery/uxlc_pointing_triage.2026-10-05.v1.json)
contains all 374 pointing-first rows, not a selection of likely successes.

| Mechanical category in decision order | Verse rows | What remains to review |
| --- | ---: | --- |
| Written token alignment not established | 3 | Reconcile boundaries before pairing words |
| Any qere present in either verse | 37 | Establish which differences concern written text or reading conventions |
| Only dagesh or rafe differs in every changed aligned word | 225 | Dagesh may distinguish morphology; this is not an automatic no-meaning category |
| Only shin or sin dots differ in every changed aligned word | 2 | Determine intended lexeme and transcription accuracy |
| Other pointing differences | 107 | Examine vowels, grammar, publisher corrections and context |

These exclusive categories total 374. There are 378 changed written-word pairs
across the aligned rows, including qere-involved rows. A chapter-context flag
identifies 13 rows in Exodus 20 or Deuteronomy 5. It does not exclude those rows
or claim every change belongs to a Decalogue pointing convention. Every row
remains semantically unadjudicated in the generated queue.

This is post-hoc operational triage following exploratory inspection, not a
predeclared blind experiment, a discovery rate or a count of English defects.
Proverbs 7:22 was deliberately chosen as a potentially relevant vowel contrast;
its no-change outcome cannot estimate the remaining queue's yield.

## Proverbs 7 22 published controls

The current [canonical record](../translation/ot/proverbs/007/022.yaml) has
pointed WLC `טָ֣בַח` and English “like an ox going to slaughter.” Its SHA-256
before and after this comparison is
`cf74c221f0a11f935ed2f33c4d0576a2f80469adcc18f2e24ea19749eeced9ec`.
The vendored [OSHB/WLC file](../sources/ot/wlc/Prov.xml) tags that word with
lemma 2874 and `HNcmsa`: a Hebrew common masculine singular absolute noun.
The qamats therefore does not by itself establish a finite verb or a new
meaning absent from POB. These are the digital source's analysis and the
contextual noun interpretation, not independently recovered ancient vowels.

The [UXLC change entry](https://www.tanach.us/Changes/2023.10.19%20-%20Changes/2023.10.19%20-%20Changes.html#2023.06.09-5)
records change 2023.06.09–5 at word 7:22.6, folio 412A, column 1, line 24:
qamats under tet becomes segol, yielding `טֶ֣בַח`. It reports segol in the BHL
body text and distinguishes the BHLA note on word 11. Those BHL/BHLA claims
are the publisher's report; neither edition was directly consulted here.
The complete matching correction entry in the pinned Proverbs XML was also
checked. No codex-image reading or two-family blinded transcription is claimed.

Root and a bounded separate source assessor inspected Michael V. Fox's
*Proverbs* (2015), printed 146 / PDF 168, as a complete native page.
Its apparatus selects `טֶבַח` with Mᴬ against `טָ֣בַח` with Mᴸ and classifies
the contrast as graphic. Printed 17 / PDF 39 defines Mᴬ as Aleppo and Mᴸ
specifically as Leningrad through digitized BHS. Fox's Mᴸ report is not a new
observation of the manuscript and must not be conflated with UXLC's later
transcription correction. His separate proposals for the verse's difficult
final comparison do not follow from this one-vowel analysis.
[Publisher PDF](https://www.sbl-site.org/wp-content/uploads/2024/11/Proverbs_Fox_SBL.pdf).

The strongest reason to prefer the segol transcription is the publisher's
specific correction record, with a compatible scholarly selected form. The
strongest limitation is that our evidence here is published interpretation,
not independent verification of the codex or full modern apparatus. The
qamats-form noun already gives slaughter in context. Even accepting the
reported segol correction does not require different English or prove the
earliest pronunciation. Age weighting adds nothing between two transcriptions
of the same codex; Fox's reported Aleppo comparison does not settle priority.

**Outcome:** retain source and English provisionally, document the published
source-correction lead, and make no reader-note change for this vowel alone.
A future adoption must use an honest source label or explicit source apparatus;
silently changing a verbatim WLC field would obscure its provenance. Reopen the
source application for a defined correction package and relevant codex/apparatus
verification, not another model vote. The final clause is a distinct question.

## Reproduction and acquisition

### Proverbs 24 25 does not establish a different lexeme

The next completed pointing comparison retains the
[current verse](../translation/ot/proverbs/024/025.yaml) and its English,
a blessing of good things. The frozen row contrasts `טוֹב` with `טֹוּב`,
not ordinary `טוּב`. Removing the retained holam would silently substitute a
different input. These are two transcriptions of the same Leningrad tradition,
not two independent ancient witnesses.

The complete matching correction in the pinned Proverbs XML says to move
holam from waw to tet and add dagesh to waw. The
[publisher entry](https://www.tanach.us/Changes/2023.10.19%20-%20Changes/2023.10.19%20-%20Changes.html#2023.06.09-25)
locates word 6 at folio 418A, column 2, line 2. It describes a connected
holam at the tet and a poorly shaped but dark, positioned waw dot. It reports
BHL body text without the dot and BHLA with the dot but holam still on waw;
neither edition was directly consulted. This confirms the intended published
encoding, not our own manuscript-pixel reading or earliest pronunciation.

The vendored OSHB/WLC marks the current last word as lemma 2896 b,
`HAamsa`, following construct `בִרְכַּת`. Its adjective/substantive analysis
fits good in context; it is not independent adjudication of UXLC. The
[published GKC grammar](https://en.wikisource.org/wiki/Gesenius%27_Hebrew_Grammar/12),
section 12 footnote 2, distinguishes the identical printed waw-dot shapes
for dagesh and shureq. The retained preceding vowel prevents automatically
reading the dot as ordinary shureq and changing the lexeme to goodness.
An anomalous manuscript mark, overlapping correction or transcription issue
remains a possible explanation, not an established physical finding.

Root inspected Fox's complete native pages, printed 328–329 / PDF 350–351.
The selected Hebrew displays the ordinary holam word. The verse-specific
apparatus discusses Syriac poor versus rebukers in the first clause, not a
good/goodness variant at the last word. That scope does not establish agreement
of every witness or defeat the later publisher correction. Fox's Syriac
edition-error diagnosis was read but its underlying editions were not newly
collated. No new HALOT or BDB consultation is claimed.

**Outcome:** retain source, English and existing notes provisionally. Hold
acceptance of an exact new diplomatic transcription; do not infer a new lexeme
or historical source preference from the digital contrast. Discriminating
codex or apparatus evidence can reopen transcription even without an English
change. Even independently
established goodness would still require demonstrating an English consequence
against the existing good-things wording. Reopen for discriminating codex or
apparatus evidence, not another model vote. This deliberately selected case
does not estimate the yield of the remaining queue.

The [comparison receipt](../sources/textual_restoration/comparisons/proverbs24_25_pointing.2026-10-05.v1.json)
pins the row, source controls and unchanged verse. No frozen queue entry is
rewritten as adjudicated; its original status describes the generated screen.
The bounded assessor's grammatical countercase and root's publisher/native-
page inspection are distinct checks, not blinded image corroboration.
The PDF skill required complete native pages; the documentation skill keeps
reported marks, lexical inference and actual English effects separate.
Ten focused queue tests, exact receipt-input/row checks, local link targets and
whitespace pass. The verse, shared method, frozen queue and protected Genizah
file remain unchanged. One final bounded critique prompted clearer separation
of transcription reopening from English consequences and of undemonstrated
novelty from a claim that novelty is impossible. It did not independently
verify private sources or confer scholarly publication approval.

The frozen screen SHA-256 is
`f893ce50894b4f6890e218a3bd1ea44c3166e44abe4efba59e6d9fba66dca4e6`.
The triage receipt pins that screen, its original comparator, protocol and book
map, all 39 WLC files, the triage generator and controlling method. It preserves
raw differing words and source-local XML positions; written word numbers are
not XML child indexes. The new generator has no canonical writer.

The public UXLC archive was reacquired with a 3,000,000-byte cap and 60-second
deadline. Its 2,365,002 bytes and hash match the original pinned UXLC 2.5 build
27.6 and the [publisher verification table](https://www.tanach.us/Pages/Technical.html).
All raw book records, differences, summary counts and archive members reproduce
the frozen screen exactly. Current canonical joins are deliberately outside
this historical raw-input reproduction; old approval pins are not rewritten.
No full site/header/image assets are redistributed.

Private study controls: the complete change-history HTML is 345,075 bytes,
SHA-256 `b8d506f4c9bb288596edad2a626d738882d8ae4b3ff7ddfd0df393ffc647344f`;
Fox's PDF is SHA-256
`1953e00d7275c1bda5031378b347fba65348bc08855ec0f8757841ca6cdc1c39`.
Web-reader errors were superseded by ordinary public retrieval; failed access
was not treated as missing text. Modern PDF and publisher site assets remain
outside Git. The PDF skill required native-page verification; the documentation
skill kept source reports, source selection and English effects separate.

```bash
.venv/bin/python -m tools.textual_restoration.triage_uxlc_pointing
.venv/bin/python -m tools.textual_restoration.triage_uxlc_pointing --archive /path/to/pinned-uxlc.zip
.venv/bin/python -m unittest discover -s tests -p 'test_uxlc_pointing_triage.py'
```

The next useful meaning question is Judges 20:48's `מְתֹם` versus `מְתִם`,
subject first to publisher history and grammatical analysis. This is a lead,
not a judgment about men versus totality. The wider all-source comparison,
fresh-reading calibration and representative English-benefit evaluation remain
unfinished. No ImageGen evidence, new witness, canon decision or scholarly
publication approval is produced by this queue or its first comparison.

## Actual validation and historical debt

Root's ten focused tests and full raw-archive reproduction passed. The ten
tests are added to the existing corpus-integrity workflow so remote CI also
checks the queue. Local Markdown link targets and whitespace checks pass;
the canonical Proverbs record and unrelated untracked Genizah file retain
their exact hashes. No verse or reader export changed.

The older comparator suite reports 13 passes and one failure, reproduced by
root and the separate reviewer. Its historical input-pin test expects
`b6ce63c3ce743f13332997712d04a70258d6844b24428d74556ee58794f87e22`
for 2 Samuel 13:37, while the current record is
`63d80b610ed4c20bc4da1b4716447727cdda57a70c1a75bd8545fc7b90c8ada1`.
That previously edited record is unchanged by this work. Complete raw-source
reproduction does not turn the old canonical-join approval into a current pass.
No historical receipt is repinned, and no clean full-suite claim is made.

One bounded independent critique passed the new queue, source qualifications,
preservation and CI addition after reproducing the ten tests and raw archive
check and inspecting native Fox pages. It did not approve historical priority,
fresh decipherment, the complete CI workflow or publication.
