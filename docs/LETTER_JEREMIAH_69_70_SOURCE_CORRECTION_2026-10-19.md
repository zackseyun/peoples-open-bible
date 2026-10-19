# Letter of Jeremiah 69–70: correct the transcription before comparing sources

Date: 2026-10-19. Baseline: `b388ce5089ea64ecd3adac354dbd1118c7dbea85`.

## Finding and proposed contribution

Two POB Greek transcription errors have affected the English. Swete III's
selected printed text has **προβασκάνιον**, a protective object, in verse 69,
and **ῥάμνῳ**, a thorny shrub, in verse 70. POB instead stores malformed
`προβάσκάινόν` and `βάμψῳ`. Its English drops the first object into an
unwatched cucumber patch and makes the second object another scarecrow.
Verse 70 also inserts `τῷ` before `νεκρῷ`, absent from the selected printed
line. Restore the complete selected lines, not just the two conspicuous nouns.

The proposed English preserves two distinct comparisons: a scarecrow that
guards nothing, then a thornbush on which birds sit and a discarded corpse.
This is a substantive correction to **our transcription and translation**,
not a new manuscript discovery, a Greek emendation, a recovered Hebrew
original, or evidence that changes Jeremiah 10's historical priority.

## Actual evidence and consultation limits

Root read the complete Letter in the PDF's extracted text, printed 379–384 /
one-based PDF 403–408. Root visually checked the complete target page 384,
including both full verses and apparatus, and the volume's title/edition and
siglum controls. This is an edition scan, not manuscript photography. The
[manifest](../sources/lxx/swete/MANIFEST.md) identifies the exact 932-page PDF,
SHA-256 `5f0bfffabf0e588fd32e15bdb24b027872616da219e7f02da3dbdc115cf97d85`.
The volume is the third edition, **1905**; `lxx-swete-1909` is a retained legacy
project identifier, not a newly verified imprint.

Printed 384 is one-based PDF 408, zero-based archive leaf 407. The existing
[page receipt](../sources/lxx/swete/transcribed/vol3_p0407.meta.json) links
[that actual scan leaf](https://archive.org/download/theoldtestamenti03swetuoft_202003/theoldtestamenti03swetuoft/page/n407_w1500.jpg).
The old page transcription and final corpus contain the same corrupted words.
They are dependent stages in one pipeline, not independent witnesses agreeing.
The raw historical page transcription/receipt remain unchanged. Correct only
the two final-corpus records used by the live source loader, preserving their
old records in correction history, and the corresponding canonical YAMLs.

Root and one bounded lexical scout each read both complete primary LSJ entries:
[προβασκάνιον](https://atlas.perseus.tufts.edu/dictionaries/entry/urn:cite2:scaife-viewer:dictionaries.v1:lsj-n86775/)
allows an apotropaic protective object or field scarecrow;
[ῥάμνος](https://atlas.perseus.tufts.edu/dictionaries/entry/urn:cite2:scaife-viewer:dictionaries.v1:lsj-n92149/)
covers several thorny shrubs, not a watch-figure. Generic **thornbush** avoids
an unsupported botanical species identification. LSJ's Letter citation is
numbered 70; align the Greek words, not an assumed universal verse number.
The scout also checked the underlying Perseus TEI at commit
`56061ca127f4a2844980baffc5f2b6d1332897b3`; root did not separately read that XML.
No modern English Bible supplied candidate wording.

In verse 69, the neuter noun and agreeing participle `φυλάσσον` retain a
protective figure as subject; `οὐδέν` is what it guards. The old English
misplaced the negative sense by deleting the object of comparison. The
apparatus reports a different participial ending in A and spelling variation
in the cucumber-patch word. In verse 70, its A alternative does not support
POB's malformed shrub word. B, A and Q are the volume's Vaticanus,
Alexandrinus and Marchalianus sigla. Selected body text, apparatus and editor
are not three manuscript votes. This correction does not certify every
apparatus reading or reconstruct the earliest Greek.

## Jeremiah 10 reception: a useful argument, not a recovered exemplar

Root and a bounded access scout read the complete public text rendition of
Benjamin D. Thomas, “Reevaluating the Influence of Jeremiah 10 upon the
Apocryphal Epistle of Jeremiah: A Case for the Short Edition,” *ZAW* 120/4
(2008), 547–562, including notes, at the
[author upload](https://www.academia.edu/855737/Reevaluating_the_Influence_of_Jeremiah_10_upon_the_Apocryphal_Epistle_of_Jeremiah_A_Case_for_the_Short_Edition)
linked by his [author profile](https://chicago.academia.edu/BenjaminThomas).
DOI: [10.1515/ZAW.2008.033](https://doi.org/10.1515/ZAW.2008.033).
This was **not** native-PDF or visually verified Greek/Hebrew table access;
the online rendition corrupts some original-language glyphs. No local PDF
was acquired and no PDF hash is claimed. Publisher access returned 405 and
the download attachment was restricted; neither was bypassed.

Thomas argues that the Letter reflects only the shorter Hebrew Jeremiah
edition. Pages 552–556 compare shared anti-idol material; 557–560 answer
alleged long-form indicators by considering alternate Hebrew interpretation
and parallels elsewhere. The shoulder-bearing image has an Isaiah 46:7
control, and inability to speak occurs in Psalms 115/135. Weather/creation
language is not exclusive to the long praise units. Pages 560–561 argue that
selective avoidance of positive praise is an inadequate explanation because
the Letter nevertheless uses positive creation language. These are original
arguments actually read, not conclusions inferred from the article title.

The argument weakens a categorical claim that the Letter's scarecrow requires
the long Masoretic form. It does **not** uniquely identify a short exemplar:
shared material and absence of an unmistakable allusion can also result from
selective adaptation of a longer text. Proposed alternate Hebrew glosses,
an original Semitic Letter and a specific source dependency remain
reconstructions, not recovered Hebrew manuscript letters. Do not adopt its
individual retroversions as an established Vorlage. Retain the separate
[Jeremiah reconstruction control](JEREMIAH_10_RECONSTRUCTION_CONTROL_2026-10-19.md)
and historical-priority HOLD. No Jeremiah canonical record changes here.

Ancient circulation, dependence on a biblical book and canonical authority
are separate questions. This work neither adds a book to a canon nor proves
an all-community canonical boundary. It improves a text already present in
POB's deuterocanonical track. The circulation question needs its own verified
manuscript and reception evidence; do not confuse Greek Deuteronomy 4Q122
with a Letter of Jeremiah witness.

## Bounded application and reader presentation

The [complete candidate](../sources/textual_restoration/candidates/letter_jeremiah_69_70.2026-10-19.v1.json)
contains both replacement YAML records and both final-corpus records.
Archive old source, translation, lexical/theological explanations, status,
revision pass and cross-check without inheriting approval. Keep original
AI-draft metadata and earlier revision history as history. The updated
records remain draft/needs-review; medium source confidence and a scoped
correction label are not a publication or whole-verse certification.
Unchanged lexical entries retain historical labels, not new consultation.

Use the existing single footnote in each verse. Verse 69's brief note preserves
the protective-charm alternative; verse 70's notes the narrower buckthorn
rendering. Move the existing anchor to the relevant phrase. Do not add
inline scholarly paragraphs, a new panel, publisher changes or reader-layout
code. The user's clutter concern is part of the application boundary.

The focused regression must validate both complete YAML records, exact old
field archives, and only the specified field changes. Compare all 72 baseline
Letter files and final-corpus records; exercise the actual source loader and
whole-Letter exporter. Only verses 69–70 may change in export, with every
other unit and book metadata unchanged. A fresh independent factual and
application reviewer must check the exact candidate before canonical
application. Actual execution, reviewed hashes and delivery status belong
in the [application receipt](../sources/textual_restoration/applications/letter_jeremiah_69_70.2026-10-19.v1.json),
not an invented historical approval. CI/main integration is a separate gate;
repository correctness does not establish live website delivery.

## Method lesson

This is worthwhile, bounded work because a reproducible source error changes
two actual comparisons. The earlier high-agreement labels did not catch it;
another vote on the corrupted text would not establish the printed reading.
Before literary-source inference, check the actual source object and its
connected grammar against the named edition. Stop when the bounded delta is
verified; do not turn a transcription repair into a claim about new biblical
originals or canon expansion. The PDF workflow supplied page-level checks;
the documentation workflow keeps evidence, inference, application and access
limits explicit in the existing Git record.
