# Project 99pv R52 — Sandia ORIGINAL metadata-only predictor negative-control pilot
**Frozen design timestamp: 2026-11-08 (Asia/Dubai), before examining any model scores.**

## Aim and scientific identity
Test how the *evaluation estimand and observed predictive error* depend on whether source metadata rows from the same identified physical photovoltaic module may appear on both sides of a train/test split. This is a non-imaging **metadata-to-IV-Pmp** regression demonstration, never a defect-detector result, raw EL image result, or a rerun of a prior published experiment.

Source: Sandia PV-IV-EL, original immutable `AnonDB.csv`, DOI 10.11578/3818365; SHA-256 8fe450440d989f9aa469f0fc206c76b13021a93dbb6071ddc3a1967fd083440e (254907 bytes, 616 rows, 438 Mod_ID). R51 separate parent/acquisition metadata and R50 split audits remain unchanged.

## Fixed target and eligibility
Target is `Pmp_(W) / Nameplate_Pmp_(W)`: measured contemporaneous IV peak power divided by published module nameplate power; both fields must be positive, finite and present. Exclude rows where the denominator or numerator is unavailable/nonpositive. This target has no defect class and is not a measured crack mask. The imaging archive is not downloaded. Full original 616 rows remain untouched.

## Predictor / observation features fixed before scoring
Categorical: `Make`, `Model`, `Cell_Wafer_Type`. Numeric: `Nameplate_Pmp_(W)`, `Module_Area_(cm2)`, parsed day number from `Total_Exposure` ('OE N days'), and `Exposure_Step`. No `Mod_ID`, `IVPath`, EL image filename, measured IV Isc/Voc/Imp/Vmp/FF/Pmp, current IV acquisition settings, reference IV values, or outcome scores as features. IV acquisition dates are used only to restrict a same-module prior-measurement negative-control, not as predictors. All categorical encoding, median imputation and feature scaling must fit on training only.

## Fixed comparison design
100 deterministic seeds `20261108...20261207`, 20% holdout (rounded for eligible cohort); each seed executes two independently generated partitions: (A) uniformly shuffled eligible metadata rows; (B) whole-module-group allocation using `Mod_ID`, approximately 20% rows and always no module ID overlap. Audit whether exact test sizes match. NO target-informed split selection, no exclusion of unfavorable seeds, no hyperparameter tuning on test.

## Fixed predictions
0. Physical baseline: `ratio_hat=1.0` (module nameplate power predicts measured Pmp).
1. General predictor: one-hot encode categories (handle unknown), median-impute and z-scale numeric, fixed Ridge(alpha=10.0). Never include module ID.
2. Retrospective module-identity *negative control*: where a test row's `Mod_ID` is in train, predict training mean target for that module; otherwise use Ridge. This *does not* ensure training measurements precede test; thus operationally inadmissible, used solely to expose the distinction.
3. Date-valid module-prior lookup negative control: use the **latest** training row with the **same Mod_ID** and STRICTLY EARLIER IV_Date than test, otherwise use Ridge. This is only a metadata/electrical prior and does not imply use of an EL image.

Primary descriptive outputs: for each model/split, mean and range across 100 seeds of test MAE on normalized ratio (percentage points) and MAE Pmp in W; pooled count of prior-eligible test rows. Also report test physical-ID overlap, count of same `IVPath` in both partitions and subset class/plant distribution. No p-values or deployment-site claims.

## Scientific guards
Differences between random-row and grouped holdouts are descriptions of different test populations, not causal bias or proof that actual historical papers used unsafe splits. A lookup using `Mod_ID` is NOT an AI/EL classifier. A more accurate result on the random-row split cannot be equated with 'leakage observed in previous literature'. No inference about physical site independence beyond `Mod_ID`. No images/curves, model checkpoint, fault label, external plant or paper-specific split was accessed. If code/execution fails, record HOLD; do not forge a result. Do not alter R37/R43/R44/R47, R50/R51 or source CSV.
