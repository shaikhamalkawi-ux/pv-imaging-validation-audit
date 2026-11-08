# 99pv R52 — Sandia original-source metadata: physical-parent split and non-imaging prediction control
**8 November 2026 | Status:** `PASS_ORIGINAL_METADATA_REGRESSION_CONTROL` / `HOLD_EL_PIXEL_MODEL_PERFORMANCE` / `NO_CAUSAL_LEAKAGE_CLAIM`.

## Source, protocol and admission
This **additive** experiment extends R50–R51 without changing their original data or scientific conclusions. It independently uses the original public Sandia PV-IV-EL `AnonDB.csv`, 254,907 bytes and SHA-256 `8fe450440d989f9aa469f0fc206c76b13021a93dbb6071ddc3a1967fd083440e` (Sandia/OEDI dataset DOI `10.11578/3818365`, <https://data.openei.org/submissions/8378>). As recorded in R51, the file contains 616 metadata rows, 438 modules identified by `Mod_ID`, and 613 distinct IV paths. Three IV paths occur twice with distinct EL acquisitions. Source rows were **not** deduplicated or edited.

R52's outcome-specific pre-analysis specification in `PREOUTCOME_PROTOCOL_LOCK.md` was saved **before** any R52 predictive scores were examined, SHA-256 `dba0dc2424c8a2bcbf9c1028107e01007d60929005c89a680ba27db54e72b7bc`. The subsequent within-test `seen/unseen` subgroup check was defined **after** the primary result was read and is explicitly exploratory; its independent short protocol SHA is in `R52_EXPLORATORY_SUBGROUP_SUMMARY.json`.

## A different measured endpoint, NOT a PV defect detector
The original source has contemporaneous, physically measured IV peak power `Pmp_(W)` and nominal nameplate `Nameplate_Pmp_(W)`. The fixed target is their ratio, measured Pmp/nameplate Pmp; 18 source rows lacking a usable nameplate denominator were excluded according to the prewritten eligibility rule. The **598 eligible rows** represent **420 modules**. R50's broader 616-row metadata split findings remain valid and separate.

The fixed non-imaging predictor Ridge(alpha=10) uses manufacturer/model and wafer type as categorical inputs, plus nameplate power, module area, reported outdoor-exposure days, and reported exposure step. **No pixels, EL image feature, physical module ID, IV curve derived power/voltage/current, target date, or target variable are given to Ridge.** Preprocessing is fitted on training only; no target-label-based model or hyperparameter selection occurred.

For each of 100 frozen seeds, random-row and `Mod_ID`-grouped partitions select **120 test rows**, with the remaining 478 for fitting. Both versions are repeated over the same dataset and nominal split size, but their test module populations differ; this is a descriptive evaluation-design comparison, not a causal randomized experiment.

## Executed numerical results, 100 seeds per partition type

| Fixed model/control | Random-row MAE (ratio percentage points) | Unseen-Mod_ID MAE (ratio percentage points) |
|---|---:|---:|
| Nameplate constant (prediction = 1.0) | 1.9735 | 1.9656 |
| **Non-ID Ridge metadata model** | **0.8650** | **0.8790** |
| Retrospective same-ID target-mean *negative control* | 0.9273 | 0.8790 |
| Strict earlier-IV same-ID lookup *negative control* | 0.8967 | 0.8790 |

The original eligible cohort has a mean **56.17** shared `Mod_ID` per random-row train/test partition, whereas every module-grouped partition has zero; the fraction of 120 row-test observations whose module also occurs in training averages **47.5083%** under row-wise partitions. A mean 0.97 original `IVPath` strings cross a row-wise split and zero cross a grouped split. These are direct source-metadata overlaps, not proof of duplicate images or published-model contamination.

The generalizable non-ID Ridge has only **0.0140 percentage points lower** mean MAE in row-wise partitions (0.8650 vs 0.8790). In 57 of 100 same-seed comparisons row-wise MAE is lower; in 43 grouped MAE is lower. The per-seed descriptive row-minus-grouped contrast ranges from **−0.3041 to +0.2723 percentage points** and is often either sign. Those 100 seeds share one dataset and are not 100 independent field studies; **no statistical significance or causal optimism claim is made**.

The retrospective target lookup is not a deployable method: it can use an observation of the same module whose IV measurement occurred after the evaluated row. Its worse mean performance than Ridge is reported faithfully, not discarded. The strictly earlier-IV variant is also not an image model and has its own eligibility/selection limits.

## Exploratory within-test interpretation (same trained model, same 120 test rows)
To reduce the between-split-population ambiguity, the later declared exploratory R52B audit holds each random-row Ridge training set and *its* test predictions fixed, then divides each held-out row into `Mod_ID` **seen** versus **unseen** in the same training set:

- Seen rows: **57.01** per test on average, MAE **0.8125 percentage points**.
- Unseen rows: **62.99** per test on average, MAE **0.9118 percentage points**.
- Seen-minus-unseen: **−0.0993 points**, with a seed-level range from **−0.4566 to +0.1925**; the seen subset has lower error in **75/100** fixed-seed partitions.
- Equal test-module weighting: mean seen MAE **0.8061** versus unseen **0.9255** percentage points.

Every Ridge overall MAE recalculated in this separate R52B script agrees with the frozen R52 primary output at tolerance `1e−10`. **These are two differently composed physical-module subpopulations, not a controlled within-module treatment comparison.** We have not established whether type, time, underlying degradation or source selection accounts for the difference. Do not call it a measured leakage penalty or report a causal effect size.

## What the combined R50–R52 evidence now supports
1. **Physical provenance affects evaluation membership.** In the original 616-row R50 source experiment, random-row splitting led to a mean 55.17 overlapping physical module IDs; grouping gave zero. This is genuine audited metadata, not a review conjecture.
2. **The valid inference changes with the test-unit definition.** A random-row score partly evaluates new measurements of modules known from fitting; a grouped score evaluates unseen `Mod_ID`s under otherwise identical task definitions. An unqualified score obscures that distinction.
3. **Performance inflation is not automatic.** The new simple metadata-only Ridge model did not exhibit a large positive score bias under the random-row protocol. The data themselves contradict any attempt to infer a universal performance penalty merely from the existence of module overlap.
4. **Source constraints matter.** R51's 613 IV curves versus 616 EL-acquisition rows, and 600 two-channel EL rows with only 479 within ±7 days of IV date, remain important if a future genuine EL-to-Pmp pixel model is attempted. The current R52 prediction is a **non-imaging control** and does not require same-date EL.

## Hard scientific boundaries and next valid gate
No EL images, masks or actual IV curve bytes were accessed in R52; no fault labels, thermographic detector or classifier were re-trained. This cannot change any original PV segmentation paper's reported mIoU, F1 or claimed module-level physical independence, and cannot estimate how often prior studies used a contaminated holdout. The original Pratt/BenchmarkELimages 2023 paper has 593 annotated images while three later public version trees have different counts; candidate filename-family overlaps remain distinct from verified module IDs. The original author benchmark-to-release mapping is still not fully verified.

**Next meaningful research:** independently acquire a **version-pinned, licensed pixel/label or pixel/IV subset** (e.g. Sandia EL.zip with matching IV, or an openly released EL segmentation benchmark with verified source-image→module parents); re-run the *same model and target* on random-image vs physically grouped splits. Until that input is available, keep actual **EL model-performance shift HOLD**, rather than treating a metadata-only regression as a completed image experiment. Formal 99pv original-study identity, full-text eligibility, final PRISMA/PRISMA-S and independent human arbitration also remain unclosed.

## Reproducibility package and integrity
- Primary script: `src/run_metadata_control.py` (all 200 split/prediction cases), primary protocol and original-source SHA lock.
- Additive exploratory script: `src/seen_unseen_exploratory.py`, locked post-outcome subgroup protocol, independent primary-metric numerical cross-check in all 100 random seeds.
- Raw numerical ledgers: `results/R52_ALL_200_SPLITS_METRICS.csv`, `results/R52_SUMMARY.json`, `results/R52_EXPLORATORY_SEEN_UNSEEN_100_SPLITS.csv` and summary JSON.
- Two figures are explicitly labeled non-imaging metadata controls. No original 254,907-byte third-party CSV is redistributed in the author-facing ZIP; load it via the separate controlled R50 source with proper Sandia attribution.
- Authoritative source: Jennifer Braid, Brandon Byford et al., **Photovoltaic Module Current-Voltage and Electroluminescence Image Data**, Sandia National Laboratories, DOI `10.11578/3818365`. Related methods journal paper listed by Sandia `10.1109/JPHOTOV.2025.3562931`.

**Editorial disposition: KEEP as modest non-imaging negative-control and claim-identifiability evidence. HOLD as proof of AI image-detector performance change or method novelty by itself. R47 main manuscript and all frozen prior research stages unchanged.**
