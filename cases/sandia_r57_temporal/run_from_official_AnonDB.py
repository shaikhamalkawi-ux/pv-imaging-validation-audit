#!/usr/bin/env python3
"""R57: independent raw-Sandia chronology x physical-parent *metadata* control.

Requires the original Sandia AnonDB.csv, obtained from DOI 10.11578/3818365.
No source CSV, image, original row/target, or person-level record is exported.
Preoutcome cutoff and model are frozen in the R54 T01/T02 protocols.
This is *not* an EL image / defect detection experiment or a leakage estimate.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math, random, re, statistics
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SOURCE_SHA = "8fe450440d989f9aa469f0fc206c76b13021a93dbb6071ddc3a1967fd083440e"
CATEGORICAL = ["Make", "Model", "Cell_Wafer_Type"]
NUMERIC = ["Nameplate_Pmp_(W)", "Module_Area_(cm2)", "Total_Exposure_Days", "Exposure_Step"]
FEATURES = NUMERIC + CATEGORICAL
CUTOFF = datetime.strptime("02/09/2021", "%m/%d/%Y").date()

def flt(x):
    try:
        y = float(x)
        return y if math.isfinite(y) else float("nan")
    except (ValueError, TypeError):
        return float("nan")

def parse_date(x):
    try:
        return datetime.strptime(x.strip(), "%m/%d/%Y").date()
    except (ValueError, AttributeError):
        return None

def source(path):
    raw = Path(path).read_bytes()
    assert len(raw) == 254907, "original source byte-count mismatch"
    sha = hashlib.sha256(raw).hexdigest()
    assert sha == SOURCE_SHA, "source sha mismatch; do not silently substitute a release"
    f = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    assert len(f.fieldnames) == 63
    rows = list(f)
    assert len(rows) == 616
    eligible = []
    for idx, r in enumerate(rows):
        measured = flt(r["Pmp_(W)"])
        rated = flt(r["Nameplate_Pmp_(W)"])
        exp = re.fullmatch(r"OE\s+(\d+)\s+days", r["Total_Exposure"].strip(), flags=re.I)
        day = parse_date(r["IV_Date"])
        if not(measured > 0 and rated > 0 and exp and day):
            continue
        module = r["Mod_ID"].strip()
        ivpath = r["IVPath"].strip()
        assert module and ivpath
        hd, ld = parse_date(r["High_EL_Date"]), parse_date(r["Low_EL_Date"])
        near = bool(r["ELHPath"].strip() and r["ELLPath"].strip()
                    and hd and ld and hd == ld and abs((hd-day).days) <= 7)
        eligible.append({
            "original_row":idx, "Mod_ID":module, "IVPath":ivpath, "IV_Date_obj":day,
            "Make":r["Make"].strip(), "Model":r["Model"].strip(),
            "Cell_Wafer_Type":r["Cell_Wafer_Type"].strip(),
            "Nameplate_Pmp_(W)":rated,
            "Module_Area_(cm2)":flt(r["Module_Area_(cm2)"]),
            "Total_Exposure_Days":int(exp.group(1)),
            "Exposure_Step":int(r["Exposure_Step"]),
            "Pmp_(W)":measured, "target_ratio":measured/rated,
            "has_both_el_paths":bool(r["ELHPath"].strip() and r["ELLPath"].strip()),
            "near_date_el_paths":near,
        })
    D = pd.DataFrame(eligible)
    assert len(D) == 598 and D["Mod_ID"].nunique() == 420
    return D, sha

def make_model():
    prep = ColumnTransformer([
        ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")),
                              ("z", StandardScaler())]), NUMERIC),
        ("categorical", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
         CATEGORICAL)
    ], remainder="drop", sparse_threshold=0)
    return Pipeline([("prep", prep), ("regressor", Ridge(alpha=10.0))])

def errors(test, pred):
    target = test["target_ratio"].to_numpy(dtype=float)
    rated = test["Nameplate_Pmp_(W)"].to_numpy(dtype=float)
    error = np.asarray(pred)-target
    return {
        "MAE_ratio_pctpt":float(np.mean(np.abs(error))*100),
        "RMSE_ratio_pctpt":float(np.sqrt(np.mean(error*error))*100),
        "mean_signed_error_pctpt":float(np.mean(error)*100),
        "MAE_Pmp_W":float(np.mean(np.abs(error)*rated)),
    }

def predict(train, test):
    assert not set(train["original_row"]) & set(test["original_row"])
    model = make_model()
    model.fit(train[FEATURES],train["target_ratio"])
    return np.asarray(model.predict(test[FEATURES]),dtype=float)

def main(path):
    D, sha = source(path)
    before = D[D["IV_Date_obj"] < CUTOFF].copy()
    future = D[D["IV_Date_obj"] >= CUTOFF].copy()
    future_mods = set(future["Mod_ID"])
    before_mods = set(before["Mod_ID"])
    shared_ids = future_mods & before_mods
    disjoint = before[~before["Mod_ID"].isin(future_mods)].copy()
    assert (len(before),len(future),len(disjoint),len(shared_ids)) == (459,139,400,56)
    assert before["Mod_ID"].nunique() == 339 and future["Mod_ID"].nunique() == 137
    assert len(set(disjoint["Mod_ID"]) & future_mods) == 0
    assert len(set(before["IVPath"]) & set(future["IVPath"])) == 0
    assert (int(before["near_date_el_paths"].sum()),
            int(future["near_date_el_paths"].sum()),
            int(disjoint["near_date_el_paths"].sum())) == (401,60,358)
    all_pred = predict(before,future)
    dis_pred = predict(disjoint,future)
    m_all, m_dis = errors(future,all_pred),errors(future,dis_pred)
    m_const = errors(future,np.ones(len(future)))
    assert abs(m_all["MAE_ratio_pctpt"]-1.3691255258791946) < 1e-8
    assert abs(m_dis["MAE_ratio_pctpt"]-1.6411116806152952) < 1e-8
    # Prespecified sample-size controls: remove exactly 59 NON-test-shared earlier rows,
    # preserving all 59 earlier measurements on test-shared physical modules.
    eligible_remove = list(disjoint.index)
    controls = []
    for seed in range(20261108,20261208):
        removed = set(random.Random(seed).sample(eligible_remove,59))
        alt = before.loc[~before.index.isin(removed)]
        assert len(alt)==400 and len(set(alt["Mod_ID"]) & future_mods)==56
        controls.append(errors(future,predict(alt,future))["MAE_ratio_pctpt"])
    def subgroup(mask):
        sub=future.loc[mask]
        return {"n":len(sub),
            "all_earlier_MAE_pctpt":float(np.mean(np.abs(all_pred[mask.to_numpy()]-sub["target_ratio"].to_numpy()))*100),
            "disjoint_MAE_pctpt":float(np.mean(np.abs(dis_pred[mask.to_numpy()]-sub["target_ratio"].to_numpy()))*100)}
    seen = future["Mod_ID"].isin(before_mods)
    near = future["near_date_el_paths"]
    result = {
        "stage":"R57_REPRODUCIBLE_FUTURE_COHORT_NONIMAGING_CONTROL",
        "source":"Sandia PV-IV-EL 10.11578/3818365",
        "source_sha256":sha,
        "records":{"raw":616,"eligible":len(D),"modules":D["Mod_ID"].nunique(),
                   "early_training_all":len(before),"future_test":len(future),
                   "shared_Mod_ID":len(shared_ids),
                   "removed_early_for_module_disjointness":len(before)-len(disjoint),
                   "early_training_disjoint":len(disjoint),
                   "EL_date_path_support_early":int(before["near_date_el_paths"].sum()),
                   "EL_date_path_support_future":int(near.sum()),
                   "EL_date_path_support_disjoint_early":int(disjoint["near_date_el_paths"].sum())},
        "fixed_future_test_n":139,
        "constant":m_const, "all_prior_Ridge":m_all,"disjoint_prior_Ridge":m_dis,
        "delta_disjoint_minus_all_MAE_ratio_pctpt":m_dis["MAE_ratio_pctpt"]-m_all["MAE_ratio_pctpt"],
        "size_matched_100_controls":{"mean":statistics.mean(controls),"median":statistics.median(controls),
             "min":min(controls),"max":max(controls),
             "count_below_disjoint":sum(v<m_dis["MAE_ratio_pctpt"] for v in controls),
             "n":len(controls),"seeds":[20261108,20261207]},
        "subgroups":{"seen_test_Mod_ID":subgroup(seen),
                     "unseen_test_Mod_ID":subgroup(~seen),
                     "near_IV_EL_metadata_only":subgroup(near)},
        "claim_boundary":"Same future test but different training size/composition. No causal effect, no EL-pixel model, no defect benchmark, no confirmed published-paper leakage. 100 controls are dependent."
    }
    # Source code is public, but only aggregate numbers are written here.
    return result

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("csv",help="Unmodified Sandia AnonDB.csv from its official source")
    ap.add_argument("--out",help="Optional aggregate JSON file, no source rows")
    args=ap.parse_args()
    z=main(args.csv)
    payload=json.dumps(z,indent=2,sort_keys=True)+"\n"
    if args.out: Path(args.out).write_text(payload,encoding="utf-8")
    print(payload,end="")
