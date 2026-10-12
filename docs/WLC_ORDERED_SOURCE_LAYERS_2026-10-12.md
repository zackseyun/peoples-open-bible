# Ordered Hebrew source layers and access follow up

The opt-in source exporter preserves the vendored XML's word and segment order,
including paragraph markers that the legacy renderer moves to verse ends.
Written wording, traditional reading alternatives and editorial notes remain
separate. This provides a more faithful digital-edition input for comparison,
not a recovered manuscript or an adjudicated original Hebrew corpus.

## Reproducible source view

The [exporter](../tools/textual_restoration/export_wlc_layers.py) reuses the
existing XML comparison parser and word assembly. Its ordered units retain
word IDs, attributes, exact Unicode text, inline special-letter annotations and
direct segment positions. Notes retain their structured content. Qere groups
keep their own words, punctuation, catchwords and reading attributes; empty,
multiword and insertion-only readings are not silently discarded or merged
into written wording.

`ordered_xml_text` is a concatenation for inspecting XML order, without added
word spaces. It is not raw XML bytes or manuscript layout, and it includes
paragraph symbols. Use the separate written words or `written_text` for letter
comparison: that lane excludes paragraph symbols while retaining actual word
letters and the supported punctuation. Do not strip samekh or pe indiscriminately
from a flattened string; they can also be genuine letters in words.

The complete execution covers all 39 vendored XML books: 23,213 verse contexts,
305,507 written words and 71,206 direct segments. It preserves 1,260 qere groups
containing 1,278 words, 4,499 notes and eleven direct-word inline segments.
The [compact receipt](../sources/textual_restoration/comparisons/wlc_ordered_layers.2026-10-12.v1.json)
pins every source file and complete book-output digest without importing a
second bulky copy of the corpus into Git.

These are XML-context counts, not counts of the differently numbered POB reader
records or independent ancient manuscripts. At 1 Chronicles 12:14 the new view
places samekh after the tenth entry and before Machbannai, while the existing
canonical source string remains unchanged. Foreign or duplicate reference IDs,
duplicate word IDs and unsupported structural markup fail closed.

An additional synthetic check exposed a silent omission: a bare letter after
an XML word was not represented in either exported stream. The current source
files contain no such stray text, as the independent raw-XML check confirmed.
New guards nevertheless reject non-whitespace text outside explicit verse or
qere units. A regression covers leading text and tails while retaining ordinary
indentation and legitimate inline-word tails. Current book outputs and counts
remain unchanged; the summary digest changes to bind the repaired exporter.

Run the full summary or inspect an XML reference with:

```bash
.venv/bin/python -m tools.textual_restoration.export_wlc_layers --all-summary
.venv/bin/python -m tools.textual_restoration.export_wlc_layers --book 1CH --verse 12:14
.venv/bin/python -m unittest tests.test_export_wlc_layers
```

The CLI writes JSON to standard output only. The subset command explicitly
labels its scope and recalculates counts. No canonical YAML, source XML,
drafting prompt or legacy renderer is changed. A later source-field migration
requires consumer and numbering review, including registered critical overlays;
passing this export does not authorize that migration.

The WLC biblical text is public domain; OSHB annotation and morphology remain
CC BY 4.0 with the vendored license's attribution. Source-file hashes establish
reproducibility, not the edition's historical priority. ImageGen supplies no
characters or evidence to this export.

## Accurate acquisition queues

The Nahum registry entry still directed work toward acquiring a full article
that the [completed review](NAHUM_SOURCE_COMPARISON_2026-10-10.md#full-article-review-on-october-11)
had already read. The updated entry preserves the historical partial extraction
and failed web-fetch route separately from the successful complete publisher
viewer. It records the figures and tables as published illustrations, without
claiming fresh decipherment, hand/joinder verification or wider survival mapping.
Its next task is the discriminating grammatical/apparatus question, not another
identical acquisition attempt. Other registry objects and policy remain intact.
The registry remains 41 mixed object, family and edition records: only the
existing Nahal Hever entry changes, with forty other objects unchanged. It is
not a census of 41 independently transmitted manuscripts.

The [Ezekiel follow up](EZEKIEL_40_49_WIDTH_AND_SOURCE_COMPARISON_2026-10-12.md#critical-edition-access-on-october-12)
identifies the exact Göttingen edition to seek and distinguishes apparatus-free
downloads from the missing apparatus. No target apparatus entry was acquired,
so earliest-width priority remains held and no further English change follows.

## Verification boundary

One bounded independent implementation/access-record review passed. Its
separate raw-XML comparison checked every direct word and segment, including
attributes, assembled text and inline Unicode offsets, across the actual 39
inputs. It also reproduced the registry's one-object update and the primary
catalogue status. The same reviewer subsequently checked only the newly found
orphan-text guard and updated bindings; previous source/registry findings were
inherited, not counted as more source votes.

Root's final 26-test run passed in 5.279 seconds: eleven exporter checks, six
registry checks, three paragraph checks and six existing inline-letter checks.
Earlier development and independent reruns are not counted again. The receipt
stores final code/test/result bindings separately from the initial review.
Documentation links, workflow parsing and diff checks pass. CI adds the new
module without disabling an existing gate. Canonical and legacy files remain
unchanged by this package, as does the protected Genizah follow-up.

Repository publication remains subject to the required integrity checks.
Source-order fidelity is narrower than historical text selection, complete
witness coverage, calibrated image reading or measured corpus-wide English
superiority. Those broader requirements remain active; this exporter enables
their source-comparison lane without certifying them prematurely.
