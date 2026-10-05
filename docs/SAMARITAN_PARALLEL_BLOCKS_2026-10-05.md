# Samaritan Torah parallels and the Numbers 20 narrative

This comparison advances the fixed twenty large Samaritan length-difference
leads beyond same-numbered verses. It finds exact repetitions across the Torah,
retains their ambiguity, and applies a qualified reader note at Numbers 20:13.
It does not recover new ancient letters or establish the earliest narrative.
The shorter WLC source and marker-free English remain unchanged.

## What the comparison establishes

The [new receipt](../sources/textual_restoration/discovery/samaritan_parallel_blocks.v1.json)
reproduces the [frozen whole-Torah screen](SAMARITAN_CORPUS_SCREEN_2026-09-04.md)
before selecting all twenty of its largest absolute length-difference leads,
in their original order. It searches every full WLC Torah verse and every full
other Samaritan node, across book boundaries. Each target Samaritan node is
excluded from its own candidate sources. Repetitions within that transcription
are useful parallels, **not independent ancient manuscript witnesses**.

| Measured result | Count |
|---|---:|
| Selected Samaritan nodes | 20 |
| WLC Torah verses searched | 5,853 |
| Samaritan nodes in the control | 5,841 |
| Other Samaritan nodes eligible per target | 5,840 |
| Distinct matching target spans | 68 |
| Control and reference alternatives across those spans | 502 |
| Target raw characters accounted for | 9,143 |
| Raw characters within matching spans | 4,672 |
| Raw characters outside matching spans | 4,471 |

WLC supplies candidates in fifteen target nodes; the Samaritan control supplies
them in nineteen. All twenty have at least one candidate, but none of these
counts means twenty completed historical adjudications. A short revelation
formula occurs at three target positions and has 140 reference alternatives
at each. Those are repetitions, not 420 discoveries or independent witnesses.

The engine removes spacing and pointing for consonantal comparison, preserving
matres and final forms. Both target endpoints must be whole-word boundaries.
All occurrences, overlapping spans and alternative references are retained;
there is no length threshold, ranking or greedy preferred match. A disjoint
partition accounts for every raw character, including residual letters and
spaces. The actual batch has no overlapping partition spans, while synthetic
tests exercise overlaps. Metadata and hashes are exported, not source strings.

Exact full-verse matching misses adapted wording, spelling differences and
partial-verse parallels. An unmatched span therefore does not mean unique
material. Preserving it prevents premature deletion; it does not explain it.
The twenty-node selection is length-biased and cannot estimate the frequency
of consequential variants throughout the Torah.

The source remains the [pinned DT-UCPH transcription](https://github.com/DT-UCPH/sp/tree/2f2120286ac48d4ff3d04e0107e33efd864aa9e1),
Text-Fabric 7.1.3, derived from Chester Beatty 751 through Deuteronomy 32:36
and Garizim 1 thereafter, with a composite boundary. All twenty target nodes
precede that boundary. Its CC BY-NC 4.0 terms remain attached to the private
research input; neither corpus import nor relicensing is claimed.

## Numbers 20 13 and its adapted parallels

The compared Samaritan node has 739 raw characters and 580 consonants, versus
37 WLC consonants. After the Meribah conclusion it adds Moses' plea to enter
the land, God's refusal, instructions to view the land and commission Joshua,
and commands about the journey through Edom. The main parallels are
Deuteronomy 3:24–28 and 2:2–6. Root read the complete target and those parallel
ranges in both controls, as well as the adjacent Numbers 20:14.

The exact engine identifies full-verse parallels to Samaritan Deuteronomy
3:24 and 3:27, WLC 3:25, and Samaritan 2:3–6. It also finds the ambiguous
revelation formula. It does not capture all the surrounding adapted material:
the refusal omits Deuteronomy's anger because of the people and failure to
listen, and first-person speech introductions become third-person narrative.
Joshua gains the designation son of Nun here. This is not a verbatim paste of
the entire Deuteronomy passage or a completed mechanical alignment.

**Interpretive consequence:** the longer form places Moses' request and the
succession/viewing instructions at Meribah, before the Edom episode. Adopting
it would materially alter the narrative sequence, not merely improve one
English word. POB should show the existence of that form without silently
blending it into the shorter text.

The directly consulted [Qumran-Digital 4Q27 transcription](https://lexicon.qumran-digital.org/transcriptions/4Q27/2026-05-21/index.html),
fragment 13 i–14, lines 24–30, reports fragmentary Meribah, prayer, refusal
and viewing material. Supplied brackets and damaged letters must remain
distinct from preserved text. The page embeds Masoretic and Samaritan controls;
those are not additional preserved 4Q27 words. This supports comparing an
ancient longer form, **not attestation of every word of the complete Samaritan
extension or its Edom commands**. Root consulted the published transcription,
not the manuscript pixels or a newly collated DJD plate. The response hash is
recorded in the application receipt; its full transcription is not vendored.

The strongest expansion explanation is contextual harmonization using familiar
Deuteronomy material. The strongest countercase is an inherited fuller form
subsequently shortened in another branch. Verbal parallels alone do not decide
direction; earlier witness age does not make every reading earlier. Historical
priority remains unresolved. The modern manuscript transcription and its
internal parallels are not independent votes for either explanation.

Dayfani's [publisher record and extracted passages](https://doi.org/10.1163/15685330-bja10179)
provide a methodological warning against treating all major Samaritan additions
as one mechanical copying operation. This pass did not obtain the publisher
PDF or the complete article; it does not rely on an unread passage-specific
argument as evidence for the Numbers decision.

## Applied reader contribution and verification

The [full candidate](../sources/textual_restoration/candidates/numbers20_13.2026-10-05.v1.json)
and [application receipt](../sources/textual_restoration/applications/numbers20_13.2026-10-05.v1.json)
bind the [Numbers record](../translation/ot/numbers/020/013.yaml) to its baseline.
The new note describes the longer Samaritan form and provisional retention of
the shorter Masoretic text. The existing holy-clause note moves from Yahweh to
the clause it explains. Both old note bodies, source wording, marker-free
English, lexical decisions, theological decisions and revision history remain.
Old review objects are archived exactly, not transferred to this candidate;
current status is draft and needs review. This is a reader disclosure, not
whole-verse approval, deployment, canon expansion or novel decipherment.

The complete Numbers export has 36 chapters and 1,289 verses; only 20:13
differs from the before export. Scoped tests check candidate equality, schema,
note anchors, preservation, review state, receipt hashes and export isolation.
Engine tests check conservative matching, ambiguity, self-exclusion, complete
partitions and saved numerical fixtures. Recompute against the private inputs:

```bash
.venv/bin/python tools/textual_restoration/screen_samaritan_parallel_blocks.py /path/to/sp/tf/7.1.3 --verify-only
.venv/bin/python -m unittest discover -s tests -p 'test_samaritan_parallel_blocks.py'
.venv/bin/python -m unittest discover -s tests -p 'test_numbers20_13_disclosure.py'
```

## Research value and the separate canon question

This is ready for bounded continuation: reproducible discovery now directs
human-readable comparison to actual structural differences. Further tokens
are useful only when they obtain discriminating evidence or test a translation
consequence. They cannot guarantee a new reading, turn supplied words into
preserved ink or prove the earliest text. Known-variant applications and
honest notes are already valid provisional POB contributions; a novel scholarly
claim additionally needs a literature check and qualified scrutiny.

The [two-question assessment](OT_SOURCE_COMPARISON_CONTINUATION_2026-10-04.md)
keeps wording and canonical authority separate. Manuscript finds can establish
ancient wording, circulation and reception of additional works, making them
worth comparing. They cannot establish universal inspiration or mandatory
canonical inclusion. The [IAA introduction](https://www.deadseascrolls.org.il/learn-about-the-scrolls/introduction?locale=en_US)
describes varied Second Temple literature and unsettled authoritative
collections; [Sinaiticus contents](https://www.codexsinaiticus.org/en/codex/content.aspx)
include Barnabas and Hermas. A labelled historical comparison library is a
defensible outcome without changing POB's canon. A canonical recommendation
requires a named tradition and its authority criteria.

The subsequent [Exodus 20:21 comparison](EXODUS_20_21_SOURCE_COMPARISON_2026-10-05.md)
now maps the complete expansion and adds a qualified draft note; its historical
priority and disputed supplied verb remain held. The
[Jubilees 1:27 overlap](OT_SOURCE_COMPARISON_CONTINUATION_2026-10-04.md#contribution-milestones-and-efficient-continuation)
is located but still needs primary Hebrew and modern Geʿez apparatus checks.
Neither task requires another readiness audit or judge-until-agreement loop.
Reopen Numbers only for named discriminating manuscript, edition or transmission
evidence; do not infer priority from this discovery receipt.
