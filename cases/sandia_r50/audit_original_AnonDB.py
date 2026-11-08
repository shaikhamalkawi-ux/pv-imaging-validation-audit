#!/usr/bin/env python3
"""Run on the genuine official Sandia AnonDB.csv. No network or packages.

Outputs source-hash-pinned real Mod_ID multiplicities and 100 fixed-seed
measurement-row vs module-grouped splits. No model training/performance,
no invented physical cells or plants, no raw images processed.

Usage: python audit_original_AnonDB.py /path/to/AnonDB.csv /path/to/report.json
"""
import csv
import hashlib
import json
import random
import statistics
import sys
from collections import Counter
from fractions import Fraction
from math import comb
from pathlib import Path


def exact_expected_shared_module_count(sizes, test_size):
    n=sum(sizes);s=test_size;t=n-s
    return sum((Fraction(1)-Fraction(comb(t,k) if t>=k else 0,comb(n,k))-
               Fraction(comb(s,k) if s>=k else 0,comb(n,k))) for k in sizes)


def split_audit(mods, seeds=range(20261108,20261208), share=.2):
    n=len(mods); gids=sorted(set(mods)); target=round(n*share)
    if not 0<target<n or len(gids)<2:raise ValueError('Not enough rows or distinct modules')
    out=[]
    for seed in seeds:
        rng=random.Random(seed)
        perm=list(range(n));rng.shuffle(perm)
        test=set(perm[:target]);train=set(perm[target:])
        trm={mods[i] for i in train};tem={mods[i] for i in test}
        # New RNG with same seed but distinct salt, deterministic grouped allocation.
        rng2=random.Random(seed ^ 0xC0FFEE)
        shuffled=gids.copy();rng2.shuffle(shuffled)
        c=Counter(mods);gt=set();nn=0
        for g in shuffled:
            size=c[g]
            if len(gt)<len(gids)-1 and abs(nn+size-target)<abs(nn-target):
                gt.add(g);nn+=size
        if not gt:gt.add(min(shuffled,key=lambda g:(abs(c[g]-target),g)))
        if len(gt)==len(gids):gt.remove(shuffled[-1])
        gtr=set(gids)-gt
        assert gt and gtr and gt.isdisjoint(gtr)
        # Trace exact physical-module ID crossing of each partition.
        out.append({'seed':seed,
                    'row_split_test_size':len(test),
                    'row_split_distinct_shared_modules':len(trm & tem),
                    'row_split_test_rows_parent_seen_in_train':sum(mods[i] in trm for i in test),
                    'module_group_split_test_size':sum(c[g] for g in gt),
                    'module_group_split_distinct_shared_modules':len(gt & gtr),
                    'module_group_split_train_module_count':len(gtr),
                    'module_group_split_test_module_count':len(gt)})
    return out


def analyze_file(path):
    raw=Path(path).read_bytes()
    decoded=raw.decode('utf-8-sig')
    rr=list(csv.DictReader(decoded.splitlines()))
    if not rr or 'Mod_ID' not in rr[0]:raise ValueError('Missing official Mod_ID column')
    mods=[str(x.get('Mod_ID','')).strip() for x in rr]
    if any(not x for x in mods):raise ValueError('Missing Mod_ID: fail closed')
    sizes=Counter(mods)
    N=len(mods);G=len(sizes);S=round(.2*N)
    runs=split_audit(mods)
    seq=[x['row_split_distinct_shared_modules'] for x in runs]
    tfr=[x['row_split_test_rows_parent_seen_in_train']/x['row_split_test_size'] for x in runs]
    exact=exact_expected_shared_module_count(list(sizes.values()),S)
    path_cols=['ELHPath','ELLPath','IVPath','RefIVPath']
    pathmissing={k:sum(not str(r.get(k,'')).strip() for r in rr) if k in rr[0] else None for k in path_cols}
    test_group_counts=[x['module_group_split_test_size'] for x in runs]
    return {
      'status':'EXECUTED_ON_ACTUAL_UPLOADED_METADATA' if (N,G)==(613,438) else 'METADATA_ROW_COUNT_DIFFERS_FROM_2026_CATALOG__CHECK_VERSION',
      'original_filename':Path(path).name,'source_sha256':hashlib.sha256(raw).hexdigest(),'source_bytes':len(raw),
      'observed_row_count':N,'observed_unique_Mod_ID':G,'official_expected_counts':[613,438],
      'actual_repeated_module_IDs':sum(v>=2 for v in sizes.values()),
      'actual_rows_in_repeated_modules':sum(v for v in sizes.values() if v>=2),
      'actual_max_rows_per_module':max(sizes.values()),
      'actual_module_multiplicity_histogram':dict(sorted(Counter(sizes.values()).items())),
      'link_path_missing_count':pathmissing,
      'random_exact_test_rows':S,'split_seed_count':len(runs),
      'theoretical_random_row_expected_shared_modules_given_ACTUAL_distribution':str(float(exact)),
      'observed_100_random_splits_mean_shared_Mod_ID':statistics.mean(seq),
      'observed_100_random_splits_range_shared_Mod_ID':[min(seq),max(seq)],
      'observed_100_random_splits_mean_test_row_parent_seen_in_train_fraction':statistics.mean(tfr),
      'module_grouped_100_splits_max_shared_Mod_ID':max(x['module_group_split_distinct_shared_modules'] for x in runs),
      'module_grouped_100_splits_test_rows_range':[min(test_group_counts),max(test_group_counts)],
      'runs':runs,
      'claim_boundary':'These split protocols are NEW TESTS ON THE PROVIDED METADATA ONLY, not a replay of a published model, not an estimate of accuracy, not proof of image-parent independence beyond the provided Mod_ID, not new-site validation.'}

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('Usage: python audit_original_AnonDB.py path/to/AnonDB.csv path/to/report.json')
    result=analyze_file(sys.argv[1]);Path(sys.argv[2]).write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');
    print(json.dumps({k:v for k,v in result.items() if k!='runs'},indent=2))
