#!/usr/bin/env python3
"""Visualization of the printed within-study Bommes Table 5 values only."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype']=42
matplotlib.rcParams['ps.fonttype']=42
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
root=Path(__file__).resolve().parent.parent
p=root/'results'/'Bommes_9Task_SelectionCondition_Matrix.csv'
r=list(csv.DictReader(open(p,encoding='utf8',newline='')))
X=list(range(len(r)))
fig,ax=plt.subplots(figsize=(10.1,3.4))
w=.245
for offset,regime,label in [(-w,'val0','Selected on validation plant 0'),(0,'val1','Selected on validation plant 1'),(w,'best_target','Selected on target labels (Best)')]:
 y=[float(x['contrastive_minus_crossentropy_'+regime]) for x in r]
 ax.bar([k+offset for k in X],y,width=w,label=label)
ax.axhline(0,color='black',linewidth=.9)
ax.set_xlim(-.55,len(X)-.45)
ax.set_ylabel('Contrastive minus cross-entropy\nAUROC (percentage points)')
ax.set_xticks(X,[x['task'].replace(' -> ','→')+('*' if x['winner_reversal_vs_both_validation_selectors']=='True' else '') for x in r])
ax.yaxis.set_major_locator(MultipleLocator(2))
ax.grid(axis='y',alpha=.2,linewidth=.6);ax.set_axisbelow(True)
ax.legend(loc='upper right',fontsize=8,frameon=False,ncol=1)
ax.text(.01,1.025,'* The winner under target-selected Best differs from both validation-plant selections',transform=ax.transAxes,fontsize=8)
fig.tight_layout(pad=1.0)
fig.savefig(root/'paper'/'bommes_selection_condition.pdf',bbox_inches='tight')
fig.savefig(root/'paper'/'bommes_selection_condition.png',dpi=200,bbox_inches='tight')
print('Saved figure')
