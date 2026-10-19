# 1 Enoch 45 primary verse-count boundary only

Charles's 1906 Ethiopic Enoch prints numbered **XLV.6** on printed page 86
(PDF page 124); the next heading is **XLVI**. The local parser recovers verses
1-6, with the sixth supplied by the continuation OCR file for chapter 46.
This makes six a scan-supported **inventory count**, not an inferred maximum
from current POB files. `audit_pob_source_coverage.py` now declares that
expected count, and its test requires absent canonical 45:6 to keep chapter
45 incomplete.

This change does **not** select any 45:6 Geʿez glyph, apparatus reading,
English translation, image, or publication. The existing 45:6 proposal is
unapproved, and the chapter's other verses and candidate art still need
editorial/visual review. No translation YAML or public catalog was changed.

Primary PDF: `sources/enoch/scans/charles_1906_ethiopic.pdf`, SHA-256
`505f248c667cebd5136991d7c570841a0a3ed9396d5b28b85bf07f4a3957053e`.
