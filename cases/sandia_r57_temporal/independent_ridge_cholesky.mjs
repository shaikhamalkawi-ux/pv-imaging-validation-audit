#!/usr/bin/env node
/**
 * Independent same-future-test Sandia R57 metadata-Ridge numerical cross-check.
 *
 * Usage: node cases/sandia_r57_temporal/independent_ridge_cholesky.mjs /path/AnonDB.csv
 * Built-in Node only; never writes raw rows, names, module IDs or predictions.
 * Same original CSV source SHA, 2021-02-09 day boundary, Ridge(alpha=10), 7 features.
 * Independently solves centered ridge normal equations with Cholesky (no sklearn).
 * NOT an EL image classifier or a causal estimation of "leakage".
 */
import fs from 'node:fs';
import crypto from 'node:crypto';

const SRC_SHA='8fe450440d989f9aa469f0fc206c76b13021a93dbb6071ddc3a1967fd083440e';
if(process.argv.length!==3){console.error('Usage: node independent_ridge_cholesky.mjs /path/to/AnonDB.csv');process.exit(2)}
const raw=fs.readFileSync(process.argv[2]);
const digest=crypto.createHash('sha256').update(raw).digest('hex');
if(raw.length!==254907||digest!==SRC_SHA)throw Error('Original Sandia AnonDB.csv bytes/hash not matched');
const txt=raw.toString('utf8').replace(/^\uFEFF/,'');
function parseCsv(s) {
 let rows=[],row=[],field='',quoted=false;
 for(let i=0;i<s.length;i++){
  const c=s[i];
  if(c==='"'){if(quoted&&s[i+1]==='"'){field+='"';i++}else quoted=!quoted}
  else if(c===','&&!quoted){row.push(field);field=''}
  else if((c==='\n'||c==='\r')&&!quoted){
   if(c==='\r'&&s[i+1]==='\n')i++;
   row.push(field);field='';
   if(row.length>1)rows.push(row);
   row=[];
  } else field+=c;
 }
 if(field.length||row.length){row.push(field);rows.push(row)}
 return rows;
}
const input=parseCsv(txt), H=input[0], rec=input.slice(1).map(line=>{
 if(line.length!==H.length)throw Error('Bad original source CSV width');
 return Object.fromEntries(H.map((v,j)=>[v,line[j]??'']));
});
if(rec.length!==616||H.length!==63)throw Error('Sandia source frame has changed');
const num=s=>s!==''&&s!==undefined&&Number.isFinite(+s)?+s:NaN;
function date(s){const m=String(s).match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);return m?Date.UTC(+m[3],+m[1]-1,+m[2]):NaN}
const rows=rec.map((r,i)=>{
 const rated=num(r['Nameplate_Pmp_(W)']), actual=num(r['Pmp_(W)']);
 const exp=String(r['Total_Exposure']).trim().match(/^OE\s+(\d+)\s+days$/i);
 return {original_row:i,mod:String(r.Mod_ID).trim(),ivdate:date(r.IV_Date),y:actual/rated,rated,
    cat:[r.Make.trim(),r.Model.trim(),r.Cell_Wafer_Type.trim()],
    numeric:[rated,num(r['Module_Area_(cm2)']),exp?+exp[1]:NaN,num(r.Exposure_Step)]};
}).filter(z=>z.y>0&&Number.isFinite(z.y)&&Number.isFinite(z.ivdate)&&Number.isFinite(z.numeric[2]));
const cutoff=date('2/9/2021'),early=rows.filter(z=>z.ivdate<cutoff),
      future=rows.filter(z=>z.ivdate>=cutoff),testMods=new Set(future.map(z=>z.mod)),
      earlyAll=early,earlyDistinct=early.filter(z=>!testMods.has(z.mod));
if(rows.length!==598||new Set(rows.map(z=>z.mod)).size!==420||earlyAll.length!==459||earlyDistinct.length!==400||future.length!==139)
 throw Error('Frozen cohort cardinalities no longer agree');
function median(a) {
 const z=a.filter(Number.isFinite).sort((x,y)=>x-y);
 return z.length%2?z[(z.length-1)/2]:(z[z.length/2-1]+z[z.length/2])/2;
}
function fit(train) {
 const C=[0,1,2].map(j=>[...new Set(train.map(z=>z.cat[j]))].sort()),
       offsets=[4,4+C[0].length,4+C[0].length+C[1].length],
       p=4+C.reduce((a,z)=>a+z.length,0),means=[],std=[],imp=[];
 for(let j=0;j<4;j++){
   const arr=train.map(z=>z.numeric[j]),m=median(arr);imp.push(m);
   const xs=arr.map(z=>Number.isFinite(z)?z:m);
   const mu=xs.reduce((a,b)=>a+b,0)/xs.length;
   const sigma=Math.sqrt(xs.reduce((a,b)=>a+(b-mu)**2,0)/xs.length)||1;
   means.push(mu);std.push(sigma);
 }
 function vec(z){
  const x=new Float64Array(p);
  for(let j=0;j<4;j++)x[j]=((Number.isFinite(z.numeric[j])?z.numeric[j]:imp[j])-means[j])/std[j];
  for(let j=0;j<3;j++){const idx=C[j].indexOf(z.cat[j]);if(idx>=0)x[offsets[j]+idx]=1}
  return x;
 }
 const X=train.map(vec),y=train.map(z=>z.y),xmean=new Float64Array(p),
       ymean=y.reduce((a,b)=>a+b,0)/y.length;
 for(const x of X)for(let j=0;j<p;j++)xmean[j]+=x[j]/X.length;
 const A=Array.from({length:p},()=>new Float64Array(p)),B=new Float64Array(p);
 for(let i=0;i<X.length;i++){
  const dx=X[i],dy=y[i]-ymean;
  for(let j=0;j<p;j++){
   const a=dx[j]-xmean[j];B[j]+=a*dy;
   for(let k=0;k<=j;k++)A[j][k]+=a*(dx[k]-xmean[k]);
  }
 }
 for(let i=0;i<p;i++){
  A[i][i]+=10;
  for(let j=i+1;j<p;j++)A[i][j]=A[j][i];
 }
 const L=Array.from({length:p},()=>new Float64Array(p));
 for(let i=0;i<p;i++)for(let j=0;j<=i;j++){
  let acc=A[i][j];
  for(let k=0;k<j;k++)acc-=L[i][k]*L[j][k];
  if(i===j){if(!(acc>0))throw Error('Ridge Gram is not SPD');L[i][j]=Math.sqrt(acc)}
  else L[i][j]=acc/L[j][j];
 }
 const z=new Float64Array(p),w=new Float64Array(p);
 for(let i=0;i<p;i++){let s=B[i];for(let k=0;k<i;k++)s-=L[i][k]*z[k];z[i]=s/L[i][i]}
 for(let i=p-1;i>=0;i--){let s=z[i];for(let k=i+1;k<p;k++)s-=L[k][i]*w[k];w[i]=s/L[i][i]}
 return {features:p,predict:r=>{
  const x=vec(r);let pred=ymean;
  for(let i=0;i<p;i++)pred+=(x[i]-xmean[i])*w[i];
  return pred;
 }};
}
function testMetric(train) {
 const model=fit(train);
 const error=future.map(z=>model.predict(z)-z.y);
 return {
  rows_train:train.length,rows_test:future.length,features:model.features,
  MAE_ratio_pctpt:100*error.reduce((s,v)=>s+Math.abs(v),0)/future.length,
  RMSE_ratio_pctpt:100*Math.sqrt(error.reduce((s,v)=>s+v*v,0)/future.length),
  mean_signed_error_pctpt:100*error.reduce((s,v)=>s+v,0)/future.length,
  MAE_Pmp_W:error.reduce((s,v,i)=>s+Math.abs(v)*future[i].rated,0)/future.length
 };
}
const all=testMetric(earlyAll), disjoint=testMetric(earlyDistinct),
      delta=disjoint.MAE_ratio_pctpt-all.MAE_ratio_pctpt;
if(Math.abs(all.MAE_ratio_pctpt-1.3691255258791946)>1e-9||
   Math.abs(disjoint.MAE_ratio_pctpt-1.6411116806152952)>1e-9||
   Math.abs(delta-0.27198615473610066)>1e-9)
 throw Error('Independent numerical replay differs from archived R54 T02 outputs');
console.log(JSON.stringify({
 stage:'R57_INDEPENDENT_NODE_CHOL_MATCH_ORIGINAL_SOURCE',
 original_csv_sha256:digest,
 original_rows:616,eligible_rows:598,original_module_ids:420,
 initial_training_rows:459,disjoint_training_rows:400,fixed_future_test_rows:139,
 nonimaging_all_prior:all,nonimaging_disjoint_prior:disjoint,
 delta_MAE_ratio_pctpt:delta,
 interpretation:'Fixed future test but train size/composition changed. Not imaging, leakage detection or causal effect.'
},null,2));
