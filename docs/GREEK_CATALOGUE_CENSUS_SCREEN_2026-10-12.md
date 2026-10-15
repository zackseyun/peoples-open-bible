# Greek catalogue coverage screen and book navigation

October 15 follow-up: the [complete held-row reconciliation](GREEK_CATALOGUE_HELD_ROW_RECONCILIATION_2026-10-15.md)
classifies all 73 held rows, adds 45 book–catalogue navigation pairs, and
distinguishes component dates and excerpt settings. The original 125/73 parser
snapshot below is unchanged; all 39 books now have navigation in the reviewed
overlay, not completed collation or global witness coverage.

The current public Göttingen catalogue list contains **1,687 distinct stable
IDs**. All nine pages were acquired and checked, rather than extrapolating
from a search sample. A bounded Greek date-overlap query supplies 53 readable
detail records for priority investigation. This expands POB's discovery queue;
it is not a count of independent physical manuscripts, complete Greek Bible
coverage, or collation of preserved wording.

The [machine-readable screen](../sources/textual_restoration/discovery/greek_catalogue_screen.2026-10-12.v1.json)
and [offline verifier](../tools/textual_restoration/greek_catalogue_screen.py)
retain source locators, raw-byte pins, filters, review holds and all 39 POB book
rows. No canonical source, translation or source-registry identity changes.

## Catalogue scope and filters

The [primary catalogue](https://septuaginta.uni-goettingen.de/catalogue/)
advertises a structured data endpoint. The unfiltered requests used
`/catalogue/data/?limit=200&page=N`, following its actual next-page fields.
Eight pages contain 200 records each and the last contains 87. Totals, page
bounds and unique stable IDs all agree. The 1,655 distinct display names are
not a valid object count: 33 separate records use the placeholder name “–”.
Other identifier systems and renamed or reassigned records remain separate;
normalizing their display names must not merge physical objects.

The dated cohort uses `yearFrom=-400&yearTo=400&dateMatch=option3&language=grc&limit=200`.
The UI labels option3 as overlap; option2, containment, returns 32 records,
all among the 53 overlap records. The 21 extra results include mixed-date
codices and descriptions extending into centuries V/VI. These are the
catalogue's search semantics, not independently adjudicated dating. A query
with only an upper year bound had reported an empty date match and ignored
the intended filter; the complete filter specification matters.

The full list also contains non-Greek routes and non-normal record states.
All 1,687 rows were accounted for, not silently filtered to a convenient subset.
The 53 detail records are a prioritized cohort, not all ancient witnesses or
the complete catalogue's detail coverage. Later copies can preserve early
readings and remain in the wider acquisition queue.

## Known witnesses missed by the public list

Four of our nine individual Greek registry controls occur in the list and the
overlap cohort: Alexandrinus A, Vaticanus B, Sinaiticus S and the 8Ḥev umbrella
Ra943. The other five names—Ra801, 802, 803, 819 and 805—do not occur in the
entire fetched public list. They correspond to already registered Greek
Leviticus, Numbers, Deuteronomy and Exodus cave witnesses. This is a catalogue
coverage/access limitation, not grounds to discard them or deny their existence.

The public [Ra801 detail route](https://septuaginta.uni-goettingen.de/catalogue/Ra_801/)
returns a page whose embedded access flag is false. Its contents were not
retrieved through another restricted route. HTTP success alone therefore cannot
stand for readable text. This supplemental control stays distinct from the
53 readable candidate descriptions.

## Book and passage navigation with explicit holds

The 53 readable descriptions contain 198 structured content rows. The strict
parser assigns 125 rows to explicitly named books and holds 73 rows unresolved.
It uses exact abbreviations and sentence-start book prefixes, not incidental
mentions or inherited context. It requires an initial explicit prefix; further
book prefixes must follow a numeric-range separator, not arbitrary prose or
`cf.`/`e.g.` bibliographic mentions. Greek Kingdoms numbering is mapped explicitly
to Samuel/Kings; an invalid `IIV Reg.` spelling is not silently corrected.
Esdras numbering, collective prophetic titles, other-corpus material and
mixed Psalm/Ode labels remain review items. Range strings are pinned by hash,
not automatically expanded into POB verse numbering or preservation claims.

All 39 POB books have an output row. Thirty-one have at least one explicitly
assigned structured row in this narrow cohort. The other eight—Ezra, Nehemiah,
Hosea, Joel, Amos, Obadiah, Haggai and Malachi—have none under these rules.
That result cannot establish absent witnesses: collective labels, unparsed
ranges, later copies and other catalogues remain relevant.

Seven descriptions, Ra961–967, have empty structured overviews. Root separately
read their complete general-description fields: Genesis, Numbers/Deuteronomy,
Isaiah, Jeremiah and Ezekiel/Daniel/Esther occur there, alongside Sirach and
Greek additions. The receipt records these as reported book hints, not structured
ranges or newly observed letters. In particular, [Ra967](https://septuaginta.uni-goettingen.de/catalogue/Ra_967/)
has real content information despite a blank list description and empty
overview. Its literary forms and precise POB alignment still need checking.

[Ra943](https://septuaginta.uni-goettingen.de/catalogue/Ra_943/)
provides six book-range rows, A/B hand distinctions and a one-scroll/two-scroll
debate. Its Nahum range list does not include the newer 1:5–6 fragment already
documented in POB. Catalogue ranges therefore need publication updates and
physical-locus checks before claiming completeness. No hand or fragment is
automatically promoted to another independent witness.

## Reproducibility and limits

The raw list/detail pages remain private. Their hashes and source URLs support
rebuilding the same metadata result. All 53 readable detail footers declare
CC BY-NC-SA 4.0. Distinctive descriptions, bibliographies, manuscript images and
transcriptions are not imported into the CC-BY repository or relicensed.
The exported identifiers, counts and navigation are not an edition of the texts.
Image/IIIF flags identify acquisition leads, not inspected pixels or usable rights.

Ten new tests and four existing reference-annotation tests pass in 0.004 seconds.
Initial URL and prefix failures were corrected without dropping catalogue rows;
the receipt preserves them. Checks cover pagination, IDs, access guards,
conservative normalization and output boundaries, not historical source priority.

The independent first review reproduced all input pins and generated fields
but identified an incidental-reference false-positive in the reusable parser.
The stricter boundary and negative regressions above correct it without changing
the actual 125/73 snapshot counts. Twenty focused tests, including six existing
edition-registry tests, pass in 0.103 seconds after the publication-guard repair
and verified fast-forward. A prematurely launched run saw the old registry
phrase before that merge finished; it is recorded as failed, not a second pass.

The corrected guard receives a bounded independent PASS: all 65 raw input pins,
all 198 actual overview rows, seven general descriptions and every generated
field verify. The independent 14-test rerun is not counted again. A separate
local diagnostic completes the prior CI reader step's 84 commands after the
registry phrase repair; because the repair happened during that run, this is
not immutable exact-head CI certification. New-head remote checks remain required.

The next breadth work is explicit identity and passage reconciliation for the
unresolved rows, the seven narrative-only descriptions and the five missing
cave controls, followed by the wider catalogue's remaining detail records.
Actual primary editions/apparatus and surviving letters must precede Hebrew
retroversion or English application. The full OT witness census, varied
two-family image calibration and corpus-wide translation evaluation remain open.
ImageGen supplies no textual evidence.
