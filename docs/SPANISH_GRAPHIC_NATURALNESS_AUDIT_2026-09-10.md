# Spanish POB graphic and priority-book naturalness audit — 2026-09-10

## Scope

This pass covers 13,910 canonical verses in Matthew, Mark, Luke, John, Acts,
Revelation, Genesis, Exodus, Leviticus, Numbers, Deuteronomy, Joshua, Judges,
Ruth, 1 Samuel, and 2 Samuel. It also inventories every verse referenced by the
live Graphic Bible catalog: 9,072 unique verses across 267 stories.

The English POB and original-language record remain controlling context. NBLA
is used as a modern Latin-American Spanish comparison, not copied as a source
corpus. The main text must preserve the POB's source decisions while reading as
natural neutral Latin-American Spanish.

## Applied findings

- Removed parenthetical punctuation from the priority corpus without deleting
  the enclosed scriptural words. Explanatory clauses now use ordinary prose or
  Spanish dash punctuation.
- Removed Spain-specific `vosotros`, `os`, possessives, and corresponding verb
  forms from the declared neutral-Latin-American corpus.
- Replaced the recurrent calques `respondió y dijo` and `aconteció que` with
  natural equivalents where they occurred in the priority books.
- Corrected concrete accuracy or fluency problems found in the drift review,
  including Acts 20:25's erroneous double negative, John 21:7's outdated
  “desnudo,” John 1:41's duplicated “Mesías,” Matthew 28:14's awkward
  “sin preocupación,” Genesis 49:28's repeated blessing formula, Exodus 32:35's
  missing plague, and several duplicated or stale constructions.
- Public reader payloads strip inline footnote markers while preserving the
  separate footnote metadata.

## Remaining review queue

`analysis/spanish_graphic_naturalness_priority.json` is the reproducible
editorial queue. It records 1,241 Graphic Bible verses whose stored Spanish base
predates the current English POB. This is a priority signal, not proof that all
1,239 require revision: some English changes are punctuation, register, or
source-detail refinements already expressed adequately in Spanish.

The queue also records non-blocking review signals such as `he aquí`,
`ahora bien`, repeated speech verbs, and literal necessity constructions.
These require verse-by-verse judgment because many are legitimate discourse or
rhetorical choices; they must not be removed by blind replacement.

## Verification contract

`tests/test_spanish_priority_reader_text.py` scans the complete 13,910-verse
priority corpus and rejects parentheses, Unicode superscripts/subscripts,
Peninsular second-person forms, `respondió y dijo`, and `aconteció que`. It also
locks the adjudicated Acts 9:3, Acts 20:25, John 1:41, and Genesis repairs.
