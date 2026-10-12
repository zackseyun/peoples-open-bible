# Pseudo-Clementine Greek sources

## Scope and current state

Added at Zack's request on 2026-10-11: **sources only for now, with checked
translations required**. No English translation was generated, approved, or
published by this addition. These four records are in the shared historical
catalog with `publish: false`. The existing 29 published catalog works are
unchanged. This is not an addition to the biblical canon.

| Work | Catalog code | Acquired Greek sections | Coverage |
|---|---|---:|---|
| Letter of Peter to James | PCPET | 3 | Sections 1–3 of the supplied file |
| Contestation / Diamartyria | PCDIA | 5 | Sections 1–5 of the supplied file |
| Letter of Clement to James | PCCLE | 20 | Sections 1–20 of the supplied file |
| Homilies | PCHOM | 505 | Homilies 1–18 and the supplied portion of 19, ending at 19.14 |

These are the Pseudo-Clementine writings, not **1 Clement** or **2 Clement**.
The traditional names do not establish authorship by Peter or Clement. They
belong in historical early-Christian literature, with their claims preserved
rather than harmonized into canonical Scripture.

**The Homilies source is incomplete.** The collection has 20 homilies, but
this supplied file ends at 19.14. Do not infer completeness from a successful
XML parse or 505 extracted sections. Acquire and review the missing ending
from a documented, rights-cleared source before describing the work as complete.
Do not use AI generation to fill absent Greek or invent an English ending.
See the [scholarly collection overview](https://academic.oup.com/book/34752/chapter-abstract/296719774).

## Provenance and rights

The four sources are from [Open Greek and Latin / First1KGreek](https://github.com/OpenGreekAndLatin/First1KGreek/tree/03776b39f4047c5cff06f5296fae4b2bae4b08fb/data/tlg1271),
pinned to commit `03776b39f4047c5cff06f5296fae4b2bae4b08fb`, records
`tlg1271.tlg003` through `tlg1271.tlg006`. Their printed source is Albert
Schwegler's *Clementis Romani quae feruntur homiliae* (Stuttgart, 1847).

Each directory under `sources/early_christian_texts/pseudo_clementine_*` contains:

- `source.xml`: unchanged upstream bytes, including contributor credits,
  funders, proofreading and conversion history, license, and print-scan links.
- `manifest.json`: pinned URL, raw SHA-256, edition, rights, coverage,
  structural-review status, and required translation/source-check policy.
- `sections.json`: normalized Greek with original CTS references and per-passage
  SHA-256 hashes. Headings are retained; page-break metadata is separate.

**Imported XML and normalized Greek retain CC BY-SA 4.0.** Credit Open Greek
and Latin / First1KGreek and the edition; preserve the full contributor details
in the TEI headers. XML bytes were not edited. The derived section files extract
headings/prose, normalize whitespace, and separate page-break markers. There
are no spelling corrections, supplied restorations, or English paraphrases.
See the [license terms](https://creativecommons.org/licenses/by-sa/4.0/).
No endorsement by the source project is implied.

The repository's CC BY 4.0 license does **not** replace the upstream license.
Before English publication, determine the applicable output rights. Where the
English is an adaptation subject to ShareAlike, preserve those terms and ensure
the reader/export can display them; otherwise establish and document an
independent lawful source basis. Do not simply label a generated translation
CC BY because that is the reader's default. No third-party photograph is vendored.

## Required generation and checking workflow

1. Validate the pinned source and prepare a passage-specific Greek prompt.
2. Generate a fresh English draft directly from that Greek, not by rewriting
   an existing English translation. Retain the source XML hash, exact CTS
   reference, normalized passage hash, prompt hash, model identity, and timestamp.
3. Run a **separate source-comparison pass** over the Greek and proposed English.
   Check every clause, quotation, negation, name, lexical ambiguity, addition,
   omission, and heading. Record corrections and unresolved source defects;
   do not silently repair apparent errors in the digitization.
4. Save a review record with reviewer identity/method, timestamp, source and
   English hashes, findings, and verdict. Any source or English change requires
   rechecking the affected passage. Automated source review is not human
   scholarly sign-off or manuscript collation.
5. Resolve output licensing, preserve historical/noncanonical labeling and
   completeness warnings, and implement the reviewed translation export before
   changing publication state. A raw source, draft, or structural test result
   alone cannot satisfy the source-language translation check.

The current code intentionally prevents publication of these source-only
entries. Updating a status string or `publish` flag is not a release mechanism.
The future checked-translation implementation must supply the hash-bound
evidence, validation, licensing support, and passage mapping described above.

From the repository root:

```sh
python3 tools/extra_texts/pseudo_clementines.py check
python3 tools/extra_texts/pseudo_clementines.py prompt \
  --work pseudo_clementine_peter_to_james --reference 1
python3 tools/extra_texts/validate_catalog.py --all
python3 -m unittest discover -s tests -p 'test_pseudo_clementines.py'
```

`prompt` prepares an auditable input; it does not call a model or claim a
translation exists. `acquire` is a first-acquisition command and refuses to
overwrite an existing snapshot. All verification is offline after acquisition.
Structural validation is not a claim that the Greek is free of transcription
errors, matches every printed page, or represents the earliest recoverable text.
