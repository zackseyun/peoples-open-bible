# Charles 1906 shared transition pages — 2026-10-02

The public-domain Charles 1906 Ethiopic scan was rehydrated from the source-manifest Internet Archive URL. Its SHA-256 is `505f248c667cebd5136991d7c570841a0a3ed9396d5b28b85bf07f4a3957053e`, matching `sources/enoch/MANIFEST.md`. The Dillmann 1851 scan was also rehydrated and matched its manifest SHA-256 `3800be7c3408d2f8a3e9f112b18025c6541fe946226654b4818ab60979880cdc`. Both PDFs remain gitignored source references, not committed assets.

Visual inspection of Charles's printed page headers confirmed that the following **single scanned pages contain the preceding chapter's tail before the next chapter begins**:

| PDF page | Printed page | Printed header span | OCR window overlap |
|---:|---:|---|---|
| 186 | 148 | LXXVII.7–LXXVIII.6 | 77:8 appears before chapter 78 |
| 190 | 152 | LXXIX.5–LXXX.4 | 79:5–6 appear before chapter 80 |
| 191 | 153 | LXXX.5–LXXXI.1 | 80:5–8 appear before chapter 81 |
| 204 | 166 | LXXXVI.6–LXXXVIII.2 | 86:6 continues before chapter 87 |

`tools/enoch/verse_parser.py` independently recovers these tails from the adjacent page-window transcription files. The existing chapter-detection cache assigned each transition page only to the newer chapter, so an OCR rerun of the preceding chapter would again omit the tail. `page_map.json` and `build_page_map.py` now preserve these four verified overlaps. The regression test checks the committed map, regenerated map, and cross-file parser results.

**This does not repair the POB translation.** The current English YAML counts for chapters 77, 79 and 80 remain 7, 4 and 4 respectively against 8, 6 and 8 recovered numbered Charles units. POB 86:6 still carries bracketed English continuation while its isolated `source.text` stops early. Source editors should review the printed Geʿez, textual notes and verse boundaries before applying corrections; OCR numbering and scans alone are not a reviewed English translation. Graphic Reader art for these chapters remains held.
