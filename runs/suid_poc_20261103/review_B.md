---
stage: B
approved: true
---
# Review checkpoint: Schema map (stage B)

MMF proposed the structured output below. Review it, edit `B_*.json` in this run directory
if anything is wrong, then set `approved: true` above (or run `mmf approve <run_dir> B`) and
re-run `mmf run`. Downstream stages use the JSON file, not this rendering.

## Cross-check (embedding vs LLM)

An independent embedding pathway (`mxbai-embed-large`) ranked each source's variables for every concept.
It does not change the mappings; it flags where the two pathways disagree. Counts: agree 42, both_none 266, llm_outside_topk 24, possible_miss 46.

- **llm_outside_topk**: the LLM's variable is not in the embedding top 10. Possible stretch or wrong mapping.
- **possible_miss**: the LLM mapped nothing, but an embedding candidate scores at least 0.65.

| Verdict | Source | Concept (role) | LLM variable(s) | Top-3 embedding candidates |
|---|---|---|---|---|
| llm_outside_topk | cdc_codenames | Maternal smoking during pregnancy (covariate) | CIG_REC | `CIG_0` Cigarettes Before Pregnancy (0.70); `CIG_1` Cigarettes 1st Trimester (0.69); `CIG_3` Cigarettes 3rd Trimester (0.69) |
| llm_outside_topk | cdc_codenames | maternal smoking status (smoking, non-smoking) (stratifier) | CIG_REC | `CIG_1` Cigarettes 1st Trimester (0.70); `F_CIGS_1` Reporting Flag for Cigarettes 1st Trimester (0.69); `CIG_2` Cigarettes 2nd Trimester (0.69) |
| llm_outside_topk | cdc_linkco15 | Geographic location (stratifier) | MRCNTYFIPS | `RESIDENTS` Territory and County-equivalent of (0.59); `ENTITY` Entity-Axis Conditions (0.58); `RESTATUS` Residence Status (0.57) |
| llm_outside_topk | cdc_linkco15 | Maternal smoking during pregnancy (covariate) | CIG_REC | `F_CIGS_0` Reporting Flag for Cigarettes before Pregnancy (0.69); `CIG0_R` Cigarettes Before Pregnancy Recode (0.68); `CIG_0` Cigarettes Before Pregnancy (0.68) |
| llm_outside_topk | cdc_linkco15 | Postconceptional age (PCA) (covariate) | COMBGEST | `ILOP_R11` Interval of Last Other Pregnancy Recode 11 (0.65); `RF_PPB` Previous Preterm Birth (0.64); `F_RF_PPB` Reporting Flag for Previous Preterm Birth (0.63) |
| llm_outside_topk | cdc_linkco15 | SUID (outcome) | UCODR130 | `F_CA_CCHD` Reporting Flag for Cyanotic Congenital Heart Disease (0.58); `F_AB_AVEN1` Reporting Flag for Assisted Ventilation (0.58); `ILIVE` Infant Living at Time of Report (0.56) |
| llm_outside_topk | cdc_linkco15 | maternal smoking status (smoking, non-smoking) (stratifier) | CIG_REC | `CIG1_R` Cigarettes 1st Trimester Recode (0.69); `F_CIGS_1` Reporting Flag for Cigarettes 1st Trimester (0.69); `F_CIGS_2` Reporting Flag for Cigarettes 2nd Trimester (0.69) |
| llm_outside_topk | cdc_natl15 | Breastfeeding status at discharge (covariate) | BFED | `F_BFED` Reporting Flag for Breastfed at Discharge (0.69); `ILOP_R` Interval Since Last Other Pregnancy Recode 000-003 Plural delivery (0.64); `ILP_R11` Interval Since Last Pregnancy Recode 11 (0.63) |
| llm_outside_topk | cdc_natl15 | Geographic location (stratifier) | OCNTYFIPS | `F_FACILITY` Reporting Flag for Birth Place (0.57); `MRTERR` Mother’s Residence Territory (0.54); `RCITY_POP` Population of Residence City (0.54) |
| llm_outside_topk | cdc_natl15 | Infant sex (exposure) | SEX | `BWTR4` Birth Weight Recode 4 (0.63); `BWTR12` Birth Weight Recode 12 (0.61); `F_RF_PPB` Reporting Flag for Previous Preterm Birth (0.61) |
| llm_outside_topk | cdc_natl15 | Maternal infections in pregnancy (exposure) | IP_HEPC | `IP_CHLAM` Chlamydia (0.66); `F_IP_CHLAM` Reporting Flag for Chlamydia (0.66); `F_CIGS_0` Reporting Flag for Cigarettes before Pregnancy (0.63) |
| llm_outside_topk | cdc_natl15 | Maternal smoking during pregnancy (covariate) | CIG_REC | `F_CIGS_0` Reporting Flag for Cigarettes before Pregnancy (0.69); `F_CIGS_1` Reporting Flag for Cigarettes 1st Trimester (0.67); `F_CIGS_2` Reporting Flag for Cigarettes 2nd Trimester (0.67) |
| llm_outside_topk | cdc_natl15 | Postconceptional age (PCA) (covariate) | COMBGEST | `RF_PPTERM` Previous Preterm Birth (0.64); `BWTR4` Birth Weight Recode 4 (0.64); `F_RF_PPB` Reporting Flag for Previous Preterm Birth (0.63) |
| llm_outside_topk | cdc_natl15 | Preterm birth (covariate) | GESTREC3 | `RF_PPTERM` Previous Preterm Birth (0.72); `F_RF_PPB` Reporting Flag for Previous Preterm Birth (0.70); `COMBGEST` Combined Gestation – Detail in Weeks (0.65) |
| llm_outside_topk | cdc_natl15 | maternal smoking status (smoking, non-smoking) (stratifier) | CIG_REC | `F_CIGS_1` Reporting Flag for Cigarettes 1st Trimester (0.69); `F_CIGS_2` Reporting Flag for Cigarettes 2nd Trimester (0.69); `F_CIGS_0` Reporting Flag for Cigarettes before Pregnancy (0.68) |
| llm_outside_topk | ncfrp_v51 | Age of death in SUID cases (outcome) | INFdayslive | `INF372infinj` In 72 hours prior to death, infant injured (0.71); `INF72infinj` In 72 hours prior to death, infant injured (0.70); `INF372other` In 72 hours prior to death, other disorders (0.70) |
| llm_outside_topk | ncfrp_v51 | Geographic location (stratifier) | INFaddrst, INFdthstate, INCstate | `INCrelhome` Place of incident - Relative’s home (0.55); `INCpark` Place of incident - State or county park (0.54); `INF4momaddrst` Mother's residence address - State (0.53) |
| llm_outside_topk | ncfrp_v51 | Infant sex (exposure) | INFsex, RES2sex, RES1sex, INFgenderid, ACTcausex | `INFexpipv` During pregnancy did mother experience intimate partner violence (0.67); `INF3drugbirth` Infant born drug exposed (0.67); `CIR2neghazardtype` Child neglect - Exposure to hazards type (0.66) |
| llm_outside_topk | ncfrp_v51 | SUID (outcome) | INF372infectunk, INF372vacsp, INF372medothsp, INF4outcome, CAUdcimmcau, CIR2dthlovedone, CIR2hxbullyvic, CIR2hxdrugalc, CIR2hxgaming, CIR2hxjobprob, CIR2hxmnyprob, CIR2hxnewschl, CIR2hxother, CIR2hxphysabs, CIR2hxprblaw, CIR2hxpregnant, CIR2hxsexabs, CIR2hxunk, REVsuidirec, ACTcausids | `INF372infinj` In 72 hours prior to death, infant injured (0.67); `INF72infinj` In 72 hours prior to death, infant injured (0.65); `INF372other` In 72 hours prior to death, other disorders (0.64) |
| llm_outside_topk | ncfrp_v51 | Sudden unexpected infant death (SUID) (outcome) | INF372infectunk, INF372vacsp, INF372medothsp, INF4outcome, CAUdcimmcau, CIR2dthlovedone, CIR2hxbullyvic, CIR2hxdrugalc, CIR2hxgaming, CIR2hxjobprob, CIR2hxmnyprob, CIR2hxnewschl, CIR2hxother, CIR2hxphysabs, CIR2hxprblaw, CIR2hxpregnant, CIR2hxsexabs, CIR2hxunk, REVsuidirec, ACTcausids | `INF372infinj` In 72 hours prior to death, infant injured (0.75); `INF72infinj` In 72 hours prior to death, infant injured (0.74); `INF2acuteill` Was child acutely ill in the two weeks before death (0.71) |
| llm_outside_topk | ncfrp_v51 | bed sharing (exposure) | CIRsamesurf | `CIRroomshare` Child sleeping in the same room as caregiver/supervisor at time of death (0.65); `CIRsleepplcbedsp` Incident sleep place - Adult bed (0.65); `CIRblnktobair` Object(s) in sleeping area - Thin blanket/flat sheet - obstruct airway? (0.63) |
| llm_outside_topk | ncfrp_v51 | maternal smoking status (smoking, non-smoking) (stratifier) | INFsmanytime | `INFsectricig` If yes, smoke during pregnancy, second trimester, number cigarettes (0.71); `INF3sectricig` If yes, smoke during pregnancy, second trimester, number cigarettes (0.71); `INF3thirdtricig` If yes, smoke during pregnancy, third trimester, number cigarettes (0.71) |
| llm_outside_topk | ncfrp_v51 | sex (male, female) (stratifier) | INFsex, RES2sex, RES1sex, INFgenderid, ACTcausex | `RES1sex` Person 1 sex (0.68); `WEAothersex` Sex of person(s) handling weapon - Other weapon (0.67); `ACTconsex` Person’s sex - Contributed (0.66) |
| llm_outside_topk | ncfrp_v51 | year of birth or death (stratifier) | INFdobyear, INFdodyear | `RES1priordeath` Person 1 has prior child deaths (0.68); `CAUmanner` Official manner of death from the death certificate (0.67); `RES1dthother` If yes, Person 1 - prior deaths - Other (0.67) |
| possible_miss | cdc_codenames | Gestational age at birth (covariate) | none | `COMBGEST` Combined Gestation – Detail in Weeks (0.73); `COMPGST_IMP` Combined Gestation Imputation Flag (0.72); `OBGEST_FLG` Obstetric Estimate of Gestation Used Flag (0.69) |
| possible_miss | cdc_codenames | Maternal infections in pregnancy (exposure) | none | `IP_CHLAM` Chlamydia (0.66); `F_IP_CHLAM` Reporting Flag for Chlamydia (0.66); `CIG_0` Cigarettes Before Pregnancy (0.63) |
| possible_miss | cdc_codenames | Postconceptional age (PCA) (covariate) | none | `COMPGST_IMP` Combined Gestation Imputation Flag (0.66); `RF_PPTERM` Previous Preterm Birth (0.64); `BWTR4` Birth Weight Recode 4 (0.64) |
| possible_miss | cdc_codenames | Preterm birth (covariate) | none | `RF_PPTERM` Previous Preterm Birth (0.72); `F_RF_PPB` Reporting Flag for Previous Preterm Birth (0.70); `COMPGST_IMP` Combined Gestation Imputation Flag (0.68) |
| possible_miss | cdc_codenames | birthweight (stratifier) | none | `BWTR4` Birth Weight Recode 4 (0.72); `BWTR12` Birth Weight Recode 12 (0.71); `DBWT` Birth Weight – Detail in Grams (0.67) |
| possible_miss | cdc_codenames | chronological age (offset) | none | `DOB_TT` Time of Birth (0.65); `DOB_MM` Birth Month (0.64); `DOB_WK` Birth Day of Week (0.64) |
| possible_miss | cdc_codenames | postconceptional age (exposure) | none | `ILP_R` Interval Since Last Pregnancy Recode (0.69); `ILOP_R` Interval Since Last Other Pregnancy Recode (0.68); `ILP_R11` Interval Since Last Pregnancy Recode 11 (0.68) |
| possible_miss | cdc_codenames | sex (stratifier) | none | `SEX` Sex of Infant (0.81); `IMP_SEX` Imputed Sex (0.60); `BWTR4` Birth Weight Recode 4 (0.60) |
| possible_miss | cdc_codenames | year of birth or death (stratifier) | none | `DOB_YY` Birth Year (0.66); `DOB_TT` Time of Birth (0.66); `DOB_MM` Birth Month (0.66) |
| possible_miss | cdc_linkco15 | Age of death in SUID cases (outcome) | none | `ILLB_R11` Interval of Last Live Birth Recode 11 (0.65); `ILLB_R` Interval of Last Live Birth Recode (0.64); `PRIORDEAD` Prior Births Now Dead (0.63) |
| possible_miss | cdc_linkco15 | birthweight (stratifier) | none | `BWTR14` Birth Weight Recode 14 (0.67); `BWTIMP` Birth Weight Imputed Flag (0.66); `BWTR4` Birth Weight Recode 4 (0.66) |
| possible_miss | cdc_linkco15 | sex (stratifier) | none | `SEX` Sex of Infant (0.80); `IMP_SEX` Imputed Sex (0.67); `NO_ABNORM` No Abnormal Conditions Checked (0.62) |
| possible_miss | cdc_natl15 | Maternal prepregnancy body mass index (BMI) (exposure) | none | `F_PWGT` Reporting Flag for Pre-pregnancy Weight (0.72); `DBWT` Birth Weight – Detail in Grams (Edited) (0.70); `BMI` BMI (0.67) |
| possible_miss | cdc_natl15 | birthweight (stratifier) | none | `BWTR4` Birth Weight Recode 4 (0.72); `BWTR12` Birth Weight Recode 12 (0.71); `DBWT` Birth Weight – Detail in Grams (Edited) (0.68) |
| possible_miss | cdc_natl15 | chronological age (offset) | none | `DOB_TT` Time of Birth (0.65); `DOB_MM` Birth Month (0.64); `DOB_WK` Birth Day of Week (0.64) |
| possible_miss | ncfrp_v51 | Breastfeeding status at discharge (covariate) | none | `INFbreast` Infant ever breastfed (0.68); `INF3breast6moexc` If yes, breastfed at 6 months, exclusively? (0.67); `INF3breast3moexc` If yes, breastfed at 3 months, exclusively? (0.67) |
| possible_miss | ncfrp_v51 | Maternal infections in pregnancy (exposure) | none | `INFmedical` During pregnancy did mother have medical complications/infections (0.71); `INF3medical` During pregnancy did mother have medical complications/infections (0.69); `IEMuti` Urinary tract infections present during pregnancy? (0.69) |
| possible_miss | ncfrp_v51 | Maternal prepregnancy body mass index (BMI) (exposure) | none | `IEMprenatalBMI` Maternal prenatal BMI (0.72); `INF4mompregwt` Mother's pre-pregnancy weight - Pounds (0.72); `INF4mompregwtunk` Mother's pre-pregnancy weight - Pounds - Unknown (0.71) |
| possible_miss | ncfrp_v51 | PCA (postconceptional age) (outcome) | none | `IEMagefirstpreg` Maternal age at first pregnancy in years (0.65); `INFgestage` Gestational age in weeks (0.65); `INF3gestage` Gestational age in weeks (0.65) |
| possible_miss | ncfrp_v51 | Postconceptional age (PCA) (covariate) | none | `INF3smallgest` Previous pregnancies - Small gestational age (0.66); `INFgestunk` Gestational age in weeks - Unknown (0.64); `INFgestage` Gestational age in weeks (0.64) |
| possible_miss | ncfrp_v51 | body movement arousal response to severe hypoxia-hypercarbia (outcome) | none | `INF372breathe` In 72 hours prior to death, difficulty breathing (0.66); `INF72breathe` In 72 hours prior to death, difficulty breathing (0.65); `INF372cyanosis` In 72 hours prior to death, cyanosis (0.64) |
| possible_miss | ncfrp_v51 | breathing frequency (outcome) | none | `SDYphysactbreath` Physical activity - Shortness of breath/difficulty breathing (0.66); `INF72breathe` In 72 hours prior to death, difficulty breathing (0.66); `INF372breathe` In 72 hours prior to death, difficulty breathing (0.65) |
| possible_miss | ncfrp_v51 | chronological age (offset) | none | `INFgestage` Gestational age in weeks (0.66); `INF3gestage` Gestational age in weeks (0.64); `INFgestunk` Gestational age in weeks - Unknown (0.64) |
| possible_miss | ncfrp_v51 | expiratory time (outcome) | none | `INF372breathe` In 72 hours prior to death, difficulty breathing (0.68); `INF72breathe` In 72 hours prior to death, difficulty breathing (0.67); `INF372cyanosis` In 72 hours prior to death, cyanosis (0.65) |
| possible_miss | ncfrp_v51 | postconceptional age (exposure) | none | `INFgestage` Gestational age in weeks (0.68); `INF3gestage` Gestational age in weeks (0.68); `INF3smallgest` Previous pregnancies - Small gestational age (0.67) |
| possible_miss | ncfrp_v51 | progesterone (exposure) | none | `INF3medprog` Medications/drugs - Progesterone/P17 (0.68); `INF4laborprechorm` If yes, precautions recommended - Rvd progesterone IM or vaginal progesterone (0.66); `INF3drugbirth` Infant born drug exposed (0.62) |
| possible_miss | prams_p7_arf | Gestational age at birth (covariate) | none | `GEST_WK_PU` Clinical estimate of gestational age grouped (0.79); `SGA_10` Small for Gestational Age Based on 10th Percentile (0.71); `PREV_LBW_RAW` Previous -- low birth weight (0.71) |
| possible_miss | prams_p7_arf | Maternal prepregnancy body mass index (BMI) (exposure) | none | `MAT_PRWT` Maternal weight - Prepregnancy (0.78); `MOM_BMI` VAR: MOM BODY MASS INDEX FROM QX (0.75); `MOM_BMI_BC` VAR: MOM BODY MASS INDEX FROM BC (0.75) |
| possible_miss | prams_p7_arf | PCA (postconceptional age) (outcome) | none | `GEST_WK_PU` Clinical estimate of gestational age grouped (0.67); `P_PRTERM` Previous preterm births (0.65); `OTH_TERM` No. of Previous other pregnancy outcomes Note: This variable is from the " NUMBER OF OTHER PREGNANCY OUTCOMES (36)" section of the U.S. standard birth certificate. This item includes spontaneous or induced losses or ectopic pregnancies. (0.64) |
| possible_miss | prams_p7_arf | Postconceptional age (PCA) (covariate) | none | `GEST_WK_PU` Clinical estimate of gestational age grouped (0.68); `SGA_10` Small for Gestational Age Based on 10th Percentile (0.67); `P_PRTERM` Previous preterm births (0.67) |
| possible_miss | prams_p7_arf | Preterm birth (covariate) | none | `P_PRTERM` Previous preterm births (0.73); `GEST_WK_PU` Clinical estimate of gestational age grouped (0.70); `PREGHX` VAR: HX PREV LIVE BIRTHS (0.69) |
| possible_miss | prams_p7_arf | birthweight (stratifier) | none | `PREV_LBW_RAW` Previous -- low birth weight (0.71); `PREV_LBW` Previous live birth -- low birth weight (FORCED SKIP) (0.70); `GRAM_NAPHSIS` Birth weight grouped into 250- gram intervals (0.68) |
| possible_miss | prams_p7_arf | birthweight (low, non-low) (stratifier) | none | `PREV_LBW` Previous live birth -- low birth weight (FORCED SKIP) (0.73); `PREV_LBW_RAW` Previous -- low birth weight (0.72); `GRAM_NAPHSIS` Birth weight grouped into 250- gram intervals (0.72) |
| possible_miss | prams_p7_arf | postconceptional age (exposure) | none | `GEST_WK_PU` Clinical estimate of gestational age grouped (0.70); `PREV_PRE` Previous live birth -- premature (FORCED SKIP) (0.68); `PREV_LBW` Previous live birth -- low birth weight (FORCED SKIP) (0.66) |
| possible_miss | prams_p7_arf | sex (stratifier) | none | `SEX` Gender of Infant (0.79); `TRANS` Infant transferred (0.64); `IDOB_MTH` Infant birth -- month (0.60) |
| possible_miss | prams_p8_arf | Gestational age at birth (covariate) | none | `GEST_WK_PU` Clinical estimate of gestational age grouped (0.79); `SGA_10` Small for Gestational Age Based on 10th Percentile (0.71); `SGA_2SD` Small for Gestational Age Based on 2SD from Mean (0.70) |
| possible_miss | prams_p8_arf | Maternal infections in pregnancy (exposure) | none | `PG8_UTI` Health prob during preg -- Kidney/bladder infection (0.65); `MM_FEVER` BC: mom had fever Note: This variable is from the "Characteristics of Labor and Delivery (45)" section of the U.S. standard birth certificate. This variable is coded as "yes" if chorioamnionitis is coded “Y”, it is coded as “no” if chorioamnionitis is  “N” , else it is coded “unknown”. (0.61); `MOMCIG` No. of cigarettes smoked daily during pregnancy Note: This variable is calculated by finding the average of the No. of Cigs in 1st Trimester, No. of Cigs in 2nd Trimester, and No. of Cigs in 3rd Trimester.  If any of these 3 values is unknown then variable is coded “unknown”. (0.61) |
| possible_miss | prams_p8_arf | Maternal prepregnancy body mass index (BMI) (exposure) | none | `MAT_PRWT` Maternal weight - Prepregnancy (0.78); `MOM_BMI` VAR: MOM BODY MASS INDEX FROM QX (0.75); `MOM_BMI_BC` VAR: MOM BODY MASS INDEX FROM BC (0.75) |
| possible_miss | prams_p8_arf | PCA (postconceptional age) (outcome) | none | `GEST_WK_PU` Clinical estimate of gestational age grouped (0.67); `P_PRTERM` Previous preterm births (0.65); `OTH_TERM` No. of Previous Other Pregnancy Outcomes Note: This variable is from the " NUMBER OF OTHER PREGNANCY OUTCOMES (36)" section of the U.S. standard birth certificate. This item includes spontaneous or induced losses or ectopic pregnancies. (0.64) |
| possible_miss | prams_p8_arf | Postconceptional age (PCA) (covariate) | none | `GEST_WK_PU` Clinical estimate of gestational age grouped (0.68); `SGA_10` Small for Gestational Age Based on 10th Percentile (0.67); `P_PRTERM` Previous preterm births (0.67) |
| possible_miss | prams_p8_arf | Preterm birth (covariate) | none | `P_PRTERM` Previous preterm births (0.73); `GEST_WK_PU` Clinical estimate of gestational age grouped (0.70); `RF_GHYPE` Gestational hypertension Note: This variable is only available starting with 2020 data (0.67) |
| possible_miss | prams_p8_arf | birthweight (stratifier) | none | `GRAM_NAPHSIS` Birth weight grouped into 250-gram intervals (0.68); `SGA_10` Small for Gestational Age Based on 10th Percentile (0.67); `MACROSOMIA` Macrosomia:  >= 4500 gram birth weight (0.67) |
| possible_miss | prams_p8_arf | birthweight (low, non-low) (stratifier) | none | `GRAM_NAPHSIS` Birth weight grouped into 250-gram intervals (0.72); `SGA_10` Small for Gestational Age Based on 10th Percentile (0.67); `MACROSOMIA` Macrosomia:  >= 4500 gram birth weight (0.67) |
| possible_miss | prams_p8_arf | postconceptional age (exposure) | none | `GEST_WK_PU` Clinical estimate of gestational age grouped (0.70); `OTH_TERM` No. of Previous Other Pregnancy Outcomes Note: This variable is from the " NUMBER OF OTHER PREGNANCY OUTCOMES (36)" section of the U.S. standard birth certificate. This item includes spontaneous or induced losses or ectopic pregnancies. (0.65); `SGA_10` Small for Gestational Age Based on 10th Percentile (0.65) |
| possible_miss | prams_p8_arf | sex (stratifier) | none | `SEX` Gender of infant (0.79); `TRANS` Infant transferred (0.66); `IDOB_MTH` Infant birth -- month (0.60) |
| possible_miss | prams_p8_std2 | Maternal prepregnancy body mass index (BMI) (exposure) | none | `PGWTGNU8_DK` Unit of preg weight gain (DONT KNOW = 7) (0.66); `PGWTGNU8` Unit of preg weight gain (0.65); `PGWTGN8` Preg weight gain (0.65) |

Full records, including agreements: `B_check.json`.

```json
{
  "mappings": [
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "cdc_linkco15",
      "variable": "UCODR130",
      "compatibility": "direct",
      "rationale": "The variable UCODR130 is a 130 Infant Cause Recode which includes codes for Sudden infant death syndrome (R95), Accidental suffocation and strangulation in bed (W75), or Other ill-defined and unspecified causes of mortality (R99)."
    },
    {
      "concept": "Infant sex",
      "source_id": "cdc_linkco15",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "The variable SEX directly represents the biological sex of the infant."
    },
    {
      "concept": "Postconceptional age (PCA)",
      "source_id": "cdc_linkco15",
      "variable": "COMBGEST",
      "compatibility": "derived",
      "rationale": "Derived from COMBGEST, which is a combined gestational age in weeks. PCA can be computed by adding postnatal age to this value."
    },
    {
      "concept": "Maternal smoking during pregnancy",
      "source_id": "cdc_linkco15",
      "variable": "CIG_REC",
      "compatibility": "proxy",
      "rationale": "The variable CIG_REC is a recode of cigarette use during pregnancy, which can be used as an indicator for maternal smoking."
    },
    {
      "concept": "Preterm birth",
      "source_id": "cdc_linkco15",
      "variable": "GESTREC3",
      "compatibility": "derived",
      "rationale": "Derived from GESTREC3, which is a recode of gestational age. Preterm birth can be derived by comparing the value to 37 weeks."
    },
    {
      "concept": "Breastfeeding status at discharge",
      "source_id": "cdc_linkco15",
      "variable": "BFED",
      "compatibility": "direct",
      "rationale": "The variable BFED indicates whether the infant was being breastfed at discharge."
    },
    {
      "concept": "postconceptional age",
      "source_id": "cdc_linkco15",
      "variable": "COMBGEST",
      "compatibility": "derived",
      "rationale": "Derived from COMBGEST, which is a combined gestational age in weeks. PCA can be computed by adding postnatal age to this value."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "cdc_linkco15",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "The variable SEX directly represents the biological sex of the infant."
    },
    {
      "concept": "year of birth or death",
      "source_id": "cdc_linkco15",
      "variable": "DOB_YY",
      "compatibility": "derived",
      "rationale": "Derived from DOB_YY, which is the year of birth. The year of death can be derived by combining this with other variables."
    },
    {
      "concept": "SUID",
      "source_id": "cdc_linkco15",
      "variable": "UCODR130",
      "compatibility": "direct",
      "rationale": "The variable UCODR130 is a 130 Infant Cause Recode which includes codes for Sudden infant death syndrome (R95), Accidental suffocation and strangulation in bed (W75), or Other ill-defined and unspecified causes of mortality (R99)."
    },
    {
      "concept": "bed sharing",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for bed sharing."
    },
    {
      "concept": "birthweight (low, non-low)",
      "source_id": "cdc_linkco15",
      "variable": "BWTR4",
      "compatibility": "derived",
      "rationale": "Derived from BWTR4, which is a birth weight recode. Low birthweight can be derived by comparing the value to 2,500 grams."
    },
    {
      "concept": "PCA (postconceptional age)",
      "source_id": "cdc_linkco15",
      "variable": "COMBGEST",
      "compatibility": "derived",
      "rationale": "Derived from COMBGEST, which is a combined gestational age in weeks. PCA can be computed by adding postnatal age to this value."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "cdc_linkco15",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "The variable SEX directly represents the biological sex of the infant."
    },
    {
      "concept": "birthweight (low, non-low)",
      "source_id": "cdc_linkco15",
      "variable": "BWTR4",
      "compatibility": "derived",
      "rationale": "Derived from BWTR4, which is a birth weight recode. Low birthweight can be derived by comparing the value to 2,500 grams."
    },
    {
      "concept": "maternal smoking status (smoking, non-smoking)",
      "source_id": "cdc_linkco15",
      "variable": "CIG_REC",
      "compatibility": "proxy",
      "rationale": "The variable CIG_REC is a recode of cigarette use during pregnancy, which can be used as an indicator for maternal smoking."
    },
    {
      "concept": "Maternal prepregnancy body mass index (BMI)",
      "source_id": "cdc_linkco15",
      "variable": "BMI_R",
      "compatibility": "direct",
      "rationale": "The variable BMI_R is a recode of the mother’s Body Mass Index."
    },
    {
      "concept": "Gestational age at birth",
      "source_id": "cdc_linkco15",
      "variable": "COMBGEST",
      "compatibility": "direct",
      "rationale": "The variable COMBGEST is a combined gestational age in weeks."
    },
    {
      "concept": "Maternal infections in pregnancy",
      "source_id": "cdc_linkco15",
      "variable": "IP_HEPC",
      "compatibility": "proxy",
      "rationale": "The variable IP_HEPC indicates whether the mother had Hepatitis C during pregnancy, which is one of the maternal infections."
    },
    {
      "concept": "Age of death in SUID cases",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for age at death specifically for SUID cases."
    },
    {
      "concept": "Geographic location",
      "source_id": "cdc_linkco15",
      "variable": "MRCNTYFIPS",
      "compatibility": "proxy",
      "rationale": "The variable MRCNTYFIPS is the FIPS County code for mother’s residence, which can be used to infer geographic location."
    },
    {
      "concept": "inner ear dysfunction",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for inner ear dysfunction."
    },
    {
      "concept": "control condition",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for control conditions in the context of experimental studies."
    },
    {
      "concept": "body movement arousal response to severe hypoxia-hypercarbia",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for body movement arousal responses."
    },
    {
      "concept": "hypercapnic ventilatory response",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for hypercapnic ventilatory response."
    },
    {
      "concept": "age of mice",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to age of experimental animals like mice."
    },
    {
      "concept": "baseline cSN activity",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for baseline sympathetic nerve activity."
    },
    {
      "concept": "breathing frequency",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for breathing frequency."
    },
    {
      "concept": "expiratory time",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for expiratory time."
    },
    {
      "concept": "PiCo specific cholinergic-glutamatergic neurons",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for PiCo-specific cholinergic-glutamatergic neurons."
    },
    {
      "concept": "glutamatergic PiCo neurons",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for glutamatergic PiCo neurons."
    },
    {
      "concept": "ChAT containing neurons",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for ChAT-containing neurons."
    },
    {
      "concept": "Dbx1 and Vglut2 neurons",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for Dbx1 and Vglut2 neurons."
    },
    {
      "concept": "preBötzinger complex (preBötC)",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for the preBötzinger complex."
    },
    {
      "concept": "chronic intermittent hypoxia (CIH)",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for chronic intermittent hypoxia."
    },
    {
      "concept": "diaphragm activity",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for diaphragm activity."
    },
    {
      "concept": "vagus nerve activity",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for vagus nerve activity."
    },
    {
      "concept": "cervical sympathetic nerve activity",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for cervical sympathetic nerve activity."
    },
    {
      "concept": "chronic intermittent hypoxia (IH)",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for chronic intermittent hypoxia."
    },
    {
      "concept": "adult neurogenesis",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for adult neurogenesis."
    },
    {
      "concept": "synaptic plasticity",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for synaptic plasticity."
    },
    {
      "concept": "reactive oxygen species (ROS)",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for reactive oxygen species."
    },
    {
      "concept": "breathing patterns",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for breathing patterns."
    },
    {
      "concept": "survival",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for survival rates in mice."
    },
    {
      "concept": "inhibition",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for inhibition."
    },
    {
      "concept": "excitation",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for excitation."
    },
    {
      "concept": "lipopolysaccharide (LPS)",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for lipopolysaccharide."
    },
    {
      "concept": "progesterone",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for progesterone."
    },
    {
      "concept": "neurogenesis",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for neurogenesis."
    },
    {
      "concept": "microglia activation",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC linked birth/infant death public-use file does not contain any variables related to microglia activation or Iba1 staining."
    },
    {
      "concept": "cell death",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC linked birth/infant death public-use file does not contain any variables related to cell death or cleaved caspase 3 (CC3) staining."
    },
    {
      "concept": "glutamatergic transmission",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC linked birth/infant death public-use file does not contain any variables related to glutamatergic transmission in the nucleus accumbens and amygdala."
    },
    {
      "concept": "hypoglossal motor nucleus (XIIn)",
      "source_id": "cdc_linkco15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC linked birth/infant death public-use file does not contain any variables related to electrophysiological recordings from the hypoglossal motor nucleus (XIIn)."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC natality public-use file does not contain specific variables for SUID outcomes."
    },
    {
      "concept": "Infant sex",
      "source_id": "cdc_natl15",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "The variable 'SEX' directly corresponds to the infant's biological sex."
    },
    {
      "concept": "Postconceptional age (PCA)",
      "source_id": "cdc_natl15",
      "variable": "COMBGEST",
      "compatibility": "derived",
      "rationale": "Derived from 'COMBGEST' which provides the combined gestational age in weeks, and postnatal age can be calculated by subtracting this value from total PCA."
    },
    {
      "concept": "Maternal smoking during pregnancy",
      "source_id": "cdc_natl15",
      "variable": "CIG_REC",
      "compatibility": "proxy",
      "rationale": "The variable 'CIG_REC' provides a recode of maternal cigarette use, which can be used as a proxy for smoking status."
    },
    {
      "concept": "Preterm birth",
      "source_id": "cdc_natl15",
      "variable": "GESTREC3",
      "compatibility": "direct",
      "rationale": "The variable 'GESTREC3' categorizes gestational age into preterm and full-term categories."
    },
    {
      "concept": "Breastfeeding status at discharge",
      "source_id": "cdc_natl15",
      "variable": "BFED",
      "compatibility": "direct",
      "rationale": "The variable 'BFED' indicates whether the infant was breastfed at hospital discharge."
    },
    {
      "concept": "postconceptional age",
      "source_id": "cdc_natl15",
      "variable": "COMBGEST",
      "compatibility": "derived",
      "rationale": "Derived from 'COMBGEST' which provides the combined gestational and postnatal age in weeks."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "cdc_natl15",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "The variable 'SEX' directly corresponds to the infant's biological sex."
    },
    {
      "concept": "year of birth or death",
      "source_id": "cdc_natl15",
      "variable": "DOB_YY",
      "compatibility": "proxy",
      "rationale": "The variable 'DOB_YY' provides the year of birth, which can be used to stratify by year."
    },
    {
      "concept": "SUID",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC natality public-use file does not contain specific variables for SUID outcomes."
    },
    {
      "concept": "bed sharing",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the CDC natality public-use file that captures bed-sharing behavior."
    },
    {
      "concept": "birthweight (low, non-low)",
      "source_id": "cdc_natl15",
      "variable": "BWTR4",
      "compatibility": "proxy",
      "rationale": "The variable 'BWTR4' categorizes birth weight into low and normal categories."
    },
    {
      "concept": "PCA (postconceptional age)",
      "source_id": "cdc_natl15",
      "variable": "COMBGEST",
      "compatibility": "derived",
      "rationale": "Derived from 'COMBGEST' which provides the combined gestational and postnatal age in weeks."
    },
    {
      "concept": "chronological age",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable that directly measures chronological age; it would need to be derived from birth date and current date."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "cdc_natl15",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "The variable 'SEX' directly corresponds to the infant's biological sex."
    },
    {
      "concept": "birthweight (low, non-low)",
      "source_id": "cdc_natl15",
      "variable": "BWTR4",
      "compatibility": "proxy",
      "rationale": "The variable 'BWTR4' categorizes birth weight into low and normal categories."
    },
    {
      "concept": "maternal smoking status (smoking, non-smoking)",
      "source_id": "cdc_natl15",
      "variable": "CIG_REC",
      "compatibility": "proxy",
      "rationale": "The variable 'CIG_REC' provides a recode of maternal cigarette use, which can be used as a proxy for smoking status."
    },
    {
      "concept": "Maternal prepregnancy body mass index (BMI)",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable that captures maternal prepregnancy BMI directly."
    },
    {
      "concept": "Gestational age at birth",
      "source_id": "cdc_natl15",
      "variable": "COMBGEST",
      "compatibility": "direct",
      "rationale": "The variable 'COMBGEST' provides the combined gestational age in weeks."
    },
    {
      "concept": "Maternal infections in pregnancy",
      "source_id": "cdc_natl15",
      "variable": "IP_HEPC",
      "compatibility": "direct",
      "rationale": "The variable 'IP_HEPC' indicates whether the mother had hepatitis C during pregnancy."
    },
    {
      "concept": "Age of death in SUID cases",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable that captures age at death for SUID cases."
    },
    {
      "concept": "Geographic location",
      "source_id": "cdc_natl15",
      "variable": "OCNTYFIPS",
      "compatibility": "proxy",
      "rationale": "The variable 'OCNTYFIPS' provides the FIPS county code, which can be used to infer geographic location."
    },
    {
      "concept": "inner ear dysfunction",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable that captures inner ear dysfunction in the CDC natality public-use file."
    },
    {
      "concept": "control condition",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept of a control condition is not applicable to this data source."
    },
    {
      "concept": "body movement arousal response to severe hypoxia-hypercarbia",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable that captures body movement arousal responses in the CDC natality public-use file."
    },
    {
      "concept": "hypercapnic ventilatory response",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable that captures hypercapnic ventilatory responses in the CDC natality public-use file."
    },
    {
      "concept": "age of mice",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept is not applicable to human birth data."
    },
    {
      "concept": "baseline cSN activity",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable that captures baseline sympathetic nerve activity in the CDC natality public-use file."
    },
    {
      "concept": "breathing frequency",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept is not applicable to human birth data."
    },
    {
      "concept": "expiratory time",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable that captures expiratory time in the CDC natality public-use file."
    },
    {
      "concept": "PiCo specific cholinergic-glutamatergic neurons",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept is not applicable to human birth data."
    },
    {
      "concept": "glutamatergic PiCo neurons",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept is not applicable to human birth data."
    },
    {
      "concept": "ChAT containing neurons",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept is not applicable to human birth data."
    },
    {
      "concept": "Dbx1 and Vglut2 neurons",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept is not applicable to human birth data."
    },
    {
      "concept": "preBötzinger complex (preBötC)",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept is not applicable to human birth data."
    },
    {
      "concept": "chronic intermittent hypoxia (CIH)",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable that captures chronic intermittent hypoxia in the CDC natality public-use file."
    },
    {
      "concept": "diaphragm activity",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept is not applicable to human birth data."
    },
    {
      "concept": "vagus nerve activity",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable that captures vagus nerve activity in the CDC natality public-use file."
    },
    {
      "concept": "cervical sympathetic nerve activity",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable that captures cervical sympathetic nerve activity in the CDC natality public-use file."
    },
    {
      "concept": "chronic intermittent hypoxia (IH)",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable that captures chronic intermittent hypoxia in the CDC natality public-use file."
    },
    {
      "concept": "adult neurogenesis",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept is not applicable to human birth data."
    },
    {
      "concept": "synaptic plasticity",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable that captures synaptic plasticity in the CDC natality public-use file."
    },
    {
      "concept": "reactive oxygen species (ROS)",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable that captures reactive oxygen species in the CDC natality public-use file."
    },
    {
      "concept": "breathing patterns",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept is not applicable to human birth data."
    },
    {
      "concept": "survival",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable that captures survival rates in the CDC natality public-use file."
    },
    {
      "concept": "inhibition",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept is not applicable to human birth data."
    },
    {
      "concept": "excitation",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept is not applicable to human birth data."
    },
    {
      "concept": "lipopolysaccharide (LPS)",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable that captures lipopolysaccharide exposure in the CDC natality public-use file."
    },
    {
      "concept": "progesterone",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable that captures progesterone administration in the CDC natality public-use file."
    },
    {
      "concept": "neurogenesis",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept is not applicable to human birth data."
    },
    {
      "concept": "microglia activation",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept of microglia activation assessed by Iba1 staining is a cellular biology measure that cannot be mapped to any variable in the CDC natality public-use file."
    },
    {
      "concept": "cell death",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept of cell death assessed by cleaved caspase 3 (CC3) staining is a cellular biology measure that cannot be mapped to any variable in the CDC natality public-use file."
    },
    {
      "concept": "glutamatergic transmission",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept of glutamatergic transmission assessed in the nucleus accumbens and amygdala is a neuroscience measure that cannot be mapped to any variable in the CDC natality public-use file."
    },
    {
      "concept": "hypoglossal motor nucleus (XIIn)",
      "source_id": "cdc_natl15",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept of hypoglossal motor nucleus assessed by electrophysiological recordings from brainstem slices is a neuroscience measure that cannot be mapped to any variable in the CDC natality public-use file."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not provide specific variables for SUID as defined by ICD-10 codes R95, R99, and W75."
    },
    {
      "concept": "Infant sex",
      "source_id": "cdc_codenames",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "The variable 'SEX' directly corresponds to the infant's biological sex."
    },
    {
      "concept": "Postconceptional age (PCA)",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for postconceptional age in the CDC data. It would need to be derived from gestational age and chronological age, which are not provided separately."
    },
    {
      "concept": "Maternal smoking during pregnancy",
      "source_id": "cdc_codenames",
      "variable": "CIG_REC",
      "compatibility": "proxy",
      "rationale": "The variable 'CIG_REC' is a recode of maternal cigarette use during pregnancy, which can be used as an indicator for smoking status."
    },
    {
      "concept": "Preterm birth",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable indicating preterm birth; it would need to be derived from gestational age, which is not available."
    },
    {
      "concept": "Breastfeeding status at discharge",
      "source_id": "cdc_codenames",
      "variable": "BFED",
      "compatibility": "direct",
      "rationale": "The variable 'BFED' indicates whether the infant was breastfed at hospital discharge."
    },
    {
      "concept": "postconceptional age",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for postconceptional age; it would need to be derived from gestational and chronological ages, which are not provided."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "cdc_codenames",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "The variable 'SEX' directly corresponds to the infant's biological sex."
    },
    {
      "concept": "year of birth or death",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for year of birth or death; it would need to be derived from the date of birth, which is not provided."
    },
    {
      "concept": "SUID",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for SUID as defined by ICD-10 codes R95, R99, and W75."
    },
    {
      "concept": "bed sharing",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for bed sharing in the CDC data."
    },
    {
      "concept": "birthweight (low, non-low)",
      "source_id": "cdc_codenames",
      "variable": "BWTR4",
      "compatibility": "proxy",
      "rationale": "The variable 'BWTR4' categorizes birth weight into low and normal categories."
    },
    {
      "concept": "PCA (postconceptional age)",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for postconceptional age; it would need to be derived from gestational and chronological ages, which are not provided."
    },
    {
      "concept": "chronological age",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for chronological age; it would need to be derived from the date of birth, which is not provided."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "cdc_codenames",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "The variable 'SEX' directly corresponds to the infant's biological sex."
    },
    {
      "concept": "birthweight (low, non-low)",
      "source_id": "cdc_codenames",
      "variable": "BWTR4",
      "compatibility": "proxy",
      "rationale": "The variable 'BWTR4' categorizes birth weight into low and normal categories."
    },
    {
      "concept": "maternal smoking status (smoking, non-smoking)",
      "source_id": "cdc_codenames",
      "variable": "CIG_REC",
      "compatibility": "proxy",
      "rationale": "The variable 'CIG_REC' is a recode of maternal cigarette use during pregnancy."
    },
    {
      "concept": "Maternal prepregnancy body mass index (BMI)",
      "source_id": "cdc_codenames",
      "variable": "BMI_R",
      "compatibility": "direct",
      "rationale": "The variable 'BMI_R' provides the mother's BMI."
    },
    {
      "concept": "Gestational age at birth",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for gestational age; it would need to be derived from obstetric estimates, which are not provided."
    },
    {
      "concept": "Maternal infections in pregnancy",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for maternal infections such as chlamydia, gonorrhea, and hepatitis C."
    },
    {
      "concept": "Age of death in SUID cases",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for age at death; it would need to be derived from the date of birth and death, which are not provided."
    },
    {
      "concept": "Geographic location",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for geographic location such as state, latitude, and longitude."
    },
    {
      "concept": "inner ear dysfunction",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to inner ear dysfunction or gentamicin injections."
    },
    {
      "concept": "control condition",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for control conditions such as intra-tympanic saline or intra-peritoneal gentamicin."
    },
    {
      "concept": "body movement arousal response to severe hypoxia-hypercarbia",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to body movement responses to hypoxia and hypercapnia."
    },
    {
      "concept": "hypercapnic ventilatory response",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to hypercapnic ventilatory responses."
    },
    {
      "concept": "age of mice",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for age of mice in the CDC data."
    },
    {
      "concept": "baseline cSN activity",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to baseline sympathetic nerve activity."
    },
    {
      "concept": "breathing frequency",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for breathing frequency in the CDC data."
    },
    {
      "concept": "expiratory time",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to expiratory times."
    },
    {
      "concept": "PiCo specific cholinergic-glutamatergic neurons",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to PiCo-specific neuronal stimulation."
    },
    {
      "concept": "glutamatergic PiCo neurons",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to glutamatergic neuronal stimulation."
    },
    {
      "concept": "ChAT containing neurons",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to ChAT-containing neuronal stimulation."
    },
    {
      "concept": "Dbx1 and Vglut2 neurons",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to Dbx1 and Vglut2 neuronal stimulation."
    },
    {
      "concept": "preBötzinger complex (preBötC)",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to preBötzinger complex neuronal stimulation."
    },
    {
      "concept": "chronic intermittent hypoxia (CIH)",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to chronic intermittent hypoxia exposure."
    },
    {
      "concept": "diaphragm activity",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for diaphragm muscle activity in the CDC data."
    },
    {
      "concept": "vagus nerve activity",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to vagal nerve activity."
    },
    {
      "concept": "cervical sympathetic nerve activity",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for cervical sympathetic nerve activity in the CDC data."
    },
    {
      "concept": "chronic intermittent hypoxia (IH)",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to chronic intermittent hypoxia exposure."
    },
    {
      "concept": "adult neurogenesis",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for adult neurogenesis in the CDC data."
    },
    {
      "concept": "synaptic plasticity",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to synaptic plasticity."
    },
    {
      "concept": "reactive oxygen species (ROS)",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for reactive oxygen species in the CDC data."
    },
    {
      "concept": "breathing patterns",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to breathing patterns."
    },
    {
      "concept": "survival",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for survival rates in the CDC data."
    },
    {
      "concept": "inhibition",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to inhibition."
    },
    {
      "concept": "excitation",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to excitation."
    },
    {
      "concept": "lipopolysaccharide (LPS)",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for lipopolysaccharide exposure in the CDC data."
    },
    {
      "concept": "progesterone",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The CDC data does not contain variables related to progesterone administration."
    },
    {
      "concept": "neurogenesis",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for neurogenesis in the CDC data."
    },
    {
      "concept": "microglia activation",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept of microglia activation assessed by Iba1 staining is a biological measurement that does not have an equivalent variable in the CDC birth/death file."
    },
    {
      "concept": "cell death",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept of cell death assessed by cleaved caspase 3 (CC3) staining is a biological measurement that does not have an equivalent variable in the CDC birth/death file."
    },
    {
      "concept": "glutamatergic transmission",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept of glutamatergic transmission assessed in the nucleus accumbens and amygdala is a biological measurement that does not have an equivalent variable in the CDC birth/death file."
    },
    {
      "concept": "hypoglossal motor nucleus (XIIn)",
      "source_id": "cdc_codenames",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept of hypoglossal motor nucleus assessed by electrophysiological recordings from brainstem slices is a biological measurement that does not have an equivalent variable in the CDC birth/death file."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "INF372infectunk",
      "compatibility": "proxy",
      "rationale": "The concept of Sudden Unexpected Infant Death (SUID) is not directly mapped to a single variable but can be inferred from the absence of infection or vaccination in the 72 hours prior to death and other medical conditions."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "INF372vacsp",
      "compatibility": "proxy",
      "rationale": "The concept of Sudden Unexpected Infant Death (SUID) is not directly mapped to a single variable but can be inferred from the absence of infection or vaccination in the 72 hours prior to death and other medical conditions."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "INF372medothsp",
      "compatibility": "proxy",
      "rationale": "The concept of Sudden Unexpected Infant Death (SUID) is not directly mapped to a single variable but can be inferred from the absence of infection or vaccination in the 72 hours prior to death and other medical conditions."
    },
    {
      "concept": "Infant sex",
      "source_id": "ncfrp_v51",
      "variable": "INFsex",
      "compatibility": "direct",
      "rationale": "The variable INFsex directly corresponds to the infant's biological sex, which is a primary exposure of interest."
    },
    {
      "concept": "Postconceptional age (PCA)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no direct variable for postconceptional age in the dataset. It would need to be derived from gestational age and birth date, but these variables are not available."
    },
    {
      "concept": "Breastfeeding status at discharge",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures breastfeeding status at discharge. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "postconceptional age",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures postconceptional age. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "ncfrp_v51",
      "variable": "INFsex",
      "compatibility": "direct",
      "rationale": "The variable INFsex directly corresponds to the infant's biological sex, which is a stratifier."
    },
    {
      "concept": "year of birth or death",
      "source_id": "ncfrp_v51",
      "variable": "INFdobyear",
      "compatibility": "direct",
      "rationale": "The variables INFdobyear and INFdodyear directly correspond to the year of birth and death respectively."
    },
    {
      "concept": "year of birth or death",
      "source_id": "ncfrp_v51",
      "variable": "INFdodyear",
      "compatibility": "direct",
      "rationale": "The variables INFdobyear and INFdodyear directly correspond to the year of birth and death respectively."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "INF372infectunk",
      "compatibility": "proxy",
      "rationale": "The concept of Sudden Unexpected Infant Death (SUID) is not directly mapped to a single variable but can be inferred from the absence of infection or vaccination in the 72 hours prior to death and other medical conditions."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "INF372vacsp",
      "compatibility": "proxy",
      "rationale": "The concept of Sudden Unexpected Infant Death (SUID) is not directly mapped to a single variable but can be inferred from the absence of infection or vaccination in the 72 hours prior to death and other medical conditions."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "INF372medothsp",
      "compatibility": "proxy",
      "rationale": "The concept of Sudden Unexpected Infant Death (SUID) is not directly mapped to a single variable but can be inferred from the absence of infection or vaccination in the 72 hours prior to death and other medical conditions."
    },
    {
      "concept": "birthweight (low, non-low)",
      "source_id": "ncfrp_v51",
      "variable": "INF3birthwtcat",
      "compatibility": "direct",
      "rationale": "The variable INF3birthwtcat directly corresponds to the birth weight category."
    },
    {
      "concept": "PCA (postconceptional age)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures postconceptional age. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "ncfrp_v51",
      "variable": "INFsex",
      "compatibility": "direct",
      "rationale": "The variable INFsex directly corresponds to the infant's biological sex, which is a stratifier."
    },
    {
      "concept": "birthweight (low, non-low)",
      "source_id": "ncfrp_v51",
      "variable": "INF3birthwtcat",
      "compatibility": "direct",
      "rationale": "The variable INF3birthwtcat directly corresponds to the birth weight category."
    },
    {
      "concept": "Maternal prepregnancy body mass index (BMI)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures maternal prepregnancy BMI. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "Maternal infections in pregnancy",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures maternal infections during pregnancy. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "Age of death in SUID cases",
      "source_id": "ncfrp_v51",
      "variable": "INFdayslive",
      "compatibility": "direct",
      "rationale": "The variable INFdayslive directly corresponds to the number of days lived, which can be used to determine age at death."
    },
    {
      "concept": "Geographic location",
      "source_id": "ncfrp_v51",
      "variable": "INFaddrst",
      "compatibility": "direct",
      "rationale": "The variables INFaddrst and INFdthstate directly correspond to the state of residence and death respectively."
    },
    {
      "concept": "Geographic location",
      "source_id": "ncfrp_v51",
      "variable": "INFdthstate",
      "compatibility": "direct",
      "rationale": "The variables INFaddrst and INFdthstate directly correspond to the state of residence and death respectively."
    },
    {
      "concept": "inner ear dysfunction",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures inner ear dysfunction. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "control condition",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures control conditions. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "body movement arousal response to severe hypoxia-hypercarbia",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures body movement arousal responses. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "hypercapnic ventilatory response",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures hypercapnic ventilatory responses. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "age of mice",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures age of mice. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "baseline cSN activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures baseline cSN activity. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "breathing frequency",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures breathing frequency. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "expiratory time",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures expiratory time. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "PiCo specific cholinergic-glutamatergic neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures PiCo specific cholinergic-glutamatergic neurons. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "glutamatergic PiCo neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures glutamatergic PiCo neurons. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "ChAT containing neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures ChAT containing neurons. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "Dbx1 and Vglut2 neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures Dbx1 and Vglut2 neurons. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "preBötzinger complex (preBötC)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures preBötzinger complex. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "chronic intermittent hypoxia (CIH)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures chronic intermittent hypoxia. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "diaphragm activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures diaphragm activity. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "vagus nerve activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures vagus nerve activity. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "cervical sympathetic nerve activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures cervical sympathetic nerve activity. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "chronic intermittent hypoxia (IH)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures chronic intermittent hypoxia. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "adult neurogenesis",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures adult neurogenesis. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "synaptic plasticity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures synaptic plasticity. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "reactive oxygen species (ROS)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures reactive oxygen species. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "breathing patterns",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures breathing patterns. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "survival",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures survival. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "inhibition",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures inhibition. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "excitation",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures excitation. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "lipopolysaccharide (LPS)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures lipopolysaccharide. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "progesterone",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures progesterone. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "neurogenesis",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no documented variable in the dataset that directly measures neurogenesis. The closest related variables do not provide a clear proxy."
    },
    {
      "concept": "microglia activation",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept 'microglia activation' assessed by Iba1 staining is a cellular process that cannot be directly or indirectly measured in the National Fatality Review Case Reporting System (NFR-CRS) data. The source does not contain any variables related to biological markers of microglial activity."
    },
    {
      "concept": "cell death",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept 'cell death' assessed by cleaved caspase 3 (CC3) staining is a cellular process that cannot be directly or indirectly measured in the National Fatality Review Case Reporting System (NFR-CRS). The source does not contain any variables related to biological markers of cell death."
    },
    {
      "concept": "glutamatergic transmission",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept 'glutamatergic transmission' assessed in the nucleus accumbens and amygdala is a neurochemical process that cannot be directly or indirectly measured in the National Fatality Review Case Reporting System (NFR-CRS). The source does not contain any variables related to neurotransmitter activity."
    },
    {
      "concept": "hypoglossal motor nucleus (XIIn)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept 'hypoglossal motor nucleus' assessed by electrophysiological recordings from brainstem slices is a neurological process that cannot be directly or indirectly measured in the National Fatality Review Case Reporting System (NFR-CRS). The source does not contain any variables related to neural activity measurements."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "INF4outcome",
      "compatibility": "direct",
      "rationale": "The variable 'INF4outcome' in the NFR-CRS codebook v5.1 includes cause of death codes that align with ICD-10 codes R95, R99, and W75."
    },
    {
      "concept": "Postconceptional age (PCA)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures postconceptional age."
    },
    {
      "concept": "Breastfeeding status at discharge",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures breastfeeding status at discharge."
    },
    {
      "concept": "postconceptional age",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures postconceptional age."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "INF4outcome",
      "compatibility": "direct",
      "rationale": "The variable 'INF4outcome' in the NFR-CRS codebook v5.1 includes cause of death codes that align with ICD-10 codes R95, R99, and W75."
    },
    {
      "concept": "PCA (postconceptional age)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures postconceptional age."
    },
    {
      "concept": "chronological age",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures chronological age."
    },
    {
      "concept": "Maternal prepregnancy body mass index (BMI)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures maternal prepregnancy BMI."
    },
    {
      "concept": "Maternal infections in pregnancy",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures maternal infections such as chlamydia, gonorrhea, and hepatitis C."
    },
    {
      "concept": "inner ear dysfunction",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures inner ear dysfunction."
    },
    {
      "concept": "control condition",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures control conditions."
    },
    {
      "concept": "body movement arousal response to severe hypoxia-hypercarbia",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures body movement arousal response to severe hypoxia-hypercarbia."
    },
    {
      "concept": "hypercapnic ventilatory response",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures hypercapnic ventilatory response."
    },
    {
      "concept": "age of mice",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures the age of mice."
    },
    {
      "concept": "baseline cSN activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures baseline cSN activity."
    },
    {
      "concept": "breathing frequency",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures breathing frequency."
    },
    {
      "concept": "expiratory time",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures expiratory time."
    },
    {
      "concept": "PiCo specific cholinergic-glutamatergic neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures PiCo specific cholinergic-glutamatergic neurons."
    },
    {
      "concept": "glutamatergic PiCo neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures glutamatergic PiCo neurons."
    },
    {
      "concept": "ChAT containing neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures ChAT containing neurons."
    },
    {
      "concept": "Dbx1 and Vglut2 neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures Dbx1 and Vglut2 neurons."
    },
    {
      "concept": "preBötzinger complex (preBötC)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures preBötzinger complex."
    },
    {
      "concept": "chronic intermittent hypoxia (CIH)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures chronic intermittent hypoxia."
    },
    {
      "concept": "diaphragm activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures diaphragm activity."
    },
    {
      "concept": "vagus nerve activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures vagus nerve activity."
    },
    {
      "concept": "cervical sympathetic nerve activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures cervical sympathetic nerve activity."
    },
    {
      "concept": "chronic intermittent hypoxia (IH)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures chronic intermittent hypoxia."
    },
    {
      "concept": "adult neurogenesis",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures adult neurogenesis."
    },
    {
      "concept": "synaptic plasticity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures synaptic plasticity."
    },
    {
      "concept": "reactive oxygen species (ROS)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures reactive oxygen species."
    },
    {
      "concept": "breathing patterns",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures breathing patterns."
    },
    {
      "concept": "survival",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures survival."
    },
    {
      "concept": "inhibition",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures inhibition."
    },
    {
      "concept": "excitation",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures excitation."
    },
    {
      "concept": "lipopolysaccharide (LPS)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures lipopolysaccharide."
    },
    {
      "concept": "progesterone",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures progesterone."
    },
    {
      "concept": "neurogenesis",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NFR-CRS codebook v5.1 does not provide a variable that captures neurogenesis."
    },
    {
      "concept": "microglia activation",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFR-CRS codebook v5.1 does not contain any variables related to microglia activation or Iba1 staining."
    },
    {
      "concept": "cell death",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFR-CRS codebook v5.1 does not contain any variables related to cell death or cleaved caspase 3 (CC3) staining."
    },
    {
      "concept": "glutamatergic transmission",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFR-CRS codebook v5.1 does not contain any variables related to glutamatergic transmission in the nucleus accumbens or amygdala."
    },
    {
      "concept": "hypoglossal motor nucleus (XIIn)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFR-CRS codebook v5.1 does not contain any variables related to electrophysiological recordings from the hypoglossal motor nucleus (XIIn)."
    },
    {
      "concept": "Postconceptional age (PCA)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that captures postconceptional age."
    },
    {
      "concept": "Breastfeeding status at discharge",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that captures breastfeeding status at discharge."
    },
    {
      "concept": "postconceptional age",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that captures postconceptional age."
    },
    {
      "concept": "PCA (postconceptional age)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that captures postconceptional age."
    },
    {
      "concept": "chronological age",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that captures chronological age."
    },
    {
      "concept": "Maternal prepregnancy body mass index (BMI)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that captures maternal BMI."
    },
    {
      "concept": "Maternal infections in pregnancy",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that captures maternal infections during pregnancy."
    },
    {
      "concept": "Geographic location",
      "source_id": "ncfrp_v51",
      "variable": "INCstate",
      "compatibility": "proxy",
      "rationale": "The data source contains variables capturing state and county of incident, which can be used as a proxy for geographic location."
    },
    {
      "concept": "inner ear dysfunction",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to inner ear dysfunction or gentamicin injections."
    },
    {
      "concept": "control condition",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that captures control conditions such as intra-tympanic saline or intra-peritoneal gentamicin."
    },
    {
      "concept": "body movement arousal response to severe hypoxia-hypercarbia",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to body movement responses to hypoxia-hypercarbia."
    },
    {
      "concept": "hypercapnic ventilatory response",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to hypercapnic ventilatory responses."
    },
    {
      "concept": "age of mice",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that captures the age of experimental animals such as mice."
    },
    {
      "concept": "baseline cSN activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to baseline sympathetic nerve activity following CIH exposure."
    },
    {
      "concept": "breathing frequency",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that captures breathing frequency changes due to CIH exposure."
    },
    {
      "concept": "expiratory time",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that captures expiratory times following CIH exposure."
    },
    {
      "concept": "PiCo specific cholinergic-glutamatergic neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to optogenetic stimulation of PiCo-specific neurons."
    },
    {
      "concept": "glutamatergic PiCo neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to optogenetic stimulation of glutamatergic PiCo neurons."
    },
    {
      "concept": "ChAT containing neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to optogenetic stimulation of ChAT-containing neurons."
    },
    {
      "concept": "Dbx1 and Vglut2 neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to optogenetic stimulation of Dbx1 and Vglut2 neurons."
    },
    {
      "concept": "preBötzinger complex (preBötC)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to optogenetic stimulation of the preBötzinger complex."
    },
    {
      "concept": "chronic intermittent hypoxia (CIH)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to chronic intermittent hypoxia exposure."
    },
    {
      "concept": "diaphragm activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that captures changes in diaphragm muscle activity."
    },
    {
      "concept": "vagus nerve activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that captures changes in vagal nerve activity."
    },
    {
      "concept": "cervical sympathetic nerve activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that captures changes in cervical sympathetic nerve activity."
    },
    {
      "concept": "chronic intermittent hypoxia (IH)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to chronic intermittent hypoxia exposure."
    },
    {
      "concept": "adult neurogenesis",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to adult neurogenesis in the brain."
    },
    {
      "concept": "synaptic plasticity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to synaptic plasticity."
    },
    {
      "concept": "reactive oxygen species (ROS)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that captures reactive oxygen species levels or their effects."
    },
    {
      "concept": "breathing patterns",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to breathing patterns in newborn mice."
    },
    {
      "concept": "survival",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that captures survival rates of experimental animals."
    },
    {
      "concept": "inhibition",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to inhibition in the pre-Bötzinger complex."
    },
    {
      "concept": "excitation",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to excitation in the pre-Bötzinger complex."
    },
    {
      "concept": "lipopolysaccharide (LPS)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to LPS administration."
    },
    {
      "concept": "progesterone",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that captures progesterone administration."
    },
    {
      "concept": "neurogenesis",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to neurogenesis in the brain."
    },
    {
      "concept": "microglia activation",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept 'microglia activation' assessed by Iba1 staining is a biological measurement not covered in the provided data sources."
    },
    {
      "concept": "cell death",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept 'cell death' assessed by cleaved caspase 3 (CC3) staining is a biological measurement not covered in the provided data sources."
    },
    {
      "concept": "glutamatergic transmission",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept 'glutamatergic transmission' assessed in the nucleus accumbens and amygdala is a biological measurement not covered in the provided data sources."
    },
    {
      "concept": "hypoglossal motor nucleus (XIIn)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept 'hypoglossal motor nucleus' assessed by electrophysiological recordings from brainstem slices is a biological measurement not covered in the provided data sources."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "CAUdcimmcau",
      "compatibility": "direct",
      "rationale": "The variable CAUdcimmcau represents the immediate cause of death from the death certificate, which can include codes for SUID such as R95 (Sudden infant death syndrome), W75 (Accidental suffocation and strangulation in bed), or R99 (Other ill-defined and unspecified causes of mortality)."
    },
    {
      "concept": "Postconceptional age (PCA)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the data source that captures postconceptional age."
    },
    {
      "concept": "Breastfeeding status at discharge",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not include a variable for breastfeeding status at discharge."
    },
    {
      "concept": "postconceptional age",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the data source that captures postconceptional age."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "CAUdcimmcau",
      "compatibility": "direct",
      "rationale": "The variable CAUdcimmcau represents the immediate cause of death from the death certificate, which can include codes for SUID such as R95 (Sudden infant death syndrome), W75 (Accidental suffocation and strangulation in bed), or R99 (Other ill-defined and unspecified causes of mortality)."
    },
    {
      "concept": "PCA (postconceptional age)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the data source that captures postconceptional age."
    },
    {
      "concept": "chronological age",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a direct variable for chronological age."
    },
    {
      "concept": "Maternal prepregnancy body mass index (BMI)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a direct variable for maternal BMI."
    },
    {
      "concept": "Maternal infections in pregnancy",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not include a variable for maternal infections during pregnancy."
    },
    {
      "concept": "inner ear dysfunction",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the data source that captures inner ear dysfunction."
    },
    {
      "concept": "control condition",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a direct variable for control conditions in experiments."
    },
    {
      "concept": "body movement arousal response to severe hypoxia-hypercarbia",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the data source that captures body movement arousal responses."
    },
    {
      "concept": "hypercapnic ventilatory response",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a direct variable for hypercapnic ventilatory responses."
    },
    {
      "concept": "age of mice",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the data source that captures age of experimental animals."
    },
    {
      "concept": "baseline cSN activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a direct variable for baseline sympathetic nerve activity."
    },
    {
      "concept": "breathing frequency",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the data source that captures breathing frequency."
    },
    {
      "concept": "expiratory time",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a direct variable for expiratory times."
    },
    {
      "concept": "PiCo specific cholinergic-glutamatergic neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the data source that captures optogenetic stimulation of PiCo neurons."
    },
    {
      "concept": "glutamatergic PiCo neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a direct variable for glutamatergic PiCo neurons."
    },
    {
      "concept": "ChAT containing neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the data source that captures ChAT-containing neurons."
    },
    {
      "concept": "Dbx1 and Vglut2 neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a direct variable for Dbx1 and Vglut2 neurons."
    },
    {
      "concept": "preBötzinger complex (preBötC)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the data source that captures preBötzinger complex."
    },
    {
      "concept": "chronic intermittent hypoxia (CIH)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a direct variable for chronic intermittent hypoxia."
    },
    {
      "concept": "diaphragm activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the data source that captures diaphragm muscle activity."
    },
    {
      "concept": "vagus nerve activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a direct variable for vagal nerve activity."
    },
    {
      "concept": "cervical sympathetic nerve activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the data source that captures cervical sympathetic nerve activity."
    },
    {
      "concept": "chronic intermittent hypoxia (IH)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a direct variable for chronic intermittent hypoxia."
    },
    {
      "concept": "adult neurogenesis",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the data source that captures adult neurogenesis."
    },
    {
      "concept": "synaptic plasticity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a direct variable for synaptic plasticity."
    },
    {
      "concept": "reactive oxygen species (ROS)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the data source that captures reactive oxygen species."
    },
    {
      "concept": "breathing patterns",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a direct variable for breathing patterns."
    },
    {
      "concept": "survival",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the data source that captures survival rates."
    },
    {
      "concept": "inhibition",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a direct variable for inhibition."
    },
    {
      "concept": "excitation",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the data source that captures excitation."
    },
    {
      "concept": "lipopolysaccharide (LPS)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a direct variable for lipopolysaccharide administration."
    },
    {
      "concept": "progesterone",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the data source that captures progesterone administration."
    },
    {
      "concept": "neurogenesis",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a direct variable for neurogenesis."
    },
    {
      "concept": "microglia activation",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept of microglia activation assessed by Iba1 staining is a biological process that cannot be directly or indirectly measured in the National Fatality Review Case Reporting System (NFR-CRS) data."
    },
    {
      "concept": "cell death",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept of cell death assessed by cleaved caspase 3 (CC3) staining is a biological process that cannot be directly or indirectly measured in the National Fatality Review Case Reporting System (NFR-CRS) data."
    },
    {
      "concept": "glutamatergic transmission",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept of glutamatergic transmission assessed in the nucleus accumbens and amygdala is a biological process that cannot be directly or indirectly measured in the National Fatality Review Case Reporting System (NFR-CRS) data."
    },
    {
      "concept": "hypoglossal motor nucleus (XIIn)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept of hypoglossal motor nucleus assessed by electrophysiological recordings from brainstem slices is a biological process that cannot be directly or indirectly measured in the National Fatality Review Case Reporting System (NFR-CRS) data."
    },
    {
      "concept": "Postconceptional age (PCA)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that measures postconceptional age."
    },
    {
      "concept": "Breastfeeding status at discharge",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not include a variable that captures breastfeeding status at hospital discharge."
    },
    {
      "concept": "postconceptional age",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the data source that measures postconceptional age."
    },
    {
      "concept": "bed sharing",
      "source_id": "ncfrp_v51",
      "variable": "CIRsamesurf",
      "compatibility": "direct",
      "rationale": "The variable CIRsamesurf indicates whether the child was sleeping on the same surface with another person or animal, which is a direct measure of bed sharing."
    },
    {
      "concept": "PCA (postconceptional age)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the data source that measures postconceptional age."
    },
    {
      "concept": "chronological age",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable for chronological age measured in weeks."
    },
    {
      "concept": "Maternal prepregnancy body mass index (BMI)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain a variable that measures maternal BMI before pregnancy."
    },
    {
      "concept": "Maternal infections in pregnancy",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables for maternal infections such as chlamydia, gonorrhea, or hepatitis C during pregnancy."
    },
    {
      "concept": "inner ear dysfunction",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to inner ear dysfunction induced by gentamicin injections."
    },
    {
      "concept": "control condition",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the data source that captures a control condition such as intra-tympanic saline or intra-peritoneal gentamicin."
    },
    {
      "concept": "body movement arousal response to severe hypoxia-hypercarbia",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to body movement responses to hypoxia and hypercarbia."
    },
    {
      "concept": "hypercapnic ventilatory response",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the data source that measures the hypercapnic ventilatory response."
    },
    {
      "concept": "age of mice",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to the age of experimental animals such as mice."
    },
    {
      "concept": "baseline cSN activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the data source that captures baseline sympathetic nerve activity following CIH exposure."
    },
    {
      "concept": "breathing frequency",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to breathing frequency changes after chronic intermittent hypoxia."
    },
    {
      "concept": "expiratory time",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the data source that measures expiratory time following CIH exposure."
    },
    {
      "concept": "PiCo specific cholinergic-glutamatergic neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to the stimulation of PiCo-specific cholinergic-glutamatergic neurons."
    },
    {
      "concept": "glutamatergic PiCo neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the data source that captures glutamatergic PiCo neuron stimulation."
    },
    {
      "concept": "ChAT containing neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to ChAT-containing neuron stimulation."
    },
    {
      "concept": "Dbx1 and Vglut2 neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the data source that captures Dbx1 and Vglut2 neuron stimulation."
    },
    {
      "concept": "preBötzinger complex (preBötC)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to preBötzinger complex stimulation."
    },
    {
      "concept": "chronic intermittent hypoxia (CIH)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the data source that captures chronic intermittent hypoxia exposure."
    },
    {
      "concept": "diaphragm activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to diaphragm muscle activity changes."
    },
    {
      "concept": "vagus nerve activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the data source that measures vagal nerve activity changes."
    },
    {
      "concept": "cervical sympathetic nerve activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to cervical sympathetic nerve activity changes."
    },
    {
      "concept": "chronic intermittent hypoxia (IH)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the data source that captures chronic intermittent hypoxia exposure."
    },
    {
      "concept": "adult neurogenesis",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to adult neurogenesis measured by immunohistochemical experiments."
    },
    {
      "concept": "synaptic plasticity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the data source that measures synaptic plasticity through paired-pulse facilitation and LTP."
    },
    {
      "concept": "reactive oxygen species (ROS)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to reactive oxygen species measured by lipid peroxidation."
    },
    {
      "concept": "breathing patterns",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the data source that captures breathing patterns measured using plethysmography."
    },
    {
      "concept": "survival",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to survival rates in mice born prematurely or at term."
    },
    {
      "concept": "inhibition",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the data source that captures inhibition investigated using biophysical models and in vitro recordings."
    },
    {
      "concept": "excitation",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to excitation investigated using partial excitation block and in vitro recordings."
    },
    {
      "concept": "lipopolysaccharide (LPS)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the data source that captures lipopolysaccharide administration to pregnant dams."
    },
    {
      "concept": "progesterone",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not contain variables related to progesterone administration to pregnant dams."
    },
    {
      "concept": "neurogenesis",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the data source that captures neurogenesis assessed by Tbr2 intermediate neural progenitor cell density and BrdU labeling."
    },
    {
      "concept": "microglia activation",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP v5.1 data source does not contain any variables related to microglia activation or Iba1 staining."
    },
    {
      "concept": "cell death",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There are no variables in the NCFRP v5.1 data source that relate to cell death as assessed by cleaved caspase 3 (CC3) staining."
    },
    {
      "concept": "glutamatergic transmission",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP v5.1 data source does not contain any variables related to glutamatergic transmission in the nucleus accumbens and amygdala."
    },
    {
      "concept": "hypoglossal motor nucleus (XIIn)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP v5.1 data source does not contain any variables related to the hypoglossal motor nucleus or electrophysiological recordings from brainstem slices."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "CIR2dthlovedone",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxbullyvic",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxdrugalc",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxgaming",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxjobprob",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxmnyprob",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxnewschl",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxother",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxphysabs",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxprblaw",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxpregnant",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxsexabs",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxunk",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "Infant sex",
      "source_id": "ncfrp_v51",
      "variable": "RES2sex",
      "compatibility": "direct",
      "rationale": "The variables RES2sex and RES1sex directly capture the sex of individuals involved in the case, which can be used to infer infant sex."
    },
    {
      "concept": "Infant sex",
      "source_id": "ncfrp_v51",
      "variable": "RES1sex",
      "compatibility": "direct",
      "rationale": "The variables RES2sex and RES1sex directly capture the sex of individuals involved in the case, which can be used to infer infant sex."
    },
    {
      "concept": "Postconceptional age (PCA)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for postconceptional age."
    },
    {
      "concept": "Breastfeeding status at discharge",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the dataset that captures breastfeeding status at discharge."
    },
    {
      "concept": "postconceptional age",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for postconceptional age."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "ncfrp_v51",
      "variable": "RES2sex",
      "compatibility": "direct",
      "rationale": "The variables RES2sex and RES1sex directly capture the sex of individuals involved in the case."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "ncfrp_v51",
      "variable": "RES1sex",
      "compatibility": "direct",
      "rationale": "The variables RES2sex and RES1sex directly capture the sex of individuals involved in the case."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "CIR2dthlovedone",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxbullyvic",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxdrugalc",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxgaming",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxjobprob",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxmnyprob",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxnewschl",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxother",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxphysabs",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxprblaw",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxpregnant",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxsexabs",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "CIR2hxunk",
      "compatibility": "proxy",
      "rationale": "The variables listed above capture various risk factors and circumstances that may be associated with SUID but do not directly measure the outcome itself."
    },
    {
      "concept": "PCA (postconceptional age)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the dataset that captures postconceptional age."
    },
    {
      "concept": "chronological age",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for chronological age."
    },
    {
      "concept": "Maternal prepregnancy body mass index (BMI)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for maternal prepregnancy BMI."
    },
    {
      "concept": "Maternal infections in pregnancy",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for maternal infections during pregnancy."
    },
    {
      "concept": "inner ear dysfunction",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the dataset that captures inner ear dysfunction."
    },
    {
      "concept": "control condition",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for control conditions in experiments or studies."
    },
    {
      "concept": "body movement arousal response to severe hypoxia-hypercarbia",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the dataset that captures body movement arousal responses."
    },
    {
      "concept": "hypercapnic ventilatory response",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for hypercapnic ventilatory responses."
    },
    {
      "concept": "age of mice",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the dataset that captures age of mice used in experiments."
    },
    {
      "concept": "baseline cSN activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for baseline sympathetic nerve activity."
    },
    {
      "concept": "breathing frequency",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the dataset that captures breathing frequency."
    },
    {
      "concept": "expiratory time",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for expiratory time measurements."
    },
    {
      "concept": "PiCo specific cholinergic-glutamatergic neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the dataset that captures optogenetic stimulation of PiCo-specific neurons."
    },
    {
      "concept": "glutamatergic PiCo neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for glutamatergic PiCo neurons."
    },
    {
      "concept": "ChAT containing neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the dataset that captures ChAT-containing neurons."
    },
    {
      "concept": "Dbx1 and Vglut2 neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for Dbx1 and Vglut2 neurons."
    },
    {
      "concept": "preBötzinger complex (preBötC)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no variable in the dataset that captures preBötzinger complex."
    },
    {
      "concept": "chronic intermittent hypoxia (CIH)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for chronic intermittent hypoxia."
    },
    {
      "concept": "diaphragm activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the dataset that captures diaphragm muscle activity."
    },
    {
      "concept": "vagus nerve activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for vagal nerve activity."
    },
    {
      "concept": "cervical sympathetic nerve activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the dataset that captures cervical sympathetic nerve activity."
    },
    {
      "concept": "chronic intermittent hypoxia (IH)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for chronic intermittent hypoxia."
    },
    {
      "concept": "adult neurogenesis",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the dataset that captures adult neurogenesis."
    },
    {
      "concept": "synaptic plasticity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for synaptic plasticity."
    },
    {
      "concept": "reactive oxygen species (ROS)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the dataset that captures reactive oxygen species levels."
    },
    {
      "concept": "breathing patterns",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for breathing patterns in mice."
    },
    {
      "concept": "survival",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the dataset that captures survival rates of mice."
    },
    {
      "concept": "inhibition",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for inhibition in biophysical models or in vitro recordings."
    },
    {
      "concept": "excitation",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the dataset that captures excitation in biophysical models or in vitro recordings."
    },
    {
      "concept": "lipopolysaccharide (LPS)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for lipopolysaccharide administration."
    },
    {
      "concept": "progesterone",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "There is no specific variable in the dataset that captures progesterone administration."
    },
    {
      "concept": "neurogenesis",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The data source does not provide a variable for neurogenesis assessment."
    },
    {
      "concept": "microglia activation",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP v5.1 data source does not contain any variables related to microglia activation or Iba1 staining."
    },
    {
      "concept": "cell death",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP v5.1 data source does not contain any variables related to cell death or cleaved caspase 3 (CC3) staining."
    },
    {
      "concept": "glutamatergic transmission",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP v5.1 data source does not contain any variables related to glutamatergic transmission in the nucleus accumbens or amygdala."
    },
    {
      "concept": "hypoglossal motor nucleus (XIIn)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP v5.1 data source does not contain any variables related to the hypoglossal motor nucleus or electrophysiological recordings from brainstem slices."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "REVsuidirec",
      "compatibility": "direct",
      "rationale": "The REVsuidirec variable in the NCFRP data source directly captures SUID cases as per CDC's SUIDI Reporting Form."
    },
    {
      "concept": "Infant sex",
      "source_id": "ncfrp_v51",
      "variable": "INFgenderid",
      "compatibility": "direct",
      "rationale": "The INFgenderid variable in the NCFRP data source captures the gender identity of the infant, which can be used to determine infant sex."
    },
    {
      "concept": "Postconceptional age (PCA)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for postconceptional age. It is derived from gestational age and postnatal age, but these are separate variables."
    },
    {
      "concept": "Maternal smoking during pregnancy",
      "source_id": "ncfrp_v51",
      "variable": "INFsmanytime",
      "compatibility": "direct",
      "rationale": "The INFsmanytime variable in the NCFRP data source captures whether the mother smoked at any time during pregnancy."
    },
    {
      "concept": "Preterm birth",
      "source_id": "ncfrp_v51",
      "variable": "INFgestage",
      "compatibility": "proxy",
      "rationale": "The INFgestage variable captures gestational age in weeks, which can be used to determine if a birth is preterm (<37 weeks)."
    },
    {
      "concept": "Breastfeeding status at discharge",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for breastfeeding status at discharge."
    },
    {
      "concept": "postconceptional age",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for postconceptional age."
    },
    {
      "concept": "sex",
      "source_id": "ncfrp_v51",
      "variable": "INFgenderid",
      "compatibility": "direct",
      "rationale": "The INFgenderid variable captures the gender identity of the infant, which can be used to determine sex."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "REVsuidirec",
      "compatibility": "direct",
      "rationale": "The REVsuidirec variable captures SUID cases as per CDC's SUIDI Reporting Form."
    },
    {
      "concept": "birthweight",
      "source_id": "ncfrp_v51",
      "variable": "INFbirthwtcat",
      "compatibility": "proxy",
      "rationale": "The INFbirthwtcat variable captures birth weight categories, which can be used to stratify by low birth weight."
    },
    {
      "concept": "PCA (postconceptional age)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for postconceptional age."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "ncfrp_v51",
      "variable": "INFgenderid",
      "compatibility": "direct",
      "rationale": "The INFgenderid variable captures the gender identity of the infant, which can be used to determine sex."
    },
    {
      "concept": "birthweight (low, non-low)",
      "source_id": "ncfrp_v51",
      "variable": "INFbirthwtcat",
      "compatibility": "proxy",
      "rationale": "The INFbirthwtcat variable captures birth weight categories, which can be used to stratify by low birth weight."
    },
    {
      "concept": "maternal smoking status (smoking, non-smoking)",
      "source_id": "ncfrp_v51",
      "variable": "INFsmanytime",
      "compatibility": "direct",
      "rationale": "The INFsmanytime variable captures whether the mother smoked at any time during pregnancy."
    },
    {
      "concept": "Maternal prepregnancy body mass index (BMI)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for maternal prepregnancy BMI."
    },
    {
      "concept": "Gestational age at birth",
      "source_id": "ncfrp_v51",
      "variable": "INFgestage",
      "compatibility": "direct",
      "rationale": "The INFgestage variable captures gestational age in weeks, which is directly relevant to the concept."
    },
    {
      "concept": "Maternal infections in pregnancy",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for maternal infections in pregnancy."
    },
    {
      "concept": "inner ear dysfunction",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for inner ear dysfunction."
    },
    {
      "concept": "control condition",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for control conditions."
    },
    {
      "concept": "body movement arousal response to severe hypoxia-hypercarbia",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for body movement arousal responses."
    },
    {
      "concept": "hypercapnic ventilatory response",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for hypercapnic ventilatory responses."
    },
    {
      "concept": "age of mice",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for age of mice."
    },
    {
      "concept": "baseline cSN activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for baseline sympathetic nerve activity."
    },
    {
      "concept": "breathing frequency",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for breathing frequency."
    },
    {
      "concept": "expiratory time",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for expiratory time."
    },
    {
      "concept": "PiCo specific cholinergic-glutamatergic neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for PiCo-specific cholinergic-glutamatergic neurons."
    },
    {
      "concept": "glutamatergic PiCo neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for glutamatergic PiCo neurons."
    },
    {
      "concept": "ChAT containing neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for ChAT-containing neurons."
    },
    {
      "concept": "Dbx1 and Vglut2 neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for Dbx1 and Vglut2 neurons."
    },
    {
      "concept": "preBötzinger complex (preBötC)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for preBötzinger complex."
    },
    {
      "concept": "chronic intermittent hypoxia (CIH)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for chronic intermittent hypoxia."
    },
    {
      "concept": "adult neurogenesis",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for adult neurogenesis."
    },
    {
      "concept": "synaptic plasticity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for synaptic plasticity."
    },
    {
      "concept": "reactive oxygen species (ROS)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for reactive oxygen species."
    },
    {
      "concept": "breathing patterns",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for breathing patterns."
    },
    {
      "concept": "survival",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for survival rates in mice."
    },
    {
      "concept": "inhibition",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for inhibition."
    },
    {
      "concept": "excitation",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for excitation."
    },
    {
      "concept": "lipopolysaccharide (LPS)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for lipopolysaccharide."
    },
    {
      "concept": "progesterone",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for progesterone."
    },
    {
      "concept": "neurogenesis",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not have a direct variable for neurogenesis."
    },
    {
      "concept": "microglia activation",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept of microglia activation assessed by Iba1 staining is a cellular biology measure that does not have an equivalent in the National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1."
    },
    {
      "concept": "cell death",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept of cell death assessed by cleaved caspase 3 (CC3) staining is a cellular biology measure that does not have an equivalent in the National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1."
    },
    {
      "concept": "glutamatergic transmission",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept of glutamatergic transmission assessed in the nucleus accumbens and amygdala is a neuroscience measure that does not have an equivalent in the National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1."
    },
    {
      "concept": "hypoglossal motor nucleus (XIIn)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept of hypoglossal motor nucleus assessed by electrophysiological recordings from brainstem slices is a neuroscience measure that does not have an equivalent in the National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "ncfrp_v51",
      "variable": "ACTcausids",
      "compatibility": "direct",
      "rationale": "The variable ACTcausids in the NCFRP data source indicates prior SIDS deaths, which aligns with the concept of sudden unexpected infant death (SUID) as defined by ICD-10 codes R95 and R99."
    },
    {
      "concept": "Infant sex",
      "source_id": "ncfrp_v51",
      "variable": "ACTcausex",
      "compatibility": "direct",
      "rationale": "The variable ACTcausex in the NCFRP data source captures the sex of the person, which can be used to identify infant sex."
    },
    {
      "concept": "Postconceptional age (PCA)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for postconceptional age."
    },
    {
      "concept": "Breastfeeding status at discharge",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for breastfeeding status at discharge."
    },
    {
      "concept": "postconceptional age",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for postconceptional age."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "ncfrp_v51",
      "variable": "ACTcausex",
      "compatibility": "direct",
      "rationale": "The variable ACTcausex in the NCFRP data source captures the sex of the person, which can be used to identify infant sex."
    },
    {
      "concept": "SUID",
      "source_id": "ncfrp_v51",
      "variable": "ACTcausids",
      "compatibility": "direct",
      "rationale": "The variable ACTcausids in the NCFRP data source indicates prior SIDS deaths, which aligns with the concept of sudden unexpected infant death (SUID) as defined by ICD-10 codes R95 and R99."
    },
    {
      "concept": "PCA (postconceptional age)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for postconceptional age."
    },
    {
      "concept": "chronological age",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for chronological age."
    },
    {
      "concept": "Maternal prepregnancy body mass index (BMI)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for maternal prepregnancy BMI."
    },
    {
      "concept": "Maternal infections in pregnancy",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for maternal infections during pregnancy."
    },
    {
      "concept": "inner ear dysfunction",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for inner ear dysfunction."
    },
    {
      "concept": "control condition",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for control conditions in experiments."
    },
    {
      "concept": "body movement arousal response to severe hypoxia-hypercarbia",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for body movement arousal responses."
    },
    {
      "concept": "hypercapnic ventilatory response",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for hypercapnic ventilatory responses."
    },
    {
      "concept": "age of mice",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for the age of mice."
    },
    {
      "concept": "baseline cSN activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for baseline sympathetic nerve activity."
    },
    {
      "concept": "breathing frequency",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for breathing frequency."
    },
    {
      "concept": "expiratory time",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for expiratory time."
    },
    {
      "concept": "PiCo specific cholinergic-glutamatergic neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for PiCo-specific cholinergic-glutamatergic neurons."
    },
    {
      "concept": "glutamatergic PiCo neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for glutamatergic PiCo neurons."
    },
    {
      "concept": "ChAT containing neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for ChAT-containing neurons."
    },
    {
      "concept": "Dbx1 and Vglut2 neurons",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for Dbx1 and Vglut2 neurons."
    },
    {
      "concept": "preBötzinger complex (preBötC)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for the preBötzinger complex."
    },
    {
      "concept": "chronic intermittent hypoxia (CIH)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for chronic intermittent hypoxia."
    },
    {
      "concept": "diaphragm activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for diaphragm activity."
    },
    {
      "concept": "vagus nerve activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for vagus nerve activity."
    },
    {
      "concept": "cervical sympathetic nerve activity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for cervical sympathetic nerve activity."
    },
    {
      "concept": "chronic intermittent hypoxia (IH)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for chronic intermittent hypoxia."
    },
    {
      "concept": "adult neurogenesis",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for adult neurogenesis."
    },
    {
      "concept": "synaptic plasticity",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for synaptic plasticity."
    },
    {
      "concept": "reactive oxygen species (ROS)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for reactive oxygen species."
    },
    {
      "concept": "breathing patterns",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for breathing patterns."
    },
    {
      "concept": "survival",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for survival rates."
    },
    {
      "concept": "inhibition",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for inhibition."
    },
    {
      "concept": "excitation",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for excitation."
    },
    {
      "concept": "lipopolysaccharide (LPS)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for lipopolysaccharide exposure."
    },
    {
      "concept": "progesterone",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for progesterone exposure."
    },
    {
      "concept": "neurogenesis",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The NCFRP data source does not provide a variable for neurogenesis."
    },
    {
      "concept": "microglia activation",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept 'microglia activation' assessed by Iba1 staining is a biological measure that does not have an equivalent in the National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1."
    },
    {
      "concept": "cell death",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept 'cell death' assessed by cleaved caspase 3 (CC3) staining is a biological measure that does not have an equivalent in the National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1."
    },
    {
      "concept": "glutamatergic transmission",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept 'glutamatergic transmission' assessed in the nucleus accumbens and amygdala is a biological measure that does not have an equivalent in the National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1."
    },
    {
      "concept": "hypoglossal motor nucleus (XIIn)",
      "source_id": "ncfrp_v51",
      "variable": null,
      "compatibility": "none",
      "rationale": "The concept 'hypoglossal motor nucleus (XIIn)' assessed by electrophysiological recordings from brainstem slices is a biological measure that does not have an equivalent in the National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "The PRAMS data does not contain specific variables for SUID outcomes."
    },
    {
      "concept": "Infant sex",
      "source_id": "prams_p8_arf",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "Variable 'SEX' directly corresponds to the infant's gender, which is used as an exposure variable."
    },
    {
      "concept": "Postconceptional age (PCA)",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct measure of postconceptional age."
    },
    {
      "concept": "Maternal smoking during pregnancy",
      "source_id": "prams_p8_arf",
      "variable": "MOMSMOKE",
      "compatibility": "direct",
      "rationale": "Variable 'MOMSMOKE' indicates whether the mother smoked during pregnancy."
    },
    {
      "concept": "Preterm birth",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct measure of preterm birth status."
    },
    {
      "concept": "Breastfeeding status at discharge",
      "source_id": "prams_p8_arf",
      "variable": "BF5EVER_RAW",
      "compatibility": "direct",
      "rationale": "Variable 'BF5EVER_RAW' indicates whether the infant was breastfed ever."
    },
    {
      "concept": "postconceptional age",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct measure of postconceptional age."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "prams_p8_arf",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "Variable 'SEX' directly corresponds to the infant's gender."
    },
    {
      "concept": "year of birth or death",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct measure of year of birth or death."
    },
    {
      "concept": "SUID",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "The PRAMS data does not contain specific variables for SUID outcomes."
    },
    {
      "concept": "bed sharing",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct measure of bed-sharing behavior."
    },
    {
      "concept": "birthweight (low, non-low)",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct measure of birth weight categorized as low or non-low."
    },
    {
      "concept": "PCA (postconceptional age)",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct measure of postconceptional age."
    },
    {
      "concept": "chronological age",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct measure of chronological age."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "prams_p8_arf",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "Variable 'SEX' directly corresponds to the infant's gender."
    },
    {
      "concept": "birthweight (low, non-low)",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct measure of birth weight categorized as low or non-low."
    },
    {
      "concept": "maternal smoking status (smoking, non-smoking)",
      "source_id": "prams_p8_arf",
      "variable": "MOMSMOKE",
      "compatibility": "direct",
      "rationale": "Variable 'MOMSMOKE' indicates whether the mother smoked during pregnancy."
    },
    {
      "concept": "Maternal prepregnancy body mass index (BMI)",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct measure of maternal BMI."
    },
    {
      "concept": "Gestational age at birth",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct measure of gestational age at birth."
    },
    {
      "concept": "Maternal infections in pregnancy",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide specific variables for maternal infections during pregnancy."
    },
    {
      "concept": "Age of death in SUID cases",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "The PRAMS data does not contain specific variables for age at death in SUID cases."
    },
    {
      "concept": "Geographic location",
      "source_id": "prams_p8_arf",
      "variable": "STATE",
      "compatibility": "proxy",
      "rationale": "Variable 'STATE' provides the state of residence, which can be used as a proxy for geographic location."
    },
    {
      "concept": "inner ear dysfunction",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide any information on inner ear dysfunction."
    },
    {
      "concept": "control condition",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not contain variables related to control conditions in experiments."
    },
    {
      "concept": "body movement arousal response to severe hypoxia-hypercarbia",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables related to body movement responses to hypoxia-hypercarbia."
    },
    {
      "concept": "hypercapnic ventilatory response",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables related to hypercapnic ventilatory responses."
    },
    {
      "concept": "age of mice",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data is focused on human pregnancies and does not contain information about the age of mice."
    },
    {
      "concept": "baseline cSN activity",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not provide variables related to baseline sympathetic nerve activity in humans or mice."
    },
    {
      "concept": "breathing frequency",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain specific measures of breathing frequency."
    },
    {
      "concept": "expiratory time",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not provide variables related to expiratory times in humans or mice."
    },
    {
      "concept": "PiCo specific cholinergic-glutamatergic neurons",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not contain variables related to neuronal stimulation in mice."
    },
    {
      "concept": "glutamatergic PiCo neurons",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not contain variables related to neuronal stimulation in mice."
    },
    {
      "concept": "ChAT containing neurons",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not contain variables related to neuronal stimulation in mice."
    },
    {
      "concept": "Dbx1 and Vglut2 neurons",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not contain variables related to neuronal stimulation in mice."
    },
    {
      "concept": "preBötzinger complex (preBötC)",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not contain variables related to neuronal stimulation in mice."
    },
    {
      "concept": "chronic intermittent hypoxia (CIH)",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not contain variables related to chronic intermittent hypoxia in mice."
    },
    {
      "concept": "diaphragm activity",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not provide measures of diaphragm muscle activity."
    },
    {
      "concept": "vagus nerve activity",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not contain variables related to vagal nerve activity in humans or mice."
    },
    {
      "concept": "cervical sympathetic nerve activity",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not contain variables related to cervical sympathetic nerve activity in humans or mice."
    },
    {
      "concept": "chronic intermittent hypoxia (IH)",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not contain variables related to chronic intermittent hypoxia in mice."
    },
    {
      "concept": "adult neurogenesis",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not provide measures of adult neurogenesis in humans or mice."
    },
    {
      "concept": "synaptic plasticity",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not contain variables related to synaptic plasticity measures in humans or mice."
    },
    {
      "concept": "reactive oxygen species (ROS)",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not contain variables related to reactive oxygen species in humans or mice."
    },
    {
      "concept": "breathing patterns",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not provide measures of breathing patterns in newborns or mice."
    },
    {
      "concept": "survival",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not contain variables related to survival rates of mice in experiments."
    },
    {
      "concept": "inhibition",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not provide measures of inhibition in neuronal models or mice."
    },
    {
      "concept": "excitation",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not contain variables related to excitation measures in neuronal models or mice."
    },
    {
      "concept": "lipopolysaccharide (LPS)",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not contain variables related to LPS administration in mice."
    },
    {
      "concept": "progesterone",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not provide measures of progesterone administration to pregnant dams."
    },
    {
      "concept": "neurogenesis",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS data does not contain variables related to neurogenesis measures in mice."
    },
    {
      "concept": "microglia activation",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "The PRAMS Phase 8 Analytic Research File does not contain any variables related to microglia activation or Iba1 staining."
    },
    {
      "concept": "cell death",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "The PRAMS Phase 8 Analytic Research File does not contain any variables related to cell death or cleaved caspase 3 staining."
    },
    {
      "concept": "glutamatergic transmission",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "The PRAMS Phase 8 Analytic Research File does not contain any variables related to glutamatergic transmission in the nucleus accumbens or amygdala."
    },
    {
      "concept": "hypoglossal motor nucleus (XIIn)",
      "source_id": "prams_p8_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "The PRAMS Phase 8 Analytic Research File does not contain any variables related to the hypoglossal motor nucleus or electrophysiological recordings from brainstem slices."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "The PRAMS data source does not contain information on cause of death."
    },
    {
      "concept": "Infant sex",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide infant sex as a variable in the provided list."
    },
    {
      "concept": "Postconceptional age (PCA)",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide postconceptional age as a variable in the provided list."
    },
    {
      "concept": "Maternal smoking during pregnancy",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide maternal smoking status as a specific variable in the provided list."
    },
    {
      "concept": "Preterm birth",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide preterm birth information as a specific variable in the provided list."
    },
    {
      "concept": "Breastfeeding status at discharge",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide breastfeeding status at discharge as a specific variable in the provided list."
    },
    {
      "concept": "postconceptional age",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide postconceptional age as a specific variable in the provided list."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide infant sex information as a specific variable in the provided list."
    },
    {
      "concept": "year of birth or death",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide year of birth or death as a specific variable in the provided list."
    },
    {
      "concept": "SUID",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain information on cause of death or SUID."
    },
    {
      "concept": "bed sharing",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide bed-sharing status as a specific variable in the provided list."
    },
    {
      "concept": "birthweight (low, non-low)",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide birth weight information as a specific variable in the provided list."
    },
    {
      "concept": "PCA (postconceptional age)",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide postconceptional age as a specific variable in the provided list."
    },
    {
      "concept": "chronological age",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide chronological age information as a specific variable in the provided list."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide infant sex information as a specific variable in the provided list."
    },
    {
      "concept": "birthweight (low, non-low)",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide birth weight information as a specific variable in the provided list."
    },
    {
      "concept": "maternal smoking status (smoking, non-smoking)",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide maternal smoking status as a specific variable in the provided list."
    },
    {
      "concept": "Maternal prepregnancy body mass index (BMI)",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide maternal BMI information as a specific variable in the provided list."
    },
    {
      "concept": "Gestational age at birth",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide gestational age information as a specific variable in the provided list."
    },
    {
      "concept": "Maternal infections in pregnancy",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide maternal infection status as a specific variable in the provided list."
    },
    {
      "concept": "Age of death in SUID cases",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide age at death information as a specific variable in the provided list."
    },
    {
      "concept": "Geographic location",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide geographic location information as a specific variable in the provided list."
    },
    {
      "concept": "inner ear dysfunction",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain variables related to inner ear dysfunction."
    },
    {
      "concept": "control condition",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide information on control conditions for experiments."
    },
    {
      "concept": "body movement arousal response to severe hypoxia-hypercarbia",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide information on body movement responses to hypoxia or hypercarbia."
    },
    {
      "concept": "hypercapnic ventilatory response",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide information on ventilatory responses to hypercapnia."
    },
    {
      "concept": "age of mice",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain variables related to age of experimental animals."
    },
    {
      "concept": "baseline cSN activity",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide information on sympathetic nerve activity."
    },
    {
      "concept": "breathing frequency",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain variables related to breathing patterns or frequencies."
    },
    {
      "concept": "expiratory time",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide information on expiratory times."
    },
    {
      "concept": "PiCo specific cholinergic-glutamatergic neurons",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain variables related to neuronal stimulation or types."
    },
    {
      "concept": "glutamatergic PiCo neurons",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain variables related to neuronal stimulation or types."
    },
    {
      "concept": "ChAT containing neurons",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain variables related to neuronal stimulation or types."
    },
    {
      "concept": "Dbx1 and Vglut2 neurons",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain variables related to neuronal stimulation or types."
    },
    {
      "concept": "preBötzinger complex (preBötC)",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain variables related to neuronal stimulation or types."
    },
    {
      "concept": "chronic intermittent hypoxia (CIH)",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain variables related to chronic intermittent hypoxia."
    },
    {
      "concept": "diaphragm activity",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide information on diaphragm muscle activity."
    },
    {
      "concept": "vagus nerve activity",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain variables related to vagal nerve activity."
    },
    {
      "concept": "cervical sympathetic nerve activity",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide information on cervical sympathetic nerve activity."
    },
    {
      "concept": "chronic intermittent hypoxia (IH)",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain variables related to chronic intermittent hypoxia."
    },
    {
      "concept": "adult neurogenesis",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide information on adult neurogenesis."
    },
    {
      "concept": "synaptic plasticity",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain variables related to synaptic plasticity."
    },
    {
      "concept": "reactive oxygen species (ROS)",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide information on reactive oxygen species levels."
    },
    {
      "concept": "breathing patterns",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain variables related to breathing patterns in mice."
    },
    {
      "concept": "survival",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide information on survival rates of experimental animals."
    },
    {
      "concept": "inhibition",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain variables related to inhibition in neuronal models."
    },
    {
      "concept": "excitation",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain variables related to excitation in neuronal models."
    },
    {
      "concept": "lipopolysaccharide (LPS)",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide information on LPS administration to pregnant dams."
    },
    {
      "concept": "progesterone",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain variables related to progesterone administration."
    },
    {
      "concept": "neurogenesis",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide information on neurogenesis in experimental models."
    },
    {
      "concept": "microglia activation",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "The PRAMS Phase 8 Standard Section II codebook does not contain any variables related to microglia activation or Iba1 staining."
    },
    {
      "concept": "cell death",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "The PRAMS Phase 8 Standard Section II codebook does not contain any variables related to cell death or cleaved caspase 3 (CC3) staining."
    },
    {
      "concept": "glutamatergic transmission",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "The PRAMS Phase 8 Standard Section II codebook does not contain any variables related to glutamatergic transmission in the nucleus accumbens or amygdala."
    },
    {
      "concept": "hypoglossal motor nucleus (XIIn)",
      "source_id": "prams_p8_std2",
      "variable": null,
      "compatibility": "none",
      "rationale": "The PRAMS Phase 8 Standard Section II codebook does not contain any variables related to the hypoglossal motor nucleus or electrophysiological recordings from brainstem slices."
    },
    {
      "concept": "Sudden unexpected infant death (SUID)",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "The PRAMS data does not contain specific variables for SUID outcomes."
    },
    {
      "concept": "Infant sex",
      "source_id": "prams_p7_arf",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "The variable 'SEX' directly corresponds to the infant's gender, which is a direct measure of infant sex."
    },
    {
      "concept": "Postconceptional age (PCA)",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables to calculate postconceptional age directly."
    },
    {
      "concept": "Maternal smoking during pregnancy",
      "source_id": "prams_p7_arf",
      "variable": "MOMSMOKE",
      "compatibility": "direct",
      "rationale": "The variable 'MOMSMOKE' indicates whether the mother smoked during any trimester of pregnancy."
    },
    {
      "concept": "Preterm birth",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct variable for preterm birth status; it would need to be derived from gestational age."
    },
    {
      "concept": "Breastfeeding status at discharge",
      "source_id": "prams_p7_arf",
      "variable": "BF5EVER_RAW",
      "compatibility": "proxy",
      "rationale": "The variable 'BF5EVER_RAW' indicates whether the infant was breastfed ever, which can be used as a proxy for breastfeeding status at discharge."
    },
    {
      "concept": "postconceptional age",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables to calculate postconceptional age directly."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "prams_p7_arf",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "The variable 'SEX' indicates the sex of the infant as male or female."
    },
    {
      "concept": "year of birth or death",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct variable for year of birth or death; it would need to be derived from other variables."
    },
    {
      "concept": "SUID",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain specific variables for SUID outcomes."
    },
    {
      "concept": "bed sharing",
      "source_id": "prams_p7_arf",
      "variable": "SLEEPPOS_RAW",
      "compatibility": "proxy",
      "rationale": "The variable 'SLEEPPOS_RAW' indicates the sleeping position of the baby, which can be used as a proxy for bed-sharing behavior."
    },
    {
      "concept": "birthweight (low, non-low)",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct variable for birth weight status; it would need to be derived from other variables."
    },
    {
      "concept": "PCA (postconceptional age)",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables to calculate postconceptional age directly."
    },
    {
      "concept": "chronological age",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct variable for chronological age; it would need to be derived from other variables."
    },
    {
      "concept": "sex (male, female)",
      "source_id": "prams_p7_arf",
      "variable": "SEX",
      "compatibility": "direct",
      "rationale": "The variable 'SEX' indicates the sex of the infant as male or female."
    },
    {
      "concept": "birthweight (low, non-low)",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct variable for birth weight status; it would need to be derived from other variables."
    },
    {
      "concept": "maternal smoking status (smoking, non-smoking)",
      "source_id": "prams_p7_arf",
      "variable": "MOMSMOKE",
      "compatibility": "direct",
      "rationale": "The variable 'MOMSMOKE' indicates whether the mother smoked during pregnancy."
    },
    {
      "concept": "Maternal prepregnancy body mass index (BMI)",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct variable for maternal BMI; it would need to be derived from height and weight."
    },
    {
      "concept": "Gestational age at birth",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide a direct variable for gestational age; it would need to be derived from other variables."
    },
    {
      "concept": "Maternal infections in pregnancy",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide specific variables for maternal infections during pregnancy."
    },
    {
      "concept": "Age of death in SUID cases",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain specific variables for age at death in SUID cases."
    },
    {
      "concept": "Geographic location",
      "source_id": "prams_p7_arf",
      "variable": "STATE",
      "compatibility": "proxy",
      "rationale": "The variable 'STATE' indicates the state of residence, which can be used as a proxy for geographic location."
    },
    {
      "concept": "inner ear dysfunction",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables related to inner ear dysfunction."
    },
    {
      "concept": "control condition",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain specific variables for control conditions in experimental studies."
    },
    {
      "concept": "body movement arousal response to severe hypoxia-hypercarbia",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables related to body movement responses to hypoxia-hypercarbia."
    },
    {
      "concept": "hypercapnic ventilatory response",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables related to hypercapnic ventilatory responses."
    },
    {
      "concept": "age of mice",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain specific variables for age in animal studies."
    },
    {
      "concept": "baseline cSN activity",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables related to baseline sympathetic nerve activity."
    },
    {
      "concept": "breathing frequency",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain specific variables for breathing frequency in infants."
    },
    {
      "concept": "expiratory time",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables related to expiratory times."
    },
    {
      "concept": "PiCo specific cholinergic-glutamatergic neurons",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain variables related to neuronal stimulation in experimental studies."
    },
    {
      "concept": "glutamatergic PiCo neurons",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables related to neuronal stimulation in experimental studies."
    },
    {
      "concept": "ChAT containing neurons",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain specific variables for neuronal types or stimulations."
    },
    {
      "concept": "Dbx1 and Vglut2 neurons",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables related to neuronal types or stimulations."
    },
    {
      "concept": "preBötzinger complex (preBötC)",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain specific variables for neuronal stimulation in experimental studies."
    },
    {
      "concept": "chronic intermittent hypoxia (CIH)",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables related to chronic intermittent hypoxia exposure."
    },
    {
      "concept": "diaphragm activity",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain specific variables for diaphragm muscle activity."
    },
    {
      "concept": "vagus nerve activity",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables related to vagal nerve activity."
    },
    {
      "concept": "cervical sympathetic nerve activity",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain specific variables for cervical sympathetic nerve activity."
    },
    {
      "concept": "chronic intermittent hypoxia (IH)",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables related to chronic intermittent hypoxia exposure."
    },
    {
      "concept": "adult neurogenesis",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain specific variables for adult neurogenesis measures."
    },
    {
      "concept": "synaptic plasticity",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables related to synaptic plasticity assessments."
    },
    {
      "concept": "reactive oxygen species (ROS)",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain specific variables for reactive oxygen species measures."
    },
    {
      "concept": "breathing patterns",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables related to breathing patterns in infants."
    },
    {
      "concept": "survival",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain specific variables for survival outcomes in animal studies."
    },
    {
      "concept": "inhibition",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables related to inhibition measures in neuronal studies."
    },
    {
      "concept": "excitation",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain specific variables for excitation measures in neuronal studies."
    },
    {
      "concept": "lipopolysaccharide (LPS)",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables related to LPS administration in animal studies."
    },
    {
      "concept": "progesterone",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not contain specific variables for progesterone administration in animal studies."
    },
    {
      "concept": "neurogenesis",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "PRAMS does not provide variables related to neurogenesis measures."
    },
    {
      "concept": "microglia activation",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "The PRAMS Phase 7 Analytic Research File does not contain any variables related to microglia activation or Iba1 staining."
    },
    {
      "concept": "cell death",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "The PRAMS Phase 7 Analytic Research File does not contain any variables related to cell death or cleaved caspase 3 (CC3) staining."
    },
    {
      "concept": "glutamatergic transmission",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "The PRAMS Phase 7 Analytic Research File does not contain any variables related to glutamatergic transmission in the nucleus accumbens or amygdala."
    },
    {
      "concept": "hypoglossal motor nucleus (XIIn)",
      "source_id": "prams_p7_arf",
      "variable": null,
      "compatibility": "none",
      "rationale": "The PRAMS Phase 7 Analytic Research File does not contain any variables related to electrophysiological recordings from the hypoglossal motor nucleus (XIIn)."
    }
  ],
  "source_summaries": {
    "cdc_linkco15": "This dataset provides detailed information on infant deaths and their causes, including SUID. It includes variables such as sex of the infant, gestational age at birth, maternal smoking status during pregnancy, preterm birth indicators, breastfeeding status, and geographic location. However, it lacks specific variables for experimental conditions like chronic intermittent hypoxia or neurogenesis. This data source contains information about births and infant deaths, including demographic details of mothers and infants, prenatal care, delivery characteristics, neonatal conditions, and causes of death. It does not include any variables related to cellular or molecular biology outcomes such as microglia activation, cell death, glutamatergic transmission, or electrophysiological recordings from specific brain regions.",
    "cdc_natl15": "The CDC natality public-use file provides detailed information on births, including infant sex (SEX), gestational age at birth (COMBGEST), and maternal smoking during pregnancy (CIG_REC). However, it lacks specific variables for SUID outcomes, bed sharing behavior, and other physiological measures such as body movement arousal responses or neurogenesis. Variables like preterm birth (GESTREC3) and breastfeeding status at discharge (BFED) are available but may require additional interpretation to align with the manuscript's concepts. The CDC natality public-use file contains variables related to demographic, socioeconomic, and health-related factors of births. It does not include biological or neurological measures such as microglia activation, cell death, glutamatergic transmission, or electrophysiological assessments of the hypoglossal motor nucleus.",
    "cdc_codenames": "The CDC birth/death file provides detailed information on infant characteristics, maternal health behaviors, and pregnancy outcomes. However, it lacks specific variables related to SUID definitions based on ICD-10 codes, postconceptional age, bed sharing, inner ear dysfunction, neuronal stimulation, chronic intermittent hypoxia exposure, breathing patterns, survival rates, inhibition/excitation measures, lipopolysaccharide administration, progesterone treatment, and neurogenesis. Variables for maternal smoking status, preterm birth, breastfeeding status at discharge, and geographic location are available but may require recoding or derivation. This data source contains variables related to newborn health, maternal and paternal characteristics, prenatal care, delivery methods, and other demographic factors. It lacks any variables pertaining to biological measurements such as microglia activation, cell death, glutamatergic transmission, or electrophysiological recordings from brainstem slices.",
    "ncfrp_v51": "The National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1 provides detailed information on infant deaths, including demographic data and medical history. It includes variables such as sex, birth weight category, days lived, and prenatal care details but lacks specific measures for postconceptional age, maternal smoking during pregnancy, preterm birth status, breastfeeding at discharge, gestational age at birth, maternal infections in pregnancy, chronic intermittent hypoxia, and other physiological measurements relevant to the manuscript concepts. The National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1 primarily documents demographic, social, and medical history information about deceased children and their families. It includes data on prenatal care, birth outcomes, child maltreatment histories, and other factors related to the circumstances of death but does not contain biological or neurological measurements relevant to concepts such as microglia activation, cell death, glutamatergic transmission, or hypoglossal motor nucleus activity. The National Fatality Review Case Reporting System (NFR-CRS) codebook version 5.1 provides detailed information on infant deaths, including cause of death codes and maternal health factors. However, it lacks specific variables for postconceptional age, infant sex, maternal smoking status during pregnancy, preterm birth status, breastfeeding status at discharge, bed sharing, birth weight categorized as low or non-low, gestational age, maternal infections such as chlamydia, gonorrhea, and hepatitis C, age of death in SUID cases, geographic location, inner ear dysfunction, control conditions, body movement arousal response to severe hypoxia-hypercarbia, hypercapnic ventilatory response, age of mice, baseline cSN activity, breathing frequency, expiratory time, PiCo specific cholinergic-glutamatergic neurons, glutamatergic PiCo neurons, ChAT containing neurons, Dbx1 and Vglut2 neurons, preBötzinger complex (preBötC), chronic intermittent hypoxia (CIH/IH), diaphragm activity, vagus nerve activity, cervical sympathetic nerve activity, adult neurogenesis, synaptic plasticity, reactive oxygen species (ROS), breathing patterns, survival, inhibition, excitation, lipopolysaccharide (LPS), and progesterone. This data source focuses on maternal and infant health complications, prenatal care, delivery outcomes, and social determinants of health. It does not contain variables related to neurobiological processes such as microglia activation, cell death, glutamatergic transmission, or electrophysiological assessments of the hypoglossal motor nucleus. This dataset primarily focuses on social and demographic factors of individuals involved in fatality cases, including biological parents, caregivers, supervisors, and incident details. It lacks specific medical or physiological data relevant to SUID, postconceptional age, birth weight, maternal smoking status, gestational age at birth, infections during pregnancy, inner ear dysfunction, neurogenesis, synaptic plasticity, reactive oxygen species levels, breathing patterns, survival rates of experimental animals, lipopolysaccharide (LPS) administration, and progesterone exposure. The dataset does provide information on geographic location through state and county variables. This dataset focuses on social services, substance abuse history, criminal background, disability status, and other demographic information related to caregivers and biological parents involved in child fatalities. It does not contain any variables that directly or indirectly measure microglia activation, cell death, glutamatergic transmission, or hypoglossal motor nucleus activity. This dataset primarily focuses on the causes and circumstances of sudden unexpected infant deaths (SUID) as reported in death certificates. It includes variables such as immediate cause of death, scene recreation details, toxicology screens, and other relevant factors that may contribute to SUID cases. However, it lacks specific variables for postconceptional age, maternal smoking status during pregnancy, preterm birth status, breastfeeding at discharge, geographic location, and various physiological measures related to experimental studies on respiratory-sympathetic coupling or neurogenesis. The National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1 does not contain any variables that can be used to assess biological processes such as microglia activation, cell death, glutamatergic transmission, or hypoglossal motor nucleus activity. The data focuses on factors related to the circumstances of child fatalities and includes information about incidents, injuries, environmental conditions, and substance use but does not cover cellular or molecular biology. The National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1 primarily focuses on documenting the circumstances surrounding sudden unexpected infant deaths, including environmental factors, substance exposures, medical conditions, and potential acts of abuse or neglect. It does not provide detailed information on postconceptional age, maternal smoking during pregnancy, preterm birth status, breastfeeding at discharge, specific genetic or neurological assessments, nor variables related to experimental procedures in animal models. This dataset focuses on fatality review cases and includes information about substances involved, medical conditions, symptoms, diagnoses, treatments, and circumstances of death. It does not contain variables related to cellular or neurological processes such as microglia activation, cell death, glutamatergic transmission, or hypoglossal motor nucleus activity. This dataset primarily focuses on child fatality reviews and captures various aspects of the circumstances surrounding deaths, including risk factors, protective factors, and services provided. It includes variables related to substance abuse history, criminal background, disability or chronic illness status, and prior death records for individuals involved in cases. However, it lacks specific variables for postconceptional age, maternal smoking during pregnancy, preterm birth, breastfeeding status at discharge, gestational age at birth, inner ear dysfunction, body movement arousal responses to hypoxia-hypercarbia, hypercapnic ventilatory response, chronic intermittent hypoxia, diaphragm activity, vagus nerve activity, cervical sympathetic nerve activity, adult neurogenesis, synaptic plasticity, reactive oxygen species levels, breathing patterns in mice, survival rates of mice, inhibition and excitation in biophysical models or in vitro recordings, lipopolysaccharide administration, progesterone administration, and neurogenesis assessment. This dataset focuses on child fatality reviews and includes information about the circumstances of death, contributing factors, and actions taken by various agencies. It does not contain any variables related to neurological or cellular processes such as microglia activation, cell death, glutamatergic transmission, or hypoglossal motor nucleus activity. The National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1 provides detailed information on sudden unexpected infant deaths, including variables related to the infant's sex and birth weight, maternal smoking during pregnancy, gestational age at birth, and SUID cases as per CDC’s SUIDI Reporting Form. However, it lacks direct variables for postconceptional age, bed sharing, geographic location, specific physiological responses, and experimental conditions involving mice or neurogenesis. The National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1 does not contain variables that directly or indirectly measure cellular biology outcomes such as microglia activation, cell death, glutamatergic transmission, and electrophysiological assessments of the hypoglossal motor nucleus. The data sources are focused on social, medical, and environmental factors related to infant deaths. The National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1 provides detailed information on the circumstances surrounding sudden infant deaths, including demographic data and potential risk factors such as substance abuse history and child maltreatment. However, it lacks specific variables for postconceptional age, maternal smoking status during pregnancy, preterm birth status, breastfeeding at discharge, geographic location, and various physiological measures relevant to experimental studies. The National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1 does not contain variables that can be used to assess biological outcomes such as microglia activation, cell death, glutamatergic transmission, or electrophysiological measures of the hypoglossal motor nucleus. The data sources in this system are primarily focused on sociological and legal aspects related to child fatalities and do not include any biological measurements.",
    "prams_p8_arf": "The PRAMS Phase 8 Analytic Research File (ARF) provides detailed information on maternal health behaviors and pregnancy outcomes. It includes variables such as smoking during pregnancy, preterm birth indicators, breastfeeding status, and infant sex but lacks specific measures for SUID, postconceptional age, bed sharing, geographic location beyond state-level data, and other biological or experimental parameters related to mice or neuronal activity. PRAMS Phase 8 Analytic Research File contains data on health behaviors and experiences of women during pregnancy and after childbirth. It includes variables related to maternal health, prenatal care, infant health, and socioeconomic factors but does not contain any information relevant to the concepts of microglia activation, cell death, glutamatergic transmission, or hypoglossal motor nucleus.",
    "prams_p8_std2": "The PRAMS Phase 8 Standard Section II codebook provides variables related to maternal health and pregnancy outcomes but lacks specific data on infant death, postconceptional age, bed sharing, infections during pregnancy, neurophysiological measures, or experimental conditions involving mice. The dataset is primarily focused on maternal behaviors and risk factors for adverse birth outcomes. This data source, PRAMS Phase 8 Standard Section II codebook, contains information on pregnancy weight gain and its units. It does not contain any variables related to biological outcomes such as microglia activation, cell death, glutamatergic transmission, or electrophysiological recordings from the hypoglossal motor nucleus.",
    "prams_p7_arf": "The PRAMS Phase 7 Analytic Research File provides detailed information on maternal health behaviors and pregnancy outcomes, but lacks specific variables for SUID outcomes, postconceptional age, gestational age at birth, and other physiological measures relevant to the concepts listed. Variables such as infant sex (SEX), maternal smoking during pregnancy (MOMSMOKE), and breastfeeding status at discharge (BF5EVER_RAW) are available but may require additional context or proxy variables for accurate interpretation. PRAMS Phase 7 Analytic Research File contains data primarily focused on maternal health, prenatal care, and infant outcomes. It includes variables related to insurance coverage, pre-pregnancy health conditions, behaviors during pregnancy (e.g., smoking, alcohol consumption), and postpartum health status but does not include any information relevant to the concepts of microglia activation, cell death, glutamatergic transmission, or hypoglossal motor nucleus electrophysiological recordings."
  }
}
```
