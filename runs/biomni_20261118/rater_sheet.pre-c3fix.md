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

- **Question:** The proportion of SUID cases with prenatal complications such as low birth weight has changed over different time periods (2008-2019 vs. 2016-2021).
- **Sources:** case: ncfrp_v51; reference: prams_p8_arf, prams_p7_arf; years 2008–2021
- **Variables:** ncfrp_v51:INFprevpreterm; ncfrp_v51:INF3lbwt; prams_p8_arf:P_PRTERM; prams_p7_arf:P_PRTERM; prams_p8_arf:PRE_LB_NAPHSIS; prams_p7_arf:PREV_LBW_RAW; prams_p8_arf:WTANAL; prams_p7_arf:WTANAL
- **Rationale:** This design is a trend analysis among case series, comparing proportions across different time periods without estimating incidence or rates.
- **Prior art:** The closest tested work includes SUID_manuscript_v9_clean.C6 and C7, which discuss temporal trends in SUID cases but do not focus on prenatal complications. The question remains open as these studies did not examine changes in prenatal factors over time.
- **Cannot establish:** This design can only establish trends in proportions of SUID cases with prenatal complications over time. It cannot estimate incidence or risk because it lacks a denominator source to calculate rates.

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

- **Question:** The proportion of SUID cases with hospital overnight stays after birth is higher compared to the weighted prevalence among live births in the general population.
- **Sources:** case: ncfrp_v51; reference: prams_p8_arf; denominator: cdc_natl15; years 2016–2021
- **Variables:** ncfrp_v51:INF4hosprtn; prams_p8_arf:NOHOSP_B; prams_p8_arf:LTH_HOSP; prams_p8_arf:WTANAL
- **Rationale:** This study uses a case-population comparison design to assess whether infants who had an overnight stay in the hospital after birth are more likely to experience sudden unexpected infant death (SUID).
- **Prior art:** None in the inputs. The closest claims do not address postnatal hospital stays and their association with SUID incidence.
- **Cannot establish:** Causation, as the design only allows for association due to potential confounding factors such as prematurity and maternal smoking.

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

- **Question:** The proportion of cases with reported pre-pregnancy hypertension differs between NCFRP and PRAMS datasets.
- **Sources:** case: ncfrp_v51; reference: prams_p8_arf, prams_p7_arf; years 2008–2021
- **Variables:** ncfrp_v51:ISSprechronicdiseasebef; prams_p8_arf:RF_PHYPE; prams_p7_arf:MM_HBP; prams_p8_arf:WTANAL; prams_p7_arf:WTANAL
- **Rationale:** This study aims to compare how maternal health problems are recorded in the National Fatality Review Case Reporting System (NCFRP) case series versus PRAMS population reference datasets. The design focuses on identifying differences in recording methods and prevalence of specific maternal health conditions, such as pre-pregnancy hypertension.
- **Prior art:** The literature has not yet compared how maternal health problems are recorded in case series versus population references, which could introduce biases when assessing risk factors for SUID (SUID_manuscript_v9_clean.C12).
- **Cannot establish:** The design cannot establish incidence or risk of SUID due to the lack of a denominator source.

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

- **Question:** The proportion of SUID cases among infants born to mothers with different pre-pregnancy health behaviors and conditions varies.
- **Sources:** case: ncfrp_v51; reference: prams_p7_arf, prams_p8_arf; denominator: cdc_natl15; years 2008–2021
- **Variables:** ncfrp_v51:INFfirsttricig; prams_p8_arf:MOMCIG; prams_p7_arf:CIG_PRIOR; prams_p8_arf:WTANAL; prams_p7_arf:WTANAL; prams_p8_arf:PRE_LB_NAPHSIS; prams_p7_arf:PRE_LB_NAPHSIS; prams_p8_arf:MM_NOMD; prams_p7_arf:MM_NOMD
- **Rationale:** This study design uses the case series (ncfrp_v51) for numerator, population reference (prams_p7_arf, prams_p8_arf) for exposure prevalence, and denominator source (cdc_natl15) to estimate live births stratified by maternal pre-pregnancy health behaviors. The design can identify associations but cannot establish causation or fully control for confounding variables.
- **Prior art:** SUID_manuscript_v9_clean.C9 suggests an association between maternal smoking and higher SUID incidence, but does not address pre-pregnancy behaviors comprehensively.
- **Cannot establish:** Causality, individual-level linkage between case series and population reference datasets.

## Q361

- **Question:** The proportion of SUID cases with documented maternal mental health conditions differs from the proportion of live births reported through PRAMS surveys.
- **Sources:** case: ncfrp_v51; reference: prams_p8_arf, prams_p7_arf; years 2012–2021
- **Variables:** ncfrp_v51:ISSmhpregdepres; ncfrp_v51:BIO1disillmhsp; prams_p8_arf:MH_PGDX8; prams_p8_arf:PG8_ANX; prams_p7_arf:PREV_LBW_RAW; prams_p8_arf:WTANAL; prams_p7_arf:WTANAL
- **Rationale:** This design compares how maternal mental health conditions are recorded between SUID cases and live births, focusing on discrepancies in documentation methods. The sources provide data on mental health conditions but do not allow for incidence rate estimation due to a lack of denominator data.
- **Prior art:** None in the inputs; the manuscript claims focus on risk factors like bed sharing and smoking rather than recording discrepancies in maternal mental health conditions.
- **Cannot establish:** incidence rates or risk estimates due to the absence of a denominator source.

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

- **Question:** The frequency and quality of prenatal care visits differ between PRAMS surveys for live births and NCFRP_v51 case reports for SUID deaths.
- **Sources:** case: ncfrp_v51; reference: prams_p7_arf, prams_p8_arf; years 2004–2021
- **Variables:** ncfrp_v51:INFprenatal; prams_p8_arf:PNC_VST; prams_p7_arf:PNC_VST; prams_p8_arf:WTANAL; prams_p7_arf:WTANAL
- **Rationale:** This study design can compare how prenatal care visits are recorded in PRAMS (population reference) versus NCFRP_v51 (case series), though it cannot establish causation due to observational nature and potential biases.
- **Prior art:** SUID_manuscript_v9_clean.C12 [limitation] notes vital-record data may have exposure misclassification issues, indicating that NCFRP data quality for prenatal care documentation is a concern. This question remains open as it focuses on methodological differences rather than causal relationships.
- **Cannot establish:** The design cannot establish the absolute incidence or risk of SUID based on prenatal care differences, nor can it establish causal relationships between prenatal care quality and SUID occurrence due to the observational nature of both data sources.

## Q484

- **Question:** The proportion of mothers with pre-pregnancy hypertension among SUID cases is higher compared to the weighted prevalence in the general population.
- **Sources:** case: cdc_linkco15, ncfrp_v51; reference: prams_p7_arf, prams_p8_arf; years 2012–2021
- **Variables:** cdc_linkco15:RF_PHYPE; cdc_linkco15:RF_PDIAB; ncfrp_v51:ISSprechronicdiseasebef; prams_p7_arf:WTANAL; prams_p8_arf:WTANAL; prams_p7_arf:PRE_CKBP; prams_p8_arf:RF_PHYPE
- **Rationale:** This study aims to compare the prevalence of maternal pre-pregnancy health conditions between SUID cases and a representative sample of the general population. The design uses case-population comparison, which can establish whether there is an association but not causality or incidence rates.
- **Prior art:** suid_literature_abstracts.C10 suggests that maternal obesity increases SUID risk, but no research has systematically analyzed prepregnancy health conditions and their influence on SUID incidence. This study aims to fill this gap by focusing specifically on pre-pregnancy maternal health conditions.
- **Cannot establish:** The design cannot establish causality or incidence rates; it can only compare proportions between cases and a population reference.

## Q892

- **Question:** The SUID rate is higher among infants whose mothers experienced severe mental health issues during pregnancy compared to those who did not.
- **Sources:** case: ncfrp_v51; reference: prams_p8_arf, prams_p7_arf; denominator: cdc_natl15; years 2016–2021
- **Variables:** ncfrp_v51:ISSmhpregdepres; prams_p8_arf:MH_PGDX8; prams_p8_arf:HTH_ANX; prams_p8_arf:BPG_DEPRS8; prams_p7_arf:PRE_DEPR; prams_p8_arf:WTANAL; prams_p7_arf:WTANAL
- **Rationale:** This design uses the case series (ncfrp_v51) for numerator and population reference sources (prams_p8_arf, prams_p7_arf) to determine maternal mental health issues during pregnancy. The denominator source (cdc_natl15) provides necessary live birth denominators.
- **Prior art:** The closest tested work is bedsharing_ms_v7.C11, which explores the association between bed-sharing and SUID incidence but does not address severe mental health issues during pregnancy.
- **Cannot establish:** This design cannot establish causation or account for potential temporal trends and changes in reporting practices over time.

## Q836

- **Question:** The proportion of mothers who had pre-pregnancy health checks for chronic diseases, high blood pressure, diabetes, and depression/anxiety is compared between SUID cases and PRAMS mothers from 2012-2015.
- **Sources:** case: ncfrp_v51; reference: prams_p7_arf; years 2012–2015
- **Variables:** ncfrp_v51:ISSprechronicdiseasebef; ncfrp_v51:ISSprechronicdiseasedur; prams_p7_arf:PRE_CKBP; prams_p7_arf:PRE_CKD; prams_p7_arf:PRE_DEPR; prams_p7_arf:WTANAL
- **Rationale:** This study design compares the use of pre-pregnancy health checks between SUID cases and a population reference using available data sources. The variables are measurable in both datasets, allowing for a valid comparison.
- **Prior art:** None in the inputs; existing manuscripts focus on developmental windows, bed sharing, smoking during pregnancy, and prematurity but do not address pre-pregnancy health checks specifically.
- **Cannot establish:** The design cannot establish causality or incidence rates; it can only compare proportions of pre-pregnancy health checks between SUID cases and the general population.

## Q466

- **Question:** Does maternal exposure to environmental pollutants during pregnancy increase the risk of SUID in early infancy?
- **Sources:** case: ncfrp_v51; reference: prams_p7_arf, prams_p8_arf; denominator: cdc_linkco15; years 2016–2019
- **Variables:** ncfrp_v51:MATERNAL_EXPOSURE_ENVIRONMENTAL_POLLUTANTS
- **Rationale:** Does maternal exposure to environmental pollutants during pregnancy increase the risk of SUID in early infancy?
- **Prior art:** The closest work is the manuscript on developmental timing of SUID and bed sharing, which did not explore MATERNAL_EXPOSURE_ENVIRONMENTAL_POLLUTANTS.
- **Cannot establish:** 

## Q158

- **Question:** The proportion of SUID cases with hospital overnight stays increased from 2008 to 2019.
- **Sources:** case: ncfrp_v51; reference: prams_p8_arf, prams_p7_arf; years 2008–2019
- **Variables:** ncfrp_v51:INF4hosprtn; prams_p8_arf:LTH_HOSP; prams_p7_arf:LTH_HOSP; prams_p8_arf:WTANAL; prams_p7_arf:WTANAL
- **Rationale:** This study can analyze trends in hospital overnight stay history among SUID cases using ncfrp_v51 and reference data from prams_p7_arf and prams_p8_arf. However, it must acknowledge its limitations regarding causal inference and incidence rate estimation.
- **Prior art:** SUID_manuscript_v9_clean.C6 discusses trends in PCA-aligned incidence but does not focus on hospital overnight stay trends. bedsharing_ms_v7.C13 examines developmental timing of SUID incidence and associations with bed sharing, smoking, and prematurity; the proposed study is distinct as it focuses specifically on hospital stays.
- **Cannot establish:** The design cannot establish incidence rates or risk ratios. It can only compare proportions of SUID cases with and without hospital overnight stays across different years.

## Q164

- **Question:** Does maternal age impact SUID incidence?
- **Sources:** case: cdc_linkco15; denominator: cdc_linkco15; years 2016–2020
- **Variables:** cdc_linkco15:MOMAGE
- **Rationale:** Maternal age is associated with various health outcomes in infants.
- **Prior art:** No similar work found in existing literature focusing specifically on this relationship using the available data sources.
- **Cannot establish:** Cannot establish causality without additional longitudinal data.

