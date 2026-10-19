# Jeremiah number shifts and royal address controls

Greek singular wording at Jeremiah37:18 is not forced by Greek grammar or by
addressing one king. Other checked passages retain mixed number, including a
plural command addressed to Zedekiah. Some also differ from WLC in individual
verbs. These controls narrow a general smoothing explanation without proving
whether the target change originated in Hebrew or Greek. Retain the
[royal-agency comparison's](JEREMIAH_38_ROYAL_AGENCY_2026-10-19.md)
historical HOLD and current POB wording; no reader change follows.

## An annotation screen rather than an automatic profile

The pinned OSHB/WLC Jeremiah XML has52 chapters and1,364 verse elements.
A first scan for mixed singular/plural finite masculine second-person verbs
returned20 candidate verses, mostly quotation/addressee changes. It misses
37:18 itself: that verse's singular address occurs in suffixes, not a singular
finite verb. Its23:36 candidate also exposes an annotation mismatch: תזכרו is
tagged `HVqi2ms` although its written form is plural. No Hebrew text or upstream
annotation is changed here.

The revised retrieval criterion, fixed before checking its Greek controls, is
a verse containing a masculine second-person singular pronominal suffix and
a masculine second-person plural finite verb. It returns13 annotation hits,
including another false positive:25:27's ביניכם is tagged `Sp2ms` despite its
plural suffix. This is a screen of tags, not every actual number shift:

```python
import re
import xml.etree.ElementTree as E
ns = {"o": "http://www.bibletechnologies.net/2003/OSIS/namespace"}
root = E.parse("sources/ot/wlc/Jer.xml").getroot()
hits = []
for verse in root.findall(".//o:verse", ns):
    parts = [part for word in verse.findall("o:w", ns)
             for part in word.get("morph", "").removeprefix("H").split("/")]
    if "Sp2ms" in parts and any(re.fullmatch(r"V.[pqiwjvh]2mp", p)
                                for p in parts):
        hits.append(verse.get("osisID"))
print(hits)
```

After excluding that false positive, five candidates cross speech/addressee
boundaries:2:31,25:28,31:7,43:2,46:14. Of the remaining seven,17:4 and27:13 fall within quantitative minuses
of the selected Greek body, not simple verb-number equivalents. Swete's
apparatus reports longer Qmg material at these sites; this is not an all-Greek
absence claim. The remaining five are11:13,20:6,22:26,34:14 and target37:18.
The neighboring27:12 was then added explicitly as a royal-address control,
not retrospectively counted as a screen hit.

## The actual Greek comparisons

SweteIII printed pp.248,259,266,270–271,302–303 and322 / PDF272,283,290,
294–295,326–327 and346 were viewed completely with relevant apparatus.
The target37:18 remains the prior pinned comparison, not a new collation.

| Hebrew unit | Selected Greek observation | Consequence |
|---|---|---|
| 11:13 | Singular σου for Judah and plural ἐτάξατε coexist. | A collective singular address need not eliminate a plural verb. |
| 20:6 | Plural πορεύσεσθε is followed by singular death/burial forms. | Greek can retain a group-to-individual shift within one speech. |
| 22:26 | Singular ἐτέχθης for birth, versus Hebrew plural; subsequent death remains plural ἀποθανεῖσθε. Qmg reports plural birth wording. | Number variation can be verb-specific; the body is not the whole Greek tradition. |
| 34:14 / Greek41:14 | Singular release verbs versus Hebrew's initial plural and later singular. The time formulation also differs: Greek six years, Hebrew end of seven years. | Singular presentation occurs elsewhere, but this is not an identical-source translation control or proof of who changed it. |
| Adjacent27:12 / Greek34:10 | Zedekiah is named as recipient; εἰσαγάγετε and ἐργάσασθε remain plural. | Royal address alone does not require Greek singularization. |
| Target37:18 / Greek44:18 | Singular σὺ δέδωκας versus Hebrew plural נתתם. | A real local difference remains; these controls do not identify its stage. |

The publisher's Rahlfs–Hanhart2006 pages corroborate the selected bodies at
[11:13](https://www.die-bibel.de/bibel/LXX/JER.11),
[20:6](https://www.die-bibel.de/bibel/LXX/JER.20) and
[22:26](https://www.die-bibel.de/bibel/LXX/JER.22).
Those edition presentations are not additional manuscripts. The other tested
publisher routes failed; their readings are not inferred from those failures.

## What this test changes

Do not explain37:18 as a grammatically necessary change or infer a uniform
Greek habit from it. Conversely, the other singular presentations do not prove
translator intervention rather than a differing source or later correction.
The constructions, quantitative differences and proposed Greek revision regions
must remain separate; these examples do not yield a translation-frequency
estimate or decide Hebrew priority. The next historical test needs target
critical collation/correction history or a genuinely matched construction
sample, not a repeat count of these controls.

The [packet](../sources/textual_restoration/comparisons/jeremiah_number_shift_controls.2026-10-19.v1.json)
pins the XML, fifteen current source/main-English records, the prior comparison
and the private Greek scan. No new checker, corpus import, restored letter,
English/note application, approval or canon decision is created.
