# Eleven compound translation and note corrections

The retained Hebrew compound עשתי עשר or עשתי עשרה means eleven, with an
ordinal English rendering where the roster or month requires it. A screen of
all 39 local WLC books identified three POB verses that instead say twelve.
The six-record reviewed application is applied and locally verified.
Correcting those renderings improves fidelity to the declared source without
claiming that the retained source is the earliest attainable text.

## Source comparison and English impact

| Passage | Baseline English | Scoped correction |
| --- | --- | --- |
| Ezekiel 40:49 | Width twelve cubits | Width eleven cubits, with the Greek twelve alternative in a note |
| 1 Chronicles 25:18 | The twelfth lot, Azarel | The eleventh lot, Azarel; his group still numbers twelve |
| 1 Chronicles 27:14 | For the twelfth month | Both the eleventh roster position and the eleventh month |
| 1 Chronicles 12:14 | Eleven note attached to tenth | Same main English, with the note attached to eleventh |
| 1 Chronicles 27:13 | Clan note attached to tenth | Same main English, with the note attached to Zerahites |
| 1 Chronicles 27:15 | Name and descent notes attached to other phrases | Same main English, with the notes attached to Heldai and Othniel |

The [frozen screen](../sources/textual_restoration/comparisons/eleven_compound_screen.2026-10-12.v1.json)
records its exact query and all 39 XML input hashes: 19 compound occurrences
in 18 verse contexts. Presence of an English eleven or eleventh in the other
15 contexts is only a screening result, not approval of their complete
translations. These files represent one shared base corpus, not 39 independent
ancient witnesses. The screen's independent factual review reproduced the
query, counts and input pins.

At 1 Chronicles 25:18, the initial compound identifies the eleventh assignment,
whereas final שנים עשר gives twelve people. The adjacent assignments are tenth
and twelfth. The selected [Rahlfs Hanhart 2006 Greek](https://www.die-bibel.de/bibel/LXX/1CH.25)
also distinguishes eleventh from twelve. The previous lexical explanation of
an eleven/ten idiom for twelve is incorrect. The existing Azareel alternative
belongs after Azarel, not after the assignment number.

At 1 Chronicles 27:14, both compound expressions survive in the retained
source. The selected [Greek](https://www.die-bibel.de/bibel/LXX/1CH.27) also
has both eleventh expressions, between tenth and twelfth assignments. The
proposed English supplies a copula to make the elliptical roster intelligible;
it does not infer a different calendar or change the twenty-four thousand.
The tribal-descent note belongs after Ephraim, not after the month.

Reading that neighboring context also identifies anchor defects at 27:13 and
27:15. Their marker-free English remains unchanged. At 27:15, the former vague
reference to parallel traditions is clarified with the actually read Heled
expression in the warrior roster at 1 Chronicles 11:30. That parallel does not
attest a manuscript variant at 27:15 or prove that the two names identify one
person. The Othniel descent note retains its existing alternatives.

At Ezekiel 40:49, Greek twelve remains a consequential alternative. Its
architectural argument and the Hebrew and Latin eleven controls are examined
in the [source comparison](EZEKIEL_40_49_WIDTH_AND_SOURCE_COMPARISON_2026-10-12.md).
The exact Hebrew source is provisionally retained, with historical priority
unresolved. Neither the Greek ten stairs nor Latin eight stairs is inserted.
The existing awkward stairs clause and other architectural terms are not
certified by correcting the width.

## Provenance and application boundary

The application baseline is `ed0deaaff86368400e6ce9e50fbe21d97e40e06f`.
The comparison screen retains its earlier baseline rather than being
retroactively rewritten. The six canonical source blocks remain exactly
equivalent as parsed fields, including vowels and segmentation. A separately
identified paragraph-marker representation problem is not amended here.

The current Ezekiel record lost its original generation metadata, notes,
lexical decisions and earlier revision in a May wholesale reversion. Exact
historical generation metadata and translation philosophy can be recovered
from Git; removed notes, lexical choices, revisions and review flags must stay
clearly historical. Restoring the old record wholesale would reintroduce a
wrong lexical choice and misplaced note. Current May revision history is
preserved, and old agreement scores do not approve the new application.

The Chronicles corrections preserve original generation provenance and all
unrelated lexical entries. Only the two dependent number explanations change.
Prior field values and review flags are archived against their actual input
hashes; the revised records remain draft and need review.

The contract's method input pin identifies the immutable baseline method.
The independent application assessment separately binds the current version
2.0.1 method that governs this review; those are distinct inputs, not a claim
that the baseline already contained today's paragraph clarification.

## Paragraph markers and diplomatic fidelity

The separate representation check found 90 internal pe or samekh markers in
88 of 23,213 local XML verse contexts. At 1 Chronicles 12:14, the XML places
samekh after the tenth entry and before Machbannai and eleven. The legacy
`Verse.hebrew_text` renderer collects words first and appends all segments at
the end; current YAML follows that convention. This is a representation
defect relative to XML ordering, not an ancient numeral variant.

The existing XML comparison parser retains typed, positioned annotations and
keeps paragraph symbols out of its written-letter stream. A regression fixture
can protect that separation without changing canonical source text, drafting
prompts or the legacy renderer. The 88-context count is not a count of verified
current YAML defects; each reader/source mapping still needs its own check.
Future diplomatic exports must preserve the XML's ordered words and segments
rather than describe a flattened rendering as verbatim.

The [position screen and reproduction record](../sources/textual_restoration/comparisons/wlc_paragraph_position_screen.2026-10-12.v1.json)
retains all 88 contexts and the shared XML pins. Three new regression tests
passed. A combined run also passed 13 existing comparison tests, but the
existing frozen-receipt pin test failed on the previously changed 2 Samuel
13:37 record. No source or historical pin was changed to hide that mismatch;
it is distinct from the paragraph tests. A subsequent check of all 47 original
input pins against the screen's publication commit
`17ff36ca71255b6bdab11dce91bbadac295c101c` found no mismatch. Only Samuel
differs in the current tree; its reviewed note application at `d73c9aecc4`
retained the same source text. The failed current-tree assertion does not
invalidate the historical edition screen or establish paragraph accuracy.

## Verification and publication

One bounded independent application review passed the exact
[contract](../sources/textual_restoration/comparisons/eleven_compound_reader_contract.2026-10-12.v1.json)
and six candidates. It reproduced sources, generation provenance, current and
historical archives, all note anchors, complete exports and non-target
aggregates. A method-hash lookup defect found during preflight was corrected:
the immutable baseline method pin and current governing-method review binding
are now separate. No candidate wording changed during that correction.

Root applied the reviewed YAML bytes. The
[application receipt](../sources/textual_restoration/applications/eleven_compound_reader.2026-10-12.v1.json)
records the actual review and 78 distinct post-application tests: eleven new
application/paragraph checks, twelve existing Ezekiel checks, and 55 shared
note/export checks. Preflight and independent reruns are not counted again.
Complete actual exports match their reviewed candidates: 29 chapters and 943
units for Chronicles; 48 chapters and 1,273 units for Ezekiel. Only the six
specified units differ; 2,210 non-target YAML files retain their byte hashes.
All seven notes export, and no source block changes.

The unrelated Genizah follow-up remains untouched. Local documentation links,
workflow parsing and diff checks pass. CI explicitly runs the new tests and
fetches the two immutable Git inputs required for history verification.
Repository publication awaits the required remote integrity checks; it is
separate from local application and does not imply deployed-reader validation.
No ImageGen output supplies letters or evidence, and no canon addition or
corpus-wide translation superiority is established. All-known-source coverage
and the varied, two-family damaged-image benchmark remain incomplete.

The bounded review also located note-anchor leads at 1 Chronicles 12:15 and
Ezekiel 40:48. Root checked their actual notes: the hundred/thousand expression
is explained after Gad; vestibule, house and jambs notes are attached to other
phrases. They remain outside this frozen package. Their wording and source
interpretations still require their own scoped review, rather than extending
this application into a whole-book approval.
