# MMF first full runs and benchmark against Biomni (Nov 2026)

As of 2026-11-19. Shareable version with comments and figures: Claude Docs, "MMF first full runs and benchmark against Biomni (Nov 2026)". This file is the repository copy.

## Summary

MMF now runs end to end on a local model. On the same model, it produced 10 research questions that all pass the design checks, and Biomni, a general biomedical AI agent, produced 17 of which 1 passes.

The Manuscript-to-Model Framework (MMF) reads our SUID manuscripts and the data dictionaries of the sources we hold. It proposes research questions those data could answer and drafts an analysis plan for each. Every step runs on a model hosted on this machine (qwen2.5:14b), so no manuscript or codebook text leaves the institution.

What was done between October 26 and November 19, 2026:

- **First full run, stages A to E (Oct 26 – Nov 11).** The pipeline worked after a series of parser and validation fixes. But the three questions it proposed restated what the manuscripts already say, so we judged the output unusable for discovery.
- **Redesign of the question-finding stage (Nov 12 – 19).** It now generates 85 candidate questions across six study designs and checks each against the data dictionaries in code. 78 passed every check, and a shortlist of 10 was ranked for expert review.
- **Benchmark against Biomni (Nov 18 – 19).** Biomni ran on the same model, with the same inputs and the same instructions, three times. Its questions mostly used variable names that do not exist in our data, and they repeated textbook risk factors.

Two cautions apply:

- **The shortlist has a known flaw.** 4 of MMF's 10 shortlisted questions compare two survey files with each other and involve no SUID cases. The novelty score rewarded them for being far from the manuscripts' topic. Three more have a design or wording problem the code checks cannot see.
- **The benchmark tests Biomni outside its intended setting.** Biomni was built for large cloud models. A rerun with a large cloud model is pinned for when funding allows it.

**Still to do:** blinded expert rating of all 27 questions (MMF and Biomni mixed, arm hidden) by the investigator and one colleague. Its results will be added to this report.

## What MMF does

MMF turns manuscripts and data dictionaries into checked research questions and analysis plans, in five stages with human review between them.

*Figure (in the shared doc): five stages A → E; investigator review after B and after C; every model answer checked in code and retried with the reason, up to 4 attempts.*

1. **A, read the manuscripts.** Extracts each manuscript's claims, variables, designs and models. Every claim must quote the manuscript word for word, or it is dropped.
2. **B, map to the data.** Matches each concept from the manuscripts to variables in the data dictionaries, and labels each match as direct, derived, proxy or none. An independent embedding search flags likely misses. The run stops here for the investigator's review.
3. **C, find research questions.** Since November 12 this stage has six steps:
   1. C0 sorts every variable into topic domains.
   2. C1 generates candidate questions under six study designs.
   3. C2 removes near-duplicates.
   4. C3 grounds each question in named sources and variables and checks its design in code.
   5. C4 scores novelty, feasibility and importance.
   6. C5 writes a shortlist for the investigator.
4. **D, plan the analysis.** Writes a structured strategy per question: design, model class, outcome, exposure, covariates, denominator. Choices come from fixed lists, and rates must name a denominator.
5. **E, check feasibility.** Code confirms that every variable exists and that the sources' years overlap. The model then lists caveats and blockers.

Three principles hold throughout:

- **Local model only.** Every language-model call uses qwen2.5:14b on Ollama on this machine. Cloud models are off unless explicitly enabled with institutional credentials, and they have not been.
- **Checks in code, not trust in the model.** Every model answer must fit a fixed schema. Code then checks it: variables must exist in the dictionary, claims must be quoted verbatim, designs must follow the rules below. A failing answer is sent back with the reason and retried, up to four attempts.
- **Source roles decide what a design may claim.** Each data source has a role:
  - Case series (NCFRP, the linked infant-death file) supply SUID cases.
  - Denominator sources (natality files) supply births.
  - Population references (PRAMS) supply survey-weighted prevalence among mothers.

  So a question may report a rate only if a denominator source is named. PRAMS prevalences must use the survey weight. Outcomes come only from case series.

## Inputs

MMF worked from three manuscript files and seven data dictionaries. It used documentation only, never row-level data.

**Manuscripts**

- The developmental-timing manuscript (SUID by postconceptional age), v9.
- The bed-sharing manuscript (sleep environment and exposures by postconceptional age), v7.
- Abstracts of related SUID papers from the Ramirez lab and collaborators, taken from PubMed.

**Data dictionaries** (6,035 variables in total, parsed by code rather than by the model)

| Source | Role | Unit | Years held | Variables |
|---|---|---|---|---|
| NCFRP case reporting system v5.1 | Case series | One child death reviewed by a fatality review team | Deaths 2004–2019 (24,314 cases) | 4,422 |
| CDC linked birth/infant death file | Case series and denominator | One 2015 live birth, linked to its death if the infant died within a year | 2015 births, deaths to 2016 | 270 |
| CDC natality file | Denominator | One live birth | 2015 | 245 |
| PRAMS Phase 7 research file | Population reference (weighted) | One sampled mother, surveyed months after birth | 2012–2015 | 386 |
| PRAMS Phase 8 research file | Population reference (weighted) | Same | 2016–2021 | 485 |
| PRAMS Phase 8 Standard Section II | Population reference | Same | 2016–2021 | 4 |
| CDC variable-name list | Reference list only, not a dataset | — | — | 223 |

What the data cannot do, as recorded for the model:

- **No linkage across sources.** NCFRP, PRAMS and the CDC files share no identifiers. Comparisons between them are at the group level only.
- **No geography.** NCFRP's state codes are randomized, and the CDC public-use files carry no geography. Only PRAMS has an urban/rural flag.
- **NCFRP is not a complete count.** It covers deaths reviewed by participating teams, and participation grew over time. It cannot supply incidence on its own.

**Years held are holdings, not limits.** More years can be acquired for every source, for example PRAMS beyond 2016–2021. Since November 18, MMF never rejects a question because a source lacks some years. It records the years to acquire instead. A question can fail only for epistemological, logical or logistical reasons.

**Epic Cosmos** is described from public information only. It will become an input once its real data dictionary is exported.

## First full run, stages A to E (Oct 26 – Nov 11)

The first run reached a complete report on November 11. Its three proposed questions restated known risk factors, which is what prompted the redesign of stage C.

**How it got there.** Each failure stopped the run, was traced to a cause, and was fixed in code before restarting.

| Date | What happened | Fix |
|---|---|---|
| Oct 26 | Stage A extracted claims but no variables. | Every output field made required; the run stops if a manuscript yields nothing (Nov 6). |
| Nov 6 | Stage B failed. Twelve variables of the linked file were missing (sex, smoking, BMI and others). | Three dictionary-parser fixes. The linked file went from 233 to 270 variables, PRAMS Phase 7 from 170 to 386, Phase 8 from 177 to 485. |
| Nov 9 | B failed on its 9th call and lost 8 finished calls, because the model packed several variables into one field. | Multi-variable answers are split, and every call is checkpointed. An independent audit of the parsed dictionaries runs on every ingest. |
| Nov 10 | B completed all 28 calls and stopped for review. | — |
| Nov 11 | Investigator reviewed B and C. D failed twice on its third question (the cause-of-death code used as a stratifier; no exposure named). | D gained births-denominator support, outcome subtypes and derived variables such as postconceptional age. Report v1 at 16:30 PST, v2 at 17:31 PST. |

**What each stage produced** (run of Nov 6–11):

- **A:** 14 claims and 12 variables from the developmental-timing manuscript; 30 and 17 from the bed-sharing manuscript; 62 and 39 from the abstracts. That is 54 distinct concepts, about 32 of them animal or cellular measures with no counterpart in population data.
- **B:** 696 concept–variable rows before review (62 direct, 10 derived, 54 proxy, 570 none). After the investigator's review, 159 rows over the 22 concepts the investigator kept (70 direct, 27 derived, 15 proxy, 47 none). The embedding search raised 46 possible misses; about half were real.
- **C (original design):** one call proposed three questions. After review they were BMI × postconceptional age, smoking × preterm birth across postconceptional age, and the postconceptional-age pattern by cause of death.
- **D:** three incidence models, each using the linked file's births as the denominator.
- **E:** in v1, two of the three strategies were rated blocked and one feasible. In v2, with identical documentation, all three were rated feasible.

**Why stage C was redesigned.** On November 12 the investigator judged the first two questions unusable: they restate the literature (a known risk factor crossed with postconceptional-age windows). The causes were in the design of stage C:

- its prompt favoured extending the manuscripts' own frameworks;
- it saw only the 66 variables B had matched to manuscript concepts, out of about 5,800;
- every question had to cite a manuscript claim;
- a single call at temperature 0 returns the model's most likely, least surprising answer.

## Redesign of the question-finding stage (Nov 12 – 19)

The redesigned stage C turned 85 candidate questions into 78 that pass every design check. From those it ranked a shortlist of 10.

**The new design.**

- Generate many candidates, then narrow them.
- The model sees every variable, grouped into 338 topic domains, instead of only the 66 matched to manuscript concepts. 309 of those domains are not used by the manuscripts.
- Candidates are generated under six study designs:
  - case–population comparison (exposure among cases vs weighted prevalence among all mothers);
  - exposure-specific rates (cases, exposure prevalence and births combined);
  - case–case comparison (SUID vs other deaths in the same series);
  - case-only analysis;
  - trends within cases;
  - measurement comparison (how the same concept is recorded in different sources).
- Three seeds per design, five ideas each, at a sampling temperature of 0.9.
- Each candidate is then grounded and checked in code.
- After November 17 the design was frozen except for one change: years held never exclude a question.

**Run by run.** Each change was made to fix a specific failure seen in the run before it. All runs used qwen2.5:14b unless noted.

| Run (PST) | What changed | Result | What it showed |
|---|---|---|---|
| Nov 12, 15:29–16:42 | First topic inventory and idea generation | 338 domains; 90 ideas | Ideas clustered on the manuscripts' own topics (obesity 23, smoking 23). PRAMS was treated as if it recorded deaths. |
| Nov 12–13, 16:43–01:45 | Same, with the larger qwen2.5:32b | 90 ideas in about 9 h | Somewhat better grounded, same topic anchoring. Too slow to use routinely. |
| Nov 16, 15:52–16:33 | Source roles and six designs replace open-ended prompts | 90 ideas | PRAMS-as-outcome errors gone. Still anchored on manuscript topics. Case-only designs still said "incidence". |
| Nov 16, 16:40–22:31 | The model must cite topic domains by ID, enforced by the output grammar | 75 ideas, 74 on topics the manuscripts do not use | Smoking ideas fell from 23 to 0, obesity from 17 to 4. |
| Nov 17, 14:40–19:42 | Grounding, scoring and shortlist built (C2–C5) | 72 after duplicates removed; 52 grounded, 11 not groundable, 9 failed | Importance ratings (all 3 or 4) did not separate questions. Several ideas were rejected only for years not held. |
| Nov 18, 14:19–22:10 | Years held no longer exclude a question; years to acquire recorded | 85 ideas; 67 grounded, 2 not groundable, 16 failed | 46 of 67 grounded questions need years not yet held. |
| Nov 19, 03:36–04:52 | Bookkeeping errors (an unused source, a missing survey weight, an unlisted citation) fixed in code on the last attempt | 78 grounded, 2 not groundable, 5 failed | Final result, used in the benchmark. |

*Figure (in the shared doc): funnel of 85 candidate ideas → 85 after near-duplicates removed → 78 grounded → 10 shortlisted.*

**The 7 questions that did not pass**, all for legitimate reasons:

- 2 were judged not answerable: BMI is not recorded for the cases (I31), and the design needs a denominator no source supplies (I68).
- 2 failed on logic: they ask for a risk with no denominator source (I55, I63).
- 3 failed on bookkeeping: they cite a claim number such as "C8" that exists in more than one manuscript, and the code does not guess which one (I24, I54, I59).

**Correction.** On November 18 the measurement-comparison questions I71–I76 were reported as logical failures. That was wrong. A measurement comparison does not need a case series. They failed only because an unused case source was listed, and they passed once the code removed it.

**The shortlist.** Selection rule:

- importance at least 3;
- ranked by novelty × feasibility;
- skip any question too similar (cosine ≥ 0.85) to one already picked;
- stop at 10.

| Rank | Gap | Design | Question, shortened | Sources | Novelty | Feasibility | Importance | Concern |
|---|---|---|---|---|---|---|---|---|
| 1 | G64 | Measurement | Pregnancy weight-gain reporting: PRAMS Phase 8 research file vs Standard Section II | PRAMS P8 (2 files), 2016–21 | 0.40 | 0.83 | 3 | No SUID cases |
| 2 | G66 | Measurement | Talks about preventive practices: PRAMS Phase 7 vs Phase 8 | PRAMS P7, P8, 2012–21 | 0.41 | 0.75 | 3 | No SUID cases |
| 3 | G74 | Measurement | Recorded pregnancy weight gain: NCFRP cases vs PRAMS Phase 8 | NCFRP; PRAMS P8, 2008–21 | 0.38 | 0.57 | 4 | Wording speaks of SUID cases in PRAMS, which has none |
| 4 | G68 | Measurement | Medicaid coverage: PRAMS Phase 7 vs Phase 8 | PRAMS P7, P8, 2012–21 | 0.42 | 0.50 | 3 | No SUID cases |
| 5 | G4 | Cases vs population | Pre-pregnancy hypertension, SUID mothers vs weighted population | Linked file, NCFRP; PRAMS P7, P8, 2012–21 | 0.31 | 0.57 | 4 | — |
| 6 | G65 | Measurement | Smoking in pregnancy: PRAMS Phase 7 vs Phase 8 | PRAMS P7, P8, 2012–21 | 0.26 | 0.67 | 3 | No SUID cases |
| 7 | G13 | Exposure rates | SUID rate by severe maternal mental-health problems | NCFRP; PRAMS; natality, 2016–21 | 0.30 | 0.57 | 4 | NCFRP cases over all US births |
| 8 | G23 | Exposure rates | SUID risk by barriers to health care | Linked file; PRAMS P8; natality, 2015–21 | 0.26 | 0.67 | 4 | — |
| 9 | G8 | Cases vs population | Pre-pregnancy health checks, SUID mothers vs PRAMS mothers | NCFRP; PRAMS P7, 2012–15 | 0.33 | 0.50 | 4 | — |
| 10 | G19 | Exposure rates | Share of SUID by pre-pregnancy behaviours and conditions | NCFRP; PRAMS; natality, 2008–21 | 0.24 | 0.67 | 3 | NCFRP cases over all US births |

The concerns are explained under Limitations. They were found by reading the output and logged without changing MMF, because tuning had stopped before the benchmark.

## Benchmark against Biomni (Nov 18 – 19)

With the same model, inputs and instructions, all 10 of MMF's shortlisted questions passed the design checks. 1 of Biomni's 17 did. Nearly every variable Biomni named does not exist in our data.

**The question.** Does MMF's staged, code-checked pipeline produce better research questions than a general biomedical AI agent working freely? Biomni (Stanford SNAP, version 0.0.8, agent A1) is a widely cited open-source agent of that kind. It reads files, writes and runs its own code, and decides when it has an answer.

**Why the model was held fixed.** Both arms used qwen2.5:14b on the same local Ollama server with the same 32,768-token context.

- The institute's rule is local models only.
- Holding the model fixed means any difference comes from the method, not the model.

**Setup.**

- **Same information.** Biomni received:
  - the manuscripts as plain text;
  - every data dictionary as a table (the same 6,035 variables MMF uses);
  - the original documents;
  - the investigator's description of each source's role, units, years held, weights and linkage.

  It received none of MMF's intermediate output or prompts.
- **Same instructions.** The task stated the same goal and the same rules MMF works under:
  - outcomes only from case series;
  - no rates without a denominator source;
  - survey weights for prevalence;
  - years held are not a limitation.

  It asked for the same output fields.
- **Changes to Biomni's defaults, each made so that it could run properly:**
  - Biomni connects to Ollama without setting a context size or stop markers. Its long instructions would have been cut off, so both were set (the stop markers are the ones Biomni sends to every other provider).
  - Its 11 GB library of molecular databases, with nothing on infant death, was not downloaded.
  - Biomni runs the code it writes on the host computer, so each run was sandboxed: network to the local model only, and file writes to its own folder only. The logs show the sandbox never blocked it.
- **Runs.** MMF ran once at temperature 0, which is deterministic. Biomni ran three times at its default temperature of 0.7 (seeds 0, 1, 2), with a limit of 300 minutes each. Biomni ran Nov 18, 22:10 to Nov 19, 03:36 PST, with nothing else using the model.

**Measures.**

- **Code checks.** The same checks MMF applies, run afterwards on the top 10 of every run:
  - variables that do not exist in the source named;
  - sources used in the wrong role;
  - missing survey weights;
  - incidence or risk claimed without a denominator source.
- **Novelty:** 1 minus the closest embedding similarity to any manuscript claim (0 = restates a claim).
- **Feasibility:** the share of named variables that exist and have documented values.
- **Redundancy:** the highest similarity between two questions in the same run.

**Results.**

| Arm | Status | Questions | Pass all checks | Variables not in the data | Survey weight missing | Wrong role | Novelty (mean) | Feasibility (mean) | Max similarity | Time |
|---|---|---|---|---|---|---|---|---|---|---|
| MMF | Finished | 10 | 10 | 0 of 66 | 0 | 0 | 0.33 | 0.63 | 0.85 | about 9 h for stage C |
| Biomni, seed 0 | Stopped at the 300-min limit after 130 steps; answer written mid-run | 5 | 0 | 8 of 8 | 5 | 0 | 0.20 | 0.00 | 0.83 | 302 min |
| Biomni, seed 1 | Finished, 37 steps | 9 | 1 | 9 of 10 | 0 | 1 | 0.26 | 0.11 | 0.87 | 14 min |
| Biomni, seed 2 | Finished, 26 steps | 3 | 0 | 10 of 10 | 2 | 0 | 0.18 | 0.00 | 0.84 | 10 min |

**What Biomni's questions look like.** They are textbook SUID risk factors phrased as incidence: smoking, prematurity, socioeconomic status, maternal age, education, prenatal care. Examples, verbatim:

- "Does socioeconomic status play a role in the incidence of SUID?" It uses the variable SOCIOECONOMIC_STATUS, which PRAMS does not have.
- "Does geographic variation in birthplace affect the incidence of SUID?" This is the one question that passed every check. Its variable, birth facility type, is real, but the public-use files carry no geography, so the question cannot be answered.
- "Does postconceptional age at which infants start bed-sharing differ between SUID cases and non-SUID live births?" All four of its variables are invented, and it pairs 2015 births with 2016–2021 deaths.

Biomni read every data dictionary it was given; the logs show the files loaded. It then wrote variable names that sound plausible (MOMEDU, SES, BED_SHARING) instead of the documented ones.

**How to read this result.**

- **What it shows:** with a 14-billion-parameter local model, MMF's narrow, checked steps keep questions tied to real variables and valid designs. A free-running agent loses that tie.
- **What it does not show:** that MMF beats Biomni in general. Biomni was built and evaluated with much larger cloud models, which handle long open-ended agent loops far better. This test runs it outside its intended setting.
- **Other differences between the arms:**
  - Temperature (0 vs 0.7) and the number of runs (1 vs 3) differ. All three Biomni runs were poor, so temperature alone is unlikely to explain the gap, but it is not ruled out.
  - MMF's shortlist is its top 10 of 78 checked questions, while Biomni returned only 3 to 9 questions per run. MMF's ranking had more to choose from.
- **Novelty here is only distance from the manuscripts,** which can reward off-topic questions (see Limitations). The blinded expert rating is the real test of quality.

## Limitations and known problems

The code checks show that MMF's questions are well-formed, not that they are good science. Seven of the ten shortlisted questions have a problem the checks cannot see; three (G4, G8, G23) have none found so far.

**Problems in the shortlist**

- **Four questions have no SUID cases (G64, G65, G66, G68).** Each compares two PRAMS files on a single item: weight gain, smoking, preventive-care talks or Medicaid. They are valid measurement comparisons but say nothing about SUID. They rank high because novelty is measured as distance from the manuscripts' claims, so off-topic questions look novel.
- **Two rates use an incomplete case count (G13, G19).** They divide NCFRP cases by all US births. NCFRP covers only deaths reviewed by participating teams, so these rates would be biased low. A defensible version would restrict the births to the reviewing jurisdictions, which the de-identified data does not allow, or use the linked file's cases.
- **One question is worded incoherently (G74).** It speaks of "SUID cases" in PRAMS, which surveys mothers of live births and records no deaths.

**Limits of the method so far**

- **Importance does not discriminate.** The model rated every grounded question 3 or 4 out of 5, so importance filters almost nothing. Novelty spans a narrow range (about 0.2 to 0.4).
- **Stages D and E have not been rerun on the new questions.** The analysis plans in report v2 belong to the old stage C.
- **Stage E is unstable.** Its verdicts flipped between v1 and v2 on identical documentation, because the blockers are written by the model rather than checked in code.
- **One MMF run.** Run-to-run variation is unmeasured. The evaluation protocol calls for five runs per condition.
- **The protocol's planned comparisons have not been run:**
  - MMF with its checks switched off;
  - a plain single-prompt baseline (B0);
  - a cloud-model condition.
- **Data documentation gaps.** Some death-record fields in the linked file are parsed without their value labels. The PRAMS Standard Section II dictionary yielded only 4 variables.

**Limits of the benchmark**

- **Biomni ran outside its intended setting** (a small local model instead of a large cloud model).
- **The arms differ in temperature, number of runs and pool size**, as described above.
- **Blinding is imperfect.** Labels are hidden, but writing style may hint at which system wrote a question.
- **Small numbers.** 27 questions and two raters. The analysis will be descriptive only.
- **No expert rating yet.** Every quality judgment in this report comes from code checks, embeddings and one reading of the output.

## Next steps

The next step is the blinded expert rating. It decides whether the code-check advantage holds up as research quality.

- [ ] **Blinded rating of 27 questions** (10 from MMF, 17 from Biomni, mixed in random order with the system hidden).
  - Raters: the investigator and one colleague.
  - Each question is scored 1–5 on feasibility, coherence, novelty, importance and interpretability.
  - Raters spend a 10-minute PubMed search on each question and log their queries.
  - The key stays closed until both raters finish.
  - The analysis will report means by system and dimension, agreement between raters, and the share of questions that pass every check and score at least 4 on both novelty and importance.
- [ ] **Investigator picks 5 of the 10 shortlisted questions** for stages D and E, then reruns D and E on them.
- [ ] **Decide whether to run the protocol's single-prompt baseline (B0)** and how many repeat runs MMF gets (the protocol asks for 5).
- [ ] **Pinned until funding allows: rerun the benchmark with a large cloud model.**
  - Trigger: an institutional cloud-model endpoint, funded through the institute. Personal accounts or keys are never used.
  - Design:
    - same inputs, task and scorer;
    - Biomni on the kind of model it was built for;
    - MMF on the same cloud model;
    - three runs each.
  - This answers whether MMF's advantage holds when the agent has a capable model, and how much a better model improves MMF itself.

MMF itself will not be tuned further unless the expert rating points to a specific fault. The problems listed above are logged, not fixed, so the benchmark compares the system as it stood.

## Appendix: settings, files and commits

All times are Pacific Standard Time. The project is open source (MIT, github.com/rickerazo/Nexus). Every input (documentation only, no row-level data) and every run artifact below is in the repository. Raters should not read this report, the run folders or the blinding key before finishing the blinded sheet.

**Model settings**

| Setting | MMF | Biomni |
|---|---|---|
| Model | qwen2.5:14b (Ollama digest 7cdf5a0187d5) | same |
| Context window | 32,768 tokens | same |
| Temperature | 0 for checks and grounding; 0.9 for idea generation; 0.7 for the grounding reasoning turn | 0.7 (default) |
| Seeds | 0 (idea generation: 0, 1, 2 per design) | 0, 1, 2 |
| Retries | up to 4 attempts per call, with the failure reason fed back | its own loop, up to 500 steps or 300 minutes |
| Embeddings | mxbai-embed-large | none (scored afterwards with mxbai-embed-large) |

**Key files**

| What | Where |
|---|---|
| First full run and reports v1, v2 | runs/suid_poc_20261103/ (report.md, report.v1-2026-11-11.md) |
| Redesigned stage C outputs and shortlist | runs/suid_poc_20261103_ideas/ (review_C_shortlist.md) |
| Benchmark scores and blinded rater sheet | runs/biomni_20261118/ (report.md, scores.csv, rater_sheet.md, rater_sheet.csv) |
| Blinding key (raters: do not open before rating) | runs/biomni_20261118/blinding_key.csv |
| Every model call, prompt and response | runs/*/llm_log/ |
| Benchmark harness | benchmarks/biomni/ |
| Design and run logs | docs/plans/2026-11-12-c-redesign.md, docs/plans/2026-11-18-biomni-benchmark.md |
| Evaluation protocol (draft v0.1, amendments A–I approved Nov 12) | docs/evaluation_protocol.md |

**Key commits**

| Commit | Date | Change |
|---|---|---|
| d6f3385 | Nov 19 | Benchmark results and final stage C rerun |
| 6bbed58 | Nov 18 | Bookkeeping errors fixed in code on the last attempt |
| c467cd8 | Nov 18 | Biomni benchmark harness |
| eb8bb59 | Nov 18 | Years held never exclude a question |
| fc2df67 | Nov 17 | Duplicate removal, grounding with design checks, scoring, shortlist |
| d6776d3 | Nov 16 | Topic domains cited by ID, enforced by the output grammar |
| c34afe4 | Nov 16 | Source roles and design-based idea generation |
| 71b06c4 | Nov 12 | Stage C redesign: topic inventory and idea generation |
| 98930b8 | Nov 11 | Report v2 and the record of stage E's unstable verdicts |
| 9d78c98 | Nov 10 | Stage B splits multi-variable answers and checkpoints each call |
| f351764 | Nov 9 | Independent audit of the parsed data dictionaries |
| 1407505 | Nov 6 | Stage A extracts variables and stops on empty output |
