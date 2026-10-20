# Chapter 18 fresh source review - 2026-10-20

All 16 selected-edition unit boundaries were inspected against the actual Charles1906 PDF, whose SHA256 matches the source manifest. Text is on printed48/PDF86 and printed50/PDF88. Printed49/PDF87 contains the facing Greek and continuation of the Ethiopic apparatus. This is a bounded AI selected-critical-edition review, not a human-specialist certification, independent manuscript collation, or a completed-book claim.

## Result

11 fresh candidate units accepted by this reviewer: 18:1-4,6-8,10-11,14-15. Five units held: 18:5,9,12,13,16. Chapter boundary inventory complete does NOT mean editorial approval of every unit.

The positive-to-negative OCR error at 18:12 is confirmed, but its whole-unit application is held for one exact glyph in the water token. 18:10 is demonstrably clipped: heavens on printed50 completes the preceding verse, rather than belonging to 18:11. Source pages for it must include both86 and88. The six absent canonical files are 18:11-16.

Other actionable issues include the old unqualified crystal identification in18:8, hidden Greek-restored wording in18:6, obsolete/misplaced footnote anchors in existing verses, and missing critical marks in parser-derived18:13 and18:16.

## Files and applicability

- `review-input.json`: exact fresh unit candidates and anchored notes; held diagnostic glosses are NOT publication-ready translations.
- `review.json`: bounded per-unit accept/hold judgment on those exact candidates.
- `existing-input.json`: canonical source/English snapshot with per-file hashes, including absences.
- `provenance.json`: PDF/input/review/scan SHA256s and exact source-bound scope.
- `scans/`: actual PDF renders and reading crops. The broader PDF86-88 sequence is retained, not just isolated verse snippets.
- `build_package.py`: reproduces this review bundle, reads canonical files, writes only here. Rerunning refreshes preconditions, so preserve the current package as an immutable review artifact when applying elsewhere.

No canonical files, source-edition OCR, Git state, artwork, or deployed content were changed. No independent second reviewer has approved these candidates. A parent must independently verify these exact candidates and precondition hashes before any narrowly bounded application. Holds must remain unpublished.

## Exact blockers

- 18:5: Charles printed48 note19 expressly calls the clouds wording corrupt; the diagnostic English does not resolve its object or syntax.
- 18:9: Charles printed48 note51, continued on49, calls the latter clause corrupt. Ge'ez within all the mountains is not silently replaced with the facing Greek beyond these mountains; a readable text needs an explicit reviewed source decision.
- 18:12: printed50 clearly has negative *ኢ before the heaven-covering verb. Parser has positive-looking አ. Independent glyph check still needed for the water token before note17, where parser has ማን versus expected water ማይ. See `scans/pdf088-top400.png`.
- 18:13: daggers surround the final clause. Note24 calls it corrupt. Do not invent a scene in which Enoch asks the angel; the visible wording concerns a spirit questioning him.
- 18:16: mystery is dagger-marked. Printed50 note36 contrasts the Ge'ez year of mystery with Greek ten thousand years and judges the Greek right. The latter is not the printed Ge'ez reading; adopting it requires an explicit reviewed textual decision.

Square brackets at18:10 must not be described indiscriminately as editorial supply: Charles note52 calls the opening an addition in Ethiopic. Parentheses at18:6 are different: note27 explicitly says restored according to Greek. Neither establishes independent manuscript agreement.
