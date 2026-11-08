# R52 replay from fresh extraction

The author-facing ZIP deliberately omits third-party CSV source bytes. Obtain exact official Sandia/OEDI `AnonDB.csv` (DOI 10.11578/3818365) or use the separately controlled original Project 99pv R50 copy. Its SHA-256 **must** be `8fe450440d989f9aa469f0fc206c76b13021a93dbb6071ddc3a1967fd083440e`. This exact source has 616 rows and 438 `Mod_ID`, although the catalog mentions 613 sets. Do not reserialize or drop the three repeated IVPath rows before the primary analysis.

Requirements: Python 3.10+, NumPy, pandas, scikit-learn (reference run 1.8.0), matplotlib for figures. Deterministic main runs (no network):

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python src/run_metadata_control.py /path/to/AnonDB.csv
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python src/seen_unseen_exploratory.py /path/to/AnonDB.csv
python src/make_figures.py
```

The first program creates `results/R52_ALL_200_SPLITS_METRICS.csv` and `results/R52_SUMMARY.json`; the exploratory run creates its separate 100-seed outputs. Re-run on the same software stack and compare to hash values in the package QA manifest. Both scripts check original source SHA and reject a different dataset version. No GitHub images, image arrays, trained image classifier or paper-specific score are used. No intended interpretation beyond a non-image electrical power task.
