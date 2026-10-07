# 1 Enoch (Mashafa Henok) — scope and source strategy

This document covers the People's Open Bible's dedicated sub-phase for
the Book of Enoch (1 Enoch / Ethiopic Enoch / Mashafa Henok /
መጽሐፈ፡ ሄኖክ). It sits under the Pseudepigrapha track alongside
[2ESDRAS.md](2ESDRAS.md), complementing
[DEUTEROCANONICAL.md](DEUTEROCANONICAL.md) (the 13 LXX-based books) and
applies the three-zone scholarly-source policy from
[REFERENCE_SOURCES.md](REFERENCE_SOURCES.md).

> **Status (2026-10-02): translated corpus is incomplete.** The read-only
> primary-source inventory finds 53 absent verse files in chapters 1–35,
> and 209 recovered-primary missing-unit leads across all 108 chapters.
> Counts beyond chapter 35 are parser-derived leads, not a certified
> versification inventory. Existing clipped source/translation records also
> need repair. Do not infer completeness from the presence of 108 chapter
> entries or from generated Graphic Reader panels.
>
> Run `python3 tools/enoch/audit_pob_source_coverage.py --chapters 1-108`.
> See `sources/enoch/coverage/pob-primary-inventory-20261002.json` for exact
> missing verse numbers and source-review leads. These checks do not approve
> translations; source-complete candidates belong outside `translation/`
> until their bounded source/review/application gates pass.

## Current source-review route (2026-10-07)

Vertex is not required. `tools/enoch/review_source_candidates.py` runs a
fresh, read-only, ephemeral scan-review pass through the existing
ChatGPT-signed-in Codex CLI, using its configured model. It does not read or
extract authentication tokens and never installs or approves translations.
The bounded transaction remains the separate application gate. Review inputs,
actual source images, output and provenance hashes are preserved.

Chapters 7–8 were restored by the October 6 bounded application. Chapter 13's
October 7 package restores clipped 13:4 and absent 13:5–10; it explicitly
discloses the selected critical edition's uncertain/editorially restored
readings. Neither that work nor the older inventory constitutes complete-book
or human-specialist certification. Recompute the audit for current counts.

## Why Enoch

Four reasons this book warrants a dedicated phase:

1. **Canonical in the Ethiopian Orthodox Tewahedo Church** — part of
   their 81-book canon. Eritrean Orthodox and Beta Israel also
   receive it. **There is no permissively-licensed modern English
   Enoch translation serving these communities.** R. H. Charles 1912
   is PD but Victorian in register; Charlesworth OTP (1983),
   Nickelsburg Hermeneia (2001/2012), Black 1985, and Knibb 1978 are
   all copyrighted.
2. **Quoted in the New Testament.** Jude 14-15 explicitly cites
   1 Enoch 1:9, and 2 Peter 2:4 alludes to the Watchers tradition
   developed in Enoch. Readers of Jude and 2 Peter benefit from
   direct access to the cited source.
3. **Early Christian reception is deep.** Tertullian, Irenaeus,
   Clement of Alexandria, and Origen all cite 1 Enoch. The book was
   lost to Western Christianity by the 5th century and rediscovered
   by James Bruce in 1773.
4. **The textual situation is rich enough to do well.** We have
   PD Ge'ez critical editions (Charles 1906, Dillmann 1851), PD
   Greek fragments (Codex Panopolitanus for chs 1-32, Syncellus
   extracts, Chester Beatty for chs 97-107), AND a validated digital
   Ge'ez text we can use as a cross-check oracle. This is actually a
   stronger source position than 2 Esdras.

## Compositional structure

1 Enoch is a composite work of five sections, compiled by the
1st century AD:

| Chapters | Section | Dating | Language history |
|---|---|---|---|
| 1–36 | Book of the Watchers | 3rd c. BC | Aramaic original (Qumran 4Q201, 4Q202 attest); Greek (Panopolitanus 1-32); Ethiopic complete |
| 37–71 | Book of Parables / Similitudes | early 1st c. AD (most scholarly consensus) | **Ethiopic-only** — not at Qumran, not in known Greek fragments |
| 72–82 | Astronomical Book / Luminaries | 3rd c. BC | Aramaic (Qumran 4Q208-211); Ethiopic |
| 83–90 | Book of Dreams / Animal Apocalypse | 2nd c. BC | Aramaic (Qumran 4Q204-207); Ethiopic |
| 91–108 | Epistle of Enoch | 2nd-1st c. BC | Aramaic (Qumran 4Q204, 4Q212); Greek (Chester Beatty 97-107); Ethiopic |

The "Book of Parables" (chs 37-71), a.k.a. Similitudes, is
distinctive — it contains the "Son of Man" material that influenced
NT christology, and it survives only in Ge'ez. This is not textually
problematic (modern scholarship converged on early 1st c. AD Jewish
composition), but it means we have only one language witness there
versus up to three elsewhere.

## Canonicity

| Tradition | Status |
|---|---|
| **Ethiopian Orthodox Tewahedo** | **Canonical** (81-book canon) |
| **Eritrean Orthodox** | **Canonical** |
| **Beta Israel (Ethiopian Jewish)** | Sacred |
| Coptic Orthodox | Not canonical but respected |
| Roman Catholic | Not canonical |
| Eastern Orthodox (Greek/Russian) | Not canonical |
| Protestant | Not canonical; typically not even in Apocrypha sections |
| New Testament | Jude 14-15 cites it directly; 2 Peter 2:4 alludes to Watchers tradition |

Per POB policy (see [DEUTEROCANONICAL.md](DEUTEROCANONICAL.md)): we
take no position on canonicity. We label the book clearly in its
canonical context when published.

## Source editions — vendored

Source-control clarification, 2026-10-05: critical editions are edited texts,
not independent manuscript witnesses. The
[Enoch 1:9 and Jude comparison](docs/ENOCH_1_9_JUDE_14_15_COMPARISON_2026-10-05.md)
checks actual survival, editorial supplies and edition dependencies. Charles
1906 explicitly uses Greek and Jude in its apparatus at this unit; its agreement
with Jude cannot automatically count as independent Ge'ez attestation. Local
Greek OCR also clips the end of this complete printed verse. The older pipeline
plans below are not evidence that these controls have passed for every verse.

### Ethiopic (primary)

| Edition | Year | Role | SHA-256 | License |
|---|---|---|---|---|
| Charles, *The Ethiopic Version of the Book of Enoch* (Oxford, Anecdota Oxoniensia Semitic Series I.vii) | 1906 | **Zone 1 primary** — critical edition based on 23 MSS with full apparatus | see `sources/enoch/MANIFEST.md` | Public Domain |
| Dillmann, *Liber Henoch, Aethiopice* (Leipzig) | 1851 | **Zone 1 secondary** — earliest critical Ethiopic, clean layout without dense apparatus | see MANIFEST | Public Domain |

### Greek (secondary witnesses)

| Edition | Year | Coverage | License |
|---|---|---|---|
| Bouriant, *Fragments grecs du livre d'Hénoch* (Akhmim / Codex Panopolitanus) | 1892 | Akhmim material through 32:6, including overlapping forms; exact units require passage checks. No Chester Beatty attribution. | Public Domain |
| Flemming & Radermacher, *Das Buch Henoch* (GCS 5, Leipzig) | 1901 | Partial Greek: Akhmim / Panopolitanus, Syncellus quotations and Vatican fragment; facing German rendering of the Ethiopic. Not a complete Greek Enoch or the later Chester Beatty–Michigan edition. | Public Domain |

The coverage descriptions above follow Flemming–Radermacher's actual
introduction, printed pages 13–14. Do not route chapters 97–107 to that 1901
volume as Chester Beatty evidence. A verified edition of the later
Chester Beatty–Michigan material is a separate acquisition and comparison task;
its chapter labels do not establish every surviving word.

### English reference (not reproduced; verse numbering + cross-check only)

| Edition | Year | License |
|---|---|---|
| Schodde, *The Book of Enoch, Translated from the Ethiopic* | 1882 | Public Domain |
| Charles (in *The Apocrypha and Pseudepigrapha of the Old Testament* vol. 2) | 1913 | Public Domain (US) |

See `sources/enoch/MANIFEST.md` for SHA-256 hashes and rehydration
commands.

## Zone 1 validation oracle (not vendored)

- **Beta maṣāḥǝft digital Ge'ez Enoch** (`LIT1340EnochE.xml`, 712 KB
  TEI XML, Hiob Ludolf Centre, University of Hamburg). Based on
  Michal Jerabek's 1995 *Library of Ethiopian Texts* digitization.
  216 chapter divisions, ~179,000 Ethiopic characters, complete
  coverage of 1 Enoch 1–108.
  - License: outer wrapper declared CC-BY-SA 4.0; inner text
    attribution says "noncommercial purpose" and "cannot be sold."
    These are in tension; conservatively treated as non-redistributable.
  - **Role in POB**: validation oracle only. We do NOT vendor this
    XML; we do NOT derive our published Ge'ez from it. Instead, we
    cross-check our own fresh OCR of Charles 1906 and Dillmann 1851
    against this digital text. Where they agree, our OCR is
    validated; where they disagree, we investigate the specific
    character and publish our reading with explicit provenance.
  - This pattern is identical to how First1KGreek TEI (CC-BY-SA)
    served as validation oracle for our LXX Swete OCR.

## Zone 2 consult (scholarly, not reproduced)

Per [REFERENCE_SOURCES.md](REFERENCE_SOURCES.md):

- **Milik, *The Books of Enoch: Aramaic Fragments of Qumrân Cave 4*** (Oxford, 1976) — Qumran Aramaic fragment reconstructions; coverage must be established passage by passage
- **Nickelsburg, *1 Enoch 1: A Commentary*** (Hermeneia, 2001) — chs 1–36, 81–108
- **Nickelsburg & VanderKam, *1 Enoch 2*** (Hermeneia, 2012) — chs 37–71
- **Knibb, *The Ethiopic Book of Enoch*** (Oxford, 1978, 2 vols) — modern critical Ethiopic edition
- **Black, *The Book of Enoch or 1 Enoch: A New English Edition*** (Brill, 1985)
- **Charlesworth (ed.), *The Old Testament Pseudepigrapha* vol. 1*** (1983) — Isaac's translation

These are consulted during translation and cited fact-level in
footnotes where their conclusions inform a reading. Their text is
never reproduced in POB output.

## Translation strategy

Same three-zone discipline as the LXX deuterocanon, adapted for
Enoch's situation:

1. **Primary source**: our own fresh OCR of Charles 1906 Ge'ez,
   cross-validated against Beta maṣāḥǝft digital text (oracle) and
   Dillmann 1851 as a second edition control, not another manuscript vote.
   Preserve Charles's apparatus and supplied/emended wording separately from
   manuscript attestations. OCR agreement checks transcription of editions,
   not automatically their earliest-source priority. This OCR, once validated, becomes
   the Zone 1 Ge'ez Vorlage for English translation.
2. **Secondary textual apparatus** for chapters 1–32: Bouriant 1892
   Greek (Panopolitanus) provides an additional witness to the lost
   Aramaic. For chapters 97–107, a separately verified Chester Beatty–Michigan
   edition is required; Flemming
   1901 cannot supply that later acquisition.
3. **Parables (chs 37–71)**: Ethiopic-only at Zone 1. No Greek,
   no Qumran. Our output disclose this in the per-verse YAML.
4. **Qumran Aramaic parallels** where they exist: Zone 2 consult via
   Milik 1976. We footnote specific textual agreements/disagreements
   between Qumran and Ethiopic without reproducing Milik's reconstructions.
5. **Per-verse YAML** follows the standard POB schema with witnesses
   added: `zone1_sources_at_draft`, `zone2_consults_known`, plus an
   `enoch_witnesses` block listing which languages attest that verse.

## OCR validation (2026-04-21)

Critical finding during setup:

- **GPT-5** (Azure deployment we've used for Greek and Hebrew) **fails on
  Ge'ez**. Multiple attempts returned "cannot read" errors even at 4000px
  resolution on clean Dillmann 1851 pages.
- **Gemini 2.5 Flash fails.** It can emit real Ethiopic Unicode, but
  it hallucinates the content and cannot be trusted for scholarly OCR.
- **Gemini 2.5 Pro in plaintext mode succeeds.** Validated against
  the Beta maṣāḥǝft chapter-1 oracle on Dillmann 1851: strong
  line-level agreement, real word separators (፡), sentence
  terminators (።), and Ge'ez numerals preserved, with the remaining
  disagreements largely traceable to witness variation rather than
  obvious OCR garbage.

**Operational implication**: our Enoch OCR pipeline uses **Gemini 2.5
Pro in plaintext mode** rather than Azure GPT-5 or Gemini Flash.
Azure GPT-5 remains primary for Greek + Latin books. For Ge'ez, Pro is
the model that actually passes validation.

## Pipeline components (planned)

| Component | Status | Purpose |
|---|---|---|
| `sources/enoch/scans/` | ✓ vendored | PDFs of all Zone 1 editions (gitignored; manifest + rehydrate) |
| `sources/enoch/ethiopic/transcribed/` | ⏳ pending | Our Gemini 2.5 Pro plaintext-mode OCR of Charles 1906 + Dillmann 1851, chapter-indexed |
| `sources/enoch/greek/transcribed/` | ⏳ pending | OCR of Bouriant 1892 + Flemming 1901 Greek fragments |
| `tools/ethiopic/ocr_geez.py` | ✓ shared tool | Resumable Gemini 2.5 Pro plaintext-mode OCR CLI for Ge'ez. Used by both Enoch and [Jubilees](JUBILEES.md). |
| `tools/enoch/validate_vs_betamasaheft.py` | ⏳ pending | Cross-check our OCR against Beta maṣāḥǝft oracle |
| `tools/enoch/multi_witness.py` | ⏳ pending | Per-verse witness aggregator (Ge'ez + Greek where available + Qumran Zone 2 registry) |
| `tools/enoch/build_translation_prompt.py` | ⏳ pending | Phase 11 translator prompt |

## Phased timeline

| Phase | Work | Effort | Dependencies |
|---|---|---|---|
| **11a — source acquisition** | ✓ PDFs vendored, Gemini 2.5 Pro Ge'ez OCR validated, Beta maṣāḥǝft oracle archived | Done 2026-04-21 | — |
| **11b — transcription** | Gemini 2.5 Pro plaintext-mode OCR of Charles 1906 + Dillmann 1851 Ge'ez (~250 pages each). Cross-validate against Beta maṣāḥǝft. OCR Bouriant 1892 + Flemming 1901 Greek. | 1-2 weeks | Phase 9 (LXX) + Phase 10 (2 Esdras) complete |
| **11c — translation** | ~1,100 verses across 108 chapters, multi-witness context, three-zone prompt | 2-3 weeks | 11b complete |
| **11d — revision** | Reviser pass per REVISION_METHODOLOGY.md | 1 week | 11c complete |
| **11e — release** | Tagged release, CHANGELOG entry, update status.json | 1 day | 11d complete |

Total ≈ 5-7 weeks of focused effort, scheduled after Phase 10 completes.

## Unique strengths of this translation

When complete, our Enoch will be:

1. **First CC-BY 4.0 modern English Enoch.** All existing modern
   translations (Nickelsburg, Black, Isaac in OTP, Knibb) are
   copyrighted. Charles 1912 is PD but 112 years old and
   Victorian-register. Our output fills a real gap.
2. **Ethiopian Orthodox / Eritrean Orthodox readers gain a permissive
   modern English.** Existing English Enochs are produced for
   Protestant or Catholic audiences; an open translation serves
   Ethiopian canon readers directly.
3. **Transparent textual provenance per verse.** Which Ge'ez
   manuscript reading, which Greek fragment (if any), which Qumran
   Aramaic fragment was consulted (Zone 2) — every verse documents it.
4. **Multi-witness Ge'ez grounding.** Cross-validated OCR against
   the best scholarly digital text (Beta maṣāḥǝft) means our Ge'ez
   Vorlage is traceable, verifiable, and competitive with modern
   critical editions for textual accuracy.

## Future related works (under consideration)

Enoch sits in the Ethiopian broader canon alongside works that
would be natural extensions of this phase if we ever pursue them:

- **Jubilees** — Ethiopic Book, also at Qumran in Hebrew fragments
- **Meqabyan 1–3** — Ethiopian Orthodox canonical, Ge'ez-only
- **4 Baruch / Paraleipomena Jeremiou** — Greek + Ethiopic witnesses

None are committed to. The Enoch phase itself is scheduled; these
remain speculative and would each need their own scope document
when/if we pursue them.
