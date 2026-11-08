#!/usr/bin/env python3
"""No raw input. Exact combinatorial certificate from OFFICIAL SUMMARY ONLY.

This NEVER estimates actual split overlap for any Sandia experiment.
All fixed-size randomization statements refer to uniformly choosing exactly
123 of 613 measurement sets for test; parent multiplicities are unknown.
"""
import json
from math import comb
from fractions import Fraction
from decimal import Decimal, localcontext
from pathlib import Path

N=613;G=438; S=123; T=N-S; D=N-G


def expected_both_group(k, n=N, train=T, test=S):
    if k <= 1:
        return Fraction(0)
    return Fraction(1) - Fraction(comb(train, k) if train>=k else 0, comb(n,k)) - Fraction(comb(test,k) if test>=k else 0, comb(n,k))


def solution():
    lo=expected_both_group(D+1)
    hi=D*expected_both_group(2)
    with localcontext() as ctx:
        ctx.prec=55
        v_lo=str(Decimal(lo.numerator)/Decimal(lo.denominator))
        v_hi=str(Decimal(hi.numerator)/Decimal(hi.denominator))
        v_c=str(Decimal(expected_both_group(2).numerator)/Decimal(expected_both_group(2).denominator))
    return {
      'project':'99pv', 'stage':'R50_FIXED_COUNTS_ONLY',
      'source_url':'https://data.openei.org/submissions/8378',
      'dataset_doi':'10.11578/3818365',
      'source_basis':'official descriptive counts only; original AnonDB.csv NOT obtained',
      'N_reported_measurement_sets':N,'G_reported_unique_modules':G,
      'repeated_measurement_excess_D':D,
      'number_of_repeated_module_IDs_range':[1,D],
      'number_of_measurement_sets_from_repeated_module_IDs_range':[D+1,2*D],
      'train_rows_for_hypothetical_exact_fixed_split':T,
      'test_rows_for_hypothetical_exact_fixed_split':S,
      'design':'uniformly random exact 490/123 measurement-row split; hypothetical only',
      'expected_count_of_distinct_shared_modules_min':v_lo,
      'min_extremal_configuration':'1 module has 176 measurement sets; remaining 437 modules have 1 each',
      'expected_count_of_distinct_shared_modules_max':v_hi,
      'max_extremal_configuration':'175 modules have 2 measurement sets; remaining 263 have 1 each',
      'probability_one_pair_straddles_fixed_split':v_c,
      'formula':'sum over physical modules j of {1-[C(T,n_j)+C(S,n_j)]/C(N,n_j)}, with C(t,k)=0 if t<k',
      'sharpness_proof':'f(k) is nondecreasing and discretely concave in k>=1, f(1)=0; with D=N-G excess rows, the minimum occurs when all excess rows belong to one module, and the maximum when D separate modules each have exactly two observations',
      'not_observed':['actual Mod_ID multiplicity histogram','any actual random split','actual cross-split overlap','any model accuracy or change in prediction performance','site-level independence or leakage in a published experiment'],
      'strict_hold':'HOLD_RAW_METADATA_ANONDB_CSV' }

if __name__=='__main__':
    d=solution();p=Path(__file__).with_name('fixed_count_certificate.json');p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(d,indent=2))
