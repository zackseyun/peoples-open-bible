# Psalm 145: presence is not exact wording

Checked 2026-09-05. This upgrades the existing provisional pilot with directly
consulted edition/transcription controls; it is not a newly discovered variant.

The later [provisional critical-source adoption](#provisional-critical-source-adoption)
revises the exact-wording hold for a working composite, not for a claim about
the earliest wording. The dated observations and earlier decisions below remain
historical.

| Consulted control | Corresponding line | Designation | Words phrase | Second-colon adjective |
|---|---|---|---|---|
| WLC Hebrew | Absent | — | — | — |
| 11Q5 published Hebrew | Present | God | in his words | חסיד, here glossed loyal |
| Rahlfs Greek 144:13a | Present | Lord | in his words | ὅσιος, holy/pious |
| CAL Peshitta 145:13 | Present | Lord | in his words | ܙܕܝܩ, righteous |
| CAL Targum 145:13→14 | Absent | — | — | — |

Only 11Q5 is a newly mapped individual manuscript here. Edition controls are
not manuscript votes. None of the three present-line controls in this first table explicitly has
“all” before words; all have it before deeds/works.

The Hebrew line occupies XVII 2–3: the final word of line 2 and first five
printed words of line 3, without supplied-letter brackets or uncertainty marks
in this excerpt. The recurring blessings are separate units. The second colon
recurs at verse 17, XVII 9–10. This is published-text evidence, not freshly read
pixels. [Qumran-Digital 11Q5, version 2026-05-21](https://lexicon.qumran-digital.org/transcriptions/11Q5/2026-05-21/index.html?v=2026-05-21).

The Syriac control has “righteous” here but “merciful” in its verse 17's second
colon. That does not prove a different underlying Hebrew adjective. Its text
is Leiden-derived with selected 7a1 corrections, not a direct reading of one
manuscript. An attempted lexical-link request returned an unrelated entry and
was excluded. [Peshitta chapter](https://cal.huc.edu/get_a_chapter.php?cset=S&file=62027&sub=145),
[edition information](https://cal.huc.edu/get_file_info.php?coord=62027145).
The Targum display moves directly from kingdom/dominion to supporting the fallen;
this does not certify absence in every copy.
[Targum chapter](https://cal.huc.edu/get_a_chapter.php?cset=H&file=81002&sub=145).

## Reproducible checks

The [receipt](../sources/textual_restoration/discovery/psalm145_control_check.v1.json)
checks 21 WLC poetic openings, excluding only the verified two-word title in
verse 1. Their sequence lacks nun. It also verifies bounded QDR morphological
tokens against the separately consulted Hebrew and the Greek suffixed reference
`Ps 144:13a`. A verse-tag-only extraction includes flanking blessings; an
integer-only Greek importer misses the added line. Neither index agreement nor
acrostic completion proves historical priority or legible ink.

QDR commit `f54f38464e18409eed8286fe24dd24f88d4735dd` and Greek commit
`c91f6b1e8fb3ba37df701e6ae31f675ace71a2b2` are external pinned inputs.
The receipt exports hashes and mapping metadata, not full corpus text.
CAL displays were consulted live, not frozen or fully imported.

```bash
.venv/bin/python tools/textual_restoration/build_psalm145_check.py /path/to/qdr.1.1.biblical.json /path/to/lxx-morph/db/seeds/lxx_morph/psalms-lxx.json --verify-only
.venv/bin/python -m unittest tests.test_psalm145_check tests.test_ot_witness_registry
```

## Decision and POB impact

Retain the earlier moderate working preference for considering inclusion,
without selecting exact wording. Early Hebrew attestation and the alphabetic
position support inclusion; early acrostic repair using familiar language and
verse 17 is a substantial counter-explanation. The scroll's recurring blessings
show a different form, not that every difference is secondary. These are
editorial hypotheses, not observed scribal intentions. Removing the modest
chronological preference leaves structural evidence but no decisive direction
of change.

Keep inclusion, divine designation, “all” before words, and the adjective
separate. The [POB note](../translation/ot/psalms/145/013.yaml) now quotes a
working translation of the Hebrew witness: “God is faithful in his words and
loyal in all his deeds.” It discloses Greek's designation and retention of MT.
“Loyal” is a lexical choice, not the only possible English equivalent. Hebrew
source and English main words are unchanged. Old review scores do not certify
this new note; its review was one context-informed Codex pass plus consistency
tests, not an independent blinded review.

The formal ledger has 13 cases and 20 coverage records, not 20 completed
collations; the first pass had 22 registry entries, now 25 after the Latin
follow-up below. The existing pilot, sample,
English-impact baseline and generated reports have been synchronized.

## Latin follow-up: an edition is not a uniform tradition

The earlier pilot's blanket “Jerome's Hebrew Psalter lacks the line” is too
broad. Direct consultation produces this more precise record:

| Consulted edition | Corresponding line | Qualification |
|---|---|---|
| Weber–Gryson 2007, *iuxta Hebraeos*, publisher VUL | Absent | Edition-specific absence, not a physical lacuna |
| Weber–Gryson 2007, *iuxta LXX*, publisher VULA | Present | Lord; **all** his words; holy in **all** his works |
| Harden 1922, *iuxta Hebraeos*, p. 187 | Present | Same two “all” qualifiers; apparatus explicitly reports omission in A H R |

Both publisher pages label this Psalm 144; Harden labels it 145. Opening and
flanking clauses confirm alignment with POB Psalm 145. The publisher's
Hebrew-based display passes from mem to samech without the corresponding line.
Its Greek-based display includes it. Neither full modern apparatus was
available in these displays.
[Hebrew-based text](https://www.die-bibel.de/bibel/VUL/PSA.144),
[Greek-based text](https://www.die-bibel.de/en/bible/VULA/PSA.144).

Harden's printed p. 187 (PDF page 223) was visually checked, not merely OCR-read.
His apparatus has `om. clausulam fidelis ... operibus suis AHR`. In **Harden's**
sigla, A is the Amiatine Psalter, H Codex Hubertianus (Add. 24142), and R the
Ricemarch Psalter (Trinity College Dublin A 4. 20). These are the editor's
historical identifiers, not newly checked holding-library records. The sigla
and method pages were also visually checked (xi–xii, xvii–xviii, xxix).
Harden warns that his A evidence comes through problematic earlier collations.
His selective apparatus states exceptions to inference from silence; we retain
the explicit A H R report without manufacturing individually verified readings
for every unmentioned witness.
[Harden's digitized edition](https://archive.org/download/psalteriumiuxtah00lond/psalteriumiuxtah00lond.pdf).

PDF SHA256: `e65a762914345706c36631d68da0bd0f6d4a87afd3230c705bc08101620b015e`.
The three edition records add no physical passage-coverage records. The full
PDF is retained outside the repository; only bounded evidence and provenance
are recorded here. Modern publisher displays were consulted live, not frozen.

This corrects attribution and verifies a Latin “all his words” form; it does
not recover that word in Hebrew. Cross-influence between Latin Psalters is a
possibility to test, not an established explanation for this unit. Neither
Harden's inclusion nor Weber–Gryson's omission alone settles Jerome's initial
Latin text, its Hebrew exemplar, or the earliest Hebrew Psalm. The moderate
working inclusion preference is unchanged, exact wording remains unresolved,
and this follow-up changes no POB source or English main text.

## Open evidence

Inspect full Hebrew/Greek/Syriac apparatuses, the late Hebrew marginal hand,
and the modern Latin apparatus and manuscript attestations behind the edition
disagreement above. Old Latin and Roman Psalter coverage remains open; the
three editions do not complete Latin collation. Brettler's *Supplementation in Psalms:
Illustrations from Psalm 145*, pp. 3–20, is an important follow-up: only its
publisher preview/metadata were accessible, not the full argument.
[Publisher record](https://www.jstor.org/stable/j.ctvvnhmb.5).

The LOC exhibition confirms the displayed nun-line witness and Sanders
publication. Its object-page route returned 403; current custody, image rights,
region mapping and new paleographic review remain unverified, as recorded in
the coverage ledger. [LOC captions](https://wwws.loc.gov/exhibits/scrolls/bib.html).
ImageGen would illustrate known wording, not recover ancient letters. No
generated image or fresh restoration was used; source promotion remains open.

## Provisional critical source adoption

Decision date: 2026-10-04, local time; machine records retain UTC timestamps.
Baseline: `6b9337f796dedecd4794b09451f712b9cfb3f6f8`.
The [decision and evidence record](../sources/textual_restoration/applications/psalm145_nun_decision.2026-10-04.v1.json)
provisionally selects the actual 11Q5 nun line, not a harmonized Hebrew
retroversion. This is a revised editorial decision on known evidence, not a
newly deciphered or discovered line. The exact earliest wording remains open.

The earlier `build_psalm145_check.py --verify-only` recipe belongs to the
note-only baseline and deliberately rejects a changed current verse. Do not
regenerate that frozen receipt to hide the source change. Its historical test
now uses the exact Git baseline; current critical binding and preserved WLC
context are checked by `test_psalm145_critical_application.py` and
`test_psalms_source_context_map.py` respectively.

Early direct Hebrew attestation, the missing alphabetic position and a
corresponding Greek line without 11Q5's recurrent blessings support a modest
inclusion preference. The strongest objection remains early acrostic repair:
an editor could provide a nun opening and reuse verse 17's second colon.
Repetition can also be poetic; neither borrowing direction nor a copying event
is established. The refrain difference isolates a textual unit but cannot by
itself prove priority. Without the modest age preference, inclusion is less
persuasive, not certain. An attested wording can serve a provisional composite
without being certified as the earliest wording.

The new print check visually inspected complete Swete II pp. 408–409
(PDF 426–427), with preface viii–x (PDF 10–12). Its Vaticanus-oriented selection
has “Lord,” no “all” before words, and the corresponding couplet printed at
Greek 14 before the support-the-fallen clause. Alignment follows content, not
verse-number equality. The apparatus reports an added *pasi* before words in
`א c.a R T`; the preface distinguishes the Sinaiticus correction, Verona and
Zurich sources. These are edition reports, not fresh manuscript collations.
This provides a concrete Greek variant behind the “all his words” question;
it does not establish Latin dependence or reconstruct that qualifier in Hebrew.
The reused scan has SHA256
`945c5b15bf0f9dfc93890b28ee5b66a388acbf4597f1f2be5430ac6cba9c30b0`.

Gentry's 2009 pp. 30–31 and footnote 47 were read through web text extraction.
His preference for inclusion is an argument, not another witness; the proposed
scroll-edge mutilation is not demonstrated by an extant exemplar or layout.
The catena and other-interpreter evidence remains his report, not our new
manuscript reading. The local PDF request returned 403 and screenshot access
did not produce a usable table; no visual Gentry-page inspection is claimed.
Brettler's full chapter remains unread after a bounded access/search attempt.
The counterargument above is not falsely attributed to that chapter.

The [reviewed source record](../sources/ot/pob_critical/psalms/145/013.json)
adds `נאמן אלוהים בדבריו וחסיד בכול מעשיו` to the retained WLC mem stanza.
The explicit composition patch also replaces the baseline's two terminal
maqafs with stanza punctuation. The record is **POB-critical**, not verbatim
WLC or the complete 11Q5 Psalm; the scroll's blessings are not imported.
The original pointed base survives separately. Qumran-Digital's CC BY-SA 4.0
attribution and the bounded-excerpt/publication limits are recorded; no full
modern edition or apparatus is redistributed or relicensed here.

The new English assertion is “God is faithful in his words and loyal in all
his deeds.” Preserve God, not Yahweh, and do not add all before words or narrow
words to promises. A [candidate-identity-withheld assessment](../sources/textual_restoration/applications/psalm145_english_review.2026-10-04.v1.json)
preferred this rendering and the same second colon at verse 17. It noted that
loyal emphasizes fidelity more than benevolent kindness; kind/gracious remain
disclosed alternatives. A separate [contextual source and full-record review](../sources/textual_restoration/applications/psalm145_editorial_review.2026-10-04.v1.json)
approved the exact candidates provisionally. Neither review was blinded
manuscript observation, a human review or a measured improvement benchmark.

Verse 17 keeps its Hebrew source and now renders the repeated phrase identically.
Its earlier assertion that Greek *hosios* or English holy necessarily implies
different Hebrew wording is removed. Greek can interpret Hebrew חסיד;
translation glosses do not become consonantal variants. Both records preserve
generation objects, prior revision history and archived old reviews, while
active status remains draft/needs-review. No stale score approves the new text.

The [application receipt](../sources/textual_restoration/applications/psalm145_nun_application.2026-10-04.v1.json)
records exact source/review/composition bindings and actual reader verification.
Historical preparation flags are not current selection/application status;
the production source record itself supplies no publication authority.
General automatic drafting still defaults to the original book edition; this
pass verifies the explicit critical-source lookup/integration and affected
reader, not an unimplemented corpus-wide drafting override. Earliest-form
questions reopen only for discriminating witnesses, insertion evidence or
actually consulted literary/transmission arguments. Genizah abbreviation,
unverified late margins and dependent Latin are not extra inclusion/omission
votes. ImageGen and fresh damaged-ink claims are unnecessary for this selection.
