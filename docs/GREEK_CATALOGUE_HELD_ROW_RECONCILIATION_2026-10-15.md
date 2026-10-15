# Greek catalogue: all 73 held rows reviewed

## Result and scope

The [October 12 catalogue screen](GREEK_CATALOGUE_CENSUS_SCREEN_2026-10-12.md)
left 73 of its 198 structured content rows unclassified by a deliberately
strict parser. This follow-up reads all 73 rows in context. It adds **45
book–catalogue navigation pairs**, giving all **39 POB OT books** at least one
route in this bounded cohort. These are not 45 new manuscripts, newly collated
passages, or proof of complete witness coverage.

The [reviewed overlay](../sources/textual_restoration/discovery/greek_catalogue_held_rows.2026-10-15.v1.json)
preserves every held row's catalogue ID, zero-based ordinal and exact row hash,
with all 11 original HTML input pins. The original 1,687-ID list, 53-detail
cohort, strict parser and 125 original classified rows are unchanged. All
classifications below concern catalogue content, not observed manuscript ink.

| Classification | Rows | Treatment |
|---|---:|---|
| OT book navigation | 19 | Explicit labels, named subcomponents or individually checked context; mixed-content qualifications retained |
| Odes excerpts | 1 | Separate quotation leads; not extra continuous-book witnesses |
| Expanded-corpus works | 26 | Separate work identities, not automatically mapped to the 39-book OT |
| Other Christian works | 4 | Clement and Hermas collection contents, not NT manuscript votes |
| NT material | 8 | Separate NT track; component dates still matter |
| Mixed NT/other material | 2 | Do not inherit an unrelated OT book label |
| Paratext | 10 | Flyleaves, contents, introductions and prologues, not continuous biblical text |
| Unresolved labels | 2 | No silent correction of Kingdoms or Esdras numbering |
| Unidentified miscellaneous material | 1 | No invented biblical identification |
| **Total** | **73** | All original held rows accounted for |

## Consequential corrections

The [Alexandrinus](https://septuaginta.uni-goettingen.de/catalogue/Ra_A/)
and [Vaticanus](https://septuaginta.uni-goettingen.de/catalogue/Ra_B/)
Twelve-Prophets rows explicitly enumerate all twelve books in their notes.
Those notes supply navigation omitted by the strict content-prefix parser.
The [Sinaiticus](https://septuaginta.uni-goettingen.de/catalogue/Ra_S/)
Joel–Malachi range explicitly uses Greek order: it routes Joel, Obadiah,
Jonah, Nahum, Habakkuk, Zephaniah, Haggai, Zechariah and Malachi, **not** Hosea,
Amos or Micah. The A/B lists provide the relevant order within the same snapshot.

The A/B Jeremiah-corpus notes distinguish Jeremiah and Lamentations from
Baruch and the Epistle of Jeremiah. Only the two named OT components enter the
39-book navigation layer; the entire collective row is not relabeled Jeremiah.

Greek II Esdras supplies Ezra–Nehemiah navigation in A26, B13 and S9. Root read
the publisher introduction's [Probleme des Buches and Esrabücher sections](https://www.die-bibel.de/bibel/LXX/EZR.10?ebc=true&scrollPositionRestoration=disabled&slug=esra-nehemia),
which explicitly distinguish the joint work from first/alpha Esdras and later
Ezra apocalypse nomenclature. [WiBiLex section 4.1](https://www.die-bibel.de/stichwort/28417/)
corroborates the book identification. This is a book-only crosswalk: no chapter
or verse conversion, or equivalence with POB's appendix “2 Esdras,” follows.
A25 is classified separately as Greek I Esdras. B12's reported III Esdras
label remains held, as does A13's malformed IIV Kingdoms label.

[Ra907](https://septuaginta.uni-goettingen.de/catalogue/Ra_907/)'s numeric-only
verso row can be routed to Genesis from its explicit general description and
Genesis recto. [Ra2029](https://septuaginta.uni-goettingen.de/catalogue/Ra_2029/)'s
eight numeric-only rows can be routed to Psalms from its explicit general
description. This does not authorize generic inheritance of the preceding book:
Ra912's explicitly identified letter/Hebrews row is not Genesis merely because
the object also contains Genesis material. No Psalm numbering conversion occurs.

## Component dates and textual function

[Ra1054](https://septuaginta.uni-goettingen.de/catalogue/Ra_1054/) is a composite
collection. Its Greek-Latin Psalter component is catalogued as **tenth century**,
with Greek represented in Latin characters. The older Latin Gospel component
does not make that Psalter an early Greek witness. Reported possible dependence
on Ra1037 is a research lead, not a verified stemma or independent vote.
Its miscellaneous-fragment row remains unidentified. Vaticanus's catalogue
also expressly assigns Revelation to a fifteenth-century supplement, GA1957;
the containing codex's early date must not be transferred to it.

Alexandrinus's Odes row combines OT excerpts, additions, NT canticles and other
material. Seven OT book leads are retained in a separate excerpt field, not
added to the continuous-book navigation counts. Ra1219's mixed Psalms/Odes
row supplies a Psalms route, but Psalm 151, the first Ode and later replacement
leaves retain their own alignment and layer questions. Collection membership
alone does not decide which texts should belong to a biblical canon.

Two physical-range anomalies remain explicit: A's Wisdom overview starts at
a folio inconsistent with its superscription note; B's Gospel overview ends
before the fuller range in its note. Book identity can be retained without
pretending to have repaired either physical locator.

## Reproduction, review and next work

The [verifier](../tools/textual_restoration/greek_catalogue_reconciliation.py)
checks exact held-row coverage, original input identities, roles, counts and
derived book navigation. With `--verify-private-inputs`, it additionally checks
all 11 HTML byte hashes, public access flags, embedded IDs and all 73 row hashes.
This mode passed against the retained original inputs. Ordinary CI requires
only committed artifacts; it cannot independently reread private catalogue
pages or establish the truth of a manual classification.

Root and one independent agent read all 73 held rows and relevant context.
The agent separately verified all 11 source hashes and the publisher's Esdras
introduction. Its WiBiLex follow-up timed out, so that corroborating passage is
root-only consultation. No full PDF or full bibliography was read for this
follow-up. The source and classification review is not a new textual-priority
vote, and reverse presentation or repeat tests are not extra witnesses.

The frozen source pages remain private under their recorded CC BY-NC-SA terms.
Only factual identifiers, classification, hashes and original analysis are
added to Git; catalogue prose, manuscript images and transcriptions are not
relicensed. A first local extraction assumed filenames followed padded `rid`
values and stopped at Ra0907. Joining by the recorded URL corrected that lookup;
no catalogue record was merged or omitted to make the run pass.

Remaining breadth work includes the seven narrative-only descriptions, the
five cave controls missing from the public list, the wider catalogue's other
1,634 detail records, and cross-catalogue identity reconciliation. The three
unresolved rows here need actual identification controls. Passage survival,
textual independence, material restoration, Hebrew retroversion and English
impact remain separate steps. No source, translation, registry object count,
ImageGen evidence or canon decision changes in this overlay.
