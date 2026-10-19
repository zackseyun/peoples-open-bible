# Ahaziah age Greek manuscript evidence and reader disclosure

Date: 2026-10-19. Baseline: `a0ae3c29b4525087faa1ceab1ed2822301aa2f37`.

## Decision

Twenty-two is directly attested in multiple Greek manuscript reports at
2 Chronicles 22:2. It is not merely a modern conjecture from Kings.
This closes the specific Greek-attribution gap in the
[October 10 comparison](CHRONICLES_22_2_AGE_COMPARISON_2026-10-10.md).
Twenty remains a real competing Greek reading, not an incorrect translation
of twenty-two. Retain POB's recorded WLC source and forty-two provisionally,
but improve the existing note and remove the explanation that labels
twenty-two as an established harmonization.

The internal chronology makes forty-two a poor ordinary personal-age reading:
Jehoram begins at thirty-two, reigns eight years, and is succeeded by his
youngest son. Twenty-two is the leading correction candidate when these
controls and the versional evidence are considered. However, that preference
does not establish whether the Greek twenty lost an element, whether a
twenty-two form was harmonized, or when the Hebrew forty-two arose.
Historical priority remains unresolved. A Hebrew critical-source proposal
must identify its reconstructed numeral explicitly, rather than silently
translating the retained forty-two as twenty-two.

## Greek apparatus and its own key

Root and one bounded source scout read the complete target page in Brooke,
McLean and Thackeray, *The Old Testament in Greek*, II.3, *Chronicles* (1932),
printed 519 / PDF 141. The
[institutional PDF](https://tmcdaniel.palmerseminary.edu/Brooke%26McLean/LXX_Brooke%26McLean_2-3.pdf)
has 184 pages; its title verifies 1932. The selected body gives twenty.
The apparatus reports the following twenty-two forms:

| Age-unit report | Sigla and own-key manuscript numbers |
| --- | --- |
| Longer replacement including `ετων εικοσι δυο` | m = 71 |
| `ετων κβ′` | d = 107 |
| `ετων εικοσι και δυο` | n–y = n,p,q,t,y = 119,106,120,134,121 |
| Add `και δυο` after `εικοσι` | b,h,e₂ = 19+108,55,93 |
| Reorder to `ετων εικοσι`, still twenty | z = 554 |

These are reports from an edition, not fresh readings of manuscript pixels.
The range includes only the selected extant sigla, not every alphabet letter.
The own-key pairing b = b′ + b combines manuscripts 19 and 108; it must not be
flattened into an extra independent witness. The Armenian version also
supports the addition in the apparatus, but is not another Greek manuscript.

Root read the complete own key, printed v–vi / PDF 11–12, and the inherited
Genesis conventions, printed i–ii, vi and viii / PDF 9–10,14,16. The own key
matters: m and n here designate different objects from earlier volumes.
The [source packet](../sources/textual_restoration/comparisons/chronicles22_2_apparatus.2026-10-19.v1.json)
records the shelfmarks. The series follows Vaticanus where extant; neither
that selected text nor Swete is a reconstructed earliest Greek or an
independent ancient vote. No forty-two age variant is reported in this local
unit. Apparatus silence is not an exhaustive absence claim.

## Connected controls and the copying hypothesis

The full local source/English/notes were read for 2 Chronicles 21:5,20;
22:1–9; and 2 Kings 8:16–29. Neighboring notes were not comprehensively
adjudicated. Kings is a parallel account, not another Chronicles manuscript.

Cambridge II.2 *Kings* (1930), printed 325 / PDF 137, selects twenty-two at
2 Kings 8:26 and reports d's alphabetic abbreviation, also twenty-two.
Root and the source scout visually checked the complete page. No twenty
reading is reported in that age unit. The existence of twenty and twenty-two
in Chronicles does not itself demonstrate that a scribe added them to make
forty-two. No numeral-letter confusion or arithmetic conflation is accepted
as an observed copying event.

Root reread CAL's complete displayed chapter 22 and
[edition metadata](https://cal.huc.edu/get_file_info.php?coord=62039).
Its [22:02 row](https://cal.huc.edu/get_a_chapter.php?cset=S&file=62039&sub=22)
has `ܥܣܪܝܢ` and `ܘܬܪܬܝܢ`, twenty and two.
CAL identifies a Leiden-derived text with some corrections based on 7a1;
this is not a claim about every Syriac manuscript or a particular hand.
No AI-generated commentary was used.

Curtis and Madsen's original discussion, printed 418–422 / PDF 446–450,
was read in full, including the critical note on printed 420. Root visually
checked 419–420. They distinguish Greek B/A twenty from Greek L/Syriac
twenty-two and regard twenty-two as probably original. This supports a
reasoned correction candidate, not a newly discovered reading or an
independent manuscript. The
[archive item](https://archive.org/details/criticalexegetic11curtuoft)
is catalogued 1910, but its actual imprint says second impression **1952**.
The private filename retains 1910; it does not establish the scanned imprint.
Other historical/narrative claims on those pages are not adopted automatically.

The strongest objection remains harmonization to Kings or the connected
chronology. Multiple Greek reports establish attestation, not independence,
a shared Hebrew spelling, or the direction of change. The modern Antiochene
Chronicles edition and full modern Hebrew/Syriac target apparatuses remain
unconsulted. Reopen the source choice for their local transmission evidence,
not another vote on the now-established existence of Greek twenty-two.

## Exact application boundary

The [complete candidate](../sources/textual_restoration/candidates/chronicles22_2_reader.2026-10-19.v1.yaml)
replaces only note a and the first theological explanation, archives their
old bindings plus status/revision-pass/cross-check, and resets draft/needs-review.
Source, marked main English, note b, lexical array, original draft metadata,
other theological explanation and prior history remain unchanged. Note a
stays attached to the age/accession clause. No new note or reader-layout code.

The regression checks the exact complete record and historical archives,
all 822 Chronicles file paths/bytes outside this record, and the actual
complete-book exporter. Only verse 22:2's note may change; source and main
English must not. The
[application receipt](../sources/textual_restoration/applications/chronicles22_2_reader.2026-10-19.v1.json)
will distinguish independent review, local application, CI and public delivery.
No source-letter restoration, ImageGen evidence, canon or About change follows.

The PDF workflow supplied complete-page checks; the documentation workflow
preserves the old dossier and separates attestation from inferred history.
The reusable lesson is to expand a compressed apparatus against its own key
before assigning support, and to avoid labelling an attested alternative a
proven harmonization. No new general infrastructure is required.
