# Epic Cosmos: public intelligence (stub)

**Status:** this is a placeholder compiled from public pages, accessed 2026-11-10. It is **not a codebook** and is
deliberately kept out of `codebooks:` in `configs/suid.yaml`, so Component B never maps concepts onto variable names
nobody has seen. Replace it with the real Cosmos Data Dictionary export (see "Next step") before Cosmos enters a run.

## What Cosmos is
- De-identified EHR data pooled from Epic customer organizations. Per Epic Research (Sep 2025): "more than 300
  million patient records from 1,700 hospitals and more than 40,000 clinics from all 50 U.S. states, Lebanon, and
  Saudi Arabia" [SP]. An earlier article (Nov 2023) reported 220 million records from 1,272 hospitals [N], so always
  cite counts with their date.
- Described as a "coded limited data set" [O] with no direct identifiers. "Dates are shifted per patient; ages may
  be truncated (all birthdays set to Jan 1)" [S]. **For infant work this matters:** age in days at death may not
  be computable from truncated birth dates. Confirm in the dictionary.
- "Continuously updated" [O].

## Data dictionary (what is known publicly)
- Opened through the book icon inside the Cosmos portal [D]. Each table entry shows availability (SlicerDicer,
  DSVM or both), data quality and completeness, and a description [D].
- The only table name published on these pages is `EncounterFact` [D]. No death, birth or mother–baby table names
  are public.
- Stanford also points to the "Cosmos Data Science White Papers and Data Encyclopedia" for limitations [S].

## Domains listed publicly
Demographics, diagnoses, encounters and admissions, labs (component results), microbiology, medications,
procedures, vitals, infections, social history, Social Vulnerability Index, ED diagnosis and disposition,
**Birth History** and **OB History** [O, S]. Claims data is listed as planned [O].

Fields used by published infant studies:
- Delivery method, gestational age and birth weight define the birth cohort [SP].
- Maternal hypertension, gestational diabetes, maternal age, drug use, infections, autoimmune conditions,
  marital status, SVI and ADI appear as covariates [N].

## SUID-relevant limits
- **Death is all-cause.** The outcome is "documented date of death in Cosmos within one year of birth," and
  Epic Research states "We were unable to study the specific cause of death" [SP]. The source of the death date
  (EHR, or a linked death index) is not stated.
- **No public cause-of-death field.** A SUID definition would have to be built from diagnosis codes recorded at
  the terminal encounter. The CDC SUID categories (ICD-10 R95 SIDS, R99 unknown cause, W75 accidental suffocation
  and strangulation in bed) are death-certificate codes; whether Cosmos holds them for infant deaths is unknown.
  This is our inference, not a Cosmos statement.
- **Mother–infant linkage:** Birth and OB History exist [O], and studies use maternal covariates [N, SP], but the
  linkage mechanism is not described publicly.
- Geography finer than national (state, county, ZIP) is not stated. Small counts (<11) must be masked [S].

## Access
- Aggregate: SlicerDicer in the Cosmos portal, for cohort discovery and feasibility [S].
- Line-level (DSVM): SQL requires COS305 + COS500 (about $800); R/Python requires COS305 + COS550 (about $400).
  Courses are sequential and virtual [S]. Exports come as SQL tables, CSV or parquet [S].
- Publications must acknowledge Cosmos, and citations are reported to the Governing Council [S]. Institutional
  eligibility rules vary; the Stanford page applies to Stanford [S]. Seattle Children's access is to be confirmed.

## Open questions for the real dictionary
1. Which table and column hold death date, and what is their source and completeness for infants?
2. Is there any cause-of-death or death-certificate ICD-10 field?
3. How are infants linked to mothers (Birth History / OB History), and with what completeness?
4. Birth date granularity for infants (the Jan-1 truncation), and how age at death in days is obtained.
5. Gestational age and birth weight fields, and units.
6. Sleep environment, bed-sharing, smoking and breastfeeding: anything beyond social history and free text?
7. Geography: state, county, ZIP or SVI only?

## Next step
Export the Cosmos Data Dictionary from the portal (CSV or Excel preferred) into `data/documentation/`. Then check
how `pass1_table` parses `Table.Column` names, adding a Cosmos branch with a `PARSER_VERSION` bump if needed, and
add an `epic_cosmos` entry to `configs/suid.yaml`. Adding a source re-runs B in full (about 4–5 h).

## Sources (accessed 2026-11-10)
- [D] Dartmouth Synergy, "Using the Cosmos Data Dictionary": https://synergy.dartmouth.edu/services/data-informatics/cosmos/additional-tips/
- [S] Stanford STARR, Cosmos onboarding guide: https://med.stanford.edu/starr-tools/other-resources/cosmos/onboarding-guide.html
- [E] Epic Research, About our data: https://www.epicresearch.org/about-our-data/
- [N] Epic Research (2023-11-30), NICU admission and neonatal mortality: https://www.epicresearch.org/articles/increased-risk-of-nicu-admission-and-neonatal-mortality-associated-with-maternal-comorbidities-race-and-age/
- [SP] Epic Research (2025-09-04), Sepsis in infants: https://www.epicresearch.org/articles/sepsis-in-infants-less-common-more-deadly
- [O] Ohio State Secondary Data Core, Epic Cosmos: https://u.osu.edu/secondarydatacore/?p=296
