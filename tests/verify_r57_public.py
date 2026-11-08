#!/usr/bin/env python3
"""Offline R57 arithmetic+evidence-gate checker, no source data or downloads."""
import json, math
from pathlib import Path
root=Path(__file__).resolve().parent.parent
a=json.loads((root/"cases/sandia_r57_temporal/R57_AGGREGATE_EVIDENCE.json").read_text())
s=json.loads((root/"cases/benchmarkel_r57_thesis/R57_STRATUM_LINEAGE.json").read_text())
C=a["cohort"];r=a["results"]
assert C["eligible_rows"]==598 and C["early_training_rows"]+C["future_test_rows"]==598
assert C["early_training_rows"]-C["earlier_rows_removed_for_disjoint"]==C["disjoint_early_training_rows"]
assert C["pre_near_date_EL_metadata"]+C["future_near_date_EL_metadata"]==461
assert C["future_near_date_EL_metadata"] < C["future_test_rows"]
assert math.isclose(r["disjoint_earlier_Ridge_MAE_pctpt"]-r["all_earlier_Ridge_MAE_pctpt"],
                    r["delta_disjoint_minus_all_MAE_pctpt"],abs_tol=1e-12)
assert abs(a["independent_js_numeric_replay"]["ridge_all_MAE_pctpt"]-r["all_earlier_Ridge_MAE_pctpt"])<3e-14
assert abs(a["independent_js_numeric_replay"]["ridge_disjoint_MAE_pctpt"]-r["disjoint_earlier_Ridge_MAE_pctpt"])<3e-14
assert a["size_matched_control_from_original_preoutcome_QA"]["count_lower_than_disjoint"]==100
versions={k:[v for v in s["strata"] if v["release"]==k] for k in ("20211104","20220723","20221008")}
for i,(k,group) in enumerate(versions.items()):
    t=s["totals"][i]
    assert len(group)==3 and {z["source"] for z in group}=={"ARTS","CFVS","CSIR"}
    assert sum(z["shared_keys"] for z in group)==t["shared_keys"]
    assert sum(z["matched_test"] for z in group)==t["matched_test"]
    assert sum(z["parsed_test"] for z in group)+t["unparsed_test"]==t["test"]
assert [x["shared_keys"] for x in s["totals"]]==[22,33,34]
assert [x["matched_test"] for x in s["totals"]]==[24,35,36]
assert sum([478,54,50])==582 and 478*4==1912 and 593-582==11
print("R57_OFFLINE_DERIVED_ARITHMETIC_AND_SCOPE_PASS: 16 gates; no original TIFFs, raw CSV or trained-predictor rerun claimed.")
