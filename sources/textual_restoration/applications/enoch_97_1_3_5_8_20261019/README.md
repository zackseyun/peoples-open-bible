# 1 Enoch 97:1, 3, 5, 8 - bounded individual-unit repair

Two independent read-only scans of all ten printed units first returned
`revise` for 97:1-9 and `hold` for 97:10. Their results are preserved in
`../enoch_97_review_20261019/`. Four exact revised candidates (97:1, 3, 5,
8) then passed a fresh read-only check against high-resolution Charles 1906
PDF pages 239-240. The candidates repair source glyphs/critical signs where
needed, remove incorrect or misplaced footnotes, and preserve the full
selected-English clause. The accepted reviewer was the signed-in Codex CLI;
no Vertex credentials or raw login tokens were used.

`manifest.json` binds every baseline and candidate byte plus the review and
primary PDF hashes. Old model/revision metadata remains recoverable in the
four baseline YAMLs; it is not carried forward as fresh certification.
`tools/textual_restoration/enoch_97_partial_transaction.py` verifies the
preimage, exact accepted candidate, note anchors and mobile export before
changing only those four YAML files. `application.json` records the verified
result. Run `verify-applied` to check the installed bytes.

**Chapter 97 remains incomplete.** Canonical 97:10 is absent, 97:2/4/6/7/9
still need correction, and the 97:10 proposed positive wealth verb was
rejected in both whole-chapter reviews. The mobile exporter still excludes
chapter 97; no Graphic art, app catalog or public chapter was published.
This is selected-edition AI review, not human-specialist or manuscript
certification.
