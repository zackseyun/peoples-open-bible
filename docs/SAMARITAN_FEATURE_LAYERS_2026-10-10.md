# Samaritan surface spellings and lexical analysis

The current DT-UCPH features preserve the two flagged Exodus 19:24 spellings
in their surface text while assigning conventional lexical interpretations.
Those interpretations must not be mistaken for manuscript letters. This
follow-up narrows the previous [editorial audit](SAMARITAN_EDITORIAL_SOURCE_AUDIT_2026-10-10.md)
with actual feature data, without changing POB Hebrew or English or claiming
that historical corrections to every layer have been reconstructed.

## What the current feature files show

Four complete word-feature files at pinned commit
`2f2120286ac48d4ff3d04e0107e33efd864aa9e1`, version 7.1.3, are acquired in
memory and byte-hashed. Each covers the same 114,889 current word nodes as the
pinned graph. At all 29 historical issue-node numbers, current word type and
declared section agree. This is a diagnostic of current locators, not proof
of stable token identity across annotation versions.

All 29 current Hebrew-script word values match their sign-slot consonants
under the existing normalization. Their `g_cons` and `g_cons_raw` values are
also identical at these locators. Neither observation certifies the original
manuscript reading or proves which features changed in the past.

| Exodus 19:24 current locator | Sign-slot spelling and Hebrew word feature | Both transliteration features | Lexical identity |
|---|---|---|---|
| 446025, issue 3 | ך | K | HLK[ |
| 446040, issue 16 | יחרסו | JXRSW | HRS[ |

The first retains the single final kaf, rather than inserting the lamed of
the WLC imperative. The second retains het in its surface spelling, while its
lexical identity refers to the conventional HRS verb. The issue annotations
describe interpretation of the first token and harmonization of the second.
Current surface/lexical separation is directly demonstrated; the exact
historical edit, correctness of the analysis, and physical manuscript marks
are not. Missing letters must not be supplied merely by expanding `HLK[`.

The [pinned descriptions](https://raw.githubusercontent.com/DT-UCPH/sp/2f2120286ac48d4ff3d04e0107e33efd864aa9e1/docs/g_cons_raw.md)
define `g_cons_raw` by the absence of shin/sin disambiguation, not by a
diplomatic guarantee. These generated documentation pages label version
5.0.2; the separately consulted actual feature headers label 7.1.3. A name
containing “raw” cannot replace checking the feature's definition and data.

## What the authors say about the dataset

Naaijer, Højgaard, Schorch and Ehrensvärd's [2024 paper](https://researchdatajournal.org/article/download/23068/24581/57171)
identifies the dataset text as the critical edition's main text supplied by
Schorch (§3, p.3). It also warns that Masoretic-trained morphological analysis
can misinterpret Samaritan forms, even with identical consonants (§3, p.4).
The feature discussion distinguishes surface word text from lexical and
morpheme features (§4, p.5). Its proper-name example deliberately shares MT
lexical identities despite different surface spellings (§5.2, p.10), and the
conclusion describes manual correction of model predictions (§6, p.11).
This explains why shared lexical labels cannot count as an extra Hebrew
attestation. It does not settle the two tokens' manuscript readings.

Root reads those five complete pages and visually checks pages 3–4. A separate
publication agent reads all 13 pages and checks relevant renderings. The paper
describes its then-current dataset, not every later change in version 7.1.3;
its word count and temporal-coverage metadata are not substituted for current
node counts or physical manuscript dates.

## Effect on POB and the next source task

POB Exodus 19:24 remains tied to WLC, whose relevant words are the imperative
לך and the prohibition verb יהרסו. Its “Go down” and “must not break through”
are compatible with that declared source. This is not a new blinded English
evaluation, a full-verse review, or a fresh HALOT consultation. The existing
lexical alternative note is anchored to “said to him,” not to its relevant
verb clause; that reader defect is queued separately, not repaired here or
certified by old review scores.

No source replacement follows from a lexical label. The next discriminating
evidence is the critical apparatus or manuscript image for these spellings,
and, if historical edit claims are needed, corresponding feature versions
with stable token alignment. Another preference vote cannot supply either.
For broader comparison, the pipeline must preserve surface text separately
from morphology and reading tradition, including equal-consonant cases.

## Reproduction and evidence limits

The [feature diagnostic](../sources/textual_restoration/discovery/samaritan_feature_layers.2026-10-10.v1.json)
stores feature byte pins, 29 current locator checks, original text hashes and
only two bounded token excerpts. Full feature files are external; attribution
and CC BY-NC 4.0 input terms are retained without corpus relicensing.

```bash
.venv/bin/python -m tools.textual_restoration.check_samaritan_feature_layers /path/to/sp/tf/7.1.3 /path/to/issues.json --fetch-pinned-features --verify-only
# Or supply --feature-directory /path/to/private/word/features instead of online fetch.
.venv/bin/python -m unittest tests.test_samaritan_feature_layers
```

Online acquisition is explicit, limited to four exact pinned URLs, and rejected
on hash mismatch. Offline tests exercise implicit node numbering, changed or
unsupported data, current section/type checks, normalization and abstention
boundaries. Neither a successful verifier nor feature agreement establishes
preserved ink, unedited diplomatic status, historical priority, all-source
coverage, a uniquely optimal English translation, publication or canon status.
