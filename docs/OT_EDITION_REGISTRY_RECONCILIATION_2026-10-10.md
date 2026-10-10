# Old Testament critical edition registry reconciliation

Eight missing edition routes are now registered, and an obsolete OHB access
label is corrected. The registry grows from32 to40 mixed object/family/edition
records, **not40 ancient manuscripts**. This bounded reconciliation improves
source discovery for the comparison program; it supplies no new reading,
complete apparatus collation, English change or claim that every known source
has been found. NETS remains an English companion, not a Greek witness.

Baseline: `e4d22d5bf07957251d3170d5551d7debe1aacd2d`. The
[receipt](../sources/textual_restoration/discovery/ot_edition_registry_reconciliation.2026-10-10.v1.json)
pins the old registry, reviewed candidate and historical evidence files.
Evidence-file pins refer to that Git snapshot, not future versions of the
linked reports. Thirty-one existing rows are unchanged; only OHB2008 is revised.
Existing object IDs, rights, source text, translation and policy are preserved.

## Routes and actual consultation

| Added route | Evidence basis | What still needs consultation |
| --- | --- | --- |
| BHQ | Current publisher project/fascicle table | The relevant published fascicle, introduction and locus apparatus; Numbers/Ezekiel remain listed in preparation2026 |
| BHS | Publisher metadata; recorded Haggai2:22 selected-text check | Actual apparatus and its conventions; online base text is not that apparatus |
| HUBP | Institutional Aleppo-based project description | Relevant published volume and passage apparatus; a hosted article is not its Bible edition |
| HBCE Proverbs, Fox2015 | One-page SBL publication notice, text extraction only | Actual book/Proverbs30:1 apparatus; editorial emendations are not new manuscript readings |
| Göttingen LXX | Current publication list plus existing39-book bibliographic routing | Book-specific edition and decisive adjacent apparatus units; routes are not completed collations |
| Schorch Samaritan edition | Institutional method/Leviticus2018 metadata | Relevant available volume and full manuscript/version apparatus; DT-UCPH is not its substitute |
| Rahlfs–Hanhart2006 | Publisher metadata; recorded Daniel7/Ezekiel28 selected text | Exact form and apparatus; distinguish Rahlfs1935, OG, Theodotion and alternate texts |
| Weber–Gryson2007 beyond Psalter | Publisher metadata; recorded Ezekiel28 selected text | Latin book-specific apparatus/source history; existing two Psalter controls remain distinct |

Current metadata was read from the primary
[BHQ publisher](https://www.die-bibel.de/en/home/scholarly-editions/vulgate/scholarly-bible-editions/biblia-hebraica-quinta-bhq),
[BHS publisher](https://www.die-bibel.de/scholarly-bible-editions/biblia-hebraica-stuttgartensia),
[Hebrew University](https://en.bible.huji.ac.il/projects-and-publications),
[SBL publication notice](https://www.sbl-site.org/assets/pdfs/pubs/062401C.pdf),
[Göttingen project](https://septuaginta.uni-goettingen.de/publications/septuaginta/),
[Halle Samaritan project](https://www.theologie.uni-halle.de/bw/samaritanerforschung/samaritanusedition/),
[Rahlfs–Hanhart publisher](https://www.die-bibel.de/en/bible-society-and-biblical-studies/scholarly-editions/septuagint/septuaginta-deutsch/the-septuagint-lxx)
and [Vulgate publisher](https://www.die-bibel.de/en/en/bible-society-and-biblical-studies/scholarly-editions/vulgate).
Publication/project dates are not ancient-copy dates. Open metadata or selected
text does not establish apparatus access or corpus redistribution rights.
The HBCE label's February2015 comes from the cited notice; the
[current SBL catalogue](https://cart.sbl-site.org/books/062401C) instead lists
April2015. Both are recorded; February is notice metadata, not a resolved exact
publication month. This distinction does not affect ancient-witness chronology.

## Corrected history and dependency limits

The old OHB row said that only metadata had been read and acquisition remained
blocked. The [existing consultation receipt](../sources/textual_restoration/discovery/deut32_8_ohb_review.v1.json)
instead records actual browser visual reading of Deuteronomy32:8's selected
text, apparatus and commentary at printed354/355/357, PDF4/5/7, on September5.
Earlier direct-download403 failures remain recorded. No verified local PDF or
file hash was obtained; Kings/Jeremiah samples and the full article were not read.
The corrected row is registered/partially mapped, not a newly acquired object.
Its exact El wording remains a labelled editorial conjecture, not extant Hebrew.

The [Haggai2:22 report](HAGGAI_DSS_COMPARISON_2026-09-07.md#english-consequence-plural-riders-at-222--2026-09-07)
records a selected BHS control, not apparatus consultation. The
[Ezekiel report](EZEKIEL_28_CHERUB_COMPARISON_2026-10-10.md) and
[Daniel source contract](../sources/textual_restoration/comparisons/daniel7_13_14_source_contract.2026-10-10.v1.json)
support the bounded publisher Greek/Latin controls. This pass does not reread
their verses or adjudicate historical priority again.

NETS Daniel's existing PDF pin and inspection scope remain linked through the
receipt. Its English endpoint/royal-authority choices and declared Göttingen
basis do not certify the underlying Greek apparatus. Adding it as Greek would
inflate witness support and misidentify its language. No registry schema or
language enum change is made. Likewise, an edition, its base manuscript and
a derived digital transcription cannot become three independent attestations.
The Vulgate umbrella overlaps its Psalter rows; dependency remains local.

## Review and verification

One local reconciliation agent identifies gaps and the stale OHB history;
one separate bounded critic passes the exact registry candidate at SHA256
`2bc16c0e240856e6f757384da6177232cd5f742d0e1346d3bf930791ced9a7f8`.
Neither is another ancient witness. Schema/custom registry and old/new coverage
checks pass. Five focused reconciliation tests plus nine source/redraft guards
pass:14tests in0.222s. No preference vote or review-until-agreement loop occurs.

The existing broad validator and entire registry suite do **not** pass: six
comparison-baseline drifts remain;50registry-suite tests yield48passes and
two historical Samuel17:4/Psalm145:13 baseline failures. The judge traces these
to comparison validation, not the registry, and old/candidate registry inputs
give identical zero coverage errors. Root confirms the affected validator,
test, comparison, canonical and source files are unchanged in this packet.
These failures are disclosed, not counted as successful new checks or silently
fixed by altering historical evidence. CI adds the five focused tests with
their exact historical baseline fetched.

The general HBCE route returns403; the lawful publisher notice supplies only
bibliographic metadata. Root extracts its text successfully; the independent
critic's direct open fails but primary search exposes the same notice text.
Vulgate/LXX navigation clicks fail before primary descriptions are located;
a Vulgate English-path passage request fails and supplies no fresh reading.
No full edition or restricted apparatus is copied, purchased or relicensed.
An initial registry serialization expanded untouched arrays; it is replaced
with a surgical rendering that preserves unrelated row formatting. A compact
inventory read is truncated and a listing command has a syntax error; bounded
reads and a corrected command succeed, without promoting either failure as
evidence. Historical input pins, review limits and retrieval failures remain
in the receipt; the documentation skill keeps this audit in Git.

The broader source-family reconciliation remains open. This packet covers
eight named route groups, not all citations, all editions or a global object
census. Individual manuscript identity, exact passage survival, corrections,
version relationships and rights still need passage-level work. The next useful
comparison acquires evidence that distinguishes live readings, not just another
edition title. ImageGen remains display-only and supplies no missing letters.
