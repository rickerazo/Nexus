Roles: a case series records the outcome events (outcomes come only from case sources); a denominator source gives the population at risk; a population reference gives exposure prevalence in the general population and never records outcomes. Comparisons between a case series and a reference source are group-level unless a linkage is stated.

- cdc_linkco15 (CDC linked birth/infant death public-use file guide, 2015). Role: case series and denominator.
  One record: one live birth in the 2015 cohort, with its linked infant death record if the infant died in the first year.
  Covers: US live births in the 2015 cohort linked to infant deaths in the first year (births and deaths), so it supplies both SUID cases and births denominators.
  Years held (more can be acquired): births in 2015 and their deaths in the first year.
  Geography: none: public-use files from 2005 on identify no US geographic detail.
  Linkage: births and infant deaths are linked within the file; no link to NCFRP or PRAMS.
  Missing answers: documented per item (e.g. 9 = unknown or not stated); blanks are unknowns.
- cdc_natl15 (CDC natality public-use file guide, 2015). Role: denominator.
  One record: one live birth.
  Covers: all US live births in 2015; no deaths.
  Years held (more can be acquired): 2015.
  Geography: none: public-use files from 2005 on identify no US geographic detail.
  Linkage: none.
  Missing answers: documented per item (e.g. 9 = unknown or not stated); blanks are unknowns.
- cdc_codenames (CDC birth/death file variable names and labels (analysis extract)): a lookup list of names and labels, not a dataset; no role.
- ncfrp_v51 (National Fatality Review Case Reporting System (NFR-CRS) codebook v5.1). Role: case series.
  One record: one child death reviewed by a fatality review team; this project uses the SUID cases.
  Covers: child deaths reviewed by participating fatality review teams; deaths only, no births or surviving infants, so it cannot supply incidence denominators.
  Years held (more can be acquired): deaths 2004-2019 in the export (24,314 cases); participation ramps up 2004-2007 (248 to 1,197 cases a year), about 1,250-1,670 a year 2008-2013 and 1,930-2,100 a year 2014-2019; the manuscript uses 2008-2019. Changes in case counts over time reflect participation, not incidence.
  Geography: de-identified: state fields are randomized codes (42 reviewing-state codes; death state blank for 51%); no state names, no county, no urban/rural. The 22 jurisdictions in the codebook header are the CDC SUID Case Registry subset, not all reviewing states.
  Linkage: none: no identifier shared with PRAMS or the CDC files, and randomized state codes prevent even state-level joins.
  Missing answers: documented per item; unknown is a separate answer, never exposed.
- prams_p8_arf (PRAMS Phase 8 Analytic Research File codebook). Role: population reference.
  One record: one sampled mother of a live birth, surveyed a few months after the birth.
  Covers: weighted survey of mothers a few months after a live birth, sampled from birth certificates in participating states; not designed to count infant deaths.
  Years held (more can be acquired): Phase 8 (the bed-sharing manuscript uses 2016-2021, 43 sites).
  Geography: participating sites only; NCHS urban/rural (2 levels) available; no case source has urban/rural.
  Linkage: none at the individual level: group-level comparisons with case series only.
  Survey weight (required for any prevalence): WTANAL.
  Missing answers: .B = don't know or blank, .S = skipped; never count these as exposed.
- prams_p8_std2 (PRAMS Phase 8 Standard Section II codebook). Role: population reference.
  One record: one sampled mother of a live birth, surveyed a few months after the birth.
  Covers: weighted survey of mothers a few months after a live birth, sampled from birth certificates in participating states; not designed to count infant deaths.
  Years held (more can be acquired): Phase 8.
  Geography: participating sites only.
  Linkage: none at the individual level: group-level comparisons with case series only; its items are used with the Phase 8 ARF, whose WTANAL weight applies.
  Missing answers: don't know is coded separately (e.g. 7777); never count it as exposed.
- prams_p7_arf (PRAMS Phase 7 Analytic Research File codebook). Role: population reference.
  One record: one sampled mother of a live birth, surveyed a few months after the birth.
  Covers: weighted survey of mothers a few months after a live birth, sampled from birth certificates in participating states; not designed to count infant deaths.
  Years held (more can be acquired): Phase 7 (2012-2015).
  Geography: participating sites only; NCHS urban/rural (2 levels) available; no case source has urban/rural.
  Linkage: none at the individual level: group-level comparisons with case series only.
  Survey weight (required for any prevalence): WTANAL.
  Missing answers: .B = don't know or blank, .S = skipped; never count these as exposed.
