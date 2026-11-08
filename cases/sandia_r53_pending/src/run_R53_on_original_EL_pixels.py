#!/usr/bin/env python3
"""PROSPECTIVE R53 original Sandia EL-pixels to measured-IV-Pmp *electrical* prediction.

Status before original EL.zip: DESIGN-ONLY, NO EXPERIMENT EXECUTED.
See R53_PIXEL_EXPERIMENT_PRE_ANALYSIS_DESIGN_LOCK.md. Never call a defect detector.

Usage: python run_R53_on_original_EL_pixels.py --metadata AnonDB.csv --el-zip EL.zip --out-dir output
Requires numpy, pandas, sklearn, Pillow, tifffile.  No network required after original official source intake.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math, random, re, statistics, zipfile
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path, PurePosixPath
import numpy as np
import pandas as pd
from PIL import Image
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
import tifffile

SRC_SHA='8fe450440d989f9aa469f0fc206c76b13021a93dbb6071ddc3a1967fd083440e'
CATEGORICAL=['Make','Model','Cell_Wafer_Type']
NUMERIC=['Nameplate_Pmp_(W)','Module_Area_(cm2)','Total_Exposure_Days','Exposure_Step']


def sha256(b):return hashlib.sha256(b).hexdigest()

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def parse_date(s):return datetime.strptime(s.strip(),'%m/%d/%Y').date()

def original_key(s):return str(PurePosixPath(s.removeprefix('./')).as_posix())

def member_index(z):
    """Map exact normalized archive member names. Never guess if ambiguous."""
    d={}
    for x in z.infolist():
        if x.is_dir():continue
        k=original_key(x.filename)
        if k in d:raise ValueError('ambiguous duplicate normalized archive member '+k)
        d[k]=x
    return d

def select_member(request,idx):
    key=original_key(request)
    if key in idx:return key
    # Some official ZIPs wrap all payloads in one top-level folder; allow ONE unambiguous suffix match.
    matches=[x for x in idx if x.endswith('/'+key)]
    if len(matches)==1:return matches[0]
    raise ValueError(f'linked image not unambiguously found: {request} (matches={len(matches)})')

def image_features_from_bytes(raw):
    a=tifffile.imread(io.BytesIO(raw))
    a=np.asarray(a,dtype=np.float64)
    a=np.squeeze(a)
    if a.ndim!=2 or min(a.shape)<16 or not np.isfinite(a).all():
        raise ValueError(f'unsupported/nonfinite source TIFF shape {a.shape}')
    p1,p99=np.percentile(a,[1,99])
    if p99>p1:a=np.clip((a-p1)/(p99-p1),0,1)
    else:a=np.zeros_like(a)
    u=(a*255).round().astype(np.uint8)
    rs=np.asarray(Image.fromarray(u).resize((64,64),resample=Image.Resampling.BILINEAR),dtype=np.float64)/255.0
    blocks=rs.reshape(8,8,8,8)
    means=blocks.mean(axis=(1,3)).reshape(-1)
    stds=blocks.std(axis=(1,3)).reshape(-1)
    quantiles=np.quantile(rs,[.10,.25,.50,.75])
    out=np.concatenate([means,stds,quantiles])
    assert out.shape==(132,) and np.isfinite(out).all()
    return out


def cohort(rows,idx,max_lag=7):
    eligible=[];excluded=[]
    for rowno,r in enumerate(rows):
        reason=[]
        if not r['ELHPath'].strip() or not r['ELLPath'].strip():reason.append('MISSING_HIGH_OR_LOW_EL_LINK')
        else:
            try:
                h=select_member(r['ELHPath'],idx);l=select_member(r['ELLPath'],idx)
            except ValueError:reason.append('EL_ARCHIVE_MEMBER_ABSENT_OR_AMBIGUOUS')
        try:
            lag=(parse_date(r['High_EL_Date'])-parse_date(r['IV_Date'])).days
            if parse_date(r['High_EL_Date'])!=parse_date(r['Low_EL_Date']):reason.append('UNPAIRED_HIGH_LOW_EL_DATES')
            if abs(lag)>max_lag:reason.append('EL_IV_TIME_LAG_OVER_'+str(max_lag)+'D')
        except (ValueError,KeyError):reason.append('EL_IV_DATE_UNPARSEABLE')
        try:
            pmp=float(r['Pmp_(W)']);nameplate=float(r['Nameplate_Pmp_(W)'])
            if not np.isfinite(pmp) or not np.isfinite(nameplate) or pmp<=0 or nameplate<=0:raise ValueError()
        except (KeyError,ValueError):reason.append('POWER_TARGET_MISSING_OR_NONPOSITIVE')
        try:
            exposure=int(re.fullmatch(r'OE\s+(\d+)\s+days',r['Total_Exposure'].strip(),re.I).group(1))
        except (KeyError,AttributeError,ValueError):reason.append('EXPOSURE_METADATA_UNPARSEABLE')
        if not r['Mod_ID'].strip():reason.append('MISSING_PHYSICAL_MODULE_ID')
        if reason:excluded.append({'source_csv_0_based_row':rowno,'reasons':reason});continue
        eligible.append({'source_csv_0_based_row':rowno,'Mod_ID':r['Mod_ID'].strip(),
          'IVPath':r['IVPath'].strip(),'ELHPath':h,'ELLPath':l,'IV_Date':r['IV_Date'].strip(),
          'EL_IV_signed_lag_days':lag,'Make':r['Make'].strip(),'Model':r['Model'].strip(),
          'Cell_Wafer_Type':r['Cell_Wafer_Type'].strip(),
          'Nameplate_Pmp_(W)':nameplate,'Module_Area_(cm2)':float(r['Module_Area_(cm2)']),
          'Total_Exposure_Days':exposure,'Exposure_Step':int(r['Exposure_Step']),
          'Pmp_(W)':pmp,'target_ratio':pmp/nameplate})
    return eligible,excluded


def make_splits(records,seed):
    n=len(records);test_target=round(.2*n);allrows=set(range(n))
    if test_target<1 or n-test_target<1:raise ValueError('not enough eligible rows')
    order=list(range(n));random.Random(seed).shuffle(order)
    row_test=set(order[:test_target]);row_train=allrows-row_test
    bymod=defaultdict(list)
    for i,r in enumerate(records):bymod[r['Mod_ID']].append(i)
    keys=sorted(bymod);random.Random(seed^0xC0FFEE).shuffle(keys)
    groups=set();ct=0
    for k in keys:
        v=len(bymod[k])
        if len(groups)<len(keys)-1 and abs(ct+v-test_target)<abs(ct-test_target):groups.add(k);ct+=v
    if not groups:groups.add(min(keys,key=lambda k:abs(len(bymod[k])-test_target)))
    if len(groups)==len(keys):groups.remove(keys[-1])
    group_test={i for k in groups for i in bymod[k]};group_train=allrows-group_test
    assert {records[i]['Mod_ID'] for i in group_train}.isdisjoint({records[i]['Mod_ID'] for i in group_test})
    return {'random_row':(row_train,row_test),'module_grouped':(group_train,group_test)}


def ridge_image(train_x,train_y,test_x):
    scaler=StandardScaler().fit(train_x)
    model=Ridge(alpha=10.0).fit(scaler.transform(train_x),train_y)
    return np.asarray(model.predict(scaler.transform(test_x)))

def ridge_metadata(train_meta,train_y,test_meta):
    prep=ColumnTransformer([
      ('numerical',Pipeline([('imputer',SimpleImputer(strategy='median')),('scale',StandardScaler())]),NUMERIC),
      ('categorical',OneHotEncoder(handle_unknown='ignore',sparse_output=False),CATEGORICAL)],remainder='drop',sparse_threshold=0)
    p=Pipeline([('prep',prep),('ridge',Ridge(alpha=10.0))])
    p.fit(train_meta[NUMERIC+CATEGORICAL],train_y)
    return p.predict(test_meta[NUMERIC+CATEGORICAL])


def _metadata_candidate_before_image(r, maxlag):
    """Check image-independent source eligibility before download; no outcome-value selection."""
    try:
        d1=parse_date(r['High_EL_Date']);d2=parse_date(r['Low_EL_Date']);d3=parse_date(r['IV_Date'])
        ratio=float(r['Pmp_(W)'])/float(r['Nameplate_Pmp_(W)'])
        return d1==d2 and abs((d1-d3).days)<=maxlag and ratio>0 and np.isfinite(ratio)
    except (KeyError,ValueError,ZeroDivisionError,TypeError):
        return False

def run(args):
    source=Path(args.metadata).read_bytes();assert sha256(source)==SRC_SHA,'AnonDB original source sha256 mismatch'
    rows=list(csv.DictReader(source.decode('utf-8-sig').splitlines()))
    assert len(rows)==616
    z=zipfile.ZipFile(args.el_zip,'r')
    corrupt=z.testzip()
    if corrupt is not None:raise RuntimeError('EL.zip CRC error: '+corrupt)
    members=member_index(z)
    records,excluded=cohort(rows,members,args.max_lag_days)
    # Pre-analysis source admission: no unexpectedly large source image unavailability is acceptable.
    preimage_candidates=sum(1 for r in rows if r.get('ELHPath','').strip() and r.get('ELLPath','').strip()
        and _metadata_candidate_before_image(r,args.max_lag_days))
    missing_linked=sum('EL_ARCHIVE_MEMBER_ABSENT_OR_AMBIGUOUS' in x['reasons'] for x in excluded)
    if preimage_candidates and missing_linked / preimage_candidates >= 0.10:
        raise RuntimeError(f'HOLD source unlinked EL members >=10%: {missing_linked}/{preimage_candidates}; no score allowed')
    if len(records)<100 or len({r['Mod_ID'] for r in records})<50:
        raise RuntimeError('HOLD insufficient linked, date-admissible, label-complete EL source support')
    x=[];imgdigests={}
    for r in records:
        features=[]
        for key in ['ELHPath','ELLPath']:
            name=r[key];b=z.read(members[name])
            imgdigests[name]={'bytes':len(b),'sha256':sha256(b),'linked_to_metadata_row':r['source_csv_0_based_row']}
            features.append(image_features_from_bytes(b))
        x.append(np.concatenate(features))
    X=np.vstack(x)
    assert X.shape==(len(records),264)
    y=np.array([r['target_ratio'] for r in records],dtype=float)
    metadata=pd.DataFrame(records)
    results=[];predicts=[]
    for seed in range(20261108,20261208):
        for kind,(tr,te) in make_splits(records,seed).items():
            tri=np.array(sorted(tr));tei=np.array(sorted(te))
            preds={'constant_nameplate':np.ones(len(tei)),
                   'EL_pixels_Ridge_fixed':ridge_image(X[tri],y[tri],X[tei]),
                   'nonID_metadata_Ridge_fixed':ridge_metadata(metadata.iloc[tri],y[tri],metadata.iloc[tei])}
            trainIDs={records[i]['Mod_ID'] for i in tri};testIDs={records[i]['Mod_ID'] for i in tei}
            common=trainIDs&testIDs
            if kind=='module_grouped':assert len(common)==0
            rec={'seed':seed,'split':kind,'n_train_rows':len(tri),'n_test_rows':len(tei),
                 'n_test_physical_Mod_ID':len(testIDs),'overlap_Mod_ID':len(common),
                 'overlap_IVPath':len({records[i]['IVPath'] for i in tri}&{records[i]['IVPath'] for i in tei})}
            for name,pred in preds.items():
                error=np.abs(y[tei]-pred)
                rec[name+'_MAE_ratio_percentage_points']=float(100*np.mean(error))
                rec[name+'_MAE_Pmp_W']=float(np.mean(error*np.array([records[i]['Nameplate_Pmp_(W)'] for i in tei])))
                rec[name+'_RMSE_ratio_percentage_points']=float(100*np.sqrt(np.mean((y[tei]-pred)**2)))
            results.append(rec)
            for j,i in enumerate(tei):
                predicts.append({'seed':seed,'split':kind,'source_csv_0_based_row':records[i]['source_csv_0_based_row'],
                    'source_Mod_ID':records[i]['Mod_ID'],'target_power_ratio':float(y[i]),
                    'pred_EL_pixel_Ridge':float(preds['EL_pixels_Ridge_fixed'][j]),
                    'pred_metadata_Ridge':float(preds['nonID_metadata_Ridge_fixed'][j])})
    out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True)
    def write_csv(name,arr):
        with (out/name).open('w',encoding='utf-8',newline='') as f:
            w=csv.DictWriter(f,fieldnames=arr[0].keys());w.writeheader();w.writerows(arr)
    write_csv('EL_source_eligible_rows.csv',records)
    write_csv('R53_200_fixed_split_predictions.csv',predicts)
    write_csv('R53_200_fixed_split_metrics.csv',results)
    (out/'EL_source_exclusion_reasons.json').write_text(json.dumps(excluded,indent=2)+'\n')
    (out/'ORIGINAL_EL_ZIP_IMAGE_SHA_MANIFEST.json').write_text(json.dumps({'source_AnonDB_SHA256':SRC_SHA,'original_EL_zip_SHA256':sha256_file(args.el_zip),
            'original_EL_zip_member_count':len(members),'decoded_image_count':len(imgdigests),'images':imgdigests},indent=2)+'\n')
    summary={'label':'R53_ACTUAL_EL_PIXEL_TO_ELECTRICAL_RATIO_REGRESSION_NOT_DEFECT_DETECTION',
             'source_sha256':SRC_SHA,'eligible_rows':len(records),'eligible_modules':len(set(r['Mod_ID'] for r in records)),
             'source_member_count':len(members),'decoded_features':list(X.shape),
             'source_omissions':Counter(t for x in excluded for t in x['reasons']),
             'execution_count':len(results),'claim_limit':'Not a fault detector or published-paper score replay; row vs group split error not a causal leakage effect',
             'metric_summary':{}}
    for kind in ('random_row','module_grouped'):
        subset=[x for x in results if x['split']==kind]
        summary['metric_summary'][kind]={'module_ID_overlap_mean':statistics.mean(r['overlap_Mod_ID'] for r in subset),
            **{model:statistics.mean(r[model+'_MAE_ratio_percentage_points'] for r in subset)
               for model in ['constant_nameplate','EL_pixels_Ridge_fixed','nonID_metadata_Ridge_fixed']}}
    (out/'R53_EL_PIXEL_EXPERIMENT_SUMMARY.json').write_text(json.dumps(summary,indent=2,default=dict)+'\n')
    z.close()
    print(json.dumps(summary,indent=2,default=dict))

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--metadata',required=True)
    ap.add_argument('--el-zip',required=True)
    ap.add_argument('--out-dir',required=True)
    ap.add_argument('--max-lag-days',type=int,default=7)
    run(ap.parse_args())
