# MMF strategy report — run `smoke_20261111T230918`

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
### G1. The effect of prenatal smoking on the risk of sudden unexpected infant death may vary by postconceptional age.
- Rationale: While the manuscript found that prenatal smoking was associated with an earlier onset of risk for sudden unexpected infant death, it did not explore whether this association varies at different developmental stages (postconceptional ages).
- Prior art: The manuscript established a link between prenatal smoking and earlier risk onset but did not investigate how this relationship changes over postconceptional age. This gap remains open as the study lacks an analysis of interaction effects by developmental timing.
- Supporting claims: mini_manuscript.C3
- Required variables: `cdc:CIG_REC`, `cdc:COMBGEST`, `cdc:UCOD`
### G2. The risk of sudden unexpected infant death may differ between male and female infants at various postconceptional ages.
- Rationale: Although the manuscript reported that male excess risk emerged after 44 weeks postconceptional age, it did not explore whether this pattern holds true for other developmental stages or if there are differences in risk patterns before this point.
- Prior art: The study identified a male-specific excess risk emerging at 44 weeks postconceptional age but did not examine the risk dynamics across different ages. This gap remains open as the manuscript does not provide an analysis of sex-specific risks over varying developmental stages.
- Supporting claims: mini_manuscript.C2
- Required variables: `cdc:SEX`, `cdc:COMBGEST`, `cdc:UCOD`

## D. Strategies and E. feasibility
### S1 (for G1) — feasible
**Question.** Does the effect of prenatal smoking on the risk of sudden unexpected infant death vary by postconceptional age?

| Element | Specification |
|---|---|
| Outcome | `cdc:UCOD` — Risk of sudden unexpected infant death (ICD-10 codes R95, R99, W75) |
| Exposures | `cdc:CIG_REC` |
| Covariates | `cdc:COMBGEST`, `cdc:SEX` |
| Interactions | `CIG_REC` × `COMBGEST` |
| Stratification |  |
| Offset | — |
| Time scale | `cdc:AGED` |
| Design | cohort |
| Model class | cox_proportional_hazards |

Rationale: A cohort study design is appropriate to follow individuals from pregnancy through the first year of life, capturing prenatal smoking status and postconceptional age. The Cox proportional hazards model allows for time-to-event analysis, enabling us to assess how the risk of sudden unexpected infant death changes over time in relation to prenatal smoking exposure. Interaction terms between prenatal smoking and postconceptional age will help determine if the effect varies by developmental stage.

Expected direction: The interaction term should show a significant change in hazard ratios at different stages of postconceptional age, indicating that the risk associated with prenatal smoking is not constant over time but rather increases or decreases as the infant develops. This would support the hypothesis that the timing of exposure (postconceptional age) modifies the effect of prenatal smoking on sudden unexpected infant death risk.

Variable resolution:
- `cdc:UCOD` — OK: Underlying cause of death ICD-10 ICDF R95=SIDS R99=UNSPECIFIED W75=ACCIDENTAL SUFFOCATION (p.1)
- `cdc:CIG_REC` — OK: Cigarette smoking during pregnancy (p.1)
- `cdc:COMBGEST` — OK: Combined gestation in weeks GESTF 17-47=WEEKS (p.1)
- `cdc:SEX` — OK: Sex of infant (p.1)
- `cdc:AGED` — OK: Age at death in days NUMF 0-364=DAYS (p.1)
Caveats:
- The variable `UCOD` is documented as having levels 'R95=SIDS', 'R99=UNSPECIFIED', and 'W75=ACCIDENTAL SUFFOCATION'. However, the research question specifies sudden unexpected infant death (SUID) which may include additional ICD-10 codes not listed here. This could lead to underreporting of cases if other relevant codes are missing.

- The variable `CIG_REC` is documented with levels '.B=DK/BLANK', '1=NO', and '2=YES'. The documentation does not specify how partial smoking (e.g., 1 cigarette per day) or varying degrees of smoking intensity during pregnancy are recorded. This could introduce measurement error if the exposure level is misclassified.

- The variable `COMBGEST` is documented as having a single level '99=UNKNOWN', which suggests that gestational age data may be frequently missing, leading to potential bias in stratifying by postconceptional age.

- The variable `AGED` (age at death) is continuous and measured in days. However, the research question requires analysis of prenatal smoking effects over postconceptional age, which would require linking this variable with gestational age data from pregnancy records. This linkage may not be feasible if these datasets are not integrated.

- The documentation does not specify year coverage for any variables, making it unclear whether the dataset spans a sufficient period to capture a representative sample of cases and controls.

Not assessed by MMF: statistical power; causal validity / confounding adequacy; actual missingness rates (documentation only; no row-level data read).
### S2 (for G2) — feasible
**Question.** Does the risk of sudden unexpected infant death differ between male and female infants at various postconceptional ages?

| Element | Specification |
|---|---|
| Outcome | `cdc:UCOD` — Underlying cause of death (ICD-10 codes R95 for SIDS, R99 for unspecified, W75 for accidental suffocation) |
| Exposures | `cdc:SEX` |
| Covariates | `cdc:COMBGEST` |
| Interactions | `SEX` × `COMBGEST` |
| Stratification |  |
| Offset | — |
| Time scale | `cdc:COMBGEST` |
| Design | cohort |
| Model class | cox_proportional_hazards |

Rationale: A cohort study design is appropriate to follow infants forward in time and assess the risk of sudden unexpected infant death. The Cox proportional hazards model allows for the inclusion of a continuous variable (postconceptional age) as the time scale, enabling an analysis of how sex-specific risks evolve over developmental stages. This approach does not establish causality or provide power estimates.

Expected direction: The model should reveal if male infants have higher risk than female infants at different postconceptional ages, particularly focusing on whether a significant excess risk emerges after 44 weeks as previously noted.

Variable resolution:
- `cdc:UCOD` — OK: Underlying cause of death ICD-10 ICDF R95=SIDS R99=UNSPECIFIED W75=ACCIDENTAL SUFFOCATION (p.1)
- `cdc:SEX` — OK: Sex of infant (p.1)
- `cdc:COMBGEST` — OK: Combined gestation in weeks GESTF 17-47=WEEKS (p.1)
Caveats:
- The variable `UCOD` is documented as having a level 'R99 = UNSPECIFIED', which may include deaths that are not due to sudden unexpected infant death. This could introduce misclassification and affect the outcome definition.

- The variable `COMBGEST` includes an unknown category ('99=UNKNOWN') for gestational age, which might lead to missing data issues if a significant proportion of cases fall into this category.

- The linkage between variables such as `UCOD`, `SEX`, and `COMBGEST` is not explicitly documented. Ensuring accurate linkage across these variables is crucial but may be challenging without clear documentation.

Not assessed by MMF: statistical power; causal validity / confounding adequacy; actual missingness rates (documentation only; no row-level data read).
