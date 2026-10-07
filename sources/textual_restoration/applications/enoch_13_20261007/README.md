# 1 Enoch 13 bounded source repair

Restores the full cross-page 13:4 clause and absent verses 5–10 from Charles1906 selected Geʿez critical text, PDF pages70/72 (printed32/34). Existing13:1–3 are preserved unchanged. The extension noun, starred place names and parenthesized Greek-based editorial restoration are disclosed in notes. This is not a fresh DSS transcription or human specialist certification.

A fresh read-only Codex CLI run through the existing ChatGPT login accepted all seven exact source/English/footnote units. Content hashes are bound in `final-source-review.json`; `review-provenance.json` records scan/input hashes. `enoch_13_transaction.py verify` is read-only, `apply` uses baseline/existence guards and checks only chapter13 export changes, and `verify-applied` binds installed bytes. No other chapters may change in this transaction.

The first provisional review/local application was rolled back after a repeat review detected OCR glyph errors. `source-review-v2-requests.json` and the superseded artifacts preserve that sequence. The exact corrected spellings and revised notes passed the final v3 review; `source-cleanup.json` binds before/after readings, and the primary parser applies only those guarded substitutions while preserving raw OCR files.
