# 1 Enoch 97 primary verse-count boundary only

Charles's 1906 Ethiopic Enoch prints numbered **XCVII.10** on printed page
203 (PDF page 241); the next heading is **XCVIII**. The local parser recovers
verses 1-10, with the tenth supplied by the continuation OCR file for chapter
98. This makes ten a scan-supported *inventory count*, not a maximum inferred
from the nine current POB verse files. `audit_pob_source_coverage.py` now
declares that count and keeps chapter 97 incomplete while canonical 97:10 is
absent.

This does **not** select the 97:10 Geʿez glyphs, apparatus reading, English
translation, imagery, or publication. The correction proposal is still
unapproved. No translation YAML, Graphic catalog, or app state changed.

Primary PDF: `sources/enoch/scans/charles_1906_ethiopic.pdf`, SHA-256
`505f248c667cebd5136991d7c570841a0a3ed9396d5b28b85bf07f4a3957053e`.
