# New Testament pilot: Mark 1:41

Checked: 2026-09-02 · Method 1.0.0

Current evidence continuation: [direct CBGM acquisition](#mark-1-41-direct-cbgm-evidence-2026-10-05).
The version-1 preference below is historical; the later acquisition does not
change the canonical Greek or English or certify version-2 compliance.

Generated from the [decision dataset](../sources/textual_restoration/decisions/nt_pilot.v1.json). These are working editorial choices from published readings, not new image restorations, cross-model-reviewed decisions, or published POB changes.

Older witnesses receive a modest preference; no numerical vote or authenticity percentage is used.

## Mark 1:41

**Working preference:** Provisionally prefer compassion; retain anger as a serious alternative to the current POB wording.
**Priority confidence:** moderate (editorial judgment, not a probability).
**Wording-level outcome:** provisional selection within this unit.

| Candidate | Greek excerpt | English effect |
|---|---|---|
| anger | ὀργισθείς | being angry |
| compassion | σπλαγχνισθείς | moved with compassion |

### Witness matrix

Every non-local row below is a published report; archival pixels were not independently re-read in this pass.

| Witness | Language / role | Reported reading | Date basis | Related evidence group | Source |
|---|---|---|---|---|---|
| Current POB / SBLGNT | Greek / critical-edition | being angry | edition-publication: 2010 edition; not an ancient manuscript | modern-editorial-decision | local-baseline |
| Codex Sinaiticus / 01 | Greek / direct-language | compassion | physical-copy: Fourth century CE | early-greek-compassion | bruehler-2024 |
| Codex Vaticanus / 03 | Greek / direct-language | compassion | physical-copy: Fourth century CE | early-greek-compassion | bruehler-2024 |
| Codex Bezae / 05 | Greek / direct-language | anger | physical-copy: Fifth century CE | bezae-latin-related | bruehler-2024 |
| Old Latin D/I families, as reported | Latin / ancient-version | anger | translation-tradition: Ancient Latin evidence; individual copies not dated in this pilot | bezae-latin-related | bruehler-2024 |
| Ephrem, commentary on the Diatessaron | Syriac / retelling | Combined compassion/anger language reported | work-composition: Fourth-century work, not a fourth-century surviving copy | diatessaron-reception | bruehler-2024 |

Baseline: [translation/nt/mark/001/041.yaml](../translation/nt/mark/001/041.yaml).

- **Why prefer it:** Earlier extant Greek support and broader transmission favor compassion. This is not a count of modern editions.
- **Strongest objection:** Anger is a difficult but contextually plausible reading that could have been softened; Bruehler argues for it despite the external balance.
- **Transmission explanation:** The direction of change remains disputed. External convergence presently outweighs the harder-reading argument; no specific copying mechanism is claimed as proven.
- **Effect of age:** Fourth-century Greek witnesses modestly favor compassion over the surviving fifth-century Greek anger witness. The Latin and Syriac evidence means anger cannot simply be dated to that later copy.
- **Independence caution:** Sinaiticus and Vaticanus can share ancestry. Bezae and related Latin families are not independent votes; commentary is a separate, imperfect evidence type.
- **Publication decision:** Stage compassion as a working alternative for further review. POB still says angry; no automatic canonical replacement.

Still unresolved:
- Inspect exact manuscript regions and correction layers before declaring an image-verified result.
- Compare ECM evidence directly and evaluate the competing internal arguments, including the cited Williams and Johnson studies.

### Direct ECM access check — 2026-09-06

The [INTF database directory](https://www.uni-muenster.de/INTF/datenbanken/index.html)
links [Mark Phase 3.5](https://ntg.uni-muenster.de/mark/ph35). Its public
[application metadata](https://ntg.uni-muenster.de/api/mark/ph35/application.json)
returned `name: Mark Phase 3.5` and `read_access: public`. This identifies the
comparison application, not a passage reading or an ECM publication revision.
The NTVMR ECM page and the Mark application did not render a usable apparatus
in the inspected browser state. Direct passage lookup attempts returned HTTP
500; the cause, including possible parameter mismatch, was not established.
No Mark 1:41 witness list, correction layer, local stemma or editorial decision
was retrieved. Do not cite this access check as consulted ECM evidence for
either reading or as confirmation of the provisional preference above.

The bounded attempt stops here. Do not repeat these failed lookups without a
working passage locator or documented parameter correction. Existing published
arguments remain available for further adjudication; the current POB source
and English and the version-1 decision dataset are unchanged.

Not used to force a result:
- SBLGNT/WH/NA/RP edition agreement is not manuscript corroboration.
- Combined commentary language is not treated as an exact two-word reading of Mark.

## Mark 1 41 direct CBGM evidence 2026 10 05

The earlier access blocker is removed. The
[frozen acquisition](../sources/textual_restoration/controls/mark1_41_ph35.2026-10-05.v1.json)
preserves five complete public responses with byte hashes: application,
passage, Greek apparatus, verse guide and local stemma. These are published
database readings and editorial relationships, not fresh manuscript pixels.
**Compassion remains a defensible working preference; hold canonical replacement
pending the specific transmission comparison below.** This pass completes
acquisition and comparison of this Greek table, not the full ECM apparatus.

### Working locator and observed readings

The application is Mark Phase 3.5. Its suggestions give book siglum Mc and
the grouped variant at words 2–10, not an isolated word 4. The latter returned
HTTP 500; using the observed group succeeds. The
[working passage request](https://ntg.uni-muenster.de/api/mark/ph35/passage.json/?siglum=Mc&chapter=1&verse=41&word=2-10&button=Go)
returns passage 299, address 20141002–10. This diagnoses the present lookup
failure, not every historical failed request or the server's underlying bug.

The [Greek table](https://ntg.uni-muenster.de/api/mark/ph35/apparatus.json/299)
distinguishes seven readings, including changes to the opening subject and
word order. Reading a has `και σπλαγχνισθεις εκτεινας την χειρα`;
b instead has `και οργισθεις εκτεινας την χειρα`. Named witnesses 01, 03
and 892 have a; 05 has b. Alexandrinus is 02 and has d, which retains compassion
but changes the opening. The row A is the reconstructed initial text, not
Alexandrinus; MT is a virtual Byzantine-text control, not another physical copy.
These identifications are checked against the
[pinned application source](https://github.com/SCDH/intf-cbgm/blob/80dfd03cf4f103d572ab0c58bde96ff49b690399/scripts/cceh/cbgm.py#L34)
and insertion of A/MT separately from named witnesses.

The response has 211 rows: two virtual controls and 209 named rows. Thirty-seven
are labeled zz (lacuna), and two have alternative assignments: 0130 c/d/g
with much of its participle supplied, and 33 a/d/g. API certainty numbers
describe assignments, not calibrated probabilities of earliest wording. Other
compassion forms must not be counted as exact a readings, nor all assigned text
treated as surviving ink. This table has only 05 at b; that is not an exhaustive
census of every Greek copy, Latin witness, quotation or correction hand.

### What the editorial stemma does not prove

The [local stemma](https://ntg.uni-muenster.de/api/mark/ph35/stemma.dot/299)
has initial-root to a, unknown-origin to b, a to d/f and d to c/e/g.
It therefore selects compassion but does not give b a demonstrated ancestor
in a. The initial text is an editorial hypothesis, not an additional witness.
The source's preparation comments explicitly distinguish its first-hand CBGM
data from corrections and alternative readings. No complete correction-layer
or version/patristic apparatus was acquired here; the verse-guide lemma alone
does not prove all printed ECM edition details.

### Contrary transmission explanations and the next evidence

Root and one bounded source assessor consulted accessible publisher abstracts
and author notes, not complete article PDFs. In
[Johnson 2017](https://www.cambridge.org/core/journals/new-testament-studies/article/abs/anger-issues-mark-141-in-ephrem-the-syrian-the-old-latin-gospels-and-codex-bezae/2000B008216E68452F69AF345A0BFD21),
the abstract challenges Ephrem as independent anger evidence and links the
Greek anger witness to geographically restricted Latin transmission. Note 68
proposes Latin parablepsis between compassion and anger forms. This is a copying
hypothesis, not an observed event; Greek–Latin association does not establish
the direction of influence.

[Bruehler's newer reassessment](https://www.cambridge.org/core/journals/harvard-theological-review/article/abs/presence-nature-cause-and-result-of-jesuss-anger-in-mark-14045/E917B884E0E93A7CA7BEEAA8AC3EA22E),
published online 19 January 2026, supplies a serious countercase. Its abstract
fits anger to the tension between healing publicity and Jesus's preaching
priority. Note 18 challenges linguistic-consistency assumptions about Ephrem
through the edited Syriac and Armenian commentary traditions. Note 4 criticizes
Williams's proposed accidental Greek change; Williams's full argument was not
read directly here. Contextual coherence and a possible smoothing of anger
remain arguments, not proof that anger preceded compassion.

The discriminating next unit is Ephrem's commentary 12.21–24: establish exactly
what is quotation, exposition of 1:43's rebuke, or evidence for 1:41, with Syriac
and Armenian transmission layers kept separate. Only then assess the proposed
Latin-to-Greek pathway using local copying behavior. Do not force a change
because anger is harder, or compassion is more widespread. The exact Greek
acquisition improves evidence coverage but does not settle these explanations.

Current Mark YAML remains `c9483350a31b7d9c23324bdd74fbebde9a6c86443d248ae55001ed57f566bcfd`;
the historical decision dataset remains
`864d21e03ef027a5c41734a879cfa737396b1b4061f709144be1ee5a41ec553e`.
Actual offline checks verify all five response hashes, label counts, witness
assignments, exact stemma edges and unchanged output pins. There is no new
reader application, novel decipherment, ImageGen evidence or publication approval.
One independent acquisition/documentation critique passed those recorded facts,
pinned software semantics and the publisher summaries. Its live API recheck
failed, so its locator verification used the preserved response rather than
independent live retrieval. It did not certify historical priority or full coverage.

## Sources

- **bruehler-2024:** [B. B. Bruehler, study of the anger/compassion variant in Mark 1:41](https://theo.kuleuven.be/apps/press/theologyresearchnews/files/2025/09/Bruehler.pdf) — Ephemerides Theologicae Lovanienses 100/2 (2024), pp. 213–230; external evidence on p. 214; DOI 10.2143/ETL.100.2.3293342.
