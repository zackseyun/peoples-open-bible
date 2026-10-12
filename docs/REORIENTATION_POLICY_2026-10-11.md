# English reorientation terminology: authorized application

## Decision and scope

The maintainer selected "reorient toward God" after comparing repentance,
change of heart/mind, turning and reorientation, then explicitly extended the
request to Simplified POB and extra-canonical reader material. Apply the policy
to English `translation/` and `translation_simplified/`, not other languages,
source transcriptions, frozen releases or historical revision evidence.

This is an AI-assisted English editorial application. Maintainer approval of
the policy is not a claim that the maintainer or an independent scholar checked
every resulting line. The current records remain drafts; previous model approval
is archived rather than inherited by this new wording.

The input baseline and exact proposed reader text are recorded in
`config/terminology/reorientation-english-2026-10-11.json`. Its input-file and
source-object hashes fail closed on changed input. Applying the plan updates
reader wording, reconciles live decision metadata, adds an anchored explanation,
and preserves earlier source/generation/history fields. Large chapter revisions
use hashes and the exact plan instead of copying whole chapters into each history
entry. This is not a runtime global replacement.

## Reasoning and limits

- 2 Corinthians 7:9-10 distinguishes sorrow from the response it produces. Keep
  sorrow in the sentence; do not equate it with the whole meaning of metanoia.
- Greek usage is wider than a minor change of opinion. Reorientation is the
  selected English rendering, not a purported literal etymology.
- "Toward God" is explicit in Acts 20:21 and a contextual expansion elsewhere.
  Direct prayer uses "toward you." Omit a duplicated or unwarranted destination.
- Preserve named wrongdoing and separate turn/return expressions. Acts 26:20
  therefore retains "reorient and turn to God" and the accompanying works.
- Baptism retains its existing grammatical relationship to the response. This
  policy does not decide symbolic versus causal sacramental interpretations.
- Extra-canonical texts are not harmonized into a single theological framework.
  Their neutral reorientation wording leaves the destination to their own context.
- Entries based on public-domain English witnesses receive an explicit adaptation
  disclosure. The underlying English witness and attribution are unchanged; no
  new ancient-language translation is claimed.

## Documented exceptions

| Context | Treatment | Reason |
|---|---|---|
| Hebrews 12:17 | change of mind | Does not decide who changes or whether the issue is reversal of the blessing; existing alternatives remain. |
| Job 42:6; Jeremiah 8:6 | regret | Preserve Hebrew nacham rather than erase contrition or confuse it with shuv. Job's alternatives remain. |
| Ezekiel 18:30 | turn back | Preserve the Hebrew turning expression. |
| Psalms of Solomon 9:15 | regret | The recorded Greek is metameleia, not metanoia; no automatic Godward expansion. |
| Psalms of Solomon 16:11; Sirach 18:21 | turning back | The recorded Greek has epistrophe. |
| Wisdom 5:3 | reconsidering | A judgment-scene recognition is not expanded into an assertion of saving conversion. |
| Jeremiah 31:19 | after I turned away, I was sorry for what I had done | Contextual sorrow over wrongdoing; turning back remains a footnote alternative. |
| Luke 17:3-4 | reorient himself / I am changing my ways | Natural first-person dialogue in v. 4; no explicit God object or added requirement to prove completed reform. |
| 1 Clement 54:4 | unregretted | The negative adjective means without regret, not refusal to change. |
| Martyrdom of Polycarp 8, 10, 12 | regret / reconsider / change of mind | Do not turn regret over an arrest or demands for apostasy into Godward conversion. |
| Hermas reader chapter 15:3; 40 | change their minds | The context concerns backing away or vacillation, not movement toward God. |
| Apostolic Constitutions 2; Didascalia 7 | divine relenting / not changing his mind | God is the subject; never make God reorient toward himself. |
| Apostolic Constitutions 7 (Judas); Proverbs quotation in older church orders | remorse / regret | Distinguish remorse and lament from a generic Godward formula. |
| SPOB Jeremiah 36:24; Joel 2:13; Psalm 51:18 | grief/sorrow/broken spirit | Replace the supplied explanatory repentance language without adding a new source claim. |

## Intensifiers and source force

Do not add "fully," "completely," "radically," "truly," "wholeheartedly," or a
superlative to make the chosen word stronger. Preserve emphatic wording that is
already source-grounded: Hermas V.3.xiii.4 (reader chapter 21:4) has
`μετανοήσαντες ὁλοτελῶς` and `ἐξ ὅλης καρδίας μετανοήσαντες`.
Its existing "completely" and "from their whole heart" remain.

The POB Luke 15:7 revision also restores the missing comparative "more" in
"more joy ... than"; the recorded Greek has `πλείων`. This is not an invented
intensifier. No other general amplification is authorized.

## Sources actually consulted

- [Mounce: metanoeo](https://www.billmounce.com/greek-dictionary/metanoeo)
- [Mounce: metanoia](https://www.billmounce.com/greek-dictionary/metanoia)
- [Mounce: metamelomai](https://www.billmounce.com/greek-dictionary/metamelomai)
- [Mounce: epistrepho](https://www.billmounce.com/greek-dictionary/epistrepho)
- [BDB: shuv](https://biblehub.com/hebrew/7725.htm) and
  [BDB: nacham](https://biblehub.com/hebrew/5162.htm), consulted during the preceding research.
- Existing POB source payloads, local context, lexical decisions and preserved
  English witness passages. Earlier BDAG/HALOT/LSJ labels are not evidence that
  those works freshly endorsed this new English wording.

Existing CEB wording and Catholic/Orthodox/Reformed explanations informed the
preceding reception discussion; they are not manuscript evidence or endorsements
of this particular policy. Reader reception has not been empirically measured.

## Validation contract

`tests/test_reorientation_policy.py` checks exact application, unchanged source
and generation fields, preserved history, reader-note anchoring, no residual
repent-family words in main English text, no newly invented intensifiers, and
specific adverse-direction/divine-subject/ambiguity exceptions. Export tests
verify that the actual reader exporter retains selected text and notes.

Current policy metadata has `independent_scholar_review: false`. Deterministic
checks verify the application, not a scholarly consensus or semantic perfection.
Deployment and live-reader evidence must be reported separately from source edits.

## Local application and validation results

397 English reader records updated: POB 230 (53 NT, 4 OT, 10 deuterocanonical,
163 extra-canonical) and SPOB 167 (53 NT, 6 OT, 9 deuterocanonical,
99 extra-canonical). These are records, not unique biblical verses: some
extra-canonical chapters also have per-unit reader records.

- 10 focused terminology/application/export tests passed.
- 18 footnote-audit, 9 extra-text reader-note, and 37 reader-footnote-export tests passed.
- Complete POB reader-corpus validation, catalog validation, and Psalm numbering passed.
- Scan of both English roots found no remaining repent-family words in main
  translation text. Notes, source witnesses and historical records intentionally
  retain traditional terminology.
- Source objects and original generation/base snapshots remain unchanged; no
  new intensifiers were added.

The active content publication path is `.github/workflows/publish-pob.yml`
on main, not the retired CodeBuild project. Public readback must be checked
after that workflow completes; local validation alone is not deployment proof.

## Approved contextual follow-up (2026-10-12)

The maintainer explicitly approved the following refinements after reviewing
actual reader examples. They affect only Jeremiah 31:19 and Luke 17:4 in POB
and Simplified POB (four records). Mark 1:15 and 2 Corinthians 7:10 remain
unchanged. No new intensifiers are added.

- Jeremiah: "For after I turned away, I was sorry for what I had done ..."
  The selected turning-away reading is interpretive, not a newly discovered
  manuscript reading. The note retains "after I turned back" as an alternative.
  "For what I had done" makes the contextual object of sorrow explicit; it is
  not a separate Hebrew phrase. This preserves contrition without defining
  every occurrence of metanoia as sadness.
- Luke: "I am changing my ways" replaces "I am reorienting myself" in direct
  speech. The offender states a change of disposition and conduct; this does
  not introduce a requirement that completed reform be demonstrated before
  forgiveness. The separate return-to-you expression remains intact.

Evidence rechecked during the discussion: [BDB nacham](https://biblehub.com/hebrew/5162.htm)
and [NET Jeremiah 31:19 and notes](https://classic.net.bible.org/verse.php?book=jer&chapter=31&verse=19).
The earlier explanation that Jeremiah necessarily describes returning to God
*before* sorrow was too certain; translations differ on the direction of shuv.

`config/terminology/reorientation-dialogue-2026-10-12.json` records the exact
before/after texts and pins the already-published input to commit
`31fb6d430dde2b77899ef4c5365258d2d6836973`. The original 397-record plan is
unchanged. Previous decisions and note bodies are archived, revisions append
to the hash chain, and ancient source/generation metadata is untouched.
Current decisions describe this wording, not a fresh scholar certification.

Tests check the four exact follow-ups, preserved prior history and sources,
anchored notes, retained alternatives, reader export parity and unchanged
Mark/2 Corinthians examples in both editions. Consistent meaning does not
require identical English phrasing in every context.
