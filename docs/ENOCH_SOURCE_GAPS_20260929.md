# 1 Enoch source-gap audit — 2026-09-29

The Graphic Reader candidates for chapters 6–17 had exact coverage of the
**current POB files**, but those files omitted verse units. Compared with the
public-domain Charles 1917 chapter/verse inventory, 42 verse files were absent
at audit time across chapters 6–10 and 12–17; chapter 11's two verse files
were present.
Several existing last-verse files also stop mid-sentence. Verse count alone
therefore cannot certify a complete chapter.

The primary Charles 1906 Geʿez OCR is arranged as overlapping page windows.
For example, chapter 6's file stops during 6:6, while the opening of chapter
7's OCR file contains the end of 6:6 and 6:7–8 before the `VII.` heading.
`tools/enoch/verse_parser.py` now joins that leading next-file span to the
chapter being parsed. The exact Geʿez words remain from Charles 1906; the
project's public-domain English reference supplies **verse numbering only**.
The unnumbered final sentence of 6:7 is split explicitly into 6:8 with a
warning, rather than silently inventing a marker in the OCR.

The corrected parser recovers the full 1–17 inventory (141 ordered verse
units). This is a source-recovery step, **not** an English translation or
publication approval. Missing POB YAMLs and any truncated existing English
verses must still be drafted from these source readings, independently
reviewed, exported to the app, and matched with newly required art before
their graphic chapters can be published. Do not derive POB text from the
rights-ambiguous Beta maṣāḥǝft validation oracle or copy a later English
edition.
