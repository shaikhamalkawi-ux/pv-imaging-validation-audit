# PV Imaging Validation Audit — Project 99pv

**Scientific identity:** dataset ancestry, physical sample units, model selection and result-specific evidence support for AI-assisted photovoltaic imaging research.

**Status:** **R57 WORKING RESEARCH — reproducible source-only and non-imaging additions; NOT submission-final, NOT a completed systematic review, NOT a certified leakage detector.** R55 frozen predecessor retained unchanged.

This archive publishes reproducible **code and bounded derived analyses**, including a source-verified Sandia module-ID partition experiment, a fixed **non-image** electrical-power metadata control, a pinned public EL Git-tree filename lineage study, and an exact source-table reanalysis of a published multi-plant IR result. It also contains the prospectively locked, but **not-yet-run on real images**, R53 pixel experiment.


**Public code source:** [GitHub repository](https://github.com/shaikhamalkawi-ux/pv-imaging-validation-audit); audited R54 65-file source snapshot: [commit `b0bf66f96700`](https://github.com/shaikhamalkawi-ux/pv-imaging-validation-audit/commit/b0bf66f9670000297986569dab6de85d55bec822). The [public reproducibility checks](https://github.com/shaikhamalkawi-ux/pv-imaging-validation-audit/actions/runs/42437282067) passed. A GitHub check validates source-table arithmetic, declared metadata and synthetic tests; it does **not** substitute for raw Sandia images or a completed independent eligibility review.

## Latest working research: R57 (8 November 2026)

The R57 source-only development update adds (1) a fixed 139-record future-date Sandia IV evaluation test and comparison of two frozen non-imaging Ridge training supports, and (2) primary-author thesis evidence qualifying provenance of the Pratt 2023 EL segmentation release family. An independent original-CSV Ridge Cholesky calculation reproduced the source T02 MAEs to numerical precision. R57 did NOT train an EL pixel model, prove paper-specific leakage, complete systematic screening, or change any frozen R55/R54 results.

- [R57 combined main + supplementary (PDF)](paper/R57_MAIN_PLUS_SUPPLEMENT.pdf).
- [R57 main manuscript (PDF)](paper/R57_WORKING_MAIN.pdf) and [R57 supplementary PDF](paper/R57_WORKING_SUPPLEMENT.pdf).
- [R57 main/supplement LaTeX source](paper/) and [R57 scientific admission and QA register](docs/R57_SCIENTIFIC_ADMISSION_AND_QA.md).
- [R57 verified public CI run](https://github.com/shaikhamalkawi-ux/pv-imaging-validation-audit/actions/runs/42439452937) and [PDF build QA](https://github.com/shaikhamalkawi-ux/pv-imaging-validation-audit/actions/runs/42439452911).

## Read the paper

- [R55 main manuscript (public-code-linked PDF)](paper/R55_WORKING_MAIN.pdf) — **working research, not final PRISMA**.
- [R55 scientific supplement](paper/R55_WORKING_SUPPLEMENT.pdf) — source boundaries and data-vintage controls.
- [R55 combined manuscript + supplement](paper/R55_MAIN_PLUS_SUPPLEMENT.pdf) — one 13-page reader copy.
- [R54 baseline main PDF](paper/R54_WORKING_MAIN.pdf) and [supplement](paper/R54_WORKING_SUPPLEMENT.pdf) — original frozen development documents.
- [Archived R47 development draft](paper/archive/R47_WORKING_MANUSCRIPT_7P_READONLY.pdf).

## What is actually reproduced?

| Original evidence route | Executed result | Stronger claim **not** supported |
|---|---|---|
| Bommes (2022), source-reported Table 5 | 54 AUROC cells; 3 of 9 selection-dependent model orderings | Leakage proof, causal score inflation, new model runs |
| Sandia PV-IV-EL official CSV (616 rows) | 100 random-row splits: 55.17 shared `Mod_ID` on average; 100 module-group splits: 0 | Published paper contamination or site-external validation |
| Sandia fixed non-ID Ridge on 598 metadata rows | MAE: 0.8650 vs 0.8790 ratio percentage points, random/grouped | EL pixel model or defect detection; universal optimistic bias |
| Pratt/BenchmarkELimages public dated Git trees | 0 identical train/test filenames but 22/33/34 shared parsed **candidate** filename families | Proven shared physical modules or original-paper segmentation score shift |
| Sandia R54-T01/T02 / R57 source replay | Same 139 later test records: non-imaging MAE 1.3691 vs 1.6411 ratio pp when 59 shared-module early records excluded | Causal overlap effect, EL defect recognition, or new site transfer |
| Pratt 2024 original doctoral thesis | 2021 release associated with 2023 paper family; CFVS example encodes module number and cell coordinates | Exact trained-study Git commit, all source serials, published-score impact |
| Sandia R53 EL pixel protocol | Code and prospective design only | **Any image-based score** — `EL.zip` source not yet replayed |

## Reproduce

See [REPRODUCE.md](REPRODUCE.md) and [case source documentation](DATA_AND_RIGHTS.md).

**Offline (does not need Sandia CSV or EL images):**

```bash
python tests/verify_public.py
python tests/verify_r57_public.py
python cases/benchmarkel_r50b/benchmarkel_git_tree_audit.py --selftest
```

**Full R52 metadata replay requires the exact official `AnonDB.csv` bytes**, obtained from the dataset owner and verified against SHA-256 `8fe450440d989f9aa469f0fc206c76b13021a93dbb6071ddc3a1967fd083440e`.

## Source and publication boundaries

- Sandia original: [PV-IV-EL dataset](https://doi.org/10.11578/3818365) — official data and imaging source. The official catalog reports 613 IV/EL measurement sets and 438 physical modules; the preserved source CSV has **616 acquisition rows** and **613 distinct IV paths**. The precise catalog counting convention is unresolved.
- Pratt et al. (2023): [EL segmentation benchmark](https://doi.org/10.1016/j.sasc.2023.200048). The original author's [2024 doctoral thesis](https://hdl.handle.net/10539/42163) ties the early release to the study family and gives an explicit CFVS crop-name interpretation, but an exact 2023 trained checkpoint-to-Git-commit and all individual physical serial identities are still unverified.
- Bommes et al. (2022): [IR source paper](https://doi.org/10.1002/pip.3518). Table-5 values are credited to the original authors.
- No original third-party EL imagery, IV traces, licensed bibliographic database exports or publisher PDFs are redistributed here.
- Work involving AI-assisted drafting and code is transparently disclosed; independent final author verification, publisher permission review, journal/author metadata and full PRISMA remain pending.

See [PUBLICATION_STATUS.md](PUBLICATION_STATUS.md), [DATA_AND_RIGHTS.md](DATA_AND_RIGHTS.md), [CITATION.md](CITATION.md), and the preserved [R54 integrity register](MANIFEST_R54_SHA256.json) before reusing results.
