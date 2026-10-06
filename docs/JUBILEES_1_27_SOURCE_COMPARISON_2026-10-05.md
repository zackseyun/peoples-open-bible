# Jubilees 1:27: recording roles, source limits and reader delivery

## Outcome

Against baseline `1505a6179adc31f2144ca797aea4de2d44171b85`, retain POB's
Geʿez source and main English; hold a Hebrew-priority or different-writer
claim. No new verse note is applied. The published Hebrew causative is a
real comparison lead, not newly recovered letters. It does not by itself
identify the person physically writing. This case does not establish a
different narrative, novel discovery or reason to enlarge a canon.

Separately, fix the extra-text exporter, which retained inline footnote
markers but omitted their bodies. Reuse its existing anchored-note helper
for both nested verse files and chapter-derived units. This delivers existing
notes; it does not adjudicate their accuracy or repair historical bad anchors.

## What was actually inspected

Root read Qumran-Digital's own column IV lines 3–10 and column V lines 1–14,
excluding embedded biblical controls. The versioned
[4Q216 transcription](https://lexicon.qumran-digital.org/transcriptions/4Q216/2026-05-21/index.html?v=2026-05-21)
places the causative spelling outside supply brackets in IV.6, with its he
marked uncertain. The identification/introductory wording before it and Moses
in IV.7 are substantially supplied. In V.1, the imperative often invoked to
identify Moses as recorder is itself inside supply brackets. These are a
modern published transcription's readings and restorations, not root's
independent observation of ancient ink. No manuscript photograph was
deciphered in this case.

Root also viewed complete native PDF pages 39–40 (printed pages 3–4) of
[Charles's 1895 Ethiopic edition](https://archive.org/download/CharlesEthiopicJubilees/The_Ethiopic_version_of_the_Hebrew_Book.pdf).
Printed page 4 has Geʿez `ጸሐፍ` at 1:27, with no attached variant note on that
word in the displayed apparatus. That silence does not establish agreement
among all surviving Geʿez manuscripts or the modern critical edition.
Charles is a printed critical edition, not one ancient manuscript.

| Consulted input | Size / SHA-256 |
|---|---|
| Versioned 4Q216 HTML | 154,999 bytes; `287414dbc053bc15397c1da0dc75dc568050338fddd52fa21ccd988181d75431` |
| Charles 1895 complete PDF, matching the repository manifest | 10,339,546 bytes; `2883e2c68247c2b3172467bfaaa9147901a6b88b18f28e5ad3a7cc2c20636dfe` |
| Unchanged chapter record, `translation/extra_canonical/jubilees/001.yaml` | `362b2aee79d6e0e73df2519269ad24d3453a9ad68c3b9ad5cf862a91abc48fbd` |
| Unchanged reader verse, `translation/extra_canonical/jubilees/001/027.yaml` | `3ac7751f4615585588cd10dde5e349a5b3833626fedf3da794528d9966d09253` |

The source files were consulted privately, not newly committed to the corpus.
The earlier locator agent's single Charles image is a separate derivative;
root's present inspection used the complete manifest-matching PDF.

## Competing explanations and decision

The Hebrew causative supports cause to write; dictate is a possible English
interpretation. A command to write for Moses could describe the same mediated
recording process, however. Neither grammar alone nor a largely restored
context proves that Moses, rather than the angel, physically writes. An
earlier categorical changes-the-writer interpretation is therefore too strong.
This is an interpretation to test, not an established narrative correction.

Before promoting a Hebrew reading, distinguish uncertain ink from editorial
supply, compare the complete local Hebrew context, and check manuscript-specific
Geʿez evidence rather than retrovert Charles's English. The present evidence
does not justify replacing the retained Geʿez-based source, changing English
to dictate, or appending a confident different-writer note. Conversely, retain
does not prove that the Geʿez form is earlier or that the existing translation
has been approved by a specialist.

Versification matters: Charles's printed 1:28 begins with the sanctuary
clause. POB's current reader 1:27 includes that clause and continues through
the Lord appearing to everyone's eyes. Compare content spans, not identical
verse numbers. Root inspected both the chapter and reader YAMLs: their English
segmentation and wording differ. The chapter is labelled authoritative, but
the reader verse carries a later revision not present in that chapter.

The existing `tools/jubilees/split_into_verses.py` regenerates verse records
from chapter data and can overwrite later per-verse revisions. It was not run
on the repository. Existing chapter notes also have imperfect anchors. No
blanket reapproval, bulk regeneration or bespoke overlay framework was added
to force a reader application from this held case. Before a future application,
identify the authoritative content span and preserve later revisions and
review provenance when synchronizing chapter and verse records.

## Missing evidence and bounded acquisition

A source assessor checked lawful routes for the primary apparatus. The
[1991 preliminary publication](https://doi.org/10.2307/3267085) was identified,
but its JSTOR route exposed a shell rather than readable article pages. A
Brill reprint route did not supply the text; the proposed chapter suffix was
not verified. A proposed HUJI file returned error HTML, not a verified PDF.
Peeters's catalogue identifies CSCO 510 (ISBN 9789042905511) and 511
(9789042905528), but no target manuscript apparatus was obtained. No purchase,
restricted-access bypass or unsupported claim of consultation followed.

Reopen for DJD XIII printed pages 11–12, especially IV.6's note and associated
plate, and the actual Jubilees 1:27 text/apparatus in CSCO 510 plus the
translation note in CSCO 511. Their exact modern Geʿez printed-page locators
remain unverified. If those controls do not discriminate, retain the hold;
do not repeat unchanged access failures or seek more agreeing model reviews.

The separate Exodus 20:21 speech-verb hold also remains. A lawful JSTOR route
for Strugnell's Notes en marge returned a JavaScript client challenge, not
article pages; the identified DJD V archive item was access-restricted, the
OUP page had a robot check, and the Orion route had a certificate/redirect
failure. No TLS disabling or access bypass was attempted. Its reopening
inputs remain DJD V pages 1–6/plate I and Strugnell pages 168–175, not a new
download of the same secondary controls.

## Reader-delivery repair and verification

The exporter change uses `reader_footnotes(record, emitted_unit_text)` after
each unit's segmentation. Only real note bodies whose normalized marker is
present in that unit are emitted. Source brackets do not manufacture notes;
unanchored/background notes stay excluded. Existing text, numbering gaps,
metadata, editorial-section labels, Jesus-word ranges and no-note JSON shapes
are preserved. The canonical export path is unchanged.

Complete exports were compared with baseline
`2c44226ca449a084beb8accf2cf60ba9661e21b7`, whose exporter is identical to
the merged baseline above:

| Book | Chapters / units | Units gaining notes | Notes emitted |
|---|---:|---:|---:|
| Jubilees | 50 / 1,154 | 421 | 541 |
| Gospel of Truth | 16 / 55 | 21 | 28 |

Removing the added footnotes gives exactly the old complete parsed JSON for
both books. Every added marker occurs in its corresponding unit. All 1,204
Jubilees and 16 Gospel of Truth YAML files stayed byte-identical. Note counts
are delivery measurements, not hundreds of newly validated textual findings.

Export hashes use SHA-256 of `json.dumps(payload, ensure_ascii=False,
sort_keys=True).encode()`; these measurements were independently reproduced
by root after the engineering task:

| Book | Before / after complete export SHA-256 |
|---|---|
| JUB | `4b440e7ece0df84b5fa210e02a54aa0f8879df6fde724279ebbbca55fda46414` / `79f9bcc08061ca3e1f41477bff8dc4da96fc516641a0f3b412f55b0b7f5a32dd` |
| GOSTR | `7585fc6acc3e7b4f1c2d34935bb856c33f3208612ff55be1584b62676ac4289f` / `134957acf2dddbfc85b61a59b7ad176d51f3b1d18b4f9fec89e3442e77389e42` |

Nine focused synthetic tests cover both storage layouts and all four chapter
split routes, anchoring, normalization, malformed notes, source non-mutation,
metadata/annotations and final JSON. Twenty-eight existing footnote regression
tests and seven existing zero-fixture extra-text tests also pass. The latter
were called directly because pytest is unavailable; no dependency was installed.
The new unittest command is included in the existing integrity workflow.
Root also ran the complete reader-corpus validator with malformed YAML treated
as errors. That guard checks parsing and duplicate/mirror regressions; it is
not full verse-schema validation or scholarly source approval.

One fresh bounded independent critique checked the stored Hebrew context,
native Charles page, chapter/reader drift, splitter and exporter patch, and
independently passed the nine new and 28 old tests. No substantive blocker
was found. Its wording correction distinguishes retained source/English from
the recording-role hold. No repeat agreement loop or approval of existing
note content followed.

## Additional institutional control

Monger's 2018 dissertation is now available for private consultation through
its migrated [institutional record](https://hdl.handle.net/11250/2491963).
The publication API requires `Accept: application/json`; it identifies
`Monger_4Q216Free.pdf` as an OpenFile permitting download. Its public file-link
response provides an ordinary download alias. The retrieved PDF has 130 pages,
19,752,136 bytes and SHA-256
`22d9d733524631305b5b7316c2a7b63c517460cd18d290bb7889fc214f34b5e8`.
It remains a scholarly consultation, not a vendored ancient source or a
permissively licensed corpus input.

In printed pages 90–92 (PDF 96–98), Monger proposes a two-sheet reconstruction
containing shorter forms of Jubilees 1–2, lacking 1:15b–25 and likely 2:25–33.
This follows material/scribal reconstruction, not an independently verified
omission across an intact join. Ancient copying hands are not the narrative's
angel/Moses recording roles. The consulted outline does not adjudicate 1:27.

Root and one bounded source assessor inspected complete native TOC/context
pages and the transition after them. PDF pages 99–102 contain only the four
article title pages; page 103 resumes at printed page 219. The article bodies
named in the TOC are absent from this public version. Their measurements,
joins and alternative reconstructions were not directly consulted. Before
adopting the shorter form, obtain the actual material-analysis article and
photographic/geometry controls; test whether both shorter and fuller layouts
fit. For 1:27, the existing DJD/Geʿez controls remain necessary. No POB source,
English or canonical status changes follow from this additional control.

The original PDF URL redirected to a JavaScript landing page. The public JSON
record recovered the legitimate download route. A failed download also exposed
a missing earlier temporary output directory; a fresh `mktemp` directory and
the provided public alias succeeded. Do not misreport that local write failure
as denial of scholarly access or repeat acquisition of the verified file.

## Modern Ethiopic text and named manuscript control on October 6

The [new bounded control record](../sources/textual_restoration/comparisons/jubilees1_27_ethiopic_controls.2026-10-06.v1.json)
acquires a modern selected-text control and a named manuscript photograph. The
[TAU provenance page](https://www.tau.ac.il/~hacohen/Jubil/InformationVdK.html)
identifies its digital text as following VanderKam's 1989 edition and translation,
with his blessing, but explicitly omits apparatus and notes. Its
[chapter 1](https://www.tau.ac.il/~hacohen/Jubil/Jubil%201.html) selects `ጸሐፍ`
at 1:27, the same local word as Charles and POB; its English uses *Dictate*.
The English contrast therefore does not require a different Ethiopic word.
The translator's reason for that rendering is not available here; do not infer
his motive or treat the selected digital text as complete manuscript agreement.

The [British Library catalogue](https://searcharchives.bl.uk/catalog/032-003358960)
dates Or 485 to 1500–1599 and links its public IIIF manifest. The recording
command is located at f.3v, column a, lines 7–10, counting the first text line
as 1. Root and the acquisition agent inspect the complete-page derivative;
line 8 visibly matches the local `ጸሐፍ`, with Moses on the next line. This is
a report-aware image check with the selected word already known, not a blinded
transcription, newly recovered word or calibrated character-accuracy result.
The intact 2063×2500 image is private consultation input, hash
`689a5be70c28ea7f3e900109a672b3a37859fbe048845700f481c4d0f08aec9a`.
Native full-resolution transfers were incomplete; their failed outputs do not
support the reading. The complete-page derivative does, within this narrow scope.

Monger printed page 64 / PDF 70, note 184, identifies Or 485 as Charles B /
VanderKam 25. His limited Jubilees 1–2 comparison reports no textual differences
among the selected Charles/VanderKam texts and that manuscript, only spacing
and alignment. The surrounding paragraph acknowledges wider manuscript
variation. Root and the acquisition agent inspect the complete native page;
this is not the absent article material discussed above. Related editions plus
one manuscript cannot be counted as three ancient copies.

Modern digital 1:27 includes the temple clause; modern 1:28 starts the Lord's
appearance. Charles places the temple clause at 1:28, while POB reader 1:27
includes both clauses. Align the command and content, not verse labels. No
chapter regeneration or synchronization is performed.

The IAA's public 4Q216 search supplies 45 image metadata records over four
pages, including repeated plate/fragment exposures. These are not 45 witnesses.
The correspondence of its plate/fragment labels to published IV.6 is not yet
established; no Hebrew photograph is deciphered. The published transcription
retrieved for that correspondence has the same historical hash, not new
variant evidence. Bounded catalogue searches did not acquire DJD XIII's target
pages. Previously failed preliminary-publication routes were not retried.

Outcome: retain the Geʿez source and English provisionally; hold the physical
writer and source-priority decision. The modern control strengthens the known
word's attestation but leaves a real interpretive contrast. The published Hebrew
causative still deserves testing: a daughter version could obscure it. Neither
that possibility nor the modern English rendering substitutes for DJD XIII's
IV.6 note/plate, the actual CSCO apparatus and the translator's corresponding
note. No source, English, reader note or canon status changes follow here.

All new full texts, images and manifest remain private; the structured record
pins their hashes and separates selected editions, the named copy, reported
comparison, image limitations and the unresolved interpretation.
One bounded reporting critic finds no substantive blocker and verifies the new
controls; a continuation checks only four metadata-response hashes added during
review. Neither supplies a source-priority vote or specialist approval. The
unchanged canonical inputs, JSON syntax and reader-corpus guard are verified.

## Source selection and canon remain separate

Jubilees merits Hebrew/Geʿez comparison as a work with distinct literary and
reception history, not as another Genesis manuscript whose expansions should
be inserted into Genesis. The historical strategy's blanket 4Q216–228 label
must not be treated as thirteen interchangeable copies: for example,
[Fitzmyer's published discussion](https://www.bsw.org/biblica/vol-83-2002/the-sacrifice-of-isaac-in-qumran-literature/233/article-p215.html)
identifies 4Q225 as Pseudo-Jubilees and compares it with Jubilees rather than
simply counting it as the same work. This is a source-class correction,
not a complete reclassification of that numerical range.

The existing [six-work reception screen](OT_SOURCE_COMPARISON_CONTINUATION_2026-10-04.md#additional-works-worth-comparing)
remains the starting point. No community's canon, library order or book-list
status is changed. Ancient survival can justify comparison and illuminate
interpretation; it cannot alone establish inspiration or universal canonical
authority. This pass delivers a discriminating retain/hold decision and a
verified engineering fix, not a promised discovery from additional tokens.
