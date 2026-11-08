#!/usr/bin/env python3
"""Public-safe deterministic Bommes Table-5 descriptive sign check; no prediction model or raw PV image needed.
Usage: python reproduce_rounding_public.py R46_AUTHOR_REVIEW_REPRODUCIBLE_20261107.zip
"""
from pathlib import Path
import zipfile,csv,io,collections,decimal,sys,json
p=Path(sys.argv[1]) if len(sys.argv)>1 else Path('R46_AUTHOR_REVIEW_REPRODUCIBLE_20261107.zip')
with zipfile.ZipFile(p) as z:
 records=list(csv.DictReader(io.StringIO(z.read('source_inputs/Bommes2022_Table5_54_SourceExtract_OriginalPublishedNumbers.csv').decode('utf-8-sig'))))
assert len(records)==54
M=collections.defaultdict(dict)
for r in records: M[(r['source_plant'],r['target_plant'])][r['method'],r['selection_regime']]=decimal.Decimal(r['score_AUROC_0_to_100'])
assert len(M)==9
reversals=[]
for (s,t),d in sorted(M.items()):
 diffs={k:d['contrastive',k]-d['crossentropy',k] for k in ('val0','val1','best_target')}
 if diffs['best_target']*diffs['val0']<0 and diffs['best_target']*diffs['val1']<0:
  assert all(abs(v)>decimal.Decimal('0.01') for v in diffs.values())
  reversals.append({'task':s+'->'+t,'deltas_source_printed_two_decimals':{k:str(v) for k,v in diffs.items()},'rounding_halfwidth_per_cell':'0.005','paired_delta_rounding_halfwidth':'0.010'})
assert [r['task'] for r in reversals]==['B->E','B->F','F->A']
print(json.dumps({'source_cells':54,'source_target_tasks':9,'reversals_robust_to_two_decimal_display_rounding':reversals,'not_inference':'no statistical significance, causality, leakage certificate or model retraining'},indent=2))
