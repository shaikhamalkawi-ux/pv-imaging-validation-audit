#!/usr/bin/env python3
"""Reproduce bounded 99pv R46 Bommes Table-5 claim-support diagnostics.
Reads only the frozen R44 Pilot02 small extracted source table (not PV images).
Requires Python 3 stdlib, optionally matplotlib for a publication figure.
NOT final PRISMA, NOT new classifier execution, NOT causal effect estimation.
"""
from pathlib import Path
from collections import defaultdict
import zipfile,csv,io,json,hashlib,decimal,sys,os
ROOT=Path(__file__).resolve().parent.parent
IN=ROOT/'source_inputs'/'PILOT02_VERIFIED_LOCKED.zip'
D=ROOT/'results'; D.mkdir(exist_ok=True)
EXPECTED_BUNDLE='3b7ae7d930851a96aa4911149ec400e67f1978e21c05bd0fc168b829d5e2c81b'
TABLE=ROOT/'source_inputs'/'Bommes2022_Table5_54_SourceExtract_OriginalPublishedNumbers.csv'
EXPECTED_TABLE='7fbcf79eb0f27f9555d24fb86a51f1b90607220b13a32bb5f042b6085425a872'
DEC=decimal.Decimal

def h(b):return hashlib.sha256(b).hexdigest()
def get():
    if TABLE.exists():
        b=TABLE.read_bytes()
        if IN.exists():
            assert h(IN.read_bytes())==EXPECTED_BUNDLE, 'Pilot02 ZIP hash mismatch'
            with zipfile.ZipFile(IN) as z:
                assert z.testzip() is None,'Pilot02 CRC mismatch'
                assert b==z.read('INPUTS/99pv_R44_Bommes2022_ResultLevel_54_20261104.csv')
    else:
        assert h(IN.read_bytes())==EXPECTED_BUNDLE, 'Pilot02 ZIP hash mismatch'
        with zipfile.ZipFile(IN) as z:
            assert z.testzip() is None,'Pilot02 CRC mismatch'
            b=z.read('INPUTS/99pv_R44_Bommes2022_ResultLevel_54_20261104.csv')
    assert h(b)==EXPECTED_TABLE, 'Frozen source-extraction table hash mismatch'
    d=list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))))
    assert len(d)==54
    return d

def writecsv(name, rows, fields):
    with open(D/name,'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def run():
    rows=get(); d=defaultdict(dict)
    for row in rows:
        key=(row['source_plant'],row['target_plant'])
        assert row['method'] in ['contrastive','crossentropy']
        assert row['selection_regime'] in ['val0','val1','best_target']
        field=(row['method'],row['selection_regime'])
        assert field not in d[key]
        d[key][field]=DEC(row['score_AUROC_0_to_100'])
    assert len(d)==9
    table=[]; gaps=[]; flips=[]
    for pair in sorted(d):
        x=d[pair]; assert len(x)==6
        src,tgt=pair
        signs=[]
        record={'source_plant':src,'target_plant':tgt,'task':src+' -> '+tgt}
        for regime in ('val0','val1','best_target'):
            c=x[('contrastive',regime)]; e=x[('crossentropy',regime)]
            record['contrastive_'+regime]=str(c)
            record['crossentropy_'+regime]=str(e)
            dif=c-e; record['contrastive_minus_crossentropy_'+regime]=str(dif)
            signs.append('C' if dif>0 else 'E' if dif<0 else 'TIE')
        record['selected_winner_val0']=signs[0]
        record['selected_winner_val1']=signs[1]
        record['selected_winner_target_best']=signs[2]
        record['winner_reversal_vs_both_validation_selectors']=str(signs[2]!=signs[0] and signs[2]!=signs[1])
        if signs[2]!=signs[0] and signs[2]!=signs[1]: flips.append(record['task'])
        for meth in ('contrastive','crossentropy'):
            for regime in ('val0','val1'):
                gap=x[(meth,'best_target')]-x[(meth,regime)]
                gaps.append({'task':src+' -> '+tgt,'method':meth,'validation_selector':regime,'target_best_auroc':str(x[(meth,'best_target')]),'other_plant_validation_auroc':str(x[(meth,regime)]),'target_best_minus_validation_pp':str(gap),'descriptive_not_causal':'TRUE'})
        table.append(record)
    assert len(gaps)==36
    assert len(flips)==3 and set(flips)=={'B -> E','B -> F','F -> A'}
    maxima={m:max([g for g in gaps if g['method']==m],key=lambda x:DEC(x['target_best_minus_validation_pp'])) for m in ('contrastive','crossentropy')}
    assert maxima['contrastive']['target_best_minus_validation_pp']=='11.71'
    assert maxima['crossentropy']['target_best_minus_validation_pp']=='19.73'
    writecsv('Bommes_9Task_SelectionCondition_Matrix.csv',table, list(table[0]))
    writecsv('Bommes_36_TargetBestMinusOtherPlantVal_Differences.csv',gaps,list(gaps[0]))
    qa={'project':'99pv','stage':'R46','source_doi':'10.1002/pip.3518',
        'source_url':'https://onlinelibrary.wiley.com/doi/10.1002/pip.3518',
        'reported_source_table':'Table 5, nine cross-plant rows; @Val0, @Val1 and Best for two classifiers',
        'input_sha256':{'pilot02_zip':EXPECTED_BUNDLE,'source_extraction_54':EXPECTED_TABLE},
        'original_extracted_cells':len(rows),'independent_tasks':len(d),'method_regimes_per_task':6,'comparison_count':len(gaps),
        'reversals_val0_and_val1_vs_best':len(flips),'reversal_tasks':flips,
        'max_gap_contrastive':maxima['contrastive'],'max_gap_crossentropy':maxima['crossentropy'],
        'no_heldout_raw_model_replay':True,'no_new_independent_studies':True,'no_prisma_rate':True,'no_causal_gap_claim':True,
        'no_standalone_cross_study_numeric_pooling':True,
        'assumption':'Treat displayed two-decimal AUROC as descriptive printed values; difference unit percentage points; no inferential CI or test.'}
    (D/'R46_Independent_CalculationQA.json').write_text(json.dumps(qa,indent=2)+'\n',encoding='utf8')
    print(json.dumps(qa,indent=2))
    return table,qa
if __name__=='__main__':run()
