# MMF strategy report — run `smoke_20261112T001017`

Backend `ollama`, model `qwen2.5:14b` (digest `7cdf5a0187d5`), seed 0, temperature 0.0, MMF 0.1.0.dev0.
LLM calls: 9; total attempts: 12.
> MMF proposes; the investigator decides. This report does not assess statistical power or causal validity and no row-level data were read.

## Inputs
| Role | File | sha256 |
|---|---|---|
| codebook | tests/fixtures/mini_codebook.txt | `77ba5a0e65da8475` |
| manuscript | tests/fixtures/mini_manuscript.md | `93c9a343932cf038` |

## A. Manuscripts
### Developmental timing of sudden unexpected infant death (`mini_manuscript`)
Designs: population_incidence. Models: poisson_regression, negative_binomial. Data: linked birth and infant death records.

Research questions:
- What is the developmental timing of sudden unexpected infant death?

Claims (4):
- **mini_manuscript.C1** [method] The study used linked birth and infant death records to examine sudden unexpected infant death. — p.1: "We used linked birth and infant death records."

- **mini_manuscript.C2** [finding] Male infants showed an excess risk of sudden unexpected infant death after reaching 44 weeks postconceptional age. — p.1: "Male excess risk emerged only after 44 weeks postconceptional age."

- **mini_manuscript.C3** [finding] Prenatal smoking was associated with an earlier onset of the risk for sudden unexpected infant death. — p.1: "Prenatal smoking was associated with earlier onset of risk."

- **mini_manuscript.C4** [limitation] The study lacked information on the sleep environment, which is not available in the linked birth-death files. — p.1: "A limitation is that the sleep environment was not available in the linked birth-death files."


## B. Data sources and concept map
- `cdc`: Mini codebook (fixture) — 6 documented variables.


| Concept | Source | Variable | Compatibility | Rationale |
|---|---|---|---|---|
| outcome | cdc | UCOD | direct | The UCOD variable in the CDC data source includes codes R95, R99, and W75 which correspond to SIDS (Sudden Infant Death Syndrome), unspecified cause of death, and accidental suffocation respectively. These are the underlying cause of death codes specified as outcomes. |
| age at outcome | cdc | AGED | direct | The AGED variable in the CDC data source represents age at death in days, which directly corresponds to the concept of 'age at outcome'. |
| postconceptional age | cdc | COMBGEST | derived | The COMBGEST variable in the CDC data source represents combined gestation in weeks. To derive postconceptional age, one would need to add this value (converted from weeks to days) to the chronological age at death (which is not directly provided but can be inferred from AGED). |
| male sex | cdc | SEX | direct | The SEX variable in the CDC data source indicates the sex of the infant, which can be used to stratify by male or female. |
| prenatal smoking | cdc | CIG_REC | proxy | The CIG_REC variable in the CDC data source indicates cigarette smoking during pregnancy, which is a proxy for prenatal smoking exposure. |

## C. Knowledge gaps
### G1. Investigate whether male infants without prenatal smoking exposure show a similar excess risk of sudden unexpected infant death after reaching 44 weeks postconceptional age.
- Rationale: The manuscript identified an excess risk for male infants after 44 weeks postconceptional age (mini_manuscript.C2). However, it did not specify whether this risk is present in the absence of prenatal smoking exposure. This gap aims to isolate the effect of sex on sudden unexpected infant death timing.
- Prior art: The manuscript found that male infants showed an excess risk after 44 weeks postconceptional age (mini_manuscript.C2). However, it did not examine whether this risk persists in the absence of prenatal smoking exposure.
- Supporting claims: mini_manuscript.C2
- Required variables: `cdc:COMBGEST`, `cdc:SEX`, `cdc:UCOD`
### G2. Determine if the earlier onset of risk for sudden unexpected infant death associated with prenatal smoking exposure is consistent across different postconceptional age intervals.
- Rationale: The manuscript reported that prenatal smoking was linked to an earlier onset of risk (mini_manuscript.C3). However, it did not explore whether this effect varies by specific postconceptional age intervals. This gap seeks to understand if the timing of risk onset is consistent across different developmental stages.
- Prior art: The manuscript found that prenatal smoking was associated with an earlier onset of risk (mini_manuscript.C3). However, it did not investigate whether this effect varies by specific postconceptional age intervals.
- Supporting claims: mini_manuscript.C3
- Required variables: `cdc:COMBGEST`, `cdc:CIG_REC`, `cdc:UCOD`

## D. Strategies and E. feasibility
### S1 (for G1) — BLOCKED
**Question.** Does male sex without prenatal smoking exposure increase the risk of sudden unexpected infant death after reaching 44 weeks postconceptional age?

| Element | Specification |
|---|---|
| Outcome | `cdc:UCOD` — ICD-10 codes R95 (SIDS), W75 (accidental suffocation), and R99 (unspecified) define sudden unexpected infant death. |
| Outcome subtypes | — |
| Exposures | `cdc:SEX` |
| Covariates | `cdc:COMBGEST`, `cdc:CIG_REC` |
| Interactions | `SEX` × `COMBGEST` |
| Stratification |  |
| Offset | — |
| Denominator | — |
| Time scale | `cdc:AGED` |
| Design | cohort |
| Model class | cox_proportional_hazards |

Rationale: This study design follows a cohort of infants forward to investigate the risk of sudden unexpected infant death after reaching 44 weeks postconceptional age, stratified by sex and without prenatal smoking exposure. The Cox proportional hazards model is used because it can handle time-to-event data and adjust for covariates such as gestational age.

Expected direction: The expected direction would be that male infants show a higher risk of sudden unexpected infant death after reaching 44 weeks postconceptional age compared to female infants, in the absence of prenatal smoking exposure. This study does not establish causality or power but aims to isolate the effect of sex on this outcome.

Variable resolution:
- `cdc:UCOD` — OK: Underlying cause of death ICD-10 ICDF R95=SIDS R99=UNSPECIFIED W75=ACCIDENTAL SUFFOCATION (p.1)
- `cdc:SEX` — OK: Sex of infant (p.1)
- `cdc:COMBGEST` — OK: Combined gestation in weeks GESTF 17-47=WEEKS (p.1)
- `cdc:CIG_REC` — OK: Cigarette smoking during pregnancy (p.1)
- `cdc:AGED` — OK: Age at death in days NUMF 0-364=DAYS (p.1)
Blockers:
- There is no explicit documentation that confirms the variable `AGED` captures ages beyond 280 days (40 weeks postconceptional age). Without this confirmation, it's impossible to ensure that only infants reaching 44 weeks are included in the analysis.

- The definition of `UCOD` does not specify whether it includes deaths after reaching 44 weeks postconceptional age. This makes it impossible to accurately identify the outcome as specified.

Caveats:
- The variable `COMBGEST` is documented as having a level of '99=UNKNOWN', which may introduce missingness and bias if not properly accounted for in the analysis.

- The variable `CIG_REC` has levels `.B=DK/BLANK`, indicating that there are cases where smoking status during pregnancy is unknown or not reported, potentially leading to incomplete data on prenatal smoking exposure.

- The documentation does not specify whether the variable `UCOD` includes only deaths after 44 weeks postconceptional age. If it includes earlier deaths, this could introduce bias in estimating the risk of sudden unexpected infant death after reaching 44 weeks.

- The variable `AGED` is documented as 'Age at death in days', but there's no explicit mention that this variable captures ages beyond 280 days (40 weeks postconceptional age). This may require additional filtering to ensure the analysis only includes infants who reach 44 weeks postconceptional age.

- The definition of `UCOD` does not explicitly state whether it is restricted to deaths after reaching 44 weeks postconceptional age, which could introduce bias if the outcome includes earlier deaths.

Not assessed by MMF: statistical power; causal validity / confounding adequacy; actual missingness rates (documentation only; no row-level data read).
### S2 (for G2) — feasible
**Question.** Is the earlier onset of risk for sudden unexpected infant death associated with prenatal smoking exposure consistent across different postconceptional age intervals?

| Element | Specification |
|---|---|
| Outcome | `cdc:UCOD` — R95=SIDS, R99=UNSPECIFIED, W75=ACCIDENTAL SUFFOCATION |
| Outcome subtypes | — |
| Exposures | `cdc:CIG_REC` |
| Covariates | `cdc:COMBGEST` |
| Interactions | `CIG_REC` × `COMBGEST` |
| Stratification |  |
| Offset | — |
| Denominator | — |
| Time scale | `cdc:AGED` |
| Design | cohort |
| Model class | cox_proportional_hazards |

Rationale: This study design will assess whether the risk of sudden unexpected infant death associated with prenatal smoking exposure varies across different postconceptional age intervals. The Cox proportional hazards model is chosen because it allows for the analysis of time-to-event data, which is appropriate for studying the timing of risk onset. However, this strategy does not establish causality or provide information on statistical power.

Expected direction: The expected direction would be that the interaction term between prenatal smoking and postconceptional age shows a significant effect, indicating that the risk associated with prenatal smoking varies across different developmental stages.

Variable resolution:
- `cdc:UCOD` — OK: Underlying cause of death ICD-10 ICDF R95=SIDS R99=UNSPECIFIED W75=ACCIDENTAL SUFFOCATION (p.1)
- `cdc:CIG_REC` — OK: Cigarette smoking during pregnancy (p.1)
- `cdc:COMBGEST` — OK: Combined gestation in weeks GESTF 17-47=WEEKS (p.1)
- `cdc:AGED` — OK: Age at death in days NUMF 0-364=DAYS (p.1)
Caveats:
- The variable `UCOD` is documented as having levels 'R95=SIDS', 'R99=UNSPECIFIED', and 'W75=ACCIDENTAL SUFFOCATION'. However, the documentation does not specify if these codes are mutually exclusive or if a death can be classified under multiple codes. This ambiguity could lead to misclassification of outcomes.

- The variable `CIG_REC` has levels '.B=DK/BLANK', '1=NO', and '2=YES'. The level '.B=DK/BLANK' indicates missing data due to don't know or blank responses, which may introduce bias if the missingness is not random. Additionally, there is no information on how many individuals fall into this category, making it difficult to assess its impact.

- The variable `COMBGEST` has a level '99=UNKNOWN', indicating that gestational age might be unknown for some cases. This could lead to incomplete data and potential bias if the missingness is not random or if there are systematic differences between those with known and unknown gestational ages.

- The variable `AGED` (age at death in days) is documented as a continuous variable, but it may have limitations due to rounding or truncation issues. For example, if deaths are recorded only up to the nearest month rather than day, this could introduce measurement error.

Not assessed by MMF: statistical power; causal validity / confounding adequacy; actual missingness rates (documentation only; no row-level data read).
