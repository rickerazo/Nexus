# MMF strategy report — run `smoke_20261111T232412`

Backend `ollama`, model `qwen2.5:14b` (digest `7cdf5a0187d5`), seed 0, temperature 0.0, MMF 0.1.0.dev0.
LLM calls: 9; total attempts: 11.
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
### G1. The impact of prenatal smoking on sudden unexpected infant death risk should be further investigated for infants with different postconceptional ages.
- Rationale: Mini manuscript C3 suggests that prenatal smoking is associated with an earlier onset of the risk for sudden unexpected infant death. However, it does not specify how this association varies across different developmental stages (postconceptional age).
- Prior art: The mini manuscript tested the general association between prenatal smoking and the timing of sudden unexpected infant death but did not stratify by postconceptional age.
- Supporting claims: mini_manuscript.C3
- Required variables: `cdc:CIG_REC`, `cdc:COMBGEST`
### G2. The developmental timing of male excess risk for sudden unexpected infant death should be further explored in relation to postconceptional age.
- Rationale: Mini manuscript C2 indicates that male infants show an excess risk after reaching 44 weeks postconceptional age. However, the study does not provide a detailed analysis of how this risk changes with different developmental stages before and after 44 weeks.
- Prior art: The mini manuscript identified a male excess risk emerging only after 44 weeks postconceptional age but did not explore the timing in detail for earlier or later periods.
- Supporting claims: mini_manuscript.C2
- Required variables: `cdc:SEX`, `cdc:COMBGEST`

## D. Strategies and E. feasibility
### S1 (for G1) — feasible
**Question.** How does the impact of prenatal smoking on sudden unexpected infant death risk vary across different postconceptional ages?

| Element | Specification |
|---|---|
| Outcome | `cdc:UCOD` — Underlying cause of death (SIDS, unspecified, accidental suffocation) |
| Exposures | `cdc:CIG_REC` |
| Covariates | `cdc:COMBGEST`, `cdc:AGED`, `cdc:SEX` |
| Interactions | `CIG_REC` × `COMBGEST` |
| Stratification |  |
| Offset | — |
| Time scale | `cdc:AGED` |
| Design | cohort |
| Model class | cox_proportional_hazards |

Rationale: A cohort study design with a Cox proportional hazards model is appropriate to assess the timing of sudden unexpected infant death risk in relation to prenatal smoking, stratified by postconceptional age. This approach allows for the examination of how the hazard ratio associated with prenatal smoking changes over time (postconceptional age). The interaction term between prenatal smoking and postconceptional age will help determine if the effect of prenatal smoking varies across different developmental stages.

Expected direction: The model should show a significant interaction term indicating that the risk associated with prenatal smoking is higher at certain postconceptional ages compared to others, supporting or refuting the hypothesis that the impact of prenatal smoking on sudden unexpected infant death risk changes over time.

Variable resolution:
- `cdc:UCOD` — OK: Underlying cause of death ICD-10 ICDF R95=SIDS R99=UNSPECIFIED W75=ACCIDENTAL SUFFOCATION (p.1)
- `cdc:CIG_REC` — OK: Cigarette smoking during pregnancy (p.1)
- `cdc:COMBGEST` — OK: Combined gestation in weeks GESTF 17-47=WEEKS (p.1)
- `cdc:AGED` — OK: Age at death in days NUMF 0-364=DAYS (p.1)
- `cdc:SEX` — OK: Sex of infant (p.1)
Caveats:
- The variable `UCOD` (Underlying cause of death) is documented as categorical with levels 'R95 = SIDS', 'R99 = UNSPECIFIED', and 'W75 = ACCIDENTAL SUFFOCATION'. However, the documentation does not specify if these codes are mutually exclusive or if a single death can be classified under multiple categories. This ambiguity could affect the interpretation of sudden unexpected infant death risk.

- The variable `CIG_REC` (Cigarette smoking during pregnancy) is documented as having levels '.B=DK/BLANK', '1=NO', and '2=YES'. The level '.B=DK/BLANK' indicates missing or unknown data, which could introduce bias if not properly accounted for in the analysis.

- The variable `COMBGEST` (Combined gestation in weeks) is documented as having a single level '99=UNKNOWN', indicating that there may be substantial missingness in gestational age information. This missingness can affect the stratification by postconceptional age and introduce bias if not addressed appropriately.

- The variable `AGED` (Age at death in days) is continuous but documented as having levels '0-364 = DAYS'. The documentation does not specify how to handle ages outside this range, which could be a limitation for the analysis of postconceptional age effects.

- Linkage between prenatal smoking (`CIG_REC`) and gestational age (`COMBGEST`) is required but not explicitly documented. This linkage may introduce additional complexity in data management and potential missingness issues.

Not assessed by MMF: statistical power; causal validity / confounding adequacy; actual missingness rates (documentation only; no row-level data read).
### S2 (for G2) — feasible
**Question.** How does the risk of sudden unexpected infant death (SUID) for male infants change with postconceptional age, particularly before and after 44 weeks?

| Element | Specification |
|---|---|
| Outcome | `cdc:UCOD` — Underlying cause of death classified as Sudden Infant Death Syndrome (ICD-10: R95), Unspecified (R99), or Accidental Suffocation and Strangulation in Bed (W75) |
| Exposures | `cdc:SEX` |
| Covariates | `cdc:COMBGEST` |
| Interactions | `SEX` × `COMBGEST` |
| Stratification |  |
| Offset | — |
| Time scale | `cdc:COMBGEST` |
| Design | cohort |
| Model class | cox_proportional_hazards |

Rationale: A cohort study design with Cox proportional hazards modeling is appropriate to assess the timing of male excess risk for SUID in relation to postconceptional age. This model allows us to examine how the hazard ratio for males changes over time, specifically before and after 44 weeks postconceptional age. The interaction term between sex and postconceptional age will help determine if there is a significant change in risk at different developmental stages.

Expected direction: The analysis should reveal an increasing or decreasing trend in the hazard ratio for males as they progress through different postconceptional age intervals, particularly highlighting any changes around 44 weeks. This would support or refute the hypothesis that male excess risk emerges after reaching this milestone and how it evolves before and after this point in development.

Variable resolution:
- `cdc:UCOD` — OK: Underlying cause of death ICD-10 ICDF R95=SIDS R99=UNSPECIFIED W75=ACCIDENTAL SUFFOCATION (p.1)
- `cdc:SEX` — OK: Sex of infant (p.1)
- `cdc:COMBGEST` — OK: Combined gestation in weeks GESTF 17-47=WEEKS (p.1)
Caveats:
- The variable `UCOD` is documented as having a level 'R95 = SIDS', which matches the strategy's definition of Sudden Infant Death Syndrome. However, it also includes levels for unspecified causes ('R99') and accidental suffocation ('W75'), which may introduce variability in the outcome classification that could affect the risk assessment.

- The variable `COMBGEST` is documented as having a level '99=UNKNOWN', indicating likely missingness or unknown gestational age. This missing data can impact the accuracy of postconceptional age calculations and thus the timing analysis specified in the research question.

- The linkage between `SEX`, `UCOD`, and `COMBGEST` variables is required to ensure that all necessary information for each infant death record is available, which may introduce additional complexity or missing data issues if not fully linked.

Not assessed by MMF: statistical power; causal validity / confounding adequacy; actual missingness rates (documentation only; no row-level data read).
