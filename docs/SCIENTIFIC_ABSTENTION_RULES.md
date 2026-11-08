# Source-gated claim rules

| Observation | Bound | DO NOT claim |
|---|---|---|
| Literal original crop file names disjoint | No identical file basename among compared directories | Physical module parent disjoint, no leakage |
| Candidate `_r#_c#` prefix appears across splits | Same parser-generated candidate source family | Identity of real physical module, model contamination |
| Original Sandia `Mod_ID` shows cross-split overlap | New row split contains measurements from known modules | Any previous published paper used the same split; a specific model overfit |
| `Mod_ID` grouped held-out | No shared declared module key in test/train for new split | New-site/new-factory/new-year independence |
| Nonimage Ridge random vs grouped MAE difference | Descriptive score difference for same target and model but different test source compositions | Causal leakage penalty, significance or PV defect detector score |
| R53 image protocol passed synthetic tests | Code structurally ready pending original TIFF pixels | Model fitted/tested on real EL images |
| Printed Table 5 selection comparison | Published checkpoint-policy effects and rounding sensitivity | 54 independent studies, retrained model, corrected AUROC significance |
