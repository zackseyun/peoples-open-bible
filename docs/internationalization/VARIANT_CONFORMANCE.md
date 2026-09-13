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
| **fr, hi** | — | not yet audited | — | outstanding |

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
