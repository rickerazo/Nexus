# MMF strategy report — run `smoke_20261111T234238`

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
### S1 (for G1) — feasible
**Question.** Does male sex alone, without prenatal smoking exposure, increase the risk of sudden unexpected infant death after reaching 44 weeks postconceptional age?

| Element | Specification |
|---|---|
| Outcome | `cdc:UCOD` — Underlying cause of death (ICD-10 codes R95 for SIDS, R99 for unspecified, and W75 for accidental suffocation) |
| Exposures | `cdc:SEX` |
| Covariates | `cdc:COMBGEST`, `cdc:CIG_REC` |
| Interactions | `SEX` × `COMBGEST` |
| Stratification | `cdc:CIG_REC` |
| Offset | — |
| Denominator | — |
| Time scale | `cdc:COMBGEST` |
| Design | cohort |
| Model class | cox_proportional_hazards |

Rationale: This study design follows a cohort of infants forward in time, examining the risk of sudden unexpected infant death (UCOD) after reaching 44 weeks postconceptional age. The inclusion of COMBGEST as both an exposure and time scale allows for the analysis to focus on the timing relative to this critical period. CIG_REC is included as a stratification variable to isolate the effect of sex in the absence of prenatal smoking exposure. This model class (cox_proportional_hazards) is appropriate because it can handle time-to-event data, allowing us to assess whether male infants have an increased risk after 44 weeks postconceptional age without considering prenatal smoking.

Expected direction: The hypothesis predicts that the hazard ratio for sudden unexpected infant death will be higher in males compared to females after reaching 44 weeks postconceptional age when stratified by no prenatal smoking exposure. This would support the gap statement, indicating an excess risk specific to male sex beyond the influence of prenatal smoking.

Variable resolution:
- `cdc:UCOD` — OK: Underlying cause of death ICD-10 ICDF R95=SIDS R99=UNSPECIFIED W75=ACCIDENTAL SUFFOCATION (p.1)
- `cdc:SEX` — OK: Sex of infant (p.1)
- `cdc:COMBGEST` — OK: Combined gestation in weeks GESTF 17-47=WEEKS (p.1)
- `cdc:CIG_REC` — OK: Cigarette smoking during pregnancy (p.1)
Caveats:
- The variable `COMBGEST` is documented as having a level of '99=UNKNOWN', which may introduce missingness in the data. This could affect the analysis if there are many unknown gestational weeks, especially around the critical period of 44 weeks postconceptional age.

- The variable `CIG_REC` has levels `.B=DK/BLANK`, indicating that some records might be marked as 'Don't Know' or 'Blank'. This could introduce missingness and affect stratification by prenatal smoking exposure.

- The documentation does not specify the exact years covered by the data source (cdc). Without this information, it is unclear if the dataset includes a sufficient time period to capture the outcome of interest after 44 weeks postconceptional age.

Not assessed by MMF: statistical power; causal validity / confounding adequacy; actual missingness rates (documentation only; no row-level data read).
### S2 (for G2) — BLOCKED
**Question.** Is the earlier onset of risk for sudden unexpected infant death associated with prenatal smoking exposure consistent across different postconceptional age intervals?

| Element | Specification |
|---|---|
| Outcome | `cdc:UCOD` — Underlying cause of death (ICD-10 codes R95, R99, W75) |
| Exposures | `cdc:CIG_REC` |
| Covariates | `cdc:COMBGEST`, `cdc:AGED`, `cdc:SEX` |
| Interactions | `CIG_REC` × `COMBGEST` |
| Stratification | `cdc:COMBGEST` |
| Offset | — |
| Denominator | — |
| Time scale | `cdc:AGED` |
| Design | cohort |
| Model class | cox_proportional_hazards |

Rationale: This study design follows a cohort of infants forward in time to assess the timing of risk onset associated with prenatal smoking exposure. The Cox proportional hazards model is chosen because it allows for the analysis of time-to-event data, enabling us to examine how postconceptional age intervals affect the risk of sudden unexpected infant death. However, this strategy does not establish causality or provide information on statistical power.

Expected direction: The expected pattern would be that infants with prenatal smoking exposure have a higher hazard rate for sudden unexpected infant death at earlier postconceptional ages compared to those without such exposure.

Variable resolution:
- `cdc:UCOD` — OK: Underlying cause of death ICD-10 ICDF R95=SIDS R99=UNSPECIFIED W75=ACCIDENTAL SUFFOCATION (p.1)
- `cdc:CIG_REC` — OK: Cigarette smoking during pregnancy (p.1)
- `cdc:COMBGEST` — OK: Combined gestation in weeks GESTF 17-47=WEEKS (p.1)
- `cdc:AGED` — OK: Age at death in days NUMF 0-364=DAYS (p.1)
- `cdc:SEX` — OK: Sex of infant (p.1)
Blockers:
- There is no explicit mention of whether the data source includes information on postconceptional age intervals. This makes it impossible to stratify and analyze risk onset across different postconceptional age intervals as required by the research strategy.

Caveats:
- The variable `UCOD` (Underlying cause of death) is documented with levels R95, R99, and W75. However, the documentation does not specify whether these codes are mutually exclusive or if an infant can have multiple underlying causes of death. This ambiguity could affect the interpretation of the outcome.

- The variable `CIG_REC` (Cigarette smoking during pregnancy) is documented with levels .B=DK/BLANK, 1=NO, and 2=YES. The level .B=DK/BLANK indicates missing or unknown data, which may introduce bias if not properly accounted for in the analysis.

- The variable `COMBGEST` (Combined gestation in weeks) is documented with a single level of 99 indicating UNKNOWN. This could lead to issues with stratification and interaction analyses as it introduces likely missingness that needs careful handling.

- The variable `AGED` (Age at death in days) is continuous but the documentation does not specify how postconceptional age intervals are defined or derived from this variable, which is crucial for the research question.

Not assessed by MMF: statistical power; causal validity / confounding adequacy; actual missingness rates (documentation only; no row-level data read).
