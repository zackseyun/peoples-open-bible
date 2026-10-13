# Ezekiel 36 language controls and Greek witness distinctions

Two Hebrew features cited for literary expansion reproduce in POB's declared
WLC edition. The reported Greek Adonai feature is witness-specific: Thackeray
describes Vaticanus, not the main text of every Greek edition. These findings
support testing a distinct section but do not date it or choose expansion over
secondary loss. Retain Hebrew/English and historical-priority HOLD. No source,
note, canon or fresh-decipherment change follows.

## Hebrew controls in the actual edition

The [OSHB WLC XML](../sources/ot/wlc/Ezek.xml), SHA256
90bf8adfa66b2f6695c702263fe668755c99c6afc386202c12de4f704f5d4e46,
contains48 chapters/1273 verse elements. Strip combining marks with Unicode NFD,
split declared slash components, and count direct verse-word elements only.
Nested variant words are excluded; a separate check finds no relevant nested
words for lemmas589,595 or2932. This is an edited text/annotation control,
not a census of ancient spellings or preserved manuscript ink.

Exact unpointed אני occurs169 times; אנכי occurs once, at36:28. For impurity
noun lemma2932, six tokens are singular:22:15,24:11,24:13 twice,36:17,39:24.
The two plural tokens are36:25 and36:29. Raw string searches also catch verbs
and adjectives; they cannot supply the noun count. Morphology is the project's
OSHB annotation, checked against the displayed forms, not new palaeography.

|Location|Stable word ID|Displayed form|Annotated noun number|
|---|---|---|---|
|22:15|26HpS|טֻמְאָתֵ֖/ךְ|singular|
|24:11|26ErY|טֻמְאָתָ֔/הּ|singular|
|24:13|26d5X|בְּ/טֻמְאָתֵ֖/ךְ|singular|
|24:13|26KKx|מִ/טֻּמְאָתֵ/ךְ֙|singular|
|36:17|26nCz|כְּ/טֻמְאַת֙|singular|
|36:25|26CPR|טֻמְאוֹתֵי/כֶ֛ם|plural|
|36:29|26eWp|טֻמְאֽוֹתֵי/כֶ֑ם|plural|
|39:24|26czb|כְּ/טֻמְאָתָ֥/ם|singular|

This corroborates two observations in the directly read
[Tov argument](EZEKIEL_36_OMISSION_MECHANISMS_2026-10-12.md#literary-expansion-argument).
Our inference is limited: rarity can fit expansion, but also a writer's local
variation or the subject's requirements. It cannot establish chronology, and
these counts alone cannot exclude loss of an already distinctive passage.

Reproduce from repository root without creating a new tool:

```python
from collections import Counter
from pathlib import Path
import unicodedata as U
import xml.etree.ElementTree as E
ns = {"o": "http://www.bibletechnologies.net/2003/OSIS/namespace"}
root = E.parse(Path("sources/ot/wlc/Ezek.xml")).getroot()
pronouns, nouns = Counter(), []
for verse in root.findall(".//o:verse", ns):
    for word in verse.findall("o:w", ns):
        text = "".join(word.itertext())
        plain = "".join(c for c in U.normalize("NFD", text)
                        if U.category(c) != "Mn")
        for pronoun in ("אני", "אנכי"):
            pronouns[pronoun] += pronoun in plain.split("/")
        if word.get("lemma", "").split("/")[-1] == "2932":
            nouns.append((verse.get("osisID"), word.get("id"),
                          text, word.get("morph")))
print(pronouns, nouns)
```

## Greek reading rather than generic LXX label

The publisher's [Rahlfs Hanhart2006 chapter36](https://www.die-bibel.de/bibel/LXX/EZK.36)
was read completely. Verses33 and37 print κύριος without Adonai. That initially
fails to reproduce Tov's reported transliteration, but does not refute a
different witness. The local first1K import has18 titles, none Ezekiel; guessed
file055 is Susanna/Theodotion. Raw Swete transcription hits in apparatus lines
are not a clean main-text or whole-book Greek count.

Thackeray's original1903 article, *JTS*4,398–411, is acquired through
[Zenodo1940137](https://zenodo.org/records/1940137), DOI10.1093/jts/os-iv.15.398.
Root reads extracted405–411 and visually checks complete405,407–408;
the source agent extracts all14 pages and reads/checks the targeted discussion.
The407–408 discussion identifies the Vatican manuscript explicitly:

|Verse|B report on407|A comparison reported on407|
|---|---|---|
|36:32|adonai + kyrios, Bᵃᵇ mg; B* has kyrios + kyrios|kyrios + ho theos|
|36:33|adonai + kyrios, B|kyrios + ho theos|
|36:37|adonai + kyrios, B|kyrios + kyrios + ho theos|

These unaccented term labels summarize a published comparison, not a fresh
diplomatic transcription. Preserve Bᵃᵇ mg without assigning correction dates;
unspecified B at33/37 is not an independent first-hand autopsy. His section is
36:24–38, not a demonstrated23c manuscript boundary. His proposed versional/
lectionary influence is an explanation, not observed editorial intention.
The lectionary he reports inspecting, Add.11841 fol.47v, covers24–28; it does
not directly attest the Adonai words at32,33,37. This1903 article does not supply
P967's later-discovered minus. The difference from modern printed Greek is
therefore resolved at the level of source identity, not historical priority.

## Madrid coverage narrows the acquisition plan

[Fundación Pastor](https://fundacionpastor.es/la-fundacion/papyri-matritenses/)
identifies the BNE deposit and Fernández-Galiano1971,7–77, rather than the
7–64 cited by Spottorno. Its28:19–43:9 span is not continuous preservation.
Root reads the complete BDPI detailed catalogue record bdh0000230543,
P.MATR.BIBL.1, record505, including its coverage summary: codex65–66
cover28:19–29:12;75–78 cover32:30–34:6;91–104 cover37:4–43:9.
Its mixed, plainly unrelated edition fields are ignored, not adopted as provenance.
The record's session-specific search URL is not persisted here.

That map excludes36→38 and begins after39→37. This is a catalogue inference,
not pixels or an exact transition-page determination. The linked
[BNE viewer](https://bdh-rd.bne.es/viewer.vm?id=0000230543) returns403 in the
source pass; no plate is read and the route is parked. Madrid remains useful
for adjacent text/order, not the decisive transition-image target. The earlier
report's newly identified Madrid edition route was a lead with unverified target
mapping, now narrowed—not proof that Princeton was the wrong holding. Do not
repeat the gated routes or turn broad spans into surviving letters.

## Source controls and next discriminating test

Baseline is e7b9b3765b94058e12a7bebcf4110db6c026ba11. Earlier case receipts,
the16 current36:23–38 records and the protected Genizah work remain unchanged.
No new parser, registry row or English preference assessment is needed.
The earlier argument report remains SHA256
d43de8c93e2e81eb1151618d07c6a1f21264c602b6fcbee2d6b07d6715ee809b.

Private Thackeray source:/private/tmp/pob-thackeray-1903.fbi8a4/thackeray-1903.pdf,
673998 bytes,14 pages, unencrypted, SHA256
e3ea1b16d07dc8d792c4491bf254183b33b03038d25bcbb9c75f41da3c8d4e26.
No PDF is imported/relicensed. Root's three complete checked renders:

|Printed page|Private render|SHA256|
|---|---|---|
|405|page-08.png|0232c6d5561c11ac7f569612d7387d5dde2c0ca312f822401ca738bf3c0f6bd8|
|407|page-10.png|95e50191e30044c6b80189519742e243528682d8f2c1eff57dd8a1693f79d959|
|408|page-11.png|909fd456cd1fe2374d38e29a5dbf4b9bef51b484398df091462780e7ff5bf217|

Next compare the exact B/A readings and correction layers with the current
apparatus, and test the broader vocabulary cluster rather than one rare word.
Seek original Latin reconstruction and precise Princeton transition pages;
Madrid catalogue metadata does not close those gates. A Greek revision signal
can establish a translation-layer difference without dating a Hebrew expansion.
Keep the lead on these discriminators; no more same-evidence preference votes.
One bounded independent critic passes the exact report at SHA256
7ab62bf278782e7030f2f5012544a857b61d0409e7e7edae1911a9f6b12c0778,
reproducing the counts and checking all20 retained inputs, four private hashes,
three complete target renders, the publisher text and complete catalogue record.
Root also checks48 chapters/1273 verses, local file links, whitespace and the
unchanged protected Genizah hash. This append records verification, not new
source evidence or historical-priority approval. No new corpus tests are claimed
for the two-path documentation scope; own exact-head CI still gates publication.

## Renewal promise comparison in the declared Hebrew form

The proposed dependence on 11:19–20 now has an explicit wording control, not
only a scholarly attribution. POB's WLC XML and current records distinguish
the following features. These edited Hebrew passages demonstrate a close
relationship; they do not establish which was composed or revised first.

| Feature | Ezekiel 11:19–20 | Ezekiel 36:26–28 |
|---|---|---|
| Heart | `לב אחד`, one heart; stone heart replaced with flesh heart | `לב חדש`, new heart; the same stone/flesh contrast |
| Recipient | Third-person recipients surround `בקרבכם`, within you, in 11:19 | Second-person recipients throughout 36:26 |
| Spirit and obedience | New spirit in 11:19; obedience is the purpose in 11:20 | New spirit in 36:26; **my Spirit** and explicit divine enablement in 36:27 |
| Covenant formula | People/God formula in 11:20, with `אני` | Formula follows the land promise in 36:28, with `אנכי` |

The [selected Rahlfs Hanhart Greek 11:19](https://www.die-bibel.de/bibel/LXX/EZK.11)
instead has `καρδίαν ἑτέραν`, another/different heart, and third-person recipients
throughout the verse. [Greek 36:26–28](https://www.die-bibel.de/bibel/LXX/EZK.36)
retains the new-heart and explicit my-Spirit distinction. These are readings
of the identified 2006 edition, not newly collated manuscript hands or an
attestation of 11:19 in P967. Do not retrovert the Greek adjective into uniquely
recovered Hebrew or equate selected Greek with every Greek witness.

Our inference: treating 36:26–28 as mere repetition loses its explicit divine
Spirit/agency emphasis. The alignment is compatible with literary expansion,
but also earlier related formulations or reuse in the reverse direction. Loss
of an already distinctive passage remains possible. Neither the recipient
regularity nor the heart adjective alone resolves the transmission history.
No source or English replacement follows.

POB currently renders 11:19's inner grant as “within them,” rather than the
declared WLC's second-person expression. [NET's own textual note](https://classic.net.bible.org/verse.php?book=Eze&chapter=11&verse=19)
reports Hebrew manuscripts and ancient versions supporting them; those unnamed
manuscripts have not been independently collated here. The choice must remain
an explicit regularization or variant choice, not an exact account of the
retained surface. Its current note invokes 36:26, whose recipient is you;
that parallel alone cannot establish them in 11:19. This is a source/English
accounting question, not approval of an anchor repair or new translation.

Current source and translation fields at 11:17–21 and 36:26–28 were read.
WLC XML retains the hash above. The five core current-record pins are:

| Repository path | SHA256 |
|---|---|
|`translation/ot/ezekiel/011/019.yaml`|`38713a93ddcd540159588dbd310e87723d290480ee133acc40f4eae82ff01f4d`|
|`translation/ot/ezekiel/011/020.yaml`|`e651bb1959bcf81b8609cc536d6d92f704d316c062aa9083feba6c08a61b9189`|
|`translation/ot/ezekiel/036/026.yaml`|`0066d01096605d65789232dcadc77ac7461c64fac2a176d61c2fd9d28e44ce05`|
|`translation/ot/ezekiel/036/027.yaml`|`8040088e2cf8ab907cf477cafdd555fc3acc0debf16392af88476386a22a3f2a`|
|`translation/ot/ezekiel/036/028.yaml`|`1404ca4cefda32b253a039da5b32b3b26a32c06a35c4e76c698999b6dc0ce40c`|

The six already pinned Qumran presentations have no displayed reference rows
for 11:19–21 in this navigation check. That is not an exhaustive absence claim
or evidence for either heart reading; unidentified, unlinked and supplied
material still requires edition-level assessment. No old receipt is rewritten,
new manuscript letters supplied, or optimum-English assessment claimed.

One bounded independent critique passes this new section at full-report SHA256
`02d8af1e4013266c679413b44b4ea2a8a98c0599ca3d6bfb516d7ebe31dee48d`,
with log SHA256 `80fcbb5ce9045b6669ffb0b5c80d05f3c0c25be09bde3e9af11811de25ebfe08`.
It checks the five pins, WLC, publisher Greek, NET note and displayed-reference
limits. Enablement describes the whole clause; OSHB word 26J3e is annotated
`HC/Vqq1cs` (Qal), not a causative stem. Root reproduces the pins and confirms
all eight current canonical consonantal word streams match the declared XML.
Whitespace and the new local document anchor pass; protected Genizah bytes
remain unchanged. No corpus test run, source-priority approval or application
is claimed. This successor is still separate from PR172's frozen head.

## Original Hebrew collation at Ezekiel 11 19

The preceding NET-only attestation limit is now narrowed. Root and the
acquisition subtask visually read De Rossi's complete original
[volume III entry, printed 135–136](https://archive.org/details/VariaeLectiones/Variae%20Lectiones%203/page/n149/mode/2up),
Parma 1786, including all five XI.19 subentries and their continuation.
These are PDF pages 150–151; title page 6 identifies the volume and date.
The same work's volume I, printed XLV–XLVI / PDF 60–61, supplies the notation.
This is a directly inspected published collation, not new manuscript glyphs.

| XI.19 expression | Reported contrast | Qualifications that affect its use |
|---|---|---|
| First grant | Them → you | Kennicott 1,114,150,253; earlier 91,155; doubtful 93. De Rossi 3,512,554; earlier 211,409. |
| Heart | One → new | Kennicott 150,158,160; Venice 1518 margin; Syriac. De Rossi 20 reports other books reading new, not necessarily its own running text. |
| Inner grant | Within you → within them | Numerous current, earlier and corrected reports are distinguished below; De Rossi 187 separately has `בקרבהם`. |
| Flesh recipient | Their → your | Includes Kennicott 1,72,96,115,150,155,158,180,224,253,602, with additional earlier/doubtful reports. |
| Second grant | Them → you | Includes Kennicott 1,93,150,155,224,253; earlier 28,72; corrected 3. De Rossi earlier 2,20,409; manuscript 319's margin reports other books reading them. |

The heart contrast is **`לב חדש`**, new heart, not Hebrew `לב אחר`, another
heart. No latter Hebrew attestation is supplied by this entry. Its reported
Syriac agreement and ancient Ambrosian copy are versional reports, not another
direct Hebrew manuscript or a newly verified shelfmark/date. The overlap of
identifiers across pronoun and heart loci does not prove five independent
readings, a uniform whole-verse form or historical priority.

For `בקרבם`, the unqualified Kennicott reports are 23,30,82,101,154,160,175,
225,228,246,601,602. Later corrected states are 150,158,172,176,198; possible
earlier states are 72,139. The Halle report adds a later state of 375, labeled
Erfurtensis 5; De Rossi's own collation adds Kennicott 420. His own unqualified
reports are 4,26,196,295,341,346,440,518,576,663; earlier 23; later states
2,174,211,304,409,413,596,789. External 103 and a later state of external 1
are separate source groups. Printed editions and ancient versions are also
reported; both 1518 editions place the alternative in the margin.

Volume I defines **primo** as an earlier reading subsequently changed, and
**nunc** as a later hand's change into the reported variant. Possible earlier
states and doubtful readings must retain those qualifications. Source groups
and text/margin annotations cannot be merged into an independent-manuscript
count. These XI.19 entries do not explicitly label the variants as formal qere.
The conventions also qualify inference from unlisted witnesses: incomplete
preservation, other readings and selective collation can prevent agreement.

The argument on 135–136 is especially relevant to the proposed 11/36 relation.
De Rossi reports Hillelian ancestry for you through Kennicott 82's margin and
his manuscript 413, whose second hand he says changed the reading. His Norzi
quotation describes Norzi first writing you in his autograph, then choosing
them after comparing copies and context, with possible influence from chapter
36 proposed for you. De Rossi endorses them. These are reported states,
ancestry claims and editorial reasoning, not proof of the ancient direction;
reading Norzi's quotation is not independent consultation of his original work.

**Effect:** within them now has an inspected primary Hebrew collation report,
and new heart has distinct reported Hebrew support. POB's current them choice
is not merely an unsupported English preference, but still differs from its
declared WLC surface. The new-heart reports could reflect assimilation to 36:26;
the pronoun reports explicitly keep that kind of contact in play. Retain the
current source/English provisionally, keep historical priority HOLD, and seek
modern target apparatus plus identifiable manuscript/hand evidence before a
critical-source application. No new decipherment, canon or optimum claim follows.

Private source directory: `/tmp/pob-ezekiel11-derossi.Ewsxue/`. The public
edition PDFs and deterministic page renders remain outside Git; no full
transcription or image is imported or relicensed. Root checks these six hashes:

| Private input | SHA256 |
|---|---|
|`derossi-vol3.pdf` — 289 pages|`9f59faefd7f26bc43cb9223091e78bf373288291d9e2fbef079f4071eea16187`|
|`derossi-vol1.pdf`|`a099c051a45c234e53b3fdb3092e9e043b4ef70fd9a29ff4691b38bb555d39e9`|
|`page-150.png` — III135|`77269d14ac1e4be208af631c2a577699b23b77438aaa0da4093e0dee59d1cea8`|
|`page-151.png` — III136|`8313580aac23ca6b857549d780a5181bf2e24c81cee7fae17a876fded236e4c0`|
|`convention-060.png` — IXLV|`c2b2524ab9e7d1e5b87cb34b8733bdc70cdf27eec62da9c4a854377350a45f20`|
|`convention-061.png` — IXLVI|`a49c0908b9e70b2ae6e58d221707de4f66afaf1a945d03723ef912d981a539c2`|

Only the declared target, surrounding entries, conventions and III title page
were read; neither volume is claimed as fully read. OCR located the entry;
the complete page images supplied the Hebrew, sigla and notation checks.

One bounded critique of this new collation evidence passes the full report at
SHA256 `6d40b0001ebf6f277af5727530bdf5027236237aaf12b2528cc31ad7e34e4cb4`
and log at `2b9f74b3e95dc59e4a72cfc7ad2711b96e8dd2894f00fc4d0ab7cf5cc170e3e8`.
The reviewer visually checks all four complete target/convention pages and
the title, reproduces six private hashes and five canonical pins, and confirms
the earlier reviewed parallel section as an unchanged 12,835-byte prefix.
This is a separate new-evidence check, not another source-priority vote.
Root reproduces the hashes, retains unchanged source/English and protected
Genizah bytes, and checks whitespace and the new local anchor. No corpus rerun
or application approval is claimed. Own publication checks remain separate.

## Original Greek apparatus at Ezekiel 11 19

Swete's [volume III](https://archive.org/details/theoldtestamenti03swetuoft),
third edition 1905, printed 402–403 / PDF 426–427, supplies a more precise
Greek control. The exterior text siglum B identifies the Vaticanus-based text;
it prints `καρδίαν ἑτέραν`, another/different heart, with third-person
recipients. The verse-19 apparatus reports two different variants:

| Witness | Printed variant | Effect |
|---|---|---|
| Γ, Cryptoferratensis | Omission of `ἐν` | Removes the preposition before the third-person recipient, not a change to you |
| A, Alexandrinus | Addition of `αὐτῶν` after the second `καρδίαν` | Adds their to the stone-heart expression, not to the first heart adjective |

No one/new-heart substitution, second-person replacement, Q reading, named
reviser or qualified correcting hand is printed in this target entry. That is
a limit of the inspected apparatus, not unanimity among all Greek manuscripts.
Swete's volume I conventions, printed XV–XVII / PDF 19–21 in the fourth
edition 1909 reprinted 1925, distinguish the exterior base-text siglum from
the witnesses collated for a page or part of it. They also distinguish the
original scribe, contemporary corrections, later hands and doubtful assignments.
Neither target variant carries such a hand qualifier; none should be invented.
Volume III's complete preface V–X and sigla page / PDF 24 identify the witnesses
and warn that the partly deciphered palimpsest Γ can be silent without agreeing.
These are published readings, not new manuscript autopsies or P967 attestation.

## Spirit and wrath at Ezekiel 39 29

The end of the restoration passage contains a consequential versional contrast:
POB's declared WLC has `רוּחִ/י`, my spirit, whereas the selected
[Rahlfs Hanhart 2006 Greek](https://www.die-bibel.de/bibel/LXX/EZK.39)
has `τὸν θυμόν μου`, my wrath. Swete III printed 472 / PDF 496 reproduces
wrath in its B-based text. Its entire verse-29 entry is `ου] ων AΓ`, a change
from singular to plural in the relative construction, not a Spirit/wrath
substitution. Γ resumes at 39:23 after its earlier break at 39:9, as the
surrounding printed 470–471 / PDF 494–495 show. No πνεῦμα alternative, Q
reading or correcting-hand label appears in the verse-29 entry. This selective
apparatus cannot establish all-Greek agreement, and neither printed edition
supplies a newly inspected reading of P967 here.

Under these construals the contrast changes the passage's emphasis: spirit
outpouring supplies a renewal promise, while wrath outpouring recalls judgment.
[LSJ's θυμός entry](https://logeion.uchicago.edu/θυμός), read in the browser,
includes spirit/disposition as well as anger; wrath is a contextual gloss, not
its only dictionary meaning. A local control supports that gloss: at
[Greek 36:18](https://www.die-bibel.de/bibel/LXX/EZK.36), the same outpouring
expression has θυμόν where current WLC/POB has `חֲמָתִ/י`, my wrath. This
parallel is not proof of a Hebrew חמה reading at 39:29. The interpretive
difference is worth displaying and investigating, but it does not by itself
recover different Hebrew consonants. The directly read enhanced BDB entry
for רוח, PDF 2247–2250, includes an anger sense in §3c and cites Zechariah 6:8
with a divine first-person suffix. Yet §9e specifically classifies Ezekiel
39:29 as reviving Israel, not anger. A lexical explanation of Greek wrath
from רוחי is therefore possible, not demonstrated; a different Hebrew
exemplar or Greek revision remains possible too. BDB's wider sense range is
not evidence that its own target interpretation is wrath.

The connecting clause requires a separate judgment. Greek `ἀνθ᾽ οὗ` links
the outpouring causally; AΓ's plural relative does not turn it into a temporal
expression. [LSJ's ἀντί entry on Logeion](https://logeion.uchicago.edu/ἀντί),
read in the browser, documents causal `ἀνθ᾽ ὧν` in §A.III.3. BDB's אשר §8c–d
on PDF 257 distinguishes causal from rare conditional/temporal uses, including
a passage it considers interpretable either way. This establishes grammatical
possibilities, not the preferred sense at 39:29. OSHB labels word 26hXM,
`שָׁפַכְתִּי`, Qal perfect first-person singular; that annotation alone cannot
decide a future-context English tense or the clause's causal/temporal relation.

Current POB says **“when I have poured out my Spirit”** and has no explanatory
note at 39:29. [NET's own rendering](https://classic.net.bible.org/verse.php?book=Eze&chapter=39&verse=29)
also uses when, while its sole note points to 11:19 and 37:14 without giving
an argument about this construction. Thus when is an attested published
interpretation, not an error established by the Greek causal wording. POB's
May 18 revision records a wholesale reversion to its drafter; that provenance
is not a fresh grammatical defense of the choice.

**Decision:** retain WLC and the current English provisionally. Open a bounded
reader-disclosure comparison for Spirit/wrath and causal/temporal alternatives;
do not replace Spirit with wrath or when with because without a separately
reviewed application. Compare actual modern target apparatus and P967's
preserved text before attributing the contrast to the shorter literary form.
The 36:26–27 my-Spirit/agency difference remains meaningful, but a Greek reading
at 39:29 cannot prove that a whole earlier form lacked Spirit theology.
No source-priority, canon or fresh-restoration claim follows.

## Greek and lexical input record

Baseline is main `3b2f9a008cf4122f51cfbc87e73dcadd826233db`. Current source and
English at 39:25–29 were read; 39:29 remains SHA256
`d768b8615338f43b9512bf8be890f45afcb0bc9114e353842d666ad4bb8c69ab`.
The WLC XML and five earlier core record pins are unchanged. Swete's main text
and apparatus were visually read on complete target pages, with the relevant
preface, sigla and conventions. BDB's title, enhanced-edition preface and
notation pages 50–52 distinguish this electronic layout from original print
pagination. Root read the complete רוח entry and the relevant אשר page;
the lexical subtask also inspected the complete אשר entry, PDF 253–258.
No whole-volume reading, new glyph recovery or fresh HALOT consultation is claimed.

Private source inputs remain outside Git:

| Input | SHA256 |
|---|---|
|`research_sources/swete-vol3-1905.pdf`|`5f0bfffabf0e588fd32e15bdb24b027872616da219e7f02da3dbdc115cf97d85`|
|`research_sources/swete-volume-i.pdf` — 1909 edition, 1925 reprint|`f2ac358a60bf8cc53e4cdc2dd18b9fba12185479ab46d97a19d20505bd4b8fea`|
|`research_sources/bdb-hebrew-college.pdf` — enhanced, reflowed 3132-page file|`9784a8d3b14dd7d4d8bcde138185f1dac86c896c59d32533868b03feab165ce3`|
|Swete PDF 426 render|`484114beddcd9928ca3ab74517c9f3b40f86443a8d6f36efec4200296058d8ac`|
|Swete PDF 427 render|`c5819b4ace468beae56fe4760e88b265312e19c93e5337b8d8b45b05681baad2`|
|Swete PDF 496 render|`c1c516a58421b8a6a5117348f67333de7baa0318fa03e3c4611aee0d6b99d407`|
|BDB PDF 2248 render|`e982673febb13d8edaae5983b6bf6730fd577929af3a5a447b3c795b45ab2ad0`|
|BDB PDF 2250 render|`0d6679a9b95425b8a6028af8de3dbb4456a87f3ee83daaaa4faa856480d59568`|
|BDB PDF 257 render|`664c32a97a7a7f0c430085a15af9acd4757269044bb81e3c483714ab5cceb59a`|

Source directory is `/Users/zack/Documents/Codex/2026-09-03/can-you-also-take-a-look/`.
Swete renders are in `/private/tmp/pob-ezekiel11-swete.cYuvMf/`; lexical renders
are in `/tmp/ezekiel39-bdb-L8nFhz/`. The volume-I scan is identified by its own
hash, not silently substituted for another registered scan. These checks pin
the inspected publication bytes, not manuscript authenticity or originality.

The bounded new-evidence critique passes report SHA256
`23e758913aeca4bc0d7a0f2c6f4be9e24363b2a724ddc9e1744de65d0a2f2012`
and log `aaa72b2a461ac4098f22fee62857b76287cf42537618b2ab8cefbd971a2686d0`.
A separate narrow check of the subsequently added Greek lexical range and
36:18 control passes report `28d23f2c0541ee048d76e9fb32825de2ebd892b187c610e195e5eaf476453526`
and log `51350bd7da9956f8b7c9d1e5e37d402a3dd2fffebb251b631737e2bccdf7e203`;
reversing only that delta reproduces the earlier reviewed bytes. The critic
uses Perseus's primary LSJ transcription for this added control, not a claimed
new Logeion browser visit. The 36:18 current record remains SHA256
`fb7106258c1a1d950e52aec09137c714814f1c10fc6379c09c94ed647e15a7c6`.
Root reproduces all nine new source/render pins, the canonical pins and the
unchanged protected Genizah hash; the prior 19,006-byte report is an unchanged
prefix. Whitespace and 368 local file links pass. No corpus test rerun, English
application or source-priority approval is claimed for this two-document scope.

## Ezekiel 39 29 reader draft on October 13

The [frozen reader candidate](../sources/textual_restoration/candidates/ezekiel39_29_reader.2026-10-13.v1.json)
adds two explanatory notes while retaining exact WLC and marker-free main
English. Note a belongs to when and gives the causal alternative without
declaring the temporal interpretation wrong. Note b belongs to my Spirit;
it discloses the consulted Greek editions' contextual wrath interpretation,
their word's broader range and the unresolved Hebrew transmission question.
The [contract](../sources/textual_restoration/comparisons/ezekiel39_29_reader_contract.2026-10-13.v1.json)
pins the complete candidate, source report, current doctrine/schema/exporter,
immutable whole-book Git manifest and the actual before/proposed exports.
This is an unapproved draft, not a main-English preference result or application.

The original metadata needed for the verse schema is recoverable, not invented.
Draft commit bb6ecf093ec3eef60e6958c73c10890139505dfd has exactly the current
source and main English, plus original ai_draft and optimal-equivalence fields.
Its full-record SHA256 is672e5693169ec219385114b13d4a6de23bcdfe4206e3de294b1d28059629a20e.
The May18 wholesale-reversion commit7e149b9c0845bf072717dfa5cf789b66809e6aa9
removed those fields, along with other rationale and review data. Only the two
required historical fields return in this candidate. The original provider
payload is not newly verified, and old HALOT labels, theological rationales
and approval scores are not restored as current authority. The candidate
archives today's revision-pass and English fields exactly, remains draft/needs
review, and preserves today's revision history. The unrelated divine-name
policy is not reapproved by retaining the existing sentence.

The P967 target is outside the cached Kenyon publications. Root and the source
subtask read 1937 printed VI/VIII / PDF10/12 and 1938 printed V–VI / PDF9–10.
The text's printed16→17 / PDF34→35 ends Ezekiel17:21 and begins Daniel3:72;
the plates' PDF28→29 likewise pass from fol.17r to71r. The separate Princeton
publication is *Princeton University Studies in Papyrology*3 (1938). Its broad
19:12–39:29 span, five missing leaves and page-number list are holding metadata,
not target letters or a demonstrated physical lacuna at39:29. These files
cannot add a P967 noun to the note. No gated acquisition is repeated.

The full proposed local export has48 chapters/1273 units; only39:29 differs,
both notes survive, and1272 other units remain identical. Its SHA256 is
312d4eae05c2f55bc63cf0c5e8fbb703aee656ce73586fd1d019e61616617565,
against baseline69bc676500f41cecef253c0f40069e5008718d4dee1371ab31a4cd5a3a865ca9.
Schema and marker checks pass with canonical bytes still unchanged. The generic
draft probe reports no source object in the lightweight payload; this is not
converted into a source-display or deployment success. Exact retained source
is separately bound in the candidate and Git evidence. Independent factual/
application review is still required; no new corpus-wide quality claim follows.

## Applied Ezekiel 39 29 notes

The independent factual/application critique passes the exact candidate at
dfda0b8dd51504f96b4974466006e31f407dc9da8be81368398c120be75b2cee and final
contractc2d4df57020a03d24d8336f4174a86924ba115efcc73315c80c87a4cf6ecab0e.
The [application receipt](../sources/textual_restoration/applications/ezekiel39_29_reader.2026-10-13.v1.json)
preserves the earlier review binding and the explicit serialization clarification;
the candidate's words did not change during review. The critic also reproduces
the exact metadata recovery, archives, complete proposed export and Kenyon
publication limit. This approves only these two notes and historical fields,
not source priority, divine-name policy, deployment or whole-verse optimality.

Root applies exactly the reviewed YAML bytes, SHA256
8d4d3343e5325ac09bc2252df7967624ccb88934f4aecb34959598425fb3589f.
The actual full-book export matches the proposed312d4eae hash above; both notes
survive and all1272 other raw canonical files and exported units are unchanged.
The six [new scoped tests](../tests/test_ezekiel39_reader_application.py) pass
in13.683seconds;64 shared reader/marker/source-guard tests pass in59.870seconds.
These are70 distinct post-application checks, not a new corpus-wide translation
evaluation. The four earlier preflight checks are not counted again. CI adds
this module and its two immutable Git baselines without removing existing checks.
Protected Genizah bytes remain unchanged, whitespace passes, and repository
publication still requires this successor's own exact-head checks.
