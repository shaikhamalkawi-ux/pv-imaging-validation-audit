# R57 Pratt primary-author thesis and source-stratum crosswalk

Source: Lawrence Pratt, 2024 doctoral thesis, University of the Witwatersrand, <https://hdl.handle.net/10539/42163>. The official university PDF contains the original author's release-family chronology (Chapter 1), selected test-cohort descriptions (Chapters 5 and 7), and explicit CFVS-00035-r8-c4 example (Chapter 7). The exact number 00035 denotes an author-described MODULE number in this example; r8/c4 denote its cell row/column. This is not a serial-number-verified mapping for all ARTS, CFVS or CSIR files.

Pratt's thesis says the 2021-11-04 dataset release stores data for the second paper, Pratt et al. (2023). It reports 582 original images/masks = 478 train + 54 validation + 50 test, and 1912 training including three augmented variants per training original. The printed 593 count in the separate journal work remains an 11-record alignment HOLD, not proof of erroneous model results. The source test images were deliberately enriched for defects; deployment representativeness is not established. The thesis says training-only augmentation was performed after partitioning.

Upstream exact original Git-tree commit:
<https://github.com/TheMakiran/BenchmarkELimages/tree/768b5e78596b429829b6b7aceb0ce4ac7b07788d>.

Independent source-stratum counts (ARTS/CFVS/CSIR) were recalculated from nine matching, nontruncated original Git subtree API responses. The results are stored in R57_STRATUM_LINEAGE.json. Each source key is a strictly parsed filename prefix before _r<number>_c<number>; BMRK/SDLE names remain UNPARSED, not considered independent.

| Release | Train/test original or listed paths | Shared parsed prefixes | Test crops on shared prefixes | Unparsed tests |
| --- | --- | ---: | ---: | ---: |
| 20211104 | 478 / 50 | 22 | 24 | 11 |
| 20220723 | 2044 / 66 | 33 | 35 | 8 |
| 20221008 | 2212 / 72 | 34 | 36 | 8 |

Public replay, network required: run the existing cases/benchmarkel_r50b/benchmarkel_git_tree_audit.py with a local output JSON path. That source verifies the pinned tree SHA names and aggregate 22/33/34 results. R57 extends it with author-thesis context and source-specific independent counts. The offline tests/verify_r57_public.py checks arithmetic against stored source-stratified evidence without downloading image pixels.

Hard HOLD: study-to-exact-commit equality, original 2023 trained model manifest, physical module IDs for every file family, source-acquisition ancestry and any change in published mIoU/F1. This is original-document and public-tree evidence only; no third-party original pixels or thesis PDF are redistributed here.
