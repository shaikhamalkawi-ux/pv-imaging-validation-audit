"""R52B independently reconstruct Ridge predictions and segment random test rows by source-module status.
Exploratory only, protocol file EXPLORATORY_SUBGROUP_PROTOCOL.md. No pixel/model author test.
"""
import csv,hashlib,random,re,json,statistics,math,sys,os
from pathlib import Path
from collections import defaultdict
import numpy as np,pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.linear_model import Ridge
ROOT=Path(__file__).resolve().parent.parent
SOURCE=Path(sys.argv[1]) if len(sys.argv)>1 else Path(os.environ.get('SANDIA_ANONDB_CSV','/mnt/data/AnonDB.csv'))
raw=SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='8fe450440d989f9aa469f0fc206c76b13021a93dbb6071ddc3a1967fd083440e'
rr=list(csv.DictReader(raw.decode('utf-8-sig').splitlines()))
valid=[]
for i,r in enumerate(rr):
 try:
  m=float(r['Nameplate_Pmp_(W)']);p=float(r['Pmp_(W)'])
  days=int(re.fullmatch(r'OE\s+(\d+)\s+days',r['Total_Exposure'],re.I).group(1))
  if not(m>0 and p>0 and math.isfinite(m) and math.isfinite(p)):continue
 except (TypeError,AttributeError,ValueError):continue
 valid.append({'row':i,'mod_id':r['Mod_ID'], 'Make':r['Make'],'Model':r['Model'],
               'Cell_Wafer_Type':r['Cell_Wafer_Type'], 'Nameplate_Pmp_(W)':m,
               'Module_Area_(cm2)':float(r['Module_Area_(cm2)']),
               'Total_Exposure_Days':days,'Exposure_Step':int(r['Exposure_Step']),
               'target_ratio':p/m})
D=pd.DataFrame(valid);assert len(D)==598
nums=['Nameplate_Pmp_(W)','Module_Area_(cm2)','Total_Exposure_Days','Exposure_Step']
cats=['Make','Model','Cell_Wafer_Type']
features=cats+nums
orig=list(csv.DictReader((ROOT/'results/R52_ALL_200_SPLITS_METRICS.csv').open()))
rowmap={int(x['seed']):x for x in orig if x['split']=='random_row'}
assert len(rowmap)==100
out=[]
for seed in range(20261108,20261208):
 ix=list(range(len(D)));random.Random(seed).shuffle(ix)
 ntest=round(.2*len(D));ti=np.array(sorted(ix[:ntest]));tr=np.array(sorted(ix[ntest:]))
 xtr,xte=D.iloc[tr],D.iloc[ti]
 prep=ColumnTransformer([('numeric',Pipeline([('imputer',SimpleImputer(strategy='median')),('z',StandardScaler())]),nums),
  ('categorical',OneHotEncoder(handle_unknown='ignore',sparse_output=False),cats)],remainder='drop',sparse_threshold=0)
 model=Pipeline([('prep',prep),('regressor',Ridge(alpha=10.0))]);model.fit(xtr[features],xtr['target_ratio'])
 prediction=model.predict(xte[features]);y=xte['target_ratio'].to_numpy();errs=np.abs(y-prediction)*100
 prev=float(rowmap[seed]['metadata_ridge_no_id_MAE_ratio_pctpts'])
 assert abs(np.mean(errs)-prev)<1e-10,(seed,np.mean(errs),prev)
 trainmods=set(xtr['mod_id']);mods=xte['mod_id'].to_numpy()
 is_seen=np.array([m in trainmods for m in mods],dtype=bool)
 assert 0<sum(is_seen)<len(is_seen)
 def mod_equal(flag):
  groups=defaultdict(list)
  for m,e,s in zip(mods,errs,is_seen):
   if s==flag:groups[m].append(float(e))
  return float(np.mean([np.mean(z) for z in groups.values()]))
 out.append({'seed':seed,'total_test_rows':len(ti),'seen_test_rows':int(sum(is_seen)),
  'unseen_test_rows':int(sum(~is_seen)),
  'seen_test_modules':len(set(mods[is_seen])),
  'unseen_test_modules':len(set(mods[~is_seen])),
  'seen_MAE_ratio_pctpoints':float(np.mean(errs[is_seen])),
  'unseen_MAE_ratio_pctpoints':float(np.mean(errs[~is_seen])),
  'seen_module_equal_MAE_ratio_pctpoints':mod_equal(True),
  'unseen_module_equal_MAE_ratio_pctpoints':mod_equal(False),
  'seen_minus_unseen_MAE_ratio_pctpoints':float(np.mean(errs[is_seen])-np.mean(errs[~is_seen]))})
summary={'source_sha256':hashlib.sha256(raw).hexdigest(),
 'exploratory_protocol_sha256':hashlib.sha256((ROOT/'EXPLORATORY_SUBGROUP_PROTOCOL.md').read_bytes()).hexdigest(),
 'source_rows':616,'eligible':598,'run_count':100,
 'random_split_R52_original_Ridge_metric_reproduced_every_seed':True,
 'results':{},
 'limits':'Exploratory within-random-test stratification on true Sandia Mod_ID. No pixel or original IV curve, causal optimism, independent PV plant, actual published author split or classification accuracy. Test group composition differs.'}
for name in ['seen_test_rows','unseen_test_rows','seen_MAE_ratio_pctpoints','unseen_MAE_ratio_pctpoints','seen_module_equal_MAE_ratio_pctpoints','unseen_module_equal_MAE_ratio_pctpoints','seen_minus_unseen_MAE_ratio_pctpoints']:
 a=np.array([r[name] for r in out],dtype=float)
 summary['results'][name]={'mean':float(a.mean()),'range':[float(a.min()),float(a.max())],'q05':float(np.quantile(a,0.05)),'q95':float(np.quantile(a,0.95))}
summary['seen_lower_than_unseen_error_seed_count']=sum(z['seen_minus_unseen_MAE_ratio_pctpoints']<0 for z in out)
with (ROOT/'results/R52_EXPLORATORY_SEEN_UNSEEN_100_SPLITS.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=out[0].keys());w.writeheader();w.writerows(out)
(ROOT/'results/R52_EXPLORATORY_SUBGROUP_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
