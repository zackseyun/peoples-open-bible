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
