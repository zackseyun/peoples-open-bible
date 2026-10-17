# 2 Samuel 21:8 — Hebrew witness identities and released source data

Date: 2026-10-17. Source-access follow-up; no canonical application.
Baseline: `eef183dd5e408dde3c05338770af176c6fcecd88`.

## Outcome

The [preceding comparison](SAMUEL_21_8_MOTHER_COMPARISON_2026-10-17.md)
established reported Merab readings in Kennicott 198 and 250, not their
present identities or original hands. This follow-up identifies the relevant
collections, corrects an overly broad loss claim, and locates released
machine-readable Kennicott data. It does **not** provide fresh mother-name
pixels, establish independence or choose earliest Hebrew Michal versus Merab.
The provisional retention of Michal remains unresolved, not newly confirmed.
No Hebrew, English, approval, reader note or canon change is applied.

## 198: Nuremberg's seven-volume Bible

Kennicott's actual 1780 *Dissertatio*, printed 88 / combined PDF 1541, describes
198 as Nuremberg's formerly Solger seven-volume public-library Bible and reports
AM 5051, corresponding to 1291. Root read extracted catalogue pages 88–91 and
visually inspected complete 88 and 91. The initially downloaded standalone
volume lacked this appendix; it is not evidence for these identifications.

The [NLI combined institutional record](https://www.nli.org.il/en/discover/manuscripts/hebrew-manuscripts/itempage?docId=PNX_MANUSCRIPTS990001899400205171-1&scope=PNX_MANUSCRIPTS&vid=MANUSCRIPTS)
explicitly identifies Kennicott 198, seven volumes, 1291 and Ashkenazic script.
It reports missing leaves in every volume. Its microfilm F10164 covers Joshua
through 1 Kings 13:7. The combined record's header is not itself the Samuel
volume identifier; reported dates are not fresh colophon or target-hand readings.
The retained NLI file is a complete normalized web-reader response, not native
HTML or manuscript image bytes.

Digital Kennicott's full K198 witness node maps the Former Prophets portion to
**Ms. Solg. 3 fol.** and [owner image route 07098004](https://online-service.nuernberg.de/viewer/image/07098004/8/).
It describes Joshua–1 Kings **12:7**, differing from NLI's **13:7**. This is a
project-reported volume locator, not an owner-verified folio or proof that
2 Samuel 21:8 survives there. All seven publicly linked owner image routes
returned 403 in the ordinary access checks; NLI marks its viewer library-only.
No authentication or restriction bypass was attempted. Stop retrying those
same routes without a genuinely new public access path.

## 250: Turin A.IV.3, partially surviving

Kennicott's printed 91 / combined PDF 1544 calls 250 Turin 5, royal-library 110,
Prophets and Writings except Megillot, and reports AM 5095 / 1335. His script
description is Hispanic. The [Turin institutional record of Peyron's note](https://archiviodistatotorino.cultura.gov.it/fe_fonti_dtl/?id=71)
explicitly connects **A.IV.3**, old Pasini **A.III.5**, with Kennicott **250**.
That record concerns Habakkuk 3:8/11; the original archival note and its codex
pages were not inspected. It establishes a catalogued identity, not our reading.

The [institutional manuscript inventory](https://archiviodistatotorino.cultura.gov.it/fe_item_dtl/?id=66)
reports 499 original leaves and **15 current surviving leaves**, unrestored,
all with mutilated text, some fragmentary or partly darkened. Its script label
is square Ashkenazic, unlike Kennicott and Digital Kennicott's Sephardic (?);
this discrepancy is recorded, not settled by counting catalogue authorities.
The [inventory source record](https://archiviodistatotorino.cultura.gov.it/fe_fonti_dtl/?id=16)
dates that database to 2017. Root read the complete target records.

Consequently, Digital Kennicott's unqualified statement that 250 was destroyed
in the 1904 fire is insufficiently precise. Partial survival does **not** mean
that 2 Samuel 21:8 is among those leaves. No passage inventory or target image
was found. A public image label **Hebr. IV.3** cannot simply be equated with
**A.IV.3**.

The [Dershowitz key](https://dershowitz.net/kennicott), actual PDF page 13 read
visually by root and source reader, routes 246–251 to **Parma 2874 / De Rossi
1302**, an eighteenth-century collation of six Turin manuscripts, not the
original biblical codices. Its all-lost wording requires the same qualification.
Both tested NLI 83876 routes returned 403. No actual collation page or target
hand was read; this surrogate is not an extra ancient Hebrew vote.

## Digital Kennicott: useful retrieval, bounded verification

The [project](https://www.digitalkennicott.unito.it/) links a
[released edition](https://www.edition-digitalkennicott.unito.it/exist/apps/dike/books.html).
Root followed its public API documentation using GET requests only. The
[DTS document collection](https://www.edition-digitalkennicott.unito.it/exist/apps/dike/api/dts/collection?id=documents&per-page=50)
contains 41 members: **39 biblical book documents plus two auxiliary/demo
documents**, `taxonomy.xml` and `registers/keywords.xml`. Root inspected all
member names/titles but downloaded only the biblical **2 Samuel** source, not
all 39 books. The outer DTS root's `totalItems: 0` is not absence of book data.

The [actual 2 Samuel TEI XML](https://www.edition-digitalkennicott.unito.it/exist/apps/dike/api/document/009_2sam.xml)
has separate Hebrew source and Latin apparatus layers. At `app loc="2 Sam 21:8"`,
the mother-name lemma and readings are:

| XML component | Value | Evidential status |
| --- | --- | --- |
| `lem/w` | מיכל | Edited base, not earliest-Hebrew judgment |
| `rdg wit="#K172" / term ref="#caret"` | ‸, no Hebrew name word | Reported omission, not Merab |
| `rdg wit="#K198" / w` | מירב | Derivative report of Kennicott 198 |
| `rdg wit="#K250" / w` | מרב | Derivative report of Kennicott 250 |

This exact sample matches the prior visual printed-apparatus reading. The full
K198/K250 metadata nodes were also read. No all-book or all-apparatus accuracy
claim follows. A future retrieval tool must preserve omission/erasure/
transposition terms and witness IDs, not merely extract Hebrew word strings.
The new catalogue discrepancies demonstrate why local source verification
remains necessary even when the sample text is correct.

The edition identifies **CC BY-NC-SA 4.0** terms. Its XML is retained privately
for consultation, not vendored into POB or automatically imported into the
source corpus. Establish compatible reuse before any such integration. For
now, use it to locate candidates and verify them against actual source editions;
do not spend resources recreating its entire OCR pipeline.

## Decision, scope and next discriminating input

Two user-authorized source readers pursued the independent 198 and 250 access
questions while root consulted the original catalogue and released data.
Root's bounded XML check uses `lem/w`, preserving non-word symbols; an initial
whole-lemma whitespace match was not a passing check. No new parser, test
infrastructure, full-book export, image-generation run or translation edit was
needed. The [source packet](../sources/textual_restoration/comparisons/samuel21_8_hebrew_witnesses.2026-10-17.v1.json)
pins consultation bytes and records exactly what was and was not read. The
earlier dossier and its independent review remain frozen historical records.

Next useful evidence is an actual accessible 198 Samuel leaf and hand assessment,
a passage inventory of 250's 15 surviving leaves, a relevant existing pre-fire
capture, or the actual Parma collation target. A collation alone would still
not establish original-hand status. If those are unavailable, pursue a new
consequential comparison through accessible editions rather than repeat these
failed routes, the same article, or another agreement loop. No numerical
confidence, comprehensive-source claim, new recovered letter or canon inference
is justified by this access result.
