# MMF strategy report — run `smoke_20261026T220417`

Backend `ollama`, model `qwen2.5:14b` (digest `7cdf5a0187d5`), seed 0, temperature 0.0, MMF 0.1.0.dev0.
LLM calls: 8; total attempts: 8.

> MMF proposes; the investigator decides. This report does not assess statistical power or causal validity and no row-level data were read.

## Inputs
| Role | File | sha256 |
|---|---|---|
| codebook | tests/fixtures/mini_codebook.txt | `77ba5a0e65da8475` |
| manuscript | tests/fixtures/mini_manuscript.md | `93c9a343932cf038` |

## A. Manuscripts
### Developmental timing of sudden unexpected infant death (`mini_manuscript`)
Designs: —. Models: —. Data: —.

Research questions:
Claims (2):
- **mini_manuscript.C1** [finding] Male excess risk emerged only after 44 weeks postconceptional age. — p.None: "Male excess risk emerged only after 44 weeks postconceptional age."

- **mini_manuscript.C2** [finding] Prenatal smoking was associated with earlier onset of risk. — p.None: "Prenatal smoking was associated with earlier onset of risk."


## B. Data sources and concept map
- `cdc`: Mini codebook (fixture) — 6 documented variables.


| Concept | Source | Variable | Compatibility | Rationale |
|---|---|---|---|---|
| Age at death | cdc | AGED | direct | The variable AGED directly measures the age at death in days, which is compatible with the concept of age at death. |
| Cigarette smoking during pregnancy | cdc | CIG_REC | direct | The variable CIG_REC directly measures cigarette smoking during pregnancy, which is compatible with the concept. |
| Gestational age at birth | cdc | COMBGEST | direct | The variable COMBGEST directly measures combined gestation in weeks, which is compatible with the concept of gestational age. |
| Mother's age at birth | cdc | MAGER9 | direct | The variable MAGER9 directly measures mother's age recode, which is compatible with the concept of mother's age. |
| Sex of infant | cdc | SEX | direct | The variable SEX directly measures the sex of the infant, which is compatible with the concept. |
| Cause of death | cdc | UCOD | direct | The variable UCOD directly measures the underlying cause of death using ICD-10 codes, which is compatible with the concept. |

## C. Knowledge gaps
### G1. The effect of prenatal smoking on the timing of sudden unexpected infant death risk may differ based on maternal age.
- Rationale: While the manuscript establishes that prenatal smoking is associated with an earlier onset of SUID risk, it does not explore how this association might vary by maternal age. This gap extends the framework set forth in the manuscript to consider potential effect modification by a demographic variable (maternal age).
- Prior art: The manuscript tested and found that prenatal smoking was associated with earlier onset of risk (mini_manuscript.C2), but it did not investigate how this association might vary based on maternal age. This gap seeks to understand if the timing of SUID risk due to prenatal smoking differs across different maternal age groups.
- Supporting claims: mini_manuscript.C2
- Required variables: `cdc:CIG_REC`, `cdc:MAGER9`
### G2. The interaction between sex of the infant and gestational age at birth on sudden unexpected infant death risk may vary based on prenatal smoking status.
- Rationale: This gap extends the manuscript's findings by exploring an interaction effect that was not tested. The manuscript found a male excess risk emerging after 44 weeks postconceptional age (mini_manuscript.C1) and an earlier onset of risk associated with prenatal smoking (mini_manuscript.C2). This gap seeks to understand if these effects interact in the presence or absence of prenatal smoking.
- Prior art: The manuscript tested that male excess risk emerged only after 44 weeks postconceptional age (mini_manuscript.C1) and that prenatal smoking was associated with earlier onset of risk (mini_manuscript.C2). However, it did not test the interaction between these factors. This gap aims to explore whether the timing and magnitude of SUID risk differ based on both sex and gestational age in relation to prenatal smoking status.
- Supporting claims: mini_manuscript.C1, mini_manuscript.C2
- Required variables: `cdc:SEX`, `cdc:COMBGEST`, `cdc:CIG_REC`

## D. Strategies and E. feasibility
### S1 (for G1) — feasible
**Question.** Does the effect of prenatal smoking on the timing of sudden unexpected infant death (SUID) risk differ based on maternal age?

| Element | Specification |
|---|---|
| Outcome | `cdc:UCOD` — Underlying cause of death as Sudden Unexpected Infant Death (ICD-10 codes R95, R99, W75) |
| Exposures | `cdc:CIG_REC` |
| Covariates |  |
| Interactions | `CIG_REC` × `MAGER9` |
| Stratification |  |
| Offset | — |
| Time scale | `cdc:AGED` |
| Design | cohort |
| Model class | cox_proportional_hazards |

Rationale: The study design is a cohort because it follows individuals forward in time from pregnancy to the occurrence of SUID. The model class chosen is cox proportional hazards, which allows for the analysis of time-to-event data and can incorporate interaction terms to assess effect modification by maternal age.

Expected direction: The strategy aims to determine if the timing of SUID risk due to prenatal smoking differs across maternal age groups. It does not establish causality or power for detecting effect modification by maternal age, which would require additional analyses and sample size calculations.

Variable resolution:
- `cdc:UCOD` — OK: Underlying cause of death ICD-10 ICDF R95=SIDS R99=UNSPECIFIED W75=ACCIDENTAL SUFFOCATION (p.1)
- `cdc:CIG_REC` — OK: Cigarette smoking during pregnancy (p.1)
- `cdc:MAGER9` — OK: Mother's age recode 9 (p.1)
- `cdc:AGED` — OK: Age at death in days NUMF 0-364=DAYS (p.1)
Caveats:
- The variable `UCOD` is defined with ICD-10 codes R95, R99, and W75. However, the documentation does not specify if these codes are mutually exclusive or if they can overlap in a single record, which could lead to misclassification of SUID.

- The variable `CIG_REC` has levels `.B=DK/BLANK`, `1=YES`, and `2=NO`. The presence of `.B=DK/BLANK` suggests that there may be missing or unknown smoking status data for some pregnancies, which could introduce bias if not properly addressed in the analysis.

- The variable `MAGER9` is recoded into three categories (under 15, 15-19, and 20-24). This limited categorization might not capture the full range of maternal ages, potentially leading to loss of information or misclassification if there are significant differences in SUID risk among other age groups.

- The variable `AGED` is continuous but documented as a numeric format with values from 0 to 364 days. The precision and accuracy of this variable could be affected by data entry errors, particularly for very young infants where the exact day of death might not always be recorded accurately.

Not assessed by MMF: statistical power; causal validity / confounding adequacy; actual missingness rates (documentation only; no row-level data read).
### S2 (for G2) — feasible
**Question.** Does the interaction between sex of the infant and gestational age at birth on sudden unexpected infant death risk vary based on prenatal smoking status?

| Element | Specification |
|---|---|
| Outcome | `cdc:UCOD` — Sudden Unexpected Infant Death (SUID) as defined by underlying cause of death codes. |
| Exposures | `cdc:SEX`, `cdc:COMBGEST`, `cdc:CIG_REC` |
| Covariates |  |
| Interactions | `SEX` × `COMBGEST` × `CIG_REC` |
| Stratification |  |
| Offset | — |
| Time scale | — |
| Design | cohort |
| Model class | logistic_regression |

Rationale: A cohort study design is appropriate to follow infants from birth through the outcome of interest (SUID). Logistic regression allows for the estimation of odds ratios and interaction terms between sex, gestational age at birth, and prenatal smoking status. This model class can handle binary outcomes and interactions.

Expected direction: The interaction term between sex, gestational age at birth, and prenatal smoking status is expected to show a significant effect if the risk patterns differ based on these factors. For example, male infants may have an increased risk of SUID after 44 weeks postconceptional age only in the absence of prenatal smoking, while this risk might be present earlier or modified by smoking status.

Variable resolution:
- `cdc:UCOD` — OK: Underlying cause of death ICD-10 ICDF R95=SIDS R99=UNSPECIFIED W75=ACCIDENTAL SUFFOCATION (p.1)
- `cdc:SEX` — OK: Sex of infant (p.1)
- `cdc:COMBGEST` — OK: Combined gestation in weeks GESTF 17-47=WEEKS (p.1)
- `cdc:CIG_REC` — OK: Cigarette smoking during pregnancy (p.1)
Caveats:
- The variable `UCOD` (Underlying cause of death) includes codes for SIDS, unspecified causes, and accidental suffocation. This may introduce misclassification issues since the outcome is specifically defined as Sudden Unexpected Infant Death (SUID), which might not fully align with these ICD-10 codes.

- The variable `COMBGEST` (Combined gestation in weeks) has a level of '99=UNKNOWN', indicating that there will be missing data for gestational age, which could affect the analysis if this is prevalent.

- The variable `CIG_REC` (Cigarette smoking during pregnancy) includes levels '.B=DK/BLANK' and '1=YES'. The presence of 'DK/BLANK' suggests potential non-response or missingness in reporting prenatal smoking status.

Not assessed by MMF: statistical power; causal validity / confounding adequacy; actual missingness rates (documentation only; no row-level data read).
