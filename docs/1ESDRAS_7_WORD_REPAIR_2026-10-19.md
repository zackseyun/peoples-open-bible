# 1 Esdras 7 source word repair

The selected printed Greek has two words miscopied into POB. Correcting7:6
changes the description of one group from having been brought back to having
been added. The candidate keeps the passive without supplying an agent or
complement; a note offers the idiomatic joined them alternative. This is an
import repair, not a newly discovered ancient variant or recovered Hebrew.

## Exact source correction

The [reviewed diagnostic](1ESDRAS_7_IMPORT_DIAGNOSTIC_2026-10-19.md) and its
[independent review](../sources/textual_restoration/comparisons/1esdras7_import_diagnostic_review.2026-10-19.v1.json)
establish the complete printed150 body and apparatus, one-based PDF168 in
the manifest-matched Swete volumeII. The original PDF hash is
`945c5b15bf0f9dfc93890b28ee5b66a388acbf4597f1f2be5430ac6cba9c30b0`.
Original images remain unchanged; the240dpi render is non-generative.
The legacy source.pages value167 remains a raw scan-leaf locator, explicitly
distinguished from printed and PDF pages in the corrected source note.

The [source candidate](../sources/textual_restoration/candidates/1esdras7_source_import.2026-10-19.v1.json)
keeps all fifteen units and accounts for every old source codepoint once.
At7:4 it replaces `προτάγματος` with printed `προσ-τάγματος`, joined as
`προστάγματος`. At7:6 it replaces `προσενεχθέντες` with `προστεθέντες`.
No other Greek codepoint, boundary or ID changes. There are no new whole
clauses, exclusions, moved passages or deleted canonical files.

Both differences already occur in raw transcription and persist through
regex/ours-only/final adjudication into canonical records. The observed stage
trace does not identify the initial generation's internal cause. The visible
apparatus does not support the imported forms at these units; this is not a
census of every ancient witness. Coele-Syria, the repeated purification text
and the current7/8 and10/11 boundaries remain as printed. The lower-resolution
boundary suspicions were rejected, not converted into additional repairs.

## English comparison and remaining ambiguity

The [English candidate](../sources/textual_restoration/candidates/1esdras7_english_import.2026-10-19.v1.json)
compares the close passive added, idiomatic joined them and current brought
back against six qualitative criteria. It prefers who had been added
provisionally: this keeps the passive and leaves the complement unstated,
although the English is less smooth. Joined them supplies a plausible
contextual complement and changes the grammatical presentation; it remains
an explicit alternative, not a demonstrated unique optimum.

The actual primary LSJ entries for
[προστίθημι](https://atlas.perseus.tufts.edu/dictionaries/entry/urn:cite2:scaife-viewer:dictionaries.v1:lsj-n90166/)
and [πρόσταγμα](https://atlas.perseus.tufts.edu/dictionaries/entry/urn:cite2:scaife-viewer:dictionaries.v1:lsj-n90108/)
were consulted, including the former's passive aorist and addition/joining
uses and the latter's command sense. Lexical range does not decide this
passage's exact complement, agent or admission event. Back and a return
journey are not expressed by the corrected participle. The approximate WLC
festival parallel is archived rather than used as evidence for it. No
Göttingen target apparatus, BDAG entry or specialist commentary is newly
consulted; the remaining inherited lexicon labels do not imply otherwise.

At7:4 the main words remain unchanged, including the existing distributive
plural royal title. The note explicitly distinguishes that interpretation
from the Greek singular after Artaxerxes. The approval note moves to approval.
At7:6 only the consequential participial words change; captivity and added
notes attach to their own terms. Active lexical/theological explanations
follow the corrected source, without inferring conversion or divine agency.
These use existing note routing, not a new reader/publisher layout.

## Application and verification contract

The [complete two-record application](../sources/textual_restoration/candidates/1esdras7_application.2026-10-19.v1.json)
uses baseline8ad14030bcedcdc533a74724afcdd672bdbf89ed. It archives old source,
English, decisions and review fields with exact baseline hashes. Both genuine
historical draft receipts remain unchanged. Active records return to
draft/needs_review and medium source confidence; old high/agree labels do
not certify a replacement. The prepared candidate is not yet applied.

The existing normalized-source lane changes only two of495 book rows and
retains the chapter5/6/8 repairs. The original six-test proofs for those
chapters replay at immutable applied snapshots with original code and inputs,
not repinned assertions. Separate live successor tests must protect493
unaffected canonical files, all fifteen chapter7 IDs, exact word replacement,
archives/schema, existing note anchors, drift rejection and actual nine-chapter
whole-book export. Neither contiguous numbering nor historical tests alone
certify the live successor. The [evidence packet](../sources/textual_restoration/comparisons/1esdras7_application.2026-10-19.v1.json)
binds one independent review to this complete candidate before replacement.

Publication requires ordinary commit/push, both own exact-head integrity jobs
and main merge after the chapter6/diagnostic predecessors. Those Git operations
do not themselves prove a website/CDN refresh or settle ancient textual priority.
