# Pentateuch source comparison — pass 3

Checked: 2026-09-04

The subsequent [Deuteronomy 32 43 assessment](DEUTERONOMY_32_43_SOURCE_COMPARISON_2026-10-04.md)
advances the plate-locator hold to a measured contextual native-image check,
evaluates concrete expansion and grammatical-updating accounts, and holds
whole-form priority while retaining WLC/main English provisionally. DJD XIV
remains unconsulted. The original pass below records its earlier scope.

## Outcome

The direct-Hebrew pass now reaches Deuteronomy 27:4 and 32:43. It also adds an
explicit distinction between a manuscript that supports a reading and a
manuscript that merely covers the verse while the decisive letters are lost.

- **Deuteronomy 27:4:** the Masoretic and Old Greek controls read Mount Ebal;
  the Samaritan Pentateuch reads Mount Gerizim. 4QDeutf (4Q33) contains the
  verse, but the whole mountain-name phrase is supplied inside a bracketed
  lacuna. It supports neither name.
- **Deuteronomy 32:43:** 4QDeutq (4Q44) preserves an unambiguously longer Hebrew
  form. The Old Greek is related but longer still, while the Masoretic and
  Samaritan controls preserve the shorter form.

No English main-text wording has been changed. Both cases remain
`not-adjudicated`; their POB notes now state the evidence more accurately.

## Pinned controls

The same reproducible controls used in the earlier passes were queried at their
pinned snapshots:

- the local POB WLC source field;
- DT-UCPH Samaritan Pentateuch 7.1.3 at commit
  `2f2120286ac48d4ff3d04e0107e33efd864aa9e1`;
- OpenScriptorium's Rahlfs LXX data at commit
  `c91f6b1e8fb3ba37df701e6ae31f675ace71a2b2` (the six stored Greek verses
  were rechecked byte-for-byte after the earlier recorded upstream object
  became unavailable); and
- QDR 1.1 at commit `f54f38464e18409eed8286fe24dd24f88d4735dd`,
  checked against versioned Qumran-Digital transcriptions and IAA manuscript
  identities.

The modern editions and transcription platforms are controls, not additional
physical manuscripts.

## Deuteronomy 27:4

| Evidence | Reading | Status |
|---|---|---|
| WLC/MT | `בהר עיבל` — Mount Ebal | supports Ebal control |
| Samaritan Pentateuch | `בהרגריזים` — Mount Gerizim | supports Gerizim control |
| Rahlfs LXX | `ἐν ὄρει Γαιβαλ` — on Mount Ebal | supports an Ebal Hebrew Vorlage as daughter-version evidence |
| 4QDeutf (4Q33), fragment 32–35, lines 6–7 | `ה[יום בהר עיבל ושדת או]תם` | **indeterminate lacuna** |

The brackets are decisive. They mark editorial reconstruction, not visible
letters. The record therefore says that 4Q33 covers the verse but cannot vote
for Ebal or Gerizim. This corrects a common methodological error: a supplied
word in a published transcript must not be converted into manuscript support.

Reports based on unprovenanced or private-market fragments are excluded until
an authenticated object and a stable scholarly publication clear the normal
evidence gates.

## Deuteronomy 32:43

4Q44, fragment 5 ii, lines 6–11, reads:

```text
הרנינו שמים עמו
והשתחוו לו כל אלהים
כי דם בניו יקום
ונקם ישיב לצריו
ולמשנאיו ישלם
ויכפר אדמת עמו
```

A close English rendering is: “Rejoice, heavens, with him; bow down to him, all
gods; for he will avenge the blood of his sons; he will return vengeance to his
adversaries and repay those who hate him; and he will atone for the land of his
people.”

This is direct Hebrew evidence for a longer ancient form. It differs from the
shorter MT/Samaritan form in at least five linked features: heavens rather than
nations in the opening, the command to all gods, sons rather than servants, the
repayment of those who hate him, and the closing construction “land of his
people.”

The Old Greek contains those broad features but is not identical. It adds
separate calls to the nations and to all angels of God. It is therefore wrong
to merge “4Q44 + LXX” into a single longer reading or count them as two copies
of one Hebrew manuscript.

The relevant fragment is visibly located on IAA image record B-280818, PAM
M42.164 (scanned infrared negative, recto). This is a plate-level locator, not a
stored image derivative or a measured region. It narrows the next verification
step without overstating what has been completed.

## English POB impact

- The marker on Deuteronomy 27:4 now sits at “Mount Ebal,” and its note explains
  both the Samaritan reading and 4Q33's evidentiary limit.
- The markers on Deuteronomy 32:43 now sit at the phrases they explain. Its
  textual note quotes the 4Q44 form and distinguishes the still-longer Greek.

The longer 32:43 form deserves formal adjudication and an English candidate,
but the current comparison package deliberately forbids a preferred reading or
canonical-change flag. Image verification and internal/external evaluation
come first.

## Next gates

1. Map the exact IAA image plate for 4Q33 and measured regions for 4Q33 and 4Q44.
2. Independently verify the visible letters, especially the joins and damaged
   characters in 4Q44, without treating supplied characters as ink.
3. Consult DJD XIV for the material reconstruction and editorial rationale.
4. Split Deuteronomy 32:43 into aligned variation units and test whether the
   shorter or longer forms better explain the multiple ancient editions.
5. Continue to Deuteronomy 32:8, then expand beyond the Pentateuch to Samuel,
   Jeremiah, Isaiah, and Psalms.

Machine-readable records are in
[`../sources/textual_restoration/coverage/pentateuch_pilot.v1.json`](../sources/textual_restoration/coverage/pentateuch_pilot.v1.json)
and
[`../sources/textual_restoration/comparisons/pentateuch_controls.v1.json`](../sources/textual_restoration/comparisons/pentateuch_controls.v1.json).

## Deuteronomy 27 4 Greek and Latin followup on October 6

Gerizim has Greek and Latin attestation beyond the Samaritan Hebrew control.
This closes a real coverage gap in the September comparison, but does not
resolve which mountain name is earlier. The original selected Rahlfs text is
an Ebal control, not evidence that every Greek witness reads Ebal. POB retains
its declared Hebrew and main English provisionally; no canonical file changes.

The [Giessen library's 1911 edition](https://digisam.ub.uni-giessen.de/ubg-ihd-adr/content/titleinfo/4820718)
provides Glaue and Rahlfs's actual transcription, conventions and historical
photographic plate. Printed 37 [journal 173], PDF page 13, column I lines 3–4,
prints the mountain form across the line break, with the iota supplied:
`αργαρ[ι] / ζιμ`. Printed 34 [170], PDF page 10 distinguishes full supplies,
uncertain partial letters and unidentified traces; modern word separation is
editorial. The complete Vorderseite plate, PDF page 4, locates the matching
upper-right half. This is a report-aware check of a published reading and
historical plate, not a new calibrated damaged-letter transcription. Printed
33 [169], PDF page 9 dates the parchment to V–VI CE, with the two editors
favoring different centuries; that is not the date of its underlying revision.

[Tov's revised author-uploaded argument](https://www.academia.edu/29064242/2_Pap_Giessen_13_19_22_26_A_Revision_of_the_LXX_RB_78_1971_355_83_and_plates_X_XI_Revised_version_Emanuel_Tov_The_Greek_and_Hebrew_Bible_1999_459_75),
especially printed 462–463 and 473–475, retains uncertainty in the opening
`ar(?)` and supplies `[i]`; one-word versus two-word writing is undetermined.
His lexical, syntactic and Hebrew-oriented revision comparisons support LXX
ancestry. He prefers a non-Samaritan revision preserving an older alternative,
but explicitly retains Samaritan adaptation of the LXX as a competing account.
LXX ancestry therefore does not establish independent Gerizim Hebrew priority.
The body text was consulted; its original PDF and plates were not acquired.

The [Lyon library's MS 1964 f.18r](https://florus.bm-lyon.fr/visualisation.php?cote=MS1964&folio=18),
column III lines 2–3, visibly reads `HODIE IN MONTE / GARZIN ET DEALBA…` in
continuous main text. The inspected complete-page JPEG is a 3000 × 3470
derivative, not the advertised 6328 × 7320 original. The applicable
[Robert 1900 edition, printed 30](https://books.google.com/books?id=MrLmAAAAMAAJ&pg=PA30)
likewise reads Garzin. Wevers identifies the Latin witness as 100, Lyon
403 + 1964, and dates it VII; the
[holding library catalogue](https://florus.bm-lyon.fr/description.php?cn=MS1964&saisie=florus)
normally dates it VI, with V entertained. Preserve this disagreement rather
than giving the object the date of the Old Latin translation.

Our inference is limited: VL100 attests Latin Gerizim compatible with a
Gerizim-bearing Greek lineage. Adjustment within Greek or Latin transmission,
including harmonization with 27:12, remains possible. Samaritan Hebrew,
Giessen Greek and this Latin copy are not three independent Hebrew votes.
4Q33's wholly supplied mountain remains neutral; private-market fragments stay
excluded. The existing Joshua Ebal altar parallel is literary context, not
another manuscript of Deuteronomy.

Gerizim would change the designated location of the stones and, in the following
verse, the altar. That is a consequential geography and worship-history question,
not a demonstrated mandate to change doctrine. Both earlier-Gerizim alteration
and later-Gerizim adjustment remain live explanations. Reopen priority for a
discriminating transmission argument or fuller local apparatus, not repeated
model agreement. A reader-note extension could disclose these controls separately
after an exact-record application review; none is applied here.

The [bounded evidence record](../sources/textual_restoration/comparisons/deuteronomy27_4_greek_latin.2026-10-06.v1.json)
pins the acquisitions and unchanged target. Full consulted materials remain
private. This is expanded comparison of known evidence, not a novel reading,
exhaustive Greek/Latin collation or a canon recommendation.

### Subsequent mountain name disclosure application

POB's note now names the selected Rahlfs Ebal control, Samaritan Gerizim,
published Giessen Greek reading with its supply/uncertainty, and Old Latin
VL100 Garzin. It preserves the wholly reconstructed 4Q33 mountain and states
that witness relationships and earliest priority remain uncertain. Hebrew and
main English are unchanged. The connected rationale describes Ebal as provisional
base retention rather than a demonstrated historical preference.

The [exact application receipt](../sources/textual_restoration/applications/deuteronomy27_4_disclosure.2026-10-06.v1.json)
pins the complete candidate and archives five prior inputs, without attributing
new approval to historical model scores. One bounded application critique found
no blocker. Schema preflight and the actual complete Deuteronomy exporter cover
34 chapters and 959 verses; only 27:4 differs. The installed YAML and complete
export match the frozen candidate and preflight hashes, and the footnote audit
is ok. Active status remains draft/needs_review; no source-priority vote,
specialist certification, novel reading or deployed-reader verification follows.
