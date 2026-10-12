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
| Job 42:6; Jeremiah 8:6; 31:19 | regret | Preserve Hebrew nacham rather than erase contrition or confuse it with shuv. Job's alternatives remain. |
| Ezekiel 18:30 | turn back | Preserve the Hebrew turning expression. |
| Psalms of Solomon 9:15 | regret | The recorded Greek is metameleia, not metanoia; no automatic Godward expansion. |
| Psalms of Solomon 16:11; Sirach 18:21 | turning back | The recorded Greek has epistrophe. |
| Wisdom 5:3 | reconsidering | A judgment-scene recognition is not expanded into an assertion of saving conversion. |
| Luke 17:3-4 | reorient himself / I am reorienting myself | Retains the interpersonal setting without inserting an explicit God object. |
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
