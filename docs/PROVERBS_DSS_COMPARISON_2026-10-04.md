# Proverbs scroll comparison and English consequences

Checked 2026-10-04 against main revision
`ed2ac2fcb73d68aa6ae852faa3f98b9d42b83a24`. Published-source comparison, not new
image restoration or complete all-source Proverbs collation. PR #3's earlier
method/Nahash work is merged; this pass extends actual OT comparison coverage.

## Scope and sources

Root read all eight published 4Q102 line records and compared the current
source/English at 1:27–33 and 2:1. One bounded agent read all 38 published 4Q103
line records and compared 39 current POB records: 13:6–9; 14:5–13,31–35;
15:1–8,19–31. This is divided work, not independent replication of every line.
Total: 46 published line records and 47 corresponding POB contexts; ranges
include supplied text, not 47 completely preserved ancient verses.

The versioned [4Q102](https://lexicon.qumran-digital.org/transcriptions/4Q102/2026-05-21/index.html)
and [4Q103](https://lexicon.qumran-digital.org/transcriptions/4Q103/2026-05-21/index.html)
pages are attributed to the DFG Qumran-Digital project, using earlier project
texts; they declare CC BY-SA 4.0. They are modern published transcriptions, not
fresh readings of manuscript pixels. Square brackets, uncertainty marks,
unassigned scraps and editorial Add PAM annotations remain distinct from ink.
Neither a reference tag nor a familiar restored phrase establishes survival.

The existing book map has three QDR labels, including **4Q103a**. Its existing
[identity hold](QUMRAN_CATALOGUE_IDENTITY_FOLLOWUP_2026-09-05.md) remains: it is
not presumed absent or equal to 4Q103. The guessed versioned page was inaccessible
in this pass; no new identity assignment follows. The 46-line result excludes
that unresolved record and is not a complete Proverbs manuscript census.

Root and the reviewing agent inspected Michael V. Fox, *Proverbs: An Eclectic
Edition with Introduction and Textual Commentary* (SBL, 2015), complete printed
pp. 19,92,229,242–243 / PDF pp. 41,114,251,264–265. The
[publisher PDF](https://www.sbl-site.org/wp-content/uploads/2024/11/Proverbs_Fox_SBL.pdf)
has SHA256 `1953e00d7275c1bda5031378b347fba65348bc08855ec0f8757841ca6cdc1c39`,
matching the earlier Proverbs 8:16 consultation. Text extraction located pages;
Poppler renderings established the actual printed arguments and qualifiers.
The web fetch returned 403; ordinary direct download succeeded. The full PDF
remains private, outside Git. No access bypass, purchase or new lexicon access.

## Consequential differences and decisions

| Passage and published locator | Difference and English consequence | Decision and limit |
| --- | --- | --- |
| 1:32; 4Q102 frg.1–2 line33 | מושכת against WLC משובת, underlying POB's turning away. An alternative cannot be treated as a new synonym of the base word. | Retain the base provisionally. Fox argues for letter confusion plus transposition, not a new meaning. An intentional alternative is not disproved, but a secure interpretation and transmission argument are missing. |
| 14:34; 4Q103 frg.5–7i+8–10 line4 | Published וח֯סר against וחסד; lack/diminution differs from the retained rare disgrace sense. | Retain source/main English; disclose the alternative and disputed letter. Fox says the resh is damaged and dalet possible. The online transcript's unmarked resh does not settle that disagreement. |
| 15:28; 4Q103 frg.7ii+11–14 line10 | Published [לב] צדיק לענות lacks יהגה, the verb behind POB's considers how to answer. | Retain the verb provisionally. Fox flags the omission uncertain and regards the verb as essential. Do not turn a shorter published line into certified physical absence or supply ready as observed wording. |

The online 14:34 transcription marks the het uncertain but not the resh. The
agent initially treated the final letter as securely unbracketed; after the
critical-edition check it corrected that assessment. These are different
editorial preservation judgments, not two ancient witnesses. A fresh claim
settling the glyph would require the named edition/plate and image gate.

Fox reports Greek and Syriac support for a diminution reading at 14:34, but
retains the base as the better sentence. Translation, alternative vocalization
and a different consonant must not be collapsed into one claim. Root's additional
WLC controls at Leviticus 20:17 and Proverbs 25:10 show negative shame language
is not invented just for 14:34; they do not prove this verse's earliest wording.
The strongest contrary case is early versional meaning fitting a resh reading;
the decisive Hebrew glyph and direction of transmission remain unresolved.

At 15:28 Fox's Greek control retains meditation with a different object;
it is not a verbatim copy of the Hebrew or an independently collated codex.
The shorter form might be a copying omission, while the longer form might
clarify an elliptical expression. Neither mechanism was observed. Current
English remains appropriate to the retained source, not a translation of the
shorter scroll form. At 1:32 Fox p.19 assigns the reading to 4QProva, while
p.92 labels it 4QProvb; preserve this attribution discrepancy, not another
manuscript vote. The direct versioned locus is 4Q102.

Other aligned material revealed no additional clearly consequential consonant
difference in this bounded screen. Spelling variation is retained without
inventing a meaning change; 4Q103 frg.15's two scraps are unaligned. The
edition's supplied comparative cross-references are not another witness lane.

## Reader disclosure and application scope

One separate agent inspected all five critical-edition page renderings and
approved an exact 14:34 disclosure proposal, conditional on preservation,
schema and export checks. It also corrected its initial resh assessment.
This was not blind transcription, a two-family benchmark, earliest-source
approval or a whole-verse translation endorsement.

The approved append to the existing note is:

> A published Qumran transcription reads a different word related to “lack,” but the decisive letter is disputed. Greek and Syriac readings have also been interpreted this way. POB provisionally retains the Masoretic wording.

The existing lexical explanation and note anchor remain intact. The reason
becomes textual_variant; old cross-check, revision-pass and source-audit objects
are archived verbatim, and active state becomes draft/needs-review. Source,
main English, lexical/theological decisions and revision history are unchanged.
The [application receipt](../sources/textual_restoration/applications/proverbs14_34_disclosure_2026-10-04.v1.json)
records actual verification and the scoped review; local application does not
establish public deployment.

## Reproduction and stopping conditions

Baseline SHA256 pins:

- 1:32 YAML: `6d65a3c714390c8e417c8f5ba84a5703458bfd2675d69c0dcf9b7f5b1a9fb8df`.
- 14:34 YAML: `0b0f0622eaf7ec26059cedf5a82752b19006b02e1a792e2b3ea098a9c2e465bd`.
- 15:28 YAML: `869933c741444c99887911434d167fab8448c88a0344dcc649a227ab355ebd43`.
- `Prov.xml`: `964f99c00239b53b854c4686c99490c8d1ac7664784a30afdfc23781a3abb161`.
- Book-file manifest: `9deb03bc2e41b43a129d65c4e3532315cf2204a6499e9cfb4cad7744ee219f62`,
  SHA256 of the exact UTF-8 output of `shasum -a 256 translation/ot/proverbs/*/*.yaml`
  from the repository root, before application.

Reopen 14:34 for decisive glyph/edition evidence or a discriminating versional
argument; reopen 15:28 for physical-line/edition evidence addressing the uncertain
omission; reopen 1:32 for a viable competing interpretation or new scribal
evidence. Do not repeat the completed published-page or Fox acquisition merely
to obtain agreement. The 4Q103a identity lane remains separate. No ImageGen,
fresh decipherment, complete book apparatus or new validation framework.
