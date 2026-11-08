# 99pv R50 — An executed three-release EL imaging dataset/source-family audit

## Scientific advance beyond the Sandia source-count theorem
We independently inspected **the actual public GitHub Git-tree filename manifests** from three timestamped EL defect-segmentation dataset releases within `TheMakiran/BenchmarkELimages`. This is **an executed, pinned repository-directory analysis**, not a mathematical hypothetical and not a raw image/pixel replay. GitHub connector REST queries were issued against exact tree SHA-1 identifiers (not loosely against dynamic screenshots). Each requested leaf tree responded with its expected hash and `truncated=false`. The commit shown by repository API was `768b5e78596b429829b6b7aceb0ce4ac7b07788d`. No binary images/masks were downloaded or redistributed.

**Original dataset/paper sources:**
- Pratt, L. E., Matheus, J., and Klein, R. (2023). *A benchmark dataset for defect detection and classification in electroluminescence images of PV modules using semantic segmentation.* Systems and Soft Computing 5:200048. DOI **10.1016/j.sasc.2023.200048**; publisher https://www.sciencedirect.com/science/article/pii/S2772941923000017 . The article reports a source benchmark of 593 cell images, 50 test images and multiple semantic segmentation methods. *The pinned repository release counts below are NOT necessarily the exact code/data vintage used to produce that publication's reported scores.*
- Official author/project repo: https://github.com/TheMakiran/BenchmarkELimages . Its README describes the three successive labeled dataset releases, original versus augmented train images, and source lab/manufacturer origins (ARTsolar, CFV Labs, CSIR, etc.). Access: 8 November 2026.

## Prospective parser and exact (not guessed) source partition
The strict parse is the prefix before `_r[integer]_c[integer]` in filenames like `ARTS_00001_r4_c2.png` and `ARTS_00001_r6_c2.png`. We call it a **filename-family source candidate key**, **NOT** a verified physical module ID. This only covers the ARTS/CFVS/CSIR naming pattern. BMRK and SDLE patterns were deliberately left UNPARSED; their physical parent semantics remain unknown. Literal crop filenames and augmentation-normalized crop IDs are separately checked. No word “leakage” is licensed by prefix matches alone.

| Pinned repo release | Train listed | Val listed | Test listed | Exact same filename train/test | Shared parsed filename-family keys train/test | Test files with parsed key also found in train | Test files not parsed |
|---|---:|---:|---:|---:|---:|---:|---:|
| `dataset_20211104` | 478 original (+1,434 augmented separately) | 54 | 50 | 0 | **22** | **24/50**, or 24/39 parsed | 11 |
| `dataset_20220723` | 2,044, incl. augmentation; 511 distinct normalized originals | 65 | 66 | 0 | **33** | **35/66**, or 35/58 parsed | 8 |
| `dataset_20221008` | 2,212, incl. augmentation; 553 distinct normalized originals | 70 | 72 | 0 | **34** | **36/72**, or 36/64 parsed | 8 |

**Concrete source-level example:** train `dataset_20211104/images_train_original/ARTS_00001_r4_c2.png`; test `dataset_20211104/images_test/ARTS_00001_r6_c2.png`. The filenames are different; the candidate family prefix `ARTS_00001` is shared. The claim that the prefix represents one actual module or original image is **HOLD** until author file-naming semantics or source-to-crop manifests are acquired.

**Positive source control:** v20211104 has 478 *original* train crop filenames and 1,434 separately stored augmented train filenames. Removing the explicit `flip` or `rotate` augmentation prefixes maps **all 1,434** augmented names to the 478 originals, exactly three derivatives per original; none of the separate original/validation/test crop names are literally duplicated across train and test. Thus, a documented training-only augmentation policy is visible in the directory evidence. This does not establish physical module-disjoint validation.

**Release mismatch gate:** the 2023 paper's abstract describes 593 labeled EL cell images; the earliest public repository directory listing exposes 478 original train +54 validation +50 test = **582 original crop filenames**. This 11-image difference is a **paper-to-release count alignment HOLD**, not a reported study arithmetic error because the paper's exact code/data vintage is not yet pinned.

## What genuinely changed in the audit's admissible inference
- **Baseline, file-only:** across the publicly listed train/test paths, 0 exact filename duplicates are found. A statement of literal filename disjointness is supported.
- **Enhanced, parsed-family:** despite that exact-name result, 22/33/34 **candidate crop-source filename families** occur in both train/test for three versions. Thus, literal filename distinctness **does not establish parsed-source-family distinctness** for these versions. The result is a real documentary disjointness-diagnostic advance, conditional on the parsing rule.
- **Physical/module:** no independent proof that such keys denote identical physical modules. Therefore the strongest source-backed conclusion is **hold physical disjointness**, not “the published 2023 model leaked”.
- **Performance:** not evaluated. We neither downloaded images nor reproduced trained weights, masks, class metrics or the exact publication experiment.

## Citation and manuscript insertion
**Source paper:** Pratt, L. E.; Matheus, J.; Klein, R. (2023), DOI 10.1016/j.sasc.2023.200048. **Repository source:** TheMakiran/BenchmarkELimages pinned commit `768b5e78596b429829b6b7aceb0ce4ac7b07788d` and 10 leaf tree SHAs listed in `benchmarkel_connector_replay_results.json`.

**Place in the R47 paper's Results, after “Source-version alignment is a separate identifiability gate” and before “Printed dataset and metric denominators”:**

> “A three-release public EL segmentation dataset audit found no identical crop filenames across published train/test directory manifests, but detected 22, 33 and 34 cross-partition matches in a restricted filename-family prefix mapping, respectively. The parser covered files with explicit `_r#_c#` crop coordinates and did not interpret other naming systems. This establishes a documentary distinction between literal file-level and name-inferred source-family disjointness, not independently verified physical-module overlap, model leakage or an effect on reported mIoU. The source publication, dataset repository version and physical module key require separate verification.”

**Place in Discussion, after positive grouped/physical independence paragraph:**

> “When original crops share a recognizable source-prefix pattern, a zero exact-filename intersection does not certify an empty shared source-family intersection. Source-version mapping and a documented physical-parent key are necessary to promote such a filename-level signal into a verified module-disjoint test claim.”

**Where NOT to place:** do not add these counts to PRISMA, a prevalence estimate across PV publications, or a published model's training-test contamination table. Do not introduce class-level F1/mIoU comparisons without actual scored masks.

## Required remaining work
1. Ask author/primary source for the file-naming convention or source-image→module mapping for the `ARTS/CFVS/CSIR` `_r#_c#` patterns; this is the exact pending **module-identity upgrade**. No external email sent.
2. Confirm exact release/commit the Pratt et al. (2023) model used; public repo now contains multiple dated releases and the 593-vs-582 vintage issue. No paper-level leakage claim until then.
3. Pin original image/mask bytes/checksums only if actual pixel replay is scientifically necessary and license-compatible; this source-genealogy audit does not need image redistribution.
4. Separate Sandia `AnonDB.csv` physical-unit controlled split test remains pending original metadata intake. Two studies/datasets are **not conflated**.

## Reproducibility
`benchmarkel_git_tree_audit.py` re-fetches the original public Git tree directory metadata at **fixed exact SHA1 IDs** from the official GitHub REST API and computes all values. Network-enabled execution required; the actual analysis in this response used the *connected GitHub fetch tool* against those identical tree URLs. Software parser selftest is offline, and independent values are stored in `benchmarkel_connector_replay_results.json`. These metadata results are not artifact-derived pixel hashes or measured fault detection scores.
