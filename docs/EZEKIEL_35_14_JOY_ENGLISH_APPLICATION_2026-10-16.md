# Ezekiel 35:14: whose joy, and when?

## Decision and scope

The working preference is **"When the whole earth rejoices, I will make you
desolate."** It replaces the clause "As the whole earth rejoiced, I will make
you desolate" under exactly retained WLC consonants, pointing and segmentation.
This is a consequential interpretation/English decision, not new Hebrew ink.
The application status and verification are recorded below.

The [source comparison](EZEKIEL_35_VARIANT_EDITIONS_2026-10-16.md) remains open
on the relative priority of the longer Hebrew and shorter Greek forms. We do
not insert the proposed noun tav at 35:14, delete 35:15a, change its recognition
formula, or construct a hybrid text from the two literary forms.

## Reasoning against the retained Hebrew

Read as a unit, 35:10-13 accuses Edom of claiming the two lands and reviling
Israel; 35:15 explicitly compares Edom's joy over Israel's desolation with
Edom's coming judgment. In 35:14, כ/שמח is an infinitive, not a finite past
verb. The neighboring explicit past joy belongs to Edom, not automatically to
the whole earth. This is the main weakness in POB's previous English, not a
general prohibition on rendering Hebrew infinitives with English past tense.

[GKC 114e/q](https://en.wikisource.org/wiki/Gesenius%27_Hebrew_Grammar/114._The_Infinitive_Construct)
allows a temporal construction and contextual time; [GKC 115e](https://en.wikisource.org/wiki/Gesenius%27_Hebrew_Grammar/115._Construction_of_the_Infinitive_Construct_with_Subject_and_Object)
supports taking a following noun phrase as subject. But 115a/b and note 2 also
allow objects and contextually supplied subjects. These are online grammar
transcriptions, not a newly inspected manuscript or printed scan. They make
the temporal reading available, not compulsory.

| Reading | Meaning and tradeoff |
|---|---|
| When the whole earth rejoices | The earth's joy accompanies Edom's announced desolation; verse 15 explains the fitting retaliation for Edom's earlier joy. This uses the following noun as subject without supplying Edom there. The occasion of the earth's joy is not named. |
| Just as you rejoiced over the whole land | Edom is the implicit subject; the land is the object of joy. This anticipates verse 15 directly and fits the preceding accusations, but requires more supplied relations in verse 14. It remains the strongest contextual rival. |
| As the whole earth rejoiced | Keeps the earth as subject but locates its joy in the past without clear contextual support. The infinitive permits past reference in principle; the issue is this passage's agency and time, not morphology alone. |

We do not add "because Edom falls" or "because Israel is restored." Neither
occasion is explicit. "Earth" remains defeasible against "land," retained in
note b; the revised rationale no longer claims an established exclusive global
scope. Note a discloses the comparative reading with Edom as implicit subject.
The source's repeated joy vocabulary survives in both verses without forcing
identical subjects or times. The Greek's compatibility with a temporal reading
does not identify a unique Hebrew Vorlage.

## Frozen comparison and application package

The [comparison contract](../sources/textual_restoration/comparisons/ezekiel35_14_joy_english_contract.2026-10-16.v1.json)
was frozen before a fresh-context reviewer received the three candidates.
Current/proposed identities, prior votes and root preference were hidden.
The [actual assessment](../sources/textual_restoration/comparisons/ezekiel35_14_joy_english_result.2026-10-16.v1.json)
prefers the temporal reading while preserving the comparative objection.
Reversing order was an order check within one assessment, not another vote.
The reviewer did not find the unlisted "As ... rejoices" demonstrably stronger;
it has not been silently substituted. No repeat-until-agreement loop occurred.

The [complete candidate](../sources/textual_restoration/candidates/ezekiel35_14_joy_reader.2026-10-16.v1.json)
and [application contract](../sources/textual_restoration/comparisons/ezekiel35_14_joy_reader.2026-10-16.v1.json)
pin baseline `4522efbfab0443723d9e8609718a913de54064a8`, the exact source,
policy, review inputs, schema, exporter and entire Ezekiel tree. A digest of all
path/byte-hash pairs binds the 1,273 baseline records without duplicating a
1,273-row manifest. Tests reconstruct that manifest from the immutable Git tree.
They compare the entire 48-chapter reader export, not just an isolated string.

Six exact prior-field archives preserve old text, notes, lexical reasoning,
status and reviews. Earlier revisions and AI-generation provenance are retained.
The active status is draft/needs review; old model scores do not certify new
wording. Only the joy clause, note a, note anchors and three dependent lexical
entries change. Note b's text and the Hebrew are unchanged.

The existing divine-title wording and theological rationale conflict with the
Yahweh policy. This clause-only review explicitly leaves that separate issue
unapproved; it does not claim an optimal complete verse. Verse 15's reader
wording is likewise context, not approved anew. Historical source priority,
all-source coverage, image-restoration calibration and the broader project
remain incomplete. ImageGen supplies no evidence here.

## Application status

At candidate freeze the canonical record was unchanged. The original clause
assessor then passed a separate full-record implementation check, including all
four preflight tests. This is not a second independent scholarly preference.
Root applied the exact reviewed candidate: YAML SHA256
`32e1aa9364a4cd57b205c4953d23ea7cdef480f4c76540502464c366846c4234`.

The actual complete 48-chapter / 1,273-record export matches the frozen proposed
SHA256 `f0cc04aea6770450f6b42d8fcdf13e4ccf810a775da7472b5d201ccbd0c65824`.
Both notes export. All 1,272 non-target YAML files remain byte-identical to the
baseline, and the target source is unchanged. The [application receipt](../sources/textual_restoration/applications/ezekiel35_14_joy_reader.2026-10-16.v1.json)
keeps the review and application milestones separate. No deployed-reader check
is claimed. The new regression module verifies archives, scope, input pins,
the full historical preflight and actual current export; CI explicitly runs it
and fetches its immutable baseline.

All five new application tests and 37 shared reader-note tests passed together
in 73.142 seconds. The four preflight tests and the reviewer's rerun are not
counted again. All 441 relative file-link targets in the three changed reports
resolve; workflow YAML and new JSON parse; `git diff --check` passes. These
checks validate the scoped implementation, not the historical interpretation.
