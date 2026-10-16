# Ezekiel 4 numbers and the attribution of 11Q30 fragment 17

**Retain POB's 390 days provisionally; disclose the Greek difference.** The
[subsequent reader application](EZEKIEL_4_READER_APPLICATION_2026-10-16.md)
adds qualified numerical notes at 4:4, 4:5 and 4:9 and corrects anchors across
4:4–9. The source-research findings below remain unchanged.
Swete's main Greek text reads 190 days in Ezekiel 4:5 and
4:9. The proposed identification of 11Q30 fragment 17 with 11Q4 supplies an
edition-history lead, not independently verified numeral evidence. Neither
number's historical priority is established by this comparison.

## Published readings and the proposed fragment placement

The [display-alias audit](QUMRAN_RELEASE_COMPARISON_2026-10-16.md#follow-up-the-repeated-displays-are-now-explicitly-mapped)
established three repeated editorial blocks. Qumran-Digital's public variant
and commentary API now identifies the editions behind them. These are the
project's reports of editions, not new readings from manuscript photographs.

| Evidence | Finding | Consequence |
|---|---|---|
| DJD XXIII, p. 442, as reported in the [section commentary](https://lexicon.qumran-digital.org/v1/qumran/comments-to-bibligraphic-item/78/for-section-with-word/200823?database-date=2026-10-06) | The remnants were cautiously described as a possible quotation of Ezekiel 4:5–6. Metadata specifies 11Q30 frg. 17, lines 1–2. | An earlier content identification exists; it is not an assertion of a physical join with 11Q4. |
| [Token 803933](https://lexicon.qumran-digital.org/v1/qumran/word-variants/803933?database-date=2026-10-06) | The API attributes `י]שר[אל` to Puech 2019a, p. 229. The selected display has `]שר[`. | Preserve the distinction between the displayed transcription and the attributed variant. The complete word is not all surviving ink. |
| [Token 200827](https://lexicon.qumran-digital.org/v1/qumran/word-variants/200827?database-date=2026-10-06) | The API attributes `צ]דך` to Puech, p. 229, against the displayed `]○ך֯`; DJD's reported note discusses dalet versus final kaf. | This is a real published reading dispute, not just duplicate metadata. Neither rendering is adopted as our fresh decipherment. |
| [Token 200823](https://lexicon.qumran-digital.org/v1/qumran/word-variants/200823?database-date=2026-10-06) and [its metadata](https://lexicon.qumran-digital.org/v1/qumran/manuscript-word-reading-extended-details/200823?database-date=2026-10-06) | Both editions are cited for `]למספר`; the token's manuscript field remains 11Q30, internal ID 668. | Display under 11Q4 does not automatically change the token's manuscript attribution. |

The [project's Puech note](https://lexicon.qumran-digital.org/v1/qumran/comments-to-bibligraphic-item/9023/for-section-with-word/200823?database-date=2026-10-06)
explains that new readings of previously known fragments enter as variants,
whereas newly edited fragments may supply the base text. It also says that
Puech does not use circelli and that his detailed comments were incorporated
selectively. Absence of a circellus in that derivative display therefore does
not establish certainty. The API's `readingIsAssumed: false` is an editorial
data field, not independent authentication of the letters.

## The precise acquisition target

Émile Puech, “Nouveaux menus fragments de la Grotte 11Q (P1344, P1345 et
P1038B),” in Jean-Baptiste Humbert and Marcello Fidanzio, eds., *Khirbet Qumrân
and Aïn Feshkha IV A*, NTOA Series Archaeologica **8a** (2019), pp. 203–229,
especially p. 229; [chapter DOI](https://doi.org/10.13109/9783666564697.203).
The API's series value “4a” conflicts with the publisher preview's visually
checked series page. Use 8a; preserve the API response hash rather than silently
rewriting acquired data. The [publisher preview](https://www.vandenhoeck-ruprecht-verlage.com/downloads/productPreviewFiles/LP_978-3-525-56469-1.pdf)
also verifies the chapter title and starting page, but its 26 pages do not
include the target discussion.

A [search-indexed excerpt of the book](https://dokumen.pub/khirbet-qumran-and-an-feshkha-iv-a-qumran-cave-11q-archaeology-and-new-scroll-fragments-1nbsped-9783666564697-9783525564691.html)
reports Puech's proposal to combine revised traces from 11Q30 frg. 17 with
11Q4 frgs. 2 and 3a into five lines of Ezekiel 4:3–6, about 13 cm wide. It
reports an argument favoring the Hebrew number over the Greek and references
different line-length estimates in DJD XXIII, pp. 18–21. This is an acquisition
lead, not a verified layout calculation: the full Hebrew reconstruction and
photographs were not available. The publisher browser explicitly showed
“NO ACCESS” and no figures; the mirror body fetch returned 403. No restriction
was bypassed. Obtain the complete discussion and relevant plate, alongside
DJD XXIII p. 442 and pp. 18–21, before evaluating the proposed placement.

## Direct Greek edition control

Swete, *The Old Testament in Greek*, vol. III, third edition (1905), printed
pp. 390–391 / PDF pp. 414–415, was visually checked including the complete
apparatus. The [source manifest](../sources/lxx/swete/MANIFEST.md) identifies
the exact public-domain scan. This is direct consultation of an edition,
not fresh inspection of Codex Vaticanus itself.

| Passage | Swete main Greek text | Control |
|---|---|---|
| 4:4 | 150 days | `πεντήκοντα καὶ ἑκατόν` |
| 4:5 | 190 days | `ἐνενήκοντα καὶ ἑκατόν`; also `δύο ἀδικίας` |
| 4:6 | 40 days | `τεσσεράκοντα` |
| 4:9 | 190 days | `ἐνενήκοντα καὶ ἑκατόν` |

At 4:5 the apparatus additionally reports 390 with `οἱ λοιποί` and the siglum
`Qmg`. This is a marginal report about “the others,” not itself another
continuous-text Septuagint manuscript reading 390. Do not expand it into
particular translators or manuscripts without the relevant explanatory
conventions. The verified claim is that Swete's main Greek text reads 190 and
its apparatus also reports 390, not that all Greek evidence agrees on 190.
The differences in 4:4–6 and 4:9 belong to a wider numerical and interpretive
context; a single numeral cannot settle which textual form came first.

## Consequence for POB and next decision

At this research pass's baseline, the [Ezekiel 4:5 record](../translation/ot/ezekiel/004/005.yaml) retained
the WLC Hebrew and translated 390 days. Its one footnote concerned the meaning
of iniquity, not the numerical difference. The existing model-agreement score
did not constitute review of this manuscript question.

The initial reader-note proposal was:

> The Greek text represented by Codex Vaticanus in Swete's edition reads
> “one hundred and ninety days.” The Hebrew text has “three hundred and
> ninety days.”

This note proposed disclosing a verified edition difference without deciding
historical priority or implying that 11Q30 preserves either numeral. The scoped
application was to check 4:4–9, place the number note at “ninety days,” move
the existing lexical note from “days” to its actual iniquity phrase, archive
prior review metadata, and verify the actual reader export. These checks and
the resulting notes are now recorded in the linked application above. The full source
and main English remain unchanged. No ImageGen output
or canon claim supplies evidence.

## Evidence and review record

The [receipt](../sources/textual_restoration/discovery/11q4_edition_attribution.2026-10-16.v1.json)
pins the six API responses, publisher preview, Swete scan and rendered pages,
and the current POB target. Raw third-party files remain outside Git. The
`lang=en` word-detail request returned a parameter error; the working URL omits
that optional parameter. No failed response is treated as source data.

An independent reader located the edition references and visually confirmed
the four Greek numbers. The review narrowed the Qmg claim to a marginal report
rather than an independently read continuous-text witness. The next source
task is the complete Puech/DJD reconstruction evidence; the reader-note
candidate is separately actionable on the verified Greek edition difference.

The final bounded report/receipt review passed with no factual corrections.
All 13 recorded byte counts and SHA256 values and all three API variant
projections match the retained inputs. The 39 display-alias, release-comparison
and published-parallel-index tests passed; these test data handling, not the
historical priority of either numeral. All 512 relative links in the four
affected reports resolve. The canonical 4:5 record and protected unrelated
Genizah input remain unchanged; `git diff --check` passes.
