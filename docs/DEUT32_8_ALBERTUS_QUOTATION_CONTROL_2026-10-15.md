# Deuteronomy 32:8: Albertus's Septuagint attribution

Current-state clarification: the baseline WLC/Israel statements and hash below
describe this check's original input, not today's canonical verse. The later
[reviewed application](DEUT32_8_CRITICAL_SOURCE_APPLICATION_2026-10-15.md)
provisionally adopted a POB-critical Hebrew composite and English “sons of God.”
That application is on main; this quotation control did not independently
authorize it. The current verse hash is
`f815dcd72c3f4372cca011eb8824d4791ec94c3432b9d2c0756a3f4862a49755`.

**Result: the cited printed edition really does attribute a Latin “sons of
God” quotation to the Septuagint at this locus.** This upgrades the Albertus
item from Hansen's report to directly consulted printed evidence. It does not
identify a Greek exemplar, establish independence from other Latin authors,
or authorize a Hebrew or English change.

## Actual source and context

The [University of Waterloo Alberti Magni e-corpus catalogue](https://www.arts.uwaterloo.ca/~albertus/Downloading.html)
links Borgnet, *Opera omnia*, volume 27 (Paris, 1894), *Super II Sententiarum*.
Root acquired its [scanned edition](https://www.arts.uwaterloo.ca/~albertus/PDFs/Borgnet-volumen%2027.PDF)
and visually inspected the work-title page and complete printed pages 37–39
(PDF pages 38–40). These contain article XIII from its heading through the
solution and replies. The rest of the 792-page PDF was not read; printed p.44
was only a page-numbering probe. The work-title page itself does not print an
edition date; the catalogue supplies that identification.

On printed p.38, left column, initial argument 5, the edition reads:

> secundum translationem Septuaginta: «Statuit terminos populorum juxta
> numerum filiorum Dei».

The preceding reference explicitly identifies Deuteronomy 32:8. Footnote 1
contrasts the Vulgate's *filiorum Israel*. That is an editorial comparison,
not a second manuscript reading observed by this project. No Greek wording,
codex identifier, hand, date of exemplar or statement of personal inspection
appears in this passage.

Article XIII asks whether rational soul and angel belong to the same species.
Argument 5 appeals to their shared perfection in grace and glory, using the
Deuteronomy quotation. The subsequent *Sed contra* and *Solutio* oppose the
same-species conclusion; the solution says they differ in species. Thus the
opening inference must not be presented as Albertus's settled conclusion.
Conversely, rejecting that inference does not erase the recorded quotation
or prove rejection of its biblical wording.

Root and one independent source checker also read the complete article XIII
in the [Magister Sententiarum digital Latin text](https://www.magistersententiarum.com/ouvrages/albertus-magnus/liber-ii/distinctio-i).
Its decisive wording and attribution agree with the scan, with ordinary
orthographic/presentation differences. The checker verified the digital
argument/solution distinction; only root inspected these printed pages.
This is two presentations of edited Albertus, not two independent ancient
witnesses or a medieval manuscript collation.

## Consequence for source selection

The prior [Latin-quotation review in PR216](https://github.com/zackseyun/peoples-open-bible/pull/216)
verified Aquinas's unnamed alternate reading and left Albertus reported-only.
The present check supplies the stronger **local attribution to the Septuagint**.
It warrants including Albertus as attributed quotation evidence. It neither
proves nor disproves a Greek antecedent with the complete divine-son phrase.

Possible transmission through Latin translations, excerpt collections,
commentaries or paraphrase remains unexcluded. Quotation agreement and an
attributed version name do not establish separate Greek exemplars. The date
of Albertus's work is not the date of an inspected manuscript; the observed
printed witness here is the nineteenth-century edition. Neither it nor its
modern digital presentation should be counted as newly recovered Hebrew.

At this check's historical baseline, the
[Deuteronomy evidence triage](DEUT32_8_EVIDENCE_TRIAGE_2026-09-06.md)
retained canonical WLC/“sons of Israel,” with a
note acknowledging the likely earlier divine-being reading and debate over
its precise Hebrew. This Latin control does not choose אל versus אלהים,
resolve 4Q37's possible adaptation, or fill Fouad 848's missing complement.
No current translation, note or confidence score changes.

## Earlier edition control: Jammy 1651

The [Waterloo catalogue](https://www.arts.uwaterloo.ca/~albertus/Downloading.html)
also supplies [Jammy volume 15](https://www.arts.uwaterloo.ca/~albertus/PDFs/Jammy-volumen%2015.pdf).
Its actual title page identifies *Commentarii in II. et III. lib. Sentent.*,
Petrus Jammy, volume XV, Lyon, 1651. Root and one acquisition agent independently
read the target article in that scan. Printed p.22, column a, continues
argument 5 with:

> secundum translationem. 70. Statuit terminos populorum iuxta numerum filiorum Dei.

Long s and line breaks are normalized here. The preceding reference gives
Deuteronomy chapter 32, without Borgnet's verse number. **Jammy prints the
numeral 70, not the expanded word Septuaginta.** Both the divine-son wording
and the local version attribution therefore predate Borgnet's 1894 edition.
The scanned article contains no target-specific Greek text, manuscript siglum
or variant apparatus. Its argumentative structure agrees with the later print:
the final solution rejects the initial same-species inference.

This excludes a narrowly defined possibility: introduction of both elements
for the first time by Borgnet. It does not prove the quotation's medieval
manuscript form, direct access to a Greek exemplar, or independence among Latin
authors. Waterloo explicitly identifies Jammy as the basis/model of Borgnet;
these editions must not count as two independent historical votes. The
transmission through a Latin intermediary remains possible. POB's separately
reviewed Hebrew/English selection is unchanged.

The PDF has 493 pages/spreads and 131,481,891 bytes; SHA256
`9cc496afed0a408c525173dab3ced41205d3fb5f480e206ee1fb49059d0e98fd`.
The title is on PDF page 2. PDF pages 25 and 26 show printed pp.20-23;
the complete article XIII occupies printed pp.21-22. Root inspected the full
spreads, then separate page views for legibility; the agent inspected the title
and complete target article independently. No whole-volume reading, manuscript
image recovery or new ancient reading is claimed. The scan stays outside Git.

The initial Borgnet recheck in this continuation was redundant: the older
triage still named it as next work despite this completed report. That repeat
is not new evidence. The triage, priorities and application-status links now
distinguish completed checks, historical baselines and the actual current verse.
Future work must first search the case reports and verify the canonical record
before acquiring a source named in an old queue.

## Efficient stopping boundary

The specific Albertus attribution and pre-Borgnet edition checks are complete.
Do not reread them or tally more authors as independent votes. A further Latin
investigation must test transmission: an actual medieval manuscript, an identifiable
intermediary, or a primary locator for the still-unverified Anselm claim.
Such work could change the weight of this quotation tradition; it is not a
prerequisite for every future provisional Hebrew editorial decision.

This is evidence about the transmission of a biblical verse, not grounds for
adding a book to a canon. ImageGen was not used; generated letters would add
no evidence to this legible printed-text comparison. The broader OT census,
restoration evaluation and source/English adjudication remain incomplete.

## Acquisition receipt and implementation boundary

Input main: `c6c7d93ea4d24ec9ad7fc22d2df6b34d83c25ac1`.
Canonical Deuteronomy 32:8 remains byte-for-byte unchanged, SHA256
`1caf32ddf68b552d662a94cff90970e5eacd9028ac0a4b8c89228634b14702af`.

| Private input | SHA256 |
|---|---|
| Borgnet volume 27 PDF; 181689808 bytes, 792 pages | `c5c8c7751163b75acb02214ffc6b2022214b28688bbc9b1f0784f777ea448ba4` |
| Printed p.37 render | `e56ab5f45c7cbfe37b1d4833718de28c9fc955714963f2546686bf0776f6069e` |
| Printed p.38 render | `02ef58614524e9419e34e39b7261f5567ec2b0cda999a44ee0f2963d0185698c` |
| Printed p.39 render | `1ca7c50efce147ec1ff2b3e62bd8e8a96f93f9cb775a340c1ca0cb879bea0f02` |
| Digital distinction-I HTML | `076a8d38e4090a4105bf213faa42dd7ade15f8b800b6379b26206e3f14138ae7` |

The PDF has no extracted text in the sampled pages; visual reading, not absent
OCR matches, establishes the passage. Renders used Poppler at 1800-pixel maximum
dimension. Files remain outside Git. Waterloo describes the old editions as
freely redistributable; no full text or image is nevertheless imported or
relicensed here. Hashes identify bytes, not source priority.

A bounded consistency check passed the digital quotation, attribution,
argument/solution distinction and inference limits. Its scope excludes root's
printed-page, footnote, acquisition and canonical-state checks. It is not a
second manuscript witness or a vote certifying original Hebrew wording.
