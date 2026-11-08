# Reproducing the bounded 99pv results

## Requirements

- Python 3.11+; offline figure/script checks use the standard library.
- For R52 full analysis: NumPy, pandas, scikit-learn. Reference versions: `numpy==2.3.5`, `scikit-learn==1.8.0` (pandas from the archived R52 environment; install compatible current version).
- For figures: Matplotlib. For R53 **only after actual images arrive**: Pillow and tifffile.

## Offline source-table and parser QA (no download)

```bash
python tests/verify_public.py
python cases/benchmarkel_r50b/benchmarkel_git_tree_audit.py --selftest
python cases/sandia_r50/test_certificates.py
```

### Bommes printed Table-5 reconstruction

```bash
python cases/bommes_r46/code/reproduce.py
python cases/bommes_r46/code/build_contract.py
```

The input is the independently extracted, attributed original published 54-cell table included under `cases/bommes_r46/source_inputs/`. It was not a rerun of published networks. Preserve the printed two-decimal precision.

### Public EL Git-tree directory audit (network required)

```bash
python cases/benchmarkel_r50b/benchmarkel_git_tree_audit.py benchmarkel_live_replay.json
```

This checks source Git tree SHA1 IDs, not image-level SHA256 or physical module IDs. The no-network self-test is separate.

### Official Sandia metadata partition and fixed Ridge control

Obtain **unmodified** source `AnonDB.csv` from <https://data.openei.org/submissions/8378> and verify its SHA256. It is omitted from this code repository intentionally.

```bash
python cases/sandia_r50/audit_original_AnonDB.py /path/to/AnonDB.csv sandia_modid_audit.json
# numeric-control reproduction; may take longer:
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python cases/sandia_r52/src/run_metadata_control.py /path/to/AnonDB.csv
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python cases/sandia_r52/src/seen_unseen_exploratory.py /path/to/AnonDB.csv
python cases/sandia_r52/src/make_figures.py
```

Compare to `cases/sandia_r52/results/` and `cases/sandia_r52/qa/`. No model was trained on EL TIFF pixels in R52.

### Prospective, NOT yet performed, R53 image experiment

Only after official Sandia `EL.zip` is obtained and its contents verified, read `cases/sandia_r53_pending/R53_PIXEL_EXPERIMENT_PRE_ANALYSIS_DESIGN_LOCK.md` and use:

```bash
python cases/sandia_r53_pending/src/run_R53_on_original_EL_pixels.py --metadata /path/to/AnonDB.csv --el-zip /path/to/EL.zip --out-dir /path/to/private_output
```

It predicts an **electrical IV power ratio**, not crack classification. Its result currently remains **HOLD**.
