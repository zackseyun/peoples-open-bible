# Historical archive source-first review - 2026-10-13

## Verified status, not a completed translation claim

The eight Historical Library witnesses are archival English editions, not
finished POB source-facing translations. The four newer church orders also
require direct-language review: all 102 checked chapter records identify their
source language as English. No archive, canonical translation, or published
reader text was rewritten in this work.

The research registry is `sources/historical_archive/catalog.json`; its explicit
`canon_effect: none` and `publication_allowed: false` keep this investigation
separate from the Bible/reader publication registries. Source-first methodology
is in `tools/prompts/historical_source_first_review.md`.

## Actual source preparation and observations

- All eight archived raw witnesses passed their existing SHA-256 pins.
- Dhammapada: pinned Bilara's published commit
  `a20fcb094d1d618080e52f41f24d20d5e347b0f7`, acquired all 26 chapters / 423 Pali
  verses with segment identities, and aligned the archived Müller translation
  and Sujato's CC0 translation as comparisons. Nine Müller paragraphs combine
  two verses: they retain combined-span labels, not fabricated per-verse English
  alignment. Headers and commentarial story titles are excluded from verse text.
  This is a direct-language edited edition, not a newly collated manuscript or
  an autograph. Sujato's CC0 license is verified in the pinned publication
  record; the Pali digital-edition scope remains a rights-review item before
  redistribution. All raw material and jobs are private research artifacts.
- D&C: prepared source-facing jobs for the title page and first preface page
  against Newberry GR_711 facsimiles and the JSP published reading of another
  copy of the 1835 edition. A first single-model visual probe confirmed visible
  OCR problems such as `pay` for `Day`, `prefabe` for `preface`, and `elass` for
  `class`. This is not an independent Azure verdict or a whole-edition review.
  The preface probe also exposed the importance of excluding JSP's inserted
  page locator from the historic words. Copyrighted JSP historical introductions
  and annotations are not republished in this repository.
- Pearl of Great Price: the cited 1913 Wikisource index still says "To be
  proofread"; it is not an independently verified replacement witness. The
  Book of Abraham requires a separate provenance/claim assessment, not a claim
  that English scan agreement establishes an Egyptian translation.

## Azure readiness and execution boundary

Read-only Azure management checks confirmed the existing subscription is enabled
and that the existing `gpt-6-1-sol-review` and separate review-model deployments
have succeeded provisionally. Management-plane provisioning is not a successful
inference test, source-check verdict, or bill/credit verification.

The older Azure tools auto-load API keys through an AWS secret path that cannot
be used under the current secret-safety rule: the required named skill and
`asm-exec` are unavailable. No secret retrieval was attempted. Keyless Entra
usage through the existing Azure sign-in was requested separately; until that
approval or an approved secret-runtime lane exists, no model API calls run.
Generation calls: **0**. Independent reviewer calls: **0**.

## Reproduce the safe preparation

```
python3 tools/historical_archive_review.py \
  --archive-root /path/to/web/public/historical-library \
  --output /private/research/historical-review --acquire both
python3 -m unittest discover -s tests -p test_historical_archive_review.py
```

The output includes archived integrity evidence, the four church-order draft
language audit, 423 hash-bound Pali review jobs, source/comparison snapshot
receipts, two D&C scan jobs, and mechanical difference reports. It never reads
credentials, generates models, marks a book verified, writes translation YAML,
or promotes content. Eleven focused tests cover missing/duplicate verses, combined
English spans, non-source headers/page locators, hash drift and cached-snapshot tampering, separate-review
identity, incomplete coverage, rights gaps, and direct scan review requirements.

## Gates still open

1. Resolve the approved model-runtime authentication lane and run bounded pilot
   drafts/source-facing reviews with stored prompts, outputs, exact model IDs,
   response IDs and hashes. Compare prior English translations only after the
   initial source-facing draft to reduce anchoring.
2. Acquire/select and license-check the remaining original-language editions;
   distinguish attested language versions from lost originals and reconstructions.
3. Complete the entire declared scope and adjudicate issues against sources.
4. Review output rights, attribution, edition identity and numbering before any
   new English edition is published. Existing archive warnings remain correct.

Primary evidence: Joseph Smith Papers 1835 pages 9 and 11; Newberry GR_711 leaves
n4 and n6; Bilara pinned root/translation/publication files; Tanzil's original
text license; the 1913 PGP Wikisource index. Discovered source candidates are
not presented as exhaustively acquired, collated, or publication-cleared.

## Whole-edition follow-up, 2026-10-13

The full D&C inventory is now derived from both upstream page inventories,
not from the reader's 87 approximate reading chunks. Newberry GR_711 contains
298 scanned leaves, and JSP's copy contains 305 gallery pages. The different
bindings are not assumed to share leaf numbers. Covers, apparent blanks,
copyright pages, index/contents, and the printed errata remain in the declared
scope. Empty OCR does not prove a blank page. The archived OCR matches the
upstream `GR_711_djvu.txt` SHA-256 pin exactly.

`tools/historical_dc_whole_edition.py` prepares every primary facsimile job
and every comparison page in a private research directory. It preserves OCR
word coordinates and source snapshot receipts. Its acquisition ledger records
every success/failure and requires both complete inventories before it can
report **acquisition** complete. It always reports whole-work verification and
publication as false; acquiring a scan is not reading/reviewing it. No model
calls, keys, source-language invention, translation writes or deployment occur.

Live checks also exposed two defects in the earlier JSP extraction: modern
popup biographies/glossaries were included after printed anchor words, and
inferred locators such as `[p. [iii]]` survived when the metadata said `iii`.
The parser now preserves the printed anchor words, excludes popup annotation
contents, and strips only the exact terminal locator for that page. The
opening jobs were regenerated: title-page mechanical difference groups are
now 5, and first-preface-page groups are 12. Previously extracted text hashes
are superseded, not accepted review evidence. These corrections affect only
private research comparisons, not the historical reader text or its preserved
raw downloads. The separate-review/full-scope gates remain open.

```
python3 tools/historical_dc_whole_edition.py \
  --output /private/research/historical-review --workers 2
```

Seventeen focused tests now cover the original review gates plus whole-copy
leaf coverage, empty OCR, reordered/missing pages, wrong-copy/error responses,
independent binding inventories, and the live-style popup/locator regressions.
