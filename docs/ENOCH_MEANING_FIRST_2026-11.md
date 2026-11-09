# 1 Enoch: meaning-first retranslation and restored verses (November 2026)

On 2026-11-09 1 Enoch moved to the same meaning-first aim as the rest of the
People's Open Bible (see [MEANING_FIRST_TRANSLATION_2026-11.md](MEANING_FIRST_TRANSLATION_2026-11.md)),
and the verses the earlier data had lost were restored.

## Why the method changed

From 2026-10-20 the book was repaired one verse at a time. Each verse went
through a source author, a frozen review packet, an independent reviewer, file
hashes, and a proof of what it replaced. That work raised the reviewed count
from 310 to 478 verses in its first week, then to 494 over the next two weeks,
as it spent its time on single disputed letters that a 1906 printed edition
cannot settle. 567 printed verses were still unreviewed, 93 had no file at all,
and the English kept the old source-surface philosophy that POB has now left.

The work splits into two layers with different needs:

- **Ge'ez source.** Keep R. H. Charles's 1906 edition as the base, keep every
  reading the 2026 source review accepted, and stop re-collating disputed
  letters. Where a reading is unclear, the English says so in one plain note.
- **English.** Translate every verse meaning-first from that source, in one
  pass, with whole-chapter context.

## Restored verses

The Charles 1906 page transcription
(`sources/enoch/ethiopic/transcribed/charles_1906/pages/`) was first split into
chapter files by page. A verse that ran onto the next page was cut off, and the
verses at the top of that page were filed under the next chapter or dropped.
Read in page order, the transcription holds all 1,060 printed units: 107 Roman
chapter numerals and 953 numbered verses. POB's reader splits chapter 6's list of
angel names into one more address, for 1,061 verses in all.

`tools/enoch/restore_sources.py` re-splits the pages at the printed numbers and
compares each unit with the verse files:

- review-accepted Ge'ez is never changed;
- 27 parser-derived sources that stopped at a page break were completed;
- 93 printed verses with no record were created.

For 39 of these 120 verses, the October-November source review had left a clean
collated draft (no unresolved letters, close to the page text), which is used
instead of the raw transcription. The rest come straight from the page
transcription. All carry `validation: page_order_transcription_restored` and a
note saying they have not been independently reviewed.

## The English pass

`tools/pob_meaning_pass.py` with prompt
`tools/prompts/pob_meaning_first_enoch_v1.md`, on Azure GPT-6.1 Sol (deployment
`pob-meaning-gpt-6-1-sol`, Flex tier, high reasoning), run `enoch-v1`. For each
verse the model sees the Ge'ez, the reading notes and uncertainty list, the
current English and notes, the revision history, and the whole chapter.

The Enoch prompt differs from the canonical one in these ways:

- it translates the Ge'ez and mentions Greek or Aramaic forms only in a
  footnote when they change the meaning;
- unclear, damaged, or editor-supplied readings get at most one short plain
  note, never invented text, and no editorial signs in the English;
- footnotes are written for readers: at most two per verse, no lexicon or
  edition names, page or column numbers, or review vocabulary;
- the book's titles (Lord of Spirits, Head of Days, the Watchers, ...) and the
  current capitalization of "son of man" and "chosen one" are kept verse by
  verse.

## Results

Run `enoch-v1` on 2026-11-09 covered all 1,061 verses for about $7.85 of Azure credit:
451 retranslated, 571 refined, 39 kept. 241 verses are marked low
confidence; 236 of them carry a note on an unclear, damaged, or disputed reading. Footnotes went from
1,997 to 510.

Azure's content filter blocked 20 verses: 7:3-5 and 9:1-3, 7, 9-10 (the giants
devouring people and the angels' report of it) and 90:1-7, 26-29 (the sheep torn
apart by birds of prey, and the judgment fire). Claude Opus 5.5 translated those 20
under the same prompt; their revisions name it as the adjudicator. In 90:1 the
printed "thirty-seven" is kept with a note that "thirty-five" fits the count of
fifty-eight in 90:5.

## Checks

`tests/test_enoch_current_text.py` replaces the per-batch receipt tests in CI.
It checks that all 1,061 printed units have one record with a matching id,
that every unit the 2026 source review accepted still carries exactly its
reviewed Ge'ez, that every verse has meaning-pass English with matching
footnote markers, and that no note uses reviewer vocabulary.

The receipt tests (`tests/test_enoch_*_application.py`,
`tests/test_enoch_full_repair_batch*.py` and the rest) compare the installed
files with the exact candidates of each review packet, so they describe the
corpus before this pass. Their evidence is unchanged under
`sources/textual_restoration/applications/`. They last passed CI at main
`cd2149417e75` and at Codex's batch-41 head `d3b1a029f40d` (draft PR 494),
whose repairs this branch merges. To re-verify that history, check out either
commit and run them there.

The Ge'ez accepted by that review is frozen in
`sources/enoch/coverage/reviewed_geez_2026-11-09.json` (512 verses). Change a
verse there only together with a new review of it.

## Not done

- No human specialist has reviewed this English or the restored Ge'ez.
- Disputed letters stay disputed; they are disclosed, not resolved.
- Graphic Reader artwork for 1 Enoch is a separate publication decision.
