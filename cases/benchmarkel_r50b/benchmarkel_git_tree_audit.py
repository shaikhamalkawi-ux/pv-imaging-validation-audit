#!/usr/bin/env python3
"""Read-only, pinned, public GitHub *FILENAME MANIFEST* study; no image bytes.

This is NOT module-identity proof, physical leakage detection, or source-model
performance verification. Uses GitHub public REST trees at known SHA1 identities.
`--selftest` runs synthetic-only parser checks without network.

Usage: python benchmarkel_git_tree_audit.py PATH_TO_JSON_OUTPUT
       python benchmarkel_git_tree_audit.py --selftest
"""
import json, os, re, sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT_COMMIT='768b5e78596b429829b6b7aceb0ce4ac7b07788d'
OWNER='TheMakiran';REPO='BenchmarkELimages'
TREES={
 '20211104':{'train':'6968b18b00784d5c646f0cfe6a97e1495c59cb93','val':'36611df1e4e01c1c223db333e8db8834a33a5e8d','test':'8c5059495d2f33b9f49fec6a149764a74b23b258','aug':'02735f5a3f82bf338e352c2ea692f5bf231b70b5'},
 '20220723':{'train':'672ff5c4166880dd6289e17eb207a29d3c44257c','val':'c5e67d74149d05a79e22c90a26188e6b6977f82d','test':'45f6d2f381f1779c13b14836c1dd1fbb950a9b50'},
 '20221008':{'train':'a920ffd6ed1422a3eda6bc52106d818d9eab7faa','val':'be71cda629b0a394df79cb9562e8d01363d9b082','test':'9f7ececd2768647596b620aa67b34f3ab42d844a'}}


def strip_augmentation(name):
    # Source examples: flip_180_... and rotate_180_....
    return re.sub(r'^(?:(?:flip|rotate|rot|mirror|aug)_[a-z0-9]+_)+','',name,flags=re.I)


def filename_family(name):
    # Strictly parsing only `_r#_c#` sources (ARTS/CFVS/CSIR); other
    # BMRK/SDLE naming families are excluded, never assumed unrelated.
    base=strip_augmentation(name)
    m=re.fullmatch(r'(.+?)_r[0-9]+_c[0-9]+\.[^.]+',base,re.I)
    return m.group(1) if m else None


def summarize_release(label,data):
    required=['train','val','test'];assert all(x in data for x in required)
    out={'release':label,'commit':ROOT_COMMIT,'git_subtree_sha1':TREES[label],
         'claim_tier':'PINNED_GITHUB_TREE_FILENAMES_NOT_IMAGES_NOT_PHYSICAL_PARENT_REPLAY'}
    for split,files in data.items():
        if len(files)!=len(set(files)):
            raise ValueError('Duplicate path within tree '+label+'/'+split)
        out[split+'_file_count']=len(files)
        out[split+'_parsed_family_count']=len(set(filename_family(x) for x in files if filename_family(x)))
        out[split+'_unparsed_count']=sum(filename_family(x) is None for x in files)
    train_fams=set(filter(None,map(filename_family,data['train'])))
    val_fams=set(filter(None,map(filename_family,data['val'])))
    test_fams=set(filter(None,map(filename_family,data['test'])))
    raw_train=set(data['train']);norm_train=set(strip_augmentation(x) for x in data['train'])
    out['exact_filename_overlap_train_test']=len(raw_train.intersection(data['test']))
    out['normalized_original_image_overlap_train_test']=len(norm_train.intersection(data['test']))
    out['shared_filename_families_train_test']=len(train_fams.intersection(test_fams))
    out['shared_filename_families_train_val']=len(train_fams.intersection(val_fams))
    out['shared_filename_families_val_test']=len(test_fams.intersection(val_fams))
    out['test_files_with_parsed_family_shared_with_train']=sum(filename_family(n) in train_fams for n in data['test'])
    out['val_files_with_parsed_family_shared_with_train']=sum(filename_family(n) in train_fams for n in data['val'])
    out['train_unique_base_filenames_after_aug_normalization']=len(norm_train)
    out['sample_source_prefixes_train_test_shared']=sorted(train_fams.intersection(test_fams))[:10]
    out['limitations']=['Only strict _r#_c# name family parsed; other images unclassified, no physical no-overlap certificate','No image pixel byte verification','No evidence any specific paper model used this exact Git tree release','No model score re-executed']
    if 'aug' in data:
        aug=data['aug']
        out['separate_augmentation_matches_train_source_names']=sum(strip_augmentation(n) in raw_train for n in aug)
        out['separate_augmentation_unique_bases']=len({strip_augmentation(x) for x in aug})
        out['separate_augmentation_total']=len(aug)
    return out


def github_tree(sha):
    url=f'https://api.github.com/repos/{OWNER}/{REPO}/git/trees/{sha}'
    headers={'Accept':'application/vnd.github+json','User-Agent':'99pv-scientific-evidence-audit'}
    token=os.environ.get('GITHUB_TOKEN')
    if token:headers['Authorization']='Bearer '+token
    with urlopen(Request(url,headers=headers),timeout=35) as f:
        z=json.load(f)
    if z.get('sha')!=sha or z.get('truncated') or not isinstance(z.get('tree'),list):
        raise ValueError('Git subtree identity/truncation failure '+sha)
    if any(x.get('type')!='blob' for x in z['tree']):
        raise ValueError('Nested folders unexpected in image leaf '+sha)
    return [x['path'] for x in z['tree']]


def live_replay():
    out={'status':'SOURCE_DIRECTORY_REPLAY_PASS','mode':'public read-only GitHub API directory filename replay','study':'99pv_R50_BENCHMARKEL_RELEASE_GENEALOGY',
         'original_paper':'Pratt, Matheus & Klein, Systems and Soft Computing 5 (2023) 200048, DOI 10.1016/j.sasc.2023.200048',
         'source_repo':f'https://github.com/{OWNER}/{REPO}',
         'frozen_commit_sha1':ROOT_COMMIT,'not_a_sandia_data_replay':True,'releases':[]}
    for version,trees in TREES.items():
        data={split:github_tree(sha) for split,sha in trees.items()}
        out['releases'].append(summarize_release(version,data))
    return out


def selftest():
    assert strip_augmentation('flip_180_ARTS_00001_r4_c2.png')=='ARTS_00001_r4_c2.png'
    assert strip_augmentation('rotate_180_ARTS_00001_r4_c2.png')=='ARTS_00001_r4_c2.png'
    assert filename_family('ARTS_00001_r4_c2.png')=='ARTS_00001'
    assert filename_family('ARTS_00001_r6_c2.png')=='ARTS_00001'
    assert filename_family('BMRK_00018_cell0078.png') is None
    assert filename_family('SDLE_00822_A11-DH3000-3000h-PT-cell54.png') is None
    d={'train':['ARTS_00001_r4_c2.png','ARTS_00002_r4_c4.png'],
       'val':['ARTS_00002_r6_c1.png'],
       'test':['ARTS_00001_r6_c2.png'],
       'aug':['flip_180_ARTS_00001_r4_c2.png','rotate_180_ARTS_00001_r4_c2.png']}
    z=summarize_release('20211104',d)
    assert z['exact_filename_overlap_train_test']==0
    assert z['shared_filename_families_train_test']==1
    assert z['test_files_with_parsed_family_shared_with_train']==1
    assert z['separate_augmentation_matches_train_source_names']==2
    return {'synthetic_filename_parser_test':'PASS','checks':10,'scope':'synthetic-only; direct live GitHub API audit done separately via authorized connector'}

if __name__=='__main__':
    if len(sys.argv)==2 and sys.argv[1]=='--selftest':print(json.dumps(selftest(),indent=2))
    elif len(sys.argv)==2:
        result=live_replay();Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps([{k:v for k,v in x.items() if k in ['release','train_file_count','test_file_count','shared_filename_families_train_test']} for x in result['releases']],indent=2))
    else:raise SystemExit('Usage: python benchmarkel_git_tree_audit.py report.json | --selftest')
