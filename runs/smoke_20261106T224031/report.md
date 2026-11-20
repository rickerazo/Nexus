# MMF strategy report — run `smoke_20261106T224031`

Backend `ollama`, model `qwen2.5:14b` (digest `7cdf5a0187d5`), seed 0, temperature 0.0, MMF 0.1.0.dev0.
LLM calls: 9; total attempts: 9.
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
| outcome | cdc | UCOD | direct | The variable UCOD in the CDC data source captures the underlying cause of death using ICD-10 codes, which directly matches the manuscript's operationalization of outcome with specific codes R95 (SIDS), R99 (unspecified), and W75 (accidental suffocation). |
| age at outcome | cdc | AGED | direct | The variable AGED in the CDC data source captures age at death in days, which directly corresponds to the manuscript's operationalization of age at outcome. |
| postconceptional age | cdc | COMBGEST | derived | The variable COMBGEST in the CDC data source captures combined gestation in weeks, which can be used to derive postconceptional age by adding it to the chronological age after birth. However, since the exact chronological age is not provided, this mapping is derived and requires additional information. |
| male sex | cdc | SEX | direct | The variable SEX in the CDC data source captures the sex of the infant, which directly corresponds to the manuscript's operationalization of male sex as a stratifying variable. |
| prenatal smoking | cdc | CIG_REC | direct | The variable CIG_REC in the CDC data source captures cigarette smoking during pregnancy, which directly corresponds to the manuscript's operationalization of prenatal smoking as an exposure variable. |

## C. Knowledge gaps
### G1. The effect of prenatal smoking on the risk of sudden unexpected infant death may vary by postconceptional age.
- Rationale: While the manuscript establishes that prenatal smoking is associated with an earlier onset of risk, it does not explore whether this association varies at different developmental stages (postconceptional ages).
- Prior art: The manuscript tested the general association between prenatal smoking and the timing of sudden unexpected infant death but did not investigate how this relationship might change across different postconceptional age intervals.
- Supporting claims: mini_manuscript.C3
- Required variables: `cdc:CIG_REC`, `cdc:COMBGEST`, `cdc:UCOD`
### G2. The risk of sudden unexpected infant death for male infants may be influenced by the sleep environment, which is not captured in the current dataset.
- Rationale: Although the manuscript identifies a developmental timing effect specific to male infants, it acknowledges that information on the sleep environment is lacking. This gap suggests exploring how the sleep environment might modify risk patterns observed in male infants.
- Prior art: The manuscript tested for excess risk among male infants after 44 weeks postconceptional age but did not account for potential modifying factors like the sleep environment due to data limitations.
- Supporting claims: mini_manuscript.C2, mini_manuscript.C4
- Required variables: `cdc:SEX`, `cdc:COMBGEST`, `cdc:UCOD`

## D. Strategies and E. feasibility
### S1 (for G1) — feasible
**Question.** Does the effect of prenatal smoking on the risk of sudden unexpected infant death vary by postconceptional age?

| Element | Specification |
|---|---|
| Outcome | `cdc:UCOD` — Underlying cause of death (ICD-10 codes R95 for SIDS, R99 for unspecified, W75 for accidental suffocation) |
| Exposures | `cdc:CIG_REC` |
| Covariates |  |
| Interactions |  |
| Stratification |  |
| Offset | — |
| Time scale | `cdc:AGED` |
| Design | cohort |
| Model class | cox_proportional_hazards |

Rationale: A cohort study design is appropriate to follow individuals from pregnancy through the first year of life, capturing prenatal smoking status and timing of sudden unexpected infant death. The Cox proportional hazards model allows for time-to-event analysis, which is suitable for assessing how risk changes over postconceptional age.

Expected direction: The effect of prenatal smoking on the risk of sudden unexpected infant death should vary across different intervals of postconceptional age. For example, there might be a stronger association at earlier ages compared to later ages or vice versa, depending on developmental vulnerabilities and exposure timing effects during pregnancy and early infancy.

Variable resolution:
- `cdc:UCOD` — OK: Underlying cause of death ICD-10 ICDF R95=SIDS R99=UNSPECIFIED W75=ACCIDENTAL SUFFOCATION (p.1)
- `cdc:CIG_REC` — OK: Cigarette smoking during pregnancy (p.1)
- `cdc:AGED` — OK: Age at death in days NUMF 0-364=DAYS (p.1)
Caveats:
- The variable `UCOD` is documented as having levels 'R95=SIDS', 'R99=UNSPECIFIED', and 'W75=ACCIDENTAL SUFFOCATION'. However, the research strategy specifies that only ICD-10 codes R95 (SIDS), R99 (unspecified), and W75 (accidental suffocation) are used to define the outcome. The documentation does not explicitly confirm if these are the only categories included or if there could be other unspecified causes of death coded differently.

- The variable `CIG_REC` is documented with levels '.B=DK/BLANK', '1=YES', and '2=NO'. This suggests that individuals who did not report smoking status (e.g., due to missing data) are categorized as 'DK/BLANK' which could introduce bias if these cases are numerous.

- The variable `AGED` is documented as a continuous variable representing age at death in days. However, the research strategy does not specify how postconceptional age will be calculated or derived from pregnancy start date and birth date, which may require additional data linkage or assumptions.

Not assessed by MMF: statistical power; causal validity / confounding adequacy; actual missingness rates (documentation only; no row-level data read).
### S2 (for G2) — BLOCKED
**Question.** Does the sleep environment modify the risk of sudden unexpected infant death (SUID) for male infants after reaching 44 weeks postconceptional age?

| Element | Specification |
|---|---|
| Outcome | `cdc:UCOD` — Underlying cause of death classified as Sudden Infant Death Syndrome (ICD-10: R95), Unspecified Cause of Death (R99), or Accidental Suffocation and Strangulation in Bed (W75) |
| Exposures | `cdc:SEX` |
| Covariates |  |
| Interactions |  |
| Stratification |  |
| Offset | — |
| Time scale | `cdc:AGED` |
| Design | cohort |
| Model class | cox_proportional_hazards |

Rationale: A cohort study design is appropriate to follow male infants over time and assess the risk of SUID. The Cox proportional hazards model allows for the inclusion of time-varying covariates (such as sleep environment if it were available) and can handle censored data, which is common in survival analysis.

Expected direction: The risk of SUID should be higher for male infants after reaching 44 weeks postconceptional age compared to before this age. The inclusion of sleep environment data would help determine if and how it modifies this risk pattern, but the current dataset does not capture this information, limiting our ability to draw definitive conclusions about its influence.

Variable resolution:
- `cdc:UCOD` — OK: Underlying cause of death ICD-10 ICDF R95=SIDS R99=UNSPECIFIED W75=ACCIDENTAL SUFFOCATION (p.1)
- `cdc:SEX` — OK: Sex of infant (p.1)
- `cdc:AGED` — OK: Age at death in days NUMF 0-364=DAYS (p.1)
Blockers:
- The strategy mentions that sleep environment data is needed but not available in the dataset. This makes it impossible to assess how the sleep environment modifies the risk of SUID for male infants as stated.

Caveats:
- The variable `UCOD` is defined in terms of ICD-10 codes (R95, R99, W75) but does not specify if these are the only possible values or if other causes of death could be included. This may lead to potential misclassification if deaths classified under other ICD-10 codes are present.

- The variable `SEX` is documented as a categorical variable with levels 1 (MALE) and 2 (FEMALE). However, the strategy focuses on male infants only, which means that female data will be excluded. This could introduce bias if there are differences in how SUID outcomes are recorded or classified for males versus females.

- The variable `AGED` is documented as age at death in days but does not specify whether it captures all relevant time points from birth to the outcome of interest (44 weeks postconceptional age). If data collection starts after 44 weeks, this could introduce selection bias or missingness issues.

Not assessed by MMF: statistical power; causal validity / confounding adequacy; actual missingness rates (documentation only; no row-level data read).
