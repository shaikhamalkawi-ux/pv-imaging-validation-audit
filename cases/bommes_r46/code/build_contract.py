#!/usr/bin/env python3
"""Generate and test lightweight experiment-indexed claim-support examples.
Pure executable reporting logic; cannot certify data it has not inspected.
"""
from pathlib import Path
import json,hashlib
base=Path(__file__).resolve().parent.parent
results=base/'results'
schema={
 '$schema':'https://json-schema.org/draft/2020-12/schema',
 '$id':'https://example.invalid/99pv/r46/experiment-claim-record.schema.json',
 'title':'99pv experiment-indexed claim-support record (research development schema, version 0.1)',
 'description':'A typed account of the evidence supporting a single reported result; not a formal study-quality score.',
 'type':'object','additionalProperties':False,
 'required':['record_id','report_doi','source_url','evidence_tier','experiment_id','input_modality','target_task','evaluation_unit','source_version','physical_parent_crosswalk','split_disjointness_unit','target_labels_used_for_selection','metric_name','metric_value','metric_unit','metric_support_n','claim_requested','claim_boundary'],
 'properties':{
  'record_id':{'type':'string','minLength':3},
  'report_doi':{'type':'string','minLength':3},
  'source_url':{'type':'string','format':'uri'},
  'evidence_tier':{'enum':['provider_abstract','publisher_abstract','original_full_methods','owner_code_or_data','raw_parent_manifest_replayed']},
  'experiment_id':{'type':'string','minLength':3},
  'input_modality':{'enum':['thermal_IR','EL','RGB','radiometric_features','mixed','unknown']},
  'target_task':{'type':'string','minLength':3},
  'evaluation_unit':{'enum':['image','crop','cell','module','plant','mask','unknown']},
  'source_version':{'type':['string','null']},
  'physical_parent_crosswalk':{'enum':['unavailable','author_described_only','replayed_from_raw_ids']},
  'split_disjointness_unit':{'enum':['image','physical_image_parent','cell','module','plant','unknown']},
  'target_labels_used_for_selection':{'enum':['yes','no_author_reported','no_replayed','unknown']},
  'metric_name':{'type':'string','minLength':3},
  'metric_value':{'type':['number','null']},
  'metric_unit':{'enum':['AUROC_percent','AUROC_fraction','accuracy_percent','F1_percent','mAP_fraction','other','not_reported']},
  'metric_support_n':{'type':['integer','null'],'minimum':1},
  'claim_requested':{'enum':['source_reported_score','author_reported_grouped_split','author_reported_crossplant_experiment','untouched_target_model_selection','replayed_physical_parent_disjointness']},
  'claim_boundary':{'type':'string','minLength':12},
  'raw_manifest_sha256':{'type':['string','null']},
  'zero_overlap_parents_replayed':{'type':['boolean','null']},
  'source_locators':{'type':'array','items':{'type':'string'}},
 }
}
records=[
 dict(record_id='BOMMES_B_E_TARGET_BEST',report_doi='10.1002/pip.3518',source_url='https://onlinelibrary.wiley.com/doi/10.1002/pip.3518',evidence_tier='original_full_methods',experiment_id='B-to-E target-best contrastive',input_modality='thermal_IR',target_task='binary anomaly discrimination',evaluation_unit='image',source_version='2022 published Table 5',physical_parent_crosswalk='author_described_only',split_disjointness_unit='module',target_labels_used_for_selection='yes',metric_name='AUROC',metric_value=96.64,metric_unit='AUROC_percent',metric_support_n=None,claim_requested='untouched_target_model_selection',claim_boundary='Target labels determine target-best selection; not a previously unseen target-label decision.',source_locators=['Table 5','Section 5.2']),
 dict(record_id='BOMMES_B_E_VALIDATION_PLANT',report_doi='10.1002/pip.3518',source_url='https://onlinelibrary.wiley.com/doi/10.1002/pip.3518',evidence_tier='original_full_methods',experiment_id='B-to-E validation on F contrastive',input_modality='thermal_IR',target_task='binary anomaly discrimination',evaluation_unit='image',source_version='2022 published Table 5',physical_parent_crosswalk='author_described_only',split_disjointness_unit='module',target_labels_used_for_selection='no_author_reported',metric_name='AUROC',metric_value=95.20,metric_unit='AUROC_percent',metric_support_n=None,claim_requested='author_reported_crossplant_experiment',claim_boundary='Author reports source B, target E, validation plant F; exact parent-manifest and checkpoint replay absent.',source_locators=['Table 5','Section 5.2']),
 dict(record_id='BOMMES_PHYSICAL_SPLIT_REQUEST_HOLD',report_doi='10.1002/pip.3518',source_url='https://onlinelibrary.wiley.com/doi/10.1002/pip.3518',evidence_tier='original_full_methods',experiment_id='B-to-E test split audit',input_modality='thermal_IR',target_task='binary anomaly discrimination',evaluation_unit='image',source_version='2022 published Table 5',physical_parent_crosswalk='author_described_only',split_disjointness_unit='module',target_labels_used_for_selection='no_author_reported',metric_name='AUROC',metric_value=95.20,metric_unit='AUROC_percent',metric_support_n=None,claim_requested='replayed_physical_parent_disjointness',claim_boundary='Source reports module grouping but raw module-to-image ID overlap has not been independently replayed.'),
 dict(record_id='DECARLO_REPORTED_MODULE_SPLIT',report_doi='10.3390/app16189018',source_url='https://www.mdpi.com/2076-3417/16/18/9018',evidence_tier='original_full_methods',experiment_id='modulewise thermal fault classification',input_modality='radiometric_features',target_task='six class fault classification',evaluation_unit='image',source_version='2026 paper',physical_parent_crosswalk='author_described_only',split_disjointness_unit='module',target_labels_used_for_selection='unknown',metric_name='Accuracy',metric_value=97.6,metric_unit='accuracy_percent',metric_support_n=None,claim_requested='author_reported_grouped_split',claim_boundary='Author reports module-wise 70/15/15; raw module identifiers and test support not independently recovered.')
]
def classify(x):
    typ=x['claim_requested'];tier=x['evidence_tier']
    if typ=='replayed_physical_parent_disjointness':
        if x.get('physical_parent_crosswalk')=='replayed_from_raw_ids' and x.get('zero_overlap_parents_replayed') is True and x.get('raw_manifest_sha256') and tier=='raw_parent_manifest_replayed':return 'ALLOW_RAW_REPLAYED_BOUND', 'Exact parent mapping and zero cross-split overlap replayed.'
        return 'HOLD_RAW_PARENT_BRIDGE','Cannot certify uninspected image-to-physical-parent disjointness.'
    if typ=='untouched_target_model_selection':
        if x['target_labels_used_for_selection']=='yes':return 'REJECT_STRONGER_CLAIM','Known target label use in checkpoint selection.'
        if x['target_labels_used_for_selection']=='no_replayed':return 'ALLOW_REPLAYED_SELECTION_BOUND','Checkpoint-label exposure replayed.'
        return 'HOLD_SELECTION_EXPOSURE','Author statement alone cannot certify an untouched target.'
    if typ=='author_reported_grouped_split':
        if tier in ('original_full_methods','owner_code_or_data','raw_parent_manifest_replayed') and x['split_disjointness_unit']!='unknown':return 'ALLOW_AUTHOR_REPORTED_ONLY','Reported split unit only, no physical manifest replay implied.'
        return 'HOLD_METHODS_REQUIRED','Original detailed methods absent or split unit unknown.'
    if typ=='author_reported_crossplant_experiment':
        if tier in ('original_full_methods','owner_code_or_data','raw_parent_manifest_replayed'):
            return 'ALLOW_AUTHOR_REPORTED_ONLY','The executed cross-plant task is reported; separate model selection and raw parent evidence.'
        return 'HOLD_METHODS_REQUIRED','Published source detail insufficient.'
    return 'ALLOW_SOURCE_REPORTED_ONLY','Report the original task, metric, units and limitations, without upgraded validity claims.'

for rec in records:
    status,why=classify(rec); rec['admission_status']=status;rec['admission_reason']=why
assert [r['admission_status'] for r in records]==['REJECT_STRONGER_CLAIM','ALLOW_AUTHOR_REPORTED_ONLY','HOLD_RAW_PARENT_BRIDGE','ALLOW_AUTHOR_REPORTED_ONLY']
# Synthetic logic tests are NOT observed PV cases.
synth=records[2].copy();synth.update({'physical_parent_crosswalk':'replayed_from_raw_ids','evidence_tier':'raw_parent_manifest_replayed','raw_manifest_sha256':'0'*64,'zero_overlap_parents_replayed':True})
assert classify(synth)[0]=='ALLOW_RAW_REPLAYED_BOUND'
synth['zero_overlap_parents_replayed']=False
assert classify(synth)[0]=='HOLD_RAW_PARENT_BRIDGE'
(results/'experiment_claim_record.schema.json').write_text(json.dumps(schema,indent=2)+'\n',encoding='utf8')
(results/'example_claim_records.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
(results/'claim_admission_tests.json').write_text(json.dumps({'real_source_examples':len(records),'statuses':[r['admission_status'] for r in records],'synthetic_logic_tests':2,'PASS':True,'scope':'Claim-bounding gates only; no raw PV data replay and no formal certification.'},indent=2)+'\n',encoding='utf8')
print('Claim-gate 4 observed documentary examples +2 synthetic unit tests PASS')
