# 1 Enoch repair audit - October 20, 2026

Historical first-batch snapshot. The [ongoing full-book repair report](ENOCH_FULL_REPAIR_PROGRESS_2026-10-20.md)
records later repairs and current evidence; do not treat the counts below as
the latest state.

The POB translation remains incomplete and is not fully source-verified. This
is a statement about this digital translation, not about the completeness of
the ancient work. Neither a chapter entry nor a Graphic Reader illustration
certifies its underlying text.

## Applied in this bounded pass

Fifteen exact units were repaired after initial and independent source-review
checks. Three previously absent records were added: **18:11, 18:14, 18:15**.

- **18:1-4, 6-8, 10-11, 14-15:** selected Charles 1906 source, English and notes.
  In particular, 18:10 restores the clipped subject **the heavens**; 18:6
  discloses Charles's Greek-based editorial supply; 18:7-8 avoid unjustified
  mineral identification. Printed corruption in 18:10 remains disclosed.
- **28:1:** replaces the unrelated whole-chapter oracle source with the actual
  selected printed unit and restores its severely clipped English. Its comma
  reflects continuation into still-absent verse 2, not chapter completeness.
- **63:7:** repairs negative prefixes and source glyphs, removes the unsupported
  affirmative alternative, identifies Charles's bracketed dittography, and
  gives the retained notes unique anchors. The bracketed clause remains visible.
- **81:4 and 89:26:** remove accidentally duplicated English clauses without
  changing the surviving running words or the source text. In 89:26 the
  existing lexical alternatives are reanchored, not newly certified.

The [application package](../sources/textual_restoration/applications/enoch_source_repairs_20261020/)
preserves exact baselines, candidates, inputs, first/independent reviews,
provenance, artifact hashes and the bounded application receipt. The integration
retains the inherited oracle-derived 28:1 preimage by its existing Git blob and
SHA-256, rather than duplicating that wording in the new application tree. The
integration
metadata explicitly says that generating model versions and full reviewer
prompts were not reported; it does not fabricate drafting receipts. Legacy
claims are archived rather than inherited as current certificates. Records
remain **draft / needs_review** for wider verification, with medium source
confidence. There is no human-specialist or independent-manuscript certification.

## What still has issues

The fresh [verse-by-verse register](../sources/enoch/coverage/editorial-issues-20261020.md)
and [machine-readable evidence](../sources/enoch/coverage/editorial-issues-20261020.json)
inspect all **892** current verse files and all 108 chapter slots. They report:

- **15 absent files under declared selected-edition counts:** 18:12-13,16;
  22:14; 24:5-6; 25:6; 28:2-3; 32:6; 34:2-3; 45:6; 84:6; 97:10.
- **153 additional parser-derived absent-unit leads**, not certified missing
  verses. Combined units, numbering and complete printed boundaries need review.
- **50 existing source-alignment signals**, not automatic declarations of error.
- **39:10** still has a malformed word-shaped footnote label and clipped text.

These categories must not be added together as a count of proven mistranslations.
Conversely, no mechanical flag does not mean that a verse is linguistically verified.
Historical review snapshots can be superseded by later bounded applications;
consult the corresponding receipt before treating an older finding as unresolved.

### Evidence holds, not guesses

- **18:5,9,12,13,16:** corrupt wording or unresolved exact glyph/interpretation.
  The negative in 18:12 is supported, but one remaining source glyph is not;
  that complete unit stays uninstalled.
- **28:2-3 and 34:1-3:** unresolved syntax, selected-reading lexical decisions
  or corrupt clauses. In 28:3, the printed corrupt *water* reading is not
  silently replaced with Charles's proposed *mist*. The 34:1 candidate's
  proposed *wonder* failed independent lexical review and is not installed.
- **84:** a fresh all-six review still holds exact readings in 2-3. The chapter's
  existing no-partial-install restriction is honored. Verified provisional
  corrections include a false asterisk in 2, an omitted negative within the
  bracket in 3, and apparatus siglum **u**, not **g**, in the note for 6. All
  remain outside canonical text until the chapter gate passes.
- **97:10:** the rejected positive reading is not installed. The separate active
  Chapter 97 lane and its uncommitted files were not modified by this pass.

## Reproduce the checks

Local validation passed 128 existing Enoch tests before application and 13 focused
tests after application, including all fifteen candidate schemas and exact review
bindings. The transaction proved that every unrelated canonical file was unchanged.
The mobile-export delta is chapter 63's repaired notes only; incomplete chapters
18,28,81,89 remain excluded. This does not establish a public CDN or device refresh.

```sh
python3 tools/textual_restoration/enoch_20261020_transaction.py verify-applied
python3 tools/enoch/audit_editorial_issues.py --output /tmp/enoch-issues.json --markdown /tmp/enoch-issues.md
python3 -m unittest discover -s tests -p 'test_enoch_editorial_issues.py'
python3 -m unittest discover -s tests -p 'test_enoch_20261020_transaction.py'
```

The mechanical audit also fixes a blind spot: empty English is now reported even
when no primary parser row exists. Chapter 84's six-unit count is declared from
the visible boundary, independently of approval of its disputed wording. A stale
26:6 regression assertion was corrected to preserve the later hash-verified
26:5 repair instead of requiring that restored verse to disappear.

Source application, Git delivery, public CDN refresh, app installation and Graphic
Reader publication remain separate evidence surfaces. This pass creates no new
artwork and grants no whole-chapter or whole-book publication approval.
