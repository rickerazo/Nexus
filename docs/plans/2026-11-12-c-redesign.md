# C redesign: generate many candidate gaps, then narrow them down (2026-11-12)

## Why
The investigator judged S1 and S2 of SUID report v2 unusable: the gaps restate the literature (a known risk factor × PCA windows). The causes are in C (HANDOFF §4 item 5f):
- The C prompt says to prefer extending the manuscripts' frameworks.
- C sees only the 66 variables B mapped to manuscript concepts, out of about 5,800 documented.
- Every gap must cite a supporting claim.
- C is one call at temperature 0, which returns the most likely answer.

## Decisions (investigator, 2026-11-12)
- Shortlist 10 candidates; the investigator picks 5 for D.
- Supporting claims become optional; `prior_art` stays mandatory and must name the closest tested work in the inputs, or say there is none.
- Try `qwen2.5:32b` for C1 alone (the machine has 32 GB).
- Build C0 and C1 first, and review the raw ideas before building C3 and C4. This replaces the temperature-only experiment.
- Evaluation protocol amendments A–I approved (see `docs/evaluation_protocol.md`).

## Steps
| Step | What | Model, temperature | Status |
|---|---|---|---|
| C0 data inventory | Every source's variables in consecutive blocks (`c_inventory_block_vars`, 150); the model splits each block into 1–8 contiguous topic domains by naming each domain's first variable. Coverage is complete by construction. Domains record which variables B mapped (`used`). | `model`, `temperature` (0) | Built (`c_ideas.build_inventory`) |
| C1 ideas | One free-text-style call per (lens, seed): 6 lenses × seeds `[0, 1, 2]` × 5 ideas = 90 candidates. Input is the findings, limitations and future work of each manuscript (no quotes or methods) plus the C0 inventory. A failed call is recorded and skipped. | `c_ideation_model` (default `model`), `c_ideation_temperature` (0.9) | Built (`c_ideas.generate_ideas`) |
| C2 dedupe | Embed with `mxbai-embed-large`; group near-duplicates; keep one per group. | none | To build |
| C3 grounding | Each idea becomes a `KnowledgeGap`. Allowed variables are the idea's nearest variables among all ~5,800 (embedding search), not B's mapped set. The current validators apply. | `model`, 0 | To build |
| C4 scoring | Novelty: embedding distance from every extracted claim (computed in code). Feasibility: passed the checks, a denominator, variables with levels. Importance: a model rating 1–5 that can only filter. Selection rule fixed in advance. | `model`, 0 | To build |
| C5 review | `review_C.md` shows the shortlist of 10; the investigator picks 5. | none | To build |

## Design notes
- **Lenses:** `unused_data`, `tensions`, `inversion`, `mechanism`, `cross_source`, `design`. Their text names no SUID-specific idea (a unit test enforces it): an example would steer every run toward it and contaminate the novelty measure and the B0 baseline.
- **C1 uses a light JSON schema, not unconstrained text.** The schema has only strings and a list of source ids, so constrained decoding barely limits the model, and the existing logging, retry and checkpoint code still applies. Only source ids are validated.
- **No `top_p` setting.** Ollama's default (0.9) applies. Adding it would change the `LLMClient` protocol for every backend and the replay client.
- **Not part of `mmf run` yet.** `mmf ideate CONFIG --run-dir DIR` runs C0 and C1 on a run whose B is approved and writes `C_inventory.json`, `C_ideas.json` and `C_ideas.md`. Each call is checkpointed under `checkpoints/C_inventory` and `checkpoints/C_ideas`.
- **`cdc_codenames` is still in the config,** so it appears in the inventory. It goes at the next full B rerun.

## First run
On a copy of `runs/suid_poc_20261103` (`runs/suid_poc_20261103_ideas`), so the approved B and C stay untouched.
1. C0 and C1 with `qwen2.5:14b`, then keep `C_ideas.md` as `C_ideas.14b.md`.
2. C1 again with `c_ideation_model: qwen2.5:32b`; C0 is a cache hit.

Estimate (not measured): about 44 inventory calls, 30–40 minutes; 18 idea calls, about 35 minutes at 14B and roughly twice that at 32B.

## Run log
- **Thu 15:29 PST, 14B:** stopped at 15:49 on `C_inventory_ncfrp_v51_11` after 4 attempts. In every attempt the model started its last domain at `INCTimeOfIncident` (position 4 in the block) when it meant `INCtimeofincqual` (position 91). This NCFRP block is ordered alphabetically, not by topic.
  - **Fix:** the retry message now gives the positions and warns that names differing in case or suffix are different variables.
  - **Fallback:** on the final attempt, domains whose start is unknown or out of order are dropped. Their variables fall into the previous domain, and the drop is recorded in the call's `dropped` list.
  - The 11 finished blocks resume from checkpoints.
- **Thu 15:50 PST, 14B resumed; done 16:42.**
  - C0: 338 domains covering 6,035 variables; 309 domains contain no variable the manuscripts use.
  - C1: 90 ideas from 18 calls, all accepted on the first attempt.
  - Recurring themes: obesity/BMI 23, smoking 23, PCA 20, SES 15. Eleven rely on something no source records (inner-ear dysfunction, chronic intermittent hypoxia, progesterone, decades).
  - Most questions take the form "does X affect SUID?". The model treats PRAMS as if it records deaths.
  - Saved as `C_ideas.14b.{md,json}`.
- **Thu 16:43 PST, 32B C1 (C0 cache hit); done Fri 01:45.**
  - About 9 hours, roughly 30 minutes per call, against an estimate of about 70 minutes. Memory is tight with 32 GB at a 32k context.
  - 90 ideas, all accepted on the first attempt. Recurring themes: obesity 16, smoking 19, PCA 14, SES 10. Two rely on unmeasured things.
  - Better grounded, and somewhat more varied in form: SUID compared with other causes of death, how consistently sleep environment is recorded across jurisdictions, documentation practices over time.
  - Still mostly "does X affect SUID?". The PRAMS-as-outcome error appears in every cross-source idea.
  - Saved as `C_ideas.32b.{md,json}`.

## Source roles (investigator, 2026-11-16) — approved as proposed, 2026-11-16
**Diagnosis:** C1's ideas were "does X affect SUID?" and treated PRAMS as recording deaths, because MMF keeps a flat list of sources. The investigator's design thesis is that the sources play different roles, and that the leverage comes from combining them.

| Role | Sources | Gives | Cannot give |
|---|---|---|---|
| Case series | `ncfrp_v51`; `cdc_linkco15` (SUID by underlying cause of death) | Validated death circumstances (NCFRP); cases with birth-record fields (linked file) | Non-cases |
| Denominator | `cdc_natl15`; `cdc_linkco15` (births) | Births at risk, by stratum | Exposures beyond the birth certificate |
| Population reference | `prams_p7_arf`, `prams_p8_arf`, `prams_p8_std2` | Weighted exposure prevalence among mothers of live births | Outcomes (no deaths) |

**Coverage, as stated by the investigator:**
- **NCFRP export:** deaths 2004–2019, 24,314 cases (the manuscript uses 2008–2019).
  - Participation ramps up over 2004–2007: 248, 749, 871 and 1,197 cases.
  - About 1,250–1,670 cases a year over 2008–2013, and about 1,930–2,100 over 2014–2019.
- **NCFRP geography is de-identified:**
  - `RRandomState`: 42 randomized codes.
  - `RRandomDeathState`: 47 codes, blank for 51% of cases.
  - The 22 jurisdictions in the codebook header are the CDC SUID Case Registry, a subset of reviewing states. Do not conflate the two.
- **Linked file and natality file:** the 2015 cohort.
- **PRAMS:** Phase 7 and Phase 8. The bed-sharing manuscript uses PRAMS 2016–2021 (43 sites).
- **Linkage:** none at the individual level between PRAMS and any case source. PRAMS and NCFRP share no identifier, and NCFRP's state codes are randomized, so even a state-level join is impossible. Every comparison across case and reference sources is between groups.

**Designs that combining roles allows** (these replace the generic C1 lenses):
1. Case–population: exposure among cases against the weighted population prevalence. The odds ratio approximates the relative risk because the outcome is rare.
2. Exposure-specific rates: cases exposed ÷ (births × reference prevalence). This is the bed-sharing manuscript's offset design.
3. Case–case: SUID against other infant deaths.
4. Case-only: death circumstances by age or PCA within the cases.
5. Trends: proportions within the case series by period. Raw counts are not usable as a trend, because participation changes over time.
6. Measurement comparison: the same concept as recorded in different sources (for example bed-sharing in PRAMS vs NCFRP, or smoking on the birth certificate vs in PRAMS).

**Changes by stage:**
- **Config.** Per source:
  - `roles` (case / denominator / reference), replacing `denominator: true`;
  - `years`;
  - `geography` (including "de-identified, not linkable");
  - `unit` (death / live birth / sampled mother);
  - `weight_variable` (PRAMS: `wtanal`);
  - how missing and don't-know answers are coded.
- **B, as harmonization.** A table computed in code shows which roles measure each concept. Example: bed-sharing appears in a case source and in the reference source, so design 1 or 2 is possible for it.
- **C.** Each idea names its design (1–6) and the source in each role. Checks:
  - outcomes come only from case sources;
  - prevalence comes only from reference sources;
  - denominators come only from denominator sources.
- **D, a Strategy schema change that needs approval.** The strategy names its case, reference and denominator sources. It carries a harmonization note for each concept used across sources: wording, timing and coding.
- **E: checks computed in code.**
  - Year overlap between the case and reference periods.
  - A survey weight is used for any reference prevalence.
  - Missing and don't-know answers are not counted as exposed.
  - No state-level join involving NCFRP.

  These would flag the issues the investigator found in the bed-sharing analysis: the PRAMS prevalence is unweighted (27.7% vs 25.1% weighted, which moves the IRRs by a factor of about 1.15); 6,414 missing or don't-know answers are counted as bed-sharing; and PRAMS covers 2016–2021 while the cases span 2008–2019. That makes the bed-sharing analysis a concrete test case for E.

**B0 baseline (agreed 2026-11-16):** the plain-prompt baseline gets the same role descriptions, so the comparison is fair.

## Prompt structure (investigator, 2026-11-16) — approved 2026-11-16 (two-turn calls for C3 and D: yes)
- **Two layers per call.**
  - *System:* one shared scientific primer for every stage it applies to. It covers epistemic standards, designs before variables, matched numerators and denominators, explicit bias (selection, information, confounding), and association vs causation. It also includes the source-role table, generated from the config.
  - *User:* the task being run right now, meaning the stage's rules and inputs.
  - The prompt hash covers both layers.
- **Scope:** C, D and E now. A and B change only at the next full B rerun (the parser fix), because changing their prompts would invalidate the reviewed B.
- **Optional reasoning turn:** a free-text "think" turn before the JSON answer, in the same conversation. It needs a multi-message client call. Proposed for C3 and D, where choices made in one field constrain the others, and not for C0 or C1.
- **B0 baseline:** gets the same primer.

## Approved 2026-11-16
- **Source-role redesign:** approved as proposed.
- **D Strategy schema:** gains role assignments and harmonization notes (approved).
- **Two-turn reason-then-answer calls** for C3 and D (approved).
- **Primer text** (investigator's wording; "epidemiolog" corrected to "epidemiology"):

  > You are a data scientist working in epidemiology study design. Reason as a scientist: separate established findings, hypotheses and speculation, and never present a hypothesis as a finding. Think in study designs before variables. A rate needs a numerator and a denominator from the same population and period. Name the biases: selection, information and confounding. Association is not causation. Use only documented data. The data sources play distinct roles: [table from the config].

  The canonical text is in `src/mmf/prompts/science_primer.md`.
- **Geography** (checked in the codebooks 2026-11-16):
  - The public-use linked and natality files have no US geographic detail from 2005 on (LinkCO15 guide).
  - The NCFRP export randomizes state codes and has no urban/rural field.
  - PRAMS Phases 7 and 8 carry `NCHS_URB_RUR2`.
  - So urban/rural exists only on the reference side; a case–population comparison by urbanicity is not possible with these files. Possible routes: ask NCFRP for a derived NCHS urban–rural code, or use the restricted-use linked file.
- **Temperature per turn** (configurable; seeds fixed):
  - C1: 0.9.
  - C3 and D: 0.7 for the reasoning turn, 0.0 for the JSON turn.
  - E: 0.
- **PRAMS weight:** `WTANAL` (analysis weight) in both phases.

## Built 2026-11-16 (steps 1–4 of the approved order)
- **Config:**
  - `SourceSpec.roles` (case / denominator / reference) plus `unit`, `years`, `geography`, `linkage`, `weight_variable` and `missing`.
  - `denominator: true` maps to the denominator role.
  - `configs/suid.yaml` carries the investigator's coverage. The PRAMS ARFs use `WTANAL`.
- **Primer:** `prompts/science_primer.md` is the system message of primed prompts (`load_primed_prompt`), with the role table generated by `components/roles.py`. The prompt hash covers both files.
- **Cross-role table:** `roles.cross_role_concepts` builds it from B's mappings, listing concepts measured in both a case series and a reference source first.
  - It is limited to manuscript concepts, because B maps only those. Bed sharing appears as case + reference.
  - Concepts outside the manuscripts reach C1 only through the inventory.
- **C1:**
  - Six designs (`case_population`, `exposure_rates`, `case_case`, `case_only`, `trends`, `measurement`) replace the lenses.
  - Each idea lists its sources by role, plus a `comparison`.
  - The validator rejects:
    - a source used in a role it doesn't have;
    - an idea missing a role its design needs;
    - a measurement comparison with fewer than two sources.
  - The task prompt (`c_ideas.md`) is primed.
- **Not yet built:**
  - the two-turn calls (needed by C3 and D, not C1);
  - C2–C5;
  - the D and E changes;
  - moving D and E onto the primer.
- **Mon 15:52 PST, role-based C1 on 14B; done 16:33.**
  - 90 ideas. One call needed 3 attempts: twice the validator caught a source listed in a role it doesn't have, once `cdc_natl15` as a reference.
  - Saved as `C_ideas.roles-14b.{md,json}`; the lens-based pool is in `prev_lenses/`.
  - **Better:**
    - No PRAMS-as-outcome ideas.
    - The form of the questions follows the designs: SUID compared with suffocation, congenital-anomaly and external-cause deaths; NCFRP vs PRAMS recording of sleeping arrangements; birth-certificate vs PRAMS BMI; trends in proportions within cases.
    - Only 2 ideas rely on unmeasured things.
  - **Still wrong:**
    - Topics stay on the manuscripts' concepts (obesity 29, smoking 22). The cross-role table lists only manuscript concepts, and it anchors the model.
    - Case-only ideas ask about "incidence".
    - Trend periods run past the case series (2015–2021, when NCFRP ends in 2019).
    - The linked file and NCFRP are combined as case sources, which double-counts deaths unless the two are deduplicated, and they can't be linked.
    - One idea uses geography within states.
