#!/usr/bin/env python3
"""Synthetic-only software validation, never a Sandia source-data result."""
import csv, math, json, tempfile
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from sandia_fixed_count_certificate import solution,expected_both_group
from audit_original_AnonDB import analyze_file, exact_expected_shared_module_count,split_audit

def partitions(total,length):
  if length==1:yield [total];return
  for i in range(total+1):
    for a in partitions(total-i,length-1):yield [i]+a

checks=[]
def ok(name,v):
    checks.append((name,bool(v)))
    if not v:raise AssertionError(name)

s=solution()
ok('N_613',s['N_reported_measurement_sets']==613)
ok('G_438',s['G_reported_unique_modules']==438)
ok('D_175',s['repeated_measurement_excess_D']==175)
ok('sharp_repeated_row_bounds',s['number_of_measurement_sets_from_repeated_module_IDs_range']==[176,350])
ok('fixed_row_splits',s['train_rows_for_hypothetical_exact_fixed_split']+s['test_rows_for_hypothetical_exact_fixed_split']==613)
ok('expected_upper_56',abs(float(s['expected_count_of_distinct_shared_modules_max'])-56.22860889869814)<1e-12)
ok('expected_lower_near_one',.99999999999<float(s['expected_count_of_distinct_shared_modules_min'])<=1)
# Exact sample enumeration small synthetic example with no Sandia raw data.
mods=['A','A','A','B','B','C'];n=len(mods);S=2
observed=[]
for subset in combinations(range(n),S):
  test=set(subset);train=set(range(n))-test
  observed.append(len({mods[i] for i in train}&{mods[i] for i in test}))
expected=Fraction(sum(observed),len(observed))
exact=exact_expected_shared_module_count([3,2,1],S)
ok('tiny_exact_hypergeom_matches_all_assignments',expected==exact)
# Tiny exhaustive partitions demonstrate sharp pair vs concentrated extremum.
D=3;G=5;N=G+D;T=6;S=N-T
vals=[]
for ds in partitions(D,G):
    val=sum((Fraction(1)-Fraction(math.comb(T,1+d) if T>=1+d else 0,math.comb(N,1+d))-
             Fraction(math.comb(S,1+d) if S>=1+d else 0,math.comb(N,1+d))) for d in ds)
    vals.append(val)
f=lambda k: Fraction(1)-Fraction(math.comb(T,k) if T>=k else 0,math.comb(N,k))-Fraction(math.comb(S,k) if S>=k else 0,math.comb(N,k))
ok('tiny_sharp_min',min(vals)==f(D+1))
ok('tiny_sharp_max',max(vals)==D*f(2))
with tempfile.TemporaryDirectory() as t:
 p=Path(t)/'SYNTHETIC_NOT_SANDIA.csv'
 with p.open('w',newline='',encoding='utf-8') as h:
  w=csv.DictWriter(h,fieldnames=['Mod_ID','ELHPath','ELLPath','IVPath']);w.writeheader()
  for i,m in enumerate(mods):w.writerow({'Mod_ID':m,'ELHPath':f'e{i}.tif','ELLPath':f'l{i}.tif','IVPath':f'i{i}.csv'})
 z=analyze_file(p)
 ok('tiny_rows',z['observed_row_count']==6)
 ok('tiny_modules',z['observed_unique_Mod_ID']==3)
 ok('tiny_synthetic_distinct_status',z['status']!='EXECUTED_ON_ACTUAL_UPLOADED_METADATA')
 ok('tiny_multiplicity',z['actual_rows_in_repeated_modules']==5)
 ok('tiny_all_group_splits_clean',z['module_grouped_100_splits_max_shared_Mod_ID']==0)
 ok('tiny_raw_test_matches_expect',abs(float(z['theoretical_random_row_expected_shared_modules_given_ACTUAL_distribution'])-float(exact_expected_shared_module_count([3,2,1],round(.2*6))))<1e-10)
 ok('tiny_100_runs',len(z['runs'])==100)
print(json.dumps({'status':'PASS','checks':len(checks),'check_names':[x for x,v in checks],'data_scope':'SYNTHETIC_UNIT_TESTS_ONLY_PLUS_OFFICIAL_COUNTS_CLOSED_FORM'},indent=2))
