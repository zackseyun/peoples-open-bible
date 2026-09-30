# Bounded 1 Enoch 5:9 and 17:7–8 source-correction candidates

These are frozen, independently reviewed candidates, **not yet applied to POB
translation or published**. They restore the Charles 1906 Geʿez continuation
across adjacent chapter-file windows and render three verses with transparent
notes. The old `status`, `revision_pass`, and `cross_check` values for 5:9 and
17:7 are archived as historical only; they do not certify the corrected text.
`manifest.json` binds baseline and candidate bytes, and
`final-source-review.json` records the new scan-grounded review. The latter
accepts the final text while acknowledging it does not certify every glyph of
the manuscript apparatus.

`python3 tools/textual_restoration/enoch_low_risk_transaction.py verify` is
read-only. It verifies the primary source, notes, approval archive, and exact
local export delta: only chapter 5 verse 9 changes and complete chapter 17
becomes eligible for export. `apply` updates only these three YAMLs with exact
baseline guards, writes `application.json`, and does **not** push or deploy.
The live CDN publisher has separate behavior; after any application and push,
verify the actual 1 Enoch book and every untouched chapter on the public CDN.
