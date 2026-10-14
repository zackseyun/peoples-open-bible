# AI assisted manuscript recovery for POB

Research date: 2026-10-13, America/Los_Angeles.

POB will pursue computational recovery of damaged biblical writing and explicit
completion hypotheses. The immediate objective is a reproducible improvement in
access to surviving writing that could resolve a source-text question. A new
reading, an inferred completion, and a new historical interpretation are distinct
possible contributions; none requires changing the English to count as useful.

## Results from this session

### Published segmentation is reproducible but uneven

The [released-mask evaluation](../sources/textual_restoration/discovery/qsd_release_evaluation.2026-10-13.v1.json)
checks 100 files totaling 2,786,607 bytes against the pinned upstream Git blobs
and records their SHA256 values. It reproduces the paper's rounded results:

| Released method and task | Macro precision | Macro recall | Macro F1 | Contributing fragments |
| --- | --- | --- | --- | --- |
| MTEM ink | 0.8935 | 0.7029 | 0.7676 | 18 nonempty pairs |
| MTEM parchment | 0.9945 | 0.9818 | 0.9877 | 20 |
| Otsu parchment | 0.5892 | 0.9460 | 0.6919 | 20 |

Ink results vary materially: `124_008` has precision 0.1905, recall 0.2189 and
F1 0.2037, whereas `124_009` has F1 0.9639. The ink masks for `690_015` and
`690_016` are empty in both reference and released prediction; these are retained
in the report, but their precision/recall/F1 are undefined. They establish zero
predicted ink relative to those annotations, not physically proven blankness.

Pooling every pixel gives ink F1 0.9102, substantially higher than the
per-fragment mean. Larger/easier images dominate that pooled score. A recovery
claim for a difficult word therefore needs its own local error analysis. This
is a concrete reason to prioritize difficult regions and false-ink controls.
The reproduction confirms the released metrics; it does not discover new text
or independently authenticate every reference label.

Visual inspection of the authors' normalized infrared image for `124_008`,
its reference mask and released prediction corroborates the kind of failure:
the reference's left-hand writing shapes are largely missed, while a substantial
right-hand region absent from the ink annotation is predicted as ink. No new
transcription is attempted. The 1000 by 2000 normalized JPEG is 418,488 bytes,
matches its pinned upstream Git blob, and has SHA256
`4be83ff8a91c3471e4929b67f5ccf6d91ee65800568abd89a7760c9b2af8584d`.
It remains in the private workspace, outside the quantitative acquisition list.

### Fresh spectral learning improves a baseline but fails the recovery gate

The [new spectral experiment](../sources/textual_restoration/discovery/qsd_spectral_probe.2026-10-13.v1.json)
actually trains two 100-tree OpenCV classifiers from 30,000 labeled pixels of
`124_001`. It then predicts every pixel of all 20 fragments. The 19-fragment
evaluation below excludes that training image and retains both empty-reference
controls. Forty original 16-bit TIFFs and forty reference masks were verified,
totaling 169,308,844 bytes; all remain outside Git. No verse text was an input.

| Evaluation on 19 other fragments | Last band alone | First and last bands plus their difference |
| --- | --- | --- |
| Pooled ink precision | 0.2987 | 0.5145 |
| Pooled ink recall | 0.9261 | 0.9198 |
| Pooled ink F1 | 0.4518 | 0.6599 |
| False positive pixels | 4,252,390 | 1,697,936 |
| Mean fragment F1, including two failed empty controls | 0.2245 | 0.4009 |

The extra measured band reduces false detections by **60.1%** in this setup,
with a small loss of recall. This supports further investigation of spectral
information. It is not an improvement over the published MTEM system: the new
model's outputs are much noisier, and the development comparison does not
establish a new state of the art.

The difficult `124_008` case gets worse: F1 is 0.1227 for the single-band model
and 0.1145 for two bands, versus 0.2037 for released MTEM. The two-band model
also predicts 16,800 and 15,354 ink pixels on the two empty-annotation controls,
where released MTEM predicts none. These failures disqualify it as a reliable
transcription aid. No regions are removed to improve the score. Macro recall
has 17 defined cases while precision/F1 have 19 for these fresh models; the
published ink mean earlier uses 18 nonempty pairs including the training image.
Use per-fragment rows or explicitly matched subsets for model comparisons.

The next justified engineering experiment is richer spatial/spectral separation
with exposure normalization and more diverse development controls, followed by
a frozen manuscript-disjoint evaluation. More votes on generated letters or
retuning this same failure until it looks attractive would not supply that
evidence. Class-balanced training and transfer from one fragment can affect
false positives; this run does not isolate their individual contributions.

This is a completed development experiment with an adverse result for deployment,
not a new biblical decipherment. NumPy 2.3.5, Pillow 12.3.0 and OpenCV 4.13.0
were used. OpenCV reported eight threads despite one being requested, so no
effective single-thread reproducibility is claimed. Parameters were not retuned
after the result. No new source image, accepted character label or POB text
was produced by the classifier.

### ImageGen improves appearance but is not a faithful measurement

One built-in ImageGen call used the exact prompt recorded below and the existing
Leningrad crop, without supplying a passage name or proposed transcription.
The output has darker, sharper-looking writing and includes the requested
warning. However, the lower writing meets the new footer with clipping, and the
rendered manuscript area does not retain the input rectangle's aspect ratio.
The complete output is 1487 by 1058 pixels, nearly the source's overall aspect
ratio even though it now contains an additional footer. It is a regenerated
rendering, not an unchanged-pixel contrast view. These are visual/framing
observations; no character-level accuracy, exact registered pixel comparison,
or new letter identification is claimed.

The actual output is retained outside Git as
`outputs/ai-generated-fidelity-test-not-evidence.png` in this session's workspace.
It is 2,381,327 bytes, SHA256
`429d75a7a1ca8f147b2bb27d40f72fc1579bc0f67559ec03996ebe460983abf6`.
The source's earlier unresolved reference remains unresolved. No favorable rerun
was selected. This single prompt tests a particular output, not every possible
generative restoration model. Generative approaches can be investigated, but
their evaluation must measure preservation and false additions rather than
visual attractiveness.

### Actual Zuqnin target acquired for the next recovery attempt

The [live manifest](https://digi.vatlib.it/iiif/MSS_Vat.sir.162/manifest.json)
maps canvas `p0222` to `107r-106v` and `p0223` to the additional
`107r.[02.wl.0000]-106v.[02.wl.0000]` capture. Its SHA256 remains
`5274d5385f8879dc64e7b913030926a1ce528da37875e78233b6810e6490e140`.
The first canvas advertises 8168 by 6495 pixels. The actual
[IIIF JPEG response](https://digi.vatlib.it/iiifimage/MSS_Vat.sir.162/Vat.sir.162_0222_fa_0107r-106v.jp2/full/full/0/default.jpg)
is only 5000 by 3976, 2,333,240 bytes, SHA256
`6e3b87b1e65b7a07f590bce1da7ff747b70c421aff031e2c4e6277b0b3b4f7b7`.
It is retained privately as `work/zuqnin-107r-106v.jpg` in this session.

The full-spread inspection was further resized by the display to 1770 by 1408.
It shows layered writing and substantial physical loss on the left leaf; it
does not supply a new Greek transcription. No native-pixel glyph autopsy,
spectral stack, or original camera file is claimed. The second capture was
identified in metadata but not downloaded. Its label alone does not establish
a UV or infrared exposure. The useful next step is exact Greek line/column
registration and better measured views of surviving material, keeping absent
parchment explicitly absent. The watermarked study image stays outside Git.

## What could produce a breakthrough

The strongest opportunity is a material trace that already exists but has not
been adequately captured, separated, aligned, or interpreted. A small gain can
matter: one recovered stroke may distinguish a name, a negation, a pronoun,
or a correction. A new fragment join may reconnect a sentence. A readable
undertext may supply a witness absent from the present comparison. Recovering
one such reading would be a substantial result even if it confirms POB.

There is also legitimate work on physically missing text. A completion can be
strongly constrained by surviving letters, line length, the scribe's habits,
grammar and other witnesses. Its evidentiary basis is the argument and those
constraints. A rendered completion supplies no additional ancient testimony.
The goal is an explicit critical reconstruction with alternatives, not a claim
to possess an original autograph or a single undifferentiated pristine Bible.

### Available methods and their best uses

| Method | Actual input needed | Useful result | Main limitation |
| --- | --- | --- | --- |
| Native-resolution imaging, registration, contrast and channel analysis | Original photographs, preferably several exposures | Better access to faint marks and correspondence between old/new photographs | Sharpening or enlargement cannot guarantee recovery of information absent from the capture |
| Multispectral separation and learned ink segmentation | Measured wavelength bands and defensible masks | Distinguish ink, substrate, holes and sometimes overwritten layers | Ink chemistry and capture conditions vary; a bright or dark pixel is not automatically writing |
| Virtual unwrapping with learned ink detection | Real volumetric scans and a surface model | Read inaccessible rolled or folded surfaces | Requires scans and correct geometry; a photograph cannot be turned into a measured CT volume |
| Fragment matching | Recto/verso photographs, edges, ruling, handwriting and dimensions | Candidate physical joins or same-manuscript groupings | Similar script or wording alone cannot prove a join |
| Specialized handwriting recognition | Script-specific images and diplomatic labels | Letter candidates with uncertainty | Recognition can normalize a variant toward a familiar biblical verse |
| Constrained language completion | Explicit gaps, observed letters, possible lengths and comparison texts | Ranked textual hypotheses, including unknown-length gaps | Plausibility is not physical preservation; related witnesses are not independent votes |
| Generative image or video reconstruction | Existing image plus a proposed reconstruction | Clearly labeled illustration, or an experimental model output to test | Generated pixels and frames are predictions, not additional measurements |

Actual repeated camera frames may support denoising or multi-frame resolution
improvement when their differences contain measured information. Generated
intermediate frames do not. For parchment, lighting/wavelength changes are
usually a more relevant acquisition question than cinematic video generation.

### Research that supports this direction

- [En-Gedi virtual unwrapping, Seales et al., 2016](https://pmc.ncbi.nlm.nih.gov/articles/PMC5031465/)
  demonstrates computational access to writing inside a charred biblical scroll.
  Our [existing En-Gedi registration experiment](EN_GEDI_REMERGE_REGISTRATION_2026-09-06.md)
  failed its geometric gate; the published achievement does not validate our
  unregistered regions.
- [Vesuvius ink-detection tutorial, updated September 6, 2026](https://scrollprize.org/tutorial5)
  describes learning ink cues from measured CT neighborhoods. Its practice of
  keeping the detection input smaller than a whole letter is an especially useful
  design precedent: linguistic plausibility should not determine physical ink
  labels. These models are not automatically applicable to Hebrew parchment.
- [Kurar-Barakat and Dershowitz, 2024 preprint](https://arxiv.org/html/2411.10668v1)
  describes spectral ink/parchment segmentation and provides the 20-fragment
  QSD reference used below. This is MTEM, a thresholding and energy-minimization
  method, not a generative language model. Its public data permit direct tests
  of physical-image processing. The paper distinguishes the publicly displayed
  color/last-band images from other bands obtainable from the custodian on
  request; the released subset supplies first and last bands.
- [Perino et al., 2023](https://arxiv.org/abs/2311.01130)
  presents overlapping-character segmentation as a proof of concept for a
  Priscian palimpsest. It motivates an undertext experiment, without establishing
  performance on our Greek/Syriac or Hebrew targets.
- [Aeneas, Assael et al., 2025](https://www.nature.com/articles/s41586-025-09292-5)
  retrieves parallels and proposes missing text of variable length in Latin
  inscriptions. Adaptation and testing would be required for biblical material.
- [Apollo Restore, September 2026 preprint, revision October 7](https://arxiv.org/abs/2609.22455v4)
  reports Greek gap completion with a 24-billion-parameter model. Its abstract
  reports top-20 candidate results, not certainty in a single restoration.
  It is a promising candidate generator for Greek witnesses; weights, runtime,
  data contamination and passage-specific accuracy remain to be evaluated here.
- [Stoicheia, August 2026 preprint](https://arxiv.org/abs/2608.07249v1)
  reports character-level masked diffusion and released folds designed to omit
  particular training passages. This is relevant to testing memorization.
  Check actual corpus overlap and checkpoint provenance before calling any
  biblical test held out; the abstract's claims have not been replicated by POB.

The last two entries are research leads assessed from their primary abstracts,
not model installations or independent benchmark confirmations. Their presence
in this report does not change the project's established transcription gates.

## How to use completion without circular reasoning

Keep the camera observation, processed view, diplomatic transcription, supplied
completion and proposed ancestor in separate fields. Store uncertainty at the
letter or span that is uncertain. A Greek reading may constrain possible Hebrew
wording without uniquely recovering it; Hebrew pointing is a further question.

For a missing span, generate several candidates and an explicit unresolved
option. Test each against remaining ink, plausible character widths learned
from that scribe, line/column geometry, grammar and independent comparison
witnesses. A fit to a standard edition is one prior, not the answer key. Report
which candidates the physical constraints exclude and which remain compatible.
Do not convert model likelihoods or a model's verbal confidence into historical
probabilities without calibration.

One promising research design is candidate-to-observation testing: simulate how
each proposed letter would look through a measured blur/noise process, then
compare the predicted traces with the original capture. Learn glyph variation
from that scribe, preserve competing shapes and marginalize over plausible
damage. This is a proposed inverse-imaging experiment, not an implemented
capability. A large lost region may leave many equally good solutions. Display
reconstructions remain outside the transcription and source-evidence workflow.

For calibration, use real paired exposures and published diplomatic references
where available. Synthetic damage can supplement these controls, but must be
evaluated separately from genuine aging and loss. Hide a complete passage and
its duplicate/parallel copies during training; a random crop split is inadequate.
Include authentic scribal variants against familiar printed editions, scrambled
or nonbiblical controls where appropriate, and blank/physically absent regions.
Pretraining contamination of closed models cannot be fully audited; record it
as unknown rather than claiming complete blinding.

Score physical segmentation, character recognition and gap completion
separately. Measure false ink, missed ink, character error, incorrect confident
readings, abstention coverage and top-k completion accuracy by gap length.
Do not let a long easy passage dilute failure at one consequential letter.
Report results by manuscript, script, damage and imaging modality. Freeze a new
evaluation set before tuning; the QSD experiments below are development work.

## Concrete biblical target queue

This is a bounded imaging track authorized for this session. It complements
the [active source-comparison portfolio](TEXTUAL_RESTORATION_PRIORITIES.md),
and does not reopen every completed verse review.

| Priority | Target and current evidence | Discriminating next input | Possible contribution |
| --- | --- | --- | --- |
| 1 | Zuqnin Greek Ezekiel undertext, especially the unreadable column assigned around 39:22-24 on current 107r | Correctly mapped native photographs; real spectral/UV exposures if available; separate Greek and Syriac orientation masks | New readable Greek letter sequence or a firmer preservation boundary |
| 2 | 4Q122, Deuteronomy 11:4, damaged marks beside the central hole | Actual full-resolution color/IR pair and the edition's plate; the old run received only 1200-square files despite larger advertised dimensions | Test whether disputed strokes survive and whether the conventional word identification can be strengthened |
| 3 | Mas1d, Ezekiel 36:26-28, observed versus supplied renewal language | Exact original plate/exposure and letter-level survival map | Clarify which spirit/renewal wording is physically preserved; do not count supplied words as attestation |
| 4 | En-Gedi, a development region with mask-valid coordinates | Local distortion/segment-to-master mapping and correct CT indexing | Establish a genuinely registered region for later ink testing; no retuning the old failed affine result |
| 5 | Fragment joins in the existing biblical Genizah inventory | Reusable paired images, scale and recto/verso relationships | Recover continuity through a physical or securely demonstrated textual join |

The first target follows the
[actual Zuqnin preservation report](EZEKIEL_36_ZUQNIN_GREEK_RENEWAL_2026-10-13.md).
It is not evidence that 39:29 survives there. A successful reading around
39:22-24 must not be used to fill an unrelated absent verse. Start with already
readable nearby Greek as a same-leaf development control, then freeze a separate
region before testing damaged writing. The [Vatican viewer](https://digi.vatlib.it/view/MSS_Vat.sir.162)
offers study imagery; this session has not established a raw spectral stack for
107r. A renamed color channel is not a new wavelength measurement.

The [4Q122 record](4Q122_DEUT11_IMAGE_FOLLOWUP_2026-09-06.md) supplies exact
institutional image identifiers and the acquisition limit. Its completion
candidate must preserve the difference between the Greek adjective and the
Hebrew source. The [Masada comparison](EZEKIEL_36_LONGER_FORM_EVIDENCE_2026-10-12.md)
defines the renewal-language question. The unrelated, untracked Genizah working
file in the shared checkout is not part of this session's changes.

QSD plate identifiers are not yet mapped here to biblical manuscript identities.
QSD is a method-development reference, not an addition of 20 biblical witnesses.
Choose the first actual target by usable input quality and consequence, not by
which generated completion looks most dramatic. Failure to obtain a new
measurement is an acquisition limit, not proof that the manuscript is unreadable.

## Evidence needed for a discovery claim

1. Identify the physical object, leaf, line and exact surviving area, with original
   files or a stable custodial reference and reproducible processing settings.
2. Demonstrate the new reading against the original measurements, including
   plausible alternative shapes and processing artifacts. Preserve all failures.
3. Check whether editions, apparatuses or prior imaging already report it. A
   project-first reading and a scholarship-first decipherment are different claims.
4. Apply the established blinded transcription and separate source-selection
   process. Multiple models can share errors; agreement is not calibration.
5. State the exact implication: a corrected transcription, stronger attestation,
   proposed historical text, English revision, or disclosure only.

No commissioned human review is made a prerequisite here; existing project
policy uses computational review and published scholarship. Where independent
calibration is unavailable, retain the corresponding uncertainty. A scholarly
novelty claim needs a literature check beyond this session's technology survey.

## Access and preservation

Retain originals and record checksums, actual received dimensions, spectral band
and exposure metadata, orientation and coordinates. Keep a crop map back to
the source. Preserve failed experiments and unknown labels. Distinguish a
published processed image from raw sensor data; multiple exposures are one
manuscript, not multiple independent textual witnesses.

The upstream QSD repository labels its code MIT. That label is not treated as
a blanket relicensing of custodial manuscript photography. Downloaded research
images remain in the private workspace cache; Git receives code, metrics and
locators only. The Leningrad source's existing provenance record reports a
public-domain reproduction label and its limitations. The generated test is
kept as an explicitly labeled local diagnostic. No custodians or researchers
have been contacted and no access controls are bypassed.

## Experiments fixed before execution

### Published spectral segmentation reproduction

Use the Qumran Segmentation Dataset and released predictions at upstream commit
`22e09c6219b16dafdf3a943fb18df774f7e3e8e8` from
[the authors' repository](https://github.com/TAU-CH/qumran_segmentation_of_ink_and_parchment_in_dead_sea_scroll_fragments).
Evaluate all 20 identifiers in the upstream ground-truth ink-mask directory.
Compare MTEM ink against ink annotations, and MTEM and Otsu parchment against
parchment annotations. Use foreground values greater than 127, matching the
authors' evaluator. Record TP, FP, FN and TN, per-fragment precision/recall/IoU/F1,
and macro and pooled summaries. Keep empty annotations and empty predictions
visible; report undefined denominators as null. Separately reproduce the
authors' averaging rule, which skips pairs where both masks are empty and uses
zero for undefined metrics. Do not tune parameters or exclude poor fragments.

This is a reproduction of released segmentation outputs, not fresh inference,
a new training run, a blind evaluation, or Hebrew recognition. It can establish
whether an external measurable reference is usable and whether claimed aggregate
performance conceals failures relevant to future recovery. Author annotations
are reference labels, not guaranteed physical truth.

Keep downloaded images outside Git. Pin the upstream commit, verify downloaded
Git blob identities, and record SHA256 values. No passage identity or manuscript
independence is inferred from photographic plate numbers. No new source letters
or translation changes may be inferred from segmentation scores.

### Generative image fidelity probe

Use only the already acquired 900 by 640 Leningrad context PNG, SHA256
`8cb788a1ebbac1dfb39b68728b2bd1c94d808f4220edc9e209564c31e28b0cae`.
The existing character-label disagreement remains unresolved. This experiment
does not reopen that transcription vote or use the image as a character gold
standard. It tests whether a generative edit preserves observable geometry.

Send one built-in ImageGen edit with the following prompt, without the passage,
expected wording, edition, or former transcriptions:

> Use case: precise-object-edit. Asset type: labeled research diagnostic, never
> manuscript evidence. Input image 1 is the sole edit target, a photograph of
> manuscript writing. Increase the visibility of the existing strokes using
> restrained contrast improvement. Preserve every visible stroke, dot, gap,
> line position, stain and parchment boundary. Do not infer or complete any
> missing letters or words. Do not replace handwriting with typography. Preserve
> the entire input rectangle and its proportions. Place the processed image
> above a separate footer reading exactly "AI-GENERATED TEST - NOT MANUSCRIPT
> EVIDENCE". Do not put the footer over source pixels. If a feature is unclear,
> keep it unclear. Do not add writing elsewhere.

Inspect for changed line topology, omitted or invented marks, and altered
geometry. Even apparent success would not establish pixel fidelity, new ink,
recognition accuracy, or a recovered letter. Record the complete prompt and
actual output, including a failed attempt; do not select a favorable rerun.
Generated output is a local diagnostic outside the evidence and transcription
directories. It is never fed into source collation or translation decisions.

### Fresh two band machine learning development test

After inspecting the released-mask evaluation, run a deliberately small new
classifier on the measured 445 nm and 924 nm TIFFs. The poor result for
`124_008` motivates the test; therefore it is development evidence, not blind
validation. Use all 20 fragments, with `124_001` alone supplying training labels.
Sample at most 10,000 pixels per reference class with NumPy seed 1776. Predict
ink, non-ink parchment, and other background with OpenCV RTrees, 100 trees,
maximum depth 12, minimum sample count 10, two active features, and seed 1776.
Features are band 1, band 12, and their difference, each scaled by 65535.
Compare against a single-band version using band 12 alone with one active
feature. No textual input, neighboring verse, or language model is supplied.

Score all pixels using the same ink metrics, with the training fragment
explicitly excluded from the 19-fragment evaluation summary. Include
`690_015` and `690_016` as empty-annotation controls, not proven blank material.
Do not tune after inspecting results. Adjacent fragments may share a manuscript,
and these annotations and failures are already public and inspected; this split
tests transfer across these images, not manuscript-disjoint generalization.
It does not reproduce MTEM's algorithm or constitute a fair model-selection
contest with its published results. No new bitmap is generated or edited:
predictions are measured in memory and only numeric results are saved.

## Reproduction and validation

Use a Python environment with NumPy and Pillow for the released-mask check;
the fresh classifier additionally requires OpenCV with `cv2.ml.RTrees_create`.
No cloud training or paid compute is required by these scripts. Run from the
repository root, using an external cache rather than committing source imagery:

```sh
python tools/textual_restoration/evaluate_qsd_release.py \
  --cache /path/to/private/qsd \
  --output /path/to/private/qsd-release-result.json
python tools/textual_restoration/probe_qsd_spectral_classifier.py \
  --cache /path/to/private/qsd \
  --release-report /path/to/private/qsd-release-result.json \
  --output /path/to/private/qsd-spectral-result.json
python -m unittest discover -s tests -p test_qsd_metrics.py -v
```

The scripts verify pinned upstream blob hashes and refuse to overwrite differing
results. They do not modify input images. Runtime versions and tool hashes are
in the saved reports; bitwise model reproduction on another OpenCV build is not
assumed. Four focused unit tests cover count arithmetic, empty-pair semantics,
false ink on an empty reference and shape mismatch. These are metric-integrity
checks, not proof of paleographic accuracy. No source-text application is made.

## Decision and next stopping point

Continue the recovery program with **measured spectral data and explicit
completion hypotheses**. The reproducible dataset, actual model experiment,
generative counterexample and acquired Zuqnin target make this an executable
research route rather than a general aspiration. This session has not recovered
a previously unread biblical letter or justified changing the Hebrew or English.

The next bounded source deliverable is a registered, source-backed observation
on surviving Zuqnin Greek undertext, with alternatives and exact preservation
limits. Start by identifying the Greek columns against the edition, then seek
a genuinely better measured capture where necessary. If only the present
limited photograph is available and no defensible new stroke can be isolated,
record the exact acquisition need and move to the next usable target. Keep
textual completion proposals in the apparatus until the separate source argument
supports a stronger status. A method paper or a working reconstruction may be
worth publishing, but neither should be advertised as recovered original ink.
