# Supplementary NT attribution audit — 2026-09-06

## Outcome

Compared all 27 remaining source-absent NT supplementary records as one batch.
Thirteen stored Greek texts are not verified against the cited RP2005-era
digital representation. Their active attribution is now
`unverified-supplementary-greek`, with the previous RP label retained as
`claimed_edition_before_audit`. Greek and English are unchanged. Their prior
review objects are historical; current status is draft/needs-review, with
`reader_supplement: false`. The exporter rejects the unresolved attribution even
if an inclusion flag is accidentally enabled. No new supplements were exported.

This is a source-attribution safeguard, not a determination of the earliest
reading or proof of absence from every RP printed edition or apparatus.

## Evidence and scope

The machine-readable [27-record comparison](../sources/textual_restoration/inventory/nt_supplement_attribution.v1.json)
contains pre-edit record hashes, stored Greek, matched primary rows, source URLs
and SHA-256 hashes. Consulted the official byztxt **v2.0.3**, using the accented
`csv-unicode/accents/no-variants` files for Matthew, Mark, Luke, John and Acts,
plus the separate `PA.csv` and `AC24.csv`. The
[versioned source documentation](https://github.com/byztxt/byzantine-majority-text/blob/v2.0.3/csv-unicode/README.md)
identifies CSVs as convenience conversions, with Robinson's CCT/ASC files the
ultimate sources. Those underlying files and a printed RP2005 volume were not
collated here. The project's existing version selection follows the official
repository's guidance that v2.0.3 is closest to RP2005, not current RP2018 main.

First compared whitespace-collapsed lowercase strings; a second screening pass
ignored combining marks and punctuation and compared Unicode letter tokens.
Token agreement is not exact orthographic agreement. Every nonmatching record
retains its contrary primary text, rather than silently normalizing differences
away. The initial browser API listing was inaccessible; the shell HTTP client
successfully retrieved the official directory listing and seven files. No paid
API, manuscript-image acquisition or reconstructed image was used.

| Finding | Records | Action |
|---|---|---|
| Same-reference digital word match | Matthew 17:21; 18:11; Mark 7:16; 9:44; 9:46; 11:26; 15:28; Luke 23:17; John 5:4; Acts 28:29 | 10 candidates for disclosure/context checks; not newly included |
| Word match within a passage with other mismatches | John 7:53; 8:1; 8:8 | Hold with the complete passage |
| Word match only in separate file consulted | Acts 24:7 in AC24.csv | Hold for the linked 24:6–8 reading |
| Different wording or unresolved mapping | Matthew 23:14; John 8:2–7, 8:9–11 | 10 unresolved attributions |
| Reference absent from the main digital file | Luke 17:36; Acts 8:37; 15:34 | 3 unresolved attributions |

## Consequential differences

- **Matthew 23:14:** the widows' houses saying appears at 23:13 in MT.csv;
  the adjacent sayings have different order. Even at that mapped reference,
  the digital text includes δὲ after Οὐαὶ, which POB's stored Greek lacks.
  A verse-number-only comparison would conflate order with wording.
- **John 8:5:** stored `ἡμῶν Μωσῆς` versus digital `Μωσῆς ἡμῖν` changes
  “our law” to “Moses commanded us.” This is not an accent/punctuation issue.
  Other mismatches include an added “to him” in 8:2, different participles in
  8:3, missing “testing” in 8:4, accusation phrasing in 8:6, construction and
  inflection in 8:7, additional words in 8:9–10, and a different verb in 8:11.
  Neither main JOH.csv nor the separate PA.csv supplies these nine local verses
  as exact word sequences. This does not identify their actual source edition.
- **Acts 24:7:** an isolated match is insufficient to insert a verse into a
  different surrounding reading. The [separate digital file](https://github.com/byztxt/byzantine-majority-text/blob/v2.0.3/csv-unicode/accents/no-variants/AC24.csv)
  includes additional clauses in 24:6 and 24:8. POB's shorter 24:8 currently
  explains “from him” as Paul; simply inserting Lysias's intervention could
  change the apparent antecedent. Resolve the unit, not just the numbered gap.

Four records lack an exported inline note: Mark 7:16, John 5:4, 8:2 and 8:5.
Existing manuscript dates and reception claims in the notes were not certified
by this edition comparison. A word match alone does not approve those claims.

## Review, checks and stopping condition

One independent check confirmed the John 8:5 mismatch and the three absent
references, and approved the narrowly qualified attribution flag. It did not
review every manuscript claim or certify all 27 translations. No judge loop.

Closeout verified 2026-09-07: **16 tests pass**. Validation checks preserve all
27 Greek strings against the snapshot, require
13 unresolved labels and no new export opt-ins, and test exporter rejection of
an unresolved source. Before/after checks also preserve the 13 records' complete
translation objects, lexical/theological decisions, generation data and archived
review objects. Existing missing draft hashes and legacy schema errors are not
retroactively repaired or represented as a clean historical-provenance pass.
All 27 pre-edit file hashes match the prior Git revision; the 14 nonflagged
records remain byte-unchanged. The 13 edited records introduce no new schema
errors. The unchanged Romans export remains 433 records, verified by its prior
SHA-256. No generated bundle/deployment.

Inventory SHA-256:
`033b2aa9e9256e8a1bdbcc0fadac123f405a8bcc3e3c86356b45628792666065`.

Reopen unresolved attribution only for an exact, identified edition/version
matching the stored text, or an explicit source-selection decision with its
English consequences reviewed. Do not relabel the text as TR merely because
it resembles a familiar reading. The 14 digital matches still need proportional
disclosure and linked-context checks; they are not automatic publication approvals.

## Acts 24 6 through 8 connected reading comparison

Compared against main `1138c56b6c4dc60cd8dea7b567d771e4222f5bac` on
2026-10-04 local date. Retain the connected shorter source and marker-free
English provisionally; keep verse 7 outside the reader. This completes the
bounded edition/context comparison, not historical priority or publication.
The [receipt](../sources/textual_restoration/applications/acts24_6_8_connected.2026-10-04.v1.json)
pins source versions/hashes, exact record changes and verification.

### Actual controls and the digital omission

The pinned [SBL apparatus](../sources/nt/sblgnt_apparatus/xml/Acts.xml),
Acts 24:6, labels the shorter unit WH, Treg, NA28 and RP and the longer unit
TR. These are edited-text comparisons, not independent manuscript votes.
Official byztxt v2.0.3 [AC.CCT](https://raw.githubusercontent.com/byztxt/byzantine-majority-text/v2.0.3/textonly-beta-code/AC.CCT)
24:06–08 has short 6, blank 7 and short 8; AC.csv agrees at the word level.
Its distinct [AC24.CCT](https://raw.githubusercontent.com/byztxt/byzantine-majority-text/v2.0.3/textonly-beta-code/AC24.CCT)
contains the longer alternative. That file alone cannot substantiate the
record's blanket “Byzantine majority” claim.

| Unit | SBL / checked Byzantine main | Separate AC24 CCT | TR reported in SBL apparatus |
|---|---|---|---|
| End of 6 | Seizure, directly to 8 | Intended judgment under their law; `κρῖναι` | Similar addition; `κρίνειν` |
| 7 | Not present | Lysias's force; `ἀπήγαγεν` | Similar account; `ἀπήγαγε` |
| Start of 8 | `παρ’ οὗ` directly | Command to accusers; `σοῦ` / `σέ` alternatives | Command with `ἐπὶ σέ` |

Do not combine these local differences into an allegedly verbatim longer
source. The [no-variants AC24 CSV](https://raw.githubusercontent.com/byztxt/byzantine-majority-text/v2.0.3/csv-unicode/accents/no-variants/AC24.csv)
prints `ἔρχεσθαι ἐπὶ παρ’ οὗ`, lacking both pronoun alternatives.
The [with-variants CSV](https://raw.githubusercontent.com/byztxt/byzantine-majority-text/v2.0.3/csv-unicode/accents/with-variants/AC24.csv)
retains them; CCT has `{B sou^: > se/: }`. The consulted
[conversion helper](https://raw.githubusercontent.com/byztxt/byzantine-majority-text/v2.0.3/scripts/beta_to_unicode_custom/beta_to_unicode_custom.py)
removes every curly-braced block when dropping variants; local regex
reproduction removes exactly this one. This establishes digital conversion
loss, not ancient omission. No pronoun is silently supplied and no upstream
file is edited. CCT/ASC are the ultimate digital sources per the project's
README; the repository declares public domain. The separately attributed
SBL apparatus remains CC BY 4.0, not relicensed by this comparison.

The [CSNTM P74 catalogue](https://manuscripts.csntm.org/manuscript/Group/GA_P74)
dates it to the seventh century, contradicting the third-century note.
This controls the catalogue date, not local attestation: no P74 ink, complete
manuscript apparatus, Latin or Coptic witnesses were collated. The old witness
list and categorical expansion verdict are archived, not certified. INTF's
workspace exposed interface headings only; browser GitHub directory access
failed while shell access succeeded. One wrong publisher XML path failed;
the existing pinned manifest supplied the correct path. No repeated broad
acquisition, generated image or new manuscript decipherment.

### Meaning and contrary transmission account

Root read Greek and POB at Acts 21:30–36, 23:27–30 and 24:5–6,8–9,22.
In the shorter unit, the seized person leads directly to “from whom”; Paul
is the natural referent. Greek leaves the object of “examining” implicit;
POB supplies “him” accordingly. The close gloss and current POB both have
Felix obtain information from that person by personal examination. No new
blinded English comparison or full-verse approval is claimed.

The longer account presents intended lawful judgment, forcible Roman
intervention and instructions to the accusers. That is the prosecution's
presentation, not independent corroboration of lawful conduct. Lysias becomes
a plausible “from whom” referent, not a necessary one: Paul remains the person
removed, the one with accusers and the person accused at the sentence's end.
A longer translation must first restore the three linked clauses, then
disclose whether Felix should examine Paul or Lysias. Verse 7 alone cannot
represent this unit.

Our working preference retains the shorter form. Explanatory expansion could
connect seizure with 23:30's instructions and 24:22's anticipated Lysias
appearance. The strongest contrary account preserves a pointed prosecution
narrative, with shortening motivated by criticism of Roman intervention or
its harder antecedent. These are hypotheses, not observed editing events.
No whole-unit eye-skip trigger is demonstrated; length or edition agreement
does not prove origin. One independent counterargument review also favors
provisional retention, but is not manuscript attestation.

### Application and stopping condition

Notes at 6/8 now disclose the connected unit and source-dependent antecedent.
Record 7 identifies its supplemental role, removes unsupported date/majority
claims and remains `reader_supplement: false`. Greek, marker-free English and
original generation metadata remain unchanged. Historical translation/review
objects are preserved; active status is draft/needs-review. Missing original
prompt/output hashes at 7 remain recorded schema debt, not invented history.

Reopen priority for verified connected manuscript evidence and a discriminating
transmission argument. A longer reader proposal needs an exact declared source
unit, pronoun/antecedent choices, matching 6/8 context and verified disclosure.
Another model vote or numbered-verse match is insufficient. Application checks
do not establish earliest text, fresh decipherment or public deployment.

One independent exact-candidate check reproduced both whole-Acts hashes and
all 28 chapters/1,002 base-edition IDs, with verse 7 still excluded. Only 6/8's
reader markers and notes change. Eighteen reader-note and nine supplement
tests pass independently; root also passed eighteen footnote tests, complete
reader validation, preservation, schema/debt checks, local links and whitespace.
Required remote CI governs merge. This scoped PASS is not a publication verdict;
no further preference loop is required.
