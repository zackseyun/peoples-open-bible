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
