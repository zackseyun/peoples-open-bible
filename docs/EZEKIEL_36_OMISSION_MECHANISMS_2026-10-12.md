# Ezekiel 36 omission and chapter order arguments

Direct reading of Tov and Spottorno makes the shorter/longer-form question more
testable, not settled. Literary expansion has substantive linguistic support;
ancestral copying loss has a concrete, assumption-dependent reconstruction.
Retain POB's Hebrew form provisionally, keep historical priority on HOLD, and
make no source, English, note or canon change. These are published arguments
newly consulted by POB, not new discoveries or recovered ink.

## Literary expansion argument

Tov's complete [author-uploaded revised essay](https://www.academia.edu/29064229/54_Recensional_Differences_between_the_MT_and_LXX_of_Ezekiel_ETL_62_1986_89_101_Revised_version_Emanuel_Tov_The_Greek_and_Hebrew_Bible_1999_397_410),
*The Greek and Hebrew Bible* (1999),397–410, was read directly by root and a
read-only source agent. The original1986 printing was not acquired. The HTML
degrades Hebrew typography; no clean diplomatic glyph verification is claimed.

Tov argues that a relatively literal translator is unlikely to explain the
general shortening. His36:23c–38 discussion,408–409, combines pre-Hexaplaric
P967, the reported Old Latin minus, Jeremiah-like vocabulary, unusual Hebrew
forms and dependence on surrounding material/11:19. Note17 proposes comparing
revision vocabulary, including the treatment of Adonai at36:33,37. His conclusion
is conditional on the witnesses and textual interpretation. The essay's ordering
discussion concerns chapter7, not the36→38→39→37 sequence. It supplies neither
transition pixels nor an ancestral page-loss reconstruction. Our inference:
general literalness makes expansion serious, but does not exclude local loss
or a later Greek editor; literary forms should not be flattened into a composite.

## Hebrew reuse controls checked on October 15

**Result: specific literary correspondences are verified; their direction and
the cause of P967's shorter form are not.** Tracy J. McKenzie's
[2025 article](https://reference-global.com/article/10.2478/perc-2025-0004),
*Composition, Order, and Motivation in Ezekiel's Two Editions*, pp.69-73,
argues that 36:24-27 integrates material from chapters 11 and 37. Its argument
for 37:21 preceding 36:24 appeals to the taking of sticks and the nations/one
nation context. It also contrasts the obedience formulations in 11:20 and
36:27. These are literary arguments, not additional manuscript witnesses.

The following controls come directly from our vendored WLC/OSHB
[Ezekiel XML](../sources/ot/wlc/Ezek.xml), SHA256
`90bf8adfa66b2f6695c702263fe668755c99c6afc386202c12de4f704f5d4e46`.
Root and a separate read-only agent independently checked the verb combination
and the 11:19/36:26 differences. Root also read the eight complete verse-word
sequences at 11:17,19,20; 36:24,26,27; 37:14,21. This is a control on one
digital Hebrew edition, not a new collation of ancient Hebrew witnesses.

| Control | Observed source wording | Consequence |
|---|---|---|
| Three-verb combination | Only 36:24 and 37:21 contain verbal lemmas 3947, 6908 and 935, in that order: take, gather, bring. | Confirms a specific correspondence, stronger than a general shared restoration theme. The first verb is sequential-perfect 1cs in 36:24 but an active participle in 37:21; this is not an identical three-word quotation. |
| Heart and spirit | 11:19 has לב אחד; 36:26 has לב חדש. Both have רוח חדשה. | Correct the article's p.71 opening contrast of new/one *spirit*: the difference concerns the heart. Later on that page its own rendering correctly distinguishes them. This local slip does not invalidate the larger literary argument. |
| Persons and object marker | 11:19 has recipients "them," interior "your," flesh "their," then recipients "them." 36:26 uses "you/your" at all four positions and adds את before the stone heart. | Do not describe 11:19 as uniformly third-person or the passages as exact duplicates. Both have divine giving/removing and a heart of flesh. |
| Gift of the spirit | 36:27 begins with the object רוחי before אתן and has בקרבכם; 37:14 has ונתתי רוחי בכם. 11:19 already has בקרבכם. | The proposed combination has actual lexical support. Word order and shared phrasing alone do not date the combination. |
| Obedience | 11:20 begins למען; 36:27 has ועשיתי את אשר before walking in the statutes. | Preserve the purpose/causing distinction in interpretation. It does not independently prove a later theological stage. |

### Reproducible boundary and historical inference

The search covers all 1,273 verse elements, selecting only direct child `w`
elements: nested qere/note readings are excluded. Lemmas are matched by exact
slash-separated numeric component, allowing a trailing lemma-group letter;
morphology must contain a verbal component. This excludes nominal לקח at
17:5 and the proper name לבוא at 47:15,47:20,48:1. The annotated verbal counts
are 64,16,186 respectively; only the two reported verses contain all three.
Morphology is modern annotation, not independent historical evidence.

From the repository root, this reproduces the decisive two-hit result:

```python
import re
import xml.etree.ElementTree as E

ns = {"o": "http://www.bibletechnologies.net/2003/OSIS/namespace"}
verses = E.parse("sources/ot/wlc/Ezek.xml").findall(".//o:verse", ns)
wanted = {"3947", "6908", "935"}
assert len(verses) == 1273
for verse in verses:
    selected = []
    for word in verse.findall("o:w", ns):
        lemmas = {re.sub(r"\s*[a-z]$", "", x.strip())
                  for x in word.get("lemma", "").split("/")}
        verbal = any(x.lstrip("HA").startswith("V")
                     for x in word.get("morph", "").split("/"))
        if verbal and lemmas & wanted:
            selected.extend(sorted(lemmas & wanted))
    if wanted <= set(selected):
        print(verse.get("osisID"), selected)
# Ezek.36.24 ['3947', '6908', '935']
# Ezek.37.21 ['3947', '6908', '935']
```

Our inference is narrower than historical priority: the longer passage is
integrated with language elsewhere in Ezekiel. A later compiler could combine
those passages, but an already-composed, similarly integrated passage could
also be lost in a Greek ancestor. Shared authorship or a common formulation
also requires consideration before assigning a unique borrowing direction.
The short-form manuscript's existence and the longer form's internal
coherence are therefore not independent proofs that expansion caused the
difference. Nor does a literary relationship itself date the chapter-order
change. The [now-observed P967 joins](EZEKIEL_36_LONGER_FORM_EVIDENCE_2026-10-12.md#papyrus-967-the-actual-36-to-38-join-acquired-on-october-15)
confirm the surviving sequence, not the proposed ancestral event.

POB 36:26-27 already retains new heart, new spirit, my Spirit and divine causing
of obedience. This comparison warrants no source, English or note change and
does not certify the remaining verse wording. Retire this exact lexical search
on these bytes. Further work needs a discriminating translation-technique or
critical-apparatus comparison at the disputed passage, not another tally of
these same parallels. No generated image supplies evidence.

### Consultation record

The [publisher PDF](https://reference-global.com/2/v2/download/article/10.2478/perc-2025-0004.pdf)
has SHA256 `559bcdb86e0ed28720b8a25f2db7a40ff382769f470b3aefb940b353a55928a1`.
Printed pp.63-74 were read through extraction and pp.69-73 were inspected as
complete rendered pages, including notes and Hebrew. This is not a claim to
have read the complete article or independently consulted its cited works.
The publisher states CC BY-NC-ND 3.0; the PDF and renders remain outside Git,
with no relicensing or reproduction of the article. The independent Hebrew
check is a factual control, not a vote certifying the historical reconstruction.

The bounded documentation review caught a normalization edge case: a space
before a lemma-group letter was not stripped by the first recipe. The corrected
recipe handles both `3947a` and `3947 a`; rerunning it preserves the two-hit
result. All 430 relative file-link targets in this report and the research log
resolve, and `git diff --check` passes. The Ezekiel XML, both checked POB
36:26-27 records and protected Genizah file retain their input bytes. These
checks validate the documentation and unchanged-text boundary, not priority.

## Greek translation-technique controls checked on October 15

**The longer passage has a distinctive Greek profile; this does not uniquely
establish later Hebrew expansion.** The original
[Thackeray article](https://www.gospelstudies.org.uk/biblicalstudies/pdf/jts/004_398.pdf),
JTS 4 (1903),398-411, was acquired through the public-domain article archive
after the Zenodo route failed. Root visually read complete printed 407-408
and extracted 407-411; the source agent visually read 407-411. Neither claims
a full-article reading or independent inspection of all its cited witnesses.

Thackeray identifies distinctive Greek renderings in 36:24-38, comparing them
with other translations. He proposes incorporation of an early Jewish
lectionary version, but also considers Christian lectionary replacement of an
older Greek translation. His directly discussed medieval lesson contains only
36:24-28. Its extension to the larger passage and the proposed ancient history
are conjectural, not observed in that manuscript. This is an argument about
Greek transmission, not proof that Hebrew lacked the passage.

### Actual edition and Hebrew controls

Root separately checked the pinned OpenScriptorium surface text and the
original printed Swete edition, rather than importing Thackeray's examples as
manuscript data. The [digital input and its limitations](EZEKIEL_36_LANGUAGE_CONTROLS_2026-10-12.md#inputs-and-reproducible-screen)
remain unchanged: 1,267 uniquely labeled rows, SHA256
`06f1b82b9c95fc5c2c1735c928cdb44299fea2f8d9b9fc68eda0e14118920a1f`.
Only ordered `surface` strings are used, not generated morphology or reasoning.
The Hebrew input is the same hash-pinned WLC/OSHB Ezekiel XML used above.

| Feature | Directly checked result | Boundary |
|---|---|---|
| Gathering at 36:24 | The sole surface prefix `αθρο` hit is ἀθροίσω. All 16 Hebrew verbal קבץ tokens in 15 verses were checked in complete Hebrew/Greek rows. The target is the only aligned use of this Greek form. | Other corresponding positions use συνάγω forms (9), εἰσδέχομαι forms (5), and περιστέλλω (1, 29:5). The Greek distribution is not simply a binary choice, and shared verse numbers alone are not alignment. |
| Lands at 36:24 | γαιῶν is present in Swete and the digital text. Two further `γαι` prefix hits, 39:11 and 39:15, belong to the named burial-valley expression, not additional plural "lands" uses. | Prefix retrieval needs contextual classification; three hits do not mean three lexical parallels. |
| Passing and garden | παροδεύοντος at 36:34 and κῆπος at 36:35 are the sole `παροδευ` and `κηπ` prefix hits in this digital book. Swete prints both. | This confirms a selected edition's distinctive vocabulary, not every manuscript or all Greek literature. |
| Compound connection at 36:34 | The normalized three-token sequence ἀνθ' ὧν ὅτι occurs only here in the digital book and is printed in Swete. Hebrew has תחת אשר. | The article's verse-34 locator is correct; no automatic inference to a different Hebrew clause follows. |
| Divine title at 36:33,37 | Swete's Vaticanus-based main text prints ἀδωναὶ Κύριος at both loci. Its apparatus records different A/Q readings. The digital control and the publisher's Rahlfs-Hanhart text instead have single κύριος. | "The Greek has Adonai" erases a consequential manuscript/edition distinction. Zero digital `αδων` hits does not refute its attestation in Swete's base witness. |
| Divine title at 36:32 | Swete's main text has Κύριος Κύριος; its apparatus records an Adonai reading under the marginal B correction siglum. | Do not merge a correction into the base-hand text or count it as a third identical original B reading. No fresh dating of the correcting hand is claimed. |
| Recognition at 36:38 | Swete and the digital text omit an explicit εἰμί; Swete's apparatus supplies it for A. At 37:6 Swete and the digital text include it. Hebrew has אני יהוה at both loci. | A demonstrable variation in Greek expression, not a recovered Hebrew omission. No whole-book formula-frequency claim is made here. |

The 15 Hebrew קבץ verse references are 11:17; 16:37 (two tokens); 20:34,41;
22:19,20; 28:25; 29:5,13; 34:13; 36:24; 37:21; 38:8; 39:17,27.
Selection uses direct verse-child words with lemma component 6908 and a verbal
morphology component; nested readings are excluded. Alignment was checked in
context. At 11:17 the neighboring Hebrew אסף corresponds to συνάγω while קבץ
corresponds to εἰσδέχομαι. At 29:5 the two negative clauses must likewise stay
distinct: the second Greek verb is περισταλῇς. At 39:17 both gathering verbs
are rendered with συνάχθητε. These controls prevent presence-only matching.

This reproduces the Greek retrieval from the downloaded pinned `ezekiel.json`:

```python
import hashlib, json, unicodedata as U
from pathlib import Path

p = Path("ezekiel.json")  # Private copy from the pinned upstream URL above.
assert hashlib.sha256(p.read_bytes()).hexdigest() == (
    "06f1b82b9c95fc5c2c1735c928cdb44299fea2f8d9b9fc68eda0e14118920a1f")
rows = json.loads(p.read_text())
assert len(rows) == len({r["ref"] for r in rows}) == 1267
def norm(s):
    return "".join(c for c in U.normalize("NFD", s.casefold())
                   if not U.combining(c)).strip("'\u2019\u1fbf")
for prefix in ("αθρο", "γαι", "αδων", "παροδευ", "κηπ"):
    hits = [(r["ref"], [w["surface"] for w in r["words"]
                       if norm(w["surface"]).startswith(prefix)]) for r in rows]
    print(prefix, [(ref, words) for ref, words in hits if words])
for r in rows:
    tokens = [norm(w["surface"]) for w in r["words"]]
    if any(tokens[i:i+3] == ["ανθ", "ων", "οτι"]
           for i in range(len(tokens)-2)):
        print("compound", r["ref"])
```

### What changes in the historical judgment

The observed Greek profile now needs an explanation in addition to the Hebrew
literary correspondences. A simple claim that the *same* uninterrupted Greek
translation was merely lost in one branch does not account for the profile;
variation within a translator, revision, replacement or a separately translated
section must also be assessed. But loss followed by a replacement translation
in another branch can also produce a shorter witness alongside a distinctive
longer Greek form. The observations alone do not establish that this happened,
or choose it over Hebrew expansion followed by translation.

The features are not seven independent ancient witnesses. The scholarly
argument, Swete's edition and its digital comparators are related descriptions
of a transmission history; neither an exact probability nor a unique translator
is inferred. Thackeray's Hexaplaric comparisons remain his reported evidence:
the corresponding Aquila/Symmachus/Theodotion apparatus was not newly consulted.
Likewise, no fresh manuscript inspection of the medieval lectionary is claimed.

Retain POB's source and English, with historical priority unresolved. The next
discriminating input is the full critical apparatus and translation evidence
behind the proposed revision affinities, not another search of these same
surface strings. In particular, establish which Greek readings are earlier
within each variant's transmission before assigning the profile to an original
translator or using it to reconstruct a missing Hebrew edition. No ImageGen
output is evidence and no missing manuscript letters were recovered here.

### Acquisition and visual scope

Thackeray PDF SHA256:
`97172a9cfa2e92012df13207dd831e6f78966ae8d511dade90e96fedac259cca`.
Printed 407-411 correspond to one-based PDF pages 11-15, after the archive's
cover. The original article is public-domain material; no full scan is imported.

The [Swete manifest's volume III](../sources/lxx/swete/MANIFEST.md) was
reacquired and matched its SHA256
`5f0bfffabf0e588fd32e15bdb24b027872616da219e7f02da3dbdc115cf97d85`
and 932-page count. Root visually inspected complete printed 464-465,
one-based PDF 488-489, including their apparatuses. The 150-dpi render hashes
are `13bcfb1946169c595608e835e933d148c30813f32dc182e43a31cd6d6bf88df0`
and `06dcf366a9bab3461debf971658d3725cdfac969eb319c8bb261252cdd7c3a32`.
These are published edition readings, not fresh Vaticanus image transcription.
The [publisher's modern chapter 36](https://www.die-bibel.de/bibel/LXX/EZK.36)
was checked separately at the target clauses; it is not another manuscript.
Full PDFs, renders and the digital Greek file remain private and unrelicensed.

A bounded independent review reproduced the Greek recipe and checked both
complete Swete pages and the article's stated alternatives, finding no concrete
defects. It did not independently recheck the Hebrew alignments or modern
publisher text. Root verified all 433 relative file-link targets in this report
and the research log, the unchanged Hebrew XML and seven target POB records,
and the protected Genizah hash; `git diff --check` passes. No broad corpus or
historical-priority certification follows from these scoped checks.

## Checking the reported Hexaplaric parallels in Field on October 15

**Subsequent direct-source qualification:** the [1840 edition and photographed
Barberini margin](#the-1840-edition-and-barberini-margin-checked-directly)
below support the spelling αθροίσω, while retaining the attachment problem.
The following section records what Field prints; its ωρθρισω report is not
our current transcription of the Barberini image.

**The affinities have a published basis, but the gathering parallel is less
secure than a bare citation suggests.** The preceding section left Thackeray's
Aquila/Symmachus/Theodotion comparisons as reported evidence. Root now inspected
the corresponding entries and source notes in Field's 1875 volume II. This
upgrades the consultation status to direct edition inspection, not manuscript
autopsy or proof of attribution. It also uncovers an editorial qualification
that must accompany the proposed Greek translation profile.

The [same cached Toronto scan](https://archive.org/details/origenhexapla02unknuoft)
used in the [earlier Spirit-reading work](EZEKIEL_36_LANGUAGE_CONTROLS_2026-10-12.md#field-edition-and-the-transmitted-spirit-reading)
was rehashed: SHA256
`85eaddcd38ac4bd35e7ee96409d9abdea3dab1b0513fe8c97cb67b72c8fcc1ff`,
1,136 PDF pages. No new acquisition or independent witness is counted.

| Ezekiel locus | Field's actual entry | Printed page / one-based PDF; note and source qualification |
|---|---|---|
| 20:34 | Under וקבצתי, Ο′ καὶ εἰσδέξομαι; Σ. Θ. καὶ ἀθροίσω. | 819 / 835, note 72: Codices 86,88 are reported with **ωρθρισω**, and attach the reading to preceding καὶ ἐξάξω / והוצאתי. Field's displayed spelling and alignment are not an unqualified transcription of those codices. |
| 29:12 | Under בארצות, Ο′ εἰς τὰς χώρας; **Πάντες** ἐν ταῖς γαίαις. | 850 / 866, note 30: *Idem*, referring to note 29's Cod.86, *teste De Reg.* Preserve the collective attribution rather than manufacture three separately inspected witnesses. The other continuous-text details in note 29 concern its own entry. |
| 7:5 | The title has Α. Σ. Θ. ἀδωναΐ κύριος. | 783 / 799, note 5: *Idem*, through note 4 to Cod.86, *teste De Reg.* |
| 18:23 | Under אדני יהוה, Ο′ κύριος; **Πάντες** ἀδωναΐ κύριος. | 814 / 830, note 34: Cod.86, *teste De Reg.* |
| 28:13 | Under גן, Ο′ τοῦ παραδείσου; Θ. τοῦ κήπου. | 847 / 863, note 21: Cod.86, *teste De Reg.* Note 21 also comments on Norberg's transcription of the Syro-Hexaplar text; the Greek Θ reading is sourced to Cod.86 through De Reg. |
| 31:8 | Under בגן, Ο′ ἐν τῷ παραδείσῳ; Α. Θ. ἐν τῷ κήπῳ. | 854 / 870, note 19: Cod.86. |
| 33:28 | Under ואין עובר, Ο′ διὰ τὸ μὴ εἶναι διαπορευόμενον; Σ. μηδενὸς παροδεύοντος. | 863 / 879, note 59: Cod.86, *teste De Reg.* |

At 20:34, the main entry supports the existence of a published Σ/Θ attribution,
but note 72 makes its exact form and attachment uncertain. It does not explain
how Field resolved those difficulties. The first quick reading of the small
parenthesis was corrected using an enlarged view: the note does **not** simply
repeat ἀθροίσω. Do not silently repair ωρθρισω into the proposed form, or turn
Field's placement under קבץ into independently verified manuscript alignment.
This qualification narrows the support for that particular revision affinity;
it does not erase ἀθροίσω in the actual longer Greek passage at 36:24.

### Why these are not independent votes

Root also reread Field's complete Ezekiel introduction, printed 765-767 /
PDF 781-783. At 766 he identifies Cod.86 as the Barberini manuscript and
describes De Regibus's published collation of its marginal readings. At 767
he argues that the marginal material reported from Cod.88 derives from 86,
appealing to corresponding gaps and the history of copying. This is Field's
documented dependency argument, not a freshly established manuscript stemma.
It is nevertheless a concrete reason not to treat the two cited numbers as
two independent Greek votes. Several different lexical parallels also depend
on the same Cod.86 report; lexical diversity and witness independence are
different properties.

The inspected source notes for these seven entries cite Greek codices or a
collator's report, unlike Field's explicitly Syriac-mediated 39:29 Spirit
entry. That distinction improves provenance, but does not establish that Field
personally saw every letter, that the attribution labels are original, or that
the readings date the longer Hebrew passage. Neither Πάντες nor Σ. Θ. is a
license to infer three or two independent Hebrew exemplars.

**Decision:** retain Hebrew and English; reduce the evidentiary weight assigned
to the apparently exact 20:34 gathering parallel. The published garden,
passing and title parallels remain real edition evidence. They do not uniquely
identify the translator of 36:24-38 or establish whether expansion, revision,
replacement or ancestral loss produced the observed forms. No automatic Hebrew
retroversion, generated restoration or source-priority approval follows.

Further work on this specific difficulty should inspect De Regibus's actual
20:34 entry or the correctly identified Cod.86/88 margins, distinguishing the
source spelling, attribution sign and attachment. Another citation of Field
or Thackeray would not add independent evidence. The original chapter-36
critical apparatus and independent evidence for Hebrew literary stages remain
separate requirements; this bounded edition check does not complete them.

### Scope and reproducibility

Root visually inspected all seven complete target pages above, reading the target entries and footnotes,
and the three introduction pages. A source agent independently read the complete
20:34 and 29:12 pages and enlarged note 72. No complete Field volume, manuscript
image, De Regibus edition or global sigla survey is claimed. Greek snippets
reproduce the relevant printed words; they are not newly recovered ancient ink.
The public-domain scan and rendered images remain outside Git. PDF hash plus
the explicit printed/PDF locators identify the consulted source without making
render counts into additional witnesses. The unused navigation render of PDF
831 is not claimed as a target-page visual inspection.

The final bounded review checked the five additional entries and the dependency
discussion. It corrected the description of 28:13 note 21: its Syriac parenthesis
belongs to that same note, not a separate neighboring note. The Greek attribution
still cites Cod.86 through De Regibus. All 477 relative file-link targets in
the three edited reports resolve; only those documents changed, the protected
Genizah hash is unchanged, and `git diff --check` passes. These checks do not
certify historical priority or the underlying manuscript readings.

## The 1840 edition and Barberini margin checked directly

**Result: strengthen the spelling evidence, retain the alignment qualification.**
The actual Barberini photograph appears to read αθροίσω. It does not reproduce
the ωρθρισω sequence reported in Field's note. The 1840 edition already prints
ἀθροίσω, so this printed form cannot be attributed to Field alone. Both the
edition's alignment and the photograph's apparent reference sign attach it to
the preceding "bring out" clause. Neither directly verifies it as a rendering
of the following Hebrew קבץ. No POB Hebrew, English or reader note changes.

### Edition, photograph and interpretation kept separate

The public [1840 De Regibus scan](https://archive.org/details/bub_gb_mNtsGShyDM0C)
is *Iezeciel secundum Septuaginta ex Tetraplis Origenis*, Rome, Salviucci.
Root visually checked its title and complete printed pages 143 and 149
(one-based PDF 7, 159 and 165), including the relevant apparatus. The acquisition
agent independently checked these and the Monitum; neither read the full volume.

| Evidence | Actual observation | Limit |
|---|---|---|
| De Regibus p.143, 20:34 | Main Greek has καὶ ἐξάξω … καὶ εἰσδέξομαι. Apparatus places Σ. Θ. Ο. καὶ ἀθροίσω under והוצאתי, followed by Ο. ἄλλως, καὶ ἐξάξω C. B. The Latin contrasts *et congregabo* with *et educam*. | Published alignment is "bring out," not "gather." Its three attribution labels are not three separately inspected ancient exemplars. |
| De Regibus p.149, lower right | The Barb./Idem source chain expressly extends to readings in verses 32,34,35. | This is another report of Barberini, not an independent manuscript vote. No local explanation for Field's different spelling was found on these inspected pages. |
| [Barb.gr.549 folio 266v](https://digi.vatlib.it/view/MSS_Barb.gr.549/0560), upper-left margin | Letters appear to read αθροίσω, without a preceding καί. Three overmarked signs resemble ϲ / θ / ο. A curved dotted sign above the word resembles the sign over main-text ἐξάξω. | Accents, the complete siglum convention and reference-sign system have not been exhaustively established. The apparent attachment is stronger than inference from vertical proximity alone, not a complete palaeographical edition. |

Root inspected complete folios 266r and 266v, then the native-size 266v image
and the source service's margin detail. The end of 266r and opening of 266v
locate 20:33–34 by actual words: βασιλεύσω ἐφ' ὑμᾶς followed by ἐξάξω and
εἰσδέξομαι. A second agent read the images before consulting our Field account
or the proposed transcription. It independently obtained the same letter
sequence and apparent attachment, while withholding a confident expansion of
the third siglum. This is an independent check of the same pixels, not another
textual witness. The edition's Ο./LXX expansion is not silently substituted
for an independently established manuscript convention.

The [Vatican manifest](https://digi.vatlib.it/iiif/MSS_Barb.gr.549/manifest.json)
contains 614 canvases and labels p0559/p0560 as 266r/266v. An indexed scholarly
[figure caption](https://zenodo.org/record/4282218/files/PV%20NG%20Transmission%20of%20the%20Tetragrammaton%20in%20Judeo-Greek%20and%20Christian%20Sources.pdf)
provided the Barb.gr.549/Rahlfs86 and 266r/20:27 locator; that paper was not read
in full. The verse locus here was checked against the image, not accepted from
the search snippet. A trial at Chig.R.VII.45 folios 272r/v instead showed Tyre
material, not the desired 20:34 margin, and contributes no target reading.
Field's own pp.766–767 distinguish R.VII.45 from his Cod.88/R.VII.46: their
historical numbering must not be flattened into an assumed shared shelfmark.
The Cod.88 target remains uninspected; no explanation of the discrepancy with
Field's note or new manuscript stemma is claimed.

### Provenance and stopping point

The De Regibus PDF has 387 pages, SHA256
`81a87d151eb2227e541c8403038e4f0d5b6852b219cb0c7a8f3842538d2ad856`.
The Vatican manifest and full 266r/266v JPEG hashes, respectively, are:

```text
400629931761100c8acbb658688623f0a60c7dfd161024758f69c8184f1ff173
bf883eaec2f897d50dbbcd67709a7de63c605f2b0ef84e91ce8e64a45c28d591
12e30dfd09af8abd76014e7dee849a23d6747ba4f4e13f9fa30ec2425e969994
```

The images came from the manifest's image services using `full/full/0/default.jpg`;
the inspected margin detail uses region `450,500,400,150`, without image
generation or pixel reconstruction. All source files remain outside Git.
The Vatican viewer permits personal/study use and requires permission for
publication of its images; no manuscript image is republished here.

The methodological correction is consequential: an edition's caution can
itself need correction against its source. We now have positive photographic
support for the lexical form, but not for Field's Hebrew alignment or a unique
translator of Ezekiel 36:24–38. This closes the bounded acquisition step; do
not make further readings of these same pages into new progress. Return to
the passage-specific chapter-36 apparatus and the competing literary/loss
mechanisms. Resolve Cod.88's margin only if it can discriminate those arguments,
not merely to accumulate another dependent citation. Historical Hebrew priority
and any ensuing POB change remain unapproved.

The bounded final review found no concrete factual defect in the new edition
comparison or image qualifications. Root verified the PDF page count/hash,
manifest count/folio labels, 479 relative documentation file targets and the
unchanged protected Genizah hash. Only the three research documents changed;
`git diff --check` passes. These checks do not certify the manuscript's siglum
system, historical priority or a corpus-wide optimum.

## Copying loss counterargument

Spottorno's [original publisher PDF](https://emerita.revistas.csic.es/index.php/emerita/article/download/780/822/842),
*Emerita*50(1982),93–98, was acquired and all six pages/notes visually read.
The printed title ends23b–38; catalogue titles ending23b–28 must not silently
replace it. Her argument requires more than one scribal eye-skip:

| Printed pages | Proposed evidence or mechanism | Material limitation |
|---|---|---|
|94–95|The Latin material preserves37 before40; the36 minus and wider arrangement are inferred through reconstruction.|This is her assessment, not a fresh collation or proof that later scholarship found no further evidence.|
|95–97|An ancestor could lose one page containing the36 ending and relocate two pages of37 after the four pages of38–39.|The ancestor's format is hypothetical, not P967's observed page layout.|
|96–97|A second proposal skips three pages and reinserts37 in the wrong place.|It needs an unsupported53-letter omission at37's end; the author explicitly acknowledges that assumption.|
|98|Linguistic lateness of the passage need not explain the order change; accident remains possible.|She does not claim to prove the accident happened.|

Her capacity calculation averages1572 letters in Ziegler's text and1451 in B:
1511.5, rounded1512. It is an assumed page unit, not a measured lost leaf.
Alternative one-/two-column layouts and abbreviations allow flexibility. Root
checked the arithmetic, not the underlying independent letter counts.

## Testing the page-capacity argument on October 15

**A roughly compatible size is not a demonstrated copying event.** The earlier
arithmetic check did not test the role of the additional chapter-37 omission
or compare an independently counted text. Root and a separate source reader
now checked complete Spottorno pp.95–97, including notes 11–14, for that purpose.
This is a new control on the model, not another acquisition or reading counted
as a new manuscript. No POB source, English or note changes.

Three distinctions matter:

1. **The table combines text bases.** Note 13 uses the mean of Ziegler and B
   for page 1, but says the other page counts and adopted wording use 967.
   It therefore does not independently reproduce the layout of a single
   witnessed exemplar. Note 12 expressly allows abbreviations and small
   textual differences; those freedoms affect how discriminating the fit is.
2. **The proposed extra deletion supplies an endpoint, not a capacity necessity.**
   Her displayed chapter-37 tail contains 54 alphabetic Greek letters:
   `ο αγιαζων αυτους εν τω ειναι τα αγια μου εν μεσω αυτων εις τον αιωνα`.
   She labels it 53; excluding the initial ο gives 53, but the displayed omission
   includes it. This one-letter discrepancy is minor, not a refutation. More
   importantly, her two chapter-37 pages total 1,507 + 1,473 = 2,980. Restoring
   all 54 letters gives 3,034, or 1,517 per page, close to her nominal 1,512.
   The second page would contain 1,527 rather than 1,473. Her permitted layout
   flexibility does not show that this text must be deleted to fit. Removing it
   instead creates the matching recognition-formula ending needed by her
   particular three-page eye-skip proposal. She explicitly acknowledges the
   absence of manuscript support for that deletion on p.97.
3. **The exact recognition formula is itself text-dependent.** Note 11 and the
   diagram distinguish readings with and without εἰμι at 36:38. The pinned
   Greek control below lacks it there, while 36:23 has it. The model's displayed
   exact match is a selected variant, not invariant Greek wording. Similar
   endings could still prompt a copying error; lack of exact identity does
   not exclude every possible eye-skip.

### Independent size sensitivity, not replication of 967

The already pinned [Greek surface-text input](EZEKIEL_36_LANGUAGE_CONTROLS_2026-10-12.md#inputs-and-reproducible-screen)
provides a reproducible modern-edition control. We count alphabetic characters
after NFD decomposition, excluding spaces, punctuation, accents and combining
iota subscripts; words remain expanded, without hypothetical sacred-name
contractions. Only ordered `surface` strings are used. No generated morphology,
confidence, reconstructed letters or manuscript-line boundaries enter the count.

| Block in this input | Expanded letters | Letters per proposed page |
|---|---:|---:|
| 36:23 after κύριος through 36:38 | 1,589 | 1,589 for one page |
| All of chapter 37 | 3,143 | 1,571.5 for two pages |
| Chapter 37 with the proposed 54-letter tail removed | 3,089 | 1,544.5 for two pages |
| Chapters 38–39 | 5,945 | 1,486.25 for four pages |

The untrimmed block ratio is approximately 1:1.98:3.74, not exactly 1:2:4.
These sizes are broadly compatible with flexible page capacities, with or
without the proposed chapter-37 deletion. They neither reproduce Spottorno's
Ziegler/B/967 counts nor falsify them: the text base and abbreviation conventions
differ. A model fitted using flexible dimensions and textual choices requires
independent physical or genealogical evidence before it can distinguish loss
from a shorter literary form. These numbers are not a probability of loss.

The following reproduces the count from the separately cached input; it makes
no network request and deliberately does not import the third-party text into Git.
Its public pinned source and acquisition hash are recorded in the linked input
section. Set `p` to that downloaded file when reproducing on another machine.

```python
from pathlib import Path
import hashlib, json, unicodedata
p = Path('/tmp/ezekiel-ruah-control-vpePQq/ezekiel.json')
assert hashlib.sha256(p.read_bytes()).hexdigest() == '06f1b82b9c95fc5c2c1735c928cdb44299fea2f8d9b9fc68eda0e14118920a1f'
rows = json.loads(p.read_text())
g = {r['ref']: ' '.join(w['surface'] for w in r['words']) for r in rows}
assert len(rows) == len(g) == 1267
def count(text):
    return sum(c.isalpha() for c in unicodedata.normalize('NFD', text))
def chapter(c, last):
    return sum(count(g[f'Ezek {c}:{v}']) for v in range(1, last + 1))
assert g['Ezek 36:23'].count('κύριος') == 1
a = count(g['Ezek 36:23'].split('κύριος', 1)[1])
a += sum(count(g[f'Ezek 36:{v}']) for v in range(24, 39))
tail = count('ο αγιαζων αυτους εν τω ειναι τα αγια μου εν μεσω αυτων εις τον αιωνα')
b, c = chapter(37, 28), chapter(38, 23) + chapter(39, 29)
assert (a, b, tail, b-tail, c) == (1589, 3143, 54, 3089, 5945)
print(a, b, tail, b-tail, c)
```

Spottorno p.97 also allows the longer ending to have entered textual history
at some point before its subsequent loss. Literary expansion and later copying
loss are therefore not necessarily mutually exclusive events. The current
evidence still cannot select one historical sequence or justify deleting the
renewal promise from POB. The useful next evidence must constrain transmission
history, not improve the numerical fit through additional free adjustments.

### Target-apparatus access boundary

A parallel bounded access check found that the
[Göttingen publisher record](https://www.vr-elibrary.de/doi/book/10.13109/9783666534355)
marks the [text/apparatus pp.91–330](https://www.vr-elibrary.de/doi/10.13109/9783666534355.91)
and [supplement pp.331–355](https://www.vr-elibrary.de/doi/10.13109/9783666534355.331)
as requiring access; only preliminaries pp.1–6 are free. The
[HUB publisher preview](https://www.magnespress.co.il/api/magnes/book/5187/preview)
has 14 pages, with a sample of Ezekiel 1:1–7, not the target chapter-36 apparatus;
its full reader requests sign-in. The source agent checked the publisher pages
and preview, not the missing apparatus. No authentication, purchase or bypass
was attempted. Repeating these same public previews is not a research step.
Do not treat the introductory mention of 36:23–38 note 1 as consultation of
the note itself. Authorized target-page access remains a separate requirement.

One independent source/count check reproduced the 54-letter tail, all five
displayed block counts and the distinction between capacity and endpoint.
Root separately reproduced them. The Spottorno source hash remains the recorded
six-page input below. No new whole-volume reading, physical leaf reconstruction
or historical-priority approval follows from this sensitivity test.

The bounded final review passed the actual documented recipe and its stated
limits. Root also executed that recipe, verified 482 relative file-link targets,
unchanged private-source and protected Genizah hashes, and the three-document
change boundary. `git diff --check` passes. No corpus tests are newly claimed
for this documentation-only result; exact-head publication checks remain separate.

## Early quotation controls checked on October 15

**Result: selected renewal clauses circulated in early Latin Christianity;
this does not decide the original Hebrew form or attest the whole longer
passage.** A quotation must be mapped by its actual words, not expanded to
the coverage implied by an editor's modern verse reference.

### Cyprian: an explicit, connected quotation

Cyprian's Letter to Magnus, **Epistula 69.12** in Hartel's numbering,
explicitly introduces scripture speaking through Ezekiel the prophet. The
[original edition scan](https://archive.org/details/corpusscriptor203cypruoft),
*CSEL* 3.2 (1871), printed p.761 lines 12-15, then quotes sprinkling clean
water, cleansing from all impurities and idols, and giving a new heart and
spirit. Its conclusion is:

> et dabo uobis cor nouum, et spiritum nouum dabo in uobis.

That connected sequence identifies **36:25 and the first part of 36:26**,
more specifically than a heart/spirit allusion alone. The text immediately
switches to Numbers. It does **not** quote the removal of the stone heart,
the heart of flesh, verse 27, or the entire 36:23b-38 passage. The Ezekiel
chapter/verse numbers in the footnote are Hartel's editorial identification,
not Cyprian's own citation form. His context is baptism administered to sick
people by sprinkling/pouring, not a continuous copy of Ezekiel.

The printed main text reads **mundamini**; its apparatus gives
**mundabimini CPv**. Other variants and corrections also occur. In particular,
line 15 records correction of holy-spirit wording to new-spirit wording in C.
Do not silently normalize the main text or treat the critical edition as
unanimous manuscript testimony. Printed p.760's apparatus also records differing
letter divisions: the work/section reference here follows Hartel.

The [abstract of Shuve's dating study](https://academic.oup.com/jts/article-abstract/61/2/627/1699877)
reports the traditional 254 date and Burns's proposed placement after spring
256; Shuve defends the traditional date. Only the abstract was consulted,
not the full study. **Mid-third-century composition** is sufficient for this
control; it is not the date of the surviving manuscripts or of every variant
in Hartel's apparatus. No independent manuscript stemma or interpolation audit
of the letter has been performed here.

### Irenaeus: a shorter indirect reference

The earlier English lead, *Against Heresies* IV.33.14, is now checked in
[Harvey's 1857 edition, volume II](https://archive.org/details/sanctiirenaeili00irengoog),
printed pp.267-269. Harvey numbers the relevant paragraph IV.LV.5; the margin
on p.269 cross-references Massuet IV.XXXIII.14. The actual wording on p.268 is:

> et cor novum, et spiritum novum dare hominibus

This reports giving people a new heart and spirit in indirect speech. A
new-covenant/Horeb clause precedes it, and Isaiah's new-things/desert-water
imagery follows. There is no accompanying sprinkling/cleansing sequence,
stone/flesh-heart clause, or verse 27 quotation in this unit. Harvey's margin
identifies Ezekiel 36:26, but that label is not additional ancient wording.

The new-heart/new-spirit pair also occurs in 18:31; the divine-giving formulation
fits 36:26 more closely than 18:31's command to make them. The related divine
promise at 11:19 has one heart in the retained Hebrew and a new spirit. Root
checked all three complete Hebrew verses in the vendored XML. This is a
comparison with our retained Hebrew edition, not a reconstruction of Irenaeus's
Greek Bible or a collation of the ancient variants at 11:19.

Harvey prints the target in Latin without a corresponding Greek fragment.
Greek material in adjacent notes does not supply these words. Record **Greek
wording not verified**, not an exhaustive claim that no Greek survives
anywhere. The ancient work's composition date must not be substituted for
the date of its surviving Latin-version manuscript evidence. This is useful
reception evidence, less passage-specific than Cyprian's connected quotation;
it does not independently establish all of 36:23b-38.

### What this adds to the comparison

The previously checked Masada Hebrew witness already prevents treating the
renewal material as merely a late Christian invention. Cyprian adds a different
kind of evidence: an explicit Latin Christian use of the connected cleansing
and renewal clauses. It therefore prevents treating the shorter Old Latin
witness discussed below as the only early Latin reception of this material.
It does not establish that Cyprian's entire biblical exemplar had the present
longer ending, its exact Greek translation profile, or the same chapter order.
Nor is his quotation automatically genealogically independent of every Greek
ancestor shared with other witnesses.

For the immediate POB question, the current Hebrew and English at 36:25-26
already contain the quoted sequence. No amendment follows. Keep the longer
Hebrew text provisionally and historical priority on HOLD. This is a
published-source comparison, not recovered manuscript ink, a newly discovered
quotation, or evidence about adding another book to the canon. ImageGen has
no evidentiary role.

### Consultation and reproducibility

Root and the acquisition agent each visually read complete printed pp.760-762
(PDF pages 774-776), including the apparatus and quotation boundaries. Neither
claims a whole-volume reading. The privately retained 862-page PDF has SHA256
`28135c86a97c5946c522940cb0aabe5b236477fb6769cc63127e5a0cfcae8ea0`.
The [pinned Leipzig transcription](https://raw.githubusercontent.com/OpenGreekAndLatin/csel-dev/6ad1353efaaea568024565a82cd13a253f0e53e0/data/stoa0104a/stoa012/stoa0104a.stoa012.opp-lat1.xml)
was a navigation/control source, not a substitute for the printed page. Its
header credits Hartel's edition, University of Leipzig (2014), and CC BY-SA
4.0; SHA256
`3ebc01f65faf2b8373310ddf843b4f645835fcabbe06ae81eb8d1d15ed982357`.
No full edition, transcription or page image is imported into Git.

For Irenaeus, root and the same source agent each visually read complete
printed pp.267-269 (PDF pages 278-280), including margins and notes. The
582-page Michigan/Google/Internet Archive PDF has SHA256
`ede42f3fa6757bc7a51b5fbaec7dcd22493987ce820a607e7b3935b7cdbde10f`.
This is not a full-volume reading or a newly verified Greek quotation.
The WLC input hash remains the one recorded above. The two early references
have now been checked; repeated citation of them is not a next research task.
Reopen their textual-history implications only with a discriminating source,
such as an actual earlier Greek quotation with relevant wording or the target
modern critical apparatus. Do not grow an undirected patristic census merely
to accumulate agreement.

## What changes in the source judgment

Neither an older long-form copy nor a long minus decides literary precedence.
A loss theory must explain order and omission together, while an expansion
theory must establish direction rather than merely identify lexical difference.
The53-letter assumption is a concrete weakness in one loss model, not a
refutation of every possible loss mechanism. Likewise, the Old Latin claim must
be checked against its actual preserved leaves, reconstruction and Greek ancestry;
do not count a reported reconstructed minus as a second direct Hebrew witness.

Spottorno93 distinguishes the Princeton1938 evidence from the Madrid publication
confirming the gap. Her note2 identifies Fernández-Galiano, *Studia Papyrologica*
10(1971),7–64, P.Matr.bibl.1, with reported coverage28:19–43:9, although her body
says publication1972. Preserve that bibliographic discrepancy. Extend the prior
[Princeton-only next action](PAPYRUS_967_IDENTITY_AND_EDITION_2026-10-12.md#literary-form-and-the-next-consequential-comparison)
to this exact Madrid edition; target leaf/page mapping remains unverified.

Next test clean Hebrew/Greek vocabulary against controls, inspect the original
Latin transition/reconstruction, and acquire the exact Madrid/Princeton target
edition pages. Physical continuity would exclude a present-day lacuna, not loss
in an ancestor. Stop repeated access searches without a new route. The earlier
[Mas1d result](EZEKIEL_36_LONGER_FORM_EVIDENCE_2026-10-12.md) remains direct
published longer-form Hebrew support, not a priority vote.

## Source controls and verification

Baseline is bd506434018a2f72989556c756f6c72d5948eeed. Previous receipts and the
16 current36:23–38 source/English files remain unchanged. No new parser, registry
row, bespoke validator or application is needed for this argument comparison.
The PDF skill required visual reading because text extraction contains only
rights overlays; the documentation skill keeps source arguments distinct from
our inference and historical receipts.

Publisher PDF:1155022 bytes, six pages, unencrypted, SHA256
3b19f849657af6bd5f15a6d1b9b82f1d73954b913cd8bba261736512b7308729.
Private path:/private/tmp/pob-ezekiel-omission.KtT7de/spottorno-1982.pdf.
All six120-dpi renders were read, not newly restored manuscript pixels:

|PDF page|SHA256 of spottorno-page-N.png|
|---|---|
|1|264c30f6ffb8fd450637bd50b2255a8f4bf352abcbfa29eea5deec52a83bdae3|
|2|d115887599fc3ce6ec68510d70487d33f1612deec5d617ce434ecf1e86016102|
|3|4a43561e1ead630cc127259291d2d64c2c6f69d11e2592a75b97c9f7716399f4|
|4|b81cc00e085cec6645c57b7575d8416dd52a34d86604bfcc4b8a543214e1b4f4|
|5|1fa774e7e2deda626011cfa2ef1a1b7d9463c19779a164d6c48afc845d158689|
|6|146d72d35508ab57ddaa61696722fa2bdad4488d1cdd88c4af91eca146356ea2|

The publisher supplies a CC BY-NC3.0 Spain notice; ResearchGate's differing
license label is not used to expand rights. Raw PDF/renders stay outside Git.
Tov is read through public author-uploaded HTML, not a downloaded PDF; no
invented download hash, full1986-reading claim or license expansion is made.
Publisher/JSTOR routes that do not expose article bodies are not full readings.
The initially attempted pdftotext path and BeautifulSoup imports were unavailable;
standard-library parsing and bundled pypdf located sources, and actual renders
supplied the Spottorno reading. No unsuccessful extraction is credited as evidence.

One bounded comparison critique passes the report at SHA256
e09b3d66538d475f31aa814640ec1cb68d7011572831c65398a4ce0de7c21f3f,
independently reading the full Tov HTML and all six Spottorno pages/notes and
verifying seven private hashes plus20 retained pins. Root verifies local file
links, arithmetic, whitespace and the unchanged protected Genizah hash. This
paragraph appends verification, not changed argument or source evidence.
No new corpus tests are needed or claimed for the two-path documentation scope;
own exact-head publication checks remain required. No exhaustive witness,
historical-priority or optimum-English approval is implied.

## Old Latin preservation and original edition check

The Old Latin evidence is now more specific: Ranke's diplomatic edition
positively reports a37:28→40:1 transition within one transcribed column. It does
not directly attest the36 minus or establish the complete P967 chapter order.
This strengthens the edition-level basis for one ordering difference, without
settling Hebrew literary priority or changing POB's source or English.

The [Würzburg custodial record](https://www.franconica.online/o/s/en/item/68684)
identifies M.p.th.f.64a. Its linked Thurn catalogue,1984, printed48–49, lists
Ezekiel24:4–21;26:10–27:4;34:16–35:5;37:19–28;40:3–42:18;38:8–20;
45:1–46:9;48:28–35. Neither36 nor39 appears in that survival list. Listing37
before40 alone would not demonstrate a preserved transition.

The [original Ranke edition,107–108](https://books.google.com/books?id=9bNCAQAAMAAJ&pg=PA108)
supplies stronger evidence. Printed107 labels37:19–23 and23–28. Printed108A
continues37:28 and then the dated opening of40; its footer explicitly labels
“XXXVII,28; XL,1–3.” The opening is in the same full-size uncial transcription,
not merely a parallel modern text. Ranke's [preface,§5, xiii–xiv](https://books.google.com/books?id=9bNCAQAAMAAJ&pg=PR13)
explains that conjectures in this first part use smaller characters; conjectures
in the later comparison use oblique type. Accordingly, Thurn's starting label
40:3 must not truncate the positive40:1–2 evidence in this edition.

Ranke's [diplomatic commentary,155](https://books.google.com/books?id=9bNCAQAAMAAJ&pg=PA155),
note108A5, attributes an omission and later compensation to the scribe. The
note actually prints “XXXVII. et XXXVIII.”, inconsistent with the37→40 boundary;
preserve that numbering inconsistency rather than silently substituting38–39.
The preceding107–108 discussion explains that Ranke initially suspected a
different scribe because of the longer lines, but abandoned that opinion after
comparison with other pages. These are his published assessments, not a new
hand attribution or proof of the history that produced the arrangement.

The consequence is to separate three claims: a directly checked diplomatic
37→40 transition; a36 minus requiring reconstruction; and a complete order or
genealogy requiring additional argument. No36 words in a fragmentary survival
list is not evidence that the intact manuscript lacked36. Nor is Latin a second
direct Hebrew witness. Shared Greek ancestry, Greek-stage rearrangement and
local Latin copying remain alternatives. The exact relationship to P967 and
the reconstruction's capacity constraints remain open.

Thurn points to Bogaert's1978 *Biblica*59,384–395 study. Its identity is confirmed
by the [author's institutional bibliography,1978b](https://www.maredsous.com/the-research/pierre-maurice-bogaert/?lang=en)
and [JSTOR42706730](https://www.jstor.org/stable/42706730), but its body remains
unacquired. Those records cannot supply his leaf arithmetic or ancestry argument.
Reopen for that actual argument or the original P967 transition; do not repeat
the gated download searches without a new route. Historical priority stays HOLD.

### Consultation and preservation record

Root and a read-only independent checker inspected the printed target pages,
notation and commentary through the public Google Books reader, copy9bNCAQAAMAAJ.
Root read the complete accessible preface batchx–xiv and visually checked its
notation passage, complete107–108 and155. Accessible OCR loses column blocks;
the printed images, not that loss, support the transition. This is a bounded
original-edition reading, not a full432-page reading or fresh palimpsest collation.
The rotated marginal numerals are not assigned to manuscript folios here.
No Ranke PDF was acquired: the different UC copy's ordinary download returned429;
the earlier Leuven copy's403 remains a separate failed acquisition.

The complete Thurn48–49 scans and their custodial sources remain outside Git in
/private/tmp/pob-old-latin-ranke.jYqYD2/. Root verified their four SHA256 values:

|Input|SHA256|
|---|---|
|thurn-1984-p48.jpg|90b9553fec08576c70aaebeff01dd9c95c101b2479802f3f544e0e17e8264242|
|thurn-1984-p49.jpg|35e635f55cd7d20d7542d9f110f3b4942adb0dae6bbe200b21c03254ad0ac947|
|thurn-manifest.json|a7106d0a5da2007e2084bb217c067ed9ceb29870aea2e5052700034bec7ca49a|
|custodial-description.html|ed4702f9f48c8338cc9442f7946cec1dc78121eb45f5012013ef254556e0e5a8|

The [institutional catalogue manifest](https://iiif.ub.uni-leipzig.de/0000034864/manifest.json)
states CC BY-SA4.0 attribution to Otto Harrassowitz. No raw image or article is
relicensed as POB text. No download hash is invented for browser-only Ranke pages.

One bounded independent source critique passes this append at full-report SHA256
8b3982cbdb312a9829c8b9ce754c1f3178d93874e0a67775b70aca9602efcdfe,
checking the original target images and notation, four private Thurn hashes,
20 retained repository inputs and the protected Genizah hash. Root independently
verifies those inputs and clean whitespace. No new corpus-test claim is needed
for this two-document append; its own exact-head publication checks are separate.

## Contemporary omission criticism and Latin ordering limits

Irwin's1943 *The Problem of Ezekiel*, complete printed62–65, supplies a
contemporary argument against simple eye-skip. On62 note3 he estimates the
missing passage as roughly1¾ pages of967 using Swete. This is Irwin's estimate,
not a newly verified Filson calculation or a measurement of the lost exemplar.
His claim that no comparable omission was known, including his report of a
conversation with Filson, is an attributed historical assessment, not a measured
error probability. Its force depends partly on an exemplar resembling967;
Spottorno's different hypothetical format is not excluded by that condition.

The same note continues on63 and reports36:23a immediately followed by38:1.
Preserve his clause label rather than harmonizing it silently with later b/c
labels. This is original scholarly testimony, not inspection of the Greek
transition's letters or supply brackets. Irwin treats the endpoint as natural
and combines the minus with distinctive Greek to infer a late Hebrew addition.
Our conclusion is narrower: Greek distinctiveness does not uniquely distinguish
Hebrew expansion from Greek revision or ancestral loss. His63–65 dating and
canon-closure inferences depend on that unresolved step and are not adopted.
The [surviving Masada longer-form words](EZEKIEL_36_LONGER_FORM_EVIDENCE_2026-10-12.md#surviving-hebrew-and-supplies)
remain the direct Hebrew control; literary priority stays HOLD.

The [Ranke118–119 print sequence](https://books.google.com/books?id=9bNCAQAAMAAJ&pg=PA119)
also limits an easy equation of the witnesses. Printed118 labels42:11–14 and
14–18;119 labels38:8–11 and12–14, explicitly referring back to108A5. These
separate printed pages are not a same-column42→38 transition or a verified
original folio map. They confirm the edition's later compensation discussion,
not the full P96736→38→39→37 arrangement. Common ancestry and local Latin
rearrangement still require discrimination. No source, English, note or canon
change follows.

### Sources and bounded consultation

[UChicago's institutional edition](https://isac.uchicago.edu/publications/problem-ezekiel-inductive-study)
identifies Irwin's1943 book and [public PDF](https://isac.uchicago.edu/sites/default/files/uploads/shared/docs/problem_ezekiel.pdf).
Root read all four target pages and notes in text and images, not the entire
364-page file. The institutional page declares CC BY-NC-ND4.0; private PDF and
renders are not imported or relicensed as POB text. Directory:
/tmp/filson-primary-z4YoYy/.

|Input|SHA256|
|---|---|
|irwin1943.pdf|5d32edf713d745bdf9c1b7dd6bfc05c18d953b3eb2b27fea50e6613e3f5f872d|
|irwin-082.png printed62|b421fab54f46e0cf62b153910586282d60f021d5ec0e9a6a196a72674177acad|
|irwin-083.png printed63|a2f88c15d6e05506520e7b20ed496f28b18f0489127589ec3c3d47458b1192a8|
|irwin-084.png printed64|2f2430cbf4b711044ebb7825b5b26e95495c21cee27ed375b5a02e6c898d25a5|
|irwin-085.png printed65|c5c9a79d5e01d5e27164e58dab4ddebe42cea0ababebab1a4c029a92af78f3cb|

Filson's own six-page JBL62(1943),27–32 article, DOI10.2307/3262380,
remains unacquired. The [original JSTOR record](https://www.jstor.org/stable/3262380)
returned a client challenge, the publisher's issue returned403, and the checked
bibliography supplied no body. Irwin's account cannot substitute for reading
Filson's argument. These distinct routes stop here unless new access appears.
Ranke118–119 were visually read through the same public copy as the preceding
check; browser-only images receive no invented file hash or fresh-ink claim.

One bounded independent critique passes this follow-up at full-report SHA256
d51565149cb1cd2083d8ef8ba01696574ea2909b25834dd7e8bd0bf25c55ea9a,
reading all four Irwin pages/notes and the Ranke labels/reference. Five private
hashes,20 retained inputs and protected Genizah bytes match. Root reproduces
those checks, resolves363 local documentation links and verifies whitespace.
This validation append changes no argument; no corpus rerun or historical
priority/application approval is claimed. PR170's frozen head is unchanged;
these successor edits still require their own commit and publication checks.

## Same codex omission control

Papyrus967's12:26–28 minus is positively attested within a surviving column,
not inferred from a present physical gap. Kenyon1937, complete printed2–3/PDF20–21,
continues fol.11v from12:23 through13:6. At12:25→13:1 it prints unbracketed,
undotted `λογον και ποιησω λεγει κ̅ς̅` followed by
`Και εγενετο λογος κ̅υ̅ προς με`. The apparatus explicitly reports26–28 omitted,
but qualifies the proposed cause: “per homoioteleuton ?” retains a question mark.
The endpoint is a declaration formula, not the recognition formula invoked
in the36 discussion. Do not use the shorter minus as a proven instance of the
same recognition-formula copying mechanism.

Kenyon1938, plate PDF15, labeled f.11.v. and captioned12:23–13:6, reproduces
the same column's continuous join. Root inspected the complete plate for
layout, using the published text for endpoint words; no fresh glyph recovery
or calibrated transcription is claimed. The text edition marks a different
gap after13:6 before the13:11 material on fol.11r. These two kinds of absence
must remain distinct. No original codex-page numeral was read at the target;
fol.11v is the observed publication locator.

This is a positive control for attested omission versus physical loss, not
for its historical cause. A continuous ancient copy can inherit an ancestral
loss, a different literary form or versional revision. The same-codex link
does not establish that12 and36 underwent the same process, and these two
publications do not count as two witnesses. The chapter36 Greek transition,
its exact clause endpoints and the versional relationships remain the
discriminating targets. Source/English selection and historical priority remain
unchanged; ImageGen supplies no evidence.

### Control inputs and consultation

The source PDFs are the existing [1937 text](https://chesterbeatty.ie/assets/uploads/2018/11/The-Chester-Beatty-Biblical-Papyti-Descriptions-and-Texts-of-Twelve-Manuscripts-on-Payprus-of-the-Greek-Bible.pdf)
and [1938 plates](https://chesterbeatty.ie/assets/uploads/2018/11/The-Chester-Beatty-Biblical-Papyri-Descriptions-and-Texts-of-Twelve-Manuscripts-on-Papyrus-of-The-Greek-Bible-Fasciculus-VII.pdf),
not new whole-book acquisitions. Root and a source agent visually read the
two complete text pages with apparatus and the complete plate. The actual
printed brackets and dots are reported without inventing a comprehensive
editorial-sign legend. Source PDFs/renders stay outside Git; access is not
permission to redistribute images. Private inputs under /private/tmp/:

|Input|SHA256|
|---|---|
|pob-ra967-kenyon-vii-text.pdf|06d31bd662d388df0cc07c8f3dea6da562951c2c5b11ebd83ea46fa76791b233|
|pob-ra967-kenyon-vii.pdf|8efe4b11bbeb3b32ae556946e98daf956c14754f8ae1fff4fa15ac4b56feb4d7|
|pob-ra967-ezek12-control-text-20.png 150dpi|0dec6664ea1b8c7885a824e7a808d664bc03a20bde7d3d85b7842579903cb5b5|
|pob-ra967-ezek12-control-text-21.png 150dpi|7925fda4264a8aa99a4eba4947312c690d6c7c93fe2a9d4995dd7dda740275e3|
|pob-ra967-ezek12-control-plate-15.png 200dpi|c0b5cfda7ff4463a1997830ea0a78eaf8c8a26ef574097612bc95285ec1d4fc1|

One independent critique passes this new control at full-report SHA256
210f1c00c01dadec1d4e7bbcccb7386b4274e4092c9eb5097d04d598713dd9d2,
reading both complete text pages and the whole plate, with five private hashes,
20 retained inputs and protected Genizah bytes verified. Root reproduces those
checks, resolves364 local links and checks whitespace. This is not a repeat
of the earlier Irwin/Latin judgments; no causal or source-priority approval
or new corpus-suite claim is implied. The successor requires its own exact-head
publication checks.

## Chapter order and resurrection interpretations

The [KU Leuven introduction](https://theo.kuleuven.be/uploads/file/ezekiel/Septuagint_Ezekiel_Intro.pdf)
provides a directly accessible later argument, not the still-unacquired Lust
1981 article or Schwagmeier dissertation. PDF metadata names Johan Lust and
dates creation December 10, 2008; the pages display 10-12-2008. No final
publication venue is assigned to this institutional file.

On pages 11–15 Lust contrasts Schwagmeier's physical-resurrection reading of
MT with Crane's corresponding reading of the Greek order. He rejects the
necessity of either inference. Pages 19–20 nevertheless favor development of
the longer form from the shorter. These are distinct judgments: his objection
to the resurrection arguments is not a reversal of his textual-history view.
Schwagmeier's argument remains mediated. Crane's relevant original discussion
was subsequently acquired and checked directly, as follows.

The [Murdoch repository](https://researchportal.murdoch.edu.au/esploro/outputs/doctoral/The-restoration-of-Israel-Ezekiel-36-39/991005542291607891)
supplies Crane's 2006 thesis. Printed 307, including note 480, explicitly allows
metaphorical regathering in P967's order and acknowledges uncertainty about
early interpretation, while preferring a physical reading. Printed 310 uses
stronger necessity language; 311 again permits overlapping interpretations and
concedes that Israel's participation in the Gog battle is not explicit. Thus
Lust's objection addresses a real claim, but an exclusive physical-versus-
metaphorical binary would misrepresent Crane's own qualifications. His section
7.5 begins on 306 with P967's Hebrew priority as a premise established by his
preceding argument, not as something this interpretive section independently
demonstrates. That preceding argument still requires direct assessment.

Our bounded check of the current WLC-based records and the previously pinned
[Greek surface-text control](EZEKIEL_36_LANGUAGE_CONTROLS_2026-10-12.md#hebrew-spirit-and-wind-translation-pattern-on-october-14)
finds that 39:11 names Gog and his multitude as the buried group; 39:12 makes
Israel the burial agent. Both forms of 37:11 identify the bones with Israel.
Consequently, simply placing 37 after 39 does not explicitly identify its
bones as Israelite battle casualties. That identification needs an additional
interpretive argument. This does not prove that no Israelites died, disprove
physical resurrection, or decide every meaning of the vision. The selected
Greek control is not a new collation of P967.

There is also a citation slip in the PDF's page 12: its shepherd-appointment
discussion prints 37:23. The wording occurs at 34:23 in the checked Hebrew and
Greek controls; 37:23 instead concerns cleansing and the people/God relation.
Preserve the printed reference when describing the source, but use 34:23 for
the actual comparison. This is a reference correction, not a manuscript variant.

The project-level consequence is to keep three decisions separate: the attested
order, the historical direction of change, and the interpretation within each
form. A theological consequence cannot be used to select a source order and
then be presented as independently proven by that selection. POB's source,
English and notes remain unchanged; earliest-form priority stays HOLD. The
physical transition and independently supported direction of revision remain
the discriminating evidence, not another preference vote about chapter order.

### Consultation record for October 14

Root read the complete 20-page text, including all 56 notes, and visually
checked complete pages 12–15. The original failed pdftotext command added no
evidence; web extraction supplied the text and rendered pages supplied the
layout/reference checks. PDF: 151663 bytes, SHA256
`6adf59ae9b6e82be288d98c74b4226f4dc6a9bdb23746da1fc46ac514edd5742`,
private path `/tmp/ezekiel-lust-intro-sqkpw4/intro.pdf`. No PDF or render is
imported into Git or relicensed. The five bounded control loci are 34:23,
37:11, 37:23 and 39:11–12; only ordered Greek surface strings were used, not
generated morphology. No new image restoration or whole-corpus audit follows.

Crane's PDF was downloaded through the institutional record's ordinary whole-
thesis link after web-fetch timed out. It has 368 pages and 1476400 bytes,
SHA256 `d8946b57d346bdd2bf8764659b8eb8444c48732e44ff3e8fbb8a24f3f8f17842`,
private path `/tmp/ezekiel-lust-intro-sqkpw4/crane2006.pdf`. The title page says
2006; PDF creation metadata says 2007. Root read printed 305–315 with notes
and visually checked complete 307/PDF310 and 311/PDF314, not the entire thesis
or its full historical-priority argument. The original flags permit printing
but disable copying; no permissions were altered and the PDF was not modified
or redistributed.
The following assessment addresses chapter 7's actual omission/order argument,
printed 254–270, rather than another secondhand interpretation.

## Crane on copying loss and the Latin witness

Crane's original argument does not eliminate ancestral copying loss. This
assessment concerns printed 254–270 of the same thesis, not the later linguistic,
liturgical and reception arguments or the whole case for Hebrew priority.
The substantial expansion hypothesis remains live; POB's source and English
remain unchanged.

On 265–266 Crane objects that Spottorno's accident proposal does not account
for the Latin witness. His note 413 explicitly says her work was unavailable
to him. Spottorno's actual 94–95 discusses that witness, distinguishing the
preserved 37-before-40 order from the reconstructed 36 minus and wider layout.
Thus Crane's objection cannot serve as a direct assessment of her complete
proposal. This does not establish that her hypothetical page arrangement is
correct: its capacity assumptions and the extra 53-letter assumption in one
model remain qualified in the earlier comparison.

Crane 255 acknowledges related ancestry for the Greek and Latin traditions,
while 265 uses the separate Latin witness against accidental loss. Our inference
is that independence from the extant P967 copy is not independence from every
earlier Greek ancestor. If an accident preceded the split, two descendants
would not require two identical accidents. Nor does a reconstructed Latin
minus carry the same weight as preserved words at an actual boundary. The
[Ranke check above](#old-latin-preservation-and-original-edition-check) supplies
positive evidence for 37→40, not the complete P967 arrangement. This is a
limit on the exclusion argument, not proof of common ancestry or of an accident.

On 259 and note 404, Crane's expectation that a scribe would notice and repair
the absent passage explicitly assumes familiarity with it. That is not measured
evidence of this scribe's knowledge. On 261 and 264, page-capacity objections
also depend on an exemplar's format. An estimate based on surviving P967 pages
cannot by itself exclude an earlier exemplar with different dimensions, lines
or columns. None of this makes any particular alternative format probable;
the original ancestor remains unobserved.

The useful constraint is still to explain omission and order together, while
testing proposed causes at the appropriate transmission stage. A careful scribe
can accurately copy an already shortened or rearranged exemplar. Literary
coherence makes a form interpretable; it does not alone establish its priority.
Consequently, these pages do not justify removing 36:23c–38, reordering the
book, or retroverting a new Hebrew source corpus. The next substantive input
is the remaining linguistic argument at 270–277, compared with the already
completed language controls, or the missing original Greek transition.

### Bounded source checks

Root read complete printed 254–270 and their notes; visually checked complete
255/PDF258, 259/PDF262 and 264–266/PDF267–269. Spottorno 94–95 were rechecked
in the original page images against their earlier recorded hashes. No full
thesis reading, new Filson or Lust 1981 consultation, ancestor reconstruction,
or new P967 photograph is claimed. Crane's 266 note 415 reports a small space
at the 39→37 transition through Johnson; that remains a reported feature,
not an independently measured gap or proof of scribal intention.

## October 16: Greek replacement is not Hebrew composition

The previously queued linguistic discussion in
[Crane's 2006 thesis](https://researchportal.murdoch.edu.au/esploro/outputs/doctoral/The-restoration-of-Israel-Ezekiel-36-39/991005542291607891),
printed 270–278, is now directly checked against the completed language controls.
**The evidence supports distinguishing a Greek translation layer; it does not
by itself exclude replacement of an older Greek translation of an already
existing Hebrew passage.** Retain historical-priority HOLD and current POB.

Crane 270–273 assembles Greek vocabulary and Hebrew stylistic differences.
On 274 he expressly recognizes the need to distinguish original absence from
replacement following omission. Pages 274–276 add junction wording, reported
cross-language agreement, sense divisions, the human-bones clarification at
37:1, and chapter-order/theological coherence. Page 276 proposes coordinated
inclusion. Pages 277–278 discuss Thackeray's alternative of a Christian lesson
replacing an older Greek translation, then object that Christian material
would not plausibly have entered Jewish Hebrew. These are cumulative arguments,
not a claim that style alone proves the entire history.

Our inference concerns that last objection specifically. A Greek-only
replacement model requires no Christian creation of Hebrew and no transfer
from a Christian lesson into a Jewish Hebrew copy. It allows the Hebrew
passage to predate the Greek revision. Therefore the objection on 278 does
not exclude that model. This is a limitation of an exclusion argument, not
evidence that Christian replacement actually happened. The earlier
[Thackeray control](#greek-translation-technique-controls-checked-on-october-15)
already records the distinction; Crane's treatment can now be evaluated
directly rather than inferred through his citations.

Keep three separate historical questions:

| Question | Relevant evidence | What remains unproved |
|---|---|---|
| Why does the surviving longer Greek have a distinctive style? | The controlled vocabulary/title distributions and possible revision affinities | First translation of newly composed Hebrew versus replacement/revision of an existing translation |
| Why does P967's branch lack the passage? | Actual continuous transition, longer Hebrew attestation, qualified Latin evidence and loss models | Ancestral absence, secondary loss or deliberate omission |
| Why do the chapter orders differ? | Observed joins, literary connections and junction variants | Direction, motive and whether this change occurred together with either event above |

The strongest counterargument to separating these events is explanatory
economy: a single compositional revision may account for several correlated
features. A replacement proposal must still explain the shorter branch,
chapter order, Hebrew literary profile and lack of a securely identified older
Greek translation of the passage; it cannot answer everything merely
by being possible. Conversely, a coherent combined narrative does not prove
that all the features arose together. Reported close Hebrew/Greek agreement
can also fit a later translator revising toward an existing Hebrew text.
No variation-rate measurement or synchronism is established in this pass.
The actual Christian lesson cited at 277 note 433 is medieval and covers only
36:24–28. It does not directly attest ancient replacement of the full block.

The [existing controls](EZEKIEL_36_LANGUAGE_CONTROLS_2026-10-12.md) retain their
witness-specific qualifications; neither Crane's repeated examples nor his
cited scholars become additional manuscripts. This closes the old instruction
to read 270–278. The useful next evidence would distinguish translation revision
from first translation, or independently establish the relationship of the
short and long branches. Do not repeat these pages as a new source-priority vote.
No source, English, note, restored letter or canon change follows.

Root and a bounded independent critic read all nine complete pages with notes;
root visually inspected PDF pages 273–281. The critic confirmed the logical
distinction and required retaining the cumulative counterargument. The PDF
hash remains `d8946b57d346bdd2bf8764659b8eb8444c48732e44ff3e8fbb8a24f3f8f17842`.
This is not a complete-thesis review, a new consultation of Thackeray 1921,
or fresh verification of every manuscript claim in Crane. No PDF/renders are
imported into Git. An accessible Klein 2010 article was screened as a related
literary argument, but is not used here as an independently adjudicated witness
or a claim of newly established borrowing direction.

## October 16: Lilly on literary edition and resurrection reception

**Retain Hebrew-priority HOLD and current POB.** Ingrid Esther Lilly's 2010
Emory dissertation, [*Papyrus 967: A Variant Literary Edition of Ezekiel*](https://etd.library.emory.edu/concern/etds/th83kz55d),
is now accessible through its institutional download. This closes a new
consultation gap, not a new manuscript discovery. The important addition is
her distinction between literary possibilities, actual reader reception and
the history that produced the text. Her positive argument for an earlier
Hebrew edition must not be omitted merely because this project retains HOLD.

### Greek layer, Hebrew composition and selected evidence

Section 4.4.4, printed 143–150 / PDF 155–162, argues cumulatively against
mechanical omission and for a shorter Hebrew form. It combines Greek diction,
Hebrew linguistic features, prophetic formulas, literary reuse and versional
evidence. At printed 150 she expressly distinguishes the Greek insertion
argument from the additional, circumstantial evidence for absence in Hebrew.
A distinctive Greek rendering alone cannot decide whether its Hebrew passage
was newly composed or already existed before Greek supplementation/replacement.

Her conclusion at printed 150–155 / PDF 162–167 is not a random sample of
Ezekiel variants. It concerns variants selected for coherent literary trends,
with historical conclusions contingent on the literary analysis. Counting the
same readings, their coherence and the manuscript's aggregate reliability as
three independent votes would overstate the evidence. Printed 152–153 also
explicitly allows that an Old Greek text-type can reflect Hebrew yet undergo
Greek literary development. She judges that explanation less likely for
Ezekiel; she does not make it logically impossible.

The earlier project controls qualify several of her supporting claims:

- Printed 145–146 uses Erman's Sahidic unit to rebut the claim that 36:16–23b
  is too short to stand alone. Our [direct reading-boundary check](#sahidic-reading-boundary-and-the-shorter-text-argument)
  establishes an excerpt with a differing endpoint, not an independently
  surviving continuous Ezekiel edition without the longer passage.
- Printed 149 acknowledges that the Latin minus is inferred from non-extant
  material. Our [original-edition check](#old-latin-preservation-and-original-edition-check)
  retains the actual 37→40 join separately from the reconstructed wider order.
- Printed 144–145 challenges a particular loss reconstruction and its phrase
  correspondence. Our [capacity test](#testing-the-page-capacity-argument-on-october-15)
  likewise leaves ancestral loss possible without establishing that it occurred.

These are qualifications of the cumulative case, not grounds to discard it.
This pass does not independently verify every cited linguistic classification,
all chapter-5 comparisons, or a modern critical apparatus. No new probability
is assigned from her selected-variant counts.

### The resurrection margin and its interpretive limit

Printed 300–303 / PDF 312–315 describes the marginal hands. The published
page-90 reading is `αναστασεως`, translated as concerning resurrection;
“concerning” is supplied in interpreting the genitive, not a separately
transcribed `περι` on this page. Her `Q` for page 90 represents the numerical
koppa (note 640), not Codex Marchalianus. The note is contemporary with or
later than the main text in her account; this pass does not independently date
or identify its hand.

Section 6.3.3.1.4, printed 330–332 / PDF 342–344, places the note over the
page containing 39:23–29 and 37:1–4. She probably relates it to chapter 37;
the proposed liturgical function is also qualified. It supports resurrection
reception, but she says the marginalia do not establish special interpretive
importance for the chapter order or a definite Gog–resurrection connection.

The final synthesis, section 7.1.3, printed 374–379 / PDF 386–391, is essential
context. Lilly positively argues that placing chapter 37 before the temple
vision more readily permits an eschatological reading. The margin attests
compatible reception. She then considers, but rejects as insufficient, the
inference that resurrection-minded Greek editors created that order. Other
reader interests do not consistently match the distinctive textual features;
some align with MT's emphases. Her final methodological limit applies to this
text/paratext comparison, not to her entire dissertation: it supports
interpretive history rather than a text-critical conclusion.

Our assessment preserves both sides. A sequence can facilitate an interpretation
without that interpretation having caused the sequence. Conversely, the lack
of a wider editing pattern does not exclude a localized rearrangement, and
later annotators need not share an earlier editor's agenda. Neither the margin
nor its fit with the literary form establishes Hebrew ancestry or eliminates
Greek-stage development. The note and the chapter joins belong to the same
manuscript, not independent source-priority votes. No new canon inference follows.

### Photograph, consultation and next test

Root checked the previously acquired full Princeton canvas 42 and a native
upper-margin region from its [institutional image service](https://iiif-cloud.princeton.edu/iiif/2/71%2F07%2Fa3%2F7107a3a893d94b959f1cd195019f980f%2Fintermediate_file/1700,650,2100,700/full/0/default.jpg).
The cursive annotation and page numeral are visible in the expected location.
The photograph is compatible with the published reading; this is not a blind
letter-by-letter decipherment or an independent certification of every cursive
stroke. The transcription remains credited to Lilly and the earlier editors
she cites. The region uses native coordinates x=1700, y=650, w=2100, h=700 on
the manifest's 6679×11011 image. No generated fill or enhanced ink was used.

Root read complete printed 143–155, 300–303, 330–332 and 373–379 with notes.
The PDF skill prompted visual checking of complete 144–150, 330–332, 375–376
and 378–379, avoiding the extraction's corrupted Greek font mapping. This is
not a complete reading of the 443-page dissertation. One bounded independent
critic checked the same principal sections and the final synthesis, confirming
the distinction while requiring the positive literary argument remain visible.
That critique is not a new scholarly witness or proof of source priority.

The [institutional PDF download](https://etd.library.emory.edu/downloads/79407x487?locale=en)
was obtained through the ordinary public browser after web-fetch returned 405.
The 2,899,291-byte PDF remains private at
`/Users/zack/Downloads/Lilly_-_Dissertation.pdf`, SHA256
`b3c1d04d137a3195a584d26a5976e320b014a51ae93896afe347efbd697749a5`.
The new native image region, retained outside Git, has SHA256
`c93b64d9ebad1d8d7d4904a7a3fb9edd3b1d31e392c9bf43150e84a1b54d5d21`;
the reused full canvas has SHA256
`59e37e807a9903a0cfdee68b079abdb8e257f1268e5eaf02e18ca2b8922a2457`.
No dissertation, page render or manuscript photograph is imported or relicensed.

This retires another review of this margin as a source-priority test. An
accessible next substantive test is Lilly's chapter-5 heart/spirit comparison:
inspect the exact readings and contrary cases before assessing whether they
link the chapter-36 minus to a coherent Hebrew revision. The conclusion's
reported coherence is not itself a completed collation. Any such test must
preserve witness dependencies and distinguish a thematic relationship from
the direction or date of change. The missing modern apparatus remains a
separate limitation. No Hebrew, English, reader note or recovered letter changes.

## October 16: heart-spirit control and the circumcision counterexample

**The pending thematic test is complete at this bounded scope: no coherent
book-wide heart/spirit revision is established, and the photographs contradict
extending the flesh omission from 44:7 to 44:9.** Retain the declared Hebrew
and POB English. This corrects the project's assessment of a published claim;
it is not a discovery of previously unknown manuscript wording.

### What the thematic argument actually concludes

Lilly's section 5.4.2, printed 254–262 / PDF 266–274, does not argue that
the heart/spirit variants establish a coordinated book-wide revision around
36:23c–38. Her opening and conclusion explicitly find no coherent distribution.
She instead interprets the longer passage as a localized reworking of chapter
11. That positive local argument remains possible: failure to find a wider
pattern neither disproves an insertion nor establishes borrowing direction.
Our previously queued test must not assume the very pattern her discussion
rejects. The earlier [language controls](EZEKIEL_36_LANGUAGE_CONTROLS_2026-10-12.md)
remain the separate record for chapter 11/36 comparisons.

Two attribution controls prevent treating the introductory totals as evidence:

- The sixth item under the MT heading, 36:5bγ, is actually Hebrew manuscript
  93's heart reading, distinguished from MT in her prose, note 521 and apparatus
  at printed 89. The retained WLC ending is `למען מגרשה לבז`, not that heart
  variant. This does not erase the earlier `כל לבב` in the same verse. The
  manuscript-93 claim remains mediated through Lilly, not a newly read codex.
- The introductory six-plus-four-plus-one count does not match the subsequent
  subsection's two shared-reading cases, 21:12(7) and 29:16. Her fourth P967
  item starts as 44:7 and later includes 44:9. We do not convert this uneven
  grouping into a corrected statistical sample or a historical probability.

These controls constrain an inference from selected variants; they do not
invalidate the dissertation's entire literary argument. Nor does the word
"heart" identify a Hebrew-stage change by itself: translation vocabulary,
inner-Greek variation and local transmission must be tested separately.

### Direct manuscript control: Ezekiel 44:7 and 44:9

The [Cologne catalogue](https://papyri.uni-koeln.de/features/rahlfs) identifies
P. Köln Theol. 11 verso as codex page 107, Ezekiel 43:26–44:7, and recto as
page 108, 44:7–15. Root checked those catalogue rows and both complete official
photographs; a separate source checker independently inspected the same pages.
This is a targeted reading of legible text, not a full diplomatic transcription.

| Target | P967 photograph | Consequence |
|---|---|---|
| 44:7 | Near the bottom of [page 107, PT11v](https://papyri.uni-koeln.de/stueck/DS_d1e78916/img/theol_03_13_15_16_8_16_9_40_42_a_b_c_43_u_ohne_inv_nr/orig/PT11v.jpg), `καρδια του γεινεϲθαι` follows the uncircumcised-heart wording continuously, without the flesh qualification. | A genuine shorter Greek reading, not a modern hole at the decisive transition. |
| 44:9 | On [page 108, PT11r](https://papyri.uni-koeln.de/stueck/DS_d1e78916/img/theol_03_13_15_16_8_16_9_40_42_a_b_c_43_u_ohne_inv_nr/orig/PT11r.jpg), body lines 8–9 read `καρ/δια και απεριτμητοϲ ϲαρκι`; line 10 continues the sanctuary exclusion. | Bodily uncircumcision is explicitly retained in this manuscript's admission rule. The slash marks the line break, not missing letters. |

The cited snippets insert word spaces but do not supply missing letters.
Line numbers for page 108 count the first body line as 1. P967 is one witness
at two adjacent loci, not two independent votes. The retained WLC has both
heart and flesh qualifications in both verses; the publisher's selected
[Rahlfs–Hanhart 2006 Greek](https://www.die-bibel.de/bibel/LXX/EZK.44) also has
both. The selected edition must not be substituted for P967 at 44:7.

Lilly printed 259 / PDF 271 extends the MT flesh plus to 44:9. That specific
extension is contradicted by the photograph. Her appendix at printed 402 /
PDF 414 records only `δια τουτο` for 44:9; its silence on circumcision is not
our proof of retention. The manuscript itself supplies the positive evidence.

Accordingly, P967's 44:7 minus cannot establish a consistent heart-only
admission policy or a Hebrew-stage theological revision. Conversely, retention
at 44:9 does not prove the origin of 44:7. Repeated circumcision wording makes
copying omission a plausible alternative to deliberate editing, not a demonstrated
cause. Greek copying, translation, editing and a differing Hebrew antecedent
remain distinguishable possibilities. No Hebrew deletion is approved.

### POB impact, provenance and next discriminating action

Current 44:7 and 44:9 already include both qualifications. Their Hebrew,
English and notes remain unchanged. A future 44:7 disclosure note should state
both the local P967 omission and its retention at 44:9; a note claiming a
heart-only temple rule would mislead. No such note is applied by this report.
The next useful work is to establish the wider witness support and apparatus
for the local 44:7 minus before assessing its history or drafting that note,
not to tally this thematic sample again. This result changes no canon judgment.

The full PDF remains the institutional Lilly input pinned in the preceding
section. Root read complete printed 254–262 with notes and visually checked
the decisive printed 254, 256, 259 and 262, plus complete apparatus pages 89
and 402. The source checker independently verified printed 259/402 and both
manuscript photographs. This is not a full dissertation or modern apparatus
collation. The PDF skill prevented relying on corrupted Greek extraction.
No generated fill, restored letter, new image enhancement or ImageGen evidence
was used; all source images and the PDF remain outside Git.

```text
PT11v.jpg (148644 bytes)  ebfae5246f18f9e060820062dd1b08d4cf29f5dcfe1b6abb6b28ec51d63f8951
PT11r.jpg (145896 bytes)  4e30a44f52ca4f85b01bfb808d3b2118ba28eeedb4c89ea019bd3eb3f7a639b7
sources/ot/wlc/Ezek.xml  90bf8adfa66b2f6695c702263fe668755c99c6afc386202c12de4f704f5d4e46
translation/ot/ezekiel/044/007.yaml  9b6f99250aa122497a577fb140c4efc24dd650bb53786774cfa65d1fdc600919
translation/ot/ezekiel/044/009.yaml  9c991a19290e57435c21b35f686a1a33b631c29c0b12181d9273d06b38b6e0bf
```

## Sahidic reading boundary and the shorter text argument

The newly consulted Coptic evidence establishes a liturgical reading ending
within Ezekiel 36:23, not another continuous Bible lacking 36:23c–38. It does
not independently establish shorter Hebrew ancestry. Retain source/English
and historical-priority HOLD.

Crane's printed 274 note 427 cites Lust 1981 page 525 for a Sahidic manuscript
with three Ezekiel oracles, the last listed as 36:16–23b. Crane explicitly says
he could not obtain the manuscript, but treats its endpoint as support for
the shorter original. The corresponding published excerpts are now directly
accessible in [Erman's 1880 edition](https://archive.org/details/bruchstckederob00ermagoog),
*Bruchstücke der oberaegyptischen Uebersetzung des alten Testamentes*, offprint
pages 3–4 and 36–37. Lust's original article remains unconsulted; his precise
claim is still mediated through Crane, not newly verified or corrected here.

### Object and actual sequence

Erman's manuscript D is **Oxford, Bodleian Library, Huntington 5**. His page 3
identifies eight fragments of a liturgy, not a continuous Ezekiel codex. The
March 31, 2021 [List of Coptic Biblical Manuscripts](https://copt-ot.adw-goe.de/documents/10231/23535/LCBM_1.0_2021.pdf/dec4f073-dbfa-4af6-9971-3b2bace5b3eb),
page 18, maps Huntington 5 to LCBM/SMR **sa 292L** and Schüssler's Biblia
Coptica **sa 211L**. These are two numbering schemes for one witness, not two
independent manuscripts. The catalogue row lists NT contents; its silence
about Ezekiel cannot negate the OT excerpts in the edition.

Erman's page 4 supplies the manuscript-content map:

| Manuscript pages as reported by Erman | Selected contents relevant here |
|---|---|
| 239–240 | Ezekiel 36:16–23, then Psalm 108:1–3 |
| 251–252 | Jeremiah 9:7–11, then Ezekiel 21:14–17 |
| 266–281 | Several readings, including Ezekiel 28:1–19 |

Thus the three Ezekiel excerpts are not arranged in the manuscript's canonical
chapter order. The word “last” in the mediated report must not become evidence
for the physical sequence. Erman's printed page 37 places Amos 3 immediately
after the Ezekiel excerpt, but this is editorial arrangement: his contents map
identifies Psalm 108 as the following manuscript reading. Neither sequence is
a preserved Ezekiel 36→37 or 36→38 transition. Psalm numbering is retained as
printed, without silently converting it to MT numbering.

[Bąk 2023](https://doi.org/10.31743/biban.13804), complete pages 11–12, identifies
the same object as Cod. XX/Huntington 5 and a paper Holy Week lectionary. His
probable twelfth/thirteenth-century dating is attributed to Schüssler, not a
fresh palaeographic finding here; the modern-study qualification below records
competing later datings. His note 56 clarifies the Holy Week setting
of Erman's term *Osterwoche*. The precise conversion of the night-hour rubric
to a modern civil weekday is unnecessary to the textual judgment. Bąk also
warns that Erman's volume includes four manuscripts; not every excerpt in it
belongs to Huntington 5.

### What the endpoint can and cannot support

Erman's complete printed pages 36–37 publish 36:16–23. The final line retains
the declaration naming Adonai and the Lord after the recognition formula.
Crane's own page 274 says P967 stops **before** that declaration. Therefore,
their clause endpoints cannot be called identical merely because a secondary
description uses “23b.” This comparison uses a historical printed Coptic text
and Crane's report of P967, not a new autopsy of either manuscript.

There is additional wording within the printed Coptic verse 23; the bounded
two-clause comparison below now identifies part of it, while full collation
remains unperformed. No exact equivalence to the whole Greek or
Hebrew verse, complete Coptic translation, or retroverted Hebrew is claimed.
The narrowly checked endpoint and the liturgical contents map suffice for the
present distinction: an excerpt stopping here is compatible both with selection
from a longer Bible and with inheritance from a shorter form. It cannot decide
between them without evidence about the parent text and the excerpt's history.

The positive contribution is evidence that a reading could be treated as a
unit ending near this point. It weakens a categorical claim that such an ending
could never function independently, but does not prove literary completeness
in the original book, the absence of the renewal promise from an ancestor,
or independence from P967's Greek transmission. A medieval copy may preserve
older material; its later date alone does not settle that question either.

Crane's linguistic discussion at 270–278 remains a substantive expansion
argument, not a new Hebrew witness. Its Greek title distinctions and Hebrew
features overlap the [completed controls](EZEKIEL_36_LANGUAGE_CONTROLS_2026-10-12.md).
The Coptic lead does not turn that cluster into proof of Hebrew priority.
Further progress requires discriminating evidence about the actual Greek
transition, versional ancestry or direction of revision. Repeating this
lectionary's endpoint or adding model votes will not supply it.

### Consultation and reproducibility

Root visually inspected the complete Erman offprint pages 3–4 and 36–37
(PDF pages 19, 20, 84 and 87), Bąk pages 11–12, Crane printed 274/PDF277,
and the LCBM page 18 row and headers. A source agent independently identified and inspected the Erman
pages. The edition transmits Schwartze's nineteenth-century copies; no new
manuscript pixels, restored letters or ImageGen evidence enter the result.
Native extraction of the scanned Erman PDF returned blank pages, so it was
not treated as a readable transcription. The actual page images control.

| Private source | SHA256 |
|---|---|
| `/tmp/pob-erman-coptic.PlKLTQ/erman1880.pdf`, 1,599,015 bytes, 118 PDF pages | `17d4f34cb77adb76a4e22f1e3cac8aae14447edb861eeee7bc9707c5103388ef` |
| `/tmp/pob-erman-coptic.PlKLTQ/bak2023.pdf` | `4e879882f65e598b40bdee894e1f8e2b9630c9d17dbc1e664eba50f08ca299bf` |
| `/tmp/pob-sahidic-ezekiel-wrdqbq/lcbm2021.pdf` | `74ee9713b712a1a5afc34e8ad9aabdfc9a957e2e3c083b82dfdc2d6b4f1bacde` |

Erman's ordinary [download](https://archive.org/download/bruchstckederob00ermagoog/bruchstckederob00ermagoog.pdf)
and Bąk's [alternative repository copy](https://theo-logos.pl/bitstreams/6d49c910-b8b0-4668-9175-9af719aba04a/download)
were acquired successfully; Bąk's KUL repository route returned 403. No access
controls were bypassed. PDFs and renders remain outside Git and are not
relicensed with POB. These checks establish a published-source comparison,
not all-Coptic coverage or completion of the wider restoration goal.

### The scattering clauses within the printed verse 23

A further visual reading of Erman's complete printed page 37 (PDF page 87)
identifies two clauses before the nations' recognition formula. With word
spacing and supralinear marks normalized, the working transcription is:

> ϯⲛⲁϫⲟⲟⲣ ⲙ̄ⲙⲱⲧⲛ̄ ⲉⲃⲟⲗ. ⲁⲩⲱ ⲧⲉⲧⲛⲛⲁⲣⲕⲟⲩⲓ.

Working translation: **“I will scatter/disperse you, and you will become
few/small.”** This is a reading of the nineteenth-century printed edition,
not a diplomatic transcription of Huntington 5 or recovered manuscript ink.
The following phrase is not transcribed here: handwritten reader marks in
this scanned copy must not be silently incorporated into the printed text.
No complete translation of verse 23 is certified by this two-clause check.

The lexical controls are explicit. The electronic transcription of
[Crum, 782a–783a, ϫⲱⲱⲣⲉ](https://remnqymi.com/crum/2447.html)
includes the Sahidic form ϫⲟⲟⲣ⸗ and the scattering/dispersal sense with
ⲉⲃⲟⲗ; it also records broader destructive senses. The subsection ⲣ ⲕ. in
[Crum, 94a, ⲕⲟⲩⲓ](https://remnqymi.com/crum/61.html) gives being small/few
and, separately, being young. Numerical diminution is the contextual working
interpretation here, not the only dictionary sense. These are consulted
electronic transcriptions, not freshly checked images of Crum's original pages.
The current Coptic Dictionary Online identifies the compound as **C1056**,
form CF3471, with references CD 94a and ChLCS 16a in its public
[entry data](https://coptic-dictionary.org/details/C1056.json).
Its C7328 entry identifies the scattering verb and links the ⲉⲃⲟⲗ compound.
The lexical resources are related tools, not independent manuscript witnesses.

Neither the local WLC Hebrew at 36:23 nor the selected Greek at that verse
contains these scattering/diminution clauses. The Greek control is the
[pinned digital edition](https://raw.githubusercontent.com/OpenScriptorium/lxx-morph/c91f6b1e8fb3ba37df701e6ae31f675ace71a2b2/db/seeds/lxx_morph/ezekiel.json)
already documented in the [language controls](EZEKIEL_36_LANGUAGE_CONTROLS_2026-10-12.md):
only the ordered surface text was used, not generated morphology or reasoning.
This comparison is with a selected text, not every Greek manuscript or the
unacquired target apparatus. Hebrew and Greek 36:25 were also checked: their
clean-water/cleansing promise does not explain these two clauses as a simple
quotation of that promise. No donor passage is established.

**Consequence:** this is not merely the familiar 36:23 wording with a shorter
endpoint. Its distinctive internal wording must be explained before the
lectionary is used to reconstruct a continuous shorter Ezekiel. Liturgical
adaptation, inherited versional variation and copying/editorial transmission
remain possibilities; this check does not establish which occurred, when,
or in which direction. It neither disproves an older shorter form nor supplies
a uniquely retrovertible Greek or Hebrew parent. POB source and English remain
unchanged, with historical priority on HOLD.

A second accessible primary publication supplies an important dependency
check: [Ciasca 1889, volume II](https://archive.org/details/sacrorumbiblioru02cias),
printed pages 299–300 (PDF pages 383–384). Root inspected both complete pages.
The page 299 note explicitly says the surviving 36:16–23 material was copied
from Erman's edition. It prints the same two clauses and observes that the
span beginning with the scattering clause and ending at the following power
expression is not recognized by the other witnesses he compared. That is
Ciasca's historical apparatus judgment, not our exhaustive search of all
known witnesses. The difference is therefore not a new scholarly discovery,
and Ciasca's printing is **not a second independent manuscript attestation**.
Page 300 finishes the excerpt, then introduces 36:25–29 with a separately
marked fragment and a note identifying a liturgical opening. The edition's
juxtaposition does not establish a continuous manuscript transition or settle
the ancestry of the 36:23 reading. No full collation of 36:25–29 is claimed.

The next discriminating comparison is a manuscript image or independent
edition of this precise reading, followed by related Holy Week lectionary
witnesses and further critical discussion of these clauses. Repeating an endpoint-only
comparison would miss the newly identified difference. The lexical check also
rejected an incorrect preliminary C111 headword citation: that entry concerns
ⲁⲙⲁϩⲧⲉ (ⲉϫⲛ-), not ⲣⲕⲟⲩⲓ. It was not published as supporting evidence.
Public entry JSON was fetched through routes used by the dictionary's own
application; the older CGI URLs returned an application shell, not entry text.
No generated image or OCR supplied letters. The Erman and Greek file hashes
were reverified against the earlier records; no source files were imported
into Git or relicensed.

The additional Ciasca PDF is retained privately at
`/tmp/pob-sahidic-ezekiel-wrdqbq/ciasca1889-vol2.pdf`, 32,719,842 bytes,
470 pages, SHA256
`42f8bb76e8d003225ce3b12ec253cfb08a5166701a679327d876c0e6ff444897`.
Its machine extraction misrecognizes Latin and Coptic as Greek; it served
only to locate pages, not as the source of quoted letters or apparatus claims.

### Modern transcription and a separate Bohairic image comparator

The official CoptOT edition now supplies the exact Huntington 5 target:
[public TEI, docID 620292, pageID 2400](https://coptot.manuscriptroom.com/community/vmr/api/transcript/get/?docID=620292&pageID=2400&format=teiraw).
Root read the entire returned TEI, including its header. It identifies the
Bodleian manuscript, credits Lina Elhage-Mensching as transcriber and Diliana
Atanassova as reviser, and carries the 2022 DFG Coptic Holy Week Lectionary
Project credit alongside the platform's 2026 notice. This is a separately
credited modern transcription of the same witness, not another manuscript.
The header does not establish its independence from earlier printed editions
or certify a fresh image collation by us.

The two scattering/diminution clauses agree with the bounded Erman reading.
The following phrase is explicitly transcribed as
**ϩ︤ⲙ︥ ⲡⲧⲣⲁⲉⲓ̈ⲣⲉ ⲛ̄ⲧⲁϭⲟⲙ**, provisionally “when I exercise my power.”
This is now a published reading, not our reconstruction from the reader-marked
print. After the nations' recognition and Adonai formula, the TEI records the
Psalm heading and number 108, then Psalm 108:1–3 and Matthew 26:30–31 (ending
mid-verse on this page). It thus corroborates the liturgical transition, not a
continuous Ezekiel 36→37/38 transition. Psalm numbering follows the edition.
The [page metadata](https://coptot.manuscriptroom.com/community/vmr/api/metadata/liste/search/?docID=620292&detail=page&includeFeatures=Extant&format=xml)
maps page 240 to shelf folio “f. 3” and explicitly marks its image protected,
access level 2. No protected image was acquired or inferred from a placeholder.

The [official Ezekiel 36:23 index query](https://coptot.manuscriptroom.com/community/vmr/api/metadata/liste/search/?indexContent=Ezek.36.23&detail=page&includeFeatures=Extant&format=xml)
returns 14 records/19 pages: seven Bohairic lectionaries, Huntington 5, one
Arabic lectionary and five non-manuscript baseline records. This is a bounded
index result, not a complete census of surviving verse 23. In particular,
[“Sahidic Bible Basetext”](https://coptot.manuscriptroom.com/community/vmr/api/transcript/get/?docID=1620025&pageID=1051036000&format=teiraw)
repeats the distinctive verse 23 wording but is not independent attestation.
Its verse 24 is explicitly marked as supplied from Shenoute; that composite
sequence is not the contents of a continuous codex. The precise source of
its verse 23 is not stated in the consulted header.

A genuinely different physical witness is **BnF Copte 7 / bo 3003L**, docID
613003, pageID 3470. Root and a source agent inspected the complete
[public manuscript image](https://coptot.manuscriptroom.com/images/webfriendly/Paris_BnF/Copte7/PBN_Copte7.f.174r_lib.jpeg),
attributed by CoptOT to Gallica/BnF. The image filename and shelf metadata use
f.174r/f.174, while the index's separate folio field says 183r; these labels
are not silently harmonized. In the compact verse 23 span, the name/profanation
material leads directly to the nations' recognition and Adonai formula, then
a separated Psalm heading. The Hunt5 scattering/few/power sequence is not
present in that observed span. The initial verb phrase is less secure at the
available 697-pixel width, so no complete diplomatic verse transcription or
character-perfect agreement with Greek is claimed. This comparison separates
**a shared liturgical stopping point from agreement in internal wording**.
Different manuscripts and dialects do not by themselves prove independent
ancestry or the direction of adaptation.

The related Sahidic lectionary **sa 16L / Z99**, Vatican Borg. copt. 109,
cass. XXIII, fasc. 99, is not a second verse 23 witness in this index result.
Its complete [f.113v TEI](https://coptot.manuscriptroom.com/community/vmr/api/transcript/get/?docID=620016&pageID=2135&format=teiraw),
read with its header, goes from John 17:25–26 to a third-night-hour rubric,
Psalm 108 and Matthew 26. No Ezekiel excerpt intervenes at that location.
That observation concerns this page, not absence from every unindexed or lost
leaf. The Holy Week rubric is not converted into a modern civil-night date.

Dating also needs qualification. [Atanassova 2018, printed 9–10](https://coptot.manuscriptroom.com/images/webfriendly/PDF/KUAYISU2.pdf),
complete pages read and visually checked, presents a probable thirteenth-century
date for Hunt5 but also reports Suciu's suggestion of the second half of the
fourteenth century, based on comparison with later manuscripts. This is a
reported alternative, not a newly established date. Her treatment confirms
the fragmentary Holy Week lectionary context. Neither date determines the
age of its underlying text, and neither changes our Hebrew priority judgment.

**Decision:** retain POB source and English. The modern transcription strengthens
confidence in what the published Hunt5 reading says; the separate Bohairic
image shows why the endpoint alone cannot carry a claim of common shorter
biblical ancestry. Next compare higher-resolution Copte 7 or another indexed
public Bohairic/Arabic page, with its actual verse wording and source provenance.
Index coverage, baseline texts, editions and manuscripts remain separate
evidence classes. No ImageGen output supplies letters or a source amendment.

Private reproducibility inputs, acquired October 14:

| Input under `/tmp/pob-sahidic-ezekiel-wrdqbq/` | SHA256 |
|---|---|
| `hunt5-p240.xml` | `afffbb59fe590a8c2775f924274687e42848fac0ccd5458db3c30dee3aa8940a` |
| `hunt5-metadata.xml` | `c16ae950f5675c231035aa32613b177bb4c0666231bb32c41759315b426f1d90` |
| `ezk36-23-index.xml` | `0ea0be09846ea8777f5923afe4e4f74cf6eab287d96a53aedaff0cc32cb685bd` |
| `sahidic-basetext-ezk36.xml` | `fb819feab98a0e869b3d37cb63881a7af14f2220106a82eaab88a23fb6b152cf` |
| `sa16L-f113v.xml` | `e247629bc2efdc0985594f15e9de56f8178af1c33775d497e2a37738e89e2a7d` |
| `copte7-f174r.jpeg` | `048899b3f0d7c0040b51d34c2beeaa300d9ed3210803a7d13039a9b4d90a31b2` |
| `atanassova-pascha.pdf` | `8157a9f90a6ccd9a705dcff1d709fb61033506aaf16b418d2e7200ec093064f5` |

Public TEI and metadata were fetched through the publisher's API; the generic
web-fetch tool could not open the target transcription URL. The TEI carries
CC BY-SA notices; the image has its separate institutional attribution.
These inputs remain outside Git and are not relicensed under POB's license.

### Further Bohairic and Arabic wording controls

The next comparison reads actual page images, not additional index votes.
Root and a source agent independently inspected the complete CoptOT images
for **BnF Copte 70 / bo 3004L**, docID 613004, pages 3670–3680:
[recto](https://coptot.manuscriptroom.com/images/webfriendly/Paris_BnF/Copte70/PBN_Copte70.f.184r_lib.jpeg)
and [verso](https://coptot.manuscriptroom.com/images/webfriendly/Paris_BnF/Copte70/PBN_Copte70.f.184v_lib.jpeg).
The indexed shelf/image labels are f.184r/v, whereas the separate folio fields
say 195r/v. Those labels are retained rather than silently equated.

Verse 23 crosses the page break. The first five main-text lines of the verso
finish the name/profanation material, recognition by all nations, and the
Adonai/Lord formula. A divider and Psalm heading follow immediately. The
readable main-text span lacks Hunt5's scatter/few/power sequence, and there
is no final sanctification clause after the formula before the Psalm. The
opening verb at the bottom of the recto is not confidently resolved. A faint
two-line addition above the verso's first main line also remains incompletely
read: the absence finding must not be expanded into certification of every
marginal glyph. The Arabic parallel is not used to supply missing Coptic.

**BnF Arabe 113 / ar 1L**, docID 900001, page 2230, supplies a different
language control. Its [complete indexed page image](https://coptot.manuscriptroom.com/images/webfriendly/Paris_BnF/Arabe113/PBN_Arabe113.f.112a_lib.jpg)
was inspected by root and the source agent. The final two lines include
**وستعلم جميع الأمم**, “and all the nations will know,” and
**أني أنا هو الرب القوي**, “that I am the mighty/strong Lord.” These are
bounded readings, not a complete diplomatic transcription. The right edge
limits the opening sanctification/name expression. No Hunt5 punitive sequence
is visible in the final four–five lines. The adjective “mighty/strong” is not
Hunt5's separate exercise-of-power clause, and this Arabic ending must not be
silently labeled the Coptic Adonai formula. A terminal dot and blank space
follow; this image does not show a subsequent Psalm heading. The shelf/image
label f.112a and index folio 111r are preserved separately.

The separate Arabic codex and the Arabic column within Copte 70 are not one
object. Nor do different objects establish independent textual ancestry.
These controls document local versional wording, not recoverable Hebrew
letters or a uniquely identifiable Greek exemplar.

**Consequence and stopping rule:** retain the POB source and English. The
comparison now has sufficient endpoint controls to stop treating another
matching liturgical cutoff as a consequential priority test by itself.
Hunt5's unusual internal wording remains a real versional question; resolving
its ancestry requires a discriminating reading, manuscript relationship or
continuous-text evidence. A fresh image with additional legible marks could
also reopen the local transcription. Repeated endpoint checks or model votes
cannot establish a continuous Ezekiel 36:23c–38 omission. No generated image
has been used to fill the unclear verb or marginal addition.

Private image inputs under `/tmp/pob-sahidic-ezekiel-wrdqbq/`:

| File | Dimensions | SHA256 |
|---|---|---|
| `copte70-f184r.jpeg` | 675 × 1053 | `940310a560216f0f9671a607597a33b822bedd665648537dda16822dc0aeff9f` |
| `copte70-f184v.jpeg` | 663 × 1054 | `25fefa1e2a9990ccfaf609cc6b018033738a53dfaa867c1a3fd1cb1cff402389` |
| `arabe113-f112a.jpg` | 653 × 997 | `17a57074157af8cea434deb485cf3ed5405eeb04e4200b78760cc8ebaaeb0363` |

All three images are attributed by the CoptOT index to Gallica/BnF and were
acquired October 14. No image is imported into Git or relicensed here.

The library's original digitization was also located and visually matched:
[Gallica view 187](https://gallica.bnf.fr/ark:/12148/btv1b100872043/f187.item)
has the recto target on the right (visible handwritten number 183), and
[view 188](https://gallica.bnf.fr/ark:/12148/btv1b100872043/f188.item)
has its verso on the left. The full-spread `highres` assets are only
1342 × 1054 and 1345 × 1054 pixels; the filename is not proof of sufficient
resolution. They confirm page identity/context but do not resolve the faint
verb and marginal addition. The viewer's zoom additionally exposes IIIF
tiles, while direct manifest/full-image command-line requests returned 403.
The public browser viewer opened after its automatic security check; no
challenge was bypassed. No complete native-resolution image was acquired,
and no claim that better capture detail is unavailable follows.

The two observed full-spread assets were retained through the browser's asset
export, privately under
`/var/folders/r7/29mcf1yj3z18g5c_t2h779jh0000gn/T/browser-use/assets/204e79cd-7ebd-4bef-9aa4-5f79a9273ff4/`:

| Asset | SHA256 |
|---|---|
| `f5b8064998e7bee0.highres` (view 187) | `771e5a69ba29cc21594b85bb8670cb75423dcfa14d3affcaa6701bdbe46e6cd8` |
| `97670035ac9fd66c.highres` (view 188) | `b972f182a424f7b438b26a6a5d3c7a5c42f89c3ccb19da723d33bd78f159cdeb` |

### Punitive wording: a bounded parallel test on October 14

**Result: partial parallels, not an identified donor or a Hebrew restoration.**
The preceding endpoint controls cannot establish Hunt5's textual ancestry.
This pass instead compares its distinctive internal sequence with four
candidate biblical contexts: Deuteronomy 4:27 and Ezekiel 12:15–16, 5:12 and
36:19. These were selected for scattering, numerical reduction and recognition
language, not as an exhaustive search of potential sources.

Hunt5's [credited TEI](https://coptot.manuscriptroom.com/community/vmr/api/transcript/get/?docID=620292&pageID=2400&format=teiraw)
at B51K36V23 has first-person future scattering of a second-person plural
object, then the addressees becoming small/few, then an exercise-of-power
clause, followed by recognition by all nations. Its distinctive few expression
is `ⲧⲉⲧ︤ⲛ︥ⲛⲁⲣ̄ⲕⲟⲩⲓ̈`; the power expression is
`ϩ︤ⲙ︥ ⲡⲧⲣⲁⲉⲓ̈ⲣⲉ ⲛ̄ⲧⲁϭⲟⲙ`.
The earlier working English “I will scatter you, and you will become few/small,
when I exercise my power” remains a bounded interpretation, not a certified
translation of the entire verse. This is a new comparison of previously read
wording, not newly discovered ink.

| Candidate | Actual comparison | Limit on the ancestry claim |
|---|---|---|
| Deuteronomy 4:27 | WLC has the Lord scattering the addressees and their remaining few in number. The selected Greek likewise combines scattering with being left few. Two manuscript-specific Sahidic transcriptions have the same scatter lexical family as Hunt5. | The Lord is third-person subject, and the Sahidic few expression uses `ⲥⲟⲃⲕ` with a numerical expression, not Hunt5's `ⲣⲕⲟⲩⲓ`. There is no exercise-of-power clause in this verse. This is the closest checked thematic sequence, not a verbatim donor. |
| Ezekiel 12:15–16 | WLC and selected Greek combine scattering, a surviving numbered group, and recognition of the Lord. The available Sahidic basetext also has scatter/recognition vocabulary. | The scattered people are third-person objects; verse 16 speaks of sparing people rather than telling the addressees they will become few. The Sahidic wording lacks Hunt5's `ⲣⲕⲟⲩⲓ` and power clause. The basetext does not identify its manuscript/edition dependency here. |
| Ezekiel 5:12 | WLC and selected Greek describe punitive scattering of a portion of the people. | This does not reproduce Hunt5's few/power sequence. The Hebrew has thirds whereas the selected Greek has quarters; those are distinct readings, not interchangeable wording. This pass does not adjudicate that separate variant. |
| Ezekiel 36:19 | In the immediate context, WLC and selected Greek describe God scattering them among nations and judging them. | This is retrospective first-person narration with third-person objects, not Hunt5's future address. Neither selected text has the few/power sequence here. Proximity alone does not prove adaptation. |

The Greek controls are the publisher's Rahlfs–Hanhart 2006 text at
[Deuteronomy 4](https://www.die-bibel.de/bibel/LXX/DEU.4),
[Ezekiel 12](https://www.die-bibel.de/bibel/LXX/EZK.12),
[Ezekiel 5](https://www.die-bibel.de/bibel/LXX/EZK.5) and
[Ezekiel 36](https://www.die-bibel.de/bibel/LXX/EZK.36).
They are selected edition readings, not an apparatus census or independent
manuscript votes. The private Ezekiel JSON was used only to locate ordered
surface words, then checked against the publisher; its generated analyses
are not linguistic evidence. The local WLC controls use direct verse-word
elements, not nested variant readings or POB's English.

The two Deuteronomy transcriptions are
[sa2001, Papyrus Bodmer XVIII, p.42](https://coptot.manuscriptroom.com/community/vmr/api/transcript/get/?docID=622001&pageID=420&format=teiraw)
and [sa2006, Morgan M566, f.110v](https://coptot.manuscriptroom.com/community/vmr/api/transcript/get/?docID=622006&pageID=2200&format=teiraw).
The first credits Diliana Atanassova and reviser Uwe-Karsten Plisch; the second
credits Suzana Hodak for Deuteronomy and reviser Diliana Atanassova.
The sa2001 header lists both joined holdings; its page is assigned to Bodmer.
Its transcription marks supplied and unclear letters, including parts of
the outward, leaving and number expressions. Those supplements are not
additional surviving letters. Morgan's transcription provides the comparison
without silently treating Bodmer's supplied letters as observed ink.

The [Ezekiel 12 Sahidic basetext](https://coptot.manuscriptroom.com/community/vmr/api/transcript/get/?docID=1620025&pageID=1051012000&format=teiraw)
has `ⲛⲧⲁϣⲱⲭⲡ` for the reserving/sparing construction and
`ⲛϩⲉⲛⲣⲱⲙⲉ ϩⲛ ⲟⲩⲏⲡⲉ` for people in number. It is an editorial
baseline, not an identified ancient witness. Its 2016 header supplies no local
source dependency. The index's separate physical sa2099 lead has not been
read at this locus and is not used to assign ancestry to this basetext.

**Decision:** neither a direct quotation nor a specific conflation is established.
Thematic resemblance is compatible with adaptation but does not prove it;
wording differences also do not exclude loose adaptation. No checked candidate
accounts for the complete distinctive sequence. Do not assemble disconnected
phrases into a hypothetical donor and then count that construction as evidence.
An unlocated donor is not positive evidence for an ancient Hebrew plus.
Conversely, a possible liturgical adaptation would not by itself disprove
P967's independent evidence for a shorter Greek passage.

Retain POB's source and English and keep historical priority unresolved.
Further work needs an independently located occurrence of the distinctive
few/power wording, a demonstrated relationship between textual witnesses, or
the missing continuous-text/critical-apparatus evidence. This finite comparison
does not justify repeating these same four contexts, extending the endpoint
sample, or claiming that no biblical parallel exists anywhere. No ImageGen
output enters the evidence and no new source letters are accepted.

Root read the target TEI clauses and headers and the Hebrew/Greek controls;
one source agent separately read the Coptic comparators. Private inputs under
`/tmp/pob-coptic-ancestry.jd3jkT/`, not imported or relicensed in Git:

| File | SHA256 |
|---|---|
| `sa2001-p42.xml` | `fbd4ca42ba19631949033a47d095112c65a886713c1a652b208a0252ff531f12` |
| `sa2006-f110v.xml` | `1c86b21993f034db58a854a41c61c15f6fec2f7ee27078cf05cc102ac6b86ae2` |
| `sahidic-basetext-ezek12.xml` | `14e4ac82685adbd42631161c23b04a13687c40d743910a4447574a4842eb0b8e` |

The manuscript TEIs declare CC BY-SA 4.0; the basetext declares CC BY-SA 3.0.
Hunt5's existing hash remains unchanged. At input commit
`59da2218dedb424b76698c9d05bed3fe9e30ee02`, WLC Deut.xml has SHA256
`04f8087442a1e67a631cd70f2ac4e42fe0a780ae132edb165a3a29f3f290358f`
and Ezek.xml has
`90bf8adfa66b2f6695c702263fe668755c99c6afc386202c12de4f704f5d4e46`.

### Sahidic phrase search and coverage control

**The available basetext has no second exact match, but its gaps prevent an
exhaustive Sahidic-Ezekiel absence claim.** The official
[filtered index](https://coptot.manuscriptroom.com/community/vmr/api/metadata/liste/search/?docID=1620025&indexContent=Ezek.1.1-Ezek.48.35&detail=page&includeFeatures=Extant&format=xml)
returns one editorial document with 48 chapter records. All 48 linked chapter
transcriptions were acquired through ordinary public requests, using the
already supported `teiraw` format. The
[receipt](../sources/textual_restoration/comparisons/ezekiel_sahidic_phrase_screen.2026-10-14.v1.json)
pins the index, every chapter URL/hash, the actual empty-reference lists and
all query matches. No full third-party chapter text is imported into Git.

Coverage matters more than the chapter count:

| Measured property | Result | Meaning |
|---|---:|---|
| Verse-labeled `ab` elements | 1,275 | Editorial labels, not 1,275 fully preserved verses |
| Elements with no word text | 432 | No searchable wording; inspected examples contain lacuna markers |
| Elements with some word text | 843 | Includes partial passages and supplements, not necessarily complete verses |
| Elements containing `supplied` | 113 | Includes material attributed to other literature |
| `supplied` / `gap` elements | 1,176 / 515 | XML elements, not counts of lost letters or independent witnesses |

For example, 36:1 and 36:30 contain only a lacuna marker within a word element;
36:24 supplies words attributed to Shenoute. The supplied-source labels across
the collection include transcriber, homily, Shenoute, Besa, Paul of Tammah,
Scala and New Testament material. These labels require passage-specific
verification before witness use; the data cannot be treated as one continuous
ancient codex. Chapter 2 has labels through 13, whereas chapter 27 lacks a
27:31 label. No direct WLC verse-count equivalence is assumed.

The search casefolds word text, applies Unicode NFD and removes combining
marks and whitespace. It concatenates descendant `w` text within each `ab`,
including editorial supplements. It is substring retrieval, not morphological
analysis. Both `ⲣⲕⲟⲩⲓ` and the exact normalized
`ⲡⲧⲣⲁⲉⲓⲣⲉⲛⲧⲁϭⲟⲙ` occur only at **Ezek.36.23**, the disputed text
itself. That match is not independent corroboration of Hunt5. Broader controls
find `ⲕⲟⲩⲓ` in 12 verse elements, `ⲥⲟⲃⲕ` in one and `ϭⲟⲙ` in 30.
These are verse-hit counts, not token counts or 30 occurrences of one lexical
sense. Root inspected the returned contexts; none supplies the complete
scattering/few/power sequence outside the target.

The broader search adds Ezekiel 5:3 as a numerical-smallness comparator, not
an identified donor. Its construction is taking a small number and binding
them in the garment, not Hunt5's prediction that the addressees will become
few. Other smallness hits include youth and relative size; those cannot be
silently grouped as numerical reduction. Coptic text outside word elements
was also screened: the sole flagged verse, B51K48V28, has an editorial `sic`
correction in a note, not missed continuous text. There are no `app` elements
in these inputs, so alternative apparatus readings are not silently counted.

**Consequence:** retire a search for another identical occurrence within these
same encoded words. Do not infer that the complete book, all orthographic
variants or all Sahidic witnesses lack a donor. The useful next evidence is
independently sourced missing text, a distinctive parallel in another work,
or continuous manuscript/apparatus evidence. Source and POB English stay
unchanged. This coverage audit is part of the all-source method: a successful
download of every indexed chapter is not a successful comparison of every
surviving manuscript reading.

Private inputs are under `/tmp/pob-sahidic-ezekiel-search.tFdL3k/` and the
basetext declares CC BY-SA 3.0. The exact core query can be reproduced against
those pinned files without a parser dependency beyond Python's standard library:

```python
from pathlib import Path
import unicodedata as U
import xml.etree.ElementTree as E
ns = {"t": "http://www.tei-c.org/ns/1.0"}
terms = ("ⲣⲕⲟⲩⲓ", "ⲡⲧⲣⲁⲉⲓⲣⲉⲛⲧⲁϭⲟⲙ")
for p in sorted(Path("/tmp/pob-sahidic-ezekiel-search.tFdL3k").glob("105*.xml")):
    for v in E.parse(p).findall(".//t:ab", ns):
        raw = "".join("".join(w.itertext()) for w in v.findall(".//t:w", ns))
        s = "".join(c for c in U.normalize("NFD", raw.casefold())
                    if U.category(c) not in ("Mn", "Mc", "Me") and not c.isspace())
        for term in terms:
            if term in s:
                print(term, v.get("n"))
```

### External Coptic phrase controls

**Neither of the two returned external contexts supplies Hunt5's distinctive
sequence.** This bounded search uses the official
[Coptic Scriptorium corpus at a fixed commit](https://github.com/CopticScriptorium/corpora/tree/3ac067f1709a0012daf39ea8da2fac79980176a5),
not another pass over the preceding Ezekiel files. The
[compact receipt](../sources/textual_restoration/comparisons/ezekiel_external_coptic_phrase_screen.2026-10-14.v1.json)
records the exact selection recipe, query layers, counts, hashes and limits.

The selection comprises 374 TT archive members from Pentateuch and selected
prophetic collections, excluding Ezekiel, plus 211 monastic TT documents from
Shenoute, Abraham, Besa, Johannes, Pachomius and the Apophthegmata corpora.
Thirteen files flagged redundant were excluded; treebank and individual-book
duplicate exports were not added. This is not all OT or all monastic literature:
Malachi and other unselected books remain outside the screen. File counts do
not establish complete chapters or complete works. OT metadata declares
Crosswire/CoptOT sources and automatic annotations, not independent manuscript
confirmation; it also warns of possible verse/English misalignment.

Both the editorial normalized-token and original-spelling attribute layers
were searched: 585 documents and 404,209 tokens per layer. These are two
representations of the same inputs, not two witnesses. Casefolding, NFD and
removal of combining marks and whitespace precede within-document substring
retrieval; punctuation remains. The two distinctive queries are the same
`ⲣⲕⲟⲩⲓ` and `ⲡⲧⲣⲁⲉⲓⲣⲉⲛⲧⲁϭⲟⲙ` used above.

| Retrieved locus, in both layers | Actual contextual reading | Consequence |
|---|---|---|
| Apophthegmata 045, MONB.EG80 line 13, token u29 | `ⲣⲕⲟⲩⲓ ⲛϩⲏⲧ`, becoming fainthearted/cowardly amid trials, followed by grumbling | A different contextual sense, not numerical reduction through scattering |
| Shenoute, Uncertain Canons, XR470, chapter 1407 verse 3, tokens u1994–u1995 | `ⲃⲁϣⲟⲣ | ⲕⲟⲩⲓ`, little foxes | Removing the boundary creates the substring; this is not the verb `ⲣⲕⲟⲩⲓ` |

There are no exact power-phrase hits in either queried layer. This does not
exclude different spellings, formulations, missing text or unsearched works.
The AP metadata identifies Chaîne 1960 section 45 and BL Or.3581A(44) f.2r;
its supplied English agrees with the contextual distinction above. Shenoute's
metadata identifies Emmel's typed transcription of Amélineau, including the
latter's errata, and explicitly says the manuscript was not consulted for
chapter/verse division. These are published digital readings, not fresh pixels.

A parser defect was caught before final conclusions: monastic files put `orig`
on separate elements, whereas OT files put it on `norm` elements. The initial
original-layer pass therefore missed all 374 OT inputs. After correction,
the same cached inputs were rerun offline; root independently reproduced both
complete query layers and the unchanged two loci. This is why per-layer text
coverage is now explicit in the controlling method. Eleven monastic filename
stems also lack exact keys in aggregate metadata; their actual file headers
were checked, and all 211 selected monastic headers say `redundant="no"`.

Root verified all 585 input hashes, the exact selection recipe, and the pinned
Git object IDs for the metadata, archive and 211 monastic files. The two source
contexts and headers were read directly. The detailed acquisition receipt and
full texts remain private; the compact Git receipt preserves reproducible
upstream selection without importing the corpus. The OT archive declares
CC BY-SA 4.0 and the two hit files CC BY 4.0; other file-specific terms remain.

No donor or ancestral wording is established. Retain Hebrew and English; do
not turn this negative exact-string result into positive support for a lost
Hebrew plus. Retire these same queries on these same bytes. The next useful
input remains a distinctively matching passage with a demonstrated relationship,
or the missing continuous Greek transition/critical apparatus. ImageGen has
no evidentiary role in this text-only comparison.
