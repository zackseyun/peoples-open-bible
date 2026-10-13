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
