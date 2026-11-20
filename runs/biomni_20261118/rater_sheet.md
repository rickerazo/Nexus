# Blinded rater sheet

Rate each question with the rubric in docs/plans/2026-11-18-biomni-benchmark.md.

## Q499

- **Question:** Is there an association between maternal smoking during pregnancy and incidence rates of SUID at different postconceptional age stages?
- **Sources:** case: cdc_linkco15; reference: prams_p8_arf, prams_p7_arf; denominator: cdc_natl15; years 2016–2021
- **Variables:** cdc_linkco15:MATSMKNG; prams_p8_arf:MATSMKNG; prams_p7_arf:MATSMKNG; cdc_natl15:LIVEBIRTH
- **Rationale:** Identifying if smoking poses varying risks based on developmental milestones can inform targeted interventions.
- **Prior art:** While the manuscript examines overall effects, it does not stratify by postconceptional age. Literature abstracts also do not focus on this detail.
- **Cannot establish:** It cannot determine causation but can identify associations.

## Q247

- **Question:** Does socioeconomic status play a role in the incidence of SUID?
- **Sources:** case: ncfrp_v51; reference: prams_p7_arf, prams_p8_arf; denominator: cdc_linkco15; years 2016–2019
- **Variables:** prams_p8_std2:SOCIOECONOMIC_STATUS
- **Rationale:** Does socioeconomic status play a role in the incidence of SUID?
- **Prior art:** The closest work is the manuscript on developmental timing of SUID and bed sharing, which did not explore SOCIOECONOMIC_STATUS.
- **Cannot establish:**

## Q319

- **Question:** The proportion of mothers with pre-pregnancy hypertension among SUID cases is higher compared to the weighted prevalence in the general population.
- **Sources:** case: cdc_linkco15, ncfrp_v51; reference: prams_p7_arf, prams_p8_arf; years 2012–2021
- **Variables:** cdc_linkco15:RF_PHYPE; cdc_linkco15:RF_PDIAB; ncfrp_v51:ISSprechronicdiseasebef; prams_p7_arf:WTANAL; prams_p8_arf:WTANAL; prams_p7_arf:PRE_CKBP; prams_p8_arf:RF_PHYPE
- **Rationale:** This study aims to compare the prevalence of maternal pre-pregnancy health conditions between SUID cases and a representative sample of the general population. The design uses case-population comparison, which can establish whether there is an association but not causality or incidence rates.
- **Prior art:** suid_literature_abstracts.C10 suggests that maternal obesity increases SUID risk, but no research has systematically analyzed prepregnancy health conditions and their influence on SUID incidence. This study aims to fill this gap by focusing specifically on pre-pregnancy maternal health conditions.
- **Cannot establish:** The design cannot establish causality or incidence rates; it can only compare proportions between cases and a population reference.

## Q697

- **Question:** How does preterm birth influence the incidence rate of SUID across different postconceptional age intervals?
- **Sources:** case: cdc_linkco15; denominator: cdc_natl15; years 2016–2021
- **Variables:** cdc_linkco15:GESTWK; cdc_natl15:LIVEBIRTH
- **Rationale:** Determining if prematurity affects risk differently depending on developmental timing can improve targeted prevention strategies.
- **Prior art:** The manuscript touches upon this but does not provide detailed analysis by specific postconceptional ages. Literature abstracts also lack focus here.
- **Cannot establish:** It cannot establish causation without further experimental designs.

## Q337

- **Question:** Is there an association between maternal smoking during pregnancy and SUID incidence?
- **Sources:** case: cdc_linkco15; reference: ncfrp_v51; denominator: cdc_linkco15; years 2016–2020
- **Variables:** cdc_linkco15:SMOKING; ncfrp_v51:MOM_SMOKE
- **Rationale:** Maternal smoking is known to be a risk factor for several adverse health outcomes in infants.
- **Prior art:** No similar work found in existing literature focusing specifically on this relationship using the available data sources.
- **Cannot establish:** Cannot establish causality without additional longitudinal data.

## Q209

- **Question:** Is there an association between maternal alcohol use during pregnancy and SUID incidence?
- **Sources:** case: cdc_linkco15; denominator: cdc_linkco15; years 2016–2020
- **Variables:** cdc_linkco15:MATHEALTH
- **Rationale:** Maternal alcohol consumption can impact fetal development.
- **Prior art:** No similar work found in existing literature focusing specifically on this relationship using the available data sources.
- **Cannot establish:** Cannot establish causality without additional longitudinal data.

## Q605

- **Question:** Does infant feeding method impact SUID incidence?
- **Sources:** case: cdc_linkco15; denominator: cdc_linkco15; years 2016–2020
- **Variables:** cdc_linkco15:INFANTFEED
- **Rationale:** Infant feeding methods can influence nutrition and health outcomes.
- **Prior art:** No similar work found in existing literature focusing specifically on this relationship using the available data sources.
- **Cannot establish:** Cannot establish causality without additional longitudinal data.

## Q537

- **Question:** The proportion of SUID cases among infants born to mothers with different pre-pregnancy health behaviors and conditions varies.
- **Sources:** case: ncfrp_v51; reference: prams_p7_arf, prams_p8_arf; denominator: cdc_natl15; years 2008–2021
- **Variables:** ncfrp_v51:INFfirsttricig; prams_p8_arf:MOMCIG; prams_p7_arf:CIG_PRIOR; prams_p8_arf:WTANAL; prams_p7_arf:WTANAL; prams_p8_arf:PRE_LB_NAPHSIS; prams_p7_arf:PRE_LB_NAPHSIS; prams_p8_arf:MM_NOMD; prams_p7_arf:MM_NOMD
- **Rationale:** This study design uses the case series (ncfrp_v51) for numerator, population reference (prams_p7_arf, prams_p8_arf) for exposure prevalence, and denominator source (cdc_natl15) to estimate live births stratified by maternal pre-pregnancy health behaviors. The design can identify associations but cannot establish causation or fully control for confounding variables.
- **Prior art:** SUID_manuscript_v9_clean.C9 suggests an association between maternal smoking and higher SUID incidence, but does not address pre-pregnancy behaviors comprehensively.
- **Cannot establish:** Causality, individual-level linkage between case series and population reference datasets.

## Q321

- **Question:** Does prematurity influence SUID incidence?
- **Sources:** case: cdc_linkco15; denominator: cdc_linkco15; years 2016–2020
- **Variables:** cdc_linkco15:PREMATURITY
- **Rationale:** Premature birth is known to be associated with various health complications, including respiratory issues.
- **Prior art:** No similar work found in existing literature focusing specifically on this relationship using the available data sources.
- **Cannot establish:** Cannot establish causality without additional longitudinal data.

## Q152

- **Question:** Does prenatal care influence SUID incidence?
- **Sources:** case: cdc_linkco15; denominator: cdc_linkco15; years 2016–2020
- **Variables:** cdc_linkco15:PREGCARE
- **Rationale:** Prenatal care can affect the health of both mother and infant.
- **Prior art:** No similar work found in existing literature focusing specifically on this relationship using the available data sources.
- **Cannot establish:** Cannot establish causality without additional longitudinal data.

## Q978

- **Question:** The proportion of mothers who had pre-pregnancy health checks for chronic diseases, high blood pressure, diabetes, and depression/anxiety is compared between SUID cases and PRAMS mothers from 2012-2015.
- **Sources:** case: ncfrp_v51; reference: prams_p7_arf; years 2012–2015
- **Variables:** ncfrp_v51:ISSprechronicdiseasebef; ncfrp_v51:ISSprechronicdiseasedur; prams_p7_arf:PRE_CKBP; prams_p7_arf:PRE_CKD; prams_p7_arf:PRE_DEPR; prams_p7_arf:WTANAL
- **Rationale:** This study design compares the use of pre-pregnancy health checks between SUID cases and a population reference using available data sources. The variables are measurable in both datasets, allowing for a valid comparison.
- **Prior art:** None in the inputs; existing manuscripts focus on developmental windows, bed sharing, smoking during pregnancy, and prematurity but do not address pre-pregnancy health checks specifically.
- **Cannot establish:** The design cannot establish causality or incidence rates; it can only compare proportions of pre-pregnancy health checks between SUID cases and the general population.

## Q576

- **Question:** Is preterm birth associated with an increased risk of SUID?
- **Sources:** case: ncfrp_v51; reference: prams_p7_arf, prams_p8_arf; denominator: cdc_linkco15; years 2016–2019
- **Variables:** ncfrp_v51:PRETERM_BIRTH; prams_p7_arf:GESTATIONAL_AGE
- **Rationale:** Is preterm birth associated with an increased risk of SUID?
- **Prior art:** The closest work is the manuscript on developmental timing of SUID and bed sharing, which did not explore PRETERM_BIRTH, GESTATIONAL_AGE.
- **Cannot establish:**

## Q284

- **Question:** Is there an association between maternal education and SUID incidence?
- **Sources:** case: cdc_linkco15; denominator: cdc_linkco15; years 2016–2020
- **Variables:** cdc_linkco15:MOMEDU
- **Rationale:** Maternal education is linked to access to healthcare and environmental factors.
- **Prior art:** No similar work found in existing literature focusing specifically on this relationship using the available data sources.
- **Cannot establish:** Cannot establish causality without additional longitudinal data.

## Q939

- **Question:** Is there an association between socioeconomic status and SUID incidence?
- **Sources:** case: cdc_linkco15; denominator: cdc_linkco15; years 2016–2020
- **Variables:** cdc_linkco15:SES
- **Rationale:** Socioeconomic factors may influence access to healthcare and environmental risks.
- **Prior art:** No similar work found in existing literature focusing specifically on this relationship using the available data sources.
- **Cannot establish:** Cannot establish causality without additional longitudinal data.

## Q673

- **Question:** The proportion of mothers reporting Medicaid coverage differs between PRAMS Phase 7 and Phase 8.
- **Sources:** reference: prams_p7_arf, prams_p8_arf; years 2012–2021
- **Variables:** prams_p7_arf:PP_MEDIC; prams_p8_arf:PP_MEDIC_RAW; prams_p7_arf:WTANAL; prams_p8_arf:WTANAL
- **Rationale:** This design compares how insurance coverage documentation has changed over time, focusing on the differences in proportions reported by mothers in PRAMS Phase 7 (2012-2015) versus Phase 8 (2016-2021).
- **Prior art:** The SUID manuscript claims C6 and C9 discuss maternal smoking as a risk factor but do not address changes in insurance coverage documentation over time, leaving this question open.
- **Cannot establish:** incidence or risk, only proportions among cases.

## Q361

- **Question:** The proportion of mothers reporting smoking during pregnancy differs between PRAMS Phase 7 and Phase 8.
- **Sources:** reference: prams_p8_arf, prams_p7_arf; years 2012–2021
- **Variables:** prams_p8_arf:CIG_PRIOR; prams_p8_arf:MOMSMOKE; prams_p7_arf:CIG_PRIOR; prams_p7_arf:MOMSMOKE; prams_p8_arf:WTANAL; prams_p7_arf:WTANAL
- **Rationale:** This design fits the available sources and can compare how maternal smoking is recorded differently in PRAMS Phase 7 versus Phase 8. The study aims to understand potential biases introduced by changes in measurement methods over different phases.
- **Prior art:** SUID_manuscript_v9_clean.C10 and bedsharing_ms_v7.C23 both mention the impact of missing maternal smoking data, but do not address differences between PRAMS phases, leaving this question open.
- **Cannot establish:** incidence or risk, only proportions among cases.

## Q736

- **Question:** Does maternal smoking during pregnancy increase the risk of SUID?
- **Sources:** case: ncfrp_v51; reference: prams_p7_arf, prams_p8_arf; denominator: cdc_linkco15; years 2016–2019
- **Variables:** ncfrp_v51:MATERNAL_SMOKING_DURING_PREGNANCY; prams_p7_arf:MATERNAL_SMOKING
- **Rationale:** Does maternal smoking during pregnancy increase the risk of SUID?
- **Prior art:** The closest work is the manuscript on developmental timing of SUID and bed sharing, which did not explore MATERNAL_SMOKING_DURING_PREGNANCY, MATERNAL_SMOKING.
- **Cannot establish:**

## Q256

- **Question:** Does geographic variation in birthplace affect the incidence of SUID?
- **Sources:** case: cdc_linkco15; denominator: cdc_linkco15; years 2016–2020
- **Variables:** cdc_linkco15:BFACIL
- **Rationale:** Geographic variations might indicate environmental or socio-economic factors influencing SUID.
- **Prior art:** No similar work found in existing literature.
- **Cannot establish:** Cannot establish causality without additional longitudinal data.

## Q958

- **Question:** Does postconceptional age at which infants start bed-sharing differ between SUID cases and non-SUID live births?
- **Sources:** case: ncfrp_v51; reference: prams_p8_arf, prams_p7_arf; denominator: cdc_natl15; years 2016–2021
- **Variables:** ncfrp_v51:BEDSHARING; prams_p8_arf:BDSHPG; prams_p7_arf:BDSHPG; cdc_natl15:LIVEBIRTH
- **Rationale:** Understanding if there are specific developmental stages where starting to share a bed with parents increases risk for SUID could guide prevention efforts.
- **Prior art:** Manuscripts discuss bed-sharing but not its timing relative to postconceptional age. Literature abstracts also lack this focus.
- **Cannot establish:** It cannot establish if bed-sharing directly causes SUID or is a marker of other risk factors.

## Q511

- **Question:** Is the risk of SUID associated with bed sharing different across postconceptional age windows?
- **Sources:** case: ncfrp_v51; reference: prams_p7_arf, prams_p8_arf; denominator: cdc_linkco15; years 2016–2019
- **Variables:** ncfrp_v51:BED_SHARING; prams_p7_arf:BED_SHARING
- **Rationale:** Is the risk of SUID associated with bed sharing different across postconceptional age windows?
- **Prior art:** The closest work is the manuscript on developmental timing of SUID and bed sharing, which did not explore BED_SHARING, BED_SHARING.
- **Cannot establish:**

## Q983

- **Question:** The risk of SUID among infants born to mothers who experienced significant barriers to healthcare access during pregnancy is higher compared to those without such obstacles.
- **Sources:** case: cdc_linkco15; reference: prams_p8_arf; denominator: cdc_natl15; years 2015–2021
- **Variables:** prams_p8_arf:PNC_MTH; prams_p8_arf:PG8_UTI; cdc_linkco15:NO_ABNORM; cdc_linkco15:NO_MMORB; cdc_natl15:F_RF_PPB; prams_p8_arf:WTANAL
- **Rationale:** This design uses a case series (numerator) and population reference (exposure prevalence) to estimate exposure-specific rates, comparing proportions or odds among cases. The sources provide the necessary data to address the research question on SUID risk associated with healthcare access barriers during pregnancy.
- **Prior art:** The closest tested work is claims C9 from the SUID manuscript which discusses maternal smoking and its association with SUID incidence. However, none of these claims directly address barriers to healthcare access, leaving this specific aspect still open for investigation.
- **Cannot establish:** The design cannot establish causation due to its observational nature and may not capture all relevant exposures, such as postnatal factors. Additionally, the randomized state codes in ncfrp_v51 prevent geographic comparisons.

## Q484

- **Question:** The proportion of mothers reporting pregnancy weight gain differs between PRAMS Phase 8 Analytic Research File and Standard Section II.
- **Sources:** reference: prams_p8_arf, prams_p8_std2; years 2016–2021
- **Variables:** prams_p8_arf:MAT_PRWT; prams_p8_arf:PG_GDB8; prams_p8_arf:TLK_WT_RAW; prams_p8_arf:WTANAL; prams_p8_std2:PGWTGN8_DK; prams_p8_std2:PGWTGNU8
- **Rationale:** This design can be carried out using the provided data sources as they enable a direct comparison between PRAMS_P8_ARF and PRAMS_P8_STD2 on recording pregnancy weight gain related to SUID risk factors.
- **Prior art:** None in the inputs. The manuscript claims do not address discrepancies between PRAMS Phase 8 ARF and Standard Section II, leaving this question open for investigation.
- **Cannot establish:** incidence rates or risk ratios since it does not have a denominator source; can only compare proportions among cases.

## Q892

- **Question:** The proportion of mothers reporting discussions about preventive practices differs between PRAMS Phase 7 and Phase 8.
- **Sources:** reference: prams_p7_arf, prams_p8_arf; years 2012–2021
- **Variables:** prams_p7_arf:WTANAL; prams_p8_arf:WTANAL; prams_p7_arf:P_PRTERM; prams_p8_arf:P_PRTERM; prams_p7_arf:MM_HBP; prams_p8_arf:MORB_BP8; prams_p7_arf:PNC_VST; prams_p8_arf:PNC_VST
- **Rationale:** This design focuses on comparing how the same concept (preventive practice discussions) is recorded in two different phases of PRAMS data collection. It evaluates measurement consistency rather than incidence rates or causality.
- **Prior art:** None in the inputs; prior research does not address discrepancies in preventive practice reporting across different PRAMS data collection phases.
- **Cannot establish:** incidence rates or causal relationships, only measurement consistency.

## Q836

- **Question:** The proportion of SUID cases with recorded pregnancy weight gain differs between NCFR-P v5.1 and PRAMS Phase 8 ARF.
- **Sources:** case: ncfrp_v51; reference: prams_p8_arf, prams_p8_std2; years 2008–2021
- **Variables:** ncfrp_v51:INF4momwtgn; ncfrp_v51:INF4mompregwt; prams_p8_arf:MOMLBS; prams_p8_arf:MAT_PRWT; prams_p8_arf:PG8_NAUS; prams_p8_std2:PGWTGN8; prams_p8_arf:WTANAL
- **Rationale:** This design compares how the same concept (pregnancy weight gain) is measured differently across two distinct sources (NCFR-P case series vs. PRAMS population reference).
- **Prior art:** The manuscripts have not addressed the comparability or differences in recording pregnancy weight gain between case series and population reference datasets, which could influence risk factor analysis for SUID.
- **Cannot establish:** incidence or risk, only proportions among cases.

## Q466

- **Question:** Does maternal exposure to environmental pollutants during pregnancy increase the risk of SUID in early infancy?
- **Sources:** case: ncfrp_v51; reference: prams_p7_arf, prams_p8_arf; denominator: cdc_linkco15; years 2016–2019
- **Variables:** ncfrp_v51:MATERNAL_EXPOSURE_ENVIRONMENTAL_POLLUTANTS
- **Rationale:** Does maternal exposure to environmental pollutants during pregnancy increase the risk of SUID in early infancy?
- **Prior art:** The closest work is the manuscript on developmental timing of SUID and bed sharing, which did not explore MATERNAL_EXPOSURE_ENVIRONMENTAL_POLLUTANTS.
- **Cannot establish:**

## Q158

- **Question:** The SUID rate is higher among infants whose mothers experienced severe mental health issues during pregnancy compared to those who did not.
- **Sources:** case: ncfrp_v51; reference: prams_p8_arf, prams_p7_arf; denominator: cdc_natl15; years 2016–2021
- **Variables:** ncfrp_v51:ISSmhpregdepres; prams_p8_arf:MH_PGDX8; prams_p8_arf:HTH_ANX; prams_p8_arf:BPG_DEPRS8; prams_p7_arf:PRE_DEPR; prams_p8_arf:WTANAL; prams_p7_arf:WTANAL
- **Rationale:** This design uses the case series (ncfrp_v51) for numerator and population reference sources (prams_p8_arf, prams_p7_arf) to determine maternal mental health issues during pregnancy. The denominator source (cdc_natl15) provides necessary live birth denominators.
- **Prior art:** The closest tested work is bedsharing_ms_v7.C11, which explores the association between bed-sharing and SUID incidence but does not address severe mental health issues during pregnancy.
- **Cannot establish:** This design cannot establish causation or account for potential temporal trends and changes in reporting practices over time.

## Q164

- **Question:** Does maternal age impact SUID incidence?
- **Sources:** case: cdc_linkco15; denominator: cdc_linkco15; years 2016–2020
- **Variables:** cdc_linkco15:MOMAGE
- **Rationale:** Maternal age is associated with various health outcomes in infants.
- **Prior art:** No similar work found in existing literature focusing specifically on this relationship using the available data sources.
- **Cannot establish:** Cannot establish causality without additional longitudinal data.
