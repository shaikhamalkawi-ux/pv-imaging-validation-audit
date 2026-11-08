#!/usr/bin/env python3
"""Offline reproducibility self-checks. No raw Sandia source, images or network.
The verifier distinguishes stored derived evidence from actual model re-execution.
"""
import csv, json, hashlib, subprocess, sys, tempfile, shutil, pathlib, ast
ROOT=pathlib.Path(__file__).resolve().parent.parent

def digest(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def read_json(p):return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))

checks=[]
def ok(name,condition):
 if not condition:raise AssertionError(name)
 checks.append(name)

src=ROOT/'cases/bommes_r46/source_inputs/Bommes2022_Table5_54_SourceExtract_OriginalPublishedNumbers.csv'
ok('published_54cell_source_hash',digest(src)=='7fbcf79eb0f27f9555d24fb86a51f1b90607220b13a32bb5f042b6085425a872')
with src.open(newline='',encoding='utf-8-sig') as f:rec=list(csv.DictReader(f))
ok('bommes_54cells',len(rec)==54)
with tempfile.TemporaryDirectory() as td:
 sandbox=pathlib.Path(td)/'bommes'
 shutil.copytree(ROOT/'cases/bommes_r46',sandbox)
 proc=subprocess.run([sys.executable,str(sandbox/'code/reproduce.py')],capture_output=True,text=True)
 ok('bommes_fresh_replay',proc.returncode==0)
 for n in ['Bommes_36_TargetBestMinusOtherPlantVal_Differences.csv','Bommes_9Task_SelectionCondition_Matrix.csv','R46_Independent_CalculationQA.json']:
  ok('bommes_output_parity_'+n, digest(sandbox/'results'/n)==digest(ROOT/'cases/bommes_r46/results'/n))
 proc2=subprocess.run([sys.executable,str(sandbox/'code/build_contract.py')],capture_output=True,text=True)
 ok('bommes_claim_rules_executed',proc2.returncode==0)
 for n in ['experiment_claim_record.schema.json','example_claim_records.json','claim_admission_tests.json']:
  ok('contract_parity_'+n,digest(sandbox/'results'/n)==digest(ROOT/'cases/bommes_r46/results'/n))

r52=read_json(ROOT/'cases/sandia_r52/results/R52_SUMMARY.json')
ok('sandia_R52_original_source_hash',r52['original_source_sha256']=='8fe450440d989f9aa469f0fc206c76b13021a93dbb6071ddc3a1967fd083440e')
ok('sandia_R52_n598',r52['eligible_rows']==598 and r52['unique_eligible_modules']==420)
ok('sandia_R52_100seeds',r52['seed_count']==100)
rr=r52['results'];row=rr['random_row'];grp=rr['module_grouped']
ok('sandia_R52_model_MAE_values',abs(row['metadata_ridge_no_id']['MAE_ratio_pctpt_mean']-.8649965134666924)<1e-13 and abs(grp['metadata_ridge_no_id']['MAE_ratio_pctpt_mean']-.8789932610681129)<1e-13)
ok('sandia_R52_explicit_split_parent_support',row['shared_Mod_ID_mean']==56.17 and grp['shared_Mod_ID_mean']==0)
with (ROOT/'cases/sandia_r52/results/R52_ALL_200_SPLITS_METRICS.csv').open(newline='') as f:
 met=list(csv.DictReader(f))
ok('sandia_R52_result_rows_200',len(met)==200)

public=read_json(ROOT/'cases/benchmarkel_r50b/benchmarkel_connector_replay_results.json')
releases=public.get('versions',[])
ok('benchmark_three_releases',len(releases)==3)
ok('benchmark_filename_family_counts',[x['train_test_shared_parsed_source_families'] for x in releases]==[22,33,34])
ok('benchmark_zero_literal_crop_intersection',all(x['train_test_identical_filenames']==0 for x in releases))
ok('benchmark_2021_augmentation',releases[0]['train_augmented_separately']==1434 and releases[0]['train_augmented_names_matching_train_original']==1434)

for rel in ['cases/sandia_r50/audit_original_AnonDB.py','cases/sandia_r52/src/run_metadata_control.py','cases/sandia_r53_pending/src/run_R53_on_original_EL_pixels.py']:
 p=ROOT/rel;ast.parse(p.read_text(encoding='utf-8'));checks.append('syntax_'+p.name)

print(json.dumps({'status':'PASS','offline_checks':len(checks),'checks':checks,'scope':'public-source arithmetic/derived-output QA only; Sandia raw CSV and EL.zip not redistributed or replayed by this checker'},indent=2))
