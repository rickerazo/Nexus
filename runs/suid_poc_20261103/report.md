# MMF strategy report — run `suid_poc_20261103`

Backend `ollama`, model `qwen2.5:14b` (digest `7cdf5a0187d5`), seed 0, temperature 0.0, MMF 0.1.0.dev0.
LLM calls: 71; total attempts: 112.
Items dropped after retries because their quotes could not be grounded: 7 (listed under `dropped` in `manifest.json`).> MMF proposes; the investigator decides. This report does not assess statistical power or causal validity and no row-level data were read.

## Inputs
| Role | File | sha256 |
|---|---|---|
| codebook | data/codebooks/LinkCO15Guide.pdf | `1b6cd81b08596230` |
| codebook | data/documentation/natl2015.pdf | `cefeaebb9d9fb574` |
| codebook | data/documentation/CDC_database_codeNames.xlsx | `0ef67f25e365f4b2` |
| codebook | data/documentation/Codebook_Version5-1_031122.xlsx | `fb90580f2efa5298` |
| codebook | data/codebooks/PRAMS_Phase_8_ARF_Codebook.pdf | `9d5b3d4dd9092af2` |
| codebook | data/codebooks/PRAMS_Phase_8_Standard_Section_II_Codebook.pdf | `792402034db4bcfe` |
| codebook | data/codebooks/PRAMS_Phase_7_ARF_Codebook.pdf | `57957107866cc22b` |
| manuscript | data/manuscripts/SUID_manuscript_v9_clean.docx | `92fd11fa182c9a7b` |
| manuscript | data/manuscripts/bedsharing_ms_v7.docx | `1496e66e4e7b2667` |
| manuscript | data/manuscripts/literature/suid_literature_abstracts.md | `687e8a02fa0c7d69` |

## A. Manuscripts
### SUID_manuscript_v9_clean (`SUID_manuscript_v9_clean`)
Designs: population_incidence. Models: negative_binomial, generalized_additive, poisson_regression, time_stratified. Data: US CDC linked birth–infant death records from 2014 to 2021; N = 23,686.

Research questions:
- To test whether male excess risk in sudden unexpected infant death (SUID) reflects a constant effect from birth or a developmentally timed phenomenon by applying a postconceptional age (PCA) alignment framework that accounts for differences in maturity at birth.

- To determine the incidence rate ratios of sudden unexpected infant death (SUID) across different developmental windows.

Claims (14):
- **SUID_manuscript_v9_clean.C1** [hypothesis] The study tests whether male excess risk in sudden unexpected infant death (SUID) is present from birth or emerges at a specific developmental stage. — p.1: "To test whether male excess risk in sudden unexpected infant death (SUID) reflects a constant effect from birth or a developmentally timed phenomenon by applying a postconceptional age (PCA) alignment framework that accounts for differences in maturity at birth."

- **SUID_manuscript_v9_clean.C2** [method] The study uses population-based analysis of US CDC linked birth–infant death records from 2014 to 2021, excluding deaths within the first postnatal week. — p.1: "Population-based analysis of US CDC linked birth–infant death records from 2014 to 2021. SUID was defined using ICD-10 codes R95, R99, and W75, excluding deaths in the first postnatal week."

- **SUID_manuscript_v9_clean.C3** [method] Infant age is aligned using postconceptional age (PCA), which combines gestational age at birth with postnatal age. — p.1: "Infant age was aligned using PCA (gestational age at birth plus postnatal age)."

- **SUID_manuscript_v9_clean.C4** [method] Weekly SUID counts across PCA weeks 36 to 90 were modelled using a negative binomial generalised additive model with spline smooths and an offset based on national live-birth proportions. — p.1: "Weekly SUID counts across PCA weeks 36 to 90 were modelled using a negative binomial generalised additive model with spline smooths and an offset based on national live-birth proportions."

- **SUID_manuscript_v9_clean.C5** [method] The study includes prespecified negative binomial models comparing an early rising window (36–42 PCA weeks) and a late declining window (≥47 PCA weeks). — p.1: "Prespecified negative binomial models compared an early rising window (36–42 PCA weeks) and a late declining window (≥47 PCA weeks)."

- **SUID_manuscript_v9_clean.C6** [finding] Among the eligible SUID cases, PCA-aligned incidence revealed a clear rise, peak, and decline pattern. — p.1: "PCA-aligned incidence revealed a clear rise, peak, and decline pattern."

- **SUID_manuscript_v9_clean.C7** [finding] Male and female trajectories overlapped during the rising phase and peak but diverged after the peak with persistently higher male incidence during the declining phase. — p.1: "Sex divergence emerged only after the peak, with persistently higher male incidence during the declining phase."

- **SUID_manuscript_v9_clean.C8** [finding] Confirmatory models showed similar male and female incidence in the early window (36–42 PCA weeks) but higher male incidence in the late window (≥47 PCA weeks). — p.1: "Confirmatory models showed similar male and female incidence in the early window and higher male incidence in the late window (Incidence rate ratios 1.14 early vs 1.36 late)."

- **SUID_manuscript_v9_clean.C9** [finding] Maternal smoking was associated with higher SUID incidence across both windows. — p.1: "Maternal smoking was associated with higher incidence across both windows."

- **SUID_manuscript_v9_clean.C10** [limitation] The analysis excludes a small number of deaths at the extremes of the PCA distribution, including some extremely and very preterm infants who died early in postnatal life. — p.1: "This excludes a small number of deaths at the extremes of the PCA distribution, including some extremely and very preterm infants who died early in postnatal life"

- **SUID_manuscript_v9_clean.C11** [limitation] The models did not account for postnatal exposures that may change during infancy, such as breastfeeding. — p.1: "Residual influence from breastfeeding and other unmeasured postnatal factors therefore cannot be excluded."

- **SUID_manuscript_v9_clean.C12** [limitation] The study uses vital-record data, which may have exposure and cause-of-death misclassification issues. — p.1: "as with all analyses based on vital-record data, exposure and cause-of-death misclassification are possible."

- **SUID_manuscript_v9_clean.C13** [future_work] Future research will focus on understanding the long-term consequences of separation from the mother in human infants and how it may predispose males to increased vulnerability to SIDS. — p.1: "Further research will be necessary to study the long-term consequences of separation from the mother in human infants."

- **SUID_manuscript_v9_clean.C14** [future_work] The study suggests that interventions targeting socioeconomic and environmental stressors may represent an important avenue for reducing risk in infants beyond the early peak period. — p.1: "interventions targeting socioeconomic and environmental stressors may represent an important avenue for reducing risk in infants beyond the early peak period."

### bedsharing_ms_v7 (`bedsharing_ms_v7`)
Designs: population_incidence. Models: negative_binomial, time_stratified, generalized_additive. Data: NCFRP Case Reporting System; Centers for Disease Control and Prevention (CDC) National Vital Statistics System linked birth records; PRAMS.

Research questions:
- To examine whether postconceptional age (PCA), the sum of gestational and postnatal age, clarifies how bed sharing, maternal smoking, and prematurity relate to SUID incidence.

- To determine the stability of the PCA window boundary diagnostics for at least 5 cases per week in each subgroup.

- To compare incidence rate ratios between primary and sensitivity analyses restricting the PCA window to different durations.

Claims (30):
- **bedsharing_ms_v7.C1** [hypothesis] Postconceptional age (PCA) may clarify how bed sharing, maternal smoking, and prematurity relate to Sudden Unexpected Infant Death (SUID) incidence. — p.1: "We examined whether postconceptional age (PCA), the sum of gestational and postnatal age, clarifies how bed sharing, maternal smoking, and prematurity relate to SUID incidence."

- **bedsharing_ms_v7.C2** [method] The study analyzed 13,013 SUID cases from the National Center for Fatality Review and Prevention Case Reporting System using population-adjusted negative binomial regression. — p.1: "We analyzed 13,013 SUID cases (2008–2019) from the National Center for Fatality Review and Prevention Case Reporting System, modeling incidence across PCA with population-adjusted negative binomial regression."

- **bedsharing_ms_v7.C3** [finding] Bed sharing was more strongly associated with SUID incidence in an early developmental window (PCA <43 weeks) compared to a later one (PCA ≥47 weeks). — p.1: "Bed sharing was more strongly associated with incidence in an early developmental window (PCA <43 weeks; incidence rate ratio [IRR] 6.45, 95% CI 3.14–13.23) than a later one (PCA ≥47 weeks; IRR 2.10, 95% CI 1.70–2.58)"

- **bedsharing_ms_v7.C4** [finding] Maternal smoking and prematurity showed a similar pattern of association with SUID incidence as bed sharing, remaining positively associated throughout. — p.1: "maternal smoking and prematurity showed the same pattern while remaining positively associated throughout."

- **bedsharing_ms_v7.C5** [finding] The association between bed sharing and SUID incidence was further amplified by maternal smoking in a later developmental window (PCA ≥47 weeks). — p.1: "Bed sharing’s association with incidence was further amplified by maternal smoking in the late window (interaction IRR 1.57, 95% CI 1.19–2.08)"

- **bedsharing_ms_v7.C6** [finding] Associations between SUID incidence and bed sharing, maternal smoking, and prematurity were similar in males and females. — p.None: "associations were similar in males and females, indicating these effects are sex-independent."

- **bedsharing_ms_v7.C7** [finding] The developmental timing of SUID incidence showed a clear rise-peak-decline pattern when aligned by postconceptional age (PCA). — p.None: "PCA alignment produced a clear rise-peak-decline pattern."

- **bedsharing_ms_v7.C8** [finding] Bed sharing was recorded for 59.5% of SUID cases, and these cases were more often associated with maternal smoking during pregnancy (52.2%) compared to non-bed-sharing cases (40.8%). — p.None: "Bed sharing was recorded for 7,739 cases (59.5%) and was absent for 5,274 (40.5%). Bed-sharing cases more often involved maternal smoking during pregnancy (52.2% versus 40.8%)."

- **bedsharing_ms_v7.C9** [finding] The incidence of SUID was highest in the first several months of life and then declined when analyzed on a postnatal age scale. — p.None: "weekly incidence was highest in the first several months of life and then declined (Figure 2A)"

- **bedsharing_ms_v7.C10** [finding] When aligned by PCA, weekly SUID incidence followed a clearer developmental structure with a steep rise across early weeks, a peak in the mid-40-week range, and a gradual decline thereafter. — p.None: "weekly incidence followed a clearer developmental structure, with a steep rise across the early weeks, a peak in the mid-40-week PCA range, and a gradual decline thereafter (Figure 2B)"

- **bedsharing_ms_v7.C11** [finding] Bed sharing was independently associated with higher incidence of SUID across both rising and declining phases of the developmental curve. — p.None: "bed sharing remained strongly associated with higher incidence, although its magnitude was smaller than that of maternal smoking."

- **bedsharing_ms_v7.C12** [finding] Maternal smoking during pregnancy showed the largest and most consistent association with SUID incidence in both windows. — p.None: "maternal smoking during pregnancy showed the largest and most consistent association with SUID incidence in both windows"

- **bedsharing_ms_v7.C13** [finding] Prematurity remained a positive and significant correlate of SUID incidence across the developmental window, though roughly twice as strong early as late. — p.None: "prematurity remained a positive and significant correlate across the developmental window, though roughly twice as strong early as late"

- **bedsharing_ms_v7.C14** [finding] The association between bed sharing and SUID incidence was larger among smokers (IRR 3.35) than non-smokers (IRR 2.07) in the later developmental window. — p.None: "the late-window bed-sharing association among smokers (IRR 3.35) than non-smokers (IRR 2.07)"

- **bedsharing_ms_v7.C15** [finding] The developmental structure of risk was similar in girls and boys once bed sharing, smoking, and prematurity were explicitly modeled. — p.None: "the developmental structure of risk was similar in girls and boys."

- **bedsharing_ms_v7.C16** [finding] PCA alignment resolved heterogeneity and yielded a smooth rise-peak-decline incidence curve, consistent with a single underlying developmental process. — p.None: "Aligning by PCA resolves this heterogeneity and yields a smooth, roughly symmetric rise-peak-decline incidence curve"

- **bedsharing_ms_v7.C17** [limitation] The study is an observational analysis of registry-based case data, resulting in associative rather than causal estimates. — p.None: "this was an observational analysis of registry-based case data, and the resulting estimates are associative rather than causal."

- **bedsharing_ms_v7.C18** [limitation] Sleep-environment classification in case-report systems may be subject to heterogeneity in ascertainment and reporting. — p.None: "sleep-environment classification in case-report systems may be subject to heterogeneity in ascertainment and reporting."

- **bedsharing_ms_v7.C19** [limitation] The bed-sharing denominator was derived indirectly from external prevalence estimates rather than a source linked to the cases. — p.None: "the bed-sharing denominator was derived indirectly from external prevalence estimates rather than a source linked to the cases"

- **bedsharing_ms_v7.C20** [limitation] The analytic strategy excluded sparse strata and zero-count cells, meaning the fitted models describe observed high-information strata rather than a fully enumerated population lattice. — p.None: "the analytic strategy intentionally excluded sparse strata and zero-count cells to stabilize estimation"

- **bedsharing_ms_v7.C21** [limitation] The peak interval was treated descriptively rather than modeled directly in the windowed regressions due to week-to-week instability. — p.None: "the peak interval was treated descriptively rather than modeled directly in the windowed regressions because of week-to-week instability"

- **bedsharing_ms_v7.C22** [limitation] The exposure IRRs, particularly maternal smoking IRR, are not directly comparable in magnitude to case-control effect estimates. — p.None: "the exposure IRRs, and the maternal smoking IRR in particular, are not directly comparable in magnitude to case-control effect estimates"

- **bedsharing_ms_v7.C23** [limitation] The largest single exclusion was missing or invalid maternal smoking status (6,113 cases), which were excluded rather than imputed. — p.None: "these cases were excluded rather than imputed, which assumes that smoking-status missingness is unrelated to the outcome within the observed cohort"

- **bedsharing_ms_v7.C24** [limitation] The case series should be understood as a large, growing multi-jurisdiction surveillance sample rather than a fixed national census. — p.None: "the case series should be understood as a large, growing multi-jurisdiction surveillance sample rather than a fixed national census"

- **bedsharing_ms_v7.C25** [limitation] The absolute incidence scale shown in Figure 2 is a population proxy rather than a jurisdiction-matched rate. — p.None: "the absolute incidence scale shown in Figure 2 is a population proxy rather than a jurisdiction-matched rate"

- **bedsharing_ms_v7.C26** [limitation] The split between suffocation and undetermined codes reflects diagnostic-practice-dependent ascertainment patterns. — p.None: "the split between suffocation and undetermined codes is diagnostic-practice-dependent and can vary by jurisdiction and year"

- **bedsharing_ms_v7.C27** [limitation] The study does not provide fine-grained mechanistic claims about the pathway from bed sharing to death. — p.None: "no fine-grained mechanistic claim about the pathway from bed sharing to death is made here"

- **bedsharing_ms_v7.C28** [method] The manuscript specifies a PCA window of 36 to 90 weeks and checks it against a count-stability criterion. — p.1: "Prespecified PCA window (36-90 weeks) checked against a count-stability criterion of at least 5 cases per week in each of 4 tracked subgroups"

- **bedsharing_ms_v7.C29** [method] The manuscript includes a sensitivity analysis comparing the primary PCA window (36-90 weeks) with an upper-bound restriction to 79 weeks. — p.1: "Late-window incidence rate ratios at the primary PCA window (36-90 weeks) versus an upper-bound sensitivity analysis restricting the window to PCA 36-79 weeks"

- **bedsharing_ms_v7.C30** [method] The manuscript presents interaction terms from windowed negative binomial models for bed sharing by maternal smoking and preterm birth. — p.1: "Prespecified interaction terms from the windowed negative binomial models"

### SUID literature from the Ramirez lab and Lavista Ferres group: abstracts (PubMed, retrieved 2026-10-26) (`suid_literature_abstracts`)
Designs: cohort, nested_case_control, case_control, cross_sectional. Models: logistic_regression, cox_proportional_hazards, generalized_additive. Data: Centers for Disease Control and Prevention National Center for Health Statistics data; National Fatality Review Case Reporting System; Centers for Disease Control and Prevention Birth Cohort Linked Birth/Infant Death Data Set; Genetic mouse model of Ndufs4; Mouse model with chronic intermittent hypoxia (CIH); Adult mice exposed to urethane anesthesia; Frontiers in physiology; Journal of neurophysiology; Reproductive sciences (Thousand Oaks, Calif.); eNeuro; Current opinion in neurobiology.

Research questions:
- To determine whether maternal obesity is a risk factor for Sudden Unexpected Infant Death (SUID) and the proportion of SUID cases attributable to maternal obesity.

- To examine pandemic-era changes in non-SUID infant mortality by gestational age, age at death and cause of death.

- To investigate the effects of maternal prepregnancy smoking, reduction during pregnancy, and smoking during pregnancy on SUID rates.

- To assess whether inner ear dysfunction not only weakens the hypercapnic response, but also plays a role in suppressing the arousal response to suffocating gas mixtures.

- To investigate the role of PiCo and preBötC in respiratory-sympathetic coupling under control conditions and following exposure to chronic intermittent hypoxia (CIH).

- To report results from an 11-step user-centered design development process for a quit smoking conversational chatbot called QuitBot.

- To investigate whether mouse models of Leigh Syndrome exhibit dysfunctions in neuromuscular activity of swallow and breathing integration.

- How does chronic intermittent hypoxia (IH) affect adult neurogenesis in the dentate gyrus?

- What are the effects of IH on synaptic plasticity in the dentate gyrus?

- Do reactive oxygen species (ROS)-dependent and ROS-independent mechanisms contribute to changes in adult neurogenesis and synaptic plasticity due to IH?

- How do breathing patterns during the first hour after birth predict survival in mice born prematurely or at term?

- What are the roles of inhibition within the pre-Bötzinger complex (preBötC) for rhythm generation?

- Does chronic intermittent hypoxia differentially impact inspiratory activity states at the level of the preBötzinger Complex?

- Can progesterone pretreatment ameliorate detrimental effects of lipopolysaccharide-induced inflammation on cortical neurogenesis in mice?

Claims (62):
- **suid_literature_abstracts.C1** [finding] The overall non-SUID infant mortality rates consistently trended downwards with no pandemic-associated change. — p.1: "Overall non-SUID infant mortality rates consistently trended downwards with no pandemic-associated change."

- **suid_literature_abstracts.C2** [finding] Mortality rates among full-term infants reversed their prepandemic declines during the pandemic. — p.1: "rates among full-term infants reversed their prepandemic declines."

- **suid_literature_abstracts.C3** [finding] Postneonatal deaths also reversed their prepandemic decline with statistically significant increases during the pandemic. — p.1: "postneonatal deaths similarly reversed their prepandemic decline, with statistically significant increases during the pandemic."

- **suid_literature_abstracts.C4** [finding] The decline in early neonatal mortality rates became more pronounced during the pandemic. — p.1: "the decline in early neonatal mortality rates became more pronounced during the pandemic, with a 7.2% reduction in observed versus expected monthly mortality rates."

- **suid_literature_abstracts.C5** [finding] Rates of mortality due to external causes increased during the pandemic. — p.1: "rates of mortality due to external causes increased during the pandemic."

- **suid_literature_abstracts.C6** [finding] Variants in 88 genes were identified, with 64.6% of infants having variants of interest. — p.1: "variants of interest were identified in 88 genes, in 64.6% of our cohort."

- **suid_literature_abstracts.C7** [finding] Seventy-three of the identified gene variants have been previously associated with SIDS/SUID/SUDP. — p.1: "seventy-three of these have been previously associated with SIDS/SUID/SUDP."

- **suid_literature_abstracts.C8** [finding] Forty-three cardiac genes were identified, related to cardiomyopathies, arrhythmias, and other conditions. — p.1: "forty-three can be characterized as cardiac genes and are related to cardiomyopathies, arrhythmias, and other conditions."

- **suid_literature_abstracts.C9** [finding] Eight gene variants are implicated in the response to hypoxia and regulation of reactive oxygen species (ROS). — p.1: "eight genes are implicated in the response to hypoxia and the regulation of reactive oxygen species (ros) and have not been previously described in sids/suid/sudp."

- **suid_literature_abstracts.C10** [finding] Maternal obesity is a risk factor for Sudden Unexpected Infant Death (SUID), with an increased risk associated with higher maternal BMI. — p.1: "infants born to mothers with obesity had a higher suid risk that increased with increasing obesity severity."

- **suid_literature_abstracts.C11** [finding] Maternal smoking during pregnancy significantly increases the risk of SUID. — p.1: "maternal smoking during pregnancy is an established risk factor for sudden unexpected infant death (suid). here, we aim to investigate the effects of maternal prepregnancy smoking, reduction during pregnancy, and smoking during pregnancy on suid rates."

- **suid_literature_abstracts.C12** [finding] Post-hypoxic recovery of respiration is gender dependent, which is centrally manifested at the level of the preBötzinger complex (preBötC). — p.1: "we conclude that post-hypoxic recovery of respiration is gender dependent, which is, in part, centrally manifested at the level of the prebötc."

- **suid_literature_abstracts.C13** [finding] Sighs monitor changes in brain states and induce arousal, playing a role in homeostatically regulating breathing stability under physiological and pathological conditions. — p.1: "sighs monitor changes in brain states, induce arousal, and reset breathing variability. these behavioral roles homeostatically regulate breathing stability under physiological and pathological conditions."

- **suid_literature_abstracts.C14** [finding] Inner ear dysfunction (IED) can suppress the movement response to hypoxia-hypercarbia in mice, potentially playing a role in Sudden Infant Death Syndrome (SIDS). — p.1: "hypercarbia did not stimulate vigorous movements in any animals under either sleep condition. hypoxia triggered vigorous movements in controls (p<0.05) and a decreased response in it-gent animals under light anesthesia."

- **suid_literature_abstracts.C15** [finding] The preBötzinger complex (preBötC) is critical for generating breathing rhythms, and its function can be influenced by gender. — p.1: "the prebötcc is a critical neuronal network for the generation of breathing. lesioning the prebötcc abolishes respiration, while when isolated in vitro, the prebötcc continues to generate respiratory rhythmic activity."

- **suid_literature_abstracts.C16** [finding] A prior study identified an association between hearing suppression on the newborn hearing test and subsequent death from SIDS. — p.1: "A prior study identified an association between hearing suppression on the newborn hearing test and subsequent death from SIDS."

- **suid_literature_abstracts.C17** [finding] Inner ear dysfunction precipitates a marked suppression of the hypercapnic ventilatory response (HCVR). — p.1: "inner ear dysfunction precipitates a marked suppression of the hypercapnic ventilatory response (HCVR)"

- **suid_literature_abstracts.C18** [finding] Inner ear dysfunction weakens the hypercapnic response and suppresses the arousal response to suffocating gas mixtures. — p.1: "the HCVR as well as the arousal movements in response to severe hypoxia-hypercarbia were suppressed in IT-Gent-treated animals compared to control animals (P<0.05)"

- **suid_literature_abstracts.C19** [finding] The HCVR was significantly decreased in bilateral and unilateral IT-Gent-treated mice compared to controls. — p.1: "Thus the HCVR was significantly decreased in the bilateral (n=9) and unilateral IT-Gent-treated mice (n=19) compared to bilateral (n=7) and unilateral IT-Saline (n=9) control groups (p<0.05)"

- **suid_literature_abstracts.C20** [finding] Arousal movements were suppressed in bilateral and unilateral IT-Gent-treated mice compared to controls. — p.1: "arousal movements were suppressed in the bilateral IT-Gent group (n=9) compared to bilateral IT-Saline controls (n=7, P<0.0001) and in the unilateral IT-Gent group (n=19) compared to unilateral IT-Saline controls (n=10, P<0.0001)"

- **suid_literature_abstracts.C21** [finding] Inner ear dysfunction could be relevant in the pathophysiology of SIDS. — p.1: "The findings support the theory that inner ear dysfunction could be relevant in the pathophysiology of SIDS"

- **suid_literature_abstracts.C22** [finding] Inner ear dysfunction plays a key role in arousal from suffocating gas mixtures. — p.1: "The inner ear appears to play a key role in arousal from suffocating gas mixtures that has not been previously identified"

- **suid_literature_abstracts.C23** [finding] Swallow-related submental complex duration and amplitude were significantly decreased in both Mecp2-/y and Mecp2+/- mice compared to wild-type. — p.1: "swallow-related submental complex duration and amplitude were significantly decreased in both mecp2-/y and mecp2+/- mice compared to wild-type, likely due to reduced motor unit activation"

- **suid_literature_abstracts.C24** [finding] Cholinergic immunoreactivity in the hypoglossal, facial, and trigeminal motor nuclei was decreased in postsymptomatic Mecp2-deficient mice. — p.1: "cholinergic staining in hypoglossal, facial, and trigeminal nuclei were decreased"

- **suid_literature_abstracts.C25** [finding] The transition time from inspiration to swallow was significantly increased in Mecp2-/y mice. — p.1: "We also observed a significant increase in the transition time from inspiration to swallow, swallow to the subsequent inspiration, and impaired post swallow respiratory rhythm resumption in Mecp2-/y, but not Mecp2+/- mice"

- **suid_literature_abstracts.C26** [finding] The study investigates the role of PiCo and preBötC in respiratory-sympathetic coupling under control conditions and following exposure to chronic intermittent hypoxia (CIH). — p.1: "This study investigates the role of the postinspiratory complex (PiCo) and preBötzinger complex (preBötC) in respiratory-sympathetic coupling under control conditions and following exposure to chronic intermittent hypoxia (CIH) for 21 days (5% O2-80 bouts/day)."

- **suid_literature_abstracts.C27** [finding] Baseline sympathetic nerve activity increased, breathing frequency increased, and expiratory time decreased following CIH exposure. — p.1: "Following CIH exposure, baseline cSN activity increased, breathing frequency increased, and expiratory time decreased."

- **suid_literature_abstracts.C28** [finding] Stimulation of PiCo specific cholinergic-glutamatergic neurons caused a sympathetic burst during all phases of the respiratory cycle in control mice but only during postinspiration and late expiration in CIH mice. — p.1: "In control mice, stimulating PiCo specific cholinergic-glutamatergic neurons caused a sympathetic burst during all phases of the respiratory cycle, whereas optogenetic activation of cholinergic-glutamatergic PiCo neurons in CIH mice increased sympathetic activity only during postinspiration and late expiration."

- **suid_literature_abstracts.C29** [finding] Stimulation of glutamatergic PiCo neurons increased cervical sympathetic nerve (cSN) activity during the postinspiratory phase in both control and CIH mice. — p.1: "Stimulation of glutamatergic PiCo neurons increased cSN activity during the postinspiratory phase in control and CIH mice."

- **suid_literature_abstracts.C30** [finding] Optogenetic stimulation of ChAT containing neurons in the PiCo area did not affect sympathetic activity under either control or CIH conditions. — p.1: "Optogenetic stimulation of ChAT containing neurons in the PiCo area did not affect sympathetic activity under control or CIH conditions."

- **suid_literature_abstracts.C31** [finding] Stimulation of Dbx1 or Vglut2 neurons in preBötC evoked an inspiration and a concomitant cSN burst under both control and CIH conditions. — p.1: "Stimulating Dbx1 or Vglut2 neurons in preBötC evoked an inspiration and a concomitant cSN burst under control and CIH conditions."

- **suid_literature_abstracts.C32** [finding] PiCo and preBötC contribute to respiratory-sympathetic coupling, which is altered by chronic intermittent hypoxia (CIH). — p.1: "Taken together, these results suggest that PiCo and preBötC contribute to respiratory-sympathetic coupling, which is altered by CIH, and may contribute to the hypertension observed in patients with OSA."

- **suid_literature_abstracts.C33** [hypothesis] It is hypothesized that adult neurogenesis in the dentate gyrus maintains normal hippocampal function. — p.1: "It is hypothesized that adult neurogenesis in the dentate gyrus is an ongoing process that maintains normal hippocampal function in many mammalian species, including humans."

- **suid_literature_abstracts.C34** [method] The study used a murine model to examine the impact of chronic intermittent hypoxia (IH) on adult neurogenesis and synaptic plasticity in the dentate gyrus over 30 days. — p.1: "Using a murine model, we examined the impact of 30 d of IH (IH30) on adult neurogenesis and synaptic plasticity in the dentate gyrus."

- **suid_literature_abstracts.C35** [finding] Chronic intermittent hypoxia did not affect paired-pulse facilitation but suppressed long-term potentiation (LTP). — p.1: "Although IH30 did not affect paired-pulse facilitation, IH30 suppressed long-term potentiation (LTP)."

- **suid_literature_abstracts.C36** [finding] Chronic intermittent hypoxia increased the number of proliferating Sox2+ neural progenitor cells but reduced the number of doublecortin-positive neurons. — p.1: "IH30 increased the number of proliferating Sox2+ neural progenitor cells in the subgranular zone yet reduced the number of doublecortin-positive neurons."

- **suid_literature_abstracts.C37** [finding] Chronic intermittent hypoxia increased radial glial cell proportion and decreased adult-born neuron proportion in the dentate gyrus. — p.1: "cell lineage tracing revealed that IH30 increased the proportion of radial glial cells in the subgranular zone, yet decreased the proportion of adult-born neurons in the dentate gyrus"

- **suid_literature_abstracts.C38** [finding] Antioxidant treatment mitigated chronic intermittent hypoxia-dependent suppression of LTP and prevented loss of adult-born neurons. — p.1: "While administration of a superoxide anion scavenger during IH did not prevent neural progenitor cell proliferation, it mitigated the IH-dependent suppression of LTP and prevented adult-born neuron loss"

- **suid_literature_abstracts.C39** [hypothesis] Breathing patterns in the first hour after birth predict survival in premature mice. — p.1: "We hypothesized that breathing patterns during the first hour of life would be predictive of survival in an animal model of prematurity."

- **suid_literature_abstracts.C40** [method] The study used plethysmography to measure breathing patterns in mice born at term, delivered prematurely after low-dose lipopolysaccharide (LPS) injection, or via caesarian section. — p.1: "Using plethysmography, we measured breathing patterns during the first hour after birth in mice born at term (Term 19.5), delivered prematurely on gestational day 18.5 following administration of low-dose lipopolysaccharide (LPS; 0.14 mg/kg) to pregnant dams (LPS 18.5), or delivered on gestational day 18.7 or 17.5 by caesarian section (C-S 18.5 and C-S 17.5, respectively)."

- **suid_literature_abstracts.C41** [finding] Mortality was significantly increased in premature pups born at gestational day 18.5 after maternal LPS injection. — p.1: "However, in premature pups born at the same gestational age (day 18.5) in response to maternal LPS injection, mortality was significantly increased."

- **suid_literature_abstracts.C42** [finding] Mice that survived had higher birth weights and showed eupneic or gasping activity transitioning into normal breathing. — p.1: "Overall, mice that survived had higher birth weights and showed eupneic or gasping activity that was able to transition to normal breathing."

- **suid_literature_abstracts.C43** [finding] Mice that did not survive exhibited distinct large amplitude breaths at low frequency, failing to transition into normal breathing. — p.1: "In contrast, mice that did not survive showed distinct, large amplitude, long-lasting breaths that occurred at low frequency and did not transition into eupnea."

- **suid_literature_abstracts.C44** [hypothesis] Local inhibition destabilizes rhythmogenesis while long-range inhibition stabilizes it in the pre-Bötzinger complex inspiratory microcircuit. — p.1: "Increasing inhibition within the microcircuit results in a limited number of out-of-phase neurons before rhythmicity and synchrony degenerate. Thus unstructured local inhibition is destabilizing and cannot support the generation of more than one rhythm."

- **suid_literature_abstracts.C45** [method] The study used a biophysical model to investigate the roles of local and long-range inhibition in the respiratory network, supported by in vitro recordings from mouse pre-Bötzinger complex. — p.1: "We use a biophysical model to investigate the different roles of local and long-range inhibition in the respiratory network, a key component of which is the pre-Bötzinger complex inspiratory microcircuit."

- **suid_literature_abstracts.C46** [finding] Partial excitation block leads to increased rhythmic variability but recovers after blockade of inhibition in the pre-Bötzinger complex. — p.1: "Partial excitation block leads to increased rhythmic variability, but this recovers after blockade of inhibition."

- **suid_literature_abstracts.C47** [hypothesis] Chronic intermittent hypoxia differentially impacts inspiratory activity states at the level of the pre-Bötzinger complex. — p.1: "The preBötzinger complex (preBötC) is a medullary brainstem network crucially involved in the generation of different inspiratory rhythms. In the isolated brainstem slice, the preBötC reconfigures to produce different rhythms that we refer to as 'fictive eupnea' under baseline conditions (i.e., carbogen), and 'fictive gasping' in hypoxia."

- **suid_literature_abstracts.C48** [method] The study examined the impact of chronic intermittent hypoxia on various dynamic aspects of rhythmogenesis during baseline conditions, transition to hypoxia, and throughout hypoxia. — p.1: "We recently demonstrated that fictive eupnea is irregular following exposure to chronic intermittent hypoxia (CIH). However, it is unknown how CIH impacts fictive gasping. To address this, brain slices containing the preBötC were prepared from control and CIH exposed mice. Electrophysiological recordings of rhythmogenesis were obtained during the perihypoxic interval."

- **suid_literature_abstracts.C49** [finding] Chronic intermittent hypoxia increased irregularity score (IrS) and fluctuation value (χ) but did not affect sample entropy (sENT) of amplitude in baseline conditions. — p.1: "In baseline conditions, CIH increased IrS of amplitude (0.21 ± 0.2) and χ of amplitude (0.34 ± 0.02) but did not affect sENT of amplitude."

- **suid_literature_abstracts.C50** [finding] During hypoxia, all slices from CIH-exposed mice exhibited rhythms throughout the interval, while only a fraction of control rhythms maintained rhythmicity. — p.1: "While 29% of control rhythms maintained rhythmicity throughout hypoxia, all slices from CIH exposed mice exhibited rhythms throughout the hypoxic interval."

- **suid_literature_abstracts.C51** [hypothesis] Progesterone pretreatment ameliorates detrimental effects of lipopolysaccharide (LPS)-induced inflammation on cortical neurogenesis in mice. — p.1: "Our objective was to determine if progesterone pretreatment could ameliorate the detrimental effects of lipopolysaccharide (LPS)-induced inflammation on cortical neurogenesis."

- **suid_literature_abstracts.C52** [method] The study used two-color immunofluorescence with primary antibodies to assess Tbr2 intermediate neural progenitor cell density, microglia activation, and cell death rates after LPS exposure. — p.1: "Two-color immunofluorescence was performed with primary antibodies T-box transcription factor 2 (Tbr2), ionized calcium binding adapter molecule 1 (Iba1), cleaved caspase 3 (CC3), and 5-bromo-2'-deoxyuridine (BrdU). Cells were counted, and statistical analysis was determined using analysis of variance and Tukey-Kramer method."

- **suid_literature_abstracts.C53** [finding] Lipopolysaccharide exposure reduced Tbr2 intermediate neural progenitor cell density but increased microglia activation and cell death rates. — p.1: "The Tbr2 intermediate neural progenitor cell density decreased after LPS exposure (P = .0022). After LPS exposure, microglia displayed an activated phenotype, and cell density was increased (P < .001). Cell death rates were low among study groups but was increased in LPS exposure groups compared to progesterone alone (P = .0015)."

- **suid_literature_abstracts.C54** [finding] Pre-exposure with progesterone statistically increased Tbr2 intermediate neural progenitors and protected against cell death induced by LPS. — p.1: "Pre-exposure to progesterone statistically increased Tbr2 intermediate neural progenitors compared to LPS treatment alone and was similar to controls (P = .0022). After LPS exposure, microglia displayed an activated phenotype, and cell density was increased (P < .001). Cell death rates were low among study groups but was increased in LPS exposure groups compared to progesterone alone (P = .0015)."

- **suid_literature_abstracts.C55** [hypothesis] Chronic intermittent hypoxia alters local respiratory circuit function at the level of the pre-Bötzinger complex. — p.1: "The preBötzinger complex (preBötC) is a pre-motor respiratory network critical for inspiratory rhythm generation. Here, we test the hypothesis that CIH increases irregular output from the isolated preBötC, which can be mitigated by antioxidant treatment."

- **suid_literature_abstracts.C56** [method] The study used electrophysiological recordings to examine burst-to-burst irregularity in period and amplitude of rhythmogenesis following chronic intermittent hypoxia exposure. — p.1: "Electrophysiological recordings from brainstem slices revealed that CIH enhanced burst-to-burst irregularity in period and/or amplitude."

- **suid_literature_abstracts.C57** [finding] Chronic intermittent hypoxia increased lipid peroxidation in the pre-Bötzinger complex, which was reduced by antioxidant treatment. — p.1: "CIH increased the degree of lipid peroxidation in the preBötC and treatment with the antioxidant, 5,10,15,20-Tetrakis (1-methylpyridinium-4-yl)-21H,23H-porphyrin manganese(III) pentachloride (MnTMPyP), reduced CIH-mediated irregularities on the network rhythm and improved transmission of preBötC to the XIIn."

- **suid_literature_abstracts.C58** [hypothesis] Excessive sensory stimulation during development alters neural plasticity and vulnerability to cocaine in mice. — p.1: "Early life experiences affect the formation of neuronal networks, which can have a profound impact on brain function and behavior later in life. Previous work has shown that mice exposed to excessive sensory stimulation during development are hyperactive and novelty seeking, and display impaired cognition compared with controls."

- **suid_literature_abstracts.C59** [method] The study assessed the reinforcing properties of cocaine and underlying circuitry in CD-1 mice exposed to excessive sensory stimulation during development. — p.1: "In this study, we addressed the issue of whether excessive sensory stimulation during development could alter behaviors related to addiction and underlying circuitry in CD-1 mice."

- **suid_literature_abstracts.C60** [finding] Mice exposed to excessive sensory stimulation showed enhanced reinforcing properties of cocaine but impaired persistence of cocaine-induced locomotor sensitization. — p.1: "We found that the reinforcing properties of cocaine were significantly enhanced in mice exposed to excessive sensory stimulation. Moreover, although these mice displayed hyperactivity that became more pronounced over time, they showed impaired persistence of cocaine-induced locomotor sensitization."

- **suid_literature_abstracts.C61** [finding] Excessive sensory stimulation altered glutamatergic transmission in the nucleus accumbens and amygdala, affecting behaviors related to addiction. — p.1: "These behavioral effects were associated with alterations in glutamatergic transmission in the nucleus accumbens and amygdala."

- **suid_literature_abstracts.C62** [hypothesis] Microcircuits in respiratory rhythm generation share commonalities with other rhythm generating networks, including synaptic inhibition and excitation roles. — p.1: "Rhythmicity is critical for the generation of rhythmic behaviors and higher brain functions. This review discusses common mechanisms of rhythm generation, including the role of synaptic inhibition and excitation, with a focus on the mammalian respiratory network."


## B. Data sources and concept map
- `cdc_linkco15`: CDC linked birth/infant death public-use file guide, 2015 — 270 documented variables.

- `cdc_natl15`: CDC natality public-use file guide, 2015 — 245 documented variables.

- `cdc_codenames`: CDC birth/death file variable names and labels (analysis extract) — 223 documented variables.

- `ncfrp_v51`: National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1 — 4422 documented variables.

- `prams_p8_arf`: PRAMS Phase 8 Analytic Research File codebook — 485 documented variables.

- `prams_p8_std2`: PRAMS Phase 8 Standard Section II codebook — 4 documented variables.

- `prams_p7_arf`: PRAMS Phase 7 Analytic Research File codebook — 386 documented variables.


| Concept | Source | Variable | Compatibility | Rationale |
|---|---|---|---|---|
| Sudden unexpected infant death (SUID) | cdc_linkco15 | UCOD | direct | [review 2026-11-11] ICD-10 underlying cause of death; permits the exact R95/R99/W75 definition. |
| Sudden unexpected infant death (SUID) | cdc_linkco15 | UCODR130 | direct | The variable UCODR130 is a 130 Infant Cause Recode which includes codes for Sudden infant death syndrome (R95), Accidental suffocation and strangulation in bed (W75), or Other ill-defined and unspecified causes of mortality (R99). |
| Sudden unexpected infant death (SUID) | cdc_natl15 | — | none | The CDC natality public-use file does not contain specific variables for SUID outcomes. |
| Sudden unexpected infant death (SUID) | ncfrp_v51 | REGsuidcat | direct | [review 2026-11-11] SUID Case Registry categorization of the death. |
| Sudden unexpected infant death (SUID) | ncfrp_v51 | CAUicdcode | direct | [review 2026-11-11] ICD-10 cause-of-death code from vital records; permits R95/R99/W75. |
| Sudden unexpected infant death (SUID) | ncfrp_v51 | CAUdcimmcau | proxy | [review 2026-11-11] Immediate cause of death from the death certificate; not coded to the SUID definition. |
| Sudden unexpected infant death (SUID) | prams_p8_arf | — | none | The PRAMS data does not contain specific variables for SUID outcomes. |
| Sudden unexpected infant death (SUID) | prams_p8_std2 | — | none | The PRAMS data source does not contain information on cause of death. |
| Sudden unexpected infant death (SUID) | prams_p7_arf | — | none | The PRAMS data does not contain specific variables for SUID outcomes. |
| Infant sex | cdc_linkco15 | SEX | direct | [review 2026-11-11] Sex of infant. |
| Infant sex | cdc_natl15 | SEX | direct | [review 2026-11-11] Sex of infant. |
| Infant sex | ncfrp_v51 | INFsex | direct | [review 2026-11-11] Sex of the deceased child. RES1sex/RES2sex (caregivers), ACTcausex (person who caused the death) and INFgenderid (gender identity) removed. |
| Infant sex | prams_p8_arf | SEX | direct | [review 2026-11-11] Gender of infant. |
| Infant sex | prams_p8_std2 | — | none | [review 2026-11-11] No matching variable. |
| Infant sex | prams_p7_arf | SEX | direct | [review 2026-11-11] Gender of infant. |
| Postconceptional age (PCA) | cdc_linkco15 | COMBGEST | derived | [review 2026-11-11] PCA (weeks) = COMBGEST + AGED/7. |
| Postconceptional age (PCA) | cdc_linkco15 | AGED | derived | [review 2026-11-11] Age at death in days; PCA = COMBGEST + AGED/7. |
| Postconceptional age (PCA) | cdc_natl15 | COMBGEST | derived | [review 2026-11-11] Births by gestational age, the person-time denominator by PCA; natality has no death age. |
| Postconceptional age (PCA) | ncfrp_v51 | INFgestage | derived | [review 2026-11-11] PCA (weeks) = INFgestage + INFdayslive/7. |
| Postconceptional age (PCA) | ncfrp_v51 | INFdayslive | derived | [review 2026-11-11] Days lived; PCA = INFgestage + INFdayslive/7. |
| Postconceptional age (PCA) | prams_p8_arf | — | none | PRAMS does not provide a direct measure of postconceptional age. |
| Postconceptional age (PCA) | prams_p8_std2 | — | none | PRAMS does not provide postconceptional age as a variable in the provided list. |
| Postconceptional age (PCA) | prams_p7_arf | — | none | PRAMS does not provide variables to calculate postconceptional age directly. |
| Maternal smoking during pregnancy | cdc_linkco15 | CIG_REC | direct | [review 2026-11-11] Any cigarette smoking in pregnancy (Y/N). |
| Maternal smoking during pregnancy | cdc_natl15 | CIG_REC | direct | [review 2026-11-11] Any cigarette smoking in pregnancy (Y/N). |
| Maternal smoking during pregnancy | ncfrp_v51 | INFsmanytime | direct | The INFsmanytime variable in the NCFRP data source captures whether the mother smoked at any time during pregnancy. |
| Maternal smoking during pregnancy | prams_p8_arf | MOMSMOKE | direct | Variable 'MOMSMOKE' indicates whether the mother smoked during pregnancy. |
| Maternal smoking during pregnancy | prams_p8_std2 | — | none | PRAMS does not provide maternal smoking status as a specific variable in the provided list. |
| Maternal smoking during pregnancy | prams_p7_arf | MOMSMOKE | direct | The variable 'MOMSMOKE' indicates whether the mother smoked during any trimester of pregnancy. |
| Preterm birth | cdc_linkco15 | GESTREC3 | derived | Derived from GESTREC3, which is a recode of gestational age. Preterm birth can be derived by comparing the value to 37 weeks. |
| Preterm birth | cdc_natl15 | GESTREC3 | direct | The variable 'GESTREC3' categorizes gestational age into preterm and full-term categories. |
| Preterm birth | ncfrp_v51 | INFgestage | derived | [review 2026-11-11] Preterm = INFgestage < 37. |
| Preterm birth | prams_p8_arf | GEST_WK_PU | derived | [review 2026-11-11] Preterm = GEST_WK_PU < 37. |
| Preterm birth | prams_p8_std2 | — | none | PRAMS does not provide preterm birth information as a specific variable in the provided list. |
| Preterm birth | prams_p7_arf | GEST_WK_PU | derived | [review 2026-11-11] Preterm = GEST_WK_PU < 37. |
| Breastfeeding status at discharge | cdc_linkco15 | BFED | direct | The variable BFED indicates whether the infant was being breastfed at discharge. |
| Breastfeeding status at discharge | cdc_natl15 | BFED | direct | The variable 'BFED' indicates whether the infant was breastfed at hospital discharge. |
| Breastfeeding status at discharge | ncfrp_v51 | INFbreast | proxy | [review 2026-11-11] Ever breastfed, not status at discharge. |
| Breastfeeding status at discharge | prams_p8_arf | BF5EVER_RAW | proxy | [review 2026-11-11] Ever breastfed, not status at discharge. |
| Breastfeeding status at discharge | prams_p8_std2 | — | none | PRAMS does not provide breastfeeding status at discharge as a specific variable in the provided list. |
| Breastfeeding status at discharge | prams_p7_arf | BF5EVER_RAW | proxy | [review 2026-11-11] Ever breastfed, not status at discharge. |
| postconceptional age | cdc_linkco15 | COMBGEST | derived | [review 2026-11-11] PCA (weeks) = COMBGEST + AGED/7. |
| postconceptional age | cdc_linkco15 | AGED | derived | [review 2026-11-11] Age at death in days; PCA = COMBGEST + AGED/7. |
| postconceptional age | cdc_natl15 | COMBGEST | derived | [review 2026-11-11] Births by gestational age, the person-time denominator by PCA; natality has no death age. |
| postconceptional age | ncfrp_v51 | INFgestage | derived | [review 2026-11-11] PCA (weeks) = INFgestage + INFdayslive/7. |
| postconceptional age | ncfrp_v51 | INFdayslive | derived | [review 2026-11-11] Days lived; PCA = INFgestage + INFdayslive/7. |
| postconceptional age | prams_p8_arf | — | none | PRAMS does not provide a direct measure of postconceptional age. |
| postconceptional age | prams_p8_std2 | — | none | PRAMS does not provide postconceptional age as a specific variable in the provided list. |
| postconceptional age | prams_p7_arf | — | none | PRAMS does not provide variables to calculate postconceptional age directly. |
| sex (male, female) | cdc_linkco15 | SEX | direct | [review 2026-11-11] Sex of infant. |
| sex (male, female) | cdc_natl15 | SEX | direct | [review 2026-11-11] Sex of infant. |
| sex (male, female) | ncfrp_v51 | INFsex | direct | [review 2026-11-11] Sex of the deceased child. RES1sex/RES2sex (caregivers), ACTcausex (person who caused the death) and INFgenderid (gender identity) removed. |
| sex (male, female) | prams_p8_arf | SEX | direct | [review 2026-11-11] Gender of infant. |
| sex (male, female) | prams_p8_std2 | — | none | [review 2026-11-11] No matching variable. |
| sex (male, female) | prams_p7_arf | SEX | direct | [review 2026-11-11] Gender of infant. |
| year of birth or death | cdc_linkco15 | DOB_YY | direct | [review 2026-11-11] Birth year. Death year (DOD_YY) is in the guide but not yet extracted. |
| year of birth or death | cdc_natl15 | DOB_YY | direct | [review 2026-11-11] Birth year. Death year (DOD_YY) is in the guide but not yet extracted. |
| year of birth or death | ncfrp_v51 | INFdobyear | direct | The variables INFdobyear and INFdodyear directly correspond to the year of birth and death respectively. |
| year of birth or death | ncfrp_v51 | INFdodyear | direct | The variables INFdobyear and INFdodyear directly correspond to the year of birth and death respectively. |
| year of birth or death | prams_p8_arf | — | none | PRAMS does not provide a direct measure of year of birth or death. |
| year of birth or death | prams_p8_std2 | — | none | PRAMS does not provide year of birth or death as a specific variable in the provided list. |
| year of birth or death | prams_p7_arf | — | none | PRAMS does not provide a direct variable for year of birth or death; it would need to be derived from other variables. |
| SUID | cdc_linkco15 | UCOD | direct | [review 2026-11-11] ICD-10 underlying cause of death; permits the exact R95/R99/W75 definition. |
| SUID | cdc_linkco15 | UCODR130 | direct | The variable UCODR130 is a 130 Infant Cause Recode which includes codes for Sudden infant death syndrome (R95), Accidental suffocation and strangulation in bed (W75), or Other ill-defined and unspecified causes of mortality (R99). |
| SUID | cdc_natl15 | — | none | The CDC natality public-use file does not contain specific variables for SUID outcomes. |
| SUID | ncfrp_v51 | REGsuidcat | direct | [review 2026-11-11] SUID Case Registry categorization of the death. |
| SUID | ncfrp_v51 | CAUicdcode | direct | [review 2026-11-11] ICD-10 cause-of-death code from vital records; permits R95/R99/W75. |
| SUID | ncfrp_v51 | CAUdcimmcau | proxy | [review 2026-11-11] Immediate cause of death from the death certificate; not coded to the SUID definition. |
| SUID | prams_p8_arf | — | none | The PRAMS data does not contain specific variables for SUID outcomes. |
| SUID | prams_p8_std2 | — | none | PRAMS does not contain information on cause of death or SUID. |
| SUID | prams_p7_arf | — | none | PRAMS does not contain specific variables for SUID outcomes. |
| bed sharing | cdc_linkco15 | — | none | The data source does not contain a variable for bed sharing. |
| bed sharing | cdc_natl15 | — | none | There is no variable in the CDC natality public-use file that captures bed-sharing behavior. |
| bed sharing | ncfrp_v51 | CIRsamesurf | direct | The variable CIRsamesurf indicates whether the child was sleeping on the same surface with another person or animal, which is a direct measure of bed sharing. |
| bed sharing | ncfrp_v51 | CIRwadult | direct | [review 2026-11-11] Same sleep surface with adult(s). |
| bed sharing | prams_p8_arf | SLEEPOWN_RAW | proxy | [review 2026-11-11] How often baby sleeps alone; inverse proxy for bed sharing in live infants. |
| bed sharing | prams_p8_std2 | — | none | PRAMS does not provide bed-sharing status as a specific variable in the provided list. |
| bed sharing | prams_p7_arf | — | none | [review 2026-11-11] No matching variable. |
| birthweight (low, non-low) | cdc_linkco15 | BWTR4 | derived | [review 2026-11-11] Low birthweight = levels 1-2 (<2,500 g). |
| birthweight (low, non-low) | cdc_natl15 | BWTR4 | derived | [review 2026-11-11] Low birthweight = levels 1-2 (<2,500 g). |
| birthweight (low, non-low) | ncfrp_v51 | INFbirthwtcat | direct | [review 2026-11-11] Birth weight category. |
| birthweight (low, non-low) | ncfrp_v51 | INF3birthwtcat | direct | [review 2026-11-11] Birth weight category (second form section). |
| birthweight (low, non-low) | prams_p8_arf | GRAM_NAPHSIS | derived | [review 2026-11-11] 250-g intervals; low = midpoint < 2,500 g. |
| birthweight (low, non-low) | prams_p8_std2 | — | none | [review 2026-11-11] No matching variable. |
| birthweight (low, non-low) | prams_p7_arf | GRAM_NAPHSIS | derived | [review 2026-11-11] 250-g intervals; low = midpoint < 2,500 g. |
| PCA (postconceptional age) | cdc_linkco15 | COMBGEST | derived | [review 2026-11-11] PCA (weeks) = COMBGEST + AGED/7. |
| PCA (postconceptional age) | cdc_linkco15 | AGED | derived | [review 2026-11-11] Age at death in days; PCA = COMBGEST + AGED/7. |
| PCA (postconceptional age) | cdc_natl15 | COMBGEST | derived | [review 2026-11-11] Births by gestational age, the person-time denominator by PCA; natality has no death age. |
| PCA (postconceptional age) | ncfrp_v51 | INFgestage | derived | [review 2026-11-11] PCA (weeks) = INFgestage + INFdayslive/7. |
| PCA (postconceptional age) | ncfrp_v51 | INFdayslive | derived | [review 2026-11-11] Days lived; PCA = INFgestage + INFdayslive/7. |
| PCA (postconceptional age) | prams_p8_arf | — | none | PRAMS does not provide a direct measure of postconceptional age. |
| PCA (postconceptional age) | prams_p8_std2 | — | none | PRAMS does not provide postconceptional age as a specific variable in the provided list. |
| PCA (postconceptional age) | prams_p7_arf | — | none | PRAMS does not provide variables to calculate postconceptional age directly. |
| maternal smoking status (smoking, non-smoking) | cdc_linkco15 | CIG_REC | direct | [review 2026-11-11] Any cigarette smoking in pregnancy (Y/N). |
| maternal smoking status (smoking, non-smoking) | cdc_natl15 | CIG_REC | direct | [review 2026-11-11] Any cigarette smoking in pregnancy (Y/N). |
| maternal smoking status (smoking, non-smoking) | ncfrp_v51 | INFsmanytime | direct | The INFsmanytime variable captures whether the mother smoked at any time during pregnancy. |
| maternal smoking status (smoking, non-smoking) | prams_p8_arf | MOMSMOKE | direct | Variable 'MOMSMOKE' indicates whether the mother smoked during pregnancy. |
| maternal smoking status (smoking, non-smoking) | prams_p8_std2 | — | none | PRAMS does not provide maternal smoking status as a specific variable in the provided list. |
| maternal smoking status (smoking, non-smoking) | prams_p7_arf | MOMSMOKE | direct | The variable 'MOMSMOKE' indicates whether the mother smoked during pregnancy. |
| Maternal prepregnancy body mass index (BMI) | cdc_linkco15 | BMI | direct | [review 2026-11-11] Prepregnancy BMI. |
| Maternal prepregnancy body mass index (BMI) | cdc_linkco15 | BMI_R | direct | [review 2026-11-11] Prepregnancy BMI recode. |
| Maternal prepregnancy body mass index (BMI) | cdc_natl15 | BMI | direct | [review 2026-11-11] Prepregnancy BMI. |
| Maternal prepregnancy body mass index (BMI) | cdc_natl15 | BMI_R | direct | [review 2026-11-11] Prepregnancy BMI recode. |
| Maternal prepregnancy body mass index (BMI) | ncfrp_v51 | INF4mombmi | direct | [review 2026-11-11] Mother's BMI, computed from height and weight. |
| Maternal prepregnancy body mass index (BMI) | prams_p8_arf | MOM_BMI_BC | direct | [review 2026-11-11] Maternal BMI from the birth certificate. |
| Maternal prepregnancy body mass index (BMI) | prams_p8_arf | MOM_BMI | proxy | [review 2026-11-11] Maternal BMI from the questionnaire (self-report). |
| Maternal prepregnancy body mass index (BMI) | prams_p8_std2 | — | none | PRAMS does not provide maternal BMI information as a specific variable in the provided list. |
| Maternal prepregnancy body mass index (BMI) | prams_p7_arf | MOM_BMI_BC | direct | [review 2026-11-11] Maternal BMI from the birth certificate. |
| Maternal prepregnancy body mass index (BMI) | prams_p7_arf | MOM_BMI | proxy | [review 2026-11-11] Maternal BMI from the questionnaire (self-report). |
| Gestational age at birth | cdc_linkco15 | COMBGEST | direct | The variable COMBGEST is a combined gestational age in weeks. |
| Gestational age at birth | cdc_natl15 | COMBGEST | direct | The variable 'COMBGEST' provides the combined gestational age in weeks. |
| Gestational age at birth | ncfrp_v51 | INFgestage | direct | The INFgestage variable captures gestational age in weeks, which is directly relevant to the concept. |
| Gestational age at birth | prams_p8_arf | GEST_WK_PU | proxy | [review 2026-11-11] Clinical estimate in weeks, top/bottom coded at 27 and 43. |
| Gestational age at birth | prams_p8_std2 | — | none | PRAMS does not provide gestational age information as a specific variable in the provided list. |
| Gestational age at birth | prams_p7_arf | GEST_WK_PU | proxy | [review 2026-11-11] Clinical estimate in weeks, top/bottom coded at 27 and 43. |
| Maternal infections in pregnancy | cdc_linkco15 | IP_CHLAM | direct | [review 2026-11-11] Chlamydia in pregnancy. |
| Maternal infections in pregnancy | cdc_linkco15 | IP_GON | direct | [review 2026-11-11] Gonorrhea in pregnancy. |
| Maternal infections in pregnancy | cdc_linkco15 | IP_HEPC | direct | [review 2026-11-11] Hepatitis C in pregnancy. |
| Maternal infections in pregnancy | cdc_natl15 | IP_CHLAM | direct | [review 2026-11-11] Chlamydia in pregnancy. |
| Maternal infections in pregnancy | cdc_natl15 | IP_GON | direct | [review 2026-11-11] Gonorrhea in pregnancy. |
| Maternal infections in pregnancy | cdc_natl15 | IP_HEPC | direct | [review 2026-11-11] Hepatitis C in pregnancy. |
| Maternal infections in pregnancy | ncfrp_v51 | INF3chlamydia | direct | [review 2026-11-11] Pregnancy complication: chlamydia. |
| Maternal infections in pregnancy | ncfrp_v51 | INF3gonorrhea | direct | [review 2026-11-11] Pregnancy complication: gonorrhea. NCFRP has no hepatitis C item. |
| Maternal infections in pregnancy | prams_p8_arf | — | none | PRAMS does not provide specific variables for maternal infections during pregnancy. |
| Maternal infections in pregnancy | prams_p8_std2 | — | none | PRAMS does not provide maternal infection status as a specific variable in the provided list. |
| Maternal infections in pregnancy | prams_p7_arf | — | none | PRAMS does not provide specific variables for maternal infections during pregnancy. |
| Age of death in SUID cases | cdc_linkco15 | AGED | direct | [review 2026-11-11] Age at death in days. |
| Age of death in SUID cases | cdc_natl15 | — | none | There is no variable that captures age at death for SUID cases. |
| Age of death in SUID cases | ncfrp_v51 | INFdayslive | direct | The variable INFdayslive directly corresponds to the number of days lived, which can be used to determine age at death. |
| Age of death in SUID cases | prams_p8_arf | — | none | The PRAMS data does not contain specific variables for age at death in SUID cases. |
| Age of death in SUID cases | prams_p8_std2 | — | none | PRAMS does not provide age at death information as a specific variable in the provided list. |
| Age of death in SUID cases | prams_p7_arf | — | none | PRAMS does not contain specific variables for age at death in SUID cases. |
| Geographic location | cdc_linkco15 | MRCNTYFIPS | proxy | The variable MRCNTYFIPS is the FIPS County code for mother’s residence, which can be used to infer geographic location. |
| Geographic location | cdc_natl15 | OCNTYFIPS | proxy | The variable 'OCNTYFIPS' provides the FIPS county code, which can be used to infer geographic location. |
| Geographic location | ncfrp_v51 | INFaddrst | direct | The variables INFaddrst and INFdthstate directly correspond to the state of residence and death respectively. |
| Geographic location | ncfrp_v51 | INFdthstate | direct | The variables INFaddrst and INFdthstate directly correspond to the state of residence and death respectively. |
| Geographic location | ncfrp_v51 | INCstate | proxy | The data source contains variables capturing state and county of incident, which can be used as a proxy for geographic location. |
| Geographic location | prams_p8_arf | STATE | proxy | Variable 'STATE' provides the state of residence, which can be used as a proxy for geographic location. |
| Geographic location | prams_p8_std2 | — | none | PRAMS does not provide geographic location information as a specific variable in the provided list. |
| Geographic location | prams_p7_arf | STATE | proxy | The variable 'STATE' indicates the state of residence, which can be used as a proxy for geographic location. |
| chronological age | cdc_linkco15 | AGED | direct | [review 2026-11-11] Age at death in days. |
| chronological age | cdc_natl15 | — | none | There is no variable that directly measures chronological age; it would need to be derived from birth date and current date. |
| chronological age | ncfrp_v51 | INFdayslive | direct | [review 2026-11-11] Days lived (from DOB and DOD). |
| chronological age | prams_p8_arf | — | none | PRAMS does not provide a direct measure of chronological age. |
| chronological age | prams_p8_std2 | — | none | PRAMS does not provide chronological age information as a specific variable in the provided list. |
| chronological age | prams_p7_arf | — | none | PRAMS does not provide a direct variable for chronological age; it would need to be derived from other variables. |
| sex | cdc_linkco15 | SEX | direct | [review 2026-11-11] Sex of infant. |
| sex | cdc_natl15 | SEX | direct | [review 2026-11-11] Sex of infant. |
| sex | ncfrp_v51 | INFsex | direct | [review 2026-11-11] Sex of the deceased child. RES1sex/RES2sex (caregivers), ACTcausex (person who caused the death) and INFgenderid (gender identity) removed. |
| sex | prams_p8_arf | SEX | direct | [review 2026-11-11] Gender of infant. |
| sex | prams_p8_std2 | — | none | [review 2026-11-11] No matching variable. |
| sex | prams_p7_arf | SEX | direct | [review 2026-11-11] Gender of infant. |
| birthweight | cdc_linkco15 | BWTR4 | derived | [review 2026-11-11] Low birthweight = levels 1-2 (<2,500 g). |
| birthweight | cdc_natl15 | BWTR4 | derived | [review 2026-11-11] Low birthweight = levels 1-2 (<2,500 g). |
| birthweight | ncfrp_v51 | INFbirthwtcat | direct | [review 2026-11-11] Birth weight category. |
| birthweight | ncfrp_v51 | INF3birthwtcat | direct | [review 2026-11-11] Birth weight category (second form section). |
| birthweight | prams_p8_arf | GRAM_NAPHSIS | derived | [review 2026-11-11] 250-g intervals; low = midpoint < 2,500 g. |
| birthweight | prams_p8_std2 | — | none | [review 2026-11-11] No matching variable. |
| birthweight | prams_p7_arf | GRAM_NAPHSIS | derived | [review 2026-11-11] 250-g intervals; low = midpoint < 2,500 g. |

## C. Knowledge gaps
### G1. Whether maternal prepregnancy obesity modifies SUID incidence differently across postconceptional age (PCA) windows has not been examined.
- Rationale: Maternal BMI is an established SUID risk factor in the literature, but neither manuscript included it. Estimating its association separately in the early rising (36-42 weeks) and late declining (>=47 weeks) PCA windows tests whether this risk is developmentally timed, extending the PCA framework to a new exposure.
- Prior art: The literature abstracts report that maternal obesity raises SUID risk, increasing with BMI (suid_literature_abstracts.C10), without any developmental alignment. The PCA manuscript defined early and late PCA windows (SUID_manuscript_v9_clean.C5) but modelled sex and smoking, not maternal BMI.
- Supporting claims: suid_literature_abstracts.C10, SUID_manuscript_v9_clean.C5
- Required variables: `cdc_linkco15:BMI_R`, `cdc_linkco15:COMBGEST`, `cdc_linkco15:AGED`, `cdc_linkco15:UCOD`
### G2. The joint effect of maternal smoking and preterm birth on SUID incidence across PCA windows has not been estimated.
- Rationale: Maternal smoking and prematurity are each strong, persistent correlates of SUID incidence across PCA, and prematurity is about twice as strong early as late. Whether smoking-associated risk differs between preterm and term infants within each PCA window is untested and bears on targeting prevention.
- Prior art: The bed-sharing manuscript found maternal smoking the largest and most consistent correlate in both windows (bedsharing_ms_v7.C12) and prematurity positive throughout but stronger early (C13). Its interaction terms were bed sharing by smoking and bed sharing by preterm birth (C30); smoking by preterm birth was not estimated.
- Supporting claims: bedsharing_ms_v7.C12, bedsharing_ms_v7.C13, bedsharing_ms_v7.C30
- Required variables: `cdc_linkco15:CIG_REC`, `cdc_linkco15:GESTREC3`, `cdc_linkco15:COMBGEST`, `cdc_linkco15:AGED`, `cdc_linkco15:UCOD`
### G3. Whether the rise-peak-decline pattern of SUID incidence by PCA differs across cause-of-death subtypes (SIDS R95, accidental suffocation and strangulation in bed W75, ill-defined R99) is unknown.
- Rationale: Certification of sudden infant deaths shifts between R95, R99 and W75 by certifier and circumstance. If the subtypes follow different PCA trajectories, the pooled SUID curve mixes distinct developmental patterns; if they share one trajectory, the pooled PCA finding is robust to the cause-of-death misclassification the PCA manuscript names as a limitation.
- Prior art: The PCA manuscript found a clear rise, peak and decline in PCA-aligned SUID incidence (SUID_manuscript_v9_clean.C6) for R95, R99 and W75 pooled, and noted that vital-record data may misclassify cause of death (C12). Subtype-specific PCA trajectories were not reported.
- Supporting claims: SUID_manuscript_v9_clean.C6, SUID_manuscript_v9_clean.C12
- Required variables: `cdc_linkco15:UCOD`, `cdc_linkco15:COMBGEST`, `cdc_linkco15:AGED`

## D. Strategies and E. feasibility
### S1 (for G1) — feasible
**Question.** Does maternal prepregnancy obesity modify SUID incidence differently across postconceptional age (PCA) windows?

| Element | Specification |
|---|---|
| Outcome | `cdc_linkco15:UCOD` — Sudden Unexpected Infant Death (SUID) |
| Outcome subtypes | — |
| Exposures | `cdc_linkco15:BMI_R` |
| Covariates | `cdc_linkco15:COMBGEST`, `derived:PCA` |
| Interactions | `BMI_R` × `PCA` |
| Stratification |  |
| Offset | — |
| Denominator | count of `cdc_linkco15` records per stratum |
| Time scale | `derived:PCA` |
| Derived variables | `derived:PCA` = COMBGEST + AGED / 7 (`cdc_linkco15:COMBGEST`, `cdc_linkco15:AGED`): Postconceptional age in weeks, calculated as the sum of gestational age at birth and postnatal age (in days) divided by 7. |
| Design | population_incidence |
| Model class | negative_binomial |

Rationale: This study design examines whether maternal prepregnancy obesity modifies SUID incidence differently across specified PCA windows. The negative binomial model is chosen to account for overdispersion in the count data of SUID events, and the denominator source provides the population at risk.

Expected direction: The expected direction would be that higher BMI_R values are associated with increased SUID rates, particularly in the early rising (36-42 weeks) PCA window compared to the late declining (≥47 weeks) PCA window.

Variable resolution:
- `cdc_linkco15:UCOD` — OK: UCOD (p.40)
- `cdc_linkco15:BMI_R` — OK: Body Mass Index Recode (p.26)
- `cdc_linkco15:COMBGEST` — OK: Combined Gestation – Detail in Weeks (p.34)
- `cdc_linkco15:AGED` — OK: AGED (p.39)
Caveats:
- The variable `UCOD` from the source `cdc_linkco15` is labeled as 'Sudden Unexpected Infant Death (SUID)', but its type is listed as 'unknown'. This suggests that the documentation does not provide a clear definition or coding scheme for this outcome, which could introduce uncertainty in how SUID cases are identified and classified.

- The variable `BMI_R` from the source `cdc_linkco15` is labeled as 'Body Mass Index Recode', but its type is also listed as 'unknown'. The documentation only provides a partial definition ('1=Underweight <18.5') which does not cover all possible BMI categories, leading to potential misclassification of prepregnancy obesity status.

- The variable `COMBGEST` from the source `cdc_linkco15` is labeled as 'Combined Gestation – Detail in Weeks', but its type is listed as 'unknown'. The documentation indicates that it includes values for gestational age ranging from 17 to 47 weeks and an unknown category (99). This could introduce missingness or misclassification issues, particularly if many cases are coded as 'Unknown' which would affect the calculation of postconceptional age.

- The variable `AGED` from the source `cdc_linkco15` is labeled but its type is listed as 'unknown'. The documentation does not provide a clear definition for this variable, making it difficult to verify if it accurately represents postnatal age in days and whether there are any missing or invalid values that could affect the calculation of PCA.

Not assessed by MMF: statistical power; causal validity / confounding adequacy; actual missingness rates (documentation only; no row-level data read).
### S2 (for G2) — feasible
**Question.** Estimate the joint effect of maternal smoking and preterm birth on SUID incidence across PCA windows.

| Element | Specification |
|---|---|
| Outcome | `cdc_linkco15:UCOD` — Sudden Unexpected Infant Death (SUID) |
| Outcome subtypes | — |
| Exposures | `cdc_linkco15:CIG_REC`, `cdc_linkco15:GESTREC3` |
| Covariates |  |
| Interactions | `CIG_REC` × `GESTREC3` |
| Stratification | `cdc_linkco15:AGED` |
| Offset | — |
| Denominator | count of `cdc_linkco15` records per stratum |
| Time scale | `cdc_linkco15:AGED` |
| Derived variables | — |
| Design | population_incidence |
| Model class | negative_binomial |

Rationale: This study design and model class are chosen to estimate the joint effect of maternal smoking (CIG_REC) and preterm birth (GESTREC3) on SUID incidence across PCA windows. The negative binomial regression accounts for overdispersion in count data, which is common when modeling rare events like SUID. Stratification by AGED allows us to examine how these effects vary within different age groups of infants.

Expected direction: The model should reveal whether the risk associated with maternal smoking differs between preterm and term infants across PCA windows.

Variable resolution:
- `cdc_linkco15:UCOD` — OK: UCOD (p.40)
- `cdc_linkco15:CIG_REC` — OK: Cigarette Recode (Revised) 270 (p.26)
- `cdc_linkco15:GESTREC3` — OK: Combined Gestation Recode 3 (p.34)
- `cdc_linkco15:AGED` — OK: AGED (p.39)
Caveats:
- The variable UCOD (UCOD) is documented as 'unknown' with no levels or years specified, which means the definition and coding of SUID may be unclear. This could affect the reliability of outcome identification.

- CIG_REC (Cigarette Recode (Revised)) has a level 'U=Unknown or not stated', indicating potential missingness in maternal smoking data that needs to be addressed.

- GESTREC3 (Combined Gestation Recode 3) includes levels for preterm birth and 'Not stated' which may introduce uncertainty if many cases are coded as 'not stated'.

- AGED is documented as 'unknown' with no levels or years specified, making it unclear how age stratification will be applied.

Not assessed by MMF: statistical power; causal validity / confounding adequacy; actual missingness rates (documentation only; no row-level data read).
### S3 (for G3) — feasible
**Question.** Does the rise-peak-decline pattern of SUID incidence by PCA differ across cause-of-death subtypes (SIDS R95, accidental suffocation and strangulation in bed W75, ill-defined R99)?

| Element | Specification |
|---|---|
| Outcome | `cdc_linkco15:UCOD` — Sudden unexpected infant death (SUID) cases classified as SIDS (R95), accidental suffocation and strangulation in bed (W75), or ill-defined causes of death (R99). |
| Outcome subtypes | R95, W75, R99 (analysed separately) |
| Exposures | `derived:PCA` |
| Covariates |  |
| Interactions |  |
| Stratification | `cdc_linkco15:UCOD` |
| Offset | — |
| Denominator | count of `cdc_linkco15` records per stratum |
| Time scale | `derived:PCA` |
| Derived variables | `derived:PCA` = (COMBGEST + AGED / 7) (`cdc_linkco15:COMBGEST`, `cdc_linkco15:AGED`): Postconceptional age in weeks, calculated as the sum of gestational age at birth (in weeks) and postnatal age at death (in days divided by 7). |
| Design | population_incidence |
| Model class | poisson_regression |

Rationale: This study design uses a population incidence approach to examine the rate of SUID cases over different cause-of-death subtypes as a function of postconceptional age (PCA). The stratification by UCOD allows us to compare the rise-peak-decline patterns for each subtype. Poisson regression is chosen because it models count data with an offset, which in this case represents the denominator population from cdc_linkco15.

Expected direction: The expected pattern would be a rise, peak, and decline of SUID incidence by PCA for at least one cause-of-death subtype (R95, W75, R99), potentially differing across subtypes. This strategy does not establish causality or power.

Variable resolution:
- `cdc_linkco15:UCOD` — OK: UCOD (p.40)
- `cdc_linkco15:COMBGEST` — OK: Combined Gestation – Detail in Weeks (p.34)
- `cdc_linkco15:AGED` — OK: AGED (p.39)
Caveats:
- The variable UCOD in the source `cdc_linkco15` is documented as 'unknown' with no specified levels or years, which may limit its utility for stratifying SUID cases by specific cause-of-death subtypes (R95, W75, R99).

- COMBGEST and AGED are both documented as 'unknown', potentially leading to issues in accurately calculating the derived variable PCA. Specifically, COMBGEST has a level of 'Unknown' which could introduce missingness or inaccuracies.

- The documentation for UCOD does not specify whether it includes all relevant cause-of-death subtypes (R95, W75, R99) necessary to answer the research question.

Not assessed by MMF: statistical power; causal validity / confounding adequacy; actual missingness rates (documentation only; no row-level data read).
