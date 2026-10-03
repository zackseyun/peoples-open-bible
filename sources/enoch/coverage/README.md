# Enoch source-completeness repair inventory

The 2026-10-02 audit found **53 absent verse YAMLs in chapters 1–35**.
Across all 108 chapters it found **209 absent recovered-primary units** and
64 existing source-length/ending review leads. Counts beyond chapter 35 are
parser-derived leads, not certified chapter counts. This inventory is not a
translation or OCR-fidelity approval.

`pob-primary-inventory-20261002.json` lists every missing verse number and
existing source-review lead. Recompute it with:

```sh
python3 tools/enoch/audit_pob_source_coverage.py --chapters 1-108
python3 tools/enoch/audit_pob_source_coverage.py --chapters 1-35 --require-complete
```

The second command fails until missing records, clipped source records,
unexpected numbers, and empty translations are resolved. Chapter 20 follows
the seven-unit Charles 1906 witness, not the eight-unit later English edition.

## Root causes and repair boundaries

- Charles chapter OCR files are page windows. A final verse and later verse
  units can survive only before the next chapter header in the next file.
  The primary parser now recovers these continuations; the old YAML inventory
  was never regenerated comprehensively after that correction.
- Dillmann chapter-7 OCR places numbered markers inside broken words. Those
  rows are **not independent verse-aligned evidence**. The secondary parser
  now fails closed for such boundaries or a missing chapter header. The raw
  OCR remains available for fresh scan alignment.
- Chapter 7's complete source and English candidates live in
  [the bounded restoration package](../../textual_restoration/applications/enoch_7_20261002).
  They are not installed in `translation/`
  and must not be presented as published text until independent scan review
  and a guarded application pass.

## Dead Sea Scrolls are a separate witness lane

The current repository registry has an Enoch target but **no Enoch images or
image-grounded Aramaic transcription**. It is a consult registry, not a full
Aramaic source text. The Library of Congress describes the Qumran discoveries
as portions of the Aramaic original:
https://www.loc.gov/exhibits/scrolls/libr.html

IAA identifies 4Q201 as Enoch and 4Q203 as the related Book of Giants:
https://www.deadseascrolls.org.il/explore-the-archive/manuscript/4Q201-1
https://www.deadseascrolls.org.il/explore-the-archive/manuscript/4Q203-1

Do not treat the range 4Q201–212 as a complete, continuous 1 Enoch source or
copy a modern editor's supplied Aramaic as surviving ink. Establish each
passage's coverage, reconstruction brackets, image rights, and actual reading
before incorporating a Qumran variant. No DSS omission can be inferred from
a lacuna or lack of coverage. Existing image-rights gates in
`sources/dead_sea_scrolls/README.md` remain in force.
