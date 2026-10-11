# Ahaziah accession age source comparison

At 2 Chronicles 22:2, twenty-two is a serious source-changing candidate, not
merely an English synonym or an unsupported attempt to match Kings. The
consulted Syriac text actually gives that age. However, the inspected Greek
edition gives twenty, not twenty-two. Earliest wording remains unresolved;
retain POB's forty-two provisionally, without treating its supplied Hebrew
base or old model agreement as a historical verdict.

## Consulted readings

| Control and location | Age | What it establishes |
| --- | --- | --- |
| Local WLC/OSHB 2Chr.22.2 and [publisher BHS](https://www.die-bibel.de/bibel/BHS/2CH.22) | `אַרְבָּעִים וּשְׁתַּיִם`, forty-two | Agreement between digital/edited Masoretic controls, not two independent Hebrew manuscripts |
| [Swete volume II scan](https://archive.org/download/theoldtestamenti03swetuoft_202003/oldtestamentingr02swet.pdf), printed 95–96, PDF 113–114 | `ὢν εἴκοσι ἐτῶν`, twenty | Published Greek selected text, not a fresh reading of codex ink |
| [CAL Peshitta 62039](https://cal.huc.edu/get_a_chapter.php?cset=S&file=62039&sub=22), row 22:02 | `ܒܪ ܥܣܪܝܢ ܗܘܐ ܘܬܪܬܝܢ ܫܢ̈ܝܢ`, twenty-two | A directly consulted Syriac edition control, not unanimity across Syriac manuscripts |
| Local WLC/POB 2 Kings 8:26 | `עֶשְׂרִים וּשְׁתַּיִם`, twenty-two | A parallel account, not another manuscript of Chronicles |

Root and the acquisition agent visually inspect the complete Swete target
pages, including the apparatus continuing onto printed 96. Preface viii–x,
PDF 10–12, identifies its Vaticanus-oriented base; the local margin is B.
The selective apparatus reports Alexandrinus differences elsewhere in this
verse but no age variant. Its silence does not establish that all Greek
manuscripts say twenty, or identify which manuscripts say twenty-two.
No imprint year is verified in this pass; the legacy 1909 label is not adopted.

CAL's [source metadata](https://cal.huc.edu/get_file_info.php?coord=62039)
describes the Leiden critical edition with some corrections based on manuscript
7a1. Its [twenty token](https://cal.huc.edu/getlex.php?coord=620392202&hasvariant=0&word=1)
and [and-two token](https://cal.huc.edu/getlex.php?coord=620392202&hasvariant=0&word=3)
confirm the numeric interpretation. No specific manuscript or correction hand
is assigned to this reading here. No AI-generated CAL commentary is used.

The [NET translators' note](https://classic.net.bible.org/verse.php?book=2Ch&chapter=22&verse=2)
reports twenty-two in some Greek manuscripts and Syriac. The present comparison
checks the Syriac control directly but does not independently establish that
Greek manuscript attribution. Modern English agreement is not manuscript support.
Publisher Greek/Latin routes failed to return usable chapter text in this pass;
no Rahlfs–Hanhart or Vulgate target consultation is claimed.

## Text selection and strongest objection

Chronicles itself gives Jehoram an accession age of thirty-two and a reign of
eight years at 21:5 and 21:20, then identifies Ahaziah as his youngest son at
22:1. The ordinary personal-age reading of forty-two creates a son older than
his father at death. Twenty-two fits that chronology and Kings; the Syriac
control demonstrates versional attestation in Chronicles itself. These support
investigating a corrupted number rather than assuming a special dynastic age
formula. The consulted wording does not establish that dynastic interpretation.

The strongest objection to selecting twenty-two is harmonization: a translator
or copyist could repair Chronicles using Kings or its own surrounding narrative.
The Greek twenty adds a distinct competing reading. A plausible historical age
does not prove the author's original wording, and these controls do not resolve
their local transmission relationships. The current Hebrew writes complete
numeral words; a proposed confusion of alphabetic numeral signs would require
separate evidence, not an invented mem/kaf accident. No physical date preference
is applied without passage-specific witness and hand identification.

This is a new published-text comparison in a previously undossiered book, not
a newly discovered variant, restored letter or complete Chronicles collation.
No earlier Hebrew manuscript at this locus or full modern Greek/Syriac apparatus
is inspected. Reopen selection for the specific age-unit evidence in the modern
Chronicles apparatuses and local versional copying/translation relationships;
do not repeat this selected-text acquisition or hold another gloss vote.

## Reader effect and input bindings

If twenty-two were selected, both the source numeral and POB's accession age
would change, resolving the stated chronological tension. Translating the
retained Hebrew as twenty-two would instead conceal a source change. The
current note discloses Kings but not these directly consulted versional readings.
A proposed, unapplied replacement is:

> The Hebrew reads “forty-two.” The parallel in 2 Kings 8:26 and the consulted
> Syriac text give twenty-two; Swete's selected Greek text gives twenty. The
> original age in Chronicles remains uncertain.

Canonical source, English, notes and review metadata remain unchanged. Applying
the disclosure would be a separate exact-record review and export check, not
approval of a new number or reuse of historical whole-verse review scores.
No ImageGen reconstruction, canon or About change follows.

One independent factual critique passes the complete Greek-page check, Syriac
interpretation and metadata, chronology, input pins and unchanged canonical
records. Ten existing book-map regression tests pass in 0.010 seconds; local
pin, link and diff checks pass. Neither the critique nor these tests establish
historical priority or approve the unapplied note.

Baseline main: `49a6a9a4767c8df9228061b62b8da7711c25784f`. SHA256 inputs:

- Chronicles verse: `b0f345cd3b40dbe834e0b26923387558146ac888ce93f1dc8fd2160282125d3d`.
- Kings parallel: `6b20178f2cda2eef7b033b961f27efc7f8899622e41700dfb9df939c85ad2acd`.
- WLC 2Chr.xml: `507294e8ca0fcf31ec25fe62fa24a7f2581f53116519bf08cfe96ff85e9c99fb`.
- Existing Swete II PDF: `945c5b15bf0f9dfc93890b28ee5b66a388acbf4597f1f2be5430ac6cba9c30b0`.

The preceding Haggai marker/syntax-lead work was committed and normally pushed
as `ac1f94f77b289ea0f09f7de555eb20283153803c` to
[PR139](https://github.com/zackseyun/peoples-open-bible/pull/139), with remote
head/tree/parent and five-path scope verified. Its thirteen focused tests and
one factual review passed; the full Smith argument stayed unread. At this
pass's opening, new-head CI remained in progress, not merged or deployed.
This independent branch started from the baseline main, incorporating neither
pending change. During this pass, PR138's two required jobs completed
successfully. Its exact eight-path current-main-relative scope was verified;
SHA-pinned merge produced `efc4fdbae664ebbd54db9ed126c1114f49d0e212`, tree
`16b1e9969dcd3adc227839c602c2617cd78fe0f8`, with baseline main and the tested
`bdcf66499312ac2241af6ec23f292d65ab076324` head as parents. Server readback,
normal fetch, ancestry and fresh no-main-worktree checks verified that result;
local main was advanced with an expected-old-ref guard and normally pushed.
The image reading/reference remains unresolved; merge does not approve letters
or deployment. Routine main integration of this research branch is separate
from the Chronicles judgment above.
