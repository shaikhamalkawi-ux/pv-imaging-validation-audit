#!/usr/bin/env python3
"""R52 99pv original Sandia *metadata-only* measured-IV-Pmp pilot.

Follows PREOUTCOME_PROTOCOL_LOCK.md exactly.  Never an EL pixel model or defect model.
Needs numpy, pandas, sklearn. No network access or file editing of input.
"""
from __future__ import annotations
import csv, hashlib, json, math, re, random, statistics, os, sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT=Path(__file__).resolve().parent.parent
if len(sys.argv)<2: raise SystemExit('Usage: python '+Path(__file__).name+' /path/to/AnonDB.csv')
SRC=Path(sys.argv[1])
OUTPUT=ROOT/'results'; OUTPUT.mkdir(parents=True,exist_ok=True)
EXPECTED_SHA='8fe450440d989f9aa469f0fc206c76b13021a93dbb6071ddc3a1967fd083440e'
raw=SRC.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
assert sha==EXPECTED_SHA,('SOURCE_HASH_MISMATCH',sha)
rows=list(csv.DictReader(raw.decode('utf-8-sig').splitlines()))
assert len(rows)==616

def get_float(x):
    try:
        v=float(x)
        return v if math.isfinite(v) else None
    except (TypeError,ValueError):return None

eligible=[];excluded=[]
for i,r in enumerate(rows):
    actual=get_float(r['Pmp_(W)']); rated=get_float(r['Nameplate_Pmp_(W)'])
    exp=re.fullmatch(r'OE\s+(\d+)\s+days',r['Total_Exposure'].strip(),re.I)
    if actual is None or rated is None or actual<=0 or rated<=0 or exp is None:
        excluded.append(i); continue
    eligible.append({'original_row':i,'mod_id':r['Mod_ID'].strip(),'ivpath':r['IVPath'].strip(),
        'ivdate':datetime.strptime(r['IV_Date'].strip(),'%m/%d/%Y').date(),
        'Make':r['Make'].strip(),'Model':r['Model'].strip(),
        'Cell_Wafer_Type':r['Cell_Wafer_Type'].strip(),
        'Nameplate_Pmp_(W)':rated,'Module_Area_(cm2)':get_float(r['Module_Area_(cm2)']),
        'Total_Exposure_Days':int(exp.group(1)),'Exposure_Step':int(r['Exposure_Step']),
        'Pmp_(W)':actual,'target_ratio':actual/rated})

categorical=['Make','Model','Cell_Wafer_Type']
numerical=['Nameplate_Pmp_(W)','Module_Area_(cm2)','Total_Exposure_Days','Exposure_Step']
for row in eligible:
 assert row['mod_id'] and row['ivpath'] and np.isfinite(row['target_ratio'])
D=pd.DataFrame(eligible)
assert D['original_row'].is_unique
assert D['mod_id'].notna().all()
# Metadata-only generalizable feature set is fixed in the pre-outcome protocol.
assert len(set(categorical+numerical)&{'Pmp_(W)','Isc_(A)','Voc_(V)','Imp_(A)','Vmp_(V)','FF_(percent)','Mod_ID','IVPath'})==0
N=len(D); TEST_N=round(.2*N)
assert N>500 and 0<TEST_N<N

def splitter(seed:int,kind:str):
    if kind=='random_row':
        indices=list(range(N));random.Random(seed).shuffle(indices)
        test=set(indices[:TEST_N])
    elif kind=='module_grouped':
        grouped=D.groupby('mod_id').indices
        ids=sorted(grouped)
        random.Random(seed ^ 0xC0FFEE).shuffle(ids)
        n=0;groups=set()
        for g in ids:
            size=len(grouped[g]);
            if len(groups)<len(ids)-1 and abs(n+size-TEST_N)<abs(n-TEST_N):
                groups.add(g);n+=size
        if not groups: groups.add(min(ids,key=lambda g:(abs(len(grouped[g])-TEST_N),g)))
        if len(groups)==len(ids):groups.remove(ids[-1])
        test=set(int(i) for g in groups for i in grouped[g])
    else:raise ValueError(kind)
    train=set(range(N))-test
    assert train and test and train.isdisjoint(test)
    return np.array(sorted(train)),np.array(sorted(test))

# A *fixed*, not test-tuned non-ID model.
def nonid_model():
    prep=ColumnTransformer([
      ('numeric',Pipeline([('imputer',SimpleImputer(strategy='median')),('z',StandardScaler())]),numerical),
      ('categorical',OneHotEncoder(handle_unknown='ignore',sparse_output=False),categorical)
    ],remainder='drop',sparse_threshold=0)
    return Pipeline([('prep',prep),('regressor',Ridge(alpha=10.0))])


def predicted_lookup(train,test,base_pred,time_safe=False):
    bymod=defaultdict(list)
    for i in train:
        r=eligible[int(i)];bymod[r['mod_id']].append((r['ivdate'],r['target_ratio']))
    out=np.array(base_pred,copy=True,dtype=float);used=0;future=0
    for p,idx in enumerate(test):
        row=eligible[int(idx)];opts=bymod.get(row['mod_id'],[])
        if not opts:continue
        if time_safe:
            older=[(date,ratio) for date,ratio in opts if date<row['ivdate']]
            if not older:continue
            v=max(older,key=lambda x:x[0])[1]
        else:
            v=statistics.mean(ratio for _,ratio in opts)
            if any(date>=row['ivdate'] for date,_ in opts):future+=1
        out[p]=v; used+=1
    return out,used,future

results=[]
for seed in range(20261108,20261208):
    for kind in ('random_row','module_grouped'):
        train,test=splitter(seed,kind)
        train_df=D.iloc[train];test_df=D.iloc[test]
        ytr=train_df['target_ratio'].to_numpy(dtype=float)
        yte=test_df['target_ratio'].to_numpy(dtype=float)
        model=nonid_model();model.fit(train_df[categorical+numerical],ytr)
        ridge=np.asarray(model.predict(test_df[categorical+numerical]))
        oracle,n_oracle,n_future=predicted_lookup(train,test,ridge,time_safe=False)
        prior,n_prior,_=predicted_lookup(train,test,ridge,time_safe=True)
        pset={
          'nameplate_fixed_ratio1':np.ones(len(test)),
          'metadata_ridge_no_id':ridge,
          'retrospective_ID_lookup_NEGATIVE_CONTROL':oracle,
          'past_IV_ID_lookup_NEGATIVE_CONTROL':prior}
        trmod={eligible[i]['mod_id'] for i in train};temod={eligible[i]['mod_id'] for i in test}
        triv={eligible[i]['ivpath'] for i in train};teiv={eligible[i]['ivpath'] for i in test}
        common=trmod & temod
        rec={'seed':seed,'split':kind,'train_rows':len(train),'test_rows':len(test),
            'n_train_modules':len(trmod),'n_test_modules':len(temod),
            'shared_Mod_ID_count':len(common),'shared_IVPath_count':len(triv & teiv),
            'test_rows_parent_in_train':sum(eligible[i]['mod_id'] in trmod for i in test),
            'fraction_test_parent_seen':sum(eligible[i]['mod_id'] in trmod for i in test)/len(test),
            'retrospective_lookup_rows':n_oracle,'retro_lookup_future_or_same_date_rows':n_future,
            'strict_prior_lookup_rows':n_prior,'first_test_original_row':int(eligible[int(test[0])]['original_row'])}
        for name,ypred in pset.items():
            assert len(ypred)==len(test) and np.isfinite(ypred).all()
            rec[name+'_MAE_ratio_pctpts']=float(np.mean(np.abs(yte-ypred))*100)
            rec[name+'_MAE_pmp_watts']=float(np.mean(np.abs(yte-ypred)*test_df['Nameplate_Pmp_(W)'].to_numpy(dtype=float)))
            rec[name+'_RMSE_ratio_pctpts']=float(np.sqrt(np.mean((yte-ypred)**2))*100)
        if kind=='module_grouped':assert len(common)==0 and len(triv & teiv)==0
        results.append(rec)

keys=list(results[0]);out_csv=OUTPUT/'R52_ALL_200_SPLITS_METRICS.csv'
with out_csv.open('w',newline='',encoding='utf-8') as f:
 w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(results)
summary={'stage':'R52_PREDECLARED_NONIMAGING_METADATA_IV_POWER_NEGATIVE_CONTROL',
         'original_source_sha256':sha,'original_source_size':len(raw),
         'protocol_lock_sha256':hashlib.sha256((ROOT/'PREOUTCOME_PROTOCOL_LOCK.md').read_bytes()).hexdigest(),
         'fixed_sklearn_version':__import__('sklearn').__version__,
         'fixed_numpy_version':np.__version__,
         'original_rows':len(rows),'eligible_rows':N,'excluded_original_indices':excluded,
         'unique_eligible_modules':len(D['mod_id'].unique()),'holdout_target_size':TEST_N,
         'eligible_module_count_histogram':dict(Counter(Counter(D['mod_id']).values())),
         'dataset_target':'Measured IV Pmp(W) / Nameplate Pmp(W)',
         'not_an_EL_image_or_defect_detector_test':True,
         'not_an_author_paper_split_or_model':True,'seed_count':100,
         'models':['nameplate_fixed_ratio1','metadata_ridge_no_id','retrospective_ID_lookup_NEGATIVE_CONTROL','past_IV_ID_lookup_NEGATIVE_CONTROL'],
         'feature_list':categorical+numerical,'per_split_results_sha256':hashlib.sha256(out_csv.read_bytes()).hexdigest(),
         'results':{}}
for kind in ('random_row','module_grouped'):
 sub=[r for r in results if r['split']==kind]
 assert len(sub)==100
 record={'train_size_range':[min(x['train_rows'] for x in sub),max(x['train_rows'] for x in sub)],
         'test_size_range':[min(x['test_rows'] for x in sub),max(x['test_rows'] for x in sub)],
         'shared_Mod_ID_mean':statistics.mean(x['shared_Mod_ID_count'] for x in sub),
         'shared_Mod_ID_range':[min(x['shared_Mod_ID_count'] for x in sub),max(x['shared_Mod_ID_count'] for x in sub)],
         'shared_IVPath_mean':statistics.mean(x['shared_IVPath_count'] for x in sub),
         'test_seen_parent_frac_mean':statistics.mean(x['fraction_test_parent_seen'] for x in sub),
         'retrospective_lookup_rows_mean':statistics.mean(x['retrospective_lookup_rows'] for x in sub),
         'retrospective_lookup_using_future_or_same_date_mean':statistics.mean(x['retro_lookup_future_or_same_date_rows'] for x in sub),
         'strict_prior_lookup_rows_mean':statistics.mean(x['strict_prior_lookup_rows'] for x in sub)}
 for name in summary['models']:
    k=name+'_MAE_ratio_pctpts'
    vals=[x[k] for x in sub]
    record[name]={'MAE_ratio_pctpt_mean':statistics.mean(vals),'MAE_ratio_pctpt_range':[min(vals),max(vals)],
        'MAE_pmp_W_mean':statistics.mean(x[name+'_MAE_pmp_watts'] for x in sub),
        'RMSE_ratio_pctpt_mean':statistics.mean(x[name+'_RMSE_ratio_pctpts'] for x in sub)}
 summary['results'][kind]=record
summary['claim_boundary']='This is a NEW non-imaging metadata-to-measured-IV-power ratio regression on original Sandia metadata. It is not a PV image or defect detector, no raw EL files or IV curves replayed, no site-external claim, no source authors model/paper split, no detected leakage. The ID lookup is a labeled negative control and may use future outcomes; do not cite as realistic performance.'
(OUTPUT/'R52_SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({'N':N,'modules':summary['unique_eligible_modules'],'excluded':len(excluded),'source':sha,'protocol':summary['protocol_lock_sha256'],'results':summary['results']},ensure_ascii=False,indent=2))
