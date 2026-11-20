# MMF strategy report — run `smoke_20261112T000254`

Backend `ollama`, model `qwen2.5:14b` (digest `7cdf5a0187d5`), seed 0, temperature 0.0, MMF 0.1.0.dev0.
LLM calls: 9; total attempts: 10.
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
| Outcome | `cdc:UCOD` — Underlying cause of death (ICD-10 codes R95, W75, and R99) |
| Outcome subtypes | R95, W75, R99 (analysed separately) |
| Exposures | `cdc:SEX` |
| Covariates | `cdc:COMBGEST`, `cdc:CIG_REC` |
| Interactions | `SEX` × `COMBGEST` |
| Stratification | `cdc:CIG_REC` |
| Offset | — |
| Denominator | — |
| Time scale | `cdc:COMBGEST` |
| Design | cohort |
| Model class | cox_proportional_hazards |

Rationale: This study design follows a cohort of infants forward in time, examining the risk of sudden unexpected infant death (UCOD) after reaching 44 weeks postconceptional age. The inclusion of an interaction term between sex and postconceptional age allows us to assess whether male infants show an excess risk specifically after this age threshold, independent of prenatal smoking exposure. This model class is chosen because it can handle time-to-event data and adjust for the timing variable (COMBGEST). However, this strategy does not establish causality or provide power calculations.

Expected direction: The hypothesis predicts that male infants without prenatal smoking exposure will show an increased risk of sudden unexpected infant death after reaching 44 weeks postconceptional age compared to other groups.

Variable resolution:
- `cdc:UCOD` — OK: Underlying cause of death ICD-10 ICDF R95=SIDS R99=UNSPECIFIED W75=ACCIDENTAL SUFFOCATION (p.1)
- `cdc:SEX` — OK: Sex of infant (p.1)
- `cdc:COMBGEST` — OK: Combined gestation in weeks GESTF 17-47=WEEKS (p.1)
- `cdc:CIG_REC` — OK: Cigarette smoking during pregnancy (p.1)
Blockers:
- The documentation does not specify whether `COMBGEST` includes postconceptional age beyond 40 weeks. Since the research question requires assessing outcomes after reaching 44 weeks postconceptional age, this variable may be insufficient to capture the necessary timing information.

Caveats:
- The variable `COMBGEST` is documented as having a level of '99=UNKNOWN', which may introduce missingness in the data. This could affect the ability to accurately assess postconceptional age and thus impact the timing of the outcome assessment.

- The variable `CIG_REC` has levels `.B=DK/BLANK`, indicating that there are cases where smoking status is unknown or not reported, which may introduce missingness in the data. This could affect the stratification by prenatal smoking exposure.

- The documentation does not specify whether `COMBGEST` includes postconceptional age beyond 40 weeks (i.e., after birth). If it only covers gestational age up to birth, then the variable cannot be used to assess postconceptional age accurately.

Not assessed by MMF: statistical power; causal validity / confounding adequacy; actual missingness rates (documentation only; no row-level data read).
### S2 (for G2) — BLOCKED
**Question.** Is the earlier onset of risk for sudden unexpected infant death associated with prenatal smoking exposure consistent across different postconceptional age intervals?

| Element | Specification |
|---|---|
| Outcome | `cdc:UCOD` — Underlying cause of death (ICD-10 codes R95, W75, and R99) |
| Outcome subtypes | R95, W75, R99 (analysed separately) |
| Exposures | `cdc:CIG_REC` |
| Covariates | `cdc:COMBGEST`, `cdc:SEX` |
| Interactions | `CIG_REC` × `COMBGEST` |
| Stratification | `cdc:COMBGEST` |
| Offset | — |
| Denominator | — |
| Time scale | `cdc:AGED` |
| Design | cohort |
| Model class | cox_proportional_hazards |

Rationale: This study design and model class allow us to assess the timing of risk onset associated with prenatal smoking exposure across different postconceptional age intervals. The Cox proportional hazards model is appropriate for time-to-event data, enabling us to evaluate how the hazard ratio changes over time within specified strata (postconceptional age intervals). This approach does not establish causality or provide power calculations.

Expected direction: The analysis should reveal whether the risk associated with prenatal smoking exposure varies across different postconceptional age intervals. If the effect is consistent, we would expect to see a similar pattern of hazard ratios across these intervals.

Variable resolution:
- `cdc:UCOD` — OK: Underlying cause of death ICD-10 ICDF R95=SIDS R99=UNSPECIFIED W75=ACCIDENTAL SUFFOCATION (p.1)
- `cdc:CIG_REC` — OK: Cigarette smoking during pregnancy (p.1)
- `cdc:COMBGEST` — OK: Combined gestation in weeks GESTF 17-47=WEEKS (p.1)
- `cdc:SEX` — OK: Sex of infant (p.1)
- `cdc:AGED` — OK: Age at death in days NUMF 0-364=DAYS (p.1)
Blockers:
- The variable `COMBGEST` is documented as '99=UNKNOWN', but it is used for stratification. If a large proportion of records are missing gestational age, this could make the stratification impossible or highly unreliable.

- The variable `AGED` (age at death) does not provide clear guidance on how to define postconceptional age intervals necessary for the analysis.

Caveats:
- The variable `UCOD` is documented as having levels 'R95=SIDS', 'W75=ACCIDENTAL SUFFOCATION', and 'R99=UNSPECIFIED'. However, the research question specifies ICD-10 codes R95, W75, and R99 without further breakdown. The documentation does not provide additional details on how these categories are used in practice, which could lead to ambiguity.

- The variable `CIG_REC` is documented with levels '.B=DK/BLANK', '1=NO', and '2=YES'. This implies that there may be a significant number of records where smoking status during pregnancy is unknown or not reported ('.B=DK/BLANK'). This missingness could introduce bias if the pattern of missing data is non-random.

- The variable `COMBGEST` is documented with levels '99=UNKNOWN'. A substantial proportion of gestational age values may be recorded as 'unknown', which can lead to incomplete stratification and potential misclassification in the analysis.

- The variable `AGED` (age at death) is continuous but its documentation does not specify how it will be used for defining postconceptional age intervals. The strategy requires specific intervals, but these are not clearly defined or documented.

- Linkage between prenatal smoking exposure (`CIG_REC`) and outcome (`UCOD`) may require additional data linkage across different time points (prenatal period to infant death), which is not explicitly covered in the documentation.

Not assessed by MMF: statistical power; causal validity / confounding adequacy; actual missingness rates (documentation only; no row-level data read).
