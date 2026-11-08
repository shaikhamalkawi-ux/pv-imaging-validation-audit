import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parent.parent
s=json.loads((ROOT/'results/R52_SUMMARY.json').read_text())
e=json.loads((ROOT/'results/R52_EXPLORATORY_SUBGROUP_SUMMARY.json').read_text())
fig,ax=plt.subplots(figsize=(8.0,4.5))
models=['nameplate_fixed_ratio1','metadata_ridge_no_id','past_IV_ID_lookup_NEGATIVE_CONTROL']
name=['Nameplate constant','Non-ID metadata Ridge','Past-IV lookup control']
y1=[s['results']['random_row'][m]['MAE_ratio_pctpt_mean'] for m in models]
y2=[s['results']['module_grouped'][m]['MAE_ratio_pctpt_mean'] for m in models]
x=np.arange(3)
ax.bar(x-.18,y1,width=.36,label='Random metadata-row split')
ax.bar(x+.18,y2,width=.36,label='Unseen-Mod_ID split')
ax.set_xticks(x,name)
ax.set_ylabel('Pmp/nameplate MAE (percentage points)')
ax.set_title('Original Sandia metadata-only regression (not EL imaging)')
ax.legend(frameon=False,loc='upper right');ax.set_ylim(0,2.6);ax.grid(axis='y',alpha=.12)
fig.text(.08,.025,'100 fixed seeds. Each test has 120 rows. Descriptive only; not independent-site testing.',fontsize=8)
fig.tight_layout(rect=(.02,.11,.98,.98))
fig.savefig(ROOT/'results/R52_METADATA_ONLY_MAE_FIGURE.png',dpi=170,bbox_inches='tight')
plt.close(fig)
fig,ax=plt.subplots(figsize=(7.3,4.2))
names=['Source Mod_ID seen\nin training','Source Mod_ID unseen\nin training']
vals=[e['results']['seen_MAE_ratio_pctpoints']['mean'],e['results']['unseen_MAE_ratio_pctpoints']['mean']]
ax.bar(names,vals,width=.52);ax.set_ylim(0,1.18)
ax.set_ylabel('Mean absolute error (percentage points)')
ax.set_title('Exploratory within the SAME random-row test cohorts')
ax.grid(axis='y',alpha=.12)
for i,v in enumerate(vals):ax.text(i,v+.025,f'{v:.3f}',ha='center',fontsize=10)
fig.text(.08,.025,'Different module populations. Not causal; not a defect-detection result.',fontsize=8)
fig.tight_layout(rect=(.02,.11,.98,.98))
fig.savefig(ROOT/'results/R52_EXPLORATORY_WITHIN_TEST_FIGURE.png',dpi=170,bbox_inches='tight')
plt.close(fig)
print('FIGURES_READY')
