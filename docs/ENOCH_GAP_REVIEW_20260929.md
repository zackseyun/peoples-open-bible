# 1 Enoch recovered-verse review checkpoint — 2026-09-29

The Charles 1906 cross-page OCR parser now recovers the complete 1–17 verse inventory. The `codex/enoch-source-gaps` branch holds 42 newly drafted missing verses; 12 clipped existing verses have separate replacement candidates outside the canonical tree. None of these candidate English texts has been merged into POB `main` or released to the app.

An independent GPT-6 Astra pass compared each candidate against the recovered Geʿez and a public-domain Charles 1917 semantic reference (not a source for POB wording): **54 candidates: 18 provisional pass, 12 revise, 24 hold**. A model `pass` is not publication approval. The `hold` cases involve dagger/bracket textual cruxes, OCR or witness uncertainty, or ungrounded wording and require specialist source review.

Held references: 1 Enoch 6:6, 1 Enoch 6:7, 1 Enoch 7:3, 1 Enoch 7:5, 1 Enoch 8:1, 1 Enoch 8:2, 1 Enoch 8:3, 1 Enoch 9:9, 1 Enoch 9:10, 1 Enoch 9:11, 1 Enoch 10:18, 1 Enoch 10:19, 1 Enoch 12:2, 1 Enoch 13:6, 1 Enoch 13:8, 1 Enoch 14:21, 1 Enoch 14:22, 1 Enoch 14:24, 1 Enoch 14:25, 1 Enoch 15:9, 1 Enoch 15:11, 1 Enoch 15:12, 1 Enoch 16:1, 1 Enoch 16:3.

Revision-needed references: 1 Enoch 5:9, 1 Enoch 7:1, 1 Enoch 7:6, 1 Enoch 8:4, 1 Enoch 10:17, 1 Enoch 10:20, 1 Enoch 10:22, 1 Enoch 12:4, 1 Enoch 13:4, 1 Enoch 14:20, 1 Enoch 17:7, 1 Enoch 17:8.

The fixable 5:9 and 17:7–8 wording has candidate reviews, and the additional 17:8 graphic panel is saved separately in `cartha-music-production`. Neither the POB correction nor the chapter-17 Graphic Reader catalog has been published. The existing live 5:9 remains a known clipped-source issue until its bounded correction passes the source publication gate.

Review files are stored outside Git under `/Users/zackseyun/Documents/future 2/output/bible-graphic-stories/1-enoch/source-corrections-20260929/independent-review` with SHA-256 checksums:
- `a-review.json`: `1aeaa401cf9786669e398b430c053697d72931d6afdf47cb3336f914c5f6ac48`
- `b-review.json`: `6cdd3fff12a0366b55d4570908b31c490a014157c6e0394b832c73ff78f6fa9b`
- `c-review.json`: `f439b368fb78d8c4122298606a66f4ef69479e080af6bd5ac738a5c181b4d44d`
- `d-review.json`: `5ca1359a5deda8b066c64560975ea9d8c5995896990051fdaa34884c19b542cb`

Next gate: resolve the held source readings with a qualified Geʿez/textual reviewer or documented scan-and-apparatus adjudication; then apply only hash-bound accepted corrections, run complete-chapter and export checks, and publish POB before any Graphic Reader catalog update.
