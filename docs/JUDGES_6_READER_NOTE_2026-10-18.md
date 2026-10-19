# Judges 6 shorter form reader note

Expand the existing Judges 6:7 note b to disclose the consequential shorter
Qumran form without adding an inline marker or panel. Preserve the note's
current lexical alternative and append:

> The Qumran manuscript 4QJudgesᵃ (4Q49) supports a shorter form without verses 7–10; the exact junction is partly reconstructed from adjacent surviving lines. Whether this reflects an earlier literary stage or a copying omission remains disputed.

The [source comparison](JUDGES_6_PROPHET_SPEECH_COMPARISON_2026-10-18.md)
establishes published short-form support from surviving adjacent lines, not a
freshly deciphered complete junction. Its working expansion preference does
not eliminate copying loss. The note therefore discloses attestation and the
preservation limit without endorsing an exact composition date or deleting
the longer speech. No outside English Bible wording supplies this note.

The [exact contract](../sources/textual_restoration/comparisons/judges6_reader_note_contract.2026-10-18.v1.json)
pins baseline `7c6b9bb703e55380b02ee50aaa15c0fb6b1a9e54`, the complete
[candidate](../sources/textual_restoration/candidates/judges6_reader_note.2026-10-18.v1.yaml),
evidence and permitted delta. Only note b's text and reason change in the
translation object. Hebrew, full marked main English, both existing anchors,
note a, lexical/theological fields and generation metadata are unchanged.
Retained historical explanations and existing anchor placements are not a
new whole-verse approval.

Old status, revision pass, cross-check and footnotes are archived exactly with
their baseline bindings. The candidate is draft/needs-review and carries no
active inherited review score. A fresh factual/application review must check
the exact candidate before application; its scope is not historical priority,
the entire English verse or actual public deployment.

The [focused test](../tests/test_judges6_reader_note_application.py) derives the
permitted record independently from Git, validates schema and exercises the
real exporter across all 618 historical Judges records. Only note b's text and
reason at 6:7 may differ; book metadata and the other 617 units must remain
unchanged. A separate postapplication raw-file check guards the live tree.
The [receipt](../sources/textual_restoration/applications/judges6_reader_note.2026-10-18.v1.json)
records actual review and checks separately from CI, main integration and
public delivery. Existing Check Provenance remains the detailed route; no
separate reader/publisher code, new marker or inline panel is introduced.

## Additional edition-access check

The authorized [BHQ Judges sample](https://g.christianbook.com/ns/pdf/sample/563870.pdf)
contains eight PDF pages: title, text/apparatus from 1:1 through the beginning
of 2:1, selected early-book Masorah notes, and critical commentary from 1:1
through part of 1:13. All eight pages were text-inspected; the final commentary
page was also rendered and visually checked. It contains no Judges 6 target
apparatus or commentary. Its SHA-256 is
`bccc6e3b72facf9bbfd37b069a7fe8b719f89c8b9a54cebe7a5c335420aff2fc`.
The separate [Logos/Biblia authorized preview](https://biblia.com/api/plugins/embeddedpreview?historybuttons=false&layout=minimal&navigationbox=false&resourceName=LLS%3AJUDGESBHQCAPP&sharebutton=false)
shows early chapter-one commentary and explicitly limits further content.
Neither route supplies the needed modern target evidence, changes the source
judgment, or justifies a claim that the full critical edition was consulted.
Do not repeat these preview routes without genuinely new access or coverage.
