# Complete 1 Enoch repair: progress, not completion

The objective remains the **entire 108-chapter POB translation**, not merely
its presently flagged verses. A chapter/file count, old acceptance label or
green mechanical test is not evidence that all its source, English and notes
are correct. Historical accepted packages must be audited before deciding that
they require retranslation. This work does not certify an autograph or fresh
independent manuscript collation, nor authorize Graphic Bible publication.

## Second bounded application

35 exact selected-edition units have been installed locally after source,
English and note checks by an author and a separate source reviewer:
**36:1–4; 37:1–5; 38:1–6; 39:1–14; 45:1–6**. Ten were missing records:
36:3–4; 37:5; 38:5–6; 39:11–14; 45:6. The 902-record application receipt
proves all unrelated canonical files were unchanged at application time.

The exact [application package](../sources/textual_restoration/applications/enoch_full_repair_batch02_20261020/)
retains candidates, accepted inputs, reviews, provenance and primary-image
hashes. Source PDF SHA-256 is
`505f248c667cebd5136991d7c570841a0a3ed9396d5b28b85bf07f4a3957053e`.
All five complete printed chapter inventories were checked. These are
independent editorial assessments of one selected edition, not independent
ancient witnesses; disclosed prior-opinion exposure means not all reviews are
blind. Actual generating model versions/full prompts were not reported.
Integration hashes are explicitly integration metadata, not invented raw-model
drafting receipts. Old oracle-derived wording is retained by existing Git
blob/hash references instead of being copied into new artifacts.

Material corrections include:

- 36:4 retains the people/angels/spirits as praising agents and the work/deeds
  as objects. 36:2 no longer inherits a whole-chapter oracle source.
- 37:4 restores the wisdom and eternal-life continuation.
- 38:1 diplomatically preserves the printed anomalous numeral-shaped final
  glyph in **ቀዳማ፲**. A note distinguishes the contextual rendering “first
  parable” from silent normalization to **ቀዳማይ**; the cause is unknown.
- 39:7 reads **ይትለሐዩ**, not OCR **ይትሰሐዩ**. Dillmann1865 column33
  explicitly cites this verse for the sense “shine/be radiant.”
- 39:10 restores the complete first-person blessing and praise. Primary
  Dillmann1865 columns1181–1182 support “For a long time” for **ጕንዳየ**.
  The malformed word-shaped note label is gone, not exported as a fake note.
- 45:3 retains Charles's corruption marker rather than silently substituting
  his proposed reconstruction. Dillmann1865 column383 explicitly cites45:3
  for invoking/seeking help, distinct from the separate accusation sense.

Critical stars, daggers and brackets remain source signs, with relevant
editorial supplies/reported variants distinguished in notes. Exact title
spellings **መንፈሳት** are preserved rather than normalized to familiar OCR.

## Current issue inventory and next repairs

The fresh [verse register](../sources/enoch/coverage/editorial-issues-batch02-20261020.md)
and [hash-bound JSON](../sources/enoch/coverage/editorial-issues-batch02-20261020.json)
report **14 absent records under declared counts**, **144 parser-derived
absent-unit leads**, **47 source-alignment signals**, **5 explicit oracle-source
policy leads** and **8 selected-witness/source mismatches**. Categories overlap
and must not be summed into a mistranslation count. Correct scan transcriptions
can still differ from damaged OCR; those signals need adjudication, not a
return to OCR. A stale witness echo likewise is not automatic proof the chosen
running source is wrong.

Declared absent records remain 18:12–13,16;22:14;24:5–6;25:6;28:2–3;
32:6;34:2–3;84:6;97:10. Genuine lexical/glyph holds remain unpublished.
The separate Chapter97 lane and its dirty checkout are untouched. Chapter84's
existing no-partial-install restriction remains in force.

The [104–108 printed count/address audit](../sources/enoch/coverage/count104-108-20261020/inventory.json)
found a material addressing defect:104 has13 units,105 has2,106 has19,
107 has3 and108 has15. Present105:1 continues104:1, while present105:2–11
contains104:2–11. The real105 starts at printed219/PDF257. Repair requires
complete reviewed104/105 replacements, a bounded retirement/relocation map
for incorrectly addressed records, and parser/export count corrections.
This discovery is not permission to move unreviewed English blindly.
106:14 is clipped across a page, and107:1 has whole-chapter oracle source
despite unit-only English. Review of these and the astronomical section
continues. The explicit remaining oracle-origin leads are4:1,50:1,51:1,
70:2,107:1.

A fresh exact-glyph check also found that63:7's previously accepted source
title should read **መንፈሳት**, not its installed **መናፍስት**. The negative-clause
repair remains separate from this spelling defect. A new reviewed superseding
application is required; historical acceptance is evidence, not infallibility.

The [108-chapter progress snapshot](../sources/enoch/coverage/full-repair-progress-batch02-20261020.json)
imports exact current evidence for50 units (the previous15 plus these35),
with five complete selected-edition chapter reviews. This is a conservative
evidence-import count, **not** a claim that every other existing unit is bad.
Unimported historical packages still require audit. Full-book completion is
explicitly false until all requirements below pass.

## Reproduce and finish

```sh
python3 -m tools.enoch.bounded_application verify-applied --package enoch_full_repair_batch02_20261020
python3 -m unittest discover -s tests -p 'test_enoch*.py'
python3 -m tools.enoch.full_repair_progress --output state/enoch-full-repair-progress.json
```

The full-book gates are: independently checked108 chapter boundaries and
counts; accepted evidence for every actual current source/English/note payload;
corrected addressing, clipped/combined units and unsupported wording; resolved
true holds or defensible reviewed critical treatment; final schemas, notes,
exports and regression checks; changes on main and exact canonical/public
delivery; and a requirement-by-requirement completion audit. No narrow test
suite substitutes for these gates.

The mobile export now adds exactly36,37,38,39,45 with their full reviewed unit
counts and notes. Other mobile chapter payloads are unchanged. Mobile export
completeness is not the CDN's policy: the base public CDN can include partial
chapters and strips footnote anchors/notes. Public English matching, repository
note preservation and actual reader-note UI verification are distinct checks.
At this snapshot this second application is local, not yet a verified public
deployment. Publication evidence must be recorded separately after CI/merge.

Local validation passed all146 Enoch tests, including transaction rollback,
artifact/preimage rejection, exact35-unit review bindings, ten additions,
the108-chapter progress limits and the full mobile-export comparison. An older
verifier weakness was fixed: installed targets are now byte-compared even when
not requesting a frozen whole-corpus check. A regression test deliberately
changes an installed fixture and verifies rejection. No actual prior15-unit
application drift was found by the separate current hash checks.
