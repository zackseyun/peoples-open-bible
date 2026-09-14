# Variant conformance across editions

Every derived edition declares a `language.variant` in each record. This is the
audit of whether the text actually honours that declaration, and the method for
re-running it.

The check is narrow on purpose. It asks one objective question — *does the
wording contradict the variant this record declares?* — and nothing about
translation quality. A rendering can be excellent and still fail here, and
passing proves only conformance, never accuracy.

Run before changing anything: **a negative result is a result.** Three editions
were audited and needed no change at all. Manufacturing edits there would be
exactly the failure `docs/SOURCE_NEAR_EDITORIAL_STANDARD.md` warns about —
novelty does not prove improvement.

## Status

| Edition | Declared variant | Marker checked | Found | State |
|---|---|---|---|---|
| **es** | neutral Latin American | vosotros / vuestro / -áis / -éis / -ad / clitic `os` | 150 verses | **fixed** — zero remain |
| **pt** | Brazilian readability | vós / vosso / convosco / 2pl verb forms | 15 verses | **fixed** — zero remain |
| **zh_hans** | Simplified Chinese | traditional-only characters | 1 verse | **fixed** — zero remain |
| **ko** | 표준어, 합쇼체 | 개역 endings, 이르되, 대저, 하옵 | 46 verses | **fixed** — one deliberate carve-out |
| **ru** | modern literary Russian | Church Slavonic forms | 0 | clean, no change |
| **de** | modern standard German | pre-1996 orthography, archaic forms | 0 | clean, no change |
| **fr** | modern international French | icelui, ains, moult, estre, vostre | 0 | clean, no change |
| **hi** | modern standard Hindi in Devanagari | non-Devanagari leakage | 1 verse | **fixed** |

The Korean carve-out is Matthew 6:9. Its `하옵소서` is the received wording of
the Lord's Prayer in Korean and is recognised far beyond this translation;
consistency is not worth the loss of recognition. It is deliberate, and it is
the only marker hit remaining in the canonical books.

## Method, and the traps in it

Each language needs its own marker set. The traps below are all mistakes that
were actually made and corrected during the 2026-09-13 pass; they are recorded
so the next person does not repeat them.

**Spanish — `-áis/-éis` is reliable, but exclude the numbers.** `dieciséis` and
`veintiséis` end in `-séis` and match a naive pattern. They produced most of the
noise in the first canonical scan.

**Portuguese — suffix matching does not transfer from Spanish.** `-ais/-eis` is
the ordinary Portuguese *plural* ending: `animais`, `oficiais`, `sinais`,
`detestáveis`. A suffix scan returned 2,446 hits, nearly all nouns and
adjectives. Only a closed list of pronouns (`vós`, `vosso`, `convosco`) plus
actual 2pl verb forms (`sois`, `fareis`, `direis`, `sereis`, …) works; it
returns 14, all genuine. **Use a closed list, never a suffix.**

**Chinese — do not hand-write the character list.** A first attempt included
`首`, `食`, `角`, `酬`, which are shared between both scripts, and reported 1,631
false hits. Only characters with a genuinely distinct simplified counterpart
count. `opencc` and `zhconv` are unavailable here and PEP 668 blocks installing
into the system Python, so the check uses a curated verified pair list.

**German — `Thron` is not archaic.** A pattern reaching for 19th-century `Th-`
spellings matched 231 verses, every one of them the ordinary modern word for
throne. Check `daß`, `muß`, `läßt`, `gewiß`, `ward`, `daselbst` instead.

**French — the imperfect-ending pattern is useless.** `\w+(oit|oient)` matches
`soit`, `doit`, `droit`, `endroit`, `voient`, `croient` — 2,313 hits, every one
ordinary modern French. `-issiez` is imperfect *indicative* (`vous agissiez`),
not a rare subjunctive, and `çà et là` is current idiom. Check `icelui`, `ains`,
`moult`, `oncques`, `estre`, `estoit`, `vostre`, `nostre` instead; there are
none.

**Hindi — the useful check is script, not vocabulary.** Judging Sanskritised vs
Perso-Arabic register is a matter of taste and does not contradict the declared
variant. What does is non-Devanagari text in the reader line. That scan found 7
verses; six were scholarly transliterations inside footnotes and are correct,
and one was a real defect — Luke 8:24 carried the model's own self-correction
note, `corrected complete text:`, in the middle of the verse.

**Russian — elevated is not archaic.** `устами`, `ибо`, `сего дня`, `доколе`
are ordinary literary Russian and do not contradict the declared variant. The
forms that would are `яко`, `аще`, `токмо`, `паче`, `понеже`, `оный`, `рече`,
`вси` — and there are none. Only `по сей день` (a fixed modern idiom) and
`дабы` appear, both acceptable.

**Korean — anchor the endings.** `니라` as a bare substring matches `아니라`
("is not"), which is ordinary modern Korean; an unanchored grep reports 14,083
files. The marker must be anchored to sentence-final position, as
`tools/korean_archaism_panel.py` does.

## What the pass found underneath

Variant conformance is a shallow check, but running it surfaced deeper defects
that no register scan was looking for. Worth noting, because it is an argument
for running cheap objective checks even when the corpus is believed clean:

- **Mixed variant inside a single sentence** was common, and is the strongest
  evidence of drift rather than choice: 2 Corinthians 9:2 read *vuestra
  disposición … por ustedes … vuestro celo*; Jubilees 15:11 read *circuncidarás
  … circuncidaréis*; Shepherd of Hermas 44:3 opened in the singular and finished
  in the European plural.
- **The same verses were wrong in several editions** — Amos 5:26, Ezekiel 45:20,
  Jeremiah 17:1, Baruch 1:15, Testament of Dan 5:10, Testament of Benjamin 9:2
  all carried the defect in both Spanish and Portuguese. That points at a shared
  drafting stage, not independent error, and means a defect found in one edition
  is worth checking for in the others.
- **Outright mistranslations** sat behind register problems in Korean:
  Leviticus 19:14 said "do not curse a *precious* person" where the Hebrew
  `חֵרֵשׁ` means *deaf*; Numbers 25:3 read `בַּעַל פְּעוֹר` as a place name,
  losing the idolatry that is the verse's point.

## A separate defect the audit uncovered: shifted Psalms verses (repaired)

Not a variant problem, but found while checking one and worth recording here
because the scoping method is the same. Repaired in
`Repair the Psalms superscription verse offset in ko and es`; kept here
because the scoping is reusable and because the first reading of the defect
was wrong in a way worth remembering.

Korean and Spanish Psalms had chapters where a verse was duplicated and
everything after it shifted by one, so a reader saw one verse twice and the
chapter's last verse sat in a stray trailing record.

Scope, measured from three independent angles that agree:

- **Verse counts.** Korean and Spanish each have 63 Psalms chapters with one
  record more than the English tree. The other seven editions have none.
- **Source text.** 987 of 2,578 Korean Psalms records carry a `source.text`
  belonging to a different verse (977 off by one, 10 by two). A scan of the
  whole Korean Old Testament finds offsets in **Psalms and nowhere else**.
- **Provenance.** 431 of those were demonstrably drafted from the offset verse:
  their pre-correction `base_translation` matched the English at the offset
  path. Recover it with `git show 9a2addab19^:<path>`.

The affected chapters are the ones carrying a superscription, which POB stores
as verse 0, and Korean and Spanish are the two editions drafted before the
Psalms renumbering — the same two that showed `base_translation` offsets.

### What the first reading got wrong

The cause is narrower than "a verse duplicated at a varying position". Both
editions were drafted while the English tree was midway through moving the
superscription to verse 0, so it then carried the superscription at both `000`
and `001`. Every chapter with a superscription came out one record too long,
with the duplicate always at `001` and the body one slot late. That is why the
count is exactly 63 in exactly these two editions.

Two corrections to what was recorded above:

- **"Do not delete the trailing record, it holds the only rendering of the
  final verse."** True of Spanish, and false of Korean by the time it was
  written. A `gpt-5.6-terra` pass on 2026-07-13 had already re-translated most
  Korean records against their own path, pushing the offset draft into
  `revisions[].from`, so in 43 Korean chapters the trailing record was a
  redundant *second* rendering of a verse already correct at its own path.
- **`source.text` as the evidence of where a record belongs.** Sound for
  Spanish, inverted for Korean: the July pass moved the rendering onto the
  right verse and left `source.text` stale, so following the source would have
  moved corrected renderings back off their verse. This is why
  `realign_by_source.py` was the wrong instrument, not merely a blocked one —
  its `apply` guard was right to refuse, and was left untouched.

The real cost was the opposite of the one feared. Deleting trailing records
would have lost little; what had actually gone missing was 32 Korean verses
and 1 Spanish verse with no live rendering anywhere, overwritten where the
July pass skipped the record that should have moved. Ps 84:4, "Blessed are
those who dwell in your house", existed nowhere in `translation_ko`. All were
recovered from the revision history of the record that replaced them.

### Method worth reusing

Three signals, each checkable, that between them fix every record:

- **Position.** Untouched editions carry the offset in their positions, and
  `source.text` agrees with position on 1116 of 1118 records — so either can
  check the other, and the disagreements are worth reading individually.
- **Revision shape.** A revision that replaced a verse and one that copy-edited
  it separate cleanly on `from`/`to` similarity (replacements at <=0.5, copy
  edits at >=0.6), which is what distinguishes a Korean record the July pass
  re-aimed from a Spanish record it never touched.
- **Coverage, not moves.** Ask which English verses have a live rendering
  rather than which records look misfiled. That is what surfaced the 33
  missing verses, which no move-based view showed at all.

Repairs run through `tools/repair_psalms_verse_offset.py`, which refuses any
chapter that does not resolve to exactly the English verse set, and preserves
every dropped rendering in the revisions entry of the record that keeps its
verse before removing it.

## Re-running

```bash
# Korean
python3 tools/korean_archaism_panel.py scan --min-similarity 0.45

# Spanish / Portuguese / Chinese: see the marker sets above. Extract
# translation.text with a YAML parse, not a line read — many records store it
# as a multi-line scalar and a line-based reader silently truncates them.
python3 tools/spanish_pipeline.py validate --only-existing
python3 tools/korean_pipeline.py validate ot --only-existing
```

`tools/spanish_pipeline.py` supports `validation_exceptions` on a record: a list
of `{check, reason}` that suppresses one named check for that record only. It
exists so a genuine false positive — a bibliographic citation whose English work
titles must not be translated — can be cleared without relaxing a check that
guards 43,000 other records. Every waiver carries a reason and appears in that
record's own diff.
